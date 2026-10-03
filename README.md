# 🌿 多作物叶片病害智能诊断系统

> 基于 **ResNet18 迁移学习** 的叶片病害识别系统：**15 种作物 · 39 个类别（含健康类）**，支持图片上传、批量诊断、热力图可视、严重度分级，并提供 FastAPI 接口与 Web 前端。
>
> 训练集 55,448 张叶片图像，验证集准确率 **99.40%**（10 epoch，见 [docs/分析报告.md](docs/分析报告.md)）

## 🔗 在线体验

**https://heyiwei.tech** —— 打开网站，进入「🌿 叶片病害诊断」卡片，上传叶片照片即可查看识别结果、热力图与严重度。

---

## 一、这个项目解决什么问题

农民/农技人员看到一片有斑点的叶子，往往需要经验判断是什么病、要不要打药。本系统用深度学习做三件事：

1. **识别病名** —— 输入叶片照片，输出最可能的病害（Top-3 置信度）+ 防治建议
2. **定位病斑** —— 输出热力图，标出模型关注的区域
3. **评估严重度** —— 用颜色分割估算病斑占叶面积比例，分为 轻度 / 中度 / 重度

支持 15 种作物：苹果、蓝莓、樱桃、玉米、葡萄、橙子、桃子、甜椒、马铃薯、树莓、大豆、南瓜、草莓、番茄、以及背景类。

---

## 二、神经网络架构（核心）

### 2.1 整体架构

```
                        输入叶片图像 (任意尺寸 RGB)
                                  │
                    ┌─────────────▼─────────────┐
                    │      预处理 / 增强管线      │
                    │  Resize(256) → RandomResizedCrop(224, 0.7~1.0)
                    │  HFlip(0.5) / VFlip(0.2) / Rotate(±25°)
                    │  ColorJitter(0.3/0.3/0.2/0.1) → ImageNet 标准化
                    └─────────────┬─────────────┘
                                  │  224×224×3
                    ┌─────────────▼─────────────┐
                    │   ResNet18 骨干（ImageNet 预训练）
                    │   conv1 7×7/2 → maxpool
                    │   layer1  2×BasicBlock  64 通道
                    │   layer2  2×BasicBlock 128 通道  (stride 2)
                    │   layer3  2×BasicBlock 256 通道  (stride 2)
                    │   layer4  2×BasicBlock 512 通道  (stride 2)
                    │   GlobalAvgPool → 512-d 特征向量
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │  全连接层 512 → 39         │
                    │  Softmax → 类别概率        │
                    └─────────────┬─────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
    病名 + Top-3 置信度       Grad-CAM 热力图          严重度分级
                                                     (HSV 病斑占比)
```

### 2.2 为什么选 ResNet18

| 方案 | 参数量 | 本任务适合度 | 说明 |
|---|---|---|---|
| **ResNet18（本项目）** | 11.2 M | ★★★★☆ | 迁移学习性价比最高，CPU 也能跑，ONNX 导出后单张推理约数十毫秒 |
| ResNet34/50 | 21.8 M / 25.6 M | ★★★☆☆ | 精度提升有限（本数据集已近饱和），推理更慢 |
| EfficientNet-B0 | 5.3 M | ★★★★☆ | 参数更少、精度接近，移动端更友好 |
| MobileNetV3-Small | 2.5 M | ★★★★★ | 手机端首选，精度略低 1~2 个百分点 |
| ConvNeXt-Tiny | 28 M | ★★★★☆ | 若追求极致精度可换，需 GPU 训练 |

**关键点：残差连接（Skip Connection）**。ResNet 用 `y = F(x) + x` 让梯度可以直接回传，因此 18 层也能稳定训练；相比普通 CNN，它避免了深层网络的退化问题，同时保留了较浅网络的速度。

### 2.3 迁移学习策略

- 骨干网络加载 **ImageNet 预训练权重**（`pretrained=True`）
- **全量微调**（`freeze_backbone=False`）—— 叶片纹理与 ImageNet 自然图像差异大，解冻全部层效果更好
- 替换最后的全连接层：`512 → 39`（类别数），随机初始化
- 实测：仅 10 个 epoch 即收敛到 99.4% 验证准确率（见分析报告）

### 2.4 训练配置

