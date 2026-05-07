from scripts import smoke_test_import_mapping_api as smoke


class FakeResponse:
    def __init__(self, data: dict) -> None:
        self._data = data

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._data


class FakeClient:
    def __init__(self, base_url: str, timeout: int) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def __enter__(self) -> "FakeClient":
        return self

    def __exit__(self, *args) -> None:
        return None

    def post(self, path: str, **kwargs) -> FakeResponse:
        assert path == "/api/v1/auth/login"
        return FakeResponse({"access_token": "token"})

    def get(self, path: str, **kwargs) -> FakeResponse:
        assert path == "/api/v1/merchant/items/import/mapping"
        assert kwargs["headers"] == {"Authorization": "Bearer token"}
        return FakeResponse({"mapping": {"name": "Product Name"}})

    def put(self, path: str, **kwargs) -> FakeResponse:
        assert path == "/api/v1/merchant/items/import/mapping"
        assert kwargs["headers"] == {"Authorization": "Bearer token"}
        assert kwargs["json"] == {"mapping": {"name": "Product Name"}}
        return FakeResponse({"saved": True, "mapping": {"name": "Product Name"}})


def test_import_mapping_smoke_script(monkeypatch) -> None:
    monkeypatch.setattr(smoke.httpx, "Client", FakeClient)

    smoke.run_import_mapping_smoke("http://testserver", "admin", "secret")
