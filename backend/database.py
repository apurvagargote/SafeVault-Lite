from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
import sqlite3
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./safevault.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    secrets = relationship("Secret", back_populates="owner")

class Secret(Base):
    __tablename__ = "secrets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    value = Column(String, nullable=False)
    description = Column(String, default="")
    category = Column(String, default="general")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="secrets")

class SecurityLog(Base):
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)  # 'login_failed', 'login_success', 'password_changed', 'secret_accessed'
    username = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    user_agent = Column(String, default="")
    details = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created with category support")