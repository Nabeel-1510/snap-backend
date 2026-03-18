import re
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Product
from schemas import SearchRequest, SearchResponse, SearchResult
from workers.tasks import analyze_product_url

router = APIRouter()

URL_PATTERN = re.compile(r"https?://[^\s]+")


@router.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest, db: AsyncSession = Depends(get_db)):
    if req.type == "url" or URL_PATTERN.match(req.query):
        stmt = select(Product).where(Product.source_url == req.query)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return SearchResponse(
                results=[
                    SearchResult(
                        id=existing.id,
                        title=existing.title,
                        brand=existing.brand,
                        image_url=existing.image_url,
                        ai_score=existing.ai_score,
                    )
                ]
            )
        task = analyze_product_url.delay(req.query)
        return SearchResponse(results=[], task_id=task.id)

    search_term = f"%{req.query}%"
    stmt = (
        select(Product)
        .where(Product.title.ilike(search_term) | Product.brand.ilike(search_term))
        .order_by(Product.ai_score.desc())
        .limit(20)
    )
    result = await db.execute(stmt)
    products = result.scalars().all()
    return SearchResponse(
        results=[
            SearchResult(
                id=p.id,
                title=p.title,
                brand=p.brand,
                image_url=p.image_url,
                ai_score=p.ai_score,
            )
            for p in products
        ]
    )


@router.get("/search/{task_id}")
async def get_search_status(task_id: str):
    from workers.celery_app import celery_app
    task = celery_app.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"status": "pending"}
    elif task.state == "SUCCESS":
        return {"status": "completed", "result": task.result}
    else:
        return {"status": "failed", "error": str(task.info)}
