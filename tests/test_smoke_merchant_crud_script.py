import httpx

from scripts.smoke_test_merchant_crud import run_merchant_crud_smoke


def test_run_merchant_crud_smoke_uses_crud_routes(monkeypatch) -> None:
    calls = []
    product_id = 999

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append((request.method, request.url.path))
        if request.method == "POST" and request.url.path == "/api/v1/merchant/items":
            return httpx.Response(200, json={"item": {"id": product_id, "name": "API临时测试商品"}})
        if request.method == "GET" and request.url.path == f"/api/v1/merchant/items/{product_id}":
            if calls.count(("GET", f"/api/v1/merchant/items/{product_id}")) >= 2:
                return httpx.Response(404, json={"detail": "product not found"})
            return httpx.Response(200, json={"id": product_id, "name": "API临时测试商品"})
        if request.method == "PUT" and request.url.path == f"/api/v1/merchant/items/{product_id}":
            return httpx.Response(200, json={"item": {"id": product_id, "price": 12.5, "description": "已通过API更新"}})
        if request.method == "DELETE" and request.url.path == f"/api/v1/merchant/items/{product_id}":
            return httpx.Response(200, json={"deleted": True})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    original_client = httpx.Client

    def fake_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", fake_client)

    run_merchant_crud_smoke("http://testserver")

    assert ("POST", "/api/v1/merchant/items") in calls
    assert ("PUT", f"/api/v1/merchant/items/{product_id}") in calls
    assert ("DELETE", f"/api/v1/merchant/items/{product_id}") in calls
