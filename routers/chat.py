from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Product, ReviewChunk
from schemas import ChatRequest, ChatResponse
from services.ai_engine import generate_chat_response

router = APIRouter()


@router.post("/product/{product_id}/chat", response_model=ChatResponse)
async def product_chat(product_id: str, req: ChatRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    chunk_stmt = select(ReviewChunk).where(ReviewChunk.product_id == product_id).limit(50)
    chunk_result = await db.execute(chunk_stmt)
    chunks = chunk_result.scalars().all()

    context_text = "\n".join([c.content for c in chunks])
    reply = await generate_chat_response(
        product_title=product.title,
        product_summary=product.ai_summary or "",
        context=context_text,
        message=req.message,
        history=req.history,
    )
    return ChatResponse(reply=reply)
