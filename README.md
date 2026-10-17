# MEDCHAIN — Full-Stack Hackathon MVP

A realistic medicine emergency supply-chain application focused on:
- inventory and batches
- facilities
- emergency transfers
- role-based approval
- shipment dispatch/receiving
- medicine QR passport lookup
- alerts
- audit history

## Stack

Frontend:
- React + Vite
- Tailwind CSS
- React Router
- Axios
- Recharts
- Leaflet + OpenStreetMap
- lucide-react
- html5-qrcode

Backend:
- FastAPI
- SQLAlchemy
- Pydantic
- JWT authentication
- SQLite by default for zero-setup local development
- PostgreSQL-ready via DATABASE_URL

## Run

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API starts at http://127.0.0.1:8000
Swagger: http://127.0.0.1:8000/docs

Seed users:
- admin@medchain.local / admin123
- officer@medchain.local / officer123
- warehouse@medchain.local / warehouse123
- hospital@medchain.local / hospital123

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

## PostgreSQL

The backend defaults to SQLite so the team can demo immediately.
For PostgreSQL, set:

```bash
export DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:5432/medchain"
```

Then install the existing `psycopg[binary]` dependency from requirements.txt.

## Demo flow

1. Login as hospital.
2. Open Inventory / Dashboard.
3. Create an emergency transfer.
4. Login as officer and approve it.
5. Login as warehouse and dispatch.
6. Login as hospital and receive.
7. Open the batch passport.
8. Open Audit Log to see the workflow.
