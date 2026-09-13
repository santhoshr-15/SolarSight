import argparse
from ultralytics import RTDETR

def parse_args():
    parser = argparse.ArgumentParser(description="Reproduce SolarSight RT-DETR-L Training")
    parser.add_argument("--data", type=str, required=True, help="Path to dataset YAML file")
    parser.add_argument("--epochs", type=int, default=20, help="Number of epochs (default: 20)")
    parser.add_argument("--batch", type=int, default=8, help="Batch size (default: 8)")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size (default: 640)")
    parser.add_argument("--device", type=str, default="0", help="CUDA device index or 'cpu' (default: '0')")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--project", type=str, default="results", help="Project output directory")
    parser.add_argument("--name", type=str, default="rtdetr_l_solar", help="Experiment name")
    return parser.parse_args()

def main():
    """
    SolarSight Training Reproduction Script
    
    NOTE: The trained model is already available at `../model/best.pt`.
    This script is provided solely for reproducibility of the original 
    training run and is not required for inference or the final FastAPI app.
    
    Original hyperparameters:
    - Model: RT-DETR-L
    - Epochs: 20
    - Batch size: 8
    - Image size: 640
    - Optimizer: AdamW
    - Seed: 42
    - AMP: True
    """
    args = parse_args()

    print(f"Starting RT-DETR-L training for SolarSight...")
    print(f"Dataset: {args.data}")
    print(f"Hyperparameters: epochs={args.epochs}, batch={args.batch}, imgsz={args.imgsz}, seed={args.seed}")

    # Initialize the model (using the pretrained ultralytics model)
    model = RTDETR("rtdetr-l.pt")

    # Train the model
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=args.device,
        seed=args.seed,
        optimizer="AdamW",
        amp=True,
        project=args.project,
        name=args.name,
        exist_ok=True
    )

    print(f"\nTraining complete! Results saved to {args.project}/{args.name}")

if __name__ == "__main__":
    main()
