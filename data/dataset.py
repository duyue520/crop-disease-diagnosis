import os
import json
import warnings
from collections import defaultdict

import torch
import torchvision.transforms as T
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import datasets
from PIL import Image, ImageFile

# 全局配置：容忍损坏图片、截断加载，避免训练直接崩溃
warnings.filterwarnings("ignore")
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None


def analyze_dataset(cfg):
    """
    数据集统计分析：类别分布、样本数量，输出+保存JSON
    """
    basic_transform = T.Compose([
        T.Resize((cfg.IMAGE_SIZE, cfg.IMAGE_SIZE)),
        T.ToTensor()
    ])

    full_dataset = datasets.ImageFolder(root=cfg.DATA_DIR, transform=basic_transform)
    class_counts = defaultdict(int)

    for _, label in full_dataset.samples:
        cls_name = full_dataset.classes[label]
        class_counts[cls_name] += 1

    # 打印统计
    print("  数据集类别分布统计:")
    print("  " + "-" * 65)
    total_samples = 0
    for cls, cnt in sorted(class_counts.items()):
        cls_cn = cfg.CLASS_CN.get(cls, cls) if hasattr(cfg, "CLASS_CN") else cls
        print(f"  {cls_cn:<25} | 样本数: {cnt:>6,}")
        total_samples += cnt
    print("  " + "-" * 65)
    print(f"  总样本数: {total_samples:,} | 类别总数: {len(class_counts)}")

    # 保存分布文件
    dist_save_path = os.path.join(cfg.OUTPUT_DIR, "dataset_distribution.json")
    with open(dist_save_path, "w", encoding="utf-8") as f:
        json.dump(dict(class_counts), f, indent=2, ensure_ascii=False)

    return class_counts


class LeafDataset(Dataset):
    """
    作物叶片病害数据集
    同时兼容 data_dir / root_dir 两种入参，适配新旧脚本
    """
    def __init__(self, data_dir=None, root_dir=None, transform=None):
        # 兼容 root_dir 参数
        if root_dir is not None:
            data_dir = root_dir
        self.data_dir = data_dir
        self.transform = transform
        self._dataset = datasets.ImageFolder(data_dir)

        self.classes = self._dataset.classes
        self.class_to_idx = self._dataset.class_to_idx
        self.idx_to_class = {v: k for k, v in self.class_to_idx.items()}
        self.samples = self._dataset.samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]

        # 异常图片兜底：损坏/无法打开时返回空白图，不中断训练
        try:
            img = Image.open(img_path).convert("RGB")
        except Exception:
            img = Image.new("RGB", (224, 224), (255, 255, 255))

        if self.transform is not None:
            img = self.transform(img)

        return img, label


def get_dataloaders(cfg):
    """
    构建训练集/验证集 DataLoader
    增强：农业病害专属增强、Windows兼容、性能优化、可配置参数
    """
    # ===================== 1. 农业病害专属数据增强 =====================
    train_transform = T.Compose([
        T.Resize((cfg.IMAGE_SIZE + 32, cfg.IMAGE_SIZE + 32)),
        T.RandomResizedCrop(cfg.IMAGE_SIZE, scale=(0.7, 1.0)),  # 模拟叶片遮挡、局部病斑
        T.RandomHorizontalFlip(p=0.5),
        T.RandomVerticalFlip(p=0.2),
        T.RandomRotation(degrees=(-25, 25)),
        # 田间光照、阴影、色差扰动（病害场景核心增强）
        T.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.1),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = T.Compose([
        T.Resize((cfg.IMAGE_SIZE, cfg.IMAGE_SIZE)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # ===================== 2. 加载完整数据集 =====================
    full_dataset = LeafDataset(data_dir=cfg.DATA_DIR, transform=None)

    # ===================== 3. 数据集拆分（可配置比例 + 固定种子） =====================
    val_split = getattr(cfg, "VAL_SPLIT", 0.2)
    total_len = len(full_dataset)
    val_size = int(total_len * val_split)
    train_size = total_len - val_size

    # 全局种子保证可复现
    torch.manual_seed(cfg.SEED)
    generator = torch.Generator().manual_seed(cfg.SEED)
    train_dataset, val_dataset = random_split(
        full_dataset, [train_size, val_size], generator=generator
    )

    # 给拆分后的子集绑定对应增强
    train_dataset.dataset.transform = train_transform
    val_dataset.dataset.transform = val_transform

    # ===================== 4. DataLoader 性能优化 =====================
    num_workers = getattr(cfg, "NUM_WORKERS", 0)
    # Windows 强制 num_workers=0 避免多进程报错
    if os.name == "nt":
        num_workers = 0

    train_loader = DataLoader(
        dataset=train_dataset,
        batch_size=cfg.BATCH_SIZE,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        drop_last=True,
        persistent_workers=num_workers > 0  # 持久化工作进程，提速
    )

    val_loader = DataLoader(
        dataset=val_dataset,
        batch_size=cfg.BATCH_SIZE * 2,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
        drop_last=False,
        persistent_workers=num_workers > 0
    )

    return train_loader, val_loader, full_dataset


# ===================== 兼容 eval.py 接口 =====================
PlantVillageDataset = LeafDataset


def get_val_transforms(cfg):
    """获取验证集预处理，兼容评估脚本"""
    image_size = cfg.IMAGE_SIZE
    val_transform = T.Compose([
        T.Resize((image_size, image_size)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return val_transform


class SubsetWithTransform(torch.utils.data.Dataset):
    """带自定义Transform的数据集子集，用于评估集划分"""
    def __init__(self, dataset, indices, transform=None):
        self.dataset = dataset
        self.indices = indices
        self.transform = transform

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        real_idx = self.indices[idx]
        img, label = self.dataset[real_idx]
        if self.transform is not None:
            img = self.transform(img)
        return img, label