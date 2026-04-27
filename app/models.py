from datetime import datetime
from typing import List

from sqlalchemy import String, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Brand(Base):
    __tablename__ = "brands"

    brand_id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    url: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    settings: Mapped[List["Settings"]] = relationship(back_populates="brand")
    products: Mapped[list["Product"]] = relationship(back_populates="brand")


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    fullname: Mapped[str] = mapped_column(String(50), unique=False, nullable=False)
    setting: Mapped["Settings"] = relationship(back_populates="user")


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"), nullable=False, unique=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.brand_id"), nullable=False, unique=False)
    min_price: Mapped[int] = mapped_column(unique=False, nullable=False)
    max_price: Mapped[int] = mapped_column(unique=False, nullable=False)
    brand: Mapped["Brand"] = relationship(back_populates="settings")
    user: Mapped["User"] = relationship(back_populates="setting")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.brand_id"), nullable=False)
    article: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    brand: Mapped["Brand"] = relationship(back_populates="products")