import os
import cv2
import numpy as np
from ultralytics import RTDETR
from pathlib import Path
import logging
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Robust model path resolution relative to this file
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = str(PROJECT_ROOT / "model" / "best.pt")

class SolarDetector:
    def __init__(self):
        self.model = None
        
    def load_model(self):
        if self.model is None:
            logger.info(f"Loading RT-DETR-L model from {MODEL_PATH}")
            self.model = RTDETR(MODEL_PATH)
            logger.info("Model loaded successfully.")
        
    def detect(self, image_bytes: bytes, conf: float = 0.50):
        self.load_model()
        # Read image
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Inference
        results = self.model.predict(image, conf=conf)
        
        detections = []
        counts = {}
        
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
                
            for box in boxes:
                cls_id = int(box.cls[0].item())
                class_name = self.model.names[cls_id]
                confidence = float(box.conf[0].item())
                coords = box.xyxy[0].tolist()
                
                det = {
                    "class_id": cls_id,
                    "class_name": class_name,
                    "confidence": confidence,
                    "bounding_box": {
                        "x1": coords[0],
                        "y1": coords[1],
                        "x2": coords[2],
                        "y2": coords[3]
                    }
                }
                detections.append(det)
                counts[class_name] = counts.get(class_name, 0) + 1
                
        return {
            "success": True,
            "detections": detections,
            "counts": counts,
            "total_detections": len(detections)
        }

# Singleton-like instantiation for FastAPI
detector_instance = None

def get_detector():
    global detector_instance
    if detector_instance is None:
        detector_instance = SolarDetector()
    return detector_instance
