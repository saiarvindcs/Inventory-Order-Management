# System Architecture

## 1. Architecture Overview

The Inventory & Order Management Platform follows a modular monolith architecture.

A modular monolith keeps all business modules inside one deployable backend application while maintaining clear separation between domains.

This approach is suitable for this project because it provides:

- Strong module separation
- Easier development and testing
- Simpler deployment than microservices
- Shared database transactions
- Clear business boundaries
- Future migration to microservices if needed

The initial system will not use microservices because they would add unnecessary operational complexity.

---

## 2. High-Level Architecture

```text
Users
  |
  v
Frontend Dashboard
  |
  v
FastAPI Backend
  |
  +------------------------+
  |                        |
  v                        v
PostgreSQL              Redis
  |                        |
  |                        +------------------+
  |                                           |
  v                                           v
Business Data                             Celery Workers
                                              |
                                              v
                                   Background and Scheduled Tasks


3. Main Components

The system contains the following main components:

1.Frontend Dashboard
2.FastAPI Backend
3.PostgreSQL Database
4.Redis
5.Celery Workers
6.Celery Beat
7.Flower Monitoring
8.External Payment Gateway
9.Logging and Monitoring Services
10.CI/CD Pipeline

4. Frontend Architecture

The frontend dashboard will communicate with the FastAPI backend using REST APIs.

The frontend will support:

User login
Dashboard metrics
Product management
Warehouse management
Inventory viewing
Stock transfers
Supplier management
Purchase orders
Customer orders
Payments
Shipments
Returns
Reports
Audit logs
System health

The frontend will never directly access PostgreSQL or Redis.

Frontend
   |
   | HTTPS REST API
   v
FastAPI Backend

5. Backend Architecture

The FastAPI backend will follow a layered structure.

API Layer
   |
   v
Service Layer
   |
   v
Repository Layer
   |
   v
Database Layer

Each layer has a separate responsibility.

6. API Layer

The API layer contains FastAPI routers and endpoints.

Responsibilities:

Receive HTTP requests
Validate request data
Read authentication tokens
Check user permissions
Call service-layer functions
Return HTTP responses
Convert business exceptions into API errors

The API layer must not contain complex business logic.

Example:

POST /api/v1/orders

The endpoint will:

Validate the request body
Identify the authenticated customer
Call the order service
Return the created order

7. Service Layer

The service layer contains business logic.

Responsibilities:

Enforce business rules
Coordinate repositories
Manage database transactions
Validate state transitions
Handle inventory reservations
Process payments
Create stock movements
Trigger background tasks
Generate audit logs

Example services:

AuthenticationService
ProductService
InventoryService
PurchaseOrderService
StockTransferService
OrderService
ReservationService
PaymentService
ShipmentService
ReturnService
RefundService
ReportService
AuditService

The service layer is the core of the application.
8. Repository Layer

The repository layer handles database operations.

Responsibilities:

Create records
Read records
Update records
Soft-delete records
Apply filters
Apply pagination
Execute row-level locks
Run database queries

Example repositories:

UserRepository
ProductRepository
WarehouseRepository
InventoryRepository
OrderRepository
PaymentRepository
ShipmentRepository
ReturnRepository

The repository layer must not contain high-level business decisions.

9. Database Layer

PostgreSQL will be the primary database.

It will store:

Users and roles
Products and categories
Warehouses
Inventory balances
Stock movements
Suppliers
Purchase orders
Stock transfers
Customer orders
Reservations
Payments
Shipments
Returns
Refunds
Reports metadata
Audit logs
Idempotency keys
Outbox events

PostgreSQL is selected because it supports:

ACID transactions
Row-level locking
Constraints
Indexing
JSON data
Reliable concurrent operations
Advanced query features

10. Redis Architecture

Redis will support temporary and high-speed operations.

Redis use cases:

Caching
Rate limiting
Celery message broker
Celery result backend
Temporary reservation metadata
Distributed locks where necessary
Session or token-related temporary data
Frequently accessed report data

Redis must not be the primary source of truth for inventory.

PostgreSQL remains the authoritative database.

11. Celery Architecture

Celery will process asynchronous tasks.

FastAPI
   |
   | Sends task
   v
Redis Queue
   |
   v
Celery Worker
   |
   v
Task Execution

Celery tasks include:

Send order confirmation
Send payment confirmation
Send shipment notifications
Release expired reservations
Generate reports
Process bulk imports
Send low-stock alerts
Retry failed notifications
Reconcile pending payments
Generate invoices

12. Celery Beat Architecture

Celery Beat schedules recurring tasks.

Example schedules:

Every 5 minutes:
Release expired stock reservations

Every hour:
Reconcile pending payments

Every morning:
Generate low-stock alerts

Every night:
Generate daily sales summary

Celery Beat sends scheduled tasks to Redis.

Celery Workers consume and execute them.

13. Flower Monitoring

Flower will provide a monitoring dashboard for Celery.

It will display:

Active workers
Queued tasks
Successful tasks
Failed tasks
Retried tasks
Task execution time
Worker status

Flower is mainly for administrators and developers.

It should not be publicly exposed without authentication.

14. Authentication Flow
User enters credentials
        |
        v
Frontend sends login request
        |
        v
FastAPI validates credentials
        |
        v
Password hash is verified
        |
        v
Access token and refresh token created
        |
        v
Frontend stores tokens securely
        |
        v
Access token sent with protected requests

Protected request flow:

Request with JWT
        |
        v
Token validation
        |
        v
User identity loaded
        |
        v
Role and permission checked
        |
        v
Endpoint access granted or denied

15. Order Creation Flow
Customer submits order
        |
        v
API validates request
        |
        v
Order service starts transaction
        |
        v
Inventory rows are locked
        |
        v
Available stock is checked
        |
        v
Stock reservation is created
        |
        v
Order and order items are created
        |
        v
Stock movement records are created
        |
        v
Transaction commits
        |
        v
Payment initiation begins

If any step fails:

Transaction rolls back

No partial order or incorrect inventory state should remain.

16. Concurrency Control Flow

To prevent overselling:

Order request
        |
        v
Database transaction begins
        |
        v
Inventory row selected FOR UPDATE
        |
        v
Available quantity checked
        |
        v
Reservation created
        |
        v
Inventory updated
        |
        v
Transaction committed

Concurrent requests must wait for the locked inventory row.

This ensures that only valid reservations succeed.

17. Payment Webhook Flow
Payment gateway sends webhook
        |
        v
Webhook signature validated
        |
        v
Event ID checked
        |
        v
Duplicate event rejected safely
        |
        v
Payment record updated
        |
        v
Order state updated
        |
        v
Inventory reservation confirmed or released
        |
        v
Audit log created

The event ID and idempotency key prevent duplicate processing.

18. Stock Transfer Flow
Transfer requested
        |
        v
Manager approval
        |
        v
Source stock reserved
        |
        v
Transfer dispatched
        |
        v
Source inventory reduced
        |
        v
Goods marked in transit
        |
        v
Destination receives goods
        |
        v
Destination inventory increased
        |
        v
Transfer completed

Every inventory change creates stock movement records.

19. Purchase Order Flow
Purchase order created
        |
        v
Purchase order approved
        |
        v
Purchase order sent to supplier
        |
        v
Goods received
        |
        v
Accepted and damaged quantities recorded
        |
        v
Inventory increased
        |
        v
Goods receipt created
        |
        v
Purchase order completed

20. Return and Refund Flow
Customer requests return
        |
        v
Return eligibility checked
        |
        v
Return approved
        |
        v
Item received
        |
        v
Item inspected
        |
        +--------------------+
        |                    |
        v                    v
Sellable                Damaged
        |                    |
        v                    v
Available inventory     Damaged inventory
        |
        v
Refund processed
21. Audit Logging Architecture

Sensitive business actions will create audit logs.

Audit logging can be triggered in the service layer after successful operations.

Examples:

Role updated
Inventory adjusted
Purchase order approved
Transfer approved
Order cancelled
Refund created
Product price changed

Audit logs will store:

Actor
Action
Entity type
Entity ID
Old values
New values
Reason
Request ID
IP address
Timestamp
22. Error Handling Architecture

The application will use centralised exception handling.

Error categories:

ValidationError
AuthenticationError
AuthorizationError
NotFoundError
ConflictError
BusinessRuleError
InsufficientInventoryError
InvalidStateTransitionError
IdempotencyConflictError
ExternalServiceError

Standard error response:

{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_INVENTORY",
    "message": "Requested quantity is not available",
    "details": {}
  },
  "request_id": "generated-request-id"
}

23. API Versioning

All main endpoints will use:

/api/v1

Examples:

/api/v1/auth/login
/api/v1/products
/api/v1/warehouses
/api/v1/inventory
/api/v1/orders
/api/v1/payments

Future breaking changes can use:

/api/v2
24. Modular Domain Structure

The backend will be separated into modules:

auth
users
roles
products
categories
warehouses
inventory
stock_movements
suppliers
purchase_orders
stock_transfers
orders
reservations
payments
shipments
returns
refunds
reports
audit_logs
health

Each module may contain:

models.py
schemas.py
repository.py
service.py
router.py
constants.py
exceptions.py

Shared logic will remain in a common core package.

25. Outbox Pattern

The project will use a transactional outbox pattern for important background events.

Example:

Order created
        |
        v
Order and outbox event saved in same transaction
        |
        v
Background dispatcher reads outbox event
        |
        v
Celery task is triggered
        |
        v
Order confirmation sent

This prevents important events from being lost if the database transaction succeeds but task submission fails.

Outbox events may include:

ORDER_CREATED
PAYMENT_SUCCESSFUL
SHIPMENT_DISPATCHED
RETURN_APPROVED
REFUND_COMPLETED
LOW_STOCK_DETECTED

26. Observability Architecture

The system will include:

Structured application logs
Request IDs
Error tracking
Health checks
Readiness checks
Performance metrics
Celery monitoring
Database query monitoring

Health endpoints:

GET /health/live
GET /health/ready
GET /metrics
27. Local Development Architecture

Docker Compose will run:

Frontend
FastAPI Backend
PostgreSQL
Redis
Celery Worker
Celery Beat
Flower

Local flow:

Browser
   |
   v
Frontend
   |
   v
FastAPI
   |
   +--------> PostgreSQL
   |
   +--------> Redis
                  |
                  +--------> Celery Worker
                  |
                  +--------> Celery Beat

28. Cloud Deployment Architecture
Internet
   |
   v
Frontend Hosting
   |
   v
Backend API
   |
   +-------------------+
   |                   |
   v                   v
Managed PostgreSQL   Managed Redis
                         |
                         v
                    Celery Workers

Cloud components:

Public frontend
Public HTTPS API
Managed PostgreSQL
Managed Redis
Celery Worker service
Celery Beat service
Protected Flower dashboard
CI/CD pipeline
Environment secret management


29. Security Boundaries

The architecture must ensure:

Frontend cannot access the database directly.
Redis is not publicly exposed.
PostgreSQL is not publicly exposed unless strictly required.
Flower is protected.
Secrets are stored in environment variables or a secret manager.
All public traffic uses HTTPS.
JWT permissions are checked on protected endpoints.
Webhook signatures are validated.
Internal errors are not exposed to users.
Sensitive logs are masked.

30. Architecture Decision Summary

The project will use:

Architecture:
Modular Monolith

Backend:
FastAPI

Database:
PostgreSQL

ORM:
SQLAlchemy

Migrations:
Alembic

Cache and Queue:
Redis

Background Processing:
Celery

Scheduled Tasks:
Celery Beat

Worker Monitoring:
Flower

Authentication:
JWT with refresh tokens

Authorization:
Role-Based Access Control

API Style:
REST

Deployment:
Docker and cloud services

This architecture provides enough complexity for an advanced portfolio project while remaining practical to build, test and deploy.