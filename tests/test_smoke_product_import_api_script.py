from scripts import smoke_test_product_import_api as smoke


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
        self.seen_upload = False

    def __enter__(self) -> "FakeClient":
        return self

    def __exit__(self, *args) -> None:
        return None

    def post(self, path: str, **kwargs) -> FakeResponse:
        if path == "/api/v1/auth/login":
            return FakeResponse({"access_token": "token"})
        if path == "/api/v1/merchant/items/import":
            self.seen_upload = True
            assert kwargs["headers"] == {"Authorization": "Bearer token"}
            assert "file" in kwargs["files"]
            assert kwargs["data"]["dry_run"] == "true"
            return FakeResponse({"parsed_count": 1, "valid_count": 1, "issue_count": 0, "imported_count": 0})
        raise AssertionError(path)


def test_product_import_smoke_script(monkeypatch) -> None:
    monkeypatch.setattr(smoke.httpx, "Client", FakeClient)

    smoke.run_product_import_smoke("http://testserver", "admin", "secret")
