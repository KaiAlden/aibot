import argparse
import sys
import time

import httpx


def run_merchant_crud_smoke(base_url: str, merchant_code: str = "QCT001") -> None:
    headers = {"X-Merchant-Code": merchant_code}
    unique_suffix = int(time.time())
    payload = {
        "name": f"API临时测试商品-{unique_suffix}",
        "category": "API测试",
        "form": "茶饮",
        "description": "用于验证商家商品CRUD接口",
        "price": 9.9,
        "weight": "1袋",
        "image_url": "https://example.com/test.jpg",
        "is_universal": False,
        "constitutions": ["气虚质"],
        "ingredients": ["黄芪"],
    }

    with httpx.Client(base_url=base_url, timeout=30, headers=headers) as client:
        created = client.post("/api/v1/merchant/items", json=payload)
        created.raise_for_status()
        created_item = created.json()["item"]
        product_id = created_item["id"]
        print(f"created: {product_id} {created_item['name']}")

        detail = client.get(f"/api/v1/merchant/items/{product_id}")
        detail.raise_for_status()
        print(f"detail: {detail.json()['name']}")

        update_payload = {"price": 12.5, "description": "已通过API更新"}
        updated = client.put(f"/api/v1/merchant/items/{product_id}", json=update_payload)
        updated.raise_for_status()
        updated_item = updated.json()["item"]
        print(f"updated: price={updated_item['price']} description={updated_item['description']}")

        deleted = client.delete(f"/api/v1/merchant/items/{product_id}")
        deleted.raise_for_status()
        print(f"deleted: {deleted.json()['deleted']}")

        after_delete = client.get(f"/api/v1/merchant/items/{product_id}")
        if after_delete.status_code != 404:
            raise AssertionError(f"expected 404 after delete, got {after_delete.status_code}")
        print("after_delete: 404")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--merchant-code", default="QCT001")
    args = parser.parse_args()
    run_merchant_crud_smoke(args.base_url, merchant_code=args.merchant_code)


if __name__ == "__main__":
    main()
