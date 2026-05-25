from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session
from typing import List
from db.database import SessionLocal
from db.models import District, Country
from db.schema import DistrictCreateSchema, DistrictOutSchema

district_router = APIRouter(prefix='/district', tags=['Райондор'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@district_router.post(
    '/',
    response_model=DistrictOutSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Жаңы район кошуу",
    description="Географиялык координаталары (кеңдик жана узундук) менен жаңы районду базага каттоого мүмкүндүк берет."
)
async def create_district(district_data: DistrictCreateSchema, db: Session = Depends(get_db)):
    country_exists = db.query(Country).filter(Country.id == district_data.country_id).first()
    if not country_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Берилген country_id боюнча мамлекет табылган жок"
        )

    existing_district = db.query(District).filter(District.district_name == district_data.district_name).first()
    if existing_district:
        raise HTTPException(status_code=400, detail="Бул район мурунтан эле кошулган")

    new_district = District(
        district_name=district_data.district_name,
        latitude=district_data.latitude,
        longitude=district_data.longitude,
        country_id=district_data.country_id
    )
    db.add(new_district)
    db.commit()
    db.refresh(new_district)
    return new_district


@district_router.get(
    '/',
    response_model=List[DistrictOutSchema],
    summary="Бардык райондордун тизмеси",
    description="Базада катталган бардык райондордун жалпы тизмесин кайтарат."
)
async def list_districts(db: Session = Depends(get_db)):
    return db.query(District).all()


@district_router.get(
    '/by-country/{country_id}',
    response_model=List[DistrictOutSchema],
    summary="Мамлекетке карап райондорду алуу",
    description="Тандалган мамлекеттин IDсине тиешелүү болгон бардык райондорду гана бөлүп чыгарат."
)
async def list_districts_by_country(country_id: int, db: Session = Depends(get_db)):
    districts = db.query(District).filter(District.country_id == country_id).all()
    return districts


@district_router.get(
    '/{district_id}',
    response_model=DistrictOutSchema,
    summary="Районду ID аркылуу алуу",
    description="Белгилүү бир райондун деталдуу маалыматын анын ID номери аркылуу таап берет."
)
async def get_district(district_id: int, db: Session = Depends(get_db)):
    district = db.query(District).filter(District.id == district_id).first()
    if not district:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Район табылган жок")
    return district


@district_router.put(
    '/{district_id}',
    response_model=DistrictOutSchema,
    summary="Райондун маалыматын жаңыртуу",
    description="Райондун атын, координаталарын же мамлекеттик байланышын өзгөртүү үчүн колдонулат."
)
async def update_district(district_id: int, district_data: DistrictCreateSchema, db: Session = Depends(get_db)):
    district_db = db.query(District).filter(District.id == district_id).first()
    if not district_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Район табылган жок")

    country_exists = db.query(Country).filter(Country.id == district_data.country_id).first()
    if not country_exists:
        raise HTTPException(status_code=404, detail="Мамлекет табылган жок")

    district_db.district_name = district_data.district_name
    district_db.latitude = district_data.latitude
    district_db.longitude = district_data.longitude
    district_db.country_id = district_data.country_id

    db.commit()
    db.refresh(district_db)
    return district_db


@district_router.delete(
    '/{district_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Районду өчүрүү",
    description="Районду маалымат базасынан биротоло өчүрүү үчүн колдонулат."
)
async def delete_district(district_id: int, db: Session = Depends(get_db)):
    district_db = db.query(District).filter(District.id == district_id).first()
    if not district_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Район табылган жок")

    db.delete(district_db)
    db.commit()
    return None
