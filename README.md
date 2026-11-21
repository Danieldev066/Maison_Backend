<div align="center">

# MAISON Restaurant API

**FastAPI backend for the MAISON restaurant web and Flutter applications**

Python 3.12 · FastAPI · SQLAlchemy 2 · Alembic · JWT · PostgreSQL / SQLite · Pytest

</div>

---

## Overview

MAISON is a restaurant backend MVP that exposes a shared REST API for a website, a Flutter mobile app, and an administrator interface. The backend handles customers, restaurant information, menu items, table reservations, and food orders.

> **Status:** MVP / integration testing. The API has been run locally, with **8 automated tests passing** as of November 21, 2026. Production hardening and deployment verification are still required.

## Features

- **Accounts:** customer registration, sign-in with bearer JWT, and profile management.
- **Restaurant:** public restaurant information and administrative updates.
- **Menu:** categories and dishes, search, availability, and admin management.
- **Reservations:** table availability checks, booking, viewing, and cancellation.
- **Orders:** pickup or dine-in orders, server-calculated totals, personal order history, cancellation, and staff status management.
- **Access control:** customer-owned resources and admin-only endpoints.
- **Documentation:** automatic Swagger UI and OpenAPI schema.

**Not included in this MVP:** payment gateway, SMS/push notifications, password reset, inventory tracking, and real-time kitchen updates.

## Tech stack

| Layer | Technology |
| --- | --- |
| API | FastAPI, Python 3.12 |
| Persistence | SQLAlchemy 2, Alembic |
| Database | SQLite (local development), PostgreSQL (deployment target) |
| Validation | Pydantic v2 |
| Authentication | JWT bearer tokens |
| Tests | Pytest, FastAPI TestClient |
| Hosting | Ubuntu / AWS EC2, Nginx, Uvicorn (deployment option) |

## Quick start (Windows / PyCharm)

Run the commands from the directory containing `app/`, `requirements.txt`, and `alembic.ini` (currently `my_site/` in the local development workspace).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the generated secret into `SECRET_KEY=` in `.env`. For local SQLite development, use:

```dotenv
DATABASE_URL=sqlite:///./maison.db
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

Then run:

```powershell
python -m alembic upgrade head
python -m scripts.seed
python -m uvicorn app.main:app --reload
```

If the database is already initialized, do **not** overwrite or delete it just to follow this guide.

| Local URL | Description |
| --- | --- |
| `http://127.0.0.1:8000/docs` | Swagger UI |
| `http://127.0.0.1:8000/openapi.json` | OpenAPI schema |
| `http://127.0.0.1:8000/health` | Health check |
| `http://127.0.0.1:8000/api/v1` | API base URL |

## API endpoints

All endpoints below are relative to `/api/v1`. Some require a valid JWT; admin operations require an administrator account.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/auth/register` | Register a customer |
| `POST` | `/auth/login` | Sign in and obtain JWT |
| `GET`, `PATCH` | `/users/me` | View / edit profile |
| `GET`, `PATCH` | `/restaurant` | Restaurant information / admin update |
| `GET`, `POST` | `/menu/categories` | List / create categories |
| `GET`, `POST` | `/menu/items` | List / create menu items |
| `GET`, `PATCH`, `DELETE` | `/menu/items/{item_id}` | View / edit / archive a menu item |
| `GET`, `POST` | `/tables` | List / add tables |
| `GET` | `/reservations/availability` | Check available tables |
| `GET`, `POST` | `/reservations` | View / create own reservations |
| `GET` | `/reservations/{reservation_id}` | View reservation |
| `POST` | `/reservations/{reservation_id}/cancel` | Cancel reservation |
| `GET` | `/admin/reservations` | Admin reservation list |
| `GET`, `POST` | `/orders` | View / create own orders |
| `GET` | `/orders/{order_id}` | View order details |
| `POST` | `/orders/{order_id}/cancel` | Cancel eligible order |
| `GET` | `/admin/orders` | Admin order list |
| `PATCH` | `/admin/orders/{order_id}/status` | Update order status |

See [`API_CONTRACT.md`](API_CONTRACT.md) and `/docs` for request schemas, example responses, and the authoritative current OpenAPI definition.

### Example: create a pickup order

Authenticate with `POST /api/v1/auth/login`, then send:

```http
POST /api/v1/orders
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "order_type": "pickup",
  "items": [{"menu_item_id": 1, "quantity": 2}],
  "notes": "No onions"
}
```

Use a real available `menu_item_id`. Prices are retrieved and calculated on the server in whole Kyrgyz som (`price_som`, `total_som`), not accepted from the client.

For `dine_in`, a confirmed reservation owned by the current user is required.

## Connecting web frontend and Flutter

**Local web:** `http://127.0.0.1:8000/api/v1` (when the backend runs on the same machine).

**Android emulator:** `http://10.0.2.2:8000/api/v1` (emulator to the host development machine).

**Deployed clients:** use `https://YOUR_DOMAIN/api/v1` after HTTPS is configured. A public IPv4 address can be used for initial connectivity tests over HTTP, but **never send credentials or tokens over public HTTP**.

Clients must attach `Authorization: Bearer <access_token>` on protected requests. Configure `CORS_ORIGINS` for exact website origins; native Flutter does not use browser CORS.

## Tests

```powershell
python -m pytest -q
python -m alembic current
```

Latest local test result reported: **8 passed, 1 deprecation warning**. Passing tests do not replace PostgreSQL concurrency, load, and security testing.

## Deployment notes

The intended public architecture is **client → HTTPS/Nginx → FastAPI → PostgreSQL**. Before going live:

1. Keep `.env` and credentials outside Git; generate a unique `SECRET_KEY` and database password.
2. Use PostgreSQL for real multi-user deployment; SQLite is for local development.
3. Apply migrations with `python -m alembic upgrade head` (or through a vetted container entrypoint).
4. Run Uvicorn behind Nginx, bound to `127.0.0.1:8000` when using a systemd service.
5. Expose only SSH (restricted source), HTTP (for HTTPS redirection/certificate setup), and HTTPS from the EC2 Security Group.
6. Configure TLS, backups, logging, CORS, and administrative access before public release.

Do not treat a reachable `/docs` page as evidence that the service is production ready.

## Project layout

```text
app/
  api/               # auth, restaurant, menu, reservations, orders
  core/              # settings, JWT/security
  db/                # session and Base
  main.py            # FastAPI application
  models.py          # SQLAlchemy entities
  schemas.py         # Pydantic models
migrations/           # Alembic revisions
scripts/              # demo data seed
tests/               # Pytest test suite
API_CONTRACT.md       # REST API contract
requirements.txt
.env.example
```

## Team workflow

Development happens in separate Git branches. The `Daniel` branch is used for the owner's work; changes should be reviewed and integrated into the team branch intentionally. Do not force-push shared branches or commit `.env`, database files, access tokens, or customer data.

---

**MAISON Restaurant — Backend MVP**
