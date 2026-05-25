from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from api.auth import auth_router
from api.country import country_router
from api.city import city_router
from api.district import district_router
from api.shop import shop_router
from api.product import product_router
from api.weather import weather_router
from api.analyze import analyze_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url("redis://localhost:6379", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="agroai-cache")
    print("Redis кэш системасы ийгиликтүү иштеди.")
    yield
    await redis.close()

app = FastAPI(
    title="AgroAIv2 API",
    description="Өсүмдүктөрдүн ооруларын аныктоо жана айыл чарба дүкөндөрүн башкаруу системасы",
    version="1.0.0",
    lifespan=lifespan
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(country_router)
app.include_router(city_router)
app.include_router(district_router)
app.include_router(shop_router)
app.include_router(product_router)
app.include_router(weather_router)
app.include_router(analyze_router)


@app.get("/", tags=["Root"])
async def root():
    return {"message": "AgroAIv2 API системасына кош келиңиз!"}
