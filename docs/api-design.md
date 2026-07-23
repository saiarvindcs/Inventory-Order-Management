# API Design

## 1. API Style

The Inventory & Order Management Platform follows REST architecture.

Design principles:

- Resource-based URLs
- Stateless requests
- JSON request and response bodies
- Standard HTTP methods
- Predictable endpoint naming
- Versioned APIs

Base URL:

```text
/api/v1
```

---

## 2. HTTP Methods

| Method | Purpose |
|---------|---------|
| GET | Read data |
| POST | Create resources |
| PUT | Full update |
| PATCH | Partial update |
| DELETE | Soft delete where applicable |

---

## 3. URL Naming Rules

Use plural resource names.

Examples:

```text
/api/v1/products
/api/v1/orders
/api/v1/payments
/api/v1/warehouses
```

Nested resources:

```text
/api/v1/orders/{order_id}/items
/api/v1/orders/{order_id}/payments
/api/v1/products/{product_id}/price-history
```

---

## 4. Authentication

Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

Public endpoints:

- Login
- Register
- Refresh Token
- Health Check

---

## 5. API Modules

The API is divided into:

- Authentication
- Users
- Roles
- Categories
- Products
- Warehouses
- Inventory
- Stock Movements
- Stock Transfers
- Suppliers
- Purchase Orders
- Orders
- Reservations
- Payments
- Shipments
- Returns
- Refunds
- Reports
- Audit Logs
- Health

---

## 6. Request Validation

All incoming requests must be validated using Pydantic.

Validation includes:

- Required fields
- Data types
- Length limits
- Enum values
- Numeric ranges
- Date validation
- Custom business validation

---

## 7. Standard Response Format

Successful response:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {}
}
```

Error response:

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Product not found"
  },
  "request_id": "generated-request-id"
}
```

---

## 8. HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Resource Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

## 9. Pagination

Example:

```text
GET /api/v1/products?page=1&page_size=20
```

Response:

```json
{
  "page": 1,
  "page_size": 20,
  "total": 250,
  "items": []
}
```

---

## 10. Filtering

Examples:

```text
GET /products?category=Electronics
GET /products?status=ACTIVE
GET /orders?status=SHIPPED
```

---

## 11. Sorting

Examples:

```text
GET /products?sort=name
GET /products?sort=-price
GET /orders?sort=-created_at
```

---

## 12. Searching

Examples:

```text
GET /products?search=keyboard
GET /suppliers?search=tech
```

---

## 13. Idempotency

Sensitive endpoints accept:

```http
Idempotency-Key: unique-key
```

Used for:

- Payments
- Refunds
- Order creation

Duplicate requests return the stored response.

---

## 14. Error Handling

Business errors include:

- Product Not Found
- Warehouse Not Found
- Insufficient Inventory
- Invalid State Transition
- Duplicate SKU
- Duplicate Payment
- Reservation Expired
- Permission Denied

---

## 15. API Versioning

Current version:

```text
/api/v1
```

Future versions:

```text
/api/v2
```

---

## 16. Health Endpoints

```text
GET /health/live
GET /health/ready
GET /metrics
```

---

## 17. Documentation

Swagger UI:

```text
/docs
```

OpenAPI JSON:

```text
/openapi.json
```

---

## 18. Security

The API enforces:

- JWT Authentication
- RBAC
- Input Validation
- Rate Limiting
- HTTPS
- CORS
- Secure Headers

---

## 19. Module Endpoint Examples

```text
POST   /auth/login
POST   /auth/register

GET    /products
POST   /products

GET    /warehouses
POST   /warehouses

GET    /inventory
PATCH  /inventory/{id}

POST   /purchase-orders
POST   /stock-transfers

POST   /orders
GET    /orders/{id}

POST   /payments

POST   /shipments

POST   /returns

GET    /reports/sales

GET    /audit-logs
```

---

## 20. API Design Summary

Architecture: REST

Data Format: JSON

Authentication: JWT

Authorization: RBAC

Validation: Pydantic

Documentation: Swagger/OpenAPI

Versioning: /api/v1

Security: HTTPS + JWT + Validation

Response Format: Standardized JSON