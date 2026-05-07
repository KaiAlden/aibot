import httpx

from scripts.smoke_test_api import run_api_smoke


def test_run_api_smoke_uses_expected_routes(monkeypatch) -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append((request.method, request.url.path))
        if request.url.path == "/api/v1/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/api/v1/chat":
            return httpx.Response(200, json={"intent": "product", "message": "ok", "recommendations": []})
        if request.url.path == "/api/v1/recommendations":
            return httpx.Response(200, json={"items": []})
        if request.url.path == "/api/v1/merchant/items":
            return httpx.Response(200, json={"items": [], "total": 0, "page": 1, "size": 3})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    original_client = httpx.Client

    def fake_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", fake_client)

    run_api_smoke("http://testserver")

    assert ("GET", "/api/v1/health") in calls
    assert calls.count(("POST", "/api/v1/chat")) == 2
    assert ("POST", "/api/v1/recommendations") in calls
    assert ("GET", "/api/v1/merchant/items") in calls
