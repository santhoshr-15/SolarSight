"""
SolarSight Constrained Reasoning Engine v2.0

Deterministic, evidence-grounded reasoning over RT-DETR detection outputs.
NEVER invents visual facts. NEVER assumes undetected objects exist.
Reports MODEL EVIDENCE, not reality.
"""

# ---------------------------------------------------------------------------
# 1. CONSTANTS & CONFIGURATION
# ---------------------------------------------------------------------------

KNOWN_CLASSES = frozenset([
    "Bird Drop",
    "Defective",
    "Dusty",
    "Non Defective",
    "Physical Damage",
    "Snow",
])

# Maps natural-language synonyms → canonical class name(s).
# Each key is lowercased; value is a list (one synonym may map to multiple).
SYNONYM_MAP = {
    # Physical Damage
    "damage": ["Physical Damage"],
    "damaged": ["Physical Damage"],
    "physical damage": ["Physical Damage"],
    "broken": ["Physical Damage"],
    "broken area": ["Physical Damage"],
    "crack": ["Physical Damage"],
    "cracked": ["Physical Damage"],
    "shattered": ["Physical Damage"],
    # Defective
    "defective": ["Defective"],
    "defect": ["Defective"],
    "faulty": ["Defective"],
    "fault": ["Defective"],
    "faults": ["Defective"],
    # Dusty
    "dust": ["Dusty"],
    "dusty": ["Dusty"],
    "dirty": ["Dusty"],
    "soiled": ["Dusty"],
    # Snow
    "snow": ["Snow"],
    "snowy": ["Snow"],
    "ice": ["Snow"],
    "icy": ["Snow"],
    "frozen": ["Snow"],
    # Bird Drop
    "bird drop": ["Bird Drop"],
    "bird drops": ["Bird Drop"],
    "bird droppings": ["Bird Drop"],
    "bird dropping": ["Bird Drop"],
    "bird waste": ["Bird Drop"],
    "bird poop": ["Bird Drop"],
    "bird": ["Bird Drop"],
    # Non Defective
    "non defective": ["Non Defective"],
    "non-defective": ["Non Defective"],
    "healthy": ["Non Defective"],
    "normal": ["Non Defective"],
    "clean": ["Non Defective"],
    "good": ["Non Defective"],
}

# Confidence tiers
CONFIDENCE_HIGH = 0.70
CONFIDENCE_MEDIUM = 0.50

# Unsupported question keywords — checked first, highest priority
UNSUPPORTED_KEYWORDS = [
    "caused", "cause", "why did",
    "cost", "price", "how much does it cost",
    "repair", "fix it", "replace",
    "temperature", "heat", "thermal",
    "power output", "power generation", "watt", "kilowatt", "energy output", "power", "producing",
    "will fail", "will it fail", "tomorrow", "predict", "prediction", "future",
    "electrical", "voltage", "current", "ampere", "resistance",
    "structural integrity", "structural",
    "severity", "how severe", "how bad",
    "warranty", "insurance",
    "how old", "age of",
    "manufacturer", "brand",
    "efficiency", "how efficient",
]

# General-knowledge question patterns (no visual evidence needed)
GENERAL_KNOWLEDGE_KEYWORDS = [
    "what is a solar panel",
    "what are solar panels",
    "what is photovoltaic",
    "what does rt-detr mean",
    "what is rt-detr",
    "explain solar",
    "what is pv",
    "how do solar panels work",
    "what is object detection",
    "what is deep learning",
    "who made this",
    "who built this",
    "what is this app",
    "what is solarsight",
]

# Visual keywords that indicate detection is needed
VISUAL_KEYWORDS = [
    "damage", "defective", "defect", "dust", "dusty", "snow", "snowy",
    "bird", "fault", "faulty", "how many", "detect", "visible", "problem",
    "broken", "crack", "dirty", "soiled", "ice", "icy", "frozen",
    "bird drop", "bird dropping", "healthy", "normal", "clean",
    "non defective", "non-defective", "good",
    "panel", "image", "photo", "picture", "uploaded",
    "present", "exist", "found", "see", "seen",
    "where", "location", "region", "left", "right", "top", "bottom", "center",
    "confidence", "confident", "strongest", "weakest", "highest", "lowest",
    "most", "frequent", "common", "compare", "comparison",
    "summarize", "summary", "what faults", "what problems",
    "count", "number of", "total",
]


# ---------------------------------------------------------------------------
# 2. INTENT ROUTER
# ---------------------------------------------------------------------------

