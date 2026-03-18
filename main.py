from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import init_db
from routers import search, products, chat, categories, ai_algorithms


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Snap Search API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(categories.router, prefix="/api/v1", tags=["categories"])
app.include_router(ai_algorithms.router, prefix="/api/v1", tags=["ai-algorithms"])


@app.get("/health")
async def health():
    return {"status": "ok"}
