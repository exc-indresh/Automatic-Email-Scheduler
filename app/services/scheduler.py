from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from app.services.fetcher import fetch_email_content
from app.services.emailer import send_email
from app.db import get_db
import pytz

scheduler = AsyncIOScheduler(timezone=pytz.utc)


async def _job_send_email(schedule_id: str):
    db = await get_db()
    s = await db.schedules.find_one({"_id": schedule_id})
    if not s:
        return

    try:
        all_schedules = await db.schedules.find({}).to_list(length=None)
        user_index = next(
            (idx for idx, doc in enumerate(all_schedules) if doc["_id"] == schedule_id),
            0
        )
        subject, body = await fetch_email_content(user_index)

        send_email(
            to_email=s["email"],
            subject=subject,
            # html_body=f"<p>{body}</p>",
            text_body=body,
        )

        await db.send_logs.insert_one({
            "schedule_id": schedule_id,
            "email": s["email"],
            "sent_at": datetime.utcnow(),
            "success": True,
            "detail": None,
        })
        await db.schedules.update_one(
            {"_id": schedule_id},
            {"$set": {"status": "sent"}}
        )
    except Exception as e:
        await db.send_logs.insert_one({
            "schedule_id": schedule_id,
            "email": s["email"],
            "sent_at": datetime.utcnow(),
            "success": False,
            "detail": str(e),
        })
        await db.schedules.update_one(
            {"_id": schedule_id},
            {"$set": {"status": "failed"}}
        )


def schedule_job(schedule_id: str, run_at: datetime):
    trigger = DateTrigger(run_date=run_at)
    scheduler.add_job(
        _job_send_email,
        trigger=trigger,
        args=[schedule_id],
        id=schedule_id,
    )

def cancel_job(schedule_id: str):
    try:
        scheduler.remove_job(schedule_id)
    except Exception:
        pass
