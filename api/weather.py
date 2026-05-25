import httpx
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from config import WEATHER_API_KEY
from fastapi_cache.decorator import cache

weather_router = APIRouter(prefix='/weather', tags=['Аба ырайы (OpenWeatherMap)'])

BASE_URL = "https://api.openweathermap.org/data/2.5"


@weather_router.get('/current', summary="Учурдагы толук аба ырайы")
@cache(expire=600)
async def get_current_weather(
    lat: float = Query(..., description="Кеңдик", example=42.87),
    lon: float = Query(..., description="Узундук", example=74.59)
):
    url = f"{BASE_URL}/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ru"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="OWM API катасы")
            data = response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Сервер туташуусу үзүлдү: {str(e)}")

    return {
        "location": data.get("name"),
        "country": data.get("sys", {}).get("country"),
        "current": {
            "temp": f"{data['main']['temp']}°C",
            "feels_like": f"{data['main']['feels_like']}°C",
            "description": data['weather'][0]['description'].capitalize(),
            "humidity": f"{data['main']['humidity']}%",
            "pressure": f"{data['main']['pressure']} hPa",
            "clouds": f"{data['clouds']['all']}%",
            "wind": {
                "speed": f"{data['wind']['speed']} м/с",
                "deg": data['wind'].get('deg'),
                "gust": f"{data['wind'].get('gust', 0)} м/с"
            },
            "rain": data.get("rain", {"1h": 0}).get("1h", 0),
            "visibility": f"{data.get('visibility', 0) / 1000} км",
            "sun": {
                "sunrise": datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                "sunset": datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
            }
        }
    }


@weather_router.get('/forecast', summary="5 күндүк прогноз (ар 3 саат сайын)")
@cache(expire=3600)
async def get_weather_forecast(
    lat: float = Query(..., description="Кеңдик", example=42.87),
    lon: float = Query(..., description="Узундук", example=74.59)
):
    url = f"{BASE_URL}/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ru"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code != 200:
                 raise HTTPException(status_code=response.status_code, detail="Прогноз алууда ката")
            data = response.json()
        except Exception:
            raise HTTPException(status_code=500, detail="Прогноз алууда ката кетти")

    forecast_list = []
    for i in range(0, len(data['list']), 8):
        day_data = data['list'][i]
        forecast_list.append({
            "date": day_data['dt_txt'],
            "temp": f"{day_data['main']['temp']}°C",
            "description": day_data['weather'][0]['description'].capitalize(),
            "humidity": f"{day_data['main']['humidity']}%",
            "pop": f"{int(day_data.get('pop', 0) * 100)}%",
            "wind": f"{day_data['wind']['speed']} м/с"
        })

    return {
        "location": data['city']['name'],
        "forecast": forecast_list
    }
