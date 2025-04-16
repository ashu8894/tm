from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Truck, CheckpointLog, Checkpoint
from auth.dependencies import require_operator
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

router = APIRouter(tags=["Operator"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# ✅ 1. View assigned checkpoint
# -----------------------------
@router.get(
    "/checkpoint",
    summary="View assigned checkpoint",
    description="Returns the checkpoint assigned to the logged-in operator."
)
def get_assigned_checkpoint(current_user: dict = Depends(require_operator), db: Session = Depends(get_db)):
    user = db.query(User).get(current_user["user_id"])
    if not user or not user.assignedCheckpointId:
        raise HTTPException(status_code=404, detail="No checkpoint assigned")

    checkpoint = db.query(Checkpoint).get(user.assignedCheckpointId)
    return {
        "checkpoint_id": checkpoint.id,
        "name": checkpoint.name,
        "description": checkpoint.description
    }

# ----------------------------------
# ✅ 2. List pending trucks at checkpoint
# ----------------------------------
@router.get(
    "/trucks",
    summary="List pending trucks",
    description="Returns all trucks currently at the operator's checkpoint."
)
def list_pending_trucks(current_user: dict = Depends(require_operator), db: Session = Depends(get_db)):
    checkpoint_id = db.query(User).get(current_user["user_id"]).assignedCheckpointId
    trucks = db.query(Truck).filter(Truck.currentCheckpointId == checkpoint_id).all()

    return [
        {
            "truck_id": t.id,
            "identifier": t.truckIdentifier,
            "status": t.status,
            "notes": t.notes
        } for t in trucks
    ]

# ✅ Add Truck Model
class TruckCreate(BaseModel):
    truckIdentifier: str = Field(..., example="DL01AX1234")
    status: str = Field(..., example="in_progress")
    notes: Optional[str] = Field(None, example="Arrived at gate")

    class Config:
        from_attributes = True

@router.post(
    "/create",
    summary="Add a new truck (by operator)",
    description="Allows operators to add a new truck at their assigned checkpoint.",
    dependencies=[Depends(require_operator)]
)
def create_truck(data: TruckCreate, current_user: dict = Depends(require_operator), db: Session = Depends(get_db)):
    user = db.query(User).get(current_user["user_id"])

    if not user or not user.assignedCheckpointId:
        raise HTTPException(status_code=400, detail="Operator checkpoint not assigned")

    truck = Truck(
        truckIdentifier=data.truckIdentifier,
        currentCheckpointId=user.assignedCheckpointId,
        status=data.status,
        notes=data.notes
    )
    db.add(truck)
    db.commit()
    db.refresh(truck)

    return {
        "message": "Truck created successfully",
        "truck_id": truck.id
    }

# ----------------------------------
# ✅ 3. Check-in / Check-out truck
# ----------------------------------
class TruckLogIn(BaseModel):
    truck_id: int = Field(..., example=5)
    action: str = Field(..., example="checkin")  # or "checkout"
    notes: Optional[str] = Field(None, example="Truck arrived 10 mins late")

@router.post(
    "/log",
    summary="Check-in or Check-out truck",
    description="Logs check-in or check-out timestamp for a truck by the operator. Adds optional notes."
)
def log_checkpoint_action(data: TruckLogIn, current_user: dict = Depends(require_operator), db: Session = Depends(get_db)):
    operator_id = current_user["user_id"]
    checkpoint_id = db.query(User).get(operator_id).assignedCheckpointId

    # Check if truck is at this checkpoint
    truck = db.query(Truck).get(data.truck_id)
    if not truck or truck.currentCheckpointId != checkpoint_id:
        raise HTTPException(status_code=400, detail="Truck not at your checkpoint")

    # Find existing log
    log = db.query(CheckpointLog).filter_by(
        truckId=data.truck_id,
        checkpointId=checkpoint_id,
        operatorId=operator_id
    ).first()

    if data.action == "checkin":
        if log and log.checkInTime:
            raise HTTPException(status_code=400, detail="Truck already checked in")
        if not log:
            log = CheckpointLog(
                truckId=data.truck_id,
                checkpointId=checkpoint_id,
                operatorId=operator_id,
                checkInTime=datetime.utcnow(),
                notes=data.notes
            )
            db.add(log)
        else:
            log.checkInTime = datetime.utcnow()
            log.notes = data.notes

    elif data.action == "checkout":
        if not log or not log.checkInTime:
            raise HTTPException(status_code=400, detail="Truck must be checked in first")
        if log.checkOutTime:
            raise HTTPException(status_code=400, detail="Truck already checked out")
        log.checkOutTime = datetime.utcnow()
        if data.notes:
            log.notes = data.notes

    else:
        raise HTTPException(status_code=400, detail="Invalid action. Must be 'checkin' or 'checkout'")

    db.commit()
    db.refresh(log)
    return {
        "message": f"Truck {data.action} successful",
        "timestamp": log.checkInTime if data.action == "checkin" else log.checkOutTime
    }
