from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import Product, ProductPrice, ReviewSource
from schemas import ProductListItem, ProductListResponse, ProductDetail, PriceOut, ReviewSourceOut
from services.cache import get_cached, set_cached

router = APIRouter()


@router.get("/products", response_model=ProductListResponse)
async def list_products(
    category: str = Query(None),
    sort: str = Query("ai_score"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Product).where(Product.status == "ready")
    if category:
        stmt = stmt.where(Product.category_id == category)

    sort_col = getattr(Product, sort, Product.ai_score)
    stmt = stmt.order_by(sort_col.desc())

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    products = result.scalars().all()

    items = []
    for p in products:
        price_stmt = select(ProductPrice).where(ProductPrice.product_id == p.id)
        price_result = await db.execute(price_stmt)
        prices = price_result.scalars().all()
        lowest = min((pr.price for pr in prices), default=None)
        items.append(
            ProductListItem(
                id=p.id,
                title=p.title,
                brand=p.brand,
                image_url=p.image_url,
                ai_score=p.ai_score,
                pros=p.pros if isinstance(p.pros, list) else [],
                lowest_price=lowest,
                store_count=len(prices),
            )
        )

    return ProductListResponse(products=items, total=total, page=page, page_size=page_size)


@router.get("/product/{product_id}", response_model=ProductDetail)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    cached = await get_cached(f"product:{product_id}")
    if cached:
        return ProductDetail(**cached)

    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    price_stmt = select(ProductPrice).where(ProductPrice.product_id == product_id)
    price_result = await db.execute(price_stmt)
    prices = price_result.scalars().all()

    source_stmt = select(ReviewSource).where(ReviewSource.product_id == product_id)
    source_result = await db.execute(source_stmt)
    sources = source_result.scalars().all()

    detail = ProductDetail(
        id=product.id,
        title=product.title,
        brand=product.brand,
        image_url=product.image_url,
        description=product.description,
        source_url=product.source_url,
        ai_score=product.ai_score,
        effectiveness_score=product.effectiveness_score,
        value_score=product.value_score,
        longevity_score=product.longevity_score,
        pros=product.pros if isinstance(product.pros, list) else [],
        cons=product.cons if isinstance(product.cons, list) else [],
        ai_summary=product.ai_summary,
        review_count=product.review_count,
        status=product.status,
        prices=[
            PriceOut(
                store_name=pr.store_name,
                store_logo=pr.store_logo,
                price=pr.price,
                currency=pr.currency,
                affiliate_url=pr.affiliate_url,
            )
            for pr in prices
        ],
        sources=[
            ReviewSourceOut(platform=s.platform, url=s.url, title=s.title)
            for s in sources
        ],
    )

    await set_cached(f"product:{product_id}", detail.model_dump(), ttl=300)
    return detail
