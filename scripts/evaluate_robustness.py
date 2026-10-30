"""Evaluate a trained YOLO model on clean and fixed degraded test sets."""
import argparse, csv, random, shutil
from pathlib import Path
import cv2
from ultralytics import YOLO
from wildlife_robustness.augmentations import apply_degradation, degradation_names
from wildlife_robustness.data.yolo_dataset import read_dataset_yaml, image_files, label_for, write_dataset_yaml
from wildlife_robustness.evaluation.robustness import absolute_drop, relative_retention

def make_condition(data_yaml, out_dir, fault, severity, seed):
    data, base, names = read_dataset_yaml(data_yaml)
    image_root = Path(data["test"])
    if not image_root.is_absolute():
        image_root = (base / image_root).resolve()
    label_root = base / "labels" / "test"
    out_dir = Path(out_dir).resolve()
    out_images, out_labels = out_dir/"images/test", out_dir/"labels/test"
    for idx, src in enumerate(image_files(image_root)):
        rel = src.relative_to(image_root)
        dst = out_images/rel
        dst_lbl = out_labels/rel.with_suffix(".txt")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst_lbl.parent.mkdir(parents=True, exist_ok=True)
        image = cv2.imread(str(src), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Cannot read {src}")
        image = apply_degradation(image, fault, severity, seed + idx)
        cv2.imwrite(str(dst), image)
        shutil.copy2(label_for(src, image_root, label_root), dst_lbl)
    # YOLO only needs test path for this evaluation dataset; val is set to same path.
    yaml_path = out_dir/"dataset.yaml"
    write_dataset_yaml(yaml_path, out_images, out_images, out_images, names)
    return yaml_path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--weights", required=True)
    p.add_argument("--data", required=True)
    p.add_argument("--output", default="runs/robustness_eval")
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--batch", type=int, default=16)
    p.add_argument("--device", default="cpu")
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--include-combined", action="store_true")
    args = p.parse_args()
    model = YOLO(args.weights)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    clean = model.val(data=args.data, split="test", imgsz=args.imgsz, batch=args.batch,
                     device=args.device, project=str(out), name="clean", exist_ok=True)
    clean_map = float(clean.box.map)
    rows.append({"condition":"clean","severity":"none","mAP50":float(clean.box.map50),
                 "mAP50_95":clean_map,"precision":float(clean.box.mp),"recall":float(clean.box.mr)})
    faults = degradation_names() if args.include_combined else degradation_names()[:-1]
    for fault in faults:
        for severity in ("low","medium","high"):
            condition_dir = out/"datasets"/f"{fault}_{severity}"
            condition_yaml = make_condition(args.data, condition_dir, fault, severity,
                                            args.seed + len(rows)*100000)
            metrics = model.val(data=str(condition_yaml), split="test", imgsz=args.imgsz,
                                batch=args.batch, device=args.device, project=str(out),
                                name=f"{fault}_{severity}", exist_ok=True)
            score = float(metrics.box.map)
            rows.append({"condition":fault,"severity":severity,"mAP50":float(metrics.box.map50),
                         "mAP50_95":score,"precision":float(metrics.box.mp),"recall":float(metrics.box.mr),
                         "absolute_drop":absolute_drop(clean_map, score),
                         "relative_retention":relative_retention(clean_map, score)})
            print(f"{fault:20s} {severity:6s} mAP50-95={score:.4f}")
    csv_path = out/"robustness_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sorted({k for row in rows for k in row}))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Clean mAP50-95: {clean_map:.4f}")
    print(f"Results: {csv_path}")

if __name__ == "__main__":
    main()
