"""
后端服务配置
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

# 数据库
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"

# JWT
SECRET_KEY = os.environ.get("SECRET_KEY", "crop-disease-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 天

# 模型
MODEL_PATH = os.path.join(PROJECT_DIR, "weights", "best_model.pth")
NUM_CLASSES = 39
IMAGE_SIZE = 224
MODEL_NAME = "resnet18"

# 上传
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "bmp"}

# CORS
CORS_ORIGINS = ["*"]

# 防治建议库
DISEASE_ADVICE = {
    "苹果疮痂病": {"pesticide": "苯醚甲环唑、吡唑醚菌酯", "method": "清除病叶，发病初期喷药，间隔7-10天喷1次，连续2-3次"},
    "苹果黑腐病": {"pesticide": "甲基硫菌灵、多菌灵", "method": "剪除病枝病果，休眠期喷石硫合剂清园"},
    "苹果锈病": {"pesticide": "三唑酮、戊唑醇", "method": "铲除附近桧柏等转主寄主，花后喷药保护"},
    "苹果健康": {"pesticide": "无需用药", "method": "保持良好管理，定期巡查"},
    "背景（无叶片）": {"pesticide": "—", "method": "请上传含有叶片的图片"},
    "蓝莓健康": {"pesticide": "无需用药", "method": "保持土壤酸性，合理灌溉"},
    "樱桃白粉病": {"pesticide": "硫磺制剂、嘧菌酯", "method": "加强通风透光，发病初期喷药防治"},
    "樱桃健康": {"pesticide": "无需用药", "method": "合理修剪，保持树体通风透光"},
    "玉米灰叶斑病": {"pesticide": "吡唑醚菌酯、嘧菌酯", "method": "合理密植，增施磷钾肥，发病初期喷药保护"},
    "玉米普通锈病": {"pesticide": "三唑酮、戊唑醇", "method": "选用抗病品种，发病初期喷雾防治"},
    "玉米北方叶枯病": {"pesticide": "苯醚甲环唑、代森锰锌", "method": "清除田间病残体，合理轮作，大喇叭口期开始喷药"},
    "玉米健康": {"pesticide": "无需用药", "method": "合理施肥灌溉，定期巡查"},
    "葡萄黑腐病": {"pesticide": "代森锰锌、嘧菌酯", "method": "清除病果病穗，花前花后各喷1次，套袋保护"},
    "葡萄黑麻疹病": {"pesticide": "多菌灵、甲基硫菌灵", "method": "休眠期清园，萌芽前喷石硫合剂，生长期喷药保护"},
    "葡萄叶枯病": {"pesticide": "嘧菌酯、吡唑醚菌酯", "method": "加强排水，合理修剪通风，发病初喷药"},
    "葡萄健康": {"pesticide": "无需用药", "method": "合理修剪，保持通风，定期监测"},
    "柑橘黄龙病": {"pesticide": "目前无特效药", "method": "挖除病树，防治木虱（传毒媒介），使用无病苗木，这是毁灭性病害"},
    "桃细菌性斑点病": {"pesticide": "农用链霉素、噻菌铜", "method": "清除病枝病叶，休眠期喷波尔多液清园"},
    "桃健康": {"pesticide": "无需用药", "method": "合理修剪，保持通风，注意排水"},
    "甜椒细菌性斑点病": {"pesticide": "氢氧化铜、噻菌铜", "method": "种子消毒，避免喷灌，发病初期喷铜制剂"},
    "甜椒健康": {"pesticide": "无需用药", "method": "合理轮作，保持通风，控制湿度"},
    "马铃薯早疫病": {"pesticide": "代森锰锌、嘧菌酯", "method": "选用抗病品种，增施有机肥，发病初期喷药"},
    "马铃薯晚疫病": {"pesticide": "霜脲·锰锌、氟吡菌胺", "method": "发现中心病株立即拔除，雨后及时喷药保护，这是马铃薯头号病害"},
    "马铃薯健康": {"pesticide": "无需用药", "method": "选用脱毒种薯，合理轮作，控制田间湿度"},
    "覆盆子健康": {"pesticide": "无需用药", "method": "合理修剪，保持通风透光"},
    "大豆健康": {"pesticide": "无需用药", "method": "合理轮作，增施有机肥，定期巡查"},
    "南瓜白粉病": {"pesticide": "硫磺制剂、三唑酮", "method": "加强通风，发病初期喷药，严重时拔除病株"},
    "草莓叶枯病": {"pesticide": "多菌灵、代森锰锌", "method": "清除病叶，合理密植，地膜覆盖减少湿度"},
    "草莓健康": {"pesticide": "无需用药", "method": "合理密植，保持通风，定期巡查"},
    "番茄细菌性斑点病": {"pesticide": "氢氧化铜、噻菌铜", "method": "种子消毒，避免湿叶，发病初期喷铜制剂"},
    "番茄早疫病": {"pesticide": "代森锰锌、苯醚甲环唑", "method": "轮作倒茬，增施磷钾肥，发病前预防性喷药"},
    "番茄晚疫病": {"pesticide": "霜脲·锰锌、烯酰吗啉", "method": "低温高湿时重点防范，发现病株立即喷药，严重时全田防治"},
    "番茄叶霉病": {"pesticide": "嘧菌酯、多抗霉素", "method": "加强通风降湿，增施磷钾肥，发病初期喷药"},
    "番茄斑枯病": {"pesticide": "苯醚甲环唑、吡唑醚菌酯", "method": "清除病叶，合理密植，发病初期喷药保护"},
    "番茄红蜘蛛": {"pesticide": "阿维菌素、联苯肼酯", "method": "干旱季节注意浇水增湿，发生初期喷药，重点喷叶背"},
    "番茄靶斑病": {"pesticide": "嘧菌酯、戊唑醇", "method": "合理密植，降低田间湿度，发病初期喷药"},
    "番茄黄化曲叶病毒病": {"pesticide": "无特效药，以预防为主", "method": "防治烟粉虱（传毒媒介），使用抗病品种，清除田间杂草寄主"},
    "番茄花叶病毒病": {"pesticide": "无特效药，以预防为主", "method": "防治蚜虫，农事操作前洗手消毒，使用抗病品种"},
    "番茄健康": {"pesticide": "无需用药", "method": "合理轮作，增施有机肥，定期巡查"},
}

# 严重度估算参数
SEVERITY_THRESHOLDS = {
    "mild": (0, 0.05),      # 0-5% 轻度
    "moderate": (0.05, 0.20),  # 5-20% 中度
    "severe": (0.20, 1.0),    # 20%+ 重度
}

# 病害中文对照 (从训练配置同步)
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

# 默认数据集路径（用于获取类名）
DATA_DIR = os.path.join(PROJECT_DIR, "Plant_leave_diseases_dataset_without_augmentation")
# 如果默认路径不存在，尝试从主配置读取
if not os.path.exists(DATA_DIR):
    try:
        import sys
        _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if _root not in sys.path:
            sys.path.insert(0, _root)
        from config.config import Config as _Cfg
        DATA_DIR = _Cfg.DATA_DIR
    except Exception:
        pass  # 用默认值
