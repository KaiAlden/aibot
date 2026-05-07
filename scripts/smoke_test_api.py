import argparse
import sys

import httpx


def print_json(title: str, data: dict) -> None:
    print(f"\n=== {title} ===")
    print(data)


def run_api_smoke(base_url: str) -> None:
    with httpx.Client(base_url=base_url, timeout=30) as client:
        health = client.get("/api/v1/health")
        health.raise_for_status()
        print_json("health", health.json())

        chat_payload = {
            "merchant_code": "QCT001",
            "query": "我是气虚质，想喝补气茶",
            "session_id": "api_smoke_001",
        }
        chat = client.post("/api/v1/chat", json=chat_payload)
        chat.raise_for_status()
        print_json("chat", chat.json())

        symptom_payload = {
            "merchant_code": "QCT001",
            "query": "我最近怕冷，手脚冰凉，腰膝发冷，推荐点茶",
            "session_id": "api_smoke_002",
        }
        symptom_chat = client.post("/api/v1/chat", json=symptom_payload)
        symptom_chat.raise_for_status()
        print_json("symptom_chat", symptom_chat.json())

        recommendation_payload = {
            "merchant_code": "QCT001",
            "constitution": "气虚质",
            "query": "补气茶",
            "top_n": 3,
        }
        recommendation = client.post("/api/v1/recommendations", json=recommendation_payload)
        recommendation.raise_for_status()
        print_json("recommendations", recommendation.json())


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    run_api_smoke(args.base_url)


if __name__ == "__main__":
    main()
