"""
Comprehensive deterministic test suite for the SolarSight reasoning engine v2.0.

All tests use mocked detector outputs — no real model required.
Covers: counting, existence, confidence, location, comparison, summary,
fault analysis, condition, general knowledge, unsupported questions,
guardrails, synonyms, overlaps, edge cases, and multi-class questions.
"""
import pytest
from app.reasoning import (
    route_intent,
    reason_over_detections,
    resolve_classes,
    get_confidence_tier,
    format_confidence_language,
    get_spatial_location,
    detect_overlaps,
    _compute_iou,
)


# ===========================================================================
# REUSABLE MOCK FIXTURES
# ===========================================================================

def _make_det(class_name, confidence, x1=0, y1=0, x2=100, y2=100):
    """Helper to build a detection dict."""
    return {
        "class_name": class_name,
        "confidence": confidence,
        "bounding_box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
    }


def _make_data(*dets, img_w=640, img_h=480):
    """Helper to build a detections_data dict."""
    det_list = list(dets)
    counts = {}
    for d in det_list:
        c = d["class_name"]
        counts[c] = counts.get(c, 0) + 1
    return {
        "success": True,
        "detections": det_list,
        "counts": counts,
        "total_detections": len(det_list),
        "image_width": img_w,
        "image_height": img_h,
    }


EMPTY_DATA = _make_data()

RICH_DATA = _make_data(
    _make_det("Physical Damage", 0.82, 300, 200, 400, 300),
    _make_det("Defective", 0.67, 10, 10, 100, 100),
    _make_det("Defective", 0.71, 50, 50, 150, 150),
    _make_det("Dusty", 0.54, 500, 400, 600, 450),
    _make_det("Snow", 0.90, 0, 0, 50, 50),
    _make_det("Bird Drop", 0.45, 200, 100, 250, 150),
)


# ===========================================================================
# 1-7: COUNT QUERIES
# ===========================================================================

class TestCountQueries:

    def test_01_count_physical_damage(self):
        res = reason_over_detections("How many Physical Damage detections?", RICH_DATA)
        assert res["intent"] == "COUNT_QUERY"
        assert res["guardrail_triggered"] is False
        assert "1 Physical Damage" in res["answer"]
        assert res["evidence"]["count"] == 1

    def test_02_count_defective(self):
        res = reason_over_detections("How many defective panels?", RICH_DATA)
        assert res["intent"] == "COUNT_QUERY"
        assert "2 Defective" in res["answer"]
        assert res["evidence"]["count"] == 2

    def test_03_count_dusty(self):
        res = reason_over_detections("How many dusty regions?", RICH_DATA)
        assert res["intent"] == "COUNT_QUERY"
        assert "1 Dusty" in res["answer"]

    def test_04_count_snow(self):
        res = reason_over_detections("How many snowy regions?", RICH_DATA)
        assert res["intent"] == "COUNT_QUERY"
        assert "1 Snow" in res["answer"]

    def test_05_count_bird_drop(self):
        res = reason_over_detections("How many bird droppings?", RICH_DATA)
        assert res["intent"] == "COUNT_QUERY"
        assert "1 Bird Drop" in res["answer"]

    def test_06_count_non_defective(self):
        data = _make_data(
            _make_det("Non Defective", 0.88),
            _make_det("Non Defective", 0.91),
        )
        res = reason_over_detections("How many non defective panels?", data)
        assert res["intent"] == "COUNT_QUERY"
        assert "2 Non Defective" in res["answer"]

    def test_07_total_detections(self):
        res = reason_over_detections("How many total detections?", RICH_DATA)
        assert res["intent"] == "COUNT_QUERY"
        assert "6 total" in res["answer"]
        assert res["evidence"]["count"] == 6


# ===========================================================================
# 8-9: CONFIDENCE QUERIES
# ===========================================================================

