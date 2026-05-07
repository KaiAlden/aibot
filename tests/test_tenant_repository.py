from app.repositories.tenants import get_or_create_tenant


class FakeSession:
    def __init__(self) -> None:
        self.added = []
        self.flushed = False

    def scalar(self, statement):
        return None

    def add(self, value) -> None:
        self.added.append(value)

    def flush(self) -> None:
        self.flushed = True


def test_get_or_create_tenant_creates_when_missing() -> None:
    session = FakeSession()

    tenant = get_or_create_tenant(session, "QCT001", "青春塘")

    assert tenant.merchant_code == "QCT001"
    assert tenant.name == "青春塘"
    assert session.added == [tenant]
    assert session.flushed is True
