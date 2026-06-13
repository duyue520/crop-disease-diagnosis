"""
病害严重度估算 —— 基于图像分割的病斑面积占比
"""
import numpy as np
from PIL import Image


def estimate_severity(image: Image.Image, is_healthy: bool = False) -> tuple:
    """
    估算叶片病害严重度

    方法：在 HSV 颜色空间中分离绿色（健康叶片）和非绿色（病斑/病变区域），
    计算病斑面积占比。

    Args:
        image: PIL 图片
        is_healthy: 模型是否已判断为健康

    Returns:
        (severity_label: str, severity_percent: float)
        severity_label: "healthy" | "mild" | "moderate" | "severe"
    """
    if is_healthy:
        return "healthy", 0.0

    try:
        # 转为 numpy + HSV
        img_np = np.array(image.convert("RGB"))
        hsv = np.array(Image.fromarray(img_np).convert("HSV"))

        # 绿色范围 (H: 35-85)
        lower_green = np.array([30, 40, 40])
        upper_green = np.array([90, 255, 255])

        green_mask = cv2_in_range(hsv, lower_green, upper_green)

        # 叶片区域（非背景，饱和度/亮度较高的像素）
        saturation = hsv[:, :, 1]
        brightness = hsv[:, :, 2]
        leaf_mask = (saturation > 20) & (brightness > 30)

        if leaf_mask.sum() < 100:
            return "mild", 0.0

        # 病斑 = 叶片区域 - 绿色区域
        diseased_mask = leaf_mask.astype(int) - green_mask.astype(int)
        diseased_mask = np.clip(diseased_mask, 0, 1)

        total_leaf_pixels = leaf_mask.sum()
        diseased_pixels = diseased_mask.sum()

        severity_pct = round(diseased_pixels / total_leaf_pixels * 100, 1) if total_leaf_pixels > 0 else 0.0

        # 分级
        if severity_pct < 5:
            label = "mild"
        elif severity_pct < 20:
            label = "moderate"
        else:
            label = "severe"

        return label, severity_pct

    except Exception as e:
        print(f" [WARN] 严重度估算失败: {e}")
        return "mild", 0.0


def cv2_in_range(hsv, lower, upper):
    """纯 numpy 模拟 cv2.inRange，避免依赖 opencv-python 版本问题"""
    mask = np.all(hsv >= lower, axis=2) & np.all(hsv <= upper, axis=2)
    return mask.astype(np.uint8)
