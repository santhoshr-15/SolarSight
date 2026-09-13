import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("Testing GET /health")
    res = client.get("/health")
    print(res.json())

    print("\nTesting POST /detect")
    with open("test/sample_images/real_world_solar_test.png", "rb") as f:
        res = client.post("/detect", files={"file": ("real_world_solar_test.png", f, "image/png")})
    print(f"Status: {res.status_code}")
    print(f"Total Detections: {res.json().get('total_detections')}")

    print("\nTesting POST /reason (visual)")
    with open("test/sample_images/real_world_solar_test.png", "rb") as f:
        res = client.post("/reason", data={"question": "How many Physical Damage detections are present?"}, files={"file": ("real_world_solar_test.png", f, "image/png")})
    print(f"Intent: {res.json().get('intent')}")
    print(f"Guardrail: {res.json().get('guardrail_triggered')}")
    print(f"Answer: {res.json().get('answer')}")

    print("\nTesting POST /reason (general bypass)")
    res = client.post("/reason", data={"question": "What is a solar panel?"})
    print(f"Intent: {res.json().get('intent')}")
    print(f"Guardrail: {res.json().get('guardrail_triggered')}")
    print(f"Answer: {res.json().get('answer')}")

    print("\nTesting POST /reason (guardrail)")
    with open("test/sample_images/real_world_solar_test.png", "rb") as f:
        # Ask for damage with a high confidence threshold
        res = client.post("/reason", data={"question": "Is there damage?", "conf": 0.99}, files={"file": ("real_world_solar_test.png", f, "image/png")})
    print(f"Intent: {res.json().get('intent')}")
    print(f"Guardrail: {res.json().get('guardrail_triggered')}")

if __name__ == "__main__":
    run_tests()
