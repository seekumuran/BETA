"""Materialize a stochastic camera-failure training view.

This samples a degradation once per source image and writes the resulting
training dataset to disk. It approximates the manuscript's per-image 0.5
augmentation probability, but is NOT online/on-the-fly augmentation.
"""
import argparse, random
from pathlib import Path
from wildlife_robustness.data.yolo_dataset import (
    read_dataset_yaml, image_files, label_for, write_dataset_yaml
)
from wildlife_robustness.augmentations import apply_degradation, degradation_names
import cv2, shutil

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True, help="Original YOLO dataset YAML")
    p.add_argument("--output", required=True, help="Output dataset directory")
    p.add_argument("--probability", type=float, default=0.5)
    p.add_argument("--severity", choices=["low","medium","high"], default=None,
                   help="If omitted, sample severity uniformly per selected image")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    if not 0 <= args.probability <= 1:
        p.error("--probability must be between 0 and 1")
    source, base, names = read_dataset_yaml(args.data)
    rng = random.Random(args.seed)
    out = Path(args.output).resolve()
    for split in ("train", "val", "test"):
        if split not in source:
            raise ValueError(f"Dataset YAML missing {split}")
        image_root = Path(source[split])
        if not image_root.is_absolute():
            image_root = (base / image_root).resolve()
        label_root = base / "labels" / split
        dest_images, dest_labels = out / "images" / split, out / "labels" / split
        files = image_files(image_root)
        if not files:
            raise FileNotFoundError(f"No images in {image_root}")
        degraded = 0
        for idx, src in enumerate(files):
            rel = src.relative_to(image_root)
            dst_img = dest_images / rel
            dst_lbl = dest_labels / rel.with_suffix(".txt")
            dst_img.parent.mkdir(parents=True, exist_ok=True)
            dst_lbl.parent.mkdir(parents=True, exist_ok=True)
            image = cv2.imread(str(src), cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError(f"Cannot read {src}")
            if split == "train" and rng.random() < args.probability:
                fault = rng.choice(degradation_names()[:-1])
                severity = args.severity or rng.choice(["low", "medium", "high"])
                image = apply_degradation(image, fault, severity, seed=args.seed + idx)
                degraded += 1
            if not cv2.imwrite(str(dst_img), image):
                raise RuntimeError(f"Could not write {dst_img}")
            src_lbl = label_for(src, image_root, label_root)
            if not src_lbl.exists():
                raise FileNotFoundError(f"Missing annotation {src_lbl}")
            shutil.copy2(src_lbl, dst_lbl)
        print(f"{split}: {len(files)} images; {degraded} degraded")
    yaml_path = out / "dataset.yaml"
    write_dataset_yaml(yaml_path, out/"images/train", out/"images/val", out/"images/test", names)
    print(f"Created {yaml_path}")

if __name__ == "__main__":
    main()
