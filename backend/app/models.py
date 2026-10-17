from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(160), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(40), nullable=False)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=True)
    facility = relationship("Facility")

class Facility(Base):
    __tablename__ = "facilities"
    id = Column(Integer, primary_key=True)
    name = Column(String(160), nullable=False)
    type = Column(String(60), nullable=False)
    address = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

class Medicine(Base):
    __tablename__ = "medicines"
    id = Column(Integer, primary_key=True)
    name = Column(String(160), nullable=False)
    manufacturer = Column(String(160), nullable=False)
    category = Column(String(100), nullable=False)

class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    batch_number = Column(String(80), unique=True, nullable=False)
    manufactured_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    status = Column(String(40), default="VERIFIED")
    medicine = relationship("Medicine")

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    quantity = Column(Integer, default=0)
    facility = relationship("Facility")
    batch = relationship("Batch")

class Transfer(Base):
    __tablename__ = "transfers"
    id = Column(Integer, primary_key=True)
    source_facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    destination_facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)
    priority = Column(String(30), default="NORMAL")
    status = Column(String(40), default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)
    source = relationship("Facility", foreign_keys=[source_facility_id])
    destination = relationship("Facility", foreign_keys=[destination_facility_id])
    batch = relationship("Batch")

class Approval(Base):
    __tablename__ = "approvals"
    id = Column(Integer, primary_key=True)
    transfer_id = Column(Integer, ForeignKey("transfers.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    decision = Column(String(30), nullable=False)
    comment = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.utcnow)
    approver = relationship("User")

class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True)
    transfer_id = Column(Integer, ForeignKey("transfers.id"), unique=True, nullable=False)
    status = Column(String(40), default="READY")
    dispatched_at = Column(DateTime, nullable=True)
    received_at = Column(DateTime, nullable=True)

class CustodyEvent(Base):
    __tablename__ = "custody_events"
    id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(60), nullable=False)
    location = Column(String(160), nullable=False)
    quantity = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    actor = relationship("User")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=True)
    type = Column(String(60), nullable=False)
    message = Column(String(255), nullable=False)
    severity = Column(String(30), nullable=False)
    status = Column(String(30), default="OPEN")
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity = Column(String(80), nullable=False)
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
