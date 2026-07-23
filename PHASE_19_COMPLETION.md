# Phase 19 — Optional Frontend Dashboard

Phase 19 adds a lightweight operations dashboard without introducing a separate Node/npm build pipeline.

## Delivered

- FastAPI-served dashboard at `/dashboard`
- Session-based JWT login (token is not persisted across browser restarts)
- API health indicator and manual data refresh
- KPI cards for products, orders, inventory, reserved stock, and revenue
- Recent-order and complete-order views
- Low-stock monitoring
- Inventory balance view
- Product catalogue view
- Shipment tracking view
- Links to Swagger and liveness health endpoints
- Responsive desktop/mobile layout
- HTML escaping before rendering API-provided text
- Same-origin Content Security Policy for dashboard assets and API calls
- Swagger-specific CSP so API documentation remains functional
- Phase 19 automated static/integration-contract tests

## Architecture choice

The dashboard is plain HTML, CSS, and JavaScript served by the FastAPI application. This keeps Docker, Render, and local deployment as a single application and avoids a second dependency/build system.

## Usage

1. Start the API.
2. Open `http://localhost:8000/dashboard`.
3. Sign in using a registered API user.
4. Use the sidebar to inspect orders, inventory, products, and shipments.

Phase 19 is intentionally an operations dashboard, not a customer storefront.
