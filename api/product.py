from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session
from typing import List
from db.database import SessionLocal
from db.models import Product, Shop
from db.schema import ProductCreateSchema, ProductOutSchema

product_router = APIRouter(prefix='/product', tags=['Товарлар'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@product_router.post(
    '/',
    response_model=ProductOutSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Жаңы товар кошуу",
    description="Жаңы товарды (дары, жер семирткич ж.б.) базага каттоого мүмкүндүк берет. Товар сөзсүз бир дүкөнгө (shop_id) байланууга тийиш."
)
async def create_product(product_data: ProductCreateSchema, db: Session = Depends(get_db)):
    shop_exists = db.query(Shop).filter(Shop.id == product_data.shop_id).first()
    if not shop_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Берилген shop_id боюнча дүкөн табылган жок"
        )

    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        image=product_data.image,
        delivery=product_data.delivery,
        disease_target=product_data.disease_target,
        shop_id=product_data.shop_id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@product_router.get(
    '/',
    response_model=List[ProductOutSchema],
    summary="Бардык товарлардын тизмеси",
    description="Базадагы бардык катталган товарлардын жалпы тизмесин кайтарат."
)
async def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@product_router.get(
    '/shop/{shop_id}',
    response_model=List[ProductOutSchema],
    summary="Дүкөндүн товарларын алуу",
    description="Белгилүү бир дүкөндүн IDси аркылуу андагы бардык товарларды тизмектеп чыгарат."
)
async def get_products_by_shop(shop_id: int, db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.shop_id == shop_id).all()
    return products


@product_router.get(
    '/search/{disease_name}',
    response_model=List[ProductOutSchema],
    summary="Оорунун аты боюнча издөө",
    description="Өсүмдүктөрдүн оорусунун аты боюнча (мисалы: 'грибок') ошол ооруга каршы дарыларды же товарларды издейт."
)
async def search_products_by_disease(disease_name: str, db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.disease_target.contains(disease_name)).all()
    return products


@product_router.get(
    '/{product_id}',
    response_model=ProductOutSchema,
    summary="Товарды ID аркылуу алуу",
    description="Бир даана товардын деталдуу маалыматын (баасы, сүрөтү, жеткирүү кызматы ж.б.) көрүү."
)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар табылган жок")
    return product


@product_router.put(
    '/{product_id}',
    response_model=ProductOutSchema,
    summary="Товардын маалыматын жаңыртуу",
    description="Товардын баасын, сүрөтүн же башка мүнөздөмөлөрүн өзгөртүү үчүн колдонулат."
)
async def update_product(product_id: int, product_data: ProductCreateSchema, db: Session = Depends(get_db)):
    product_db = db.query(Product).filter(Product.id == product_id).first()
    if not product_db:
        raise HTTPException(status_code=404, detail="Товар табылган жок")

    shop_exists = db.query(Shop).filter(Shop.id == product_data.shop_id).first()
    if not shop_exists:
        raise HTTPException(status_code=404, detail="Дүкөн табылган жок")

    product_db.name = product_data.name
    product_db.description = product_data.description
    product_db.price = product_data.price
    product_db.image = product_data.image
    product_db.delivery = product_data.delivery
    product_db.disease_target = product_data.disease_target
    product_db.shop_id = product_data.shop_id

    db.commit()
    db.refresh(product_db)
    return product_db


@product_router.delete(
    '/{product_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Товарды өчүрүү",
    description="Товарды маалымат базасынан биротоло өчүрүү."
)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product_db = db.query(Product).filter(Product.id == product_id).first()
    if not product_db:
        raise HTTPException(status_code=404, detail="Товар табылган жок")

    db.delete(product_db)
    db.commit()
    return None