| 项目 | 取值 | 说明 |
|---|---|---|
| 损失函数 | `CrossEntropyLoss` | 多分类标准损失 |
| 优化器 | `Adam(lr=1e-3)` | 自适应学习率，收敛快 |
| 学习率调度 | `StepLR(step=7, gamma=0.1)` | 第 7 epoch 后降为 0.1 倍（此步带来显著跃升） |
| Batch Size | 32 | 显存不足可降为 16 |
| Epochs | 10 | 配合 EarlyStopping 防止过拟合 |
| 输入尺寸 | 224×224 | ResNet 标准输入 |
| 验证集比例 | 20% | `random_split` |
| 早停 | `EarlyStopping` | 验证指标不再提升时停止并回滚最优权重 |

### 2.5 数据增强设计（为什么这样设计）

```python
train_transform = T.Compose([
    T.Resize((256, 256)),
    T.RandomResizedCrop(224, scale=(0.7, 1.0)),   # 模拟叶片遮挡、局部病斑取景
    T.RandomHorizontalFlip(p=0.5),                # 叶片方向随机
    T.RandomVerticalFlip(p=0.2),
    T.RandomRotation(degrees=(-25, 25)),          # 拍摄角度抖动
    T.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.1),  # 光照/色温差异
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),    # ImageNet 统计
])
```

> 每一条增强都对应一个真实拍摄场景：**裁剪缩放**对应"只拍一片叶子"；**翻转旋转**对应"随手拍"；**颜色抖动**对应"阴天/正午/白平衡"。这是提升田间泛化最廉价有效的手段。

---

## 三、推理链路

```
图片 → 预处理(Resize224 + ImageNet 标准化)
     → ONNX Runtime（优先）/ PyTorch（回退）推理
     → Softmax 概率 → Top-3 病名
     → Grad-CAM 热力图（定位病斑区域）
     → HSV 病斑分割 → 严重度百分比 → 轻/中/重
```

**严重度算法**（`server/utils/severity.py`）：

1. RGB → HSV 空间
2. 绿色掩码（H 30~90）→ 代表健康叶片组织
3. 叶片掩码（S > 20 且 V > 30）→ 排除背景
4. 病斑像素 = 叶片 − 绿色 → `严重度 = 病斑 / 叶片面积`
5. 分级：< 5% 轻度 ｜ 5%~20% 中度 ｜ ≥ 20% 重度

> 该方法是**启发式估算**，不是分割模型的输出，因此对紫色/红色品种叶片、复杂背景会偏大。详见分析报告"局限与改进"。

---

## 四、目录结构

```
crop-disease-diagnosis/
├── config/
│   └── config.py              # 全局配置：模型名、类别表、超参数、路径
├── data/
│   └── dataset.py             # 数据集加载、增强管线、训练/验证划分
├── utils/
│   ├── train_utils.py         # 训练/验证单轮循环、EarlyStopping、指标统计
│   └── plot_utils.py          # 训练曲线、混淆矩阵、类别指标绘图
├── models/                    # 模型构建（backbone + 分类头）
├── train.py                   # 训练入口
├── eval.py                    # 验证集评估（混淆矩阵 / 分类报告）
├── inference.py               # 单图推理（Top-K + 结果可视化）
├── generate_report.py         # 生成训练报告与图表
├── weights/
│   ├── best_model.onnx        # 导出好的 ONNX 模型（可直接推理，42.7MB）
│   └── model.onnx
├── outputs/                   # 训练产物：曲线、混淆矩阵、类别指标、数据集分布
├── server/                    # FastAPI 后端（预测接口 + 站点业务接口）
│   ├── main.py                # 应用入口
│   ├── routers/predict.py     # /predict、/predict/batch、/health
│   ├── services/predict_service.py  # 模型加载（ONNX 优先）+ 推理
│   ├── utils/severity.py      # 严重度估算
│   └── Dockerfile
├── frontend/                  # Web 前端（Vue）
├── demo/                      # 示例图片
├── docs/
│   ├── 技术报告.md             # 架构 / 网络 / 训练 / 推理 技术细节
│   └── 分析报告.md             # 数据集分析 / 训练分析 / 模型强度评估 / 改进路线
├── docker-compose.yml
└── requirements.txt
```

---

## 五、快速开始

