from fastapi import APIRouter, Depends
from app.db import get_db
from app.services.fetcher import fetch_email_content
from app.services.emailer import send_email
from datetime import datetime, timedelta
import pytz

router = APIRouter()

@router.get("/cron-run")
async def cron_run(db=Depends(get_db)):
    now = datetime.now(pytz.utc).replace(second=0, microsecond=0)
    window_start = now - timedelta(minutes=1)
    window_end = now + timedelta(minutes=1)

    results = []

    schedules = await db.schedules.find({
        "status": "scheduled",
        "run_at": {"$gte": window_start, "$lte": window_end}
    }).to_list(length=100)

    for idx, s in enumerate(schedules):
        updated = await db.schedules.find_one_and_update(
            {"_id": s["_id"], "status": "scheduled"},
            {"$set": {"status": "processing"}}
        )

        if not updated:
            # Someone else already picked it up
            continue

        subject, body = await fetch_email_content(idx)

        try:
            send_email(
                to_email=s["email"],
                subject=subject,
                text_body=body,
            )
            await db.send_logs.insert_one({
                "schedule_id": s["_id"],
                "email": s["email"],
                "sent_at": now,
                "success": True,
                "detail": None,
            })
            await db.schedules.update_one(
                {"_id": s["_id"]},
                {"$set": {"status": "sent"}}
            )
            results.append({"id": s["_id"], "status": "sent"})
        except Exception as e:
            await db.send_logs.insert_one({
                "schedule_id": s["_id"],
                "email": s["email"],
                "sent_at": now,
                "success": False,
                "detail": str(e),
            })
            await db.schedules.update_one(
                {"_id": s["_id"]},
                {"$set": {"status": "failed"}}
            )
            results.append({"id": s["_id"], "status": "failed", "error": str(e)})

    return {"checked": len(schedules), "results": results}
