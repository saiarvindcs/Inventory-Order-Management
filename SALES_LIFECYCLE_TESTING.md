# Complete Sales Lifecycle — Swagger Test Order

Use these endpoints in this order after starting the API and authorizing in Swagger.

1. `POST /api/v1/customers` — create a customer and copy the returned `id`.
2. `POST /api/v1/customers/{customer_id}/addresses` — create an address and copy its `id`.
3. `POST /api/v1/orders` — use the customer ID, address ID, and a valid product variant ID.
4. `POST /api/v1/payments` — amount must exactly match the order `total_amount`; copy `payment_reference`.
5. `POST /api/v1/payments/webhooks/{provider}` — send `payment.captured` with the payment reference.
6. Move the order through `confirmed`, `processing`, and `packed` using `POST /api/v1/orders/{order_id}/status`.
7. `POST /api/v1/shipments` — use an order-item ID from the order response and a valid warehouse ID.
8. Move the shipment through `packed`, `shipped`, and `delivered` using `POST /api/v1/shipments/{shipment_id}/status`.
9. `POST /api/v1/returns` — use the delivered order and its order-item ID.
10. Move the return through `approved`, `received`, and `completed` using `POST /api/v1/returns/{return_id}/status`.
11. `POST /api/v1/refunds` — use the order, payment, and return IDs.
12. `GET /api/v1/notifications?user_id={customer_id}` — lifecycle notifications should now exist.
13. `POST /api/v1/notifications/{notification_id}/read` — marks a notification as read.

## Important validation rules

- Payment amount must equal the order total.
- Shipment items must belong to the selected order and cannot exceed ordered quantities.
- Returns are accepted only after delivery.
- Refunds cannot exceed the remaining refundable order amount.
- Payment creation is idempotent through `idempotency_key`.
