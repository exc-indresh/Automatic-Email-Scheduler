from fastapi import FastAPI
from app.api import schedules as schedules_router
from app.db import init_db
from app.services.scheduler import scheduler
from app.utils.excel_reader import import_from_excel


app = FastAPI(title="Email Scheduler")

app.include_router(schedules_router.router, prefix="/schedules", tags=["schedules"])

@app.on_event("startup")
async def startup_event():
    await init_db()
    await import_from_excel("example_schedules.xlsx")
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()