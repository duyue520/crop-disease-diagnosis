"""
用户认证路由: 注册 / 登录 / 个人中心
"""
import base64
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..database import get_db
from ..models.db_models import User, DiagnosisRecord
from ..schemas.schemas import UserRegister, UserLogin, Token, UserInfo
from ..services.auth_service import hash_password, verify_password, create_access_token, get_current_user


class UpdateProfileRequest(BaseModel):
    username: str = Field(default="", max_length=50)
    avatar_base64: str = Field(default="")


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=50)

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=Token)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查重名
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.username)
    return Token(access_token=token, username=user.username)


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名不存在，请先注册")
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="密码错误，请重试")

    token = create_access_token(user.id, user.username)
    return Token(access_token=token, username=user.username)


@router.get("/me", response_model=UserInfo)
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    diag_count = db.query(User).filter(User.id == user.id).first()
    return UserInfo(
        id=user.id,
        username=user.username,
        email=user.email,
        diagnosis_count=len(user.diagnoses),
        created_at=user.created_at,
    )


@router.get("/history")
def get_diagnosis_history(
    skip: int = 0,
    limit: int = 20,
    user: User = Depends(get_current_user),
):
    """获取用户诊断历史"""
    records = sorted(user.diagnoses, key=lambda r: r.created_at, reverse=True)[skip: skip + limit]
    return {
        "total": len(user.diagnoses),
        "records": [
            {
                "id": r.id,
                "top1_disease": r.top1_disease,
                "top1_confidence": r.top1_confidence,
                "is_healthy": r.is_healthy,
                "severity": r.severity,
                "severity_percent": r.severity_percent,
                "created_at": r.created_at.isoformat(),
                "image_base64": r.image_base64,
            }
            for r in records
        ],
    }


@router.delete("/history/{record_id}")
def delete_history_record(
    record_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除单条诊断记录"""
    record = db.query(DiagnosisRecord).filter(
        DiagnosisRecord.id == record_id,
        DiagnosisRecord.user_id == user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(record)
    db.commit()
    return {"success": True, "message": "已删除"}


@router.delete("/history")
def delete_all_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除全部诊断历史"""
    count = db.query(DiagnosisRecord).filter(
        DiagnosisRecord.user_id == user.id,
    ).delete()
    db.commit()
    return {"success": True, "message": f"已删除 {count} 条记录"}


@router.get("/profile")
def get_profile(user: User = Depends(get_current_user)):
    """获取完整个人资料"""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar_base64": user.avatar_base64,
        "diagnosis_count": len(user.diagnoses),
        "created_at": user.created_at.isoformat(),
    }


@router.put("/profile")
def update_profile(
    data: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新用户名和头像"""
    if data.username and data.username != user.username:
        existing = db.query(User).filter(User.username == data.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已被占用")
        user.username = data.username
    if data.avatar_base64:
        # 限制头像大小 ~200KB
        if len(data.avatar_base64) > 300000:
            raise HTTPException(status_code=400, detail="头像图片太大，请压缩后上传")
        user.avatar_base64 = data.avatar_base64
    db.commit()
    return {"success": True, "message": "资料已更新", "username": user.username}


@router.put("/password")
def change_password(
    data: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改密码"""
    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="原密码不正确")
    user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"success": True, "message": "密码已修改，请重新登录"}


class ForgotPasswordRequest(BaseModel):
    username: str = Field(..., max_length=50)
    email: str = Field(..., max_length=100)


class ResetPasswordRequest(BaseModel):
    username: str = Field(..., max_length=50)
    email: str = Field(..., max_length=100)
    new_password: str = Field(..., min_length=6, max_length=50)


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """验证身份，返回验证通过（无需邮件，本地验证）"""
    user = db.query(User).filter(
        User.username == data.username,
        User.email == data.email,
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户名和邮箱不匹配，请检查后重试")
    return {"success": True, "message": "身份验证通过", "username": data.username, "email": data.email}


@router.put("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """重置密码（需先通过 forgot-password 验证）"""
    user = db.query(User).filter(
        User.username == data.username,
        User.email == data.email,
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户名和邮箱不匹配")
    user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"success": True, "message": "密码已重置，请使用新密码登录"}


@router.post("/avatar")
async def upload_avatar(
    image: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传头像图片（自动压缩）"""
    contents = await image.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片不能超过 5MB")

    # 压缩到合适大小
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    img.thumbnail((256, 256))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70)
    b64 = base64.b64encode(buf.getvalue()).decode()

    user.avatar_base64 = b64
    db.commit()
    return {"success": True, "avatar_base64": b64}
