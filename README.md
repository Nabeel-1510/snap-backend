# Snap Search API

FastAPI backend for the Snap Search AI shopping assistant.

## Local Development

```bash
docker-compose up -d
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Deploy to Render

1. Push repo to GitHub
2. Render Dashboard → New → Blueprint → connect repo
3. Render detects `render.yaml` and provisions web service + PostgreSQL + Redis
4. Add your secret keys via Render Dashboard → Environment, or upload `config.env` as a secret file
5. Update `CORS_ORIGINS` with your frontend URL

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/search/` | Search products |
| GET | `/api/v1/products/{id}` | Product details |
| POST | `/api/v1/chat/` | AI chat |
| GET | `/api/v1/categories/` | List categories |
| GET | `/api/v1/ai/explore` | Best First Search |
| POST | `/api/v1/ai/pca` | PCA scatter coordinates |
| POST | `/api/v1/ai/classify-image` | CNN image classification |

## Project Structure

```
backend/
├── main.py
├── config.py
├── database.py
├── models.py
├── schemas.py
├── config.env
├── render.yaml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── routers/
│   ├── search.py
│   ├── products.py
│   ├── chat.py
│   ├── categories.py
│   └── ai_algorithms.py
├── services/
│   ├── ai_engine.py
│   ├── graph_search.py
│   ├── pca_analysis.py
│   ├── image_classifier.py
│   ├── scoring.py
│   ├── scraper.py
│   ├── reddit.py
│   ├── youtube.py
│   └── cache.py
└── workers/
    ├── celery_app.py
    └── tasks.py
```