class TestConfidenceQueries:

    def test_08_highest_confidence(self):
        res = reason_over_detections("Which detection has the highest confidence?", RICH_DATA)
        assert res["intent"] == "CONFIDENCE_QUERY"
        assert "Snow" in res["answer"]
        assert "90%" in res["answer"]

    def test_09_lowest_confidence(self):
        res = reason_over_detections("Which detection has the lowest confidence?", RICH_DATA)
        assert res["intent"] == "CONFIDENCE_QUERY"
        assert "Bird Drop" in res["answer"]
        assert "45%" in res["answer"]


# ===========================================================================
# 10-11: COMPARISON QUERIES
# ===========================================================================

class TestComparisonQueries:

    def test_10_most_frequent_class(self):
        res = reason_over_detections("Which class appears most frequently?", RICH_DATA)
        assert res["intent"] == "COMPARISON_QUERY"
        assert "Defective" in res["answer"]
        assert "2" in res["answer"]

    def test_11_comparison_two_classes(self):
        res = reason_over_detections(
            "Are there more defective detections than dusty detections?", RICH_DATA
        )
        assert res["intent"] == "COMPARISON_QUERY"
        assert "Defective" in res["answer"]
        assert "Dusty" in res["answer"]

    def test_11b_tied_comparison(self):
        data = _make_data(
            _make_det("Defective", 0.80),
            _make_det("Dusty", 0.75),
        )
        res = reason_over_detections("Which class appears most frequently?", data)
        assert "tied" in res["answer"]


# ===========================================================================
# 12-15: CLASS EXISTENCE QUERIES
# ===========================================================================

class TestClassExistenceQueries:

    def test_12_physical_damage_existence(self):
        res = reason_over_detections("Is there any physical damage?", RICH_DATA)
        assert res["intent"] == "CLASS_QUERY"
        assert res["guardrail_triggered"] is False
        assert "Physical Damage" in res["answer"]

    def test_13_dust_existence(self):
        res = reason_over_detections("Is dust detected?", RICH_DATA)
        assert res["intent"] == "CLASS_QUERY"
        assert "Dusty" in res["answer"]

    def test_14_snow_existence(self):
        res = reason_over_detections("Is snow present?", RICH_DATA)
        assert res["intent"] == "CLASS_QUERY"
        assert "Snow" in res["answer"]

    def test_15_bird_drop_existence(self):
        res = reason_over_detections("Are there any bird drops?", RICH_DATA)
        assert res["intent"] == "CLASS_QUERY"
        # Bird Drop has 0.45 confidence — LOW tier → guardrail
        assert res["guardrail_triggered"] is True
        assert "low-confidence" in res["answer"]

    def test_15b_existence_not_present(self):
        data = _make_data(_make_det("Snow", 0.80))
        res = reason_over_detections("Is there any physical damage?", data)
        assert res["guardrail_triggered"] is True
        assert "No reliable" in res["answer"]


# ===========================================================================
# 16: LOCATION QUERIES
# ===========================================================================

class TestLocationQueries:

    def test_16_location_reasoning(self):
        data = _make_data(
            _make_det("Physical Damage", 0.82, 400, 200, 500, 300),
            img_w=640, img_h=480,
        )
        res = reason_over_detections("Where is the physical damage?", data)
        assert res["intent"] == "LOCATION_QUERY"
        assert res["guardrail_triggered"] is False
        # bbox center ~(450, 250) in 640x480 → right-ish area
        assert "right" in res["answer"].lower() or "center" in res["answer"].lower()

    def test_16b_location_highest_confidence(self):
        data = _make_data(
            _make_det("Defective", 0.55, 10, 10, 100, 100),
            _make_det("Defective", 0.90, 500, 400, 600, 450),
            img_w=640, img_h=480,
        )
        res = reason_over_detections("Where is the highest-confidence detection?", data)
        assert "90%" in res["answer"]


# ===========================================================================
# 17-18: CONFIDENCE TIERS & GUARDRAILS
# ===========================================================================

class TestConfidenceTiers:

    def test_17_medium_confidence(self):
        data = _make_data(_make_det("Physical Damage", 0.61))
        res = reason_over_detections("Is there physical damage?", data)
        assert "moderate confidence" in res["answer"] or "61%" in res["answer"]
        assert res["evidence"]["confidence_tier"] == "MEDIUM"

    def test_18_low_confidence_guardrail(self):
        data = _make_data(_make_det("Physical Damage", 0.31))
        res = reason_over_detections("Is there physical damage?", data)
        assert res["guardrail_triggered"] is True
        assert "low-confidence" in res["answer"]
        assert "31%" in res["answer"]
        assert res["evidence"]["confidence_tier"] == "LOW"


