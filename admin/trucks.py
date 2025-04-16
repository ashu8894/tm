from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import Truck, Checkpoint
from database import SessionLocal
from auth.dependencies import require_admin
from pydantic import BaseModel, Field
from typing import List, Optional

# ✅ Tag for grouping in Swagger UI
router = APIRouter(tags=["Admin Trucks"])

# ✅ DB Session Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Response Model for Clean Docs
class TruckStatusResponse(BaseModel):
    truck_id: int = Field(..., example=101)
    identifier: str = Field(..., example="HR55AB1234")
    checkpoint: str = Field(..., example="Dock 2")
    status: str = Field(..., example="in_progress")
    notes: Optional[str] = Field(None, example="Waiting for inspection")

    class Config:
        orm_mode = True

@router.get(
    "/status",
    summary="View real-time truck status",
    description="Returns a list of all trucks inside the factory with their current checkpoint, status, and any notes.",
    response_model=List[TruckStatusResponse],
    dependencies=[Depends(require_admin)]
)
def live_truck_status(db: Session = Depends(get_db)):
    trucks = (
        db.query(Truck, Checkpoint)
        .join(Checkpoint, Truck.currentCheckpointId == Checkpoint.id)
        .all()
    )

    return [
        {
            "truck_id": t.Truck.id,
            "identifier": t.Truck.truckIdentifier,
            "checkpoint": t.Checkpoint.name,
            "status": t.Truck.status,
            "notes": t.Truck.notes
        }
        for t in trucks
    ]
