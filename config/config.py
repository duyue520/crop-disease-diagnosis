"""
全局配置文件 —— 所有超参数和路径集中管理
"""
import os
import torch

class Config:
    # ==================== 路径配置 ====================
    # 数据集根目录 (嵌套结构: 作物/病害类别/图片)
    DATASET_ROOT = r"F:/22/Plant_leave_diseases_dataset_without_augmentation"
    DATA_DIR = DATASET_ROOT  # 别名，供 dataset.py 使用

    # 项目输出目录
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
    WEIGHT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "weights")

    # ==================== 模型配置 ====================
    MODEL_NAME = "resnet18"      # 可选: resnet18, resnet34, resnet50, efficientnet_b0
    NUM_CLASSES = 39             # 14种作物共39个病害/健康类别（含背景类）
    PRETRAINED = True            # 使用 ImageNet 预训练权重 (迁移学习核心)

    # ==================== 训练配置 (GPU 优化) ====================
    IMAGE_SIZE = 224             # 输入尺寸 (ResNet/EfficientNet 标准输入)
    BATCH_SIZE = 32              # GPU 推荐32，显存不足改为16
    EPOCHS = 10                  # 训练轮数
    LR = 0.001                   # 初始学习率
    WEIGHT_DECAY = 1e-4          # L2 正则化系数 (防止过拟合)
    NUM_WORKERS = 2              # Windows GPU 建议 0/2，避免多进程报错
    SEED = 42                    # 随机种子（保证实验可复现）
    VAL_SPLIT = 0.2              # 验证集划分比例

    # 学习率调度
    LR_STEP_SIZE = 7             # 每7个epoch学习率衰减一次
    LR_GAMMA = 0.1               # 衰减为原来的0.1倍

    # 早停策略
    EARLY_STOP_PATIENCE = 10     # 验证集loss连续10轮不降则停止
    EARLY_STOP_MIN_DELTA = 0.001 # 最小改善阈值

    # ==================== 数据增强配置 ====================
    # 训练集增强 (模拟真实拍摄场景: 不同角度/光照)
    TRAIN_AUGMENT = {
        "random_horizontal_flip": 0.5,
        "random_vertical_flip": 0.1,    # 叶片方向不确定
        "random_rotation": 30,           # ±30度旋转
        "color_jitter": {                # 颜色抖动 (光照变化)
            "brightness": 0.3,
            "contrast": 0.3,
            "saturation": 0.3,
            "hue": 0.1
        },
        "random_affine": {              # 仿射变换
            "degrees": 0,
            "translate": (0.1, 0.1),    # 平移
            "scale": (0.9, 1.1)         # 缩放
        }
    }

    # ==================== 设备配置 (GPU/CPU 自动切换) ====================
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # ==================== 类别信息 ====================
    # 按作物分组的类别 (方便后续分析和可视化)
    CROP_CLASSES = {
        "苹果 Apple": ["Apple___Apple_scab", "Apple___Black_rot",
                       "Apple___Cedar_apple_rust", "Apple___healthy"],
        "蓝莓 Blueberry": ["Blueberry___healthy"],
        "樱桃 Cherry": ["Cherry___Powdery_mildew", "Cherry___healthy"],
        "玉米 Corn": ["Corn___Cercospora_leaf_spot Gray_leaf_spot",
                     "Corn___Common_rust", "Corn___Northern_Leaf_Blight",
                     "Corn___healthy"],
        "葡萄 Grape": ["Grape___Black_rot", "Grape___Esca_(Black_Measles)",
                      "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy"],
        "橙子 Orange": ["Orange___Haunglongbing_(Citrus_greening)"],
        "桃子 Peach": ["Peach___Bacterial_spot", "Peach___healthy"],
        "甜椒 Pepper": ["Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy"],
        "马铃薯 Potato": ["Potato___Early_blight", "Potato___Late_blight",
                         "Potato___healthy"],
        "覆盆子 Raspberry": ["Raspberry___healthy"],
        "大豆 Soybean": ["Soybean___healthy"],
        "南瓜 Squash": ["Squash___Powdery_mildew"],
        "草莓 Strawberry": ["Strawberry___Leaf_scorch", "Strawberry___healthy"],
        "番茄 Tomato": ["Tomato___Bacterial_spot", "Tomato___Early_blight",
                        "Tomato___Late_blight", "Tomato___Leaf_Mold",
                        "Tomato___Septoria_leaf_spot",
                        "Tomato___Spider_mites Two-spotted_spider_mite",
                        "Tomato___Target_Spot",
                        "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
                        "Tomato___Tomato_mosaic_virus", "Tomato___healthy"],
        "背景 Background": ["Background_without_leaves"],
    }

    # 病害中文对照 (用于结果展示)
    CLASS_CN = {
        "Apple___Apple_scab": "苹果疮痂病",
        "Apple___Black_rot": "苹果黑腐病",
        "Apple___Cedar_apple_rust": "苹果锈病",
        "Apple___healthy": "苹果健康",
        "Background_without_leaves": "背景（无叶片）",
        "Blueberry___healthy": "蓝莓健康",
        "Cherry___Powdery_mildew": "樱桃白粉病",
        "Cherry___healthy": "樱桃健康",
        "Corn___Cercospora_leaf_spot Gray_leaf_spot": "玉米灰叶斑病",
        "Corn___Common_rust": "玉米普通锈病",
        "Corn___Northern_Leaf_Blight": "玉米北方叶枯病",
        "Corn___healthy": "玉米健康",
        "Grape___Black_rot": "葡萄黑腐病",
        "Grape___Esca_(Black_Measles)": "葡萄黑麻疹病",
        "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "葡萄叶枯病",
        "Grape___healthy": "葡萄健康",
        "Orange___Haunglongbing_(Citrus_greening)": "柑橘黄龙病",
        "Peach___Bacterial_spot": "桃细菌性斑点病",
        "Peach___healthy": "桃健康",
        "Pepper,_bell___Bacterial_spot": "甜椒细菌性斑点病",
        "Pepper,_bell___healthy": "甜椒健康",
        "Potato___Early_blight": "马铃薯早疫病",
        "Potato___Late_blight": "马铃薯晚疫病",
        "Potato___healthy": "马铃薯健康",
        "Raspberry___healthy": "覆盆子健康",
        "Soybean___healthy": "大豆健康",
        "Squash___Powdery_mildew": "南瓜白粉病",
        "Strawberry___Leaf_scorch": "草莓叶枯病",
        "Strawberry___healthy": "草莓健康",
        "Tomato___Bacterial_spot": "番茄细菌性斑点病",
        "Tomato___Early_blight": "番茄早疫病",
        "Tomato___Late_blight": "番茄晚疫病",
        "Tomato___Leaf_Mold": "番茄叶霉病",
        "Tomato___Septoria_leaf_spot": "番茄斑枯病",
        "Tomato___Spider_mites Two-spotted_spider_mite": "番茄红蜘蛛",
        "Tomato___Target_Spot": "番茄靶斑病",
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "番茄黄化曲叶病毒病",
        "Tomato___Tomato_mosaic_virus": "番茄花叶病毒病",
        "Tomato___healthy": "番茄健康",
    }


def get_config():
    """获取配置单例"""
    return Config()