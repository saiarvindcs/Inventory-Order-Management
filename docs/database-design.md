# Database Design

## 1. Database Overview

The Inventory & Order Management Platform uses PostgreSQL as the primary relational database.

The database follows Third Normal Form (3NF) to minimize redundancy while maintaining data integrity.

The design supports:

- Multi-warehouse inventory
- Inventory ledger
- Purchase orders
- Customer orders
- Payments
- Shipments
- Returns
- Audit logs
- Background processing

---

# 2. Core Entities

The system consists of the following entities:

## Security

- Users
- Roles
- Permissions
- User Roles

---

## Product Catalogue

- Categories
- Products
- Product Variants
- Price History

---

## Inventory

- Warehouses
- Inventory
- Stock Movements
- Stock Reservations
- Stock Adjustments
- Stock Transfers
- Stock Transfer Items

---

## Procurement

- Suppliers
- Purchase Orders
- Purchase Order Items
- Goods Receipts

---

## Sales

- Customers
- Customer Addresses
- Orders
- Order Items

---

## Payments

- Payments
- Payment Events
- Idempotency Keys

---

## Shipping

- Shipments
- Shipment Items

---

## Returns

- Returns
- Return Items
- Refunds

---

## System

- Audit Logs
- Notifications
- Outbox Events

---

# 3. Entity Relationships

Users
↓
UserRoles
↓
Roles
↓
Permissions

Categories
↓
Products
↓
Product Variants

Products
↓
Inventory
↓
Warehouses

Products
↓
Stock Movements

Products
↓
Purchase Order Items
↓
Purchase Orders
↓
Suppliers

Orders
↓
Order Items
↓
Products

Orders
↓
Payments
↓
Payment Events

Orders
↓
Shipments

Orders
↓
Returns
↓
Refunds

---

# 4. Primary Keys

Every table uses a surrogate primary key.

Example:

Users

id

Products

id

Orders

id

Payments

id

Returns

id

---

# 5. Foreign Keys

Examples:

Order Items

order_id → Orders

product_id → Products

Inventory

warehouse_id → Warehouses

product_id → Products

Payments

order_id → Orders

Shipment Items

shipment_id → Shipments

order_item_id → Order Items

---

# 6. Unique Constraints

Examples:

User email

Username

SKU

Warehouse code

Supplier code

Tracking number

Payment transaction ID

Idempotency key

---

# 7. Check Constraints

Examples:

Quantity >= 0

Price >= 0

Refund <= Payment

Available inventory >= 0

Reserved inventory >= 0

---

# 8. Soft Delete Strategy

The following tables will support soft deletion:

Products

Categories

Suppliers

Customers

Warehouses

Instead of deleting rows:

deleted_at timestamp

---

# 9. Timestamp Columns

Every business table should include:

created_at

updated_at

created_by (where applicable)

updated_by (where applicable)

---

# 10. Inventory Design

Inventory stores:

warehouse_id

product_id

total_quantity

reserved_quantity

available_quantity

damaged_quantity

last_updated

Business Rule:

One inventory record exists for one Product + Warehouse combination.

---

# 11. Stock Movement Ledger

Every inventory change creates a movement.

Movement Types

PURCHASE_RECEIPT

SALE

RETURN

TRANSFER_IN

TRANSFER_OUT

RESERVATION

RESERVATION_RELEASE

ADJUSTMENT

DAMAGE

Each movement stores:

Previous quantity

New quantity

Movement quantity

Reference type

Reference ID

Performed by

Timestamp

---

# 12. Order Design

Orders

Header information

Customer

Status

Totals

Taxes

Shipping

Order Items

Product

Quantity

Price

Discount

Tax

Subtotal

---

# 13. Payment Design

Payments

Order

Gateway

Amount

Currency

Status

Transaction ID

Payment Events

Webhook payload

Gateway response

Timestamp

---

# 14. Return Design

Returns

Order

Reason

Status

Approval

Return Items

Quantity

Inspection result

Refund amount

---

# 15. Audit Log Design

Audit Log stores:

Actor

Action

Entity Type

Entity ID

Old Values

New Values

Reason

Request ID

IP Address

Timestamp

---

# 16. Indexing Strategy

Indexes:

email

username

sku

warehouse_code

order_number

tracking_number

payment_transaction

supplier_code

created_at

status

Composite indexes:

(product_id, warehouse_id)

(order_id, status)

(payment_id, status)

---

# 17. Transactions

Database transactions are required for:

Order creation

Inventory reservation

Payment confirmation

Purchase order receipt

Stock transfer

Return processing

Refund processing

---

# 18. Row-Level Locking

SELECT ... FOR UPDATE will be used for:

Inventory

Reservations

Payments

Stock transfers

This prevents concurrent overselling.

---

# 19. Idempotency

The database contains:

Idempotency Keys

Each incoming payment request stores:

Key

Request hash

Response

Expiration

Duplicate requests return the stored response instead of executing again.

---

# 20. Outbox Events

Outbox stores:

ORDER_CREATED

PAYMENT_SUCCESS

SHIPMENT_DISPATCHED

RETURN_APPROVED

REFUND_COMPLETED

LOW_STOCK

Background workers process these events.

---

# 21. Database Summary

Database

PostgreSQL

Normalization

Third Normal Form (3NF)

Primary Keys

Surrogate IDs

Relationships

Foreign Keys

Deletes

Soft Delete where applicable

Concurrency

Transactions + Row Locks

Background Integration

Outbox Pattern

Integrity

Constraints + Indexes