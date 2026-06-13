"""
Pydantic 数据模型 (请求/响应验证)
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== 用户认证 ====================
class UserRegister(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6, max_length=50)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


class UserInfo(BaseModel):
    id: int
    username: str
    email: str
    diagnosis_count: int = 0
    created_at: datetime


# ==================== 诊断 ====================
class Prediction(BaseModel):
    rank: int
    disease_cn: str
    disease_en: str
    confidence: float


class PredictResponse(BaseModel):
    success: bool
    predictions: List[Prediction]
    is_healthy: bool
    severity: Optional[str] = None
    severity_percent: Optional[float] = None
    advices: Optional[dict] = None
    grad_cam_base64: Optional[str] = None
    inference_time_ms: float
    diagnosis_id: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "predictions": [
                    {"rank": 1, "disease_cn": "番茄早疫病", "disease_en": "Tomato___Early_blight", "confidence": 0.965}
                ],
                "is_healthy": False,
                "severity": "moderate",
                "severity_percent": 12.5,
                "advices": {
                    "pesticide": "代森锰锌、苯醚甲环唑",
                    "method": "轮作倒茬，增施磷钾肥，发病前预防性喷药"
                },
                "inference_time_ms": 85.3,
                "diagnosis_id": 42
            }
        }


class BatchPredictResponse(BaseModel):
    success: bool
    total: int
    results: List[dict]


class ExportRequest(BaseModel):
    diagnosis_ids: Optional[List[int]] = None
    format: str = "excel"  # excel / pdf


# ==================== 诊断记录 ====================
class DiagnosisRecordOut(BaseModel):
    id: int
    top1_disease: str
    top1_confidence: float
    is_healthy: bool
    severity: Optional[str]
    severity_percent: Optional[float]
    created_at: datetime
    image_base64: Optional[str] = None


# ==================== 反馈 ====================
class FeedbackCreate(BaseModel):
    category: str = Field(..., max_length=30)
    title: str = Field(..., max_length=200)
    content: str = Field(..., max_length=2000)


class FeedbackAdminReply(BaseModel):
    reply: str = Field(..., max_length=2000)


class FeedbackResponse(BaseModel):
    id: int
    category: str
    title: str
    content: str
    reply: Optional[str]
    replied_at: Optional[datetime]
    created_at: datetime
    username: str


# ==================== 纠错 ====================
class CorrectionCreate(BaseModel):
    diagnosis_id: Optional[int] = None
    original_prediction: str
    corrected_label: str


# ==================== 批量导出 ====================
class UserDiagnosisHistory(BaseModel):
    total: int
    records: List[DiagnosisRecordOut]
