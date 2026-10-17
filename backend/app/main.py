from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .database import Base, engine, get_db
from .models import *
from .schemas import *
from .auth import *
from .seed import seed

Base.metadata.create_all(bind=engine)
with next(get_db()) as _db:
    seed(_db)

app = FastAPI(title="MEDCHAIN API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def audit(db, user, action, entity, entity_id=None, details=""):
    db.add(AuditLog(user_id=user.id if user else None, action=action, entity=entity, entity_id=entity_id, details=details))

@app.get("/")
def root():
    return {"name": "MEDCHAIN API", "status": "running"}

@app.post("/api/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return {"access_token": create_token(user.id), "token_type": "bearer", "user": UserOut.model_validate(user)}

@app.get("/api/auth/me", response_model=UserOut)
def me(user=Depends(current_user)):
    return user

@app.get("/api/facilities", response_model=list[FacilityOut])
def facilities(db: Session = Depends(get_db), user=Depends(current_user)):
    return db.query(Facility).all()

@app.get("/api/medicines", response_model=list[MedicineOut])
def medicines(db: Session = Depends(get_db), user=Depends(current_user)):
    return db.query(Medicine).all()

@app.get("/api/batches", response_model=list[BatchOut])
def batches(db: Session = Depends(get_db), user=Depends(current_user)):
    rows = db.query(Batch).join(Medicine).all()
    return [BatchOut(id=b.id, medicine_id=b.medicine_id, medicine_name=b.medicine.name, batch_number=b.batch_number,
                     manufactured_date=b.manufactured_date, expiry_date=b.expiry_date, status=b.status) for b in rows]

@app.get("/api/inventory", response_model=list[InventoryOut])
def inventory(db: Session = Depends(get_db), user=Depends(current_user)):
    rows = db.query(Inventory).join(Facility).join(Batch).join(Medicine).all()
    return [InventoryOut(id=x.id, facility_id=x.facility_id, facility_name=x.facility.name, batch_id=x.batch_id,
                         medicine_name=x.batch.medicine.name, batch_number=x.batch.batch_number, quantity=x.quantity,
                         expiry_date=x.batch.expiry_date, status=x.batch.status) for x in rows]

@app.get("/api/transfers", response_model=list[TransferOut])
def transfers(db: Session = Depends(get_db), user=Depends(current_user)):
    rows = db.query(Transfer).order_by(desc(Transfer.created_at)).all()
    return [TransferOut(id=x.id, source_facility=x.source.name, destination_facility=x.destination.name,
                        medicine=x.batch.medicine.name, batch_number=x.batch.batch_number, quantity=x.quantity,
                        reason=x.reason, priority=x.priority, status=x.status, created_at=x.created_at) for x in rows]

@app.post("/api/transfers", response_model=TransferOut)
def create_transfer(payload: TransferCreate, db: Session = Depends(get_db), user=Depends(current_user)):
    if payload.quantity <= 0:
        raise HTTPException(400, "Quantity must be positive")
    stock = db.query(Inventory).filter(Inventory.facility_id == payload.source_facility_id,
                                        Inventory.batch_id == payload.batch_id).first()
    if not stock or stock.quantity < payload.quantity:
        raise HTTPException(400, "Insufficient source inventory")
    transfer = Transfer(**payload.model_dump())
    db.add(transfer)
    db.flush()
    audit(db, user, "TRANSFER_CREATED", "transfer", transfer.id, f"{payload.quantity} units requested")
    db.commit()
    db.refresh(transfer)
    return TransferOut(id=transfer.id, source_facility=transfer.source.name, destination_facility=transfer.destination.name,
                       medicine=transfer.batch.medicine.name, batch_number=transfer.batch.batch_number, quantity=transfer.quantity,
                       reason=transfer.reason, priority=transfer.priority, status=transfer.status, created_at=transfer.created_at)

@app.post("/api/transfers/{transfer_id}/approve", response_model=TransferOut)
def approve_transfer(transfer_id: int, payload: DecisionRequest, db: Session = Depends(get_db), user=Depends(require_roles("ADMIN", "OFFICER"))):
    t = db.get(Transfer, transfer_id)
    if not t: raise HTTPException(404, "Transfer not found")
    if t.status != "PENDING": raise HTTPException(400, "Transfer is not pending")
    stock = db.query(Inventory).filter(Inventory.facility_id == t.source_facility_id, Inventory.batch_id == t.batch_id).first()
    if not stock or stock.quantity < t.quantity:
        raise HTTPException(400, "Source inventory is no longer sufficient")
    t.status = "APPROVED"
    db.add(Approval(transfer_id=t.id, approver_id=user.id, decision="APPROVED", comment=payload.comment))
    db.add(Shipment(transfer_id=t.id, status="READY"))
    audit(db, user, "TRANSFER_APPROVED", "transfer", t.id, payload.comment)
    db.commit()
    db.refresh(t)
    return TransferOut(id=t.id, source_facility=t.source.name, destination_facility=t.destination.name,
                       medicine=t.batch.medicine.name, batch_number=t.batch.batch_number, quantity=t.quantity,
                       reason=t.reason, priority=t.priority, status=t.status, created_at=t.created_at)

@app.post("/api/transfers/{transfer_id}/reject", response_model=TransferOut)
def reject_transfer(transfer_id: int, payload: DecisionRequest, db: Session = Depends(get_db), user=Depends(require_roles("ADMIN", "OFFICER"))):
    t = db.get(Transfer, transfer_id)
    if not t: raise HTTPException(404, "Transfer not found")
    t.status = "REJECTED"
    db.add(Approval(transfer_id=t.id, approver_id=user.id, decision="REJECTED", comment=payload.comment))
    audit(db, user, "TRANSFER_REJECTED", "transfer", t.id, payload.comment)
    db.commit()
    return TransferOut(id=t.id, source_facility=t.source.name, destination_facility=t.destination.name,
                       medicine=t.batch.medicine.name, batch_number=t.batch.batch_number, quantity=t.quantity,
                       reason=t.reason, priority=t.priority, status=t.status, created_at=t.created_at)

@app.post("/api/shipments/{transfer_id}/dispatch")
def dispatch(transfer_id: int, db: Session = Depends(get_db), user=Depends(require_roles("ADMIN", "WAREHOUSE"))):
    t = db.get(Transfer, transfer_id)
    shipment = db.query(Shipment).filter(Shipment.transfer_id == transfer_id).first()
    if not t or not shipment: raise HTTPException(404, "Shipment not found")
    if t.status != "APPROVED": raise HTTPException(400, "Transfer must be approved first")
    stock = db.query(Inventory).filter(Inventory.facility_id == t.source_facility_id, Inventory.batch_id == t.batch_id).first()
    if not stock or stock.quantity < t.quantity: raise HTTPException(400, "Insufficient inventory")
    stock.quantity -= t.quantity
    shipment.status = "IN_TRANSIT"
    shipment.dispatched_at = datetime.utcnow()
    db.add(CustodyEvent(shipment_id=shipment.id, actor_id=user.id, event_type="DISPATCHED", location=t.source.name, quantity=t.quantity))
    t.status = "IN_TRANSIT"
    audit(db, user, "SHIPMENT_DISPATCHED", "shipment", shipment.id, f"{t.quantity} units")
    db.commit()
    return {"message": "Shipment dispatched", "status": t.status}

@app.post("/api/shipments/{transfer_id}/receive")
def receive(transfer_id: int, db: Session = Depends(get_db), user=Depends(require_roles("ADMIN", "HOSPITAL"))):
    t = db.get(Transfer, transfer_id)
    shipment = db.query(Shipment).filter(Shipment.transfer_id == transfer_id).first()
    if not t or not shipment: raise HTTPException(404, "Shipment not found")
    if t.status != "IN_TRANSIT": raise HTTPException(400, "Shipment is not in transit")
    target_stock = db.query(Inventory).filter(Inventory.facility_id == t.destination_facility_id, Inventory.batch_id == t.batch_id).first()
    if target_stock:
        target_stock.quantity += t.quantity
    else:
        target_stock = Inventory(facility_id=t.destination_facility_id, batch_id=t.batch_id, quantity=t.quantity)
        db.add(target_stock)
    shipment.status = "RECEIVED"
    shipment.received_at = datetime.utcnow()
    t.status = "RECEIVED"
    db.add(CustodyEvent(shipment_id=shipment.id, actor_id=user.id, event_type="RECEIVED", location=t.destination.name, quantity=t.quantity))
    audit(db, user, "SHIPMENT_RECEIVED", "shipment", shipment.id, f"{t.quantity} units")
    db.commit()
    return {"message": "Shipment received", "status": t.status}

@app.get("/api/alerts")
def alerts(db: Session = Depends(get_db), user=Depends(current_user)):
    return db.query(Alert).order_by(desc(Alert.created_at)).all()

@app.get("/api/audit", response_model=list[AuditOut])
def audit_logs(db: Session = Depends(get_db), user=Depends(current_user)):
    rows = db.query(AuditLog).order_by(desc(AuditLog.timestamp)).limit(100).all()
    return [AuditOut(id=x.id, action=x.action, entity=x.entity, entity_id=x.entity_id, details=x.details,
                     timestamp=x.timestamp, user_name=x.user.name if x.user else None) for x in rows]

@app.get("/api/passport/{batch_id}")
def passport(batch_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    batch = db.get(Batch, batch_id)
    if not batch: raise HTTPException(404, "Batch not found")
    inv = db.query(Inventory).filter(Inventory.batch_id == batch_id, Inventory.quantity > 0).all()
    events = db.query(CustodyEvent).join(Shipment).join(Transfer).filter(Transfer.batch_id == batch_id).order_by(CustodyEvent.timestamp).all()
    return {
        "batch_id": batch.id,
        "medicine": batch.medicine.name,
        "manufacturer": batch.medicine.manufacturer,
        "batch_number": batch.batch_number,
        "manufactured_date": str(batch.manufactured_date),
        "expiry_date": str(batch.expiry_date),
        "status": batch.status,
        "current_locations": [{"facility": x.facility.name, "quantity": x.quantity} for x in inv],
        "journey": [{"event": e.event_type, "location": e.location, "quantity": e.quantity, "timestamp": e.timestamp} for e in events]
    }

@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db), user=Depends(current_user)):
    inv = db.query(Inventory).all()
    critical = sum(1 for x in inv if x.quantity < 500)
    total = sum(x.quantity for x in inv)
    transfers = db.query(Transfer).count()
    pending = db.query(Transfer).filter(Transfer.status == "PENDING").count()
    return {"total_units": total, "critical_inventory": critical, "transfers": transfers, "pending_approvals": pending}