### 5.1 环境要求

- Python 3.10+（推荐 3.11）
- 可选：CUDA GPU（CPU 也能推理，本项目默认 CPU 推理）
- Node.js 18+（仅前端需要）

### 5.2 安装依赖

```bash
git clone https://github.com/duyue520/crop-disease-diagnosis.git
cd crop-disease-diagnosis
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> 仓库已内置训练好的 `weights/*.onnx`，**不训练也能直接推理**。

### 5.3 单张图片推理

```bash
python inference.py --image demo/sugarcane_red_rot.jpg
```

### 5.4 启动 API 服务

```bash
cd server
uvicorn main:app --host 0.0.0.0 --port 8000
# 打开 http://localhost:8000/docs 查看接口文档
```

### 5.5 Docker 一键起

```bash
cp .env.example .env      # 按需修改 SECRET_KEY 等
docker compose up -d
```

### 5.6 自行训练

```bash
# 1) 准备数据（ImageFolder 结构：data/raw/<类别名>/*.jpg）
# 2) 修改 config/config.py 中的路径与超参
python train.py           # 训练 → 保存 best 权重 + outputs/ 曲线
python eval.py            # 评估 → 混淆矩阵 / 分类报告
python generate_report.py # 生成图表报告
```

**数据集准备（ImageFolder 结构）**：

```
data/raw/
├── Apple___Apple_scab/          # 目录名 = 类别名（与 config.CROP_CLASSES 对应）
│   ├── 001.jpg
│   └── ...
├── Tomato___Late_blight/
└── ...
```

---

## 六、API 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/predict` | 单图诊断：上传图片 → 病名 + 置信度 + 严重度 + Top-3 |
| POST | `/api/predict/batch` | 批量诊断（多图） |
| GET | `/api/health` | 健康检查 |

调用示例：

```bash
curl -X POST http://localhost:8000/api/predict \
  -F "file=@demo/wheat_yellow_rust.jpg"
```

---

## 七、常见问题

**Q1：验证准确率 99%+，为什么我拍的叶子识别不准？**
A：数据集是实验室条件下的单叶图像（背景干净、光照均匀）。田间照片有土壤背景、遮挡、复杂光照，会显著掉点。请尽量让叶片占画面主体、背景单一。改进方向见 [docs/分析报告.md](docs/分析报告.md)。

**Q2：能识别多少种作物？**
A：15 种作物、39 个类别（含各类的健康叶片）。具体类别见 `config/config.py` 的 `CROP_CLASSES`。

**Q3：没有 GPU 能跑吗？**
A：可以。ONNX Runtime 在 CPU 上单张推理通常几十毫秒，本项目默认就是 CPU 推理。

**Q4：想换更轻/更强的模型？**
A：改 `config/config.py` 的 `MODEL_NAME`：`resnet18 / resnet34 / resnet50 / efficientnet_b0`，然后重新训练即可（模型构建见 `models/`）。

**Q5：怎么加新病害类别？**
A：① 新增数据目录（目录名即类别名）；② 更新 `config/config.py` 的 `CROP_CLASSES` 与 `CLASS_CN`；③ 修改 `NUM_CLASSES`；④ 重新训练。

---

## 八、模型强度评估（结论速览）

| 维度 | 结论 |
|---|---|
| 本数据集准确率 | 验证集 **99.40%**（10 epoch），属于该数据集的上限水平 |
| 田间泛化 | ⚠️ **主要短板**：实验室→田间存在域偏移，需补田间数据/强增强 |
| 类别不平衡 | ⚠️ 最多 5,507 张 vs 最少 152 张（36×），少数类需加权 |
| 非叶片拒识 | ⚠️ 无 OOD 机制，非叶片图片也会被强行分类 |
| 推理效率 | ✅ ONNX + CPU 可跑；可 int8 量化到 ~11MB |

详细分析与改进路线见 **[docs/分析报告.md](docs/分析报告.md)**。

---

## 九、免责声明

- 本项目为**学习与研究用途**，诊断结果仅供参考，**不能替代专业植保人员的判断**。
- 数据集来自公开的 PlantVillage 类叶片图像；训练权重随仓库分发，请遵守原数据集许可。
- 实际用药请以当地农技部门指导为准。

## 十、许可

[MIT License](LICENSE)