# ===========================================================================
# 19: NO DETECTIONS
# ===========================================================================

class TestNoDetections:

    def test_19_no_detections(self):
        res = reason_over_detections("Is there damage?", EMPTY_DATA)
        assert res["guardrail_triggered"] is True
        assert "No detections" in res["answer"] or "insufficient" in res["answer"].lower()


# ===========================================================================
# 20-23: UNSUPPORTED QUESTIONS
# ===========================================================================

class TestUnsupportedQuestions:

    def test_20_unsupported_generic(self):
        res = reason_over_detections("How much does it cost to repair?", EMPTY_DATA)
        assert res["intent"] == "UNSUPPORTED"
        assert res["guardrail_triggered"] is True
        assert "cannot determine" in res["answer"]

    def test_21_causal_question(self):
        res = reason_over_detections("What caused the damage?", EMPTY_DATA)
        assert res["intent"] == "UNSUPPORTED"
        assert res["guardrail_triggered"] is True

    def test_22_future_prediction(self):
        res = reason_over_detections("Will this panel fail tomorrow?", EMPTY_DATA)
        assert res["intent"] == "UNSUPPORTED"
        assert res["guardrail_triggered"] is True

    def test_23_electrical_property(self):
        res = reason_over_detections("What is the voltage of this panel?", EMPTY_DATA)
        assert res["intent"] == "UNSUPPORTED"
        assert res["guardrail_triggered"] is True

    def test_23b_power_output(self):
        res = reason_over_detections("How much power is this panel producing?", EMPTY_DATA)
        assert res["intent"] == "UNSUPPORTED"


# ===========================================================================
# 24: OVERLAPPING DETECTIONS
# ===========================================================================

class TestOverlappingDetections:

    def test_24_overlapping_detections(self):
        data = _make_data(
            _make_det("Defective", 0.80, 100, 100, 200, 200),
            _make_det("Defective", 0.75, 110, 110, 210, 210),  # heavy overlap
            _make_det("Defective", 0.70, 105, 105, 205, 205),
        )
        res = reason_over_detections("Summarize the image.", data)
        assert "overlapping" in res["answer"].lower()
        assert res["evidence"]["overlapping_detections"] is True

    def test_24b_iou_calculation(self):
        box_a = {"x1": 0, "y1": 0, "x2": 100, "y2": 100}
        box_b = {"x1": 50, "y1": 50, "x2": 150, "y2": 150}
        iou = _compute_iou(box_a, box_b)
        # Intersection: 50x50=2500, Union: 10000+10000-2500=17500
        assert abs(iou - 2500 / 17500) < 0.01

    def test_24c_no_overlap(self):
        box_a = {"x1": 0, "y1": 0, "x2": 50, "y2": 50}
        box_b = {"x1": 200, "y1": 200, "x2": 300, "y2": 300}
        assert _compute_iou(box_a, box_b) == 0.0


# ===========================================================================
# 25: GENERAL KNOWLEDGE QUESTIONS
# ===========================================================================

class TestGeneralKnowledge:

    def test_25_general_knowledge(self):
        res = reason_over_detections("What is a solar panel?", EMPTY_DATA)
        assert res["intent"] == "GENERAL_KNOWLEDGE"
        assert res["guardrail_triggered"] is False
        assert res["detector_invoked"] is False
        assert "general knowledge" in res["answer"].lower()

    def test_25b_rt_detr_question(self):
        res = reason_over_detections("What does RT-DETR mean?", EMPTY_DATA)
        assert res["intent"] == "GENERAL_KNOWLEDGE"

    def test_25c_photovoltaic(self):
        res = reason_over_detections("What is photovoltaic energy?", EMPTY_DATA)
        assert res["intent"] == "GENERAL_KNOWLEDGE"


