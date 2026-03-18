from typing import Optional
from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    type: str = "text"


class SearchResult(BaseModel):
    id: str
    title: str
    brand: Optional[str] = None
    image_url: Optional[str] = None
    ai_score: float = 0.0
    category: Optional[str] = None


class SearchResponse(BaseModel):
    results: list[SearchResult]
    task_id: Optional[str] = None


class PriceOut(BaseModel):
    store_name: str
    store_logo: Optional[str] = None
    price: float
    currency: str = "INR"
    affiliate_url: Optional[str] = None


class ReviewSourceOut(BaseModel):
    platform: str
    url: str
    title: Optional[str] = None


class ProductListItem(BaseModel):
    id: str
    title: str
    brand: Optional[str] = None
    image_url: Optional[str] = None
    ai_score: float
    pros: list[str] = []
    lowest_price: Optional[float] = None
    store_count: int = 0


class ProductDetail(BaseModel):
    id: str
    title: str
    brand: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    ai_score: float
    effectiveness_score: float
    value_score: float
    longevity_score: float
    pros: list[str] = []
    cons: list[str] = []
    ai_summary: Optional[str] = None
    review_count: int = 0
    status: str
    prices: list[PriceOut] = []
    sources: list[ReviewSourceOut] = []


class ProductListResponse(BaseModel):
    products: list[ProductListItem]
    total: int
    page: int
    page_size: int


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


class ChatResponse(BaseModel):
    reply: str


class CategoryOut(BaseModel):
    id: str
    name: str
    slug: str
    icon: Optional[str] = None
    product_count: int = 0
