"""
SQLAlchemy ORM 模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    avatar_base64 = Column(Text, nullable=True)  # 用户头像 base64
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联
    diagnoses = relationship("DiagnosisRecord", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    corrections = relationship("CorrectedLabel", back_populates="user", cascade="all, delete-orphan")


class DiagnosisRecord(Base):
    __tablename__ = "diagnosis_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_base64 = Column(Text, nullable=True)  # 压缩后的缩略图
    top1_disease = Column(String(100), nullable=False)
    top1_confidence = Column(Float, nullable=False)
    top2_disease = Column(String(100), nullable=True)
    top2_confidence = Column(Float, nullable=True)
    top3_disease = Column(String(100), nullable=True)
    top3_confidence = Column(Float, nullable=True)
    is_healthy = Column(Boolean, default=False)
    severity = Column(String(20), nullable=True)  # healthy / mild / moderate / severe
    severity_percent = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="diagnoses")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(30), nullable=False)  # bug / suggestion / question / other
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    reply = Column(Text, nullable=True)  # 管理员回复
    replied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedbacks")


class CorrectedLabel(Base):
    """用户对诊断结果的纠错记录（用于后续模型改进）"""
    __tablename__ = "corrected_labels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    diagnosis_id = Column(Integer, ForeignKey("diagnosis_records.id"), nullable=True)
    original_prediction = Column(String(100), nullable=False)
    corrected_label = Column(String(100), nullable=False)
    image_base64 = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="corrections")