# ===========================================================================
# 26: EMPTY / EDGE-CASE QUESTIONS
# ===========================================================================

class TestEdgeCases:

    def test_26_empty_question(self):
        res = reason_over_detections("", EMPTY_DATA)
        assert res["intent"] == "UNSUPPORTED"
        assert res["guardrail_triggered"] is True

    def test_26b_whitespace_only(self):
        res = reason_over_detections("   ", EMPTY_DATA)
        assert res["intent"] == "UNSUPPORTED"

    def test_27_intent_routing_consistency(self):
        """All visual intents route correctly."""
        assert route_intent("How many damaged areas?") == "COUNT_QUERY"
        assert route_intent("Is there any dust?") == "CLASS_QUERY"
        assert route_intent("What is the confidence?") == "CONFIDENCE_QUERY"
        assert route_intent("Where is the damage?") == "LOCATION_QUERY"
        assert route_intent("Which class appears most frequently?") == "COMPARISON_QUERY"
        assert route_intent("Summarize the image.") == "SUMMARY_QUERY"
        assert route_intent("What types of faults are detected?") == "FAULT_ANALYSIS_QUERY"
        assert route_intent("Is the panel defective?") == "CONDITION_QUERY"
        assert route_intent("What is a solar panel?") == "GENERAL_KNOWLEDGE"
        assert route_intent("How much does it cost to repair?") == "UNSUPPORTED"
        assert route_intent("") == "UNSUPPORTED"


# ===========================================================================
# 28: CASE-INSENSITIVE QUESTIONS
# ===========================================================================

class TestCaseInsensitive:

    def test_28_case_insensitive_routing(self):
        assert route_intent("HOW MANY DEFECTIVE PANELS?") == "COUNT_QUERY"
        assert route_intent("IS THERE PHYSICAL DAMAGE?") == "CLASS_QUERY"
        assert route_intent("WHAT IS A SOLAR PANEL?") == "GENERAL_KNOWLEDGE"

    def test_28b_case_insensitive_answer(self):
        res = reason_over_detections("HOW MANY DEFECTIVE PANELS?", RICH_DATA)
        assert "2 Defective" in res["answer"]


# ===========================================================================
# 29: NATURAL SYNONYMS
# ===========================================================================

class TestNaturalSynonyms:

    def test_29_synonym_resolution(self):
        assert "Physical Damage" in resolve_classes("Is there any damage?")
        assert "Dusty" in resolve_classes("Is there dust?")
        assert "Snow" in resolve_classes("Is it snowy?")
        assert "Bird Drop" in resolve_classes("Are there bird droppings?")
        assert "Defective" in resolve_classes("Is the panel faulty?")
        assert "Non Defective" in resolve_classes("Is the panel healthy?")

    def test_29b_synonym_broken(self):
        data = _make_data(_make_det("Physical Damage", 0.85))
        res = reason_over_detections("Is there a broken area?", data)
        assert "Physical Damage" in res["answer"]

    def test_29c_synonym_bird_waste(self):
        data = _make_data(_make_det("Bird Drop", 0.75))
        res = reason_over_detections("Is there any bird waste?", data)
        assert "Bird Drop" in res["answer"]


# ===========================================================================
# 30: MULTIPLE-CLASS QUESTIONS
# ===========================================================================

class TestMultiClassQuestions:

    def test_30_multiple_classes(self):
        """Question mentioning multiple classes returns all relevant evidence."""
        data = _make_data(
            _make_det("Physical Damage", 0.82),
            _make_det("Dusty", 0.60),
        )
        res = reason_over_detections(
            "How many damaged and dusty detections are there?", data
        )
        assert res["intent"] == "COUNT_QUERY"
        assert "Physical Damage" in res["answer"]
        assert "Dusty" in res["answer"]
        assert res["evidence"]["count"] == 2


# ===========================================================================
# BONUS: ADDITIONAL COVERAGE
# ===========================================================================

class TestSummaryQuery:

    def test_summary_all_classes(self):
        res = reason_over_detections("Summarize the image.", RICH_DATA)
        assert res["intent"] == "SUMMARY_QUERY"
        assert "6" in res["answer"]
        assert res["guardrail_triggered"] is False

    def test_summary_no_detections(self):
        res = reason_over_detections("Summarize the image.", EMPTY_DATA)
        assert res["guardrail_triggered"] is True