def route_intent(question: str) -> str:
    """
    Classify a natural-language question into one of 11 intent categories.

    Priority order:
    1. UNSUPPORTED — reject immediately
    2. GENERAL_KNOWLEDGE — no detector needed
    3. Specific visual intents — each with distinct keyword patterns
    4. DETECTION_REQUIRED — fallback for visual questions
    5. GENERAL_KNOWLEDGE — fallback for everything else
    """
    if not question or not question.strip():
        return "UNSUPPORTED"

    q = question.lower().strip()

    # --- Priority 1: Unsupported questions ---
    for kw in UNSUPPORTED_KEYWORDS:
        if kw in q:
            return "UNSUPPORTED"

    # --- Priority 2: General knowledge (exact phrase matches) ---
    for phrase in GENERAL_KNOWLEDGE_KEYWORDS:
        if phrase in q:
            return "GENERAL_KNOWLEDGE"

    # --- Priority 3: Specific visual intents ---

    # COUNT_QUERY
    count_triggers = ["how many", "count", "number of", "total detection", "total number"]
    for trigger in count_triggers:
        if trigger in q:
            return "COUNT_QUERY"

    # CONFIDENCE_QUERY
    confidence_triggers = [
        "confidence", "confident", "how sure",
        "strongest detection", "weakest detection",
        "highest confidence", "lowest confidence",
        "strongest defect", "strongest fault", "strongest evidence",
    ]
    for trigger in confidence_triggers:
        if trigger in q:
            return "CONFIDENCE_QUERY"

    # LOCATION_QUERY
    location_triggers = [
        "where is", "where are", "location of",
        "which region", "which area",
        "on the left", "on the right",
        "is the damage on",
        "where is the highest",
        "where is the strongest",
    ]
    for trigger in location_triggers:
        if trigger in q:
            return "LOCATION_QUERY"

    # COMPARISON_QUERY
    comparison_triggers = [
        "which class appears most",
        "which fault has the highest",
        "which fault has the lowest",
        "most frequently", "most common",
        "more than", "less than",
        "are there more", "compare",
        "which is more common",
        "which detected fault is",
        "most frequent",
    ]
    for trigger in comparison_triggers:
        if trigger in q:
            return "COMPARISON_QUERY"

    # SUMMARY_QUERY
    summary_triggers = [
        "summarize", "summary", "give me a",
        "what faults were", "what faults are",
        "what problems are", "what problems were",
        "what was detected", "what is detected",
        "detection summary", "overview",
    ]
    for trigger in summary_triggers:
        if trigger in q:
            return "SUMMARY_QUERY"

    # FAULT_ANALYSIS_QUERY
    fault_analysis_triggers = [
        "types of faults", "type of fault",
        "most significant", "significant fault",
        "strongest evidence of",
        "does the image contain any",
        "any detected fault",
    ]
    for trigger in fault_analysis_triggers:
        if trigger in q:
            return "FAULT_ANALYSIS_QUERY"

    # CONDITION_QUERY
    condition_triggers = [
        "is the panel", "is this panel",
        "does this panel", "does the panel",
        "panel defective", "panel damaged", "panel healthy",
        "any visible fault", "any detected problem",
        "are there any detected",
        "appear healthy",
        "any visible",
    ]
    for trigger in condition_triggers:
        if trigger in q:
            return "CONDITION_QUERY"

    # CLASS_QUERY — existence checks
    class_triggers = [
        "is there any", "is there a",
        "are there any", "is there",
        "is dust", "is snow", "is bird",
        "detected?", "present?", "visible?",
        "are all detected",
    ]
    for trigger in class_triggers:
        if trigger in q:
            return "CLASS_QUERY"

    # --- Fallback: check for any visual keyword ---
    for kw in VISUAL_KEYWORDS:
        if kw in q:
            return "DETECTION_REQUIRED"

    # --- Default: general knowledge ---
    return "GENERAL_KNOWLEDGE"


# ---------------------------------------------------------------------------
# 3. SYNONYM RESOLVER
# ---------------------------------------------------------------------------

def resolve_classes(question: str) -> list:
    """
    Extract canonical class names from natural-language question text.
    Returns a list of unique class names. Order preserved by first appearance.
    """
    q = question.lower()
    found = []
    seen = set()

    # Sort by length descending so longer phrases match first
    # (e.g. "bird droppings" before "bird")
    sorted_synonyms = sorted(SYNONYM_MAP.keys(), key=len, reverse=True)

    for synonym in sorted_synonyms:
        if synonym in q:
            for cls in SYNONYM_MAP[synonym]:
                if cls not in seen:
                    found.append(cls)
                    seen.add(cls)

    return found


# ---------------------------------------------------------------------------
# 4. CONFIDENCE TIERS
# ---------------------------------------------------------------------------

def get_confidence_tier(score: float) -> str:
    """Return the confidence tier label."""
    if score >= CONFIDENCE_HIGH:
        return "HIGH"
    elif score >= CONFIDENCE_MEDIUM:
        return "MEDIUM"
    else:
        return "LOW"


def format_confidence_language(class_name: str, score: float) -> str:
    """
    Generate tier-appropriate natural language for a detection.
    """
    pct = f"{score * 100:.0f}%"
    tier = get_confidence_tier(score)

    if tier == "HIGH":
        return f"The detector identified {class_name} with high confidence ({pct})."
    elif tier == "MEDIUM":
        return f"The detector identified {class_name} with moderate confidence ({pct})."
    else:
        return (
            f"The detector produced a low-confidence {class_name} detection ({pct}), "
            f"so this should not be treated as reliable evidence."
        )


# ---------------------------------------------------------------------------
# 5. SPATIAL LOCATION RESOLVER
# ---------------------------------------------------------------------------

