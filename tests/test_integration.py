import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.mark.integration
def test_real_model_inference():
    """
    Integration test that actually loads best.pt and runs inference.
    Run this manually using: pytest -m integration -v
    """
    # Unpatch the detector if it was patched globally (our patch was in test_main module, so it shouldn't affect here)
    client = TestClient(app)
    
    try:
        with open("test/sample_images/real_world_solar_test.png", "rb") as f:
            image_data = f.read()
    except FileNotFoundError:
        pytest.skip("Sample image not found for integration test")
        
    # POST /detect
    response = client.post(
        "/detect", 
        files={"file": ("test.png", image_data, "image/png")},
        data={"conf": 0.50}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Verify the real-world test result we know is there
    assert data["total_detections"] >= 1
