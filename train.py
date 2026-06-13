"""
训练主脚本 —— 一键启动模型训练

用法: python train.py

这个脚本做了什么（按顺序）：
1. 加载配置和数据
2. 创建模型 (迁移学习：ImageNet预训练 → 微调17类叶片)
3. 训练循环 + 验证 + 早停
4. 保存最佳模型
5. 生成训练曲线和混淆矩阵图
"""
import os
import sys
import json
import time

# 将预训练权重下载到项目本地 weights/ 目录
os.environ['TORCH_HOME'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weights')

import torch
import torch.nn as nn

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from data.dataset import get_dataloaders, analyze_dataset
from models import get_model, count_parameters
from utils import (
    EarlyStopping, train_one_epoch, validate_one_epoch,
    plot_confusion_matrix, plot_training_curves, plot_class_report
)


def main():
    cfg = Config()
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
    os.makedirs(cfg.WEIGHT_DIR, exist_ok=True)

    print("\n" + "=" * 70)
    print(" 🌿 多作物叶片病害智能诊断系统 —— 训练")
    print("=" * 70)
    print(f" 设备: {cfg.DEVICE}")
    print(f" 模型: {cfg.MODEL_NAME}")
    print(f" 类别数: {cfg.NUM_CLASSES}")
    print(f" 输入尺寸: {cfg.IMAGE_SIZE}×{cfg.IMAGE_SIZE}")
    print(f" Batch Size: {cfg.BATCH_SIZE}")
    print(f" 学习率: {cfg.LR}")
    print(f" 预训练: {cfg.PRETRAINED}")
    print("=" * 70)

    # ==================== 1. 数据分析 ====================
    print("\n[1/5] 分析数据集...")
    dist = analyze_dataset(cfg)

    # ==================== 2. 加载数据 ====================
    print("\n[2/5] 加载数据...")
    train_loader, val_loader, full_dataset = get_dataloaders(cfg)
    print(f" 训练集: {len(train_loader.dataset):,} 张")
    print(f" 验证集: {len(val_loader.dataset):,} 张")

    # ==================== 3. 创建模型 ====================
    print("\n[3/5] 创建模型...")
    model = get_model(
        model_name=cfg.MODEL_NAME,
        num_classes=cfg.NUM_CLASSES,
        pretrained=cfg.PRETRAINED,
        freeze_backbone=False  # 全量微调
    )
    model = model.to(cfg.DEVICE)

    total_p, trainable_p = count_parameters(model)
    print(f" 总参数: {total_p/1e6:.1f}M")
    print(f" 可训练: {trainable_p/1e6:.1f}M")

    # ==================== 4. 训练配置 ====================
    criterion = nn.CrossEntropyLoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=cfg.LR,
        weight_decay=cfg.WEIGHT_DECAY
    )

    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer,
        step_size=cfg.LR_STEP_SIZE,
        gamma=cfg.LR_GAMMA
    )

    best_model_path = os.path.join(cfg.WEIGHT_DIR, 'best_model.pth')
    early_stopping = EarlyStopping(
        patience=cfg.EARLY_STOP_PATIENCE,
        min_delta=cfg.EARLY_STOP_MIN_DELTA,
        save_path=best_model_path
    )

    # ==================== 5. 训练循环 ====================
    print("\n[4/5] 开始训练...")
    print("-" * 70)

    history = {
        'train_loss': [], 'val_loss': [],
        'train_acc': [], 'val_acc': []
    }
    start_time = time.time()

    for epoch in range(1, cfg.EPOCHS + 1):
        # 训练一轮
        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, cfg.DEVICE, epoch
        )

        # 验证一轮
        val_loss, val_acc, val_preds, val_labels = validate_one_epoch(
            model, val_loader, criterion, cfg.DEVICE, epoch
        )

        scheduler.step()
        current_lr = scheduler.get_last_lr()[0]

        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_acc'].append(train_acc)
        history['val_acc'].append(val_acc)

        print(f"  学习率: {current_lr:.6f}  |  "
              f"Train Loss={train_loss:.4f} Acc={train_acc:.2f}%  |  "
              f"Val Loss={val_loss:.4f} Acc={val_acc:.2f}%")

        if early_stopping(val_loss, model):
            print(f"\n ⏹ 早停在 Epoch {epoch} 触发！"
                  f"最佳 Val Loss = {early_stopping.best_loss:.4f}")
            break

    train_time = time.time() - start_time
    actual_epochs = len(history['train_loss'])
    print(f"\n ⏱ 训练完成，共 {actual_epochs} 轮，耗时 {train_time/60:.1f} 分钟")

    # ==================== 6. 保存结果 ====================
    print("\n[5/5] 生成训练结果...")

    history_path = os.path.join(cfg.OUTPUT_DIR, 'training_history.json')
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    curves_path = os.path.join(cfg.OUTPUT_DIR, 'training_curves.png')
    plot_training_curves(history, curves_path)

    # 加载最优模型评估
    model.load_state_dict(torch.load(best_model_path, weights_only=True))
    _, _, final_preds, final_labels = validate_one_epoch(
        model, val_loader, criterion, cfg.DEVICE, epoch=0
    )

    class_names = [cfg.CLASS_CN.get(cls, cls) for cls in full_dataset.classes]

    cm_path = os.path.join(cfg.OUTPUT_DIR, 'confusion_matrix.png')
    plot_confusion_matrix(final_labels, final_preds, class_names, cm_path)

    report_path = os.path.join(cfg.OUTPUT_DIR, 'class_metrics.png')
    plot_class_report(final_labels, final_preds, class_names, report_path)

    # 保存最终模型
    final_model_path = os.path.join(cfg.WEIGHT_DIR, 'final_model.pth')
    torch.save({
        'model_state_dict': model.state_dict(),
        'model_name': cfg.MODEL_NAME,
        'num_classes': cfg.NUM_CLASSES,
        'class_to_idx': full_dataset.class_to_idx,
        'idx_to_class': full_dataset.idx_to_class,
        'classes': full_dataset.classes,
        'image_size': cfg.IMAGE_SIZE,
    }, final_model_path)

    # 训练总结
    print("\n" + "=" * 70)
    print(" 🎉 训练完成!")
    print("=" * 70)
    best_epoch = history['val_loss'].index(min(history['val_loss'])) + 1
    print(f" 最佳 Epoch: {best_epoch}")
    print(f" 最佳 Val Accuracy: {max(history['val_acc']):.2f}%")
    print(f" 最佳 Val Loss: {min(history['val_loss']):.4f}")
    print(f" 模型保存: {best_model_path}")
    print(f" 输出目录: {cfg.OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()