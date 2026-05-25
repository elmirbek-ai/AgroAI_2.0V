from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session
from typing import List
from db.database import SessionLocal
from db.models import City, Country
from db.schema import CityCreateSchema, CityOutSchema

city_router = APIRouter(prefix='/city', tags=['Шаарлар'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@city_router.post(
    '/',
    response_model=CityOutSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Жаңы шаар кошуу",
    description="Жаңы шаарды базага каттоого мүмкүндүк берет. Каттоо үчүн мамлекеттин ID номери (country_id) талап кылынат."
)
async def create_city(city_data: CityCreateSchema, db: Session = Depends(get_db)):
    country_exists = db.query(Country).filter(Country.id == city_data.country_id).first()
    if not country_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Берилген country_id боюнча мамлекет табылган жок"
        )

    existing_city = db.query(City).filter(City.city_name == city_data.city_name).first()
    if existing_city:
        raise HTTPException(status_code=400, detail="Бул шаар мурунтан эле кошулган")

    new_city = City(
        city_name=city_data.city_name,
        latitude=city_data.latitude,
        longitude=city_data.longitude,
        country_id=city_data.country_id
    )
    db.add(new_city)
    db.commit()
    db.refresh(new_city)
    return new_city


@city_router.get(
    '/',
    response_model=List[CityOutSchema],
    summary="Бардык шаарлардын тизмеси",
    description="Маалымат базасындагы бардык катталган шаарларды тизме катары кайтарат."
)
async def list_cities(db: Session = Depends(get_db)):
    return db.query(City).all()


@city_router.get(
    '/by-country/{country_id}',
    response_model=List[CityOutSchema],
    summary="Мамлекетке карап шаарларды алуу",
    description="Тандалган мамлекеттин IDсине тиешелүү болгон бардык шаарларды чыгарып берет."
)
async def list_cities_by_country(country_id: int, db: Session = Depends(get_db)):
    return db.query(City).filter(City.country_id == country_id).all()


@city_router.get(
    '/{city_id}',
    response_model=CityOutSchema,
    summary="Шаарды ID аркылуу алуу",
    description="Белгилүү бир шаардын маалыматын анын ID номери аркылуу таап берет."
)
async def get_city(city_id: int, db: Session = Depends(get_db)):
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Шаар табылган жок")
    return city


@city_router.put(
    '/{city_id}',
    response_model=CityOutSchema,
    summary="Шаардын маалыматын жаңыртуу",
    description="Тандалган шаардын атын же кайсы мамлекетке таандык экенин өзгөртүү үчүн колдонулат."
)
async def update_city(city_id: int, city_data: CityCreateSchema, db: Session = Depends(get_db)):
    city_db = db.query(City).filter(City.id == city_id).first()
    if not city_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Шаар табылган жок")

    country_exists = db.query(Country).filter(Country.id == city_data.country_id).first()
    if not country_exists:
        raise HTTPException(status_code=404, detail="Мамлекет табылган жок")

    city_db.city_name = city_data.city_name
    city_db.country_id = city_data.country_id

    db.commit()
    db.refresh(city_db)
    return city_db


@city_router.delete(
    '/{city_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Шаарды өчүрүү",
    description="ID аркылуу шаарды маалымат базасынан биротоло өчүрөт."
)
async def delete_city(city_id: int, db: Session = Depends(get_db)):
    city_db = db.query(City).filter(City.id == city_id).first()
    if not city_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Шаар табылган жок")

    db.delete(city_db)
    db.commit()
    return None
