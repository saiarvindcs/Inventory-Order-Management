# Phase 10 — Customer Order State Machine

## Implemented

- Customer order creation with active-customer validation.
- Shipping and billing address ownership validation.
- Multiple unique product variants per order.
- Server-side price snapshots and line-total calculations.
- Subtotal, tax, shipping, discount, and final-total calculation.
- Order listing, filtering, retrieval, and pending-order editing.
- Controlled order lifecycle:
  - pending
  - confirmed
  - processing
  - packed
  - shipped
  - delivered
  - cancelled
- Invalid transition protection.
- Cancellation timestamp.
- Complete status-history records with optional actor and notes.
- Phase 8–10 regression tests.

## Deferred to fixed later phases

- Inventory reservations and concurrency: Phase 11.
- Payment processing: Phase 12.
- Shipment records, returns, and refunds: Phase 13.
