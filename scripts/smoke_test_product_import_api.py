import argparse
import io
import json

import httpx
from openpyxl import Workbook


def build_sample_workbook() -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "茶饮"
    sheet.append(["商品名称", "适用体质", "产品形态", "价格", "成分"])
    sheet.append(["接口导入预检商品", "气虚质", "茶", 19.9, "黄芪,红枣"])
    stream = io.BytesIO()
    workbook.save(stream)
    return stream.getvalue()


def run_product_import_smoke(base_url: str, username: str, password: str) -> None:
    mapping = {
        "name": "商品名称",
        "constitutions": "适用体质",
        "form": "产品形态",
        "price": "价格",
        "ingredients": "成分",
    }
    with httpx.Client(base_url=base_url, timeout=30) as client:
        login = client.post("/api/v1/auth/login", json={"username": username, "password": password})
        login.raise_for_status()
        token = login.json()["access_token"]
        response = client.post(
            "/api/v1/merchant/items/import",
            headers={"Authorization": f"Bearer {token}"},
            data={
                "mapping_json": json.dumps(mapping, ensure_ascii=False),
                "all_sheets": "true",
                "replace": "false",
                "dry_run": "true",
            },
            files={
                "file": (
                    "sample-products.xlsx",
                    build_sample_workbook(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )
        response.raise_for_status()
        data = response.json()
        assert data["parsed_count"] == 1, data
        assert data["valid_count"] == 1, data
        assert data["issue_count"] == 0, data
        assert data["imported_count"] == 0, data
        print(
            "product import dry-run ok: "
            f"parsed={data['parsed_count']} valid={data['valid_count']} "
            f"issues={data['issue_count']} imported={data['imported_count']}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke test product import API.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--username", default="qct_admin")
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    run_product_import_smoke(args.base_url, args.username, args.password)


if __name__ == "__main__":
    main()
