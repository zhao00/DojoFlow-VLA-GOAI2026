#!/usr/bin/env python3
"""Extract DojoFlow-VLA scalar history from an offline W&B record into CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from wandb.proto import wandb_internal_pb2
from wandb.sdk.internal.datastore import DataStore


TRAIN_KEYS = ["train/iter", "train/epoch_f", "train/loss", "train/lr"]
VAL_KEYS = ["val/iter", "val/epoch_f", "val/loss", "val/angle dist"]


def write_csv(path: Path, rows: list[dict], keys: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        writer.writerows({key: row.get(key) for key in keys} for row in rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("wandb_file", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("results/metrics"))
    args = parser.parse_args()

    store = DataStore()
    store.open_for_scan(str(args.wandb_file))
    train_rows: list[dict] = []
    val_rows: list[dict] = []

    while True:
        payload = store.scan_data()
        if payload is None:
            break
        record = wandb_internal_pb2.Record()
        record.ParseFromString(payload)
        if record.WhichOneof("record_type") != "history":
            continue

        row: dict = {}
        for item in record.history.item:
            key = item.key or ".".join(item.nested_key)
            try:
                row[key] = json.loads(item.value_json)
            except json.JSONDecodeError:
                row[key] = item.value_json

        if row.get("train/iter") is not None:
            train_rows.append(row)
        if row.get("val/iter") is not None:
            val_rows.append(row)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "training_metrics.csv", train_rows, TRAIN_KEYS)
    write_csv(args.output_dir / "validation_metrics.csv", val_rows, VAL_KEYS)
    print(f"training rows: {len(train_rows)}")
    print(f"validation rows: {len(val_rows)}")


if __name__ == "__main__":
    main()
