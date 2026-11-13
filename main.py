import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from api.auth import auth_router
from api.country import country_router
from api.city import city_router
from api.district import district_router
from api.shop import shop_router
from api.product import product_router
from api.weather import weather_router
from api.analyze import analyze_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = aioredis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        encoding="utf8",
        decode_responses=True,
    )
    try:
        FastAPICache.init(RedisBackend(redis_client), prefix="agroai-cache")
        yield
    finally:
        await redis_client.aclose()


app = FastAPI(
    title="AgroAIv2 API",
    description="Өсүмдүктөрдүн ооруларын аныктоо жана айыл чарба дүкөндөрүн башкаруу системасы",
    version="1.0.0",
    lifespan=lifespan,
)

# Explicit frontend allowlist; no wildcard origin when credentials are enabled.
origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
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