def get_spatial_location(bbox: dict, img_width: int, img_height: int) -> str:
    """
    Map a bounding-box center to a human-readable spatial region.
    Returns e.g. "top-left", "center", "bottom-right".
    """
    if not bbox or img_width <= 0 or img_height <= 0:
        return "unknown"

    cx = (bbox.get("x1", 0) + bbox.get("x2", 0)) / 2
    cy = (bbox.get("y1", 0) + bbox.get("y2", 0)) / 2

    # Horizontal
    if cx < img_width / 3:
        h = "left"
    elif cx < 2 * img_width / 3:
        h = "center"
    else:
        h = "right"

    # Vertical
    if cy < img_height / 3:
        v = "top"
    elif cy < 2 * img_height / 3:
        v = "middle"
    else:
        v = "bottom"

    # Simplify "middle-center" → "center"
    if v == "middle" and h == "center":
        return "center"
    if v == "middle":
        return f"center-{h}"
    if h == "center":
        return f"{v}-center"
    return f"{v}-{h}"


# ---------------------------------------------------------------------------
# 6. OVERLAP DETECTOR
# ---------------------------------------------------------------------------

def _compute_iou(box_a: dict, box_b: dict) -> float:
    """Compute Intersection-over-Union between two bounding boxes."""
    x1 = max(box_a.get("x1", 0), box_b.get("x1", 0))
    y1 = max(box_a.get("y1", 0), box_b.get("y1", 0))
    x2 = min(box_a.get("x2", 0), box_b.get("x2", 0))
    y2 = min(box_a.get("y2", 0), box_b.get("y2", 0))

    inter = max(0, x2 - x1) * max(0, y2 - y1)
    if inter == 0:
        return 0.0

    area_a = max(0, box_a.get("x2", 0) - box_a.get("x1", 0)) * max(0, box_a.get("y2", 0) - box_a.get("y1", 0))
    area_b = max(0, box_b.get("x2", 0) - box_b.get("x1", 0)) * max(0, box_b.get("y2", 0) - box_b.get("y1", 0))

    union = area_a + area_b - inter
    if union == 0:
        return 0.0

    return inter / union


def detect_overlaps(detections: list, iou_threshold: float = 0.5) -> bool:
    """
    Check if any pair of detections has IoU above the threshold.
    Returns True if overlapping detections are found.
    """
    for i in range(len(detections)):
        for j in range(i + 1, len(detections)):
            box_a = detections[i].get("bounding_box", {})
            box_b = detections[j].get("bounding_box", {})
            if _compute_iou(box_a, box_b) >= iou_threshold:
                return True
    return False


# ---------------------------------------------------------------------------
# 7. HELPER: Extract filtered detections & stats
# ---------------------------------------------------------------------------

def _extract_evidence(detections_data: dict, target_classes: list):
    """
    Filter detections by target classes and compute statistics.
    If target_classes is empty, use ALL detections.
    Returns (filtered_detections, counts_dict, max_confidence, min_confidence, max_class, min_class).
    """
    all_dets = detections_data.get("detections", [])

    if target_classes:
        filtered = [d for d in all_dets if d.get("class_name") in target_classes]
    else:
        filtered = list(all_dets)

    counts = {}
    max_conf = 0.0
    min_conf = float("inf")
    max_class = None
    min_class = None

    for d in filtered:
        cls = d.get("class_name", "Unknown")
        conf = d.get("confidence", 0.0)
        counts[cls] = counts.get(cls, 0) + 1

        if conf > max_conf:
            max_conf = conf
            max_class = cls
        if conf < min_conf:
            min_conf = conf
            min_class = cls

    if not filtered:
        min_conf = 0.0

    return filtered, counts, max_conf, min_conf, max_class, min_class


# ---------------------------------------------------------------------------
# 8. ANSWER GENERATORS — one per intent
# ---------------------------------------------------------------------------

def _answer_count(question: str, detections_data: dict, target_classes: list) -> dict:
    """Handle COUNT_QUERY intent."""
    q = question.lower()
    all_dets = detections_data.get("detections", [])

    # "total detections" / "total number" → count everything
    if "total" in q:
        total = len(all_dets)
        return _build_response(
            question=question,
            intent="COUNT_QUERY",
            answer=f"There are {total} total detection(s) in the image.",
            evidence_class=None,
            count=total,
            max_confidence=max((d.get("confidence", 0) for d in all_dets), default=0.0),
            detections=all_dets,
        )

    filtered, counts, max_conf, _, max_class, _ = _extract_evidence(detections_data, target_classes)

    if not filtered:
        class_label = ", ".join(target_classes) if target_classes else "the requested category"
        return _build_response(
            question=question,
            intent="COUNT_QUERY",
            answer=f"No reliable {class_label} detections were found.",
            evidence_class=class_label,
            count=0,
            max_confidence=0.0,
            detections=[],
            guardrail=True,
        )

    parts = []
    for cls, cnt in counts.items():
        parts.append(f"{cnt} {cls}")

    counts_str = ", ".join(parts)
    answer = f"I found {counts_str} detection(s) in the image."

    return _build_response(
        question=question,
        intent="COUNT_QUERY",
        answer=answer,
        evidence_class=", ".join(counts.keys()),
        count=sum(counts.values()),
        max_confidence=max_conf,
        detections=filtered,
    )


