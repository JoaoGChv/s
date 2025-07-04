#!/usr/bin/env python3
import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a GroundingDINO model")
    parser.add_argument("dataset", type=Path, help="Path to dataset directory")
    parser.add_argument("--config", type=Path, default=None, help="Model config file")
    parser.add_argument("--epochs", type=int, default=30, help="Number of training epochs")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.dataset.exists():
        raise SystemExit(f"Dataset path {args.dataset} does not exist")

    # Placeholder: integrate with GroundingDINO training routine.
    # from groundingdino.engine import Trainer
    # trainer = Trainer(args.config, data_path=args.dataset, epochs=args.epochs, lr=args.lr)
    # trainer.train()

    print("[Placeholder] Training GroundingDINO with parameters:")
    for k, v in vars(args).items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()