# 📦 Inventory & Order Management Platform

A production-ready backend Inventory & Order Management Platform built using **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Alembic**, **JWT Authentication**, **Redis**, **Celery**, and **Docker**.

The project provides a scalable REST API for managing products, warehouses, inventory, suppliers, purchase orders, stock transfers, customer orders, authentication, reporting, and audit logging.

---

# 🚀 Features

## Authentication & Authorization

- JWT Authentication
- Refresh Tokens
- Role-Based Access Control (RBAC)
- Password Hashing
- Protected APIs
- User Management

---

## Product Management

- Product CRUD
- Category Management
- SKU Support
- Product Status
- Search & Filtering

---

## Warehouse Management

- Warehouse CRUD
- Multi-Warehouse Support
- Warehouse Status

---

## Inventory Management

- Inventory Tracking
- Inventory Ledger
- Stock In
- Stock Out
- Inventory Adjustments
- Inventory Reports
- Available Stock Calculation

---

## Suppliers

- Supplier CRUD
- Supplier Status
- Contact Information

---

## Purchase Orders

- Purchase Order Creation
- Purchase Status Tracking
- Receiving Inventory
- Supplier Integration

---

## Stock Transfers

- Warehouse-to-Warehouse Transfers
- Transfer Status
- Inventory Synchronization

---

## Customer Orders

- Customer Management
- Order Creation
- Order Status Workflow
- Order Validation

---

## Reports

- Inventory Reports
- Warehouse Reports
- Product Reports

---

## Developer Features

- OpenAPI / Swagger Documentation
- Alembic Database Migrations
- Docker Support
- Redis Integration
- Celery Background Tasks
- GitHub Actions CI
- Environment-based Configuration

---

# 🛠 Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic

### Database

- PostgreSQL

### Authentication

- JWT
- Passlib

### Caching

- Redis

### Background Processing

- Celery

### DevOps

- Docker
- GitHub Actions

### Testing

- Pytest

---

# 📂 Project Structure

```
app/
│
├── api/
├── core/
├── db/
├── models/
├── repositories/
├── schemas/
├── services/
├── utils/
└── main.py

alembic/
docs/
tests/
scripts/
```

---

# 🔐 Security

- JWT Authentication
- Password Hashing
- Role-Based Authorization
- Request Validation
- Environment Variables

---

# 📖 API Documentation

Swagger UI

```
/docs
```

ReDoc

```
/redoc
```

---

# ⚙ Installation

```bash
git clone https://github.com/saiarvindcs/Inventory-Order-Management.git

cd Inventory-Order-Management

python -m venv .venv

source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create environment variables

```bash
cp .env.example .env
```

Run migrations

```bash
alembic upgrade head
```

Start server

```bash
uvicorn app.main:app --reload
```

---

# 🧪 Testing

```bash
pytest
```

---

# 🐳 Docker

```bash
docker compose up --build
```

---

# 📈 Roadmap

- Authentication
- RBAC
- Product Catalogue
- Inventory Ledger
- Warehouses
- Suppliers
- Purchase Orders
- Stock Transfers
- Customer Orders
- Payments
- Reporting
- Audit Logs
- Docker
- CI/CD

---

# 👨‍💻 Author

**Sai Aravind**

Backend Developer

GitHub:
https://github.com/saiarvindcs
