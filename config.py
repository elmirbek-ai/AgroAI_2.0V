import os
from dotenv import load_dotenv


load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_LIFETIME = 30
REFRESH_ACCESS_TOKEN_LIFETIME = 3