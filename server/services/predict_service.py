"""
推理服务 —— 加载模型 + 图片预处理 + 预测
"""
import io
import os
import sys
import time
import base64
import torch
import torch.nn.functional as F
import torchvision.transforms as T
import numpy as np
from PIL import Image
from typing import Tuple, Optional

# 将项目根目录加入 sys.path（server/ 的上一级）
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from server.config import (
    MODEL_PATH, NUM_CLASSES, IMAGE_SIZE, MODEL_NAME,
    DISEASE_ADVICE, CLASS_CN, DATA_DIR,
)
from server.utils.severity import estimate_severity
from server.utils.grad_cam import generate_gradcam

# 内联模型工厂 (避免 server/models 与 models/ 命名冲突)
def _get_model(model_name='resnet18', num_classes=39, pretrained=False):
    """模型工厂函数"""
    import torch.nn as nn
    import torchvision.models as vision_models

    if model_name == 'resnet18':
        model = vision_models.resnet18(weights=None)
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, num_classes)
    elif model_name == 'resnet34':
        model = vision_models.resnet34(weights=None)
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, num_classes)
    elif model_name == 'resnet50':
        model = vision_models.resnet50(weights=None)
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, num_classes)
    elif model_name == 'efficientnet_b0':
        model = vision_models.efficientnet_b0(weights=None)
        in_features = model.classifier[-1].in_features
        model.classifier[-1] = nn.Linear(in_features, num_classes)
    else:
        raise ValueError(f"不支持的模型: {model_name}")
    return model

# 全局模型单例
_model = None
_device = None
_class_names = None


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model():
    """延迟加载模型（首次调用时加载）"""
    global _model, _device, _class_names
    if _model is None:
        _device = get_device()
        _model = _get_model(MODEL_NAME, NUM_CLASSES, pretrained=False)
        state = torch.load(MODEL_PATH, map_location=_device, weights_only=True)
        if isinstance(state, dict) and "model_state_dict" in state:
            state = state["model_state_dict"]
        _model.load_state_dict(state)
        _model.to(_device)
        _model.eval()
        print(f" [OK] 模型已加载到 {_device}")
    return _model, _device


def get_transform():
    """图片预处理（与训练时验证集一致）"""
    return T.Compose([
        T.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def load_class_names() -> list:
    """加载数据集的类别名列表"""
    try:
        from data.dataset import LeafDataset
        if os.path.exists(DATA_DIR):
            ds = LeafDataset(DATA_DIR, transform=None)
            return ds.classes
    except Exception:
        pass
    # fallback: 用 CLASS_CN 的 keys 生成类名列表
    return list(CLASS_CN.keys())


def predict(image_bytes: bytes, top_k: int = 3, enable_gradcam: bool = False) -> dict:
    """
    对单张图片进行推理
    """
    model, device = load_model()
    transform = get_transform()
    class_names = load_class_names()
    cn_map = CLASS_CN

    # 预处理
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    original_img = img.copy()
    input_tensor = transform(img).unsqueeze(0).to(device)

    # 推理
    start = time.time()
    with torch.no_grad():
        output = model(input_tensor)
        probs = F.softmax(output, dim=1)
        top_probs, top_indices = torch.topk(probs, top_k, dim=1)

    inference_time = (time.time() - start) * 1000

    top_probs = top_probs.squeeze().cpu().numpy()
    top_indices = top_indices.squeeze().cpu().numpy()

    if top_k == 1:
        top_probs = [top_probs.item()]
        top_indices = [top_indices.item()]

    predictions = []
    for i in range(len(top_probs)):
        cls_idx = int(top_indices[i])
        cls_name = str(class_names[cls_idx]) if cls_idx < len(class_names) else f"class_{cls_idx}"
        predictions.append({
            "rank": i + 1,
            "disease_cn": cn_map.get(cls_name, cls_name),
            "disease_en": cls_name,
            "confidence": round(float(top_probs[i]) * 100, 2),
        })

    # 判断是否健康
    top1_name = str(class_names[int(top_indices[0])]) if top_indices[0] < len(class_names) else ""
    is_healthy = "healthy" in top1_name.lower()

    # 严重度估算
    severity, severity_pct = estimate_severity(original_img, is_healthy)

    # 防治建议
    top1_cn = cn_map.get(top1_name, top1_name)
    advices = DISEASE_ADVICE.get(top1_cn, {"pesticide": "请咨询当地农技站", "method": "建议联系农业专家进一步确认"})

    # Grad-CAM
    grad_cam_b64 = None
    if enable_gradcam:
        grad_cam_b64 = generate_gradcam(model, input_tensor, original_img, target_layer="layer4")

    return {
        "predictions": predictions,
        "is_healthy": is_healthy,
        "severity": severity,
        "severity_percent": severity_pct,
        "advices": advices,
        "grad_cam_base64": grad_cam_b64,
        "inference_time_ms": round(inference_time, 2),
    }
