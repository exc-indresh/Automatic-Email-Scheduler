from fastapi import Depends
import pandas as pd
from dateutil import parser
from datetime import datetime
from app.db import get_db
from app.services.scheduler import schedule_job
import pytz
import uuid

IST = pytz.timezone("Asia/Kolkata")

async def import_from_excel(path: str):
    db = await get_db() 
    df = pd.read_excel(path)
    for _, row in df.iterrows():
        email = row["email"]
        raw_time = row["send_time"]

        if pd.isna(raw_time):
            continue

        if isinstance(raw_time, str):
            dt = parser.parse(raw_time)
        elif isinstance(raw_time, datetime):
            dt = raw_time
        else:
            dt = parser.parse(str(raw_time))

        if dt.tzinfo is None:
            localized = IST.localize(dt)
        else:
            localized = dt.astimezone(IST)


        run_at_utc = localized.astimezone(pytz.utc)

        schedule_id = str(uuid.uuid4())
        doc = {
            "_id": schedule_id,
            "email": email,
            "run_at": run_at_utc,
            "tz": "Asia/Kolkata",   
            "status": "scheduled",
        }
        await db.schedules.insert_one(doc)

        schedule_job(schedule_id, run_at_utc)
