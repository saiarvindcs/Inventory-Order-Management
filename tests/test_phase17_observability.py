from types import SimpleNamespace

from app.core.metrics import _route_label
from app.middleware.request_context import RequestContextMiddleware


def test_metrics_uses_route_template_instead_of_raw_url() -> None:
    request = SimpleNamespace(scope={"route": SimpleNamespace(path="/products/{product_id}")})
    assert _route_label(request) == "/products/{product_id}"


def test_metrics_uses_unmatched_for_unknown_routes() -> None:
    request = SimpleNamespace(scope={})
    assert _route_label(request) == "unmatched"


def test_request_id_rejects_control_characters() -> None:
    generated = RequestContextMiddleware._request_id("bad\nrequest-id")
    assert generated != "bad\nrequest-id"
    assert len(generated) == 36