def _answer_class_existence(question: str, detections_data: dict, target_classes: list) -> dict:
    """Handle CLASS_QUERY intent — is a class present?"""
    q = question.lower()

    # Handle "are all detected panels non-defective?"
    if "are all" in q:
        all_dets = detections_data.get("detections", [])
        if not all_dets:
            return _build_response(
                question=question,
                intent="CLASS_QUERY",
                answer="No detections were found, so this cannot be determined.",
                evidence_class=None,
                count=0,
                max_confidence=0.0,
                detections=[],
                guardrail=True,
            )
        non_target = [d for d in all_dets if d.get("class_name") not in (target_classes or ["Non Defective"])]
        if non_target:
            fault_classes = set(d.get("class_name") for d in non_target)
            answer = f"No. The detector found {', '.join(fault_classes)} detection(s), so not all panels appear non-defective."
            return _build_response(
                question=question,
                intent="CLASS_QUERY",
                answer=answer,
                evidence_class=", ".join(fault_classes),
                count=len(non_target),
                max_confidence=max(d.get("confidence", 0) for d in non_target),
                detections=non_target,
            )
        else:
            return _build_response(
                question=question,
                intent="CLASS_QUERY",
                answer="Yes. All detections are classified as Non Defective.",
                evidence_class="Non Defective",
                count=len(all_dets),
                max_confidence=max(d.get("confidence", 0) for d in all_dets),
                detections=all_dets,
            )

    filtered, counts, max_conf, _, max_class, _ = _extract_evidence(detections_data, target_classes)

    if not filtered:
        class_label = ", ".join(target_classes) if target_classes else "the requested class"
        return _build_response(
            question=question,
            intent="CLASS_QUERY",
            answer=f"No reliable {class_label} detection was found by the detector.",
            evidence_class=class_label,
            count=0,
            max_confidence=0.0,
            detections=[],
            guardrail=True,
        )

    # Check confidence tier of strongest detection
    tier = get_confidence_tier(max_conf)

    if tier == "LOW":
        class_label = max_class or ", ".join(target_classes)
        return _build_response(
            question=question,
            intent="CLASS_QUERY",
            answer=(
                f"The detector produced a low-confidence {class_label} detection "
                f"({max_conf * 100:.0f}%), so there is not enough reliable evidence "
                f"to confirm {class_label}."
            ),
            evidence_class=class_label,
            count=len(filtered),
            max_confidence=max_conf,
            detections=filtered,
            guardrail=True,
        )

    # Build affirmative answer with confidence language
    total = sum(counts.values())
    parts = []
    for cls, cnt in counts.items():
        parts.append(f"{cnt} {cls}")
    det_str = ", ".join(parts)

    answer = f"Yes. The detector found {det_str} detection(s). {format_confidence_language(max_class, max_conf)}"

    return _build_response(
        question=question,
        intent="CLASS_QUERY",
        answer=answer,
        evidence_class=max_class,
        count=total,
        max_confidence=max_conf,
        detections=filtered,
    )


def _answer_confidence(question: str, detections_data: dict, target_classes: list) -> dict:
    """Handle CONFIDENCE_QUERY intent."""
    q = question.lower()
    filtered, counts, max_conf, min_conf, max_class, min_class = _extract_evidence(
        detections_data, target_classes
    )

    if not filtered:
        return _build_response(
            question=question,
            intent="CONFIDENCE_QUERY",
            answer="No detections were found, so confidence information is unavailable.",
            evidence_class=None,
            count=0,
            max_confidence=0.0,
            detections=[],
            guardrail=True,
        )

    # "lowest" / "weakest"
    if "lowest" in q or "weakest" in q:
        answer = (
            f"The lowest-confidence detection is {min_class} at "
            f"{min_conf * 100:.0f}%. {format_confidence_language(min_class, min_conf)}"
        )
        return _build_response(
            question=question,
            intent="CONFIDENCE_QUERY",
            answer=answer,
            evidence_class=min_class,
            count=len(filtered),
            max_confidence=min_conf,
            detections=filtered,
        )

    # Default: highest / strongest
    answer = (
        f"The highest-confidence detection is {max_class} at "
        f"{max_conf * 100:.0f}%. {format_confidence_language(max_class, max_conf)}"
    )
    return _build_response(
        question=question,
        intent="CONFIDENCE_QUERY",
        answer=answer,
        evidence_class=max_class,
        count=len(filtered),
        max_confidence=max_conf,
        detections=filtered,
    )


