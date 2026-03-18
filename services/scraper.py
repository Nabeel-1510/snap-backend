import httpx
from bs4 import BeautifulSoup


async def scrape_product_page(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    title = ""
    og_title = soup.find("meta", property="og:title")
    if og_title:
        title = og_title.get("content", "")
    if not title:
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

    image = ""
    og_image = soup.find("meta", property="og:image")
    if og_image:
        image = og_image.get("content", "")

    description = ""
    og_desc = soup.find("meta", property="og:description")
    if og_desc:
        description = og_desc.get("content", "")
    if not description:
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            description = meta_desc.get("content", "")

    price = None
    price_selectors = [
        {"class_": "a-price-whole"},
        {"class_": "price"},
        {"itemprop": "price"},
    ]
    for sel in price_selectors:
        el = soup.find(attrs=sel)
        if el:
            raw = el.get_text(strip=True).replace(",", "").replace("₹", "").replace("$", "")
            try:
                price = float(raw)
            except ValueError:
                pass
            break

    brand = ""
    brand_el = soup.find(attrs={"class": "brand"}) or soup.find("a", id="bylineInfo")
    if brand_el:
        brand = brand_el.get_text(strip=True)

    return {
        "title": title,
        "image_url": image,
        "description": description,
        "price": price,
        "brand": brand,
        "source_url": url,
    }
