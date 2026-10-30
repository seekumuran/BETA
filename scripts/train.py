import argparse, json
from pathlib import Path
from ultralytics import YOLO

def main():
    p = argparse.ArgumentParser(description="Train a YOLOv8 detector.")
    p.add_argument("--data", required=True, help="YOLO dataset YAML")
    p.add_argument("--model", default="yolov8n.pt")
    p.add_argument("--name", required=True)
    p.add_argument("--project", default="runs/wildlife")
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--batch", type=int, default=16)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--device", default="cpu", help="cpu, 0, 0,1, etc.")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--patience", type=int, default=10)
    args = p.parse_args()
    model = YOLO(args.model)
    results = model.train(
        data=args.data, epochs=args.epochs, imgsz=args.imgsz,
        batch=args.batch, seed=args.seed, deterministic=True,
        device=args.device, workers=args.workers, patience=args.patience,
        optimizer="SGD", momentum=0.937, weight_decay=0.0005,
        lr0=0.01, lrf=0.01, cos_lr=True,
        project=args.project, name=args.name, exist_ok=True,
    )
    save_dir = Path(results.save_dir)
    metadata = vars(args) | {"save_dir": str(save_dir), "weights": str(save_dir/"weights"/"best.pt")}
    (save_dir/"run_config.json").write_text(json.dumps(metadata, indent=2))
    print(f"Best weights: {save_dir/'weights'/'best.pt'}")

if __name__ == "__main__":
    main()
