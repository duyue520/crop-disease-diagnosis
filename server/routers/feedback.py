"""
留言反馈 + 诊断纠错路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.db_models import User, Feedback, CorrectedLabel
from ..schemas.schemas import FeedbackCreate, FeedbackResponse, CorrectionCreate
from ..services.auth_service import get_current_user

router = APIRouter(prefix="/api", tags=["反馈"])


# ==================== 留言反馈 ====================
@router.post("/feedback")
def create_feedback(
    data: FeedbackCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """提交留言反馈"""
    if data.category not in {"bug", "suggestion", "question", "other"}:
        raise HTTPException(400, "分类必须为 bug / suggestion / question / other")

    fb = Feedback(
        user_id=user.id,
        category=data.category,
        title=data.title,
        content=data.content,
    )
    db.add(fb)
    db.commit()
    return {"success": True, "message": "谢谢你的反馈，我会继续努力！", "feedback_id": fb.id}


@router.get("/feedback/my")
def get_my_feedbacks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取我的留言反馈列表（含管理员回复）"""
    feedbacks = (
        db.query(Feedback)
        .filter(Feedback.user_id == user.id)
        .order_by(Feedback.created_at.desc())
        .all()
    )
    return {
        "total": len(feedbacks),
        "items": [
            FeedbackResponse(
                id=f.id,
                category=f.category,
                title=f.title,
                content=f.content,
                reply=f.reply,
                replied_at=f.replied_at,
                created_at=f.created_at,
                username=user.username,
            )
            for f in feedbacks
        ],
    }


# ==================== 诊断纠错 ====================
@router.post("/correct")
def correct_prediction(
    data: CorrectionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """纠正模型的诊断结果（用于后续模型迭代）"""
    correction = CorrectedLabel(
        user_id=user.id,
        diagnosis_id=data.diagnosis_id,
        original_prediction=data.original_prediction,
        corrected_label=data.corrected_label,
    )
    db.add(correction)
    db.commit()
    return {"success": True, "message": "纠错记录已保存，感谢您的贡献！"}
