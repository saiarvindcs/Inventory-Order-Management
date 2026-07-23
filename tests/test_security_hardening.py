from fastapi.testclient import TestClient

from app.main import app


def test_security_headers_and_request_id() -> None:
    client = TestClient(app)
    response = client.get(
        "/api/v1/health/live",
        headers={"X-Request-ID": "test-request-123"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-123"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "camera=()" in response.headers["Permissions-Policy"]
    assert response.headers["Content-Security-Policy"] == "default-src 'none'; frame-ancestors 'none'"


def test_untrusted_host_is_rejected() -> None:
    client = TestClient(app, base_url="http://malicious.example")
    response = client.get("/api/v1/health/live")

    assert response.status_code == 400
    assert response.text == "Invalid host header"