def _answer_location(question: str, detections_data: dict, target_classes: list) -> dict:
    """Handle LOCATION_QUERY intent."""
    img_w = detections_data.get("image_width", 0)
    img_h = detections_data.get("image_height", 0)

    filtered, counts, max_conf, _, max_class, _ = _extract_evidence(detections_data, target_classes)

    if not filtered:
        class_label = ", ".join(target_classes) if target_classes else "the requested class"
        return _build_response(
            question=question,
            intent="LOCATION_QUERY",
            answer=f"No reliable {class_label} detection was found, so location cannot be determined.",
            evidence_class=class_label,
            count=0,
            max_confidence=0.0,
            detections=[],
            guardrail=True,
        )

    if img_w <= 0 or img_h <= 0:
        # Cannot compute location without image dimensions
        class_label = max_class or ", ".join(target_classes)
        total = sum(counts.values())
        answer = (
            f"The detector found {total} {class_label} detection(s), but image dimensions "
            f"are unavailable so precise location cannot be determined."
        )
        return _build_response(
            question=question,
            intent="LOCATION_QUERY",
            answer=answer,
            evidence_class=class_label,
            count=total,
            max_confidence=max_conf,
            detections=filtered,
        )

    # Build location descriptions for each detection
    q = question.lower()

    # "where is the highest-confidence detection?"
    if "highest" in q or "strongest" in q:
        best_det = max(filtered, key=lambda d: d.get("confidence", 0))
        loc = get_spatial_location(best_det.get("bounding_box", {}), img_w, img_h)
        answer = (
            f"The highest-confidence detection ({best_det['class_name']} at "
            f"{best_det['confidence'] * 100:.0f}%) is located near the {loc} area of the image."
        )
        return _build_response(
            question=question,
            intent="LOCATION_QUERY",
            answer=answer,
            evidence_class=best_det["class_name"],
            count=1,
            max_confidence=best_det["confidence"],
            detections=[best_det],
            location=loc,
        )

    # General: list all locations
    location_parts = []
    for d in filtered:
        bbox = d.get("bounding_box", {})
        loc = get_spatial_location(bbox, img_w, img_h)
        conf_pct = f"{d['confidence'] * 100:.0f}%"
        location_parts.append(
            f"A {d['class_name']} detection ({conf_pct}) is located near the {loc} area"
        )

    answer = ". ".join(location_parts) + " of the image."

    return _build_response(
        question=question,
        intent="LOCATION_QUERY",
        answer=answer,
        evidence_class=max_class,
        count=len(filtered),
        max_confidence=max_conf,
        detections=filtered,
        location="multiple",
    )


def _answer_comparison(question: str, detections_data: dict) -> dict:
    """Handle COMPARISON_QUERY intent."""
    all_dets = detections_data.get("detections", [])

    if not all_dets:
        return _build_response(
            question=question,
            intent="COMPARISON_QUERY",
            answer="No detections were found, so comparison is not possible.",
            evidence_class=None,
            count=0,
            max_confidence=0.0,
            detections=[],
            guardrail=True,
        )

    q = question.lower()

    # Count all classes
    class_counts = {}
    class_max_conf = {}
    for d in all_dets:
        cls = d.get("class_name", "Unknown")
        conf = d.get("confidence", 0.0)
        class_counts[cls] = class_counts.get(cls, 0) + 1
        if cls not in class_max_conf or conf > class_max_conf[cls]:
            class_max_conf[cls] = conf

    # "most frequent" / "most common" / "which class appears most"
    if any(kw in q for kw in ["most frequent", "most common", "most often", "appears most"]):
        max_count = max(class_counts.values())
        top_classes = [cls for cls, cnt in class_counts.items() if cnt == max_count]

        if len(top_classes) == 1:
            answer = (
                f"{top_classes[0]} is the most frequently detected class, "
                f"with {max_count} detection(s)."
            )
        else:
            tied = " and ".join(top_classes)
            answer = (
                f"{tied} are tied for the highest count, "
                f"with {max_count} detection(s) each."
            )

        return _build_response(
            question=question,
            intent="COMPARISON_QUERY",
            answer=answer,
            evidence_class=", ".join(top_classes),
            count=max_count,
            max_confidence=max(class_max_conf.get(c, 0) for c in top_classes),
            detections=all_dets,
        )

    # "highest confidence" / "strongest"
    if any(kw in q for kw in ["highest confidence", "strongest", "highest"]):
        best_cls = max(class_max_conf, key=class_max_conf.get)
        best_conf = class_max_conf[best_cls]
        answer = (
            f"{best_cls} has the highest-confidence detection at "
            f"{best_conf * 100:.0f}%."
        )
        return _build_response(
            question=question,
            intent="COMPARISON_QUERY",
            answer=answer,
            evidence_class=best_cls,
            count=class_counts[best_cls],
            max_confidence=best_conf,
            detections=all_dets,
        )

    # "lowest confidence"
    if any(kw in q for kw in ["lowest confidence", "weakest", "lowest"]):
        worst_cls = min(class_max_conf, key=class_max_conf.get)
        worst_conf = class_max_conf[worst_cls]
        answer = (
            f"{worst_cls} has the lowest-confidence detection at "
            f"{worst_conf * 100:.0f}%."
        )
        return _build_response(
            question=question,
            intent="COMPARISON_QUERY",
            answer=answer,
            evidence_class=worst_cls,
            count=class_counts[worst_cls],
            max_confidence=worst_conf,
            detections=all_dets,
        )

    # "more ... than" comparisons — extract two classes
    if "more" in q and "than" in q:
        resolved = resolve_classes(question)
        if len(resolved) >= 2:
            cls_a, cls_b = resolved[0], resolved[1]
            cnt_a = class_counts.get(cls_a, 0)
            cnt_b = class_counts.get(cls_b, 0)
            if cnt_a > cnt_b:
                answer = f"Yes. {cls_a} has {cnt_a} detection(s) compared to {cls_b} with {cnt_b}."
            elif cnt_b > cnt_a:
                answer = f"No. {cls_b} has {cnt_b} detection(s) compared to {cls_a} with {cnt_a}."
            else:
                answer = f"{cls_a} and {cls_b} are tied with {cnt_a} detection(s) each."
            return _build_response(
                question=question,
                intent="COMPARISON_QUERY",
                answer=answer,
                evidence_class=f"{cls_a}, {cls_b}",
                count=cnt_a + cnt_b,
                max_confidence=max(class_max_conf.get(cls_a, 0), class_max_conf.get(cls_b, 0)),
                detections=all_dets,
            )

    # Fallback comparison: show all class counts
    parts = [f"{cls}: {cnt}" for cls, cnt in sorted(class_counts.items(), key=lambda x: -x[1])]
    answer = "Detection counts by class: " + ", ".join(parts) + "."
    return _build_response(
        question=question,
        intent="COMPARISON_QUERY",
        answer=answer,
        evidence_class=None,
        count=len(all_dets),
        max_confidence=max(class_max_conf.values()) if class_max_conf else 0.0,
        detections=all_dets,
    )


