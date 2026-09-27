# TracePass — Digital Product Passport & Supply-Chain Compliance System

Flask-based platform for product identity, composition, origin, supply-chain events, certificates and compliance.

## Features Implemented

### Phase 1 — Identity, Access & Organizations
- Flask app factory, config, blueprints
- Models: User, Role, Organization
- Register / Login / Logout / Change Password
- Password hashing + Flask-Login
- `@role_required()` decorator
- Admin: Users, Roles, Organizations, Settings
- **Public registration = Customer only** (other roles assigned by Admin)

### Phase 2 — Product Passport
- Products (passport code, status, compliance status)
- Batches / lots
- Materials catalog + product–material linking
- Publish passport + QR code (public link)

### Phase 3 — Supply-Chain Traceability
- Supply-chain events (sourcing, manufacturing, shipment, etc.)
- Shipments between organizations
- Chronological timeline view

### Phase 4 — Compliance
- Certificates (upload, expiry detection)
- Compliance rules
- Automated checks
- Auditor review queue (approve / reject / request correction)

### Phase 5 — Reporting & Public
- Dashboard with Chart.js (roles, product status, compliance)
- Audit log (recent activity)
- Public verify page + public passport view

## Quick Start

```bash
cd 01_tracepass
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python seed.py
python run.py
```

Open http://127.0.0.1:5000

## Demo Accounts

| Role | Email | Password |
|------|--------|----------|
| Admin | admin@tracepass.com | Admin@123 |
| Manufacturer | manufacturer@tracepass.com | Mfr@12345 |
| Auditor | auditor@tracepass.com | Audit@123 |

Public registration creates **Customer** accounts only.

## Key URLs

- Login: `/auth/login`
- Dashboard: `/dashboard`
- Products: `/products`
- Compliance queue: `/compliance/queue`
- Public verify: `/public/verify`
- Public passport: `/public/passport/<CODE>`

## Project Structure

```
01_tracepass/
├── app/
│   ├── auth/          # Login, register (Customer only)
│   ├── admin/         # Users, orgs, roles
│   ├── products/      # Passports, batches, materials
│   ├── supply/        # Events, shipments, timeline
│   ├── compliance/    # Rules, certificates, reviews
│   ├── public/        # Verify + public passport
│   ├── main/          # Dashboard
│   ├── models/
│   └── templates/
├── config.py
├── run.py
├── seed.py
└── requirements.txt
```

## REST API (`/api/v1`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/health` | No | Health check |
| POST | `/api/v1/auth/login` | No | JSON `{email, password}` |
| GET | `/api/v1/auth/me` | Yes | Current user |
| GET | `/api/v1/products` | Yes | List products (`?q=&status=`) |
| GET | `/api/v1/products/<id>` | Yes | Product detail |
| POST | `/api/v1/products` | Manufacturer/Admin | Create product |
| GET | `/api/v1/public/passport/<code>` | No | Public passport JSON |
| GET | `/api/v1/public/verify?code=` | No | Verify passport |
| GET | `/api/v1/organizations` | Yes | List orgs |
| GET | `/api/v1/compliance/rules` | Auditor/Admin | List rules |

Example:
```bash
curl -X POST http://127.0.0.1:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@tracepass.com","password":"Admin@123"}' -c cookies.txt

curl http://127.0.0.1:5000/api/v1/products -b cookies.txt
```

## Running Tests

```bash
pip install -r requirements.txt
pytest -v
```

## Docker + PostgreSQL (Production-style)

Requirements: Docker Desktop installed.

```bash
cd 01_tracepass
docker compose up --build
```

App: http://localhost:8000  
Postgres: localhost:5432 (user/pass/db: `tracepass` / `tracepass_secret` / `tracepass`)

Default admin after seed:
- Email: `admin@tracepass.com`
- Password: `Admin@123`

Stop:
```bash
docker compose down
```

Data persists in Docker volumes (`pgdata`, `uploads`).

### Environment

Copy `.env.example` to `.env` and set a strong `SECRET_KEY` before real deployment.

## Migrations

```bash
# Windows PowerShell / CMD (with venv active)
set FLASK_APP=run.py
flask db init
flask db migrate -m "initial schema"
flask db upgrade
```

Or run `init_migrations.sh` on Linux/Mac.

Local SQLite still works with `db.create_all()` via `seed.py` / app startup.

## PDF Passport

On product detail page click **PDF** to download a passport summary (ReportLab).

## Recalls

Compliance menu → **Recalls** → Issue / Close product recalls (also logged as supply-chain event).
