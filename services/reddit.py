import praw
from config import settings


def fetch_reddit_reviews(product_name: str, limit: int = 20) -> list[dict]:
    reddit = praw.Reddit(
        client_id=settings.reddit_client_id,
        client_secret=settings.reddit_client_secret,
        user_agent=settings.reddit_user_agent,
    )

    results = []
    query = f"{product_name} review"
    for submission in reddit.subreddit("all").search(query, sort="relevance", limit=limit):
        body = submission.selftext or ""
        if len(body) < 50:
            continue
        results.append({
            "source": "reddit",
            "title": submission.title,
            "content": body[:2000],
            "url": f"https://reddit.com{submission.permalink}",
            "score": submission.score,
        })

        submission.comments.replace_more(limit=0)
        for comment in submission.comments[:5]:
            if len(comment.body) > 50:
                results.append({
                    "source": "reddit",
                    "title": f"Comment on: {submission.title}",
                    "content": comment.body[:1000],
                    "url": f"https://reddit.com{comment.permalink}",
                    "score": comment.score,
                })

    return results