class TestFaultAnalysis:

    def test_fault_analysis(self):
        res = reason_over_detections("What types of faults are detected?", RICH_DATA)
        assert res["intent"] == "FAULT_ANALYSIS_QUERY"
        assert res["guardrail_triggered"] is False
        # Should not include "Non Defective" as a fault
        assert "Non Defective" not in res["answer"]

    def test_fault_analysis_no_faults(self):
        data = _make_data(_make_det("Non Defective", 0.95))
        res = reason_over_detections("What types of faults are detected?", data)
        assert res["guardrail_triggered"] is True
        assert "No fault" in res["answer"]


class TestConditionQuery:

    def test_condition_healthy(self):
        data = _make_data(
            _make_det("Non Defective", 0.90),
            _make_det("Non Defective", 0.85),
        )
        res = reason_over_detections("Does this panel appear healthy?", data)
        assert res["intent"] == "CONDITION_QUERY"
        assert "Non Defective" in res["answer"]
        assert res["guardrail_triggered"] is False

    def test_condition_not_healthy(self):
        data = _make_data(
            _make_det("Non Defective", 0.90),
            _make_det("Physical Damage", 0.75),
        )
        res = reason_over_detections("Does this panel appear healthy?", data)
        assert "not" in res["answer"].lower() or "does not" in res["answer"].lower()


class TestResponseStructure:

    def test_response_has_all_fields(self):
        """Verify backward-compatible response shape."""
        res = reason_over_detections("How many defective?", RICH_DATA)
        assert "question" in res
        assert "intent" in res
        assert "answer" in res
        assert "guardrail_triggered" in res
        assert "relevant_detections" in res
        assert "detections_used" in res
        assert "detector_invoked" in res
        assert "evidence" in res
        assert "relevant_class" in res["evidence"]
        assert "count" in res["evidence"]
        assert "max_confidence" in res["evidence"]
        assert "confidence_tier" in res["evidence"]
        assert "location" in res["evidence"]
        assert "overlapping_detections" in res["evidence"]


class TestHelperFunctions:

    def test_confidence_tiers(self):
        assert get_confidence_tier(0.90) == "HIGH"
        assert get_confidence_tier(0.70) == "HIGH"
        assert get_confidence_tier(0.69) == "MEDIUM"
        assert get_confidence_tier(0.50) == "MEDIUM"
        assert get_confidence_tier(0.49) == "LOW"
        assert get_confidence_tier(0.10) == "LOW"

    def test_format_confidence_high(self):
        text = format_confidence_language("Defective", 0.90)
        assert "high confidence" in text

    def test_format_confidence_medium(self):
        text = format_confidence_language("Dusty", 0.55)
        assert "moderate confidence" in text

    def test_format_confidence_low(self):
        text = format_confidence_language("Snow", 0.30)
        assert "low-confidence" in text
        assert "not be treated as reliable" in text

    def test_spatial_location_center(self):
        loc = get_spatial_location({"x1": 200, "y1": 150, "x2": 300, "y2": 250}, 640, 480)
        assert loc == "center"

    def test_spatial_location_top_left(self):
        loc = get_spatial_location({"x1": 0, "y1": 0, "x2": 50, "y2": 50}, 640, 480)
        assert loc == "top-left"

    def test_spatial_location_bottom_right(self):
        loc = get_spatial_location({"x1": 500, "y1": 400, "x2": 600, "y2": 460}, 640, 480)
        assert loc == "bottom-right"

    def test_detect_overlaps_true(self):
        dets = [
            _make_det("A", 0.9, 100, 100, 200, 200),
            _make_det("B", 0.8, 110, 110, 210, 210),
        ]
        assert detect_overlaps(dets) is True

    def test_detect_overlaps_false(self):
        dets = [
            _make_det("A", 0.9, 0, 0, 50, 50),
            _make_det("B", 0.8, 500, 500, 600, 600),
        ]
        assert detect_overlaps(dets) is False
