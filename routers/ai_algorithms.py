from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Product
from services.graph_search import ProductGraph
from services.pca_analysis import run_pca
from services.image_classifier import classify_image

router = APIRouter()


async def _load_products(
    db: AsyncSession,
    ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    stmt = select(Product)
    if ids:
        stmt = stmt.where(Product.id.in_(ids))

    result = await db.execute(stmt)
    rows = result.scalars().all()

    return [
        {
            "id": p.id,
            "title": p.title,
            "brand": p.brand,
            "category_id": p.category_id,
            "ai_score": float(p.ai_score or 0.0),
            "effectiveness_score": float(p.effectiveness_score or 0.0),
            "value_score": float(p.value_score or 0.0),
            "longevity_score": float(p.longevity_score or 0.0),
            "review_count": int(p.review_count or 0),
            "image_url": p.image_url,
            "ai_summary": p.ai_summary,
        }
        for p in rows
    ]


@router.get("/ai/explore")
async def explore_products(
    product_id: str = Query(...),
    max_results: int = Query(10, ge=1, le=50),
    min_score: float = Query(0.0, ge=0.0, le=100.0),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    products = await _load_products(db)
    if not products:
        raise HTTPException(status_code=404, detail="No products in database.")

    graph = ProductGraph()
    graph.build_from_products(products)

    results = graph.best_first_search(
        start_id=product_id,
        max_results=max_results,
        min_score=min_score,
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"Product '{product_id}' not found or has no related products.",
        )

    return {
        "search_algorithm": "Best First Search",
        "seed_product_id": product_id,
        "results": results,
    }


class PCARequest(BaseModel):
    product_ids: list[str] | None = None


@router.post("/ai/pca")
async def pca_scatter(
    body: PCARequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    products = await _load_products(db, ids=body.product_ids)

    if len(products) < 2:
        raise HTTPException(
            status_code=400,
            detail="PCA requires at least 2 products.",
        )

    try:
        result = run_pca(products)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {"algorithm": "PCA (2 components)", "data": result}


@router.post("/ai/classify-image")
async def classify_product_image(
    file: UploadFile = File(...),
) -> dict[str, Any]:
    allowed = ("image/jpeg", "image/png", "image/webp")
    if file.content_type not in allowed:
        raise HTTPException(
            status_code=422,
            detail="Only JPEG, PNG, and WebP images are supported.",
        )

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=422, detail="Uploaded file is empty.")

    try:
        prediction = classify_image(raw)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference failed: {exc}")

    return {
        "model": "ResNet-18 CNN",
        "filename": file.filename,
        **prediction,
    }
