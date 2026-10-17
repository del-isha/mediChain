from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class LoginRequest(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    role: str
    facility_id: Optional[int] = None

class FacilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    type: str
    address: str
    latitude: float
    longitude: float

class MedicineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    manufacturer: str
    category: str

class BatchOut(BaseModel):
    id: int
    medicine_id: int
    medicine_name: str
    batch_number: str
    manufactured_date: date
    expiry_date: date
    status: str

class InventoryOut(BaseModel):
    id: int
    facility_id: int
    facility_name: str
    batch_id: int
    medicine_name: str
    batch_number: str
    quantity: int
    expiry_date: date
    status: str

class TransferCreate(BaseModel):
    source_facility_id: int
    destination_facility_id: int
    batch_id: int
    quantity: int
    reason: str
    priority: str = "NORMAL"

class TransferOut(BaseModel):
    id: int
    source_facility: str
    destination_facility: str
    medicine: str
    batch_number: str
    quantity: int
    reason: str
    priority: str
    status: str
    created_at: datetime

class DecisionRequest(BaseModel):
    comment: str = ""

class AuditOut(BaseModel):
    id: int
    action: str
    entity: str
    entity_id: Optional[int]
    details: str
    timestamp: datetime
    user_name: Optional[str]
