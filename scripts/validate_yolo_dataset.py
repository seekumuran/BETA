import argparse
from pathlib import Path
from wildlife_robustness.data.yolo_dataset import read_dataset_yaml, image_files, label_for

def main():
    p = argparse.ArgumentParser(description="Validate YOLO dataset structure and labels.")
    p.add_argument("--data", required=True, help="Dataset YAML")
    args = p.parse_args()
    data, base, names = read_dataset_yaml(args.data)
    errors, total_images, total_boxes = [], 0, 0
    for split in ("train", "val", "test"):
        if split not in data:
            print(f"WARNING: no '{split}' split configured")
            continue
        image_root = Path(data[split])
        if not image_root.is_absolute():
            image_root = base / image_root
        label_root = base / "labels" / split
        images = image_files(image_root)
        boxes = 0
        for image in images:
            label = label_for(image, image_root, label_root)
            if not label.exists():
                errors.append(f"Missing label: {label}")
                continue
            for line_no, line in enumerate(label.read_text().splitlines(), 1):
                parts = line.split()
                if len(parts) != 5:
                    errors.append(f"{label}:{line_no}: expected 5 YOLO fields")
                    continue
                try:
                    cls, x, y, w, h = int(float(parts[0])), *map(float, parts[1:])
                    if cls not in names or not all(0 <= v <= 1 for v in (x, y, w, h)) or w <= 0 or h <= 0:
                        errors.append(f"{label}:{line_no}: invalid class/normalized box")
                    else:
                        boxes += 1
                except ValueError:
                    errors.append(f"{label}:{line_no}: non-numeric annotation")
        print(f"{split}: {len(images)} images, {boxes} boxes, labels={label_root}")
        total_images += len(images)
        total_boxes += boxes
    print(f"Total: {total_images} images, {total_boxes} boxes, {len(names)} classes")
    if errors:
        print(f"\nFound {len(errors)} problem(s):")
        for e in errors[:50]:
            print(" -", e)
        raise SystemExit(1)
    print("Dataset validation passed.")

if __name__ == "__main__":
    main()
