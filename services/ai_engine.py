import json
from openai import AsyncOpenAI
from config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)


async def synthesize_reviews(product_title: str, review_chunks: list[str]) -> dict:
    combined = "\n---\n".join(review_chunks[:30])

    messages = [
        {
            "role": "system",
            "content": (
                "You are a product analyst. Given user reviews, extract structured insights. "
                "Return valid JSON with keys: pros (list of 3 strings), cons (list of 3 strings), "
                "summary (string, 2-3 sentences), effectiveness_score (0-100), "
                "value_score (0-100), longevity_score (0-100)."
            ),
        },
        {
            "role": "user",
            "content": f"Product: {product_title}\n\nReviews:\n{combined}",
        },
    ]

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {
            "pros": [],
            "cons": [],
            "summary": "",
            "effectiveness_score": 0,
            "value_score": 0,
            "longevity_score": 0,
        }
    return data


async def generate_chat_response(
    product_title: str,
    product_summary: str,
    context: str,
    message: str,
    history: list[dict],
) -> str:
    system_msg = (
        f"You are a helpful shopping assistant specialized in '{product_title}'. "
        f"Product summary: {product_summary}\n\n"
        f"User reviews and context:\n{context[:4000]}\n\n"
        "Answer the user's question based on the above context. Be concise and helpful."
    )

    messages = [{"role": "system", "content": system_msg}]
    for h in history[-10:]:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": message})

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0.5,
        max_tokens=500,
    )
    return response.choices[0].message.content
