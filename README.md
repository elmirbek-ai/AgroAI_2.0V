# AgroAI 2.0

AgroAI is a FastAPI backend for plant-disease image classification, agricultural weather data, users, shops, and products.

> This repository is an educational prototype. Model predictions are not a substitute for diagnosis by an agronomist.

## Capabilities

- identifies diseases for tomato, potato, apple, corn, pepper, grape, and strawberry images;
- returns confidence and a basic recommendation;
- provides current weather and a five-day forecast through OpenWeather;
- supports registration, JWT access/refresh tokens, and logout;
- manages countries, cities, districts, agricultural shops, and products;
- caches weather responses with Redis;
- manages PostgreSQL migrations with Alembic.

## Tech stack

- Python and FastAPI
- TensorFlow/Keras, NumPy, Pillow
- SQLAlchemy and PostgreSQL
- Alembic
- Redis and fastapi-cache2
- HTTPX
- JWT authentication

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Copy the environment template:

```bash
cp .env.example .env
```

4. Configure PostgreSQL and start Redis locally.
5. Apply migrations:

```bash
alembic upgrade head
```

6. Start the API:

```bash
uvicorn main:app --reload
```

Swagger is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Configuration

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | JWT signing secret |
| `WEATHER_API_KEY` | OpenWeather API key |
| `DATABASE_URL` | PostgreSQL connection URL |
| `REDIS_URL` | Redis connection URL |

Never commit real values. The previously tracked `.env` must be treated as exposed: rotate any active keys and remove the file from Git history before a production release.

## Plant analysis

Send `multipart/form-data` to `POST /analyze/`:

- `plant_type`: one of `tomato`, `potato`, `apple`, `corn`, `pepper`, `grape`, `strawberry`;
- `file`: a plant image.

The current models expect RGB images resized to 224×224.

## Known limitations

- training notebooks, dataset provenance, metrics, and model cards are not yet included;
- recommendations cover only part of the predicted classes;
- model files are stored directly in Git instead of a model registry or Git LFS;
- automated API and ML tests are not yet implemented;
- Redis and PostgreSQL must already be running;
- authentication and error handling require production hardening.

## Before production

- rotate every secret that has ever been committed;
- remove `.env`, IDE files, caches, and bytecode from Git history;
- validate configuration at startup;
- restrict CORS to the real frontend domains;
- add file-size and MIME validation for uploads;
- add rate limits and authenticated analysis history;
- document datasets, model metrics, and limitations;
- add tests before enabling automated deployment.
