import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "")
if len(SECRET_KEY) < 32 or SECRET_KEY == "replace-with-a-long-random-secret":
    raise RuntimeError("Set SECRET_KEY to a unique random secret of at least 32 characters.")

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_LIFETIME = 30
REFRESH_ACCESS_TOKEN_LIFETIME = 3
