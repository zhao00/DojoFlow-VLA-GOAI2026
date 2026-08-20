#!/usr/bin/env python3
"""Render static, reviewer-friendly figures from extracted W&B CSV files."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def read_columns(path: Path, x_key: str, y_key: str) -> tuple[np.ndarray, np.ndarray]:
    xs: list[float] = []
    ys: list[float] = []
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if row.get(x_key) and row.get(y_key):
                xs.append(float(row[x_key]))
                ys.append(float(row[y_key]))
    return np.asarray(xs), np.asarray(ys)


def ema(values: np.ndarray, alpha: float = 0.08) -> np.ndarray:
    if values.size == 0:
        return values
    output = np.empty_like(values)
    output[0] = values[0]
    for index in range(1, values.size):
        output[index] = alpha * values[index] + (1 - alpha) * output[index - 1]
    return output


def save_train_loss(metrics: Path, output: Path) -> None:
    x, y = read_columns(metrics, "train/iter", "train/loss")
    fig, axis = plt.subplots(figsize=(8.5, 4.8))
    axis.plot(x, y, color="#93b7dc", alpha=0.35, linewidth=0.7, label="raw")
    axis.plot(x, ema(y), color="#1f5a94", linewidth=1.8, label="EMA")
    axis.set(title="DojoFlow-VLA training loss", xlabel="Training iteration", ylabel="Flow-matching loss")
    axis.grid(alpha=0.25)
    axis.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def save_line(metrics: Path, x_key: str, y_key: str, title: str, ylabel: str, output: Path) -> None:
    x, y = read_columns(metrics, x_key, y_key)
    fig, axis = plt.subplots(figsize=(8.5, 4.8))
    axis.plot(x, y, marker="o" if len(x) < 100 else None, markersize=2.5, linewidth=1.5, color="#1f5a94")
    axis.set(title=title, xlabel="Training iteration", ylabel=ylabel)
    axis.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics-dir", type=Path, default=Path("results/metrics"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/figures"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    train = args.metrics_dir / "training_metrics.csv"
    val = args.metrics_dir / "validation_metrics.csv"
    save_train_loss(train, args.output_dir / "train_loss.png")
    save_line(train, "train/iter", "train/lr", "Learning-rate schedule", "Learning rate", args.output_dir / "learning_rate.png")
    save_line(val, "val/iter", "val/loss", "Offline proxy validation loss", "Flow-matching loss", args.output_dir / "val_loss.png")
    save_line(val, "val/iter", "val/angle dist", "Offline proxy action distance", "Normalized action L1", args.output_dir / "val_action_distance.png")
    print(f"figures written to {args.output_dir}")


if __name__ == "__main__":
    main()
