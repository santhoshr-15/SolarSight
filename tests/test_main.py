import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Patch get_detector before app.main imports it to prevent loading RT-DETR during standard unit tests
patcher = patch("app.main.get_detector")
mock_get_detector = patcher.start()
mock_detector_instance = MagicMock()
mock_get_detector.return_value = mock_detector_instance

# Setup default mock return value
mock_detector_instance.detect.return_value = {
    "success": True,
    "detections": [
        {"class_name": "Physical Damage", "confidence": 0.90, "bounding_box": {"x1":0,"y1":0,"x2":10,"y2":10}}
    ],
    "counts": {"Physical Damage": 1},
    "total_detections": 1
}

from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["model"] == "RT-DETR-L"

from PIL import Image
import io

def get_dummy_image_bytes():
    img = Image.new('RGB', (1, 1), color='red')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return buf.getvalue()

def test_detect_endpoint():
    dummy_image = get_dummy_image_bytes()
    response = client.post(
        "/detect", 
        files={"file": ("test.jpg", dummy_image, "image/jpeg")},
        data={"conf": 0.50}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_detections"] == 1
    assert data["counts"]["Physical Damage"] == 1

def test_detect_endpoint_invalid_file():
    response = client.post(
        "/detect", 
        files={"file": ("test.txt", b"hello", "text/plain")},
        data={"conf": 0.50}
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

def test_reason_general_no_image():
    response = client.post("/reason", data={"question": "What is a solar panel?", "conf": 0.50})
    assert response.status_code == 200
    res = response.json()
    assert res["intent"] == "general_question"
    assert res["guardrail_triggered"] is False

def test_reason_visual_no_image():
    response = client.post("/reason", data={"question": "Is there damage?", "conf": 0.50})
    assert response.status_code == 400
    assert "image file is required" in response.json()["detail"]

def test_reason_visual_with_image():
    dummy_image = get_dummy_image_bytes()
    response = client.post(
        "/reason", 
        data={"question": "Is there damage?", "conf": 0.50},
        files={"file": ("test.jpg", dummy_image, "image/jpeg")}
    )
    assert response.status_code == 200
    res = response.json()
    assert res["intent"] == "visual_detection_required"
    assert res["guardrail_triggered"] is False
    assert "Physical Damage" in res["answer"]

def test_cors():
    response = client.options(
        "/health",
        headers={
            "Origin": "https://solar-sight-muv.vercel.app",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://solar-sight-muv.vercel.app"
