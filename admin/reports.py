from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from models import CheckpointLog
from database import SessionLocal
from auth.dependencies import require_admin
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

# ✅ Tag defined here only — DO NOT add again in main.py
router = APIRouter(tags=["Admin Reports"])

# ✅ Shared DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Response model for Swagger docs
class TurnaroundReport(BaseModel):
    truck_id: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    turnaround_time_minutes: Optional[float]

    class Config:
        orm_mode = True

# ✅ Documented GET endpoint with proper query param examples
@router.get(
    "/turnaround",
    summary="Generate truck turnaround time report",
    description="Returns each truck's start time, end time, and turnaround time in minutes between the given start and end datetime range.",
    response_model=List[TurnaroundReport],
    dependencies=[Depends(require_admin)]
)
def get_turnaround_report(
    start: datetime = Query(..., example="2024-04-01T00:00:00"),
    end: datetime = Query(..., example="2024-04-30T23:59:59"),
    db: Session = Depends(get_db)
):
    result = (
        db.query(
            CheckpointLog.truckId,
            func.min(CheckpointLog.checkInTime).label("start_time"),
            func.max(CheckpointLog.checkOutTime).label("end_time")
        )
        .filter(CheckpointLog.checkInTime >= start)
        .filter(CheckpointLog.checkOutTime <= end)
        .group_by(CheckpointLog.truckId)
        .all()
    )

    report = []
    for row in result:
        turnaround = (row.end_time - row.start_time) if row.end_time and row.start_time else None
        report.append({
            "truck_id": row.truckId,
            "start_time": row.start_time,
            "end_time": row.end_time,
            "turnaround_time_minutes": turnaround.total_seconds() // 60 if turnaround else None
        })

    return report
