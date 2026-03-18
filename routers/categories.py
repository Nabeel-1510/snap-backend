from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import Category, Product
from schemas import CategoryOut

router = APIRouter()


@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    stmt = select(Category).order_by(Category.name)
    result = await db.execute(stmt)
    categories = result.scalars().all()

    output = []
    for cat in categories:
        count_stmt = select(func.count()).where(Product.category_id == cat.id)
        count_result = await db.execute(count_stmt)
        count = count_result.scalar() or 0
        output.append(
            CategoryOut(
                id=cat.id,
                name=cat.name,
                slug=cat.slug,
                icon=cat.icon,
                product_count=count,
            )
        )
    return output
