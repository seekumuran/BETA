import argparse
import cv2
from wildlife_robustness.augmentations import apply_degradation, degradation_names

def main():
    parser = argparse.ArgumentParser(description="Apply a synthetic camera degradation.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--type", required=True, choices=degradation_names())
    parser.add_argument("--severity", choices=["low", "medium", "high"], default="medium")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    image = cv2.imread(args.input)
    if image is None:
        raise SystemExit(f"Could not read input image: {args.input}")
    result = apply_degradation(image, args.type, args.severity, args.seed)
    if not cv2.imwrite(args.output, result):
        raise SystemExit(f"Could not write output image: {args.output}")
    print(f"Saved {args.type}/{args.severity} preview to {args.output}")

if __name__ == "__main__":
    main()
