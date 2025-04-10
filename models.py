from sqlalchemy import create_engine, Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    notes = relationship("Note", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(name='{self.name}')>"

class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category = relationship("Category", back_populates="notes")

    def __repr__(self):
        return f"<Note(title='{self.title}', category='{self.category.name if self.category else None}')>"

# 创建数据库引擎
engine = create_engine('sqlite:///notes.db', echo=False)
# 创建所有表
Base.metadata.create_all(engine)
# 创建会话工厂
Session = sessionmaker(bind=engine) 