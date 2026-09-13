import argparse
from ultralytics import RTDETR

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate SolarSight RT-DETR-L Model")
    parser.add_argument("--model", type=str, required=True, help="Path to trained model (e.g., ../model/best.pt)")
    parser.add_argument("--data", type=str, required=True, help="Path to dataset YAML file")
    parser.add_argument("--split", type=str, default="test", help="Dataset split to evaluate on (val, test)")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size (default: 640)")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold (default: 0.25)")
    parser.add_argument("--project", type=str, default="results", help="Project output directory")
    parser.add_argument("--name", type=str, default="eval", help="Experiment name")
    return parser.parse_args()

def main():
    """
    SolarSight Evaluation Reproduction Script
    
    This script evaluates the trained RT-DETR-L model on the specified dataset split.
    Original test results:
    - Precision: ~0.4423
    - Recall: ~0.5144
    - mAP50: ~0.4237
    - mAP50-95: ~0.2707
    """
    args = parse_args()

    print(f"Loading model from: {args.model}")
    model = RTDETR(args.model)

    print(f"Starting evaluation on split: {args.split}")
    
    # Run evaluation
    metrics = model.val(
        data=args.data,
        split=args.split,
        imgsz=args.imgsz,
        conf=args.conf,
        project=args.project,
        name=args.name,
        exist_ok=True
    )

    # Print the specific metrics requested
    # Metrics object has 'results_dict' in recent ultralytics versions
    res = metrics.results_dict
    
    print("\n--- Evaluation Metrics ---")
    print(f"Precision: {res.get('metrics/precision(B)', 0.0):.4f}")
    print(f"Recall:    {res.get('metrics/recall(B)', 0.0):.4f}")
    print(f"mAP50:     {res.get('metrics/mAP50(B)', 0.0):.4f}")
    print(f"mAP50-95:  {res.get('metrics/mAP50-95(B)', 0.0):.4f}")
    print("--------------------------")
    
    print(f"\nEvaluation complete. Results saved to {args.project}/{args.name}")

if __name__ == "__main__":
    main()
