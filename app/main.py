from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import io
import cv2
import numpy as np
from PIL import Image
from app.detector import get_detector
from app.reasoning import route_intent, reason_over_detections
import logging

# Configure standard Python logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SolarSight API", description="Constrained object detection and reasoning API")

frontend_origin = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_origin, 
        "http://localhost:3000",
        "http://localhost:5173",
        "https://solar-sight-mu.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    logger.info("Health check requested.")
    return {"status": "ok", "model": "RT-DETR-L"}

@app.post("/detect")
async def detect(file: UploadFile = File(...), conf: float = Form(0.50)):
    logger.info(f"Received detection request for file: {file.filename} with conf: {conf}")
    if not file.content_type.startswith("image/"):
        logger.warning(f"Invalid file type submitted: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    try:
        contents = await file.read()
        detector = get_detector()
        result = detector.detect(contents, conf=conf)
        logger.info(f"Detection successful. Found {result.get('total_detections', 0)} objects.")
        return result
        
    except Exception as e:
        logger.error(f"Error during detection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reason")
async def reason(
    question: str = Form(...),
    file: UploadFile = File(None),
    conf: float = Form(0.50)
):
    logger.info(f"Received reasoning request. Question: '{question}'")
    intent = route_intent(question)
    logger.info(f"Routed intent: {intent}")
    
    if intent in ("GENERAL_KNOWLEDGE", "UNSUPPORTED"):
        return reason_over_detections(question, {"total_detections": 0, "detections": [], "counts": {}})
        
    if not file:
        logger.warning("Visual reasoning requested but no image file was provided.")
        raise HTTPException(status_code=400, detail="An image file is required for visual questions.")
        
    if not file.content_type.startswith("image/"):
        logger.warning(f"Invalid file type submitted for reasoning: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
        
    try:
        contents = await file.read()

        # Extract image dimensions for spatial location queries
        img = Image.open(io.BytesIO(contents))
        img_width, img_height = img.size

        detector = get_detector()
        detections = detector.detect(contents, conf=conf)

        # Inject image dimensions into detections data for location reasoning
        detections["image_width"] = img_width
        detections["image_height"] = img_height
        
        reasoning_result = reason_over_detections(question, detections)
        if reasoning_result.get("guardrail_triggered"):
            logger.warning("Reasoning guardrail triggered (insufficient information).")
        else:
            logger.info("Reasoning completed successfully.")
            
        return reasoning_result
        
    except Exception as e:
        logger.error(f"Error during reasoning: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
