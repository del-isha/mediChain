from datetime import date, timedelta
from .models import *
from .auth import hash_password

def seed(db):
    if db.query(User).count():
        return

    facilities = [
        Facility(name="Punjab Central Warehouse", type="Warehouse", address="Mohali, Punjab", latitude=30.7046, longitude=76.7179),
        Facility(name="Chandigarh Distribution Center", type="Warehouse", address="Chandigarh", latitude=30.7333, longitude=76.7794),
        Facility(name="Himachal Regional Hospital", type="Hospital", address="Shimla, Himachal Pradesh", latitude=31.1048, longitude=77.1734),
        Facility(name="Delhi Regional Warehouse", type="Warehouse", address="New Delhi", latitude=28.6139, longitude=77.2090),
    ]
    db.add_all(facilities)
    db.flush()

    medicines = [
        Medicine(name="Insulin", manufacturer="ABC Pharma", category="Critical Care"),
        Medicine(name="Ceftriaxone", manufacturer="MediCore", category="Antibiotic"),
        Medicine(name="Paracetamol", manufacturer="HealthFirst", category="General"),
        Medicine(name="Amoxicillin", manufacturer="NovaMed", category="Antibiotic"),
    ]
    db.add_all(medicines)
    db.flush()

    today = date(2026, 8, 18)
    batches = [
        Batch(medicine_id=medicines[0].id, batch_number="DX48291", manufactured_date=date(2026,8,12), expiry_date=date(2028,8,12), status="VERIFIED"),
        Batch(medicine_id=medicines[0].id, batch_number="DX48292", manufactured_date=date(2025,3,10), expiry_date=date(2027,3,10), status="EXPIRING_SOON"),
        Batch(medicine_id=medicines[1].id, batch_number="CF28192", manufactured_date=date(2026,5,1), expiry_date=date(2028,5,1), status="VERIFIED"),
        Batch(medicine_id=medicines[2].id, batch_number="PC19281", manufactured_date=date(2026,4,5), expiry_date=date(2029,4,5), status="VERIFIED"),
        Batch(medicine_id=medicines[3].id, batch_number="AM18273", manufactured_date=date(2026,1,15), expiry_date=date(2027,1,15), status="VERIFIED"),
    ]
    db.add_all(batches)
    db.flush()

    inv = [
        Inventory(facility_id=facilities[0].id, batch_id=batches[0].id, quantity=5000),
        Inventory(facility_id=facilities[0].id, batch_id=batches[1].id, quantity=2100),
        Inventory(facility_id=facilities[1].id, batch_id=batches[2].id, quantity=8200),
        Inventory(facility_id=facilities[1].id, batch_id=batches[3].id, quantity=21000),
        Inventory(facility_id=facilities[2].id, batch_id=batches[4].id, quantity=1200),
        Inventory(facility_id=facilities[2].id, batch_id=batches[0].id, quantity=420),
        Inventory(facility_id=facilities[3].id, batch_id=batches[2].id, quantity=7500),
    ]
    db.add_all(inv)
    db.flush()

    users = [
        User(name="System Administrator", email="admin@medchain.local", password_hash=hash_password("admin123"), role="ADMIN", facility_id=facilities[0].id),
        User(name="Authorized Officer", email="officer@medchain.local", password_hash=hash_password("officer123"), role="OFFICER", facility_id=facilities[0].id),
        User(name="Warehouse Manager", email="warehouse@medchain.local", password_hash=hash_password("warehouse123"), role="WAREHOUSE", facility_id=facilities[0].id),
        User(name="Hospital Administrator", email="hospital@medchain.local", password_hash=hash_password("hospital123"), role="HOSPITAL", facility_id=facilities[2].id),
    ]
    db.add_all(users)

    alerts = [
        Alert(facility_id=facilities[2].id, medicine_id=medicines[0].id, type="STOCK", message="Insulin stock below emergency threshold", severity="CRITICAL"),
        Alert(facility_id=facilities[0].id, medicine_id=medicines[0].id, type="EXPIRY", message="Batch DX48292 expires within 180 days", severity="WARNING"),
        Alert(facility_id=facilities[2].id, medicine_id=medicines[3].id, type="STOCK", message="Amoxicillin inventory is low", severity="WARNING"),
    ]
    db.add_all(alerts)
    db.commit()
