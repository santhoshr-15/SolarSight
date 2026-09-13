# SolarSight Training Reproduction

This directory contains scripts and artifacts for reproducing the model training.

## Training Script
`train.py` allows you to reproduce the RT-DETR-L model training on the SolarSight dataset.

**Note:** The already trained model weights are located at `../model/best.pt`. You do **not** need to run training to use the FastAPI application or perform inference.

### How to use
Run the script using the following command (requires the dataset YAML configuration):
```bash
python train.py --data /path/to/dataset.yaml
```

**Original Hyperparameters:**
- Model: RT-DETR-L
- Epochs: 20
- Batch size: 8
- Image size: 640
- Optimizer: AdamW
- Seed: 42
- AMP: True

## Training Results
The `results/` folder contains metrics, graphs, and confusion matrices generated during the original training run.
