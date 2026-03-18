import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from workers.celery_app import celery_app
from config import settings
from services.scraper import scrape_product_page
from services.reddit import fetch_reddit_reviews
from services.youtube import fetch_youtube_reviews
from services.ai_engine import synthesize_reviews
from services.scoring import compute_ai_score

_sync_engine = None


def _get_engine():
    global _sync_engine
    if _sync_engine is None:
        _sync_engine = create_engine(settings.sync_database_url)
    return _sync_engine


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3)
def analyze_product_url(self, url: str):
    from models import Product, ReviewChunk, ReviewSource, ProductPrice
    from database import Base

    product_data = _run_async(scrape_product_page(url))

    reddit_reviews = fetch_reddit_reviews(product_data.get("title", ""))
    youtube_reviews = _run_async(fetch_youtube_reviews(product_data.get("title", "")))
    all_reviews = reddit_reviews + youtube_reviews

    review_texts = [r["content"] for r in all_reviews]
    if review_texts:
        ai_result = _run_async(synthesize_reviews(product_data["title"], review_texts))
    else:
        ai_result = {
            "pros": [],
            "cons": [],
            "summary": "No reviews found yet.",
            "effectiveness_score": 0,
            "value_score": 0,
            "longevity_score": 0,
        }

    ai_score = compute_ai_score(
        ai_result.get("effectiveness_score", 0),
        ai_result.get("value_score", 0),
        ai_result.get("longevity_score", 0),
    )

    with Session(_get_engine()) as session:
        product = Product(
            title=product_data["title"],
            brand=product_data.get("brand", ""),
            image_url=product_data.get("image_url", ""),
            description=product_data.get("description", ""),
            source_url=url,
            ai_score=ai_score,
            effectiveness_score=ai_result.get("effectiveness_score", 0),
            value_score=ai_result.get("value_score", 0),
            longevity_score=ai_result.get("longevity_score", 0),
            pros=ai_result.get("pros", []),
            cons=ai_result.get("cons", []),
            ai_summary=ai_result.get("summary", ""),
            review_count=len(all_reviews),
            status="ready",
        )
        session.add(product)
        session.flush()

        if product_data.get("price"):
            price_entry = ProductPrice(
                product_id=product.id,
                store_name="Source Store",
                price=product_data["price"],
                affiliate_url=url,
            )
            session.add(price_entry)

        for review in all_reviews:
            chunk = ReviewChunk(
                product_id=product.id,
                source=review["source"],
                content=review["content"],
            )
            session.add(chunk)

            source = ReviewSource(
                product_id=product.id,
                platform=review["source"],
                url=review.get("url", ""),
                title=review.get("title", ""),
            )
            session.add(source)

        session.commit()
        return {"product_id": product.id, "status": "ready"}


@celery_app.task
def refresh_prices(product_id: str):
    from models import Product, ProductPrice

    with Session(_get_engine()) as session:
        product = session.get(Product, product_id)
        if not product or not product.source_url:
            return {"status": "skipped"}

        product_data = _run_async(scrape_product_page(product.source_url))
        if product_data.get("price"):
            existing = (
                session.query(ProductPrice)
                .filter_by(product_id=product_id, store_name="Source Store")
                .first()
            )
            if existing:
                existing.price = product_data["price"]
            else:
                session.add(
                    ProductPrice(
                        product_id=product_id,
                        store_name="Source Store",
                        price=product_data["price"],
                        affiliate_url=product.source_url,
                    )
                )
            session.commit()
        return {"status": "updated"}
