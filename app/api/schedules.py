from datetime import datetime
from dateutil import parser
from fastapi import APIRouter, HTTPException, Depends
from pydantic import EmailStr
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_db
from app.services import scheduler as sched_service
from pydantic import BaseModel
import pytz
import uuid

router = APIRouter()


class CreateScheduleIn(BaseModel):
    email: EmailStr
    run_at: str  
    tz: str   


@router.post("/", status_code=201)
async def create_schedule(payload: CreateScheduleIn, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        local_dt = parser.isoparse(payload.run_at)
    except Exception:
        local_dt = parser.parse(payload.run_at)

    tzinfo = pytz.timezone(payload.tz)
    if local_dt.tzinfo is None:
        local_dt = tzinfo.localize(local_dt)

    utc_dt = local_dt.astimezone(pytz.utc)

    schedule_id = str(uuid.uuid4())
    doc = {
        "_id": schedule_id,
        "email": payload.email,
        "run_at": utc_dt,
        "tz": payload.tz,
        "status": "scheduled",
    }

    await db.schedules.insert_one(doc)
    sched_service.schedule_job(schedule_id, utc_dt)
    return {"id": schedule_id}


@router.get("/")
async def list_schedules(db: AsyncIOMotorDatabase = Depends(get_db)):
    items = []
    async for doc in db.schedules.find({}):
        items.append({
            "id": doc["_id"],
            "email": doc["email"],
            "run_at": doc["run_at"],
            "tz": doc.get("tz"),
            "status": doc.get("status"),
        })
    return items


@router.get("/{schedule_id}")
async def get_schedule(schedule_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await db.schedules.find_one({"_id": schedule_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return doc


@router.post("/{schedule_id}/cancel")
async def cancel_schedule(schedule_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await db.schedules.find_one({"_id": schedule_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")

    await db.schedules.update_one(
        {"_id": schedule_id},
        {"$set": {"status": "cancelled"}}
    )
    sched_service.cancel_job(schedule_id)
    return {"id": schedule_id, "status": "cancelled"}
