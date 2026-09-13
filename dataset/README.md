# SolarSight Dataset Information

**Dataset Source:**
- **Name:** Solar Panel Fault Dataset New
- **Publisher/Creator:** 6rianstorm
- **Platform:** Roboflow Universe
- **URL:** [https://universe.roboflow.com/6rianstorm/solar-panel-fault-dataset-new](https://universe.roboflow.com/6rianstorm/solar-panel-fault-dataset-new)

The original public v2 dataset contains 8,730 images at 640x640 resolution, featuring both YOLO detection bounding boxes and polygon segmentation annotations.

## Local Preparation
For this repository, the dataset was independently processed:
- Segmentation polygons were explicitly converted into axis-aligned YOLO bounding boxes to standardize the RT-DETR-L training pipeline.
- The 8,730 images were divided into:
  - **Train:** 7,669 images
  - **Validation:** 611 images
  - **Test:** 450 images

**Split Strategy Justification:**
The large training partition (approx. 88%) was chosen to preserve maximum variance and examples for fine-tuning the model, ensuring it sees enough diverse representations of highly variable classes (like Snow and Dusty), while still maintaining strictly independent validation and held-out test partitions.

*Note: Due to size constraints, the actual image/label files are excluded from this repository via `.gitignore`.*
