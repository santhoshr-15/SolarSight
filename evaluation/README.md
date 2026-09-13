# SolarSight Evaluation Reproduction

This directory contains scripts and artifacts for evaluating the trained model.

## Evaluation Script
`evaluate.py` reproduces the validation and test evaluation metrics for the RT-DETR-L model.

### How to use
Evaluate on the test set:
```bash
python evaluate.py --model ../model/best.pt --data /path/to/dataset.yaml --split test
```

Evaluate on the validation set:
```bash
python evaluate.py --model ../model/best.pt --data /path/to/dataset.yaml --split val
```

**Original Test Metrics:**
- Precision: ~0.4423
- Recall: ~0.5144
- mAP50: ~0.4237
- mAP50-95: ~0.2707

## Evaluation Results
The `results/` folder contains the PR curves, metrics, and batch prediction visualizations from the original model evaluation.
