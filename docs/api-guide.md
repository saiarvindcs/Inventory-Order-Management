# API Guide

The OpenAPI document at `/docs` is the source of truth for request and response schemas.

## Recommended demonstration order

1. Register and log in through the authentication endpoints.
2. Copy the access token into Swagger's **Authorize** dialog.
3. Create a category and product.
4. Create a warehouse and initialize inventory.
5. Create a supplier and purchase order, then receive stock.
6. Create a stock transfer and complete its lifecycle.
7. Create an order and add items.
8. Reserve inventory and confirm available quantity decreases.
9. Create a payment using an idempotency key.
10. Process a payment webhook twice and confirm duplicate safety.
11. Create and progress a shipment.
12. Create a return and refund.
13. Open reports, audit logs, notifications, health, and metrics.

## Authentication

Protected endpoints expect `Authorization: Bearer <access-token>`. Access and refresh tokens have distinct token types. Refresh processing also verifies that the referenced user still exists and is active.

## Idempotency

Payment creation and webhook flows use stable idempotency/event identifiers. Retrying the same operation must return or preserve the original result instead of creating a duplicate financial effect.

## Errors and request tracing

Application errors use controlled HTTP responses. Every request receives an `X-Request-ID`, which is returned to the caller and included in structured logs. Clients may supply a valid request ID, otherwise the API generates one.
