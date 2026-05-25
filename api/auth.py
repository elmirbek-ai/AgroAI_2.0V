from fastapi import Depends, HTTPException, APIRouter, status, Body
from db.database import SessionLocal
from db.models import User, RefreshToken
from db.schema import UserCreateSchema, UserLoginSchema
from sqlalchemy.orm import Session
from typing import Optional
from passlib.context import CryptContext
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from config import ALGORITHM, SECRET_KEY, ACCESS_TOKEN_LIFETIME, REFRESH_ACCESS_TOKEN_LIFETIME
from datetime import timedelta, datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")

auth_router = APIRouter(prefix='/auth', tags=['Auth'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expires = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_LIFETIME))
    to_encode.update({"exp": expires})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_ACCESS_TOKEN_LIFETIME))


@auth_router.post('/register', response_model=dict)
async def register(user: UserCreateSchema, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.username == user.username).first()
    user_email = db.query(User).filter(User.email == user.email).first()

    if user_db:
        raise HTTPException(status_code=400, detail='Бул username мурун катталган')
    elif user_email:
        raise HTTPException(status_code=400, detail='Бул email мурун катталган')

    hash_password = get_password_hash(user.password)

    new_user = User(
        full_name=user.full_name,
        username=user.username,
        email=user.email,
        country_id=user.country_id,
        password=hash_password,
        phone_number=user.phone_number
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": 'Ийгиликтүү катталды'}


@auth_router.post('/login')
async def login(form_data: UserLoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Логин же сырсөз туура эмес")

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})

    new_token = RefreshToken(user_id=user.id, token=refresh_token)
    db.add(new_token)
    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@auth_router.post('/logout')
async def logout(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()

    if not stored_token:
        raise HTTPException(status_code=401, detail="Токен туура эмес же табылган жок")

    db.delete(stored_token)
    db.commit()

    return {"message": "Ийгиликтүү чыктыңыз (Logout)"}


@auth_router.post('/refresh')
async def refresh(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()

    if not stored_token:
        raise HTTPException(status_code=401, detail="Токен туура эмес же мөөнөтү бүткөн")
    access_token = create_access_token({"sub": stored_token.token_user.username})

    return {"access_token": access_token, "token_type": "bearer"}