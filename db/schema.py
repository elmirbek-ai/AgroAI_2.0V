from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class TypeUse(str, Enum):
    freemium = 'freemium'
    premium = 'premium'


class CountryCreateSchema(BaseModel):
    country_name: str


class CountryOutSchema(BaseModel):
    id: int
    country_name: str

    class Config:
        from_attributes = True


class CityCreateSchema(BaseModel):
    city_name: str
    latitude: float
    longitude: float
    country_id: int


class CityOutSchema(BaseModel):
    id: int
    city_name: str
    latitude: float
    longitude: float
    country_id: int

    class Config:
        from_attributes = True


class DistrictCreateSchema(BaseModel):
    district_name: str
    latitude: float
    longitude: float
    country_id: int


class DistrictOutSchema(BaseModel):
    id: int
    district_name: str
    latitude: float
    longitude: float
    country_id: int

    class Config:
        from_attributes = True


class ProductCreateSchema(BaseModel):
    name: str
    description: str
    price: float
    image: str
    delivery: bool
    disease_target: str
    shop_id: int


class ProductOutSchema(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image: str
    delivery: bool
    disease_target: str
    shop_id: int

    class Config:
        from_attributes = True


class ShopCreateSchema(BaseModel):
    name: str
    address: str
    phone: str
    city_id: int
    owner_id: int


class ShopOutSchema(BaseModel):
    id: int
    name: str
    address: str
    phone: str
    city_id: int
    owner_id: int
    products: List[ProductOutSchema] = []

    class Config:
        from_attributes = True


class UserCreateSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    phone_number: str = Field(..., description="Мисалы: +996700123456")
    full_name: str
    country_id: int
    password: str = Field(..., min_length=6)


class UserOutSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone_number: str
    full_name: str
    country_id: int
    shops: List[ShopOutSchema] = []

    class Config:
        from_attributes = True


class UserLoginSchema(BaseModel):
    username: str
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenSchema(BaseModel):
    id: int
    token: str
    user_id: int
    created_date: datetime

    class Config:
        from_attributes = True


class AnalysisResultCreateSchema(BaseModel):
    disease_name: str
    confidence: float
    image_url: str
    ai_recommendation: str
    user_id: int


class AnalysisResultOutSchema(BaseModel):
    id: int
    disease_name: str
    confidence: float
    image_url: str
    ai_recommendation: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
