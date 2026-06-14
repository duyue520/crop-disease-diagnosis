# 🌿 多作物叶片病害智能诊断系统

> AI 作物病害诊断 + 博客 + 音乐播放器 + 个人网站
> 
> 🌐 在线地址: http://119.91.113.191

## ✨ 功能

| 模块 | 功能 |
|------|------|
| 🌿 **病害诊断** | 拍照/上传 → ResNet18 识别 39 种病害 → 严重度 → 防治建议 → 热力图 |
| ✍️ **博客** | Markdown 写文章、分类、匿名评论、随机封面 |
| 🎵 **音乐** | 本地 13 首歌 + 网易云歌单、流式歌词、频谱跳动 |
| 👤 **用户** | 注册登录、JWT 7天免登录、个人中心 |
| 💬 **留言板** | 公共留言、可删自己的 |
| 🐱 **月薪喵** | Python 终端动画 (ttyd) |
| 🛡️ **管理** | 杜越 管理员可删所有文章/评论 |

## 🏗️ 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + Vuetify 3 + Vite |
| 后端 | FastAPI + SQLAlchemy + SQLite |
| 模型 | PyTorch ResNet18 (ONNX 加速 ~60ms) |
| 部署 | Nginx + Ubuntu 22.04 腾讯云 Lighthouse 2核2G |

## 📁 项目结构

```
crop-disease-diagnosis/
├── server/                    # FastAPI 后端 (17 个 API 端点)
│   ├── main.py                # 入口
│   ├── config.py              # 配置
│   ├── database.py            # SQLite
│   ├── models/db_models.py    # ORM
│   ├── schemas/schemas.py     # Pydantic
│   ├── routers/               # 路由
│   │   ├── auth.py            # 认证 (注册/登录/改密码/个人中心)
│   │   ├── predict.py         # 病害诊断
│   │   ├── blog.py            # 博客 CRUD + 评论
│   │   ├── feedback.py        # 反馈 + 纠错
│   │   ├── guestbook.py       # 留言板
│   │   └── export.py          # Excel 导出
│   ├── services/              # 业务逻辑
│   └── utils/                 # 工具 (Grad-CAM, 严重度)
│
├── frontend/                  # Vue 组件
│   └── components/disease/    # 诊断、博客、音乐等组件
│
├── models/  config/  data/  utils/  # 训练相关
├── weights/                   # 模型权重 (不上传)
├── train.py                   # 训练脚本
├── eval.py                    # 评估
├── admin.py                   # 管理工具
└── docker-compose.yml         # Docker
```

## 🚀 启动

```bash
# 后端
pip install fastapi uvicorn sqlalchemy python-jose passlib python-multipart openpyxl pillow onnxruntime torch torchvision
python -m server.main

# 前端 (另见 leleo-home-page 仓库)
npm install && npx vite --host 0.0.0.0
```

## 🛠️ 管理

```bash
python admin.py              # 交互菜单
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

## 📝 License

MIT
