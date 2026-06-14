"""博客 """
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Session, relationship
from pydantic import BaseModel, Field
from ..database import Base, get_db, engine
from ..services.auth_service import get_current_user
from ..models.db_models import User

router = APIRouter(prefix="/api/blog", tags=["博客"])

class BlogCategory(Base):
    __tablename__ = "blog_categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

class BlogArticle(Base):
    __tablename__ = "blog_articles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(500), default="")
    cover_url = Column(String(500), default="")
    category_id = Column(Integer, ForeignKey("blog_categories.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
    category = relationship("BlogCategory")

class BlogComment(Base):
    __tablename__ = "blog_comments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("blog_articles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")

Base.metadata.create_all(bind=engine)

class ArticleCreate(BaseModel):
    title: str = Field(..., max_length=200)
    content: str = Field(..., min_length=1)
    category_name: str = Field(default="", max_length=50)
    cover_url: str = Field(default="", max_length=500)

class ArticleUpdate(BaseModel):
    title: str = Field(default="", max_length=200)
    content: str = Field(default="")
    category_name: str = Field(default="", max_length=50)
    cover_url: str = Field(default="", max_length=500)

@router.get("/articles")
def list_articles(skip: int=0, limit:int=20, category:str="", db:Session=Depends(get_db)):
    q = db.query(BlogArticle)
    if category:
        cat = db.query(BlogCategory).filter(BlogCategory.name==category).first()
        if cat: q = q.filter(BlogArticle.category_id==cat.id)
    total = q.count()
    articles = q.order_by(BlogArticle.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "articles": [{
        "id":a.id,"title":a.title,"summary":a.summary or a.content[:200],
        "content":a.content[:300],"cover_url":a.cover_url or "",
        "category":a.category.name if a.category else "",
        "author":a.user.username if a.user else "","views":a.views,
        "created_at":a.created_at.strftime("%Y-%m-%d %H:%M")} for a in articles]}

@router.get("/articles/{aid}")
def get_article(aid:int, db:Session=Depends(get_db)):
    a=db.query(BlogArticle).filter(BlogArticle.id==aid).first()
    if not a: raise HTTPException(404,"不存在")
    a.views+=1; db.commit()
    comments=db.query(BlogComment).filter(BlogComment.article_id==aid).order_by(BlogComment.created_at).all()
    return {"id":a.id,"title":a.title,"content":a.content,"cover_url":a.cover_url or "",
        "category":a.category.name if a.category else "",
        "author":a.user.username if a.user else "","views":a.views,"created_at":a.created_at.strftime("%Y-%m-%d %H:%M"),
        "comments":[{"id":c.id,"content":c.content,"author":c.user.username if c.user else "","created_at":c.created_at.strftime("%m-%d %H:%M")} for c in comments]}

@router.post("/articles")
def create_article(data:ArticleCreate, user:User=Depends(get_current_user), db:Session=Depends(get_db)):
    cat=None
    if data.category_name:
        cat=db.query(BlogCategory).filter(BlogCategory.name==data.category_name).first()
        if not cat: cat=BlogCategory(name=data.category_name); db.add(cat); db.flush()
    a=BlogArticle(title=data.title,content=data.content,summary=data.content[:200],cover_url=data.cover_url,category_id=cat.id if cat else None,user_id=user.id)
    db.add(a); db.commit(); db.refresh(a)
    return {"success":True,"article_id":a.id}

@router.put("/articles/{aid}")
def update_article(aid:int, data:ArticleUpdate, user:User=Depends(get_current_user), db:Session=Depends(get_db)):
    a=db.query(BlogArticle).filter(BlogArticle.id==aid).first()
    if not a: raise HTTPException(404,"不存在")
    if a.user_id!=user.id and user.username!="杜越": raise HTTPException(403,"只能改自己的")
    if data.title: a.title=data.title
    if data.content: a.content=data.content; a.summary=data.content[:200]
    if data.cover_url: a.cover_url=data.cover_url
    if data.category_name:
        cat=db.query(BlogCategory).filter(BlogCategory.name==data.category_name).first()
        if not cat: cat=BlogCategory(name=data.category_name); db.add(cat); db.flush()
        a.category_id=cat.id
    db.commit()
    return {"success":True,"message":"已更新"}

@router.delete("/articles/{aid}")
def delete_article(aid:int, user:User=Depends(get_current_user), db:Session=Depends(get_db)):
    a=db.query(BlogArticle).filter(BlogArticle.id==aid).first()
    if not a: raise HTTPException(404,"文章不存在")
    if a.user_id!=user.id and user.username!="杜越": raise HTTPException(403,"只能删自己的")
    db.query(BlogComment).filter(BlogComment.article_id==aid).delete()
    db.delete(a); db.commit()
    return {"success":True}

@router.get("/categories")
def list_categories(db:Session=Depends(get_db)):
    return [{"id":c.id,"name":c.name,"count":db.query(BlogArticle).filter(BlogArticle.category_id==c.id).count()} for c in db.query(BlogCategory).all()]

class CommentCreate(BaseModel):
    content: str = Field(..., max_length=1000)
    nickname: str = Field(default="匿名", max_length=50)

@router.delete("/comments/{cid}")
def delete_comment(cid:int, user:User=Depends(get_current_user), db:Session=Depends(get_db)):
    c = db.query(BlogComment).filter(BlogComment.id==cid).first()
    if not c: raise HTTPException(404,"评论不存在")
    if c.user_id!=user.id and user.username!="杜越": raise HTTPException(403,"只能删自己的")
    db.delete(c); db.commit()
    return {"success":True,"message":"已删除"}

@router.post("/articles/{aid}/comments")
def add_comment(aid:int, data:CommentCreate, db:Session=Depends(get_db)):
    if not db.query(BlogArticle).filter(BlogArticle.id==aid).first(): raise HTTPException(404,"不存在")
    c=BlogComment(article_id=aid,user_id=0,content=data.content)
    db.add(c); db.commit(); db.refresh(c)
    return {"success":True,"comment":{"id":c.id,"content":c.content,"author":"匿名","created_at":c.created_at.strftime("%m-%d %H:%M")}}
