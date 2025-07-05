#!/usr/bin/env python3
import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a YOLOe model using Ultralytics")
    parser.add_argument("dataset", type=Path, help="Path to dataset directory")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--img-size", type=int, default=640, help="Training image size")
    parser.add_argument("--lr", type=float, default=0.01, help="Learning rate")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.dataset.exists():
        raise SystemExit(f"Dataset path {args.dataset} does not exist")

    dataset_yaml = args.dataset / "data.yaml"
    if not dataset_yaml.exists():
        raise SystemExit(f"Dataset config {dataset_yaml} does not exist")

    from ultralytics import YOLO

    model = YOLO("yolov8e.yaml")
    model.train(
        data=str(dataset_yaml),
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.img_size,
        lr0=args.lr,
    )


if __name__ == "__main__":
    main()