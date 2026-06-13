"""
Grad-CAM 可视化 —— 展示模型关注的叶片区域
"""
import io
import base64
import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
import cv2


def generate_gradcam(model, input_tensor, original_img, target_layer="layer4", image_size=224):
    """
    生成 Grad-CAM 热力图

    原理（面试重点）：
    1. 前向传播时，hook 目标层的特征图
    2. 反向传播时，计算目标类别对该层特征的梯度
    3. 全局平均池化梯度 → 得到每个通道的重要性权重
    4. 加权求和 + ReLU → 热力图

    Args:
        model: PyTorch 模型
        input_tensor: 已预处理的输入 (1, 3, 224, 224)
        original_img: 原始 PIL Image
        target_layer: 目标卷积层
        image_size: 图片尺寸

    Returns:
        base64 编码的热力图叠加图
    """
    try:
        # 找到目标层
        layer = None
        for name, module in model.named_modules():
            if target_layer in name and isinstance(module, torch.nn.Conv2d):
                layer = module
                break

        if layer is None:
            # fallback: 用最后一个卷积层
            for name, module in model.named_modules():
                if "conv" in name.lower() or "layer4" in name:
                    layer = module
            if layer is None:
                return None

        activations = {}
        gradients = {}

        def forward_hook(module, input, output):
            activations["value"] = output

        def backward_hook(module, grad_input, grad_output):
            gradients["value"] = grad_output[0]

        forward_handle = layer.register_forward_hook(forward_hook)
        backward_handle = layer.register_backward_hook(backward_hook)

        # 前向
        model.zero_grad()
        output = model(input_tensor)
        pred_class = output.argmax(dim=1).item()

        # 反向传播目标类
        one_hot = torch.zeros_like(output)
        one_hot[0, pred_class] = 1
        output.backward(gradient=one_hot, retain_graph=True)

        # 获取激活和梯度
        act = activations["value"].detach()  # (1, C, H, W)
        grad = gradients["value"].detach()    # (1, C, H, W)

        # 全局平均池化梯度 → 权重
        weights = grad.mean(dim=(2, 3), keepdim=True)  # (1, C, 1, 1)

        # 加权求和 + ReLU
        cam = (weights * act).sum(dim=1, keepdim=True)
        cam = F.relu(cam)  # (1, 1, H, W)

        # 归一化
        cam = cam - cam.min()
        cam = cam / (cam.max() + 1e-8)

        # 上采样到原图大小
        cam = F.interpolate(cam, size=(image_size, image_size), mode="bilinear", align_corners=False)
        cam = cam.squeeze().cpu().numpy()

        # 与原图叠加
        original_resized = original_img.resize((image_size, image_size))
        original_np = np.array(original_resized)

        # 生成热力图
        heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

        # 叠加: 热力图 0.4 + 原图 0.6
        overlay = (heatmap * 0.4 + original_np * 0.6).astype(np.uint8)

        # 编码为 base64
        overlay_img = Image.fromarray(overlay)
        buf = io.BytesIO()
        overlay_img.save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode()

        # 清理 hooks
        forward_handle.remove()
        backward_handle.remove()

        return b64

    except Exception as e:
        print(f" [WARN] Grad-CAM 生成失败: {e}")
        return None
