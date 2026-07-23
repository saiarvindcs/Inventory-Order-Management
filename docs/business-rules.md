# Business Rules

## 1. Product Rules

1. Every product must have a unique SKU.
2. Product prices cannot be negative.
3. Inactive products cannot be ordered.
4. Products with order history cannot be permanently deleted.
5. Product deletion must use soft deletion.
6. Product price changes must be stored in price history.
7. Inventory must not be stored directly in the product table.

---

## 2. Warehouse Rules

1. Every warehouse must have a unique code.
2. A product can exist in multiple warehouses.
3. A warehouse can contain multiple products.
4. Inactive warehouses cannot receive new stock.
5. Warehouses containing inventory cannot be permanently deleted.
6. A stock transfer cannot use the same source and destination warehouse.

---

## 3. Inventory Rules

1. Available inventory cannot become negative.
2. Reserved quantity cannot exceed sellable quantity.
3. Damaged inventory cannot be sold.
4. Every inventory change must create a stock movement.
5. Inventory quantities cannot be edited directly.
6. Inventory updates must use database transactions.
7. Concurrent orders must not cause overselling.
8. Each product and warehouse pair must be unique.
9. Manual adjustments require a reason.
10. High-value adjustments may require manager approval.

---

## 4. Stock Movement Rules

1. Stock movements are immutable.
2. Incorrect movements must be corrected using compensating movements.
3. Every movement must contain a reference.
4. Every movement must record the user responsible.
5. Every movement must record before and after quantities.

Movement types include:

- PURCHASE_RECEIPT
- ORDER_RESERVATION
- RESERVATION_RELEASE
- SALE
- TRANSFER_OUT
- TRANSFER_IN
- CUSTOMER_RETURN
- DAMAGE
- MANUAL_ADJUSTMENT

---

## 5. Purchase Order Rules

1. Draft purchase orders can be edited.
2. Only authorised users can approve purchase orders.
3. Approved purchase orders cannot be freely modified.
4. Received quantity cannot exceed ordered quantity.
5. Partial deliveries are allowed.
6. Damaged received goods must be recorded separately.
7. Accepted goods increase warehouse inventory.
8. Cancelled purchase orders cannot receive stock.
9. Every receipt must create stock movements.
10. The creator should not approve the same purchase order in strict workflows.

---

## 6. Stock Transfer Rules

1. The source warehouse must have enough available inventory.
2. Source and destination warehouses must be different.
3. Transfer stock must be reserved before dispatch.
4. Dispatch reduces source inventory.
5. Receipt increases destination inventory.
6. Partial receipt is allowed.
7. Damaged or missing units must be recorded.
8. Completed transfers cannot be edited.
9. Every transition must be stored in transfer history.
10. Stock transfers must use database transactions.

---

## 7. Order Rules

1. Only active products can be ordered.
2. Prices must be calculated by the backend.
3. Frontend-submitted totals must not be trusted.
4. Inventory must be validated before reservation.
5. Creating an order must reserve stock.
6. Payment success confirms the reservation.
7. Payment failure or expiry releases the reservation.
8. Paid orders cannot be deleted.
9. Invalid order-status transitions must be rejected.
10. Every status change must be recorded.
11. Duplicate requests must not create duplicate orders.
12. Orders may be fulfilled from multiple warehouses.

---

## 8. Reservation Rules

1. Default reservation duration is 15 minutes.
2. Reserved stock cannot be sold to another customer.
3. Payment success converts reserved stock into sold stock.
4. Payment failure releases the reservation.
5. Celery must release expired reservations.
6. Reservation processing must be idempotent.
7. Repeated release tasks must not increase inventory twice.
8. Inventory rows must be locked during reservation creation.

---

## 9. Payment Rules

1. One order can have multiple payment attempts.
2. Only one successful payment can confirm an order.
3. Duplicate payment webhooks must not process twice.
4. Every payment event must have a unique event ID.
5. Failed payments cannot deduct inventory.
6. Refund amount cannot exceed the paid amount.
7. Partial refunds are allowed.
8. Payment events must remain stored.
9. Webhook signatures must be validated.
10. Payment processing must be idempotent.

---

## 10. Shipment Rules

1. Unpaid orders cannot be shipped.
2. A shipment must contain at least one order item.
3. Partial shipments are allowed.
4. One order can contain multiple shipments.
5. Every shipment requires a unique tracking number.
6. Shipped quantity cannot exceed ordered quantity.
7. Shipment status changes must be recorded.
8. Delivered items become eligible for returns.

---

## 11. Return and Refund Rules

1. Only delivered items can be returned.
2. The default return window is seven days.
3. Return quantity cannot exceed delivered quantity.
4. Partial returns are allowed.
5. Returned items must be inspected.
6. Sellable items return to available inventory.
7. Damaged items enter damaged inventory.
8. Refunds require approval.
9. Duplicate refund requests must not create multiple refunds.
10. Return and refund history must be retained.

---

## 12. Audit Rules

1. Audit logs cannot be modified by ordinary users.
2. Sensitive actions must create an audit record.
3. Every audit record must contain the actor and timestamp.
4. Old and new values must be captured where applicable.
5. Audit logs must include request IDs.
6. Audit logs must include the source IP address where available.