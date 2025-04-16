from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Workflow, Checkpoint
from database import SessionLocal
from auth.dependencies import require_admin
from pydantic import BaseModel, Field
from typing import List

# ✅ Cleanly tagged for Swagger UI grouping
router = APIRouter(tags=["Admin Workflow"])

# ✅ DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Checkpoint Models ----------

class CheckpointIn(BaseModel):
    name: str = Field(..., example="Dock 1")
    description: str = Field(..., example="Initial unloading dock")
    workflowId: int = Field(..., example=1)
    position: int = Field(..., example=1)

class CheckpointOut(BaseModel):
    id: int
    name: str
    description: str
    workflowId: int
    position: int

    class Config:
        from_attributes = True

# ✅ Route: POST /workflows/checkpoints
@router.post(
    "/checkpoints",
    summary="Create a checkpoint for a workflow",
    description="Allows admins to attach a checkpoint (like a dock or inspection bay) to a workflow in sequence.",
    response_model=CheckpointOut,
    dependencies=[Depends(require_admin)]
)
def create_checkpoint(data: CheckpointIn, db: Session = Depends(get_db)):
    cp = Checkpoint(**data.dict())
    db.add(cp)
    db.commit()
    db.refresh(cp)
    return cp

# ✅ Route: GET /workflows/checkpoints
@router.get(
    "/checkpoints",
    summary="Get all checkpoints",
    description="Returns a list of all checkpoints configured in workflows.",
    response_model=List[CheckpointOut],
    dependencies=[Depends(require_admin)]
)
def get_all_checkpoints(db: Session = Depends(get_db)):
    return db.query(Checkpoint).all()

# ✅ Route: GET /workflows/checkpoints/{checkpoint_id}
@router.get(
    "/checkpoints/{checkpoint_id}",
    summary="Get a specific checkpoint by ID",
    description="Returns the checkpoint with the specified ID.",
    response_model=CheckpointOut,
    dependencies=[Depends(require_admin)]
)
def get_checkpoint_by_id(checkpoint_id: int, db: Session = Depends(get_db)):
    checkpoint = db.query(Checkpoint).get(checkpoint_id)
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return checkpoint

# ✅ Route: PATCH /workflows/checkpoints/{checkpoint_id}
@router.patch(
    "/checkpoints/{checkpoint_id}",
    summary="Update a checkpoint",
    description="Allows admins to update the name, description, workflow, or position of a checkpoint.",
    response_model=CheckpointOut,
    dependencies=[Depends(require_admin)]
)
def update_checkpoint(checkpoint_id: int, data: CheckpointIn, db: Session = Depends(get_db)):
    checkpoint = db.query(Checkpoint).get(checkpoint_id)
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    checkpoint.name = data.name
    checkpoint.description = data.description
    checkpoint.workflowId = data.workflowId
    checkpoint.position = data.position
    db.commit()
    db.refresh(checkpoint)
    return checkpoint



# ---------- Workflow Models ----------

class WorkflowIn(BaseModel):
    name: str = Field(..., example="Inbound Dock Workflow")
    description: str = Field(..., example="Handles check-in to unloading.")

class WorkflowOut(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True

# ✅ Route: POST /workflows/
@router.post(
    "/",
    summary="Create a new workflow",
    description="Allows admins to create a new truck movement workflow inside the factory.",
    response_model=WorkflowOut,
    dependencies=[Depends(require_admin)]
)
def create_workflow(data: WorkflowIn, db: Session = Depends(get_db)):
    wf = Workflow(name=data.name, description=data.description)
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return wf

# ✅ Route: GET /workflows/
@router.get(
    "/",
    summary="Get all workflows",
    description="Returns a list of all configured workflows.",
    response_model=List[WorkflowOut],
    dependencies=[Depends(require_admin)]
)
def get_all_workflows(db: Session = Depends(get_db)):
    return db.query(Workflow).all()

# ✅ Route: GET /workflows/{workflow_id}
@router.get(
    "/{workflow_id}",
    summary="Get a specific workflow by ID",
    description="Returns the workflow with the specified ID.",
    response_model=WorkflowOut,
    dependencies=[Depends(require_admin)]
)
def get_workflow_by_id(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.query(Workflow).get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

# ✅ Route: PATCH /workflows/{workflow_id}
@router.patch(
    "/{workflow_id}",
    summary="Update a workflow",
    description="Allows admins to update name or description of an existing workflow.",
    response_model=WorkflowOut,
    dependencies=[Depends(require_admin)]
)
def update_workflow(workflow_id: int, data: WorkflowIn, db: Session = Depends(get_db)):
    workflow = db.query(Workflow).get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow.name = data.name
    workflow.description = data.description
    db.commit()
    db.refresh(workflow)
    return workflow

