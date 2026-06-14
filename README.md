# 🌿 多作物叶片病害智能诊断系统

> AI 作物病害诊断 + 博客 + 音乐播放 + 个人网站

## ✨ 功能

| 模块 | 功能 |
|------|------|
| 🌿 **病害诊断** | 拍照/上传 → ResNet18 识别 39 种病害 → 严重度 → 防治建议 → 热力图 |
| ✍️ **博客** | Markdown 写文章、分类、匿名评论、20 张随机封面 |
| 🎵 **音乐** | 网易云歌单 + 本地 13 首歌、歌词滚动、频谱跳动 |
| 👤 **用户** | 注册登录、JWT、7天免登录、个人中心 |
| 💬 **留言板** | 公共留言、可删自己的 |
| 🐱 **月薪喵** | Python 终端动画 (ttyd) |
| 🛡️ **管理员** | 杜越可管理所有文章 |
| 📊 **历史** | 诊断记录、Excel 导出 |

## 🏗️ 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + Vuetify 3 + Vite |
| 后端 | FastAPI + SQLAlchemy + SQLite |
| 模型 | PyTorch ResNet18 (ONNX 加速) |
| 部署 | Nginx + Ubuntu 22.04 腾讯云 Lighthouse |

## 📁 项目结构

```
crop-disease-diagnosis/
├── server/                    # FastAPI 后端
│   ├── main.py                # 入口
│   ├── config.py              # 配置
│   ├── database.py            # SQLite
│   ├── models/db_models.py    # ORM
│   ├── schemas/schemas.py     # Pydantic
│   ├── routers/               # API 路由
│   │   ├── auth.py            # 认证
│   │   ├── predict.py         # 诊断
│   │   ├── blog.py            # 博客
│   │   ├── feedback.py        # 反馈
│   │   ├── guestbook.py       # 留言板
│   │   └── export.py          # 导出
│   ├── services/              # 业务层
│   │   ├── auth_service.py    # JWT
│   │   └── predict_service.py # 推理
│   └── utils/                 # 工具
│       ├── grad_cam.py        # 热力图
│       └── severity.py        # 严重度
│
├── frontend/components/disease/  # Vue 诊断组件
├── models/                    # 模型定义
├── config/                    # 训练配置
├── data/                      # 数据集
├── utils/                     # 训练工具
├── weights/                   # 模型权重(不上传)
├── train.py                   # 训练脚本
├── eval.py                    # 评估
├── admin.py                   # 管理工具
└── docker-compose.yml         # Docker
```

## 🚀 快速启动

```bash
# 后端
pip install fastapi uvicorn sqlalchemy python-jose passlib python-multipart openpyxl pillow onnxruntime torch torchvision
cd crop-disease-diagnosis
python -m server.main

# 前端 (另一个仓库 leleo-home-page)
cd leleo-home-page
npm install && npx vite --host 0.0.0.0
```

## 🛠️ 管理员

```bash
python admin.py users        # 查看用户
python admin.py reset 用户名 密码  # 重置密码
```

## 📊 模型

| 指标 | 数值 |
|------|------|
| 模型 | ResNet18 |
| 类别 | 39 种 |
| 准确率 | 99.4% |
| 推理 | ~60ms (ONNX CPU) |

## 🌐 在线地址

http://119.91.113.191

## 📝 License

MIT
