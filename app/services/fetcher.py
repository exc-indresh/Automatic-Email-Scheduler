import httpx
from app.core.config import settings


async def fetch_email_content(user_index: int = 0):
   
    url = settings.API_CONTENT_URL
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=10.0)
        r.raise_for_status()
        data = r.json()

    if isinstance(data, list) and data:
        post = data[user_index % len(data)] 
        subject = post.get("title", "Scheduled Email")
        body = post.get("body", str(post))
    else:
        subject = "Scheduled Email"
        body = str(data)

    return subject, body
