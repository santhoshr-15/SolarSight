from app.reasoning import route_intent, reason_over_detections

def test_intent_routing_visual():
    assert route_intent("Is there physical damage?") == "visual_detection_required"
    assert route_intent("How many defective panels?") == "visual_detection_required"
    assert route_intent("Are there any dusty panels?") == "visual_detection_required"
    assert route_intent("What faults are visible?") == "visual_detection_required"

def test_intent_routing_general():
    assert route_intent("Explain what a solar panel is.") == "general_question"
    assert route_intent("Who made this application?") == "general_question"

def test_general_question_reasoning():
    res = reason_over_detections("Explain what a solar panel is.", {"total_detections": 0, "detections": [], "counts": {}})
    assert res["intent"] == "general_question"
    assert res["guardrail_triggered"] is False
    assert "does not require visual inspection" in res["answer"]

def test_visual_insufficient_information_empty():
    res = reason_over_detections("Is there damage?", {"total_detections": 0, "detections": [], "counts": {}})
    assert res["intent"] == "visual_detection_required"
    assert res["guardrail_triggered"] is True
    assert "Insufficient information from the detector to answer reliably" in res["answer"]

def test_visual_insufficient_information_mismatch():
    mock_detections = {
        "total_detections": 1,
        "counts": {"Snow": 1},
        "detections": [
            {"class_name": "Snow", "confidence": 0.90, "bounding_box": {}}
        ]
    }
    # Asking for damage, but only snow is present
    res = reason_over_detections("Is there damage?", mock_detections)
    assert res["guardrail_triggered"] is True
    assert "Insufficient information" in res["answer"]

def test_visual_detection_high_confidence():
    mock_detections = {
        "total_detections": 1,
        "counts": {"Physical Damage": 1},
        "detections": [
            {"class_name": "Physical Damage", "confidence": 0.95, "bounding_box": {}}
        ]
    }
    res = reason_over_detections("Is there damage?", mock_detections)
    assert res["guardrail_triggered"] is False
    assert "Physical Damage was detected" in res["answer"]
    assert "0.95" in res["answer"]

def test_visual_detection_counting():
    mock_detections = {
        "total_detections": 2,
        "counts": {"Defective": 2},
        "detections": [
            {"class_name": "Defective", "confidence": 0.85, "bounding_box": {}},
            {"class_name": "Defective", "confidence": 0.60, "bounding_box": {}}
        ]
    }
    res = reason_over_detections("How many defective panels?", mock_detections)
    assert res["guardrail_triggered"] is False
    assert "2 Defective" in res["answer"]

def test_visual_detection_ambiguous_multiple_classes():
    mock_detections = {
        "total_detections": 2,
        "counts": {"Defective": 1, "Dusty": 1},
        "detections": [
            {"class_name": "Defective", "confidence": 0.85, "bounding_box": {}},
            {"class_name": "Dusty", "confidence": 0.80, "bounding_box": {}}
        ]
    }
    # Question about all faults
    res = reason_over_detections("What faults are visible?", mock_detections)
    assert res["guardrail_triggered"] is False
    assert "Defective and Dusty" in res["answer"] or "Dusty and Defective" in res["answer"]
