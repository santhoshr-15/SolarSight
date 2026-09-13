def route_intent(question: str) -> str:
    """
    Simple intent router determining if visual detection is required.
    """
    question_lower = question.lower()
    visual_keywords = [
        "damage", "defective", "dust", "snow", "bird", 
        "fault", "how many", "detect", "visible", "problem"
    ]
    
    for kw in visual_keywords:
        if kw in question_lower:
            return "visual_detection_required"
            
    return "general_question"


def reason_over_detections(question: str, detections_data: dict) -> dict:
    """
    Produce a concise natural-language answer over structured detections.
    Implements a strict confidence/insufficient information guardrail.
    """
    intent = route_intent(question)
    
    if intent == "general_question":
        return {
            "question": question,
            "intent": intent,
            "answer": "This appears to be a general question that does not require visual inspection of the solar panel.",
            "relevant_detections": [],
            "guardrail_triggered": False
        }
        
    if detections_data.get("total_detections", 0) == 0:
        return {
            "question": question,
            "intent": intent,
            "answer": "Insufficient information from the detector to answer reliably. The detector did not produce a sufficiently confident detection for the requested condition.",
            "relevant_detections": [],
            "guardrail_triggered": True
        }
        
    question_lower = question.lower()
    
    # Simple mapping of questions to expected classes
    relevant_classes = []
    if "damage" in question_lower:
        relevant_classes.append("Physical Damage")
    if "defective" in question_lower:
        relevant_classes.append("Defective")
    if "dust" in question_lower or "dusty" in question_lower:
        relevant_classes.append("Dusty")
    if "snow" in question_lower:
        relevant_classes.append("Snow")
    if "bird" in question_lower:
        relevant_classes.append("Bird Drop")
        
    # If no specific faults mentioned, consider all detections relevant
    if not relevant_classes: 
        relevant_classes = list(detections_data["counts"].keys())
        
    relevant_detections = [
        d for d in detections_data["detections"] 
        if d["class_name"] in relevant_classes
    ]
    
    # GUARDRAIL TRIGGER
    if not relevant_detections:
        return {
            "question": question,
            "intent": intent,
            "answer": "Insufficient information from the detector to answer reliably. The detector did not produce a sufficiently confident detection for the requested condition.",
            "relevant_detections": [],
            "guardrail_triggered": True
        }
        
    # Generate explicit answer
    counts = {}
    highest_conf = 0.0
    for d in relevant_detections:
        c = d["class_name"]
        counts[c] = counts.get(c, 0) + 1
        if d["confidence"] > highest_conf:
            highest_conf = d["confidence"]
            
    if "how many" in question_lower:
        counts_str = ", ".join([f"{count} {cls}" for cls, count in counts.items()])
        answer = f"I found {counts_str} in the image."
    else:
        classes_str = " and ".join(counts.keys())
        answer = f"{classes_str} was detected with {highest_conf:.2f} confidence."
        
    return {
        "question": question,
        "intent": intent,
        "answer": answer,
        "relevant_detections": relevant_detections,
        "guardrail_triggered": False
    }
