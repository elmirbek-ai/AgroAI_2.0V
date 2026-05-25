from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session
from typing import List
from db.database import SessionLocal
from db.models import Country
from db.schema import CountryCreateSchema, CountryOutSchema

country_router = APIRouter(prefix='/country', tags=['Мамлекеттер'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@country_router.post(
    '/',
    response_model=CountryOutSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Жаңы мамлекет кошуу",
    description="Маалымат базасына жаңы мамлекеттин атын кошуу үчүн колдонулат."
)
async def create_country(country_data: CountryCreateSchema, db: Session = Depends(get_db)):
    existing_country = db.query(Country).filter(Country.country_name == country_data.country_name).first()
    if existing_country:
        raise HTTPException(status_code=400, detail="Бул мамлекет мурунтан эле бар")

    new_country = Country(country_name=country_data.country_name)
    db.add(new_country)
    db.commit()
    db.refresh(new_country)
    return new_country


@country_router.get(
    '/',
    response_model=List[CountryOutSchema],
    summary="Бардык мамлекеттердин тизмеси",
    description="Базада катталган бардык мамлекеттерди тизме катары кайтарат."
)
async def list_countries(db: Session = Depends(get_db)):
    return db.query(Country).all()


@country_router.get(
    '/{country_id}',
    response_model=CountryOutSchema,
    summary="Мамлекетти ID аркылуу алуу",
    description="Белгилүү бир мамлекеттин маалыматын анын уникалдуу ID номери аркылуу таап берет."
)
async def get_country(country_id: int, db: Session = Depends(get_db)):
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Мамлекет табылган жок")
    return country


@country_router.put(
    '/{country_id}',
    response_model=CountryOutSchema,
    summary="Мамлекеттин маалыматын жаңыртуу",
    description="Тандалган мамлекеттин атын же башка маалыматтарын өзгөртүү үчүн колдонулат."
)
async def update_country(country_id: int, country_data: CountryCreateSchema, db: Session = Depends(get_db)):
    country_db = db.query(Country).filter(Country.id == country_id).first()
    if not country_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Мамлекет табылган жок")

    country_db.country_name = country_data.country_name
    db.commit()
    db.refresh(country_db)
    return country_db


@country_router.delete(
    '/{country_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Мамлекетти өчүрүү",
    description="ID аркылуу мамлекетти маалымат базасынан биротоло өчүрөт."
)
async def delete_country(country_id: int, db: Session = Depends(get_db)):
    country_db = db.query(Country).filter(Country.id == country_id).first()
    if not country_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Мамлекет табылган жок")

    db.delete(country_db)
    db.commit()
    return None
