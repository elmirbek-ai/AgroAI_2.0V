from sqlalchemy import Integer, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.database import Base
from typing import List
from enum import Enum as PyEnum
from datetime import datetime
from passlib.hash import bcrypt


class TypeUse(str, PyEnum):
    freemium = 'freemium'
    premium = 'premium'


class Country(Base):
    __tablename__ = 'country'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country_name: Mapped[str] = mapped_column(String(64), unique=True)

    users: Mapped[List["User"]] = relationship("User", back_populates="country")
    cities: Mapped[List["City"]] = relationship("City", back_populates="country", cascade="all, delete-orphan")
    districts: Mapped[List["District"]] = relationship("District", back_populates="country",
                                                       cascade="all, delete-orphan")


class City(Base):
    __tablename__ = 'city'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city_name: Mapped[str] = mapped_column(String(64), unique=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    country_id: Mapped[int] = mapped_column(ForeignKey("country.id"))
    country: Mapped["Country"] = relationship("Country", back_populates="cities")

    shops: Mapped[List["Shop"]] = relationship("Shop", back_populates="city_rel")


class District(Base):
    __tablename__ = 'district'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    district_name: Mapped[str] = mapped_column(String(32), unique=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    country_id: Mapped[int] = mapped_column(ForeignKey("country.id"))
    country: Mapped["Country"] = relationship("Country", back_populates="districts")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String, unique=True)
    full_name: Mapped[str] = mapped_column(String)

    country_id: Mapped[int] = mapped_column(ForeignKey("country.id"))
    country: Mapped["Country"] = relationship("Country", back_populates="users")

    password: Mapped[str] = mapped_column(String(100), nullable=False)

    shops: Mapped[List["Shop"]] = relationship("Shop", back_populates="owner")
    user_token: Mapped[List['RefreshToken']] = relationship('RefreshToken', back_populates='token_user',
                                                            cascade='all, delete-orphan')
    analyses: Mapped[List["AnalysisResult"]] = relationship("AnalysisResult", back_populates="user")

    def set_password(self, password: str):
        self.password = bcrypt.hash(password)


class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    token_user: Mapped["User"] = relationship("User", back_populates='user_token')
    token: Mapped[str] = mapped_column(String, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Shop(Base):
    __tablename__ = "shops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    address: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)

    city_id: Mapped[int] = mapped_column(ForeignKey("city.id"))
    city_rel: Mapped["City"] = relationship("City", back_populates="shops")

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship("User", back_populates="shops")
    products: Mapped[List["Product"]] = relationship("Product", back_populates="shop")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)
    image: Mapped[str] = mapped_column(String)
    delivery: Mapped[bool] = mapped_column(Boolean)
    disease_target: Mapped[str] = mapped_column(String)

    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id"))
    shop: Mapped["Shop"] = relationship("Shop", back_populates="products")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="analyses")
    disease_name: Mapped[str] = mapped_column(String)
    confidence: Mapped[float] = mapped_column(Float)
    image_url: Mapped[str] = mapped_column(String)
    ai_recommendation: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())