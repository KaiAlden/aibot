import argparse

import httpx


def run_import_mapping_smoke(base_url: str, username: str, password: str) -> None:
    with httpx.Client(base_url=base_url, timeout=30) as client:
        login = client.post("/api/v1/auth/login", json={"username": username, "password": password})
        login.raise_for_status()
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        current = client.get("/api/v1/merchant/items/import/mapping", headers=headers)
        current.raise_for_status()
        mapping = current.json()["mapping"]

        saved = client.put("/api/v1/merchant/items/import/mapping", headers=headers, json={"mapping": mapping})
        saved.raise_for_status()
        data = saved.json()
        assert data["saved"] is True, data
        assert data["mapping"]["name"], data
        print(f"import mapping smoke ok: fields={len(data['mapping'])}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke test product import mapping API.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--username", default="qct_admin")
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    run_import_mapping_smoke(args.base_url, args.username, args.password)


if __name__ == "__main__":
    main()