def _answer_summary(question: str, detections_data: dict) -> dict:
    """Handle SUMMARY_QUERY intent."""
    all_dets = detections_data.get("detections", [])

    if not all_dets:
        return _build_response(
            question=question,
            intent="SUMMARY_QUERY",
            answer="No detections were found in the image.",
            evidence_class=None,
            count=0,
            max_confidence=0.0,
            detections=[],
            guardrail=True,
        )

    class_counts = {}
    class_max_conf = {}
    for d in all_dets:
        cls = d.get("class_name", "Unknown")
        conf = d.get("confidence", 0.0)
        class_counts[cls] = class_counts.get(cls, 0) + 1
        if cls not in class_max_conf or conf > class_max_conf[cls]:
            class_max_conf[cls] = conf

    total = len(all_dets)
    parts = []
    for cls in sorted(class_counts.keys()):
        cnt = class_counts[cls]
        conf = class_max_conf[cls]
        tier = get_confidence_tier(conf)
        tier_label = f"{'high' if tier == 'HIGH' else 'moderate' if tier == 'MEDIUM' else 'low'} confidence"
        parts.append(f"{cnt} {cls} ({tier_label}, up to {conf * 100:.0f}%)")

    summary = ", ".join(parts)

    # Check for overlaps
    has_overlaps = detect_overlaps(all_dets)
    overlap_note = ""
    if has_overlaps:
        overlap_note = (
            " Note: Some detections have overlapping bounding boxes and may represent "
            "repeated detections of the same underlying area."
        )

    answer = f"The detector found {total} detection(s): {summary}.{overlap_note}"

    return _build_response(
        question=question,
        intent="SUMMARY_QUERY",
        answer=answer,
        evidence_class=None,
        count=total,
        max_confidence=max(class_max_conf.values()) if class_max_conf else 0.0,
        detections=all_dets,
        overlapping=has_overlaps,
    )


def _answer_fault_analysis(question: str, detections_data: dict) -> dict:
    """Handle FAULT_ANALYSIS_QUERY intent."""
    all_dets = detections_data.get("detections", [])
    # Filter out "Non Defective" for fault analysis
    fault_dets = [d for d in all_dets if d.get("class_name") != "Non Defective"]

    if not fault_dets:
        return _build_response(
            question=question,
            intent="FAULT_ANALYSIS_QUERY",
            answer="No fault detections were found in the image. All detections (if any) are Non Defective.",
            evidence_class=None,
            count=0,
            max_confidence=0.0,
            detections=[],
            guardrail=True,
        )

    fault_counts = {}
    fault_max_conf = {}
    for d in fault_dets:
        cls = d.get("class_name")
        conf = d.get("confidence", 0.0)
        fault_counts[cls] = fault_counts.get(cls, 0) + 1
        if cls not in fault_max_conf or conf > fault_max_conf[cls]:
            fault_max_conf[cls] = conf

    # Find strongest fault
    strongest_cls = max(fault_max_conf, key=fault_max_conf.get)
    strongest_conf = fault_max_conf[strongest_cls]

    fault_types = sorted(fault_counts.keys())
    types_str = ", ".join(fault_types)
    total = sum(fault_counts.values())

    answer = (
        f"The detector found {total} fault detection(s) across {len(fault_types)} type(s): {types_str}. "
        f"The strongest evidence is {strongest_cls} at {strongest_conf * 100:.0f}% confidence. "
        f"{format_confidence_language(strongest_cls, strongest_conf)}"
    )

    return _build_response(
        question=question,
        intent="FAULT_ANALYSIS_QUERY",
        answer=answer,
        evidence_class=strongest_cls,
        count=total,
        max_confidence=strongest_conf,
        detections=fault_dets,
    )


