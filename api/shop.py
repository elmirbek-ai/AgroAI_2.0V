from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session
from typing import List
from db.database import SessionLocal
from db.models import Shop, User, City
from db.schema import ShopCreateSchema, ShopOutSchema

shop_router = APIRouter(prefix='/shop', tags=['Дүкөндөр'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@shop_router.post(
    '/',
    response_model=ShopOutSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Жаңы дүкөн кошуу",
    description="Жаңы дүкөндү базага каттоого мүмкүндүк берет. Дүкөн ээси (owner_id) жана шаардын IDси (city_id) талап кылынат."
)
async def create_shop(shop_data: ShopCreateSchema, db: Session = Depends(get_db)):
    owner_exists = db.query(User).filter(User.id == shop_data.owner_id).first()
    if not owner_exists:
        raise HTTPException(status_code=404, detail="Колдонуучу (owner) табылган жок")

    city_exists = db.query(City).filter(City.id == shop_data.city_id).first()
    if not city_exists:
        raise HTTPException(status_code=404, detail="Мындай шаар табылган жок")

    new_shop = Shop(
        name=shop_data.name,
        address=shop_data.address,
        phone=shop_data.phone,
        city_id=shop_data.city_id,
        owner_id=shop_data.owner_id
    )
    db.add(new_shop)
    db.commit()
    db.refresh(new_shop)
    return new_shop


@shop_router.get(
    '/',
    response_model=List[ShopOutSchema],
    summary="Бардык дүкөндөрдүн тизмеси",
    description="Базадагы бардык катталган дүкөндөрдүн жалпы тизмесин кайтарат."
)
async def list_shops(db: Session = Depends(get_db)):
    return db.query(Shop).all()


@shop_router.get(
    '/city/{city_id}',
    response_model=List[ShopOutSchema],
    summary="Шаар боюнча дүкөндөрдү чыпкалоо",
    description="Белгилүү бир шаардын IDси аркылуу ошол шаарда жайгашкан бардык дүкөндөрдү табуу."
)
async def get_shops_by_city(city_id: int, db: Session = Depends(get_db)):
    shops = db.query(Shop).filter(Shop.city_id == city_id).all()
    if not shops:
        raise HTTPException(status_code=404, detail="Бул шаарда азырынча дүкөндөр жок")
    return shops


@shop_router.get(
    '/{shop_id}',
    response_model=ShopOutSchema,
    summary="Бир дүкөн жөнүндө маалымат алуу",
    description="Дүкөндүн IDси аркылуу анын дарегин, байланыш телефондорун жана андагы товарларды көрүү."
)
async def get_shop(shop_id: int, db: Session = Depends(get_db)):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Дүкөн табылган жок")
    return shop


@shop_router.put(
    '/{shop_id}',
    response_model=ShopOutSchema,
    summary="Дүкөндүн маалыматын жаңыртуу",
    description="Дүкөндүн атын, дарегин же башка маалыматтарын өзгөртүү үчүн колдонулат."
)
async def update_shop(shop_id: int, shop_data: ShopCreateSchema, db: Session = Depends(get_db)):
    shop_db = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop_db:
        raise HTTPException(status_code=404, detail="Дүкөн табылган жок")

    city_exists = db.query(City).filter(City.id == shop_data.city_id).first()
    if not city_exists:
        raise HTTPException(status_code=404, detail="Мамлекет табылган жок")

    shop_db.name = shop_data.name
    shop_db.address = shop_data.address
    shop_db.phone = shop_data.phone
    shop_db.city_id = shop_data.city_id
    shop_db.owner_id = shop_data.owner_id

    db.commit()
    db.refresh(shop_db)
    return shop_db


@shop_router.delete(
    '/{shop_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Дүкөндү өчүрүү",
    description="Дүкөндү базадан биротоло өчүрүү үчүн колдонулат."
)
async def delete_shop(shop_id: int, db: Session = Depends(get_db)):
    shop_db = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop_db:
        raise HTTPException(status_code=404, detail="Дүкөн табылган жок")

    db.delete(shop_db)
    db.commit()
    return None
