# SolarSight
Solar panel fault detection and constrained visual reasoning API using RT-DETR-L.

## 1. Project Overview
SolarSight is an intelligent inspection API designed to detect faults in solar panels and answer natural-language questions about them. The system uses a fine-tuned RT-DETR-L object detection model to identify various panel conditions and faults. Instead of using an unconstrained LLM that might hallucinate or directly guess from an image, SolarSight features a strict, constrained reasoning endpoint. It processes questions, routes them by intent, runs the detector only when visual information is required, and reasons exclusively over the structured detector output. It features a strict confidence and insufficient-information guardrail to prevent hallucination.

## 2. Detected Classes
The model was trained on a domain-specific dataset (non-COCO) to detect six distinct classes:
1. Bird Drop
2. Defective
3. Dusty
4. Non Defective
5. Physical Damage
6. Snow

## 3. System Architecture
SolarSight's reasoning capabilities operate through a strict, deterministic pipeline:

`Image` &rarr; `RT-DETR-L Detector` &rarr; `Structured Detections (class, confidence, bounding box, counts)` &rarr; `Reasoning / Intent Router` &rarr; `Natural-Language Answer`

When a user submits a question via the `/reason` endpoint, the system uses an intent router to determine whether visual detection is required. If detection is required, it invokes the detector and reasons *only* over the structured result. 

*(Note: This is a plain Python deterministic implementation. This is **not** an autonomous LLM agent.)*

