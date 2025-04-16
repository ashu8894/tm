from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User
from database import SessionLocal
from auth.dependencies import require_admin
from pydantic import BaseModel, Field
from typing import List, Optional

# ✅ Grouped in Swagger under 'Admin Users'
router = APIRouter(tags=["Admin Users"])

# ✅ DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Input model for updating user
class UserEdit(BaseModel):
    name: str = Field(..., example="Operator 1")
    role: str = Field(..., example="operator")  # 'operator' or 'admin'
    assignedCheckpointId: Optional[int] = Field(None, example=2)

# ✅ Output model for consistent API response
class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    assignedCheckpointId: Optional[int]

    class Config:
        orm_mode = True

# ✅ List all operators
@router.get(
    "/operators",
    summary="List all operators",
    description="Returns all users who have the role of 'operator'. Used by admin to manage factory staff.",
    response_model=List[UserOut],
    dependencies=[Depends(require_admin)]
)
def list_operators(db: Session = Depends(get_db)):
    return db.query(User).filter(User.role == "operator").all()

# ✅ Update an existing user
@router.patch(
    "/{user_id}",
    summary="Update a user's details",
    description="Allows admin to update a user's name, role, or assigned checkpoint. Mainly for managing operators.",
    response_model=UserOut,
    dependencies=[Depends(require_admin)]
)
def update_user(user_id: int, data: UserEdit, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.name = data.name
    user.role = data.role
    user.assignedCheckpointId = data.assignedCheckpointId
    db.commit()
    db.refresh(user)
    return user