def _answer_condition(question: str, detections_data: dict, target_classes: list) -> dict:
    """Handle CONDITION_QUERY intent — 'Is the panel defective?', 'Is the panel healthy?'"""
    q = question.lower()
    all_dets = detections_data.get("detections", [])

    # "healthy" / "normal" → check if only Non Defective exists
    asking_healthy = any(kw in q for kw in ["healthy", "normal", "good condition", "appear healthy"])

    if asking_healthy:
        fault_dets = [d for d in all_dets if d.get("class_name") != "Non Defective"]

        if not all_dets:
            return _build_response(
                question=question,
                intent="CONDITION_QUERY",
                answer="No detections were found, so the panel's condition cannot be determined from the available evidence.",
                evidence_class=None,
                count=0,
                max_confidence=0.0,
                detections=[],
                guardrail=True,
            )

        if fault_dets:
            # Has faults — high-conf faults are definitive, low-conf are cautious
            max_fault_conf = max(d.get("confidence", 0) for d in fault_dets)
            fault_classes = set(d.get("class_name") for d in fault_dets)
            tier = get_confidence_tier(max_fault_conf)

            if tier == "LOW":
                answer = (
                    f"The detector found low-confidence {', '.join(fault_classes)} detection(s) "
                    f"(up to {max_fault_conf * 100:.0f}%), so the panel's condition cannot be "
                    f"reliably determined from the available evidence."
                )
                return _build_response(
                    question=question,
                    intent="CONDITION_QUERY",
                    answer=answer,
                    evidence_class=", ".join(fault_classes),
                    count=len(fault_dets),
                    max_confidence=max_fault_conf,
                    detections=fault_dets,
                    guardrail=True,
                )

            answer = (
                f"The detector found {', '.join(fault_classes)} detection(s), "
                f"so the panel does not appear fully healthy. "
                f"{format_confidence_language(list(fault_classes)[0], max_fault_conf)}"
            )
            return _build_response(
                question=question,
                intent="CONDITION_QUERY",
                answer=answer,
                evidence_class=", ".join(fault_classes),
                count=len(fault_dets),
                max_confidence=max_fault_conf,
                detections=fault_dets,
            )
        else:
            # Only Non Defective
            max_conf = max((d.get("confidence", 0) for d in all_dets), default=0.0)
            answer = (
                f"Based on the available detections, all panels appear Non Defective "
                f"(highest confidence: {max_conf * 100:.0f}%)."
            )
            return _build_response(
                question=question,
                intent="CONDITION_QUERY",
                answer=answer,
                evidence_class="Non Defective",
                count=len(all_dets),
                max_confidence=max_conf,
                detections=all_dets,
            )

    # "defective" / "damaged" / general fault condition
    filtered, counts, max_conf, _, max_class, _ = _extract_evidence(detections_data, target_classes)

    # If no target classes resolved, look for all fault classes
    if not target_classes:
        filtered = [d for d in all_dets if d.get("class_name") != "Non Defective"]
        counts = {}
        max_conf = 0.0
        max_class = None
        for d in filtered:
            cls = d.get("class_name")
            conf = d.get("confidence", 0.0)
            counts[cls] = counts.get(cls, 0) + 1
            if conf > max_conf:
                max_conf = conf
                max_class = cls

    if not filtered:
        class_label = ", ".join(target_classes) if target_classes else "any fault"
        return _build_response(
            question=question,
            intent="CONDITION_QUERY",
            answer=f"The detector did not find sufficient evidence of {class_label}.",
            evidence_class=class_label,
            count=0,
            max_confidence=0.0,
            detections=[],
            guardrail=True,
        )

    tier = get_confidence_tier(max_conf)

    if tier == "LOW":
        answer = (
            f"The detector produced only low-confidence evidence ({max_conf * 100:.0f}%), "
            f"so the panel's condition cannot be reliably confirmed."
        )
        return _build_response(
            question=question,
            intent="CONDITION_QUERY",
            answer=answer,
            evidence_class=max_class,
            count=len(filtered),
            max_confidence=max_conf,
            detections=filtered,
            guardrail=True,
        )

    total = sum(counts.values())
    classes_str = ", ".join(counts.keys())
    answer = (
        f"The detector found {total} {classes_str} detection(s). "
        f"{format_confidence_language(max_class, max_conf)}"
    )
    return _build_response(
        question=question,
        intent="CONDITION_QUERY",
        answer=answer,
        evidence_class=max_class,
        count=total,
        max_confidence=max_conf,
        detections=filtered,
    )


def _answer_general_knowledge(question: str) -> dict:
    """Handle GENERAL_KNOWLEDGE intent — no detector needed."""
    return _build_response(
        question=question,
        intent="GENERAL_KNOWLEDGE",
        answer=(
            "This appears to be a general knowledge question that does not require "
            "visual inspection of the solar panel. The SolarSight reasoning engine "
            "is designed to answer questions about detector evidence from uploaded images."
        ),
        evidence_class=None,
        count=0,
        max_confidence=0.0,
        detections=[],
        detector_invoked=False,
    )


def _answer_unsupported(question: str) -> dict:
    """Handle UNSUPPORTED intent — outside detector capability."""
    return _build_response(
        question=question,
        intent="UNSUPPORTED",
        answer=(
            "The available visual detection data cannot determine that. "
            "The detector identifies visual fault categories (Bird Drop, Defective, Dusty, "
            "Non Defective, Physical Damage, Snow) but does not provide enough information "
            "to answer this type of question."
        ),
        evidence_class=None,
        count=0,
        max_confidence=0.0,
        detections=[],
        guardrail=True,
        detector_invoked=False,
    )


