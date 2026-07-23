# System Workflows

## 1. Purchase Order Workflow

```text
DRAFT
→ APPROVED
→ SENT
→ PARTIALLY_RECEIVED
→ RECEIVED
→ CLOSED

CANCELLED

## 2. Stock Transfer Workflow

REQUESTED
→ APPROVED
→ DISPATCHED
→ IN_TRANSIT
→ RECEIVED
→ COMPLETED

Alternative states:

REJECTED
CANCELLED
PARTIALLY_RECEIVED

3. Customer Order Workflow
DRAFT
→ PENDING_PAYMENT
→ PAID
→ PROCESSING
→ PACKED
→ SHIPPED
→ DELIVERED

Alternative states:

PAYMENT_FAILED
CANCELLED
RETURN_REQUESTED
PARTIALLY_RETURNED
RETURNED
REFUNDED

4. Stock Reservation Workflow
Customer creates order
        ↓
Inventory row is locked
        ↓
Available inventory is validated
        ↓
Stock is reserved for 15 minutes
        ↓
Payment succeeds or reservation expires

Payment success:

Reserved stock
→ Confirmed sale
→ Inventory deducted
→ Stock movement created

Payment failure or expiry:

Reserved stock
→ Reservation released
→ Inventory becomes available

5. Payment Workflow
INITIATED
→ PENDING
→ SUCCESS

Alternative states:

FAILED
CANCELLED
PARTIALLY_REFUNDED
REFUNDED

Shipment Workflow
CREATED
→ PACKED
→ DISPATCHED
→ IN_TRANSIT
→ DELIVERED

Alternative states:

DELIVERY_FAILED
RETURNED_TO_SENDER
CANCELLED

7. Return Workflow
REQUESTED
→ APPROVED
→ RECEIVED
→ INSPECTED
→ RESTOCKED or DAMAGED
→ REFUNDED