from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from auth.auth_handler import create_access_token
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(tags=["Auth"])  # Adds a dedicated 'Auth' section in docs

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Models ----------

class RegisterRequest(BaseModel):
    name: str = Field(..., example="Ashutosh")
    email: str = Field(..., example="ashu@factory.com")
    password: str = Field(..., example="admin123")
    role: str = Field(..., example="admin")  # 'admin' or 'operator'
    assignedCheckpointId: Optional[int] = Field(None, example=1)

class RegisterResponse(BaseModel):
    message: str = Field(..., example="User registered successfully")
    user_id: int = Field(..., example=1)

class LoginRequest(BaseModel):
    email: str = Field(..., example="ashu@factory.com")
    password: str = Field(..., example="admin123")

class LoginResponse(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5...")
    token_type: str = Field(..., example="bearer")

# ---------- Routes ----------

@router.post(
    "/register",
    summary="Register a new user",
    response_model=RegisterResponse
)
def register_user(user: RegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user (admin or operator). Only used by admin (manually or from frontend later).
    """
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password,  # plain text for demo
        role=user.role,
        assignedCheckpointId=user.assignedCheckpointId
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id}


@router.post(
    "/login",
    summary="Authenticate user and return JWT token",
    response_model=LoginResponse
)
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login route to authenticate user and return access token.
    """
    user = db.query(User).filter(User.email == data.email).first()
    if not user or user.password != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": user.email,
        "role": user.role,
        "user_id": user.id
    })
    return {"access_token": token, "token_type": "bearer"}
