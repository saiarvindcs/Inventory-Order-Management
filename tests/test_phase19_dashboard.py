from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_assets_are_present_and_externalized() -> None:
    html = (ROOT / "app/static/dashboard/index.html").read_text()
    css = ROOT / "app/static/dashboard/dashboard.css"
    javascript = ROOT / "app/static/dashboard/dashboard.js"

    assert css.is_file()
    assert javascript.is_file()
    assert 'href="/static/dashboard/dashboard.css"' in html
    assert 'src="/static/dashboard/dashboard.js"' in html
    assert "<script>" not in html
    assert "<style>" not in html


def test_dashboard_uses_real_api_endpoints_and_session_storage() -> None:
    javascript = (ROOT / "app/static/dashboard/dashboard.js").read_text()

    required_paths = [
        "/auth/login",
        "/auth/me",
        "/reports/dashboard",
        "/reports/low-stock?threshold=10",
        "/orders?limit=100&sort_order=desc",
        "/inventory?limit=100",
        "/products?limit=100",
        "/shipments",
    ]
    for path in required_paths:
        assert path in javascript

    assert "sessionStorage" in javascript
    assert "localStorage" not in javascript
    assert "Authorization" in javascript


def test_fastapi_serves_dashboard_and_static_assets() -> None:
    main = (ROOT / "app/main.py").read_text()

    assert 'app.mount("/static"' in main
    assert '@app.get("/dashboard"' in main
    assert 'FileResponse("app/static/dashboard/index.html")' in main


def test_dashboard_content_security_policy_allows_only_same_origin_assets() -> None:
    middleware = (ROOT / "app/middleware/request_context.py").read_text()

    assert 'request.url.path.startswith(("/dashboard", "/static/dashboard"))' in middleware
    assert "script-src 'self'" in middleware
    assert "connect-src 'self'" in middleware
    assert "frame-ancestors 'none'" in middleware
