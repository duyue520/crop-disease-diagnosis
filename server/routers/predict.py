"""
诊断推理路由: 单张预测 / 批量预测 / Grad-CAM
"""
import base64
import io
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from PIL import Image

from ..database import get_db
from ..models.db_models import User, DiagnosisRecord
from ..schemas.schemas import PredictResponse
from ..services.auth_service import get_optional_user
from ..services.predict_service import predict

router = APIRouter(prefix="/api", tags=["诊断"])

MAX_THUMBNAIL_SIZE = (256, 256)


def compress_image_to_base64(image_bytes: bytes, size=MAX_THUMBNAIL_SIZE) -> str:
    """压缩图片为缩略图 base64 用于历史记录"""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img.thumbnail(size)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=60)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ""


@router.post("/predict", response_model=PredictResponse)
async def predict_single(
    image: UploadFile = File(...),
    enable_gradcam: bool = Query(False, description="是否生成 Grad-CAM 热力图"),
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    单张叶片病害诊断

    - **image**: 叶片照片 (jpg/png/webp)
    - **enable_gradcam**: 设为 true 会额外返回热力图（耗时可忽略）
    """
    # 校验文件类型
    ext = image.filename.rsplit(".", 1)[-1].lower() if image.filename else "jpg"
    if ext not in {"jpg", "jpeg", "png", "webp", "bmp"}:
        raise HTTPException(400, "不支持的图片格式，请上传 jpg/png/webp")

    image_bytes = await image.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(400, "图片大小不能超过 10MB")

    # 推理
    result = predict(image_bytes, top_k=3, enable_gradcam=enable_gradcam)

    # 保存诊断记录（已登录用户）
    diagnosis_id = None
    if user:
        thumb = compress_image_to_base64(image_bytes)
        try:
            record = DiagnosisRecord(
                user_id=user.id,
                image_base64=thumb,
                top1_disease=result["predictions"][0]["disease_cn"],
                top1_confidence=result["predictions"][0]["confidence"],
                top2_disease=result["predictions"][1]["disease_cn"] if len(result["predictions"]) > 1 else None,
                top2_confidence=result["predictions"][1]["confidence"] if len(result["predictions"]) > 1 else None,
                top3_disease=result["predictions"][2]["disease_cn"] if len(result["predictions"]) > 2 else None,
                top3_confidence=result["predictions"][2]["confidence"] if len(result["predictions"]) > 2 else None,
                is_healthy=result["is_healthy"],
                severity=result["severity"],
                severity_percent=result["severity_percent"],
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            diagnosis_id = record.id
        except Exception:
            db.rollback()

    return PredictResponse(
        success=True,
        predictions=result["predictions"],
        is_healthy=result["is_healthy"],
        severity=result["severity"],
        severity_percent=result["severity_percent"],
        advices=result["advices"],
        grad_cam_base64=result.get("grad_cam_base64"),
        inference_time_ms=result["inference_time_ms"],
        diagnosis_id=diagnosis_id,
    )


@router.post("/predict/batch")
async def predict_batch(
    images: list[UploadFile] = File(...),
    enable_gradcam: bool = Query(False),
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    批量叶片病害诊断 (最多 50 张)
    """
    if len(images) > 50:
        raise HTTPException(400, "单次最多 50 张图片")

    results = []
    for img in images:
        img_bytes = await img.read()
        try:
            r = predict(img_bytes, top_k=3, enable_gradcam=enable_gradcam)
            results.append({
                "filename": img.filename,
                "success": True,
                "top1": r["predictions"][0],
                "is_healthy": r["is_healthy"],
                "severity": r["severity"],
            })
        except Exception as e:
            results.append({
                "filename": img.filename,
                "success": False,
                "error": str(e),
            })

    return {"success": True, "total": len(images), "results": results}


@router.get("/health")
def health_check():
    """API 健康检查"""
    from ..services.predict_service import _model
    return {
        "status": "ok",
        "model_loaded": _model is not None,
    }
