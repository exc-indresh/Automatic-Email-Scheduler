from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class ScheduleCreate(BaseModel):
    email: EmailStr
    run_at: datetime
    tz: str

class Schedule(ScheduleCreate):
    id: str
    status: str = Field(default="scheduled")

class SendLog(BaseModel):
    schedule_id: str
    email: EmailStr
    sent_at: datetime
    success: bool
    detail: Optional[str]