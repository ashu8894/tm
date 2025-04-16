# models.py
from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)  # 'admin' or 'operator'
    assignedCheckpointId = Column(Integer, ForeignKey("checkpoints.id"))

class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)

class Checkpoint(Base):
    __tablename__ = "checkpoints"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    workflowId = Column(Integer, ForeignKey("workflows.id"))
    position = Column(Integer)

class Truck(Base):
    __tablename__ = "trucks"
    id = Column(Integer, primary_key=True, index=True)
    truckIdentifier = Column(String, unique=True)
    currentCheckpointId = Column(Integer, ForeignKey("checkpoints.id"))
    status = Column(String)
    notes = Column(Text)

class CheckpointLog(Base):
    __tablename__ = "checkpointlogs"
    id = Column(Integer, primary_key=True, index=True)
    truckId = Column(Integer, ForeignKey("trucks.id"))
    checkpointId = Column(Integer, ForeignKey("checkpoints.id"))
    operatorId = Column(Integer, ForeignKey("users.id"))
    checkInTime = Column(DateTime, default=datetime.datetime.utcnow)
    checkOutTime = Column(DateTime, nullable=True)
    notes = Column(Text)
