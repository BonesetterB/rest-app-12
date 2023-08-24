from sqlalchemy import  Integer, String, Date,func,DateTime,ForeignKey,Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from .db import Base

class Contact(Base):
    __tablename__ = 'contacts'

    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:Mapped[str] = mapped_column(String(100), nullable=False)
    surname:Mapped[str] = mapped_column(String(100), nullable=False)
    email:Mapped[str] = mapped_column(String(150),unique=True, nullable=False)
    phone:Mapped[str] = mapped_column(String(20),unique=True,nullable=False)
    birthday:Mapped[Date] = mapped_column(Date,nullable=False)
    notes:Mapped[str] = mapped_column(String(500),nullable=True)
    created_at:Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at:Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    user : Mapped["User"] = relationship('User',backref='contacts')
    user_id:Mapped[int]=mapped_column(Integer,ForeignKey('users.id'),nullable=True)

    
class User(Base):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    username:Mapped[str] = mapped_column(String(50))
    email :Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password:Mapped[str] = mapped_column(String(255), nullable=False)
    created_at:Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at:Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    avatar:Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token:Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed:Mapped[bool] = mapped_column(Boolean, default=False)
    