## 4. Dataset
**Dataset Source:** [Solar Panel Fault Dataset New](https://universe.roboflow.com/6rianstorm/solar-panel-fault-dataset-new) by 6rianstorm (Roboflow Universe).

The original public v2 dataset contains 8,730 images at 640x640 resolution, featuring both YOLO detection bounding boxes and polygon segmentation annotations. To standardize our local pipeline, segmentation polygons were successfully converted into axis-aligned YOLO bounding boxes. We did not create the original annotations.

**Corrected Dataset Statistics (8,730 total):**
- **Train:** 7,669 images (41,014 objects)
- **Validation:** 611 images (3,453 objects)
- **Test:** 450 images (2,796 objects)

**Split Strategy Justification:** The large training partition preserves maximum examples for fine-tuning—critical for capturing the visual variance of amorphous classes like Snow and Dusty—while still maintaining independent validation and held-out test partitions.

The dataset contains exactly 6 classes with no missing images/labels and no invalid objects after conversion. 
*Note: Due to file size and licensing constraints, the dataset itself is excluded from this GitHub repository. The `.gitignore` prevents it from being committed.*

## 5. Training
The model was fine-tuned on the dataset using the following configuration:
- **Model:** RT-DETR-L (Starting checkpoint: `rtdetr-l.pt`)
- **Epochs:** 20
- **Image size:** 640
- **Batch size:** 8
- **Optimizer:** AdamW
- **Seed:** 42
- **AMP:** Enabled
- **Hardware:** NVIDIA Tesla T4
- **Environment:** Ultralytics v8.4.150, PyTorch 2.11.0+cu128, Python 3.13.15
- **Training time:** ~3.066 hours

The best checkpoint was selected based on validation performance and is stored at `model/best.pt`.

## 6. Evaluation Results

The model's performance on the held-out sets:

**Validation:**
- Precision: 52.9%
- Recall: 56.0%
- mAP50: 51.1%
- mAP50-95: 34.8%

**Test (Held-out):**
- Precision: 44.23%
- Recall: 51.44%
- mAP50: 42.37%
- mAP50-95: 27.07%

**Per-Class Test Metrics:**

| Class | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| Bird Drop | 50.2% | 24.7% | 28.2% | 9.3% |
| Defective | 43.2% | 69.7% | 55.9% | 48.5% |
| Dusty | 34.2% | 58.7% | 47.8% | 34.1% |
| Non Defective | 37.4% | 59.2% | 42.3% | 30.2% |
| Physical Damage | 62.3% | 47.2% | 45.8% | 20.7% |
| Snow | 38.1% | 49.1% | 34.2% | 19.7% |

## 7. Failure Cases and Limitations
While the model successfully identifies various conditions, it is not a perfect inspection system and has known limitations:
- **Recall Issues:** Certain classes, such as *Bird Drop*, exhibit relatively low recall.
- **Ambiguity:** Visually similar or compounding categories can produce overlapping detections. For example, real-world qualitative testing showed a strong *Physical Damage* detection alongside multiple *Defective* detections on the same area, demonstrating semantic ambiguity.
- **Qualitative vs Quantitative:** The provided real-world sample (`test/sample_images/real_world_solar_test.png`) is qualitative only; it does not represent a quantitative accuracy measurement as it lacks ground-truth annotation.
- **Thresholding:** Confidence thresholding reduces weak/duplicate detections, but cannot completely eliminate semantic ambiguity.

**Reasoning Guardrail:** 
To prevent hallucination, the API implements a strict guardrail. When detector evidence is empty, below the confidence threshold, or ambiguous, the API explicitly returns:
> *"Insufficient information from the detector to answer reliably."*

## 8. API

### `GET /health`
Returns the status of the API and the loaded model.
```bash
curl http://127.0.0.1:8000/health
```
**Response:** 
```json
{
  "status": "ok",
  "model": "RT-DETR-L"
}
```

### `POST /detect`
Accepts an image and an optional confidence threshold, returning structured detections.
```bash
curl -X POST "http://127.0.0.1:8000/detect" \
  -F "file=@test\sample_images\real_world_solar_test.png" \
  -F "conf=0.50"
```
**Response:**
```json
{
  "success": true,
  "detections": [
    {
      "class_id": 4,
      "class_name": "Physical Damage",
      "confidence": 0.72,
      "bounding_box": {
        "x1": 142,
        "y1": 205,
        "x2": 450,
        "y2": 512
      }
    }
  ],
  "counts": {
    "Physical Damage": 1
  },
  "total_detections": 1
}
```

### `POST /reason`
Accepts an image and a natural-language question. It routes the intent, extracts visual detections if necessary, applies guardrails, and answers the question.

**Example A: Successful visual question**
```bash
curl -X POST "http://127.0.0.1:8000/reason" \
  -F "question=How many dusty panels are visible?" \
  -F "file=@test\sample_images\real_world_solar_test.png"
```
**Response:**
```json
{
  "question": "How many dusty panels are visible?",
  "intent": "visual_detection_required",
  "answer": "Based on the visual analysis, I found 2 Dusty instances.",
  "relevant_detections": [
    {"class_name": "Dusty", "confidence": 0.81, "bounding_box": {"x1": 10, "y1": 20, "x2": 100, "y2": 100}},
    {"class_name": "Dusty", "confidence": 0.76, "bounding_box": {"x1": 200, "y1": 150, "x2": 300, "y2": 250}}
  ],
  "guardrail_triggered": false
}
```

**Example B: Insufficient information (Guardrail triggered)**
```bash
curl -X POST "http://127.0.0.1:8000/reason" \
  -F "question=Is there damage?" \
  -F "file=@test\sample_images\real_world_solar_test.png" \
  -F "conf=0.95"
```
*(Detector finds nothing above 0.95 confidence)*
**Response:**
```json
{
  "question": "Is there damage?",
  "intent": "visual_detection_required",
  "answer": "Insufficient information from the detector to answer reliably.",
  "relevant_detections": [],
  "guardrail_triggered": true
}
```

**Example C: Non-visual/general question**
```bash
curl -X POST "http://127.0.0.1:8000/reason" \
  -F "question=What is a solar panel?"
```
*(Detector inference is skipped)*
**Response:**
```json
{
  "question": "What is a solar panel?",
  "intent": "general_question",
  "answer": "This is a general knowledge question that does not require visual inspection. Solar panels convert sunlight into electricity...",
  "relevant_detections": [],
  "guardrail_triggered": false
}
```

## 9. Running Locally

**1. Set up the environment:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**2. Start the API:**
```powershell
$env:PYTHONPATH="."
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**3. API Documentation:**
Interactive Swagger documentation is automatically available at: `http://127.0.0.1:8000/docs`

## 10. Testing
The project includes a robust, headless unit test suite that does not require a GPU or load the actual model weights (the detector is mocked for speed and stability).

Run the tests:
```powershell
$env:PYTHONPATH="."
pytest -v
```
**Result:** 14 passed, 0 failed, 1 skipped.

**Integration Test:**
To test the *actual* model inference against the sample image (requires the `best.pt` model and runtime dependencies), run the separated integration test:
```powershell
$env:PYTHONPATH="."
pytest -m integration -v
```

## 11. Reproducibility
The ML workflow is highly reproducible. Please refer to:
- `training/train.py` & `training/README.md`
- `evaluation/evaluate.py` & `evaluation/README.md`
- `SolarSight_Training_Evaluation.ipynb`
- `training/results/` and `evaluation/results/` (Original recorded artifacts)

These artifacts provide the exact commands and hyperparameter configurations used to train the model.

## 12. Repository Structure
```text
SolarSight/
├── app/                                    # FastAPI application & logic
├── dataset/                                # Dataset documentation
├── docs/                                   # Project memos and PDFs
├── evaluation/                             # Evaluation scripts and metric plots
├── model/                                  # Trained weights (best.pt)
├── test/                                   # Sample images for testing
├── training/                               # Training scripts and curves
├── tests/                                  # Pytest unit & integration tests
├── collect_artifacts.py                    # Colab artifact extraction script
├── Dockerfile                              # Containerization configuration
├── requirements.txt                        # API dependencies
├── SolarSight_Training_Evaluation.ipynb    # Original ML workflow notebook
└── README.md                               # Project documentation
```

## 13. Constraints Followed
- **Model:** RT-DETR used for object detection.
- **Dataset:** Custom domain dataset utilized, featuring non-COCO/domain-specific classes.
- **API:** FastAPI API successfully implemented.
- **Reasoning:** Constrained Python reasoning layer implemented based purely on structured detections.
- **No Agentic Frameworks:** LangChain, LangGraph, CrewAI, AutoGen, or similar agentic frameworks were explicitly **NOT** used.
- **No AutoML:** No-code training or AutoML was completely avoided.
- **Reproducibility:** Standalone reproducible training and evaluation scripts are included.

## 14. Submission Checklist
- [x] Source code (FastAPI, Detector, Reasoning)
- [x] Model weights (`model/best.pt`)
- [x] Training code (`training/train.py`)
- [x] Evaluation code (`evaluation/evaluate.py`)
- [x] FastAPI endpoints (`/health`, `/detect`)
- [x] Reasoning endpoint (`/reason` with guardrails)
- [x] Tests (Unit tests passed; Integration test separated)
- [x] Reproducibility documentation (READMEs included)
- [x] Evaluation artifacts (Curves, plots, matrices)
- [ ] 2-page memo (`docs/memo.pdf` - Pending generation/inclusion)
