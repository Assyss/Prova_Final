from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

app = FastAPI()

# Configuração da conexão com MySQL
engine = create_engine('mysql+mysqlconnector://root:root@localhost:3390/curso')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

Base = declarative_base()

# Modelo Post
class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    text = Column(String)
    comments = relationship('Comment', cascade="all, delete-orphan")

# Modelo Comment
class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('post.id', ondelete='CASCADE'))
    text = Column(String)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    user = Column(String)
    attached_files = relationship('AttachedFiles', cascade="all, delete-orphan")

# Modelo AttachedFiles
class AttachedFiles(Base):
    __tablename__ = 'attachedfiles'

    id = Column(Integer, primary_key=True)
    comment_id = Column(Integer, ForeignKey('comment.id', ondelete='CASCADE'))
    title = Column(String)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    file_path = Column(String)

# Criar tabelas no banco
Base.metadata.create_all(bind=engine)

# Rotas para Post
@app.get("/api/posts")
def get_posts():
    posts = session.query(Post).all()
    result = [
        {
            "id": post.id,
            "title": post.title,
            "created": str(post.created),
            "text": post.text,
            "comments": [
                {
                    "id": comment.id,
                    "text": comment.text,
                    "created": str(comment.created),
                    "user": comment.user,
                    "attached_files": [
                        {
                            "id": file.id,
                            "title": file.title,
                            "created": str(file.created),
                            "file_path": file.file_path
                        }
                        for file in comment.attached_files
                    ]
                }
                for comment in post.comments
            ],
        }
        for post in posts
    ]
    return JSONResponse(content=result)

@app.post("/api/posts")
def create_post(title: str, text: str):
    post = Post(title=title, text=text)
    session.add(post)
    session.commit()
    return JSONResponse(content={"id": post.id, "title": post.title, "created": str(post.created), "text": post.text})

@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
    post = session.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    result = {
        "id": post.id,
        "title": post.title,
        "created": str(post.created),
        "text": post.text,
        "comments": [
            {
                "id": comment.id,
                "text": comment.text,
                "created": str(comment.created),
                "user": comment.user,
                "attached_files": [
                    {
                        "id": file.id,
                        "title": file.title,
                        "created": str(file.created),
                        "file_path": file.file_path
                    }
                    for file in comment.attached_files
                ]
            }
            for comment in post.comments
        ],
    }
    return JSONResponse(content=result)

@app.put("/api/posts/{post_id}")
def update_post(post_id: int, title: str, text: str):
    post = session.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.title = title
    post.text = text
    session.commit()
    return JSONResponse(content={"id": post.id, "title": post.title, "text": post.text})

@app.delete("/api/posts/{post_id}")
def delete_post(post_id: int):
    post = session.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    session.delete(post)
    session.commit()
    return JSONResponse(content={"message": "Post deleted successfully"})

# Rotas para Comment
@app.get("/api/comments")
def get_comments():
    comments = session.query(Comment).all()
    result = [
        {
            "id": comment.id,
            "post_id": comment.post_id,
            "text": comment.text,
            "created": str(comment.created),
            "user": comment.user,
            "attached_files": [
                {
                    "id": file.id,
                    "title": file.title,
                    "created": str(file.created),
                    "file_path": file.file_path
                }
                for file in comment.attached_files
            ],
        }
        for comment in comments
    ]
    return JSONResponse(content=result)

# Continue implementando as outras rotas conforme o padrão.
