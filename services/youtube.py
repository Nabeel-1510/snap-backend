import httpx
from youtube_transcript_api import YouTubeTranscriptApi
from config import settings


async def search_youtube_videos(product_name: str, max_results: int = 5) -> list[dict]:
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"{product_name} review",
        "type": "video",
        "maxResults": max_results,
        "key": settings.youtube_api_key,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            return []
        data = response.json()

    videos = []
    for item in data.get("items", []):
        video_id = item["id"].get("videoId")
        if not video_id:
            continue
        videos.append({
            "video_id": video_id,
            "title": item["snippet"]["title"],
            "url": f"https://www.youtube.com/watch?v={video_id}",
        })
    return videos


def fetch_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript_list])
    except Exception:
        return ""


async def fetch_youtube_reviews(product_name: str) -> list[dict]:
    videos = await search_youtube_videos(product_name)
    results = []
    for video in videos:
        transcript = fetch_transcript(video["video_id"])
        if len(transcript) < 100:
            continue
        results.append({
            "source": "youtube",
            "title": video["title"],
            "content": transcript[:3000],
            "url": video["url"],
        })
    return results
