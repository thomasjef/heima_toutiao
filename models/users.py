from typing import Optional
from sqlalchemy import Index, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    __table_args__ = (
        Index("username_UNIQUE", "username"),
        Index("phone_UNIQUE", "phone"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True, comment="用户id")
    username: Mapped[str] = mapped_column(String(50), nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码")
    nickname: Mapped[Optional[str]] = mapped_column(String(50),  comment="昵称")
    avatar: Mapped[Optional[str]] = mapped_column(String(255),  default="https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif", comment="头像url")
    gender: Mapped[Optional[str]] = mapped_column(Enum("male", "female", "unknown"), default="unknown", comment="性别")
    bio: Mapped[Optional[str]] = mapped_column(String(500),  default="这个人很懒，什么都没留下", comment="个人简介")
    phone: Mapped[Optional[str]] = mapped_column(String(20),  comment="手机号")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, password={self.password}, nickname={self.nickname}, avator={self.avator}, gender={self.gender}, bio={self.bio}, phone={self.phone})>"


class UserToken(Base):
    __tablename__ = "user_token"

    __table_args__ = (
        Index("fk_user_token_user_idx", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True, comment="令牌id")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, comment="用户id")
    token: Mapped[str] = mapped_column(String(255), nullable=False, comment="令牌值")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="令牌过期时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")

    def __repr__(self):
        return f"<UserToken(id={self.id}, user_id={self.user_id}, token={self.token}, expired_at={self.expired_at})>"