def _answer_detection_required(question: str, detections_data: dict, target_classes: list) -> dict:
    """Handle DETECTION_REQUIRED fallback intent."""
    filtered, counts, max_conf, _, max_class, _ = _extract_evidence(detections_data, target_classes)

    if not filtered:
        return _build_response(
            question=question,
            intent="DETECTION_REQUIRED",
            answer=(
                "The detector did not find sufficient evidence to answer this question reliably."
            ),
            evidence_class=None,
            count=0,
            max_confidence=0.0,
            detections=[],
            guardrail=True,
        )

    # Check for low confidence
    tier = get_confidence_tier(max_conf)

    if tier == "LOW":
        answer = (
            f"The detector produced only low-confidence evidence ({max_conf * 100:.0f}%), "
            f"so I cannot reliably confirm that."
        )
        return _build_response(
            question=question,
            intent="DETECTION_REQUIRED",
            answer=answer,
            evidence_class=max_class,
            count=len(filtered),
            max_confidence=max_conf,
            detections=filtered,
            guardrail=True,
        )

    # Build general answer
    total = sum(counts.values())
    classes_str = " and ".join(counts.keys())

    has_overlaps = detect_overlaps(filtered)
    overlap_note = ""
    if has_overlaps:
        overlap_note = (
            " Note: Some detections have overlapping bounding boxes and may represent "
            "repeated detections of the same underlying area."
        )

    answer = (
        f"{classes_str} was detected with {max_conf * 100:.0f}% confidence "
        f"({total} detection(s)).{overlap_note}"
    )

    return _build_response(
        question=question,
        intent="DETECTION_REQUIRED",
        answer=answer,
        evidence_class=max_class,
        count=total,
        max_confidence=max_conf,
        detections=filtered,
        overlapping=has_overlaps,
    )


# ---------------------------------------------------------------------------
# 9. RESPONSE BUILDER
# ---------------------------------------------------------------------------

def _build_response(
    question: str,
    intent: str,
    answer: str,
    evidence_class,
    count: int,
    max_confidence: float,
    detections: list,
    guardrail: bool = False,
    detector_invoked: bool = True,
    location: str = None,
    overlapping: bool = False,
) -> dict:
    """
    Build the structured response, ensuring backward compatibility.
    """
    return {
        # Core fields (backward-compatible)
        "question": question,
        "intent": intent,
        "answer": answer,
        "guardrail_triggered": guardrail,
        # Backward-compat fields used by frontend
        "relevant_detections": detections,
        "detections_used": len(detections),
        "detector_invoked": detector_invoked,
        # New structured evidence object
        "evidence": {
            "relevant_class": evidence_class,
            "count": count,
            "max_confidence": round(max_confidence, 4),
            "confidence_tier": (
                get_confidence_tier(max_confidence) if max_confidence > 0 else "N/A"
            ),
            "location": location,
            "overlapping_detections": overlapping,
        },
    }


# ---------------------------------------------------------------------------
# 10. MASTER ORCHESTRATOR
# ---------------------------------------------------------------------------

def reason_over_detections(question: str, detections_data: dict) -> dict:
    """
    Master reasoning orchestrator.

    Pipeline:
      question → intent → class resolution → evidence extraction
      → confidence validation → answer generation → structured response

    CORE RULE: If the detector does not provide enough evidence,
    the system MUST say it cannot reliably determine the answer.
    """
    intent = route_intent(question)

    # --- Intents that don't require detector evidence ---
    if intent == "GENERAL_KNOWLEDGE":
        return _answer_general_knowledge(question)

    if intent == "UNSUPPORTED":
        return _answer_unsupported(question)

    # --- Intents that require detector evidence ---
    target_classes = resolve_classes(question)

    # No detections at all
    if detections_data.get("total_detections", 0) == 0 and not detections_data.get("detections"):
        return _build_response(
            question=question,
            intent=intent,
            answer=(
                "No detections were produced by the detector for this image, "
                "so there is insufficient evidence to answer reliably."
            ),
            evidence_class=None,
            count=0,
            max_confidence=0.0,
            detections=[],
            guardrail=True,
        )

    # --- Dispatch to intent-specific handler ---
    if intent == "COUNT_QUERY":
        return _answer_count(question, detections_data, target_classes)

    if intent == "CLASS_QUERY":
        return _answer_class_existence(question, detections_data, target_classes)

    if intent == "CONFIDENCE_QUERY":
        return _answer_confidence(question, detections_data, target_classes)

    if intent == "LOCATION_QUERY":
        return _answer_location(question, detections_data, target_classes)

    if intent == "COMPARISON_QUERY":
        return _answer_comparison(question, detections_data)

    if intent == "SUMMARY_QUERY":
        return _answer_summary(question, detections_data)

    if intent == "FAULT_ANALYSIS_QUERY":
        return _answer_fault_analysis(question, detections_data)

    if intent == "CONDITION_QUERY":
        return _answer_condition(question, detections_data, target_classes)

    # DETECTION_REQUIRED fallback
    return _answer_detection_required(question, detections_data, target_classes)
