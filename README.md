# Camera-Failure-Aware Data Augmentation for Robust Wildlife Detection

Research code accompanying the study **“Making Wildlife Detection Survive Bad Cameras: Camera-Failure-Aware Augmentation.”**

The project investigates whether synthetic camera-failure augmentation can improve YOLOv8n wildlife detection under degraded surveillance imagery and camera-location shift.

> **Reproducibility notice:** The original experiment machine is currently unavailable and the original training code/logs/checkpoints have not yet been recovered. This repository provides a reconstructed, runnable implementation. It does not establish that the manuscript's historical numerical results have been reproduced. Do not interpret a new run as reproducing the manuscript until the dataset version, location splits, training configuration, software versions and original artifacts have been verified.

## Research described in the manuscript

The manuscript reports a filtered Caltech Camera Traps subset with six classes (deer, wild boar, fox, coyote, raccoon and cattle), 17,000 images, 21,900 boxes and 85 camera locations. It reports location-based train/validation/test splits of 60/10/15 locations, respectively.

The proposed method applies synthetic camera degradations to training images and compares an unmodified YOLOv8n baseline with a failure-aware training condition.

### Camera degradation operators

| Operator | Simulated condition |
|---|---|
| Motion blur | Camera shake / motion during exposure |
| Sensor noise | Low-light gain noise |
| JPEG compression | Bandwidth-limited image streams |
| Dead pixels | Stuck black/white sensor pixels |
| Lens obstruction | Dirt, water drops or insects |
| Random occlusion | Foliage or objects blocking the view |
| Frame corruption | Corrupted horizontal bands / transmission errors |
| Combined | Random composition of two or three faults |

Each operator supports low, medium and high severity. The parameter ranges are in `configs/degradation.yaml`.

## Repository structure

```text
wildlife-robustness/
├── configs/
│   ├── degradation.yaml
│   └── experiment.yaml
├── docs/
│   ├── methodology.md
│   └── reproduction.md
├── scripts/
│   ├── apply_degradation.py
│   ├── validate_yolo_dataset.py
│   ├── build_training_dataset.py
│   ├── train.py
│   ├── evaluate_robustness.py
│   └── run_experiment.ps1
├── src/wildlife_robustness/
│   ├── augmentations/
│   ├── data/
│   └── evaluation/
├── tests/
├── CITATION.cff
├── LICENSE
├── pyproject.toml
└── requirements.txt
```

## Installation

Python 3.10 is recommended for compatibility with the Ultralytics version used in the manuscript.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
pip install "ultralytics==8.1.0"
```

For CPU-only execution, install a CPU-compatible PyTorch build appropriate for your Python and operating-system combination before installing Ultralytics if needed.

## Dataset format

The scripts expect a standard Ultralytics YOLO detection dataset with one label text file per image:

```text
dataset/
├── dataset.yaml
├── images/
│   ├── train/
│   ├── val/
│   └── test/
└── labels/
    ├── train/
    ├── val/
    └── test/
```

Each label row must use YOLO format:

```text
class_id x_center y_center width height
```

Coordinates must be normalized to `[0, 1]`. `dataset.yaml` must define `train`, `val`, `test`, and `names`. The image and label relative paths must correspond.

The manuscript's dataset filtering and camera-location split construction are not inferred automatically by these scripts. Prepare and verify the location-level split before training. The dataset itself is not included; follow the source dataset's access terms and attribution requirements.

Validate the dataset:

```powershell
python scripts/validate_yolo_dataset.py --data path/to/dataset.yaml
```

## Preview a camera failure

```powershell
python scripts/apply_degradation.py --input deer.jpg --output deer_blur.jpg --type motion_blur --severity high --seed 42
```

Replace `motion_blur` with `sensor_noise`, `jpeg`, `dead_pixels`, `lens_obstruction`, `random_occlusion`, `frame_corruption`, or `combined`.

## Train the baseline

```powershell
python scripts/train.py --data path/to/dataset.yaml --name baseline --device cpu
```

## Build a failure-aware training dataset

```powershell
python scripts/build_training_dataset.py --data path/to/dataset.yaml --output datasets/failure_aware --probability 0.5 --seed 42
```

This script materializes one sampled training view: each training image is degraded with the configured probability, otherwise it remains clean. Validation and test images are copied without degradation.

**Methodological distinction:** This implementation materializes augmentation before training. It is not on-the-fly augmentation at every epoch as described in the manuscript. Consequently, it is a reconstructed implementation variant and must not be described as an exact implementation of the historical method without further work.

## Train the failure-aware model

```powershell
python scripts/train.py --data datasets/failure_aware/dataset.yaml --name failure_aware --device cpu
```

## Evaluate robustness

```powershell
python scripts/evaluate_robustness.py --weights runs/wildlife/baseline/weights/best.pt --data path/to/dataset.yaml --output runs/eval_baseline --device cpu --include-combined
```

Run the same command with the failure-aware checkpoint and a different output directory. The script evaluates clean test data and each degradation/severity condition, then writes `robustness_results.csv`.

The test corruptions are generated deterministically from the supplied seed and image ordering. Preserve the generated datasets and configuration for auditability.

## Tests

```powershell
pip install pytest
pytest -q
```

## Metrics

The evaluation helpers calculate:

- Absolute drop: `clean_score - degraded_score`
- Relative retention: `degraded_score / clean_score`
- Mean absolute drop and mean relative retention across conditions

Ultralytics supplies detection metrics such as precision, recall, mAP@0.5 and mAP@0.5:0.95.

## Reported results in the manuscript

The manuscript reports clean mAP@0.5:0.95 of 0.68 for the baseline and 0.67 for the proposed model. It reports mean high-severity performance drop of 0.26 versus 0.16 and mean relative retention of 0.61 versus 0.76.

These are **values reported in the manuscript**, not outputs generated by this reconstructed repository. They should only be presented as reproduced results if the original artifacts or a documented rerun substantiate them.

## Limitations and responsible use

- Synthetic degradations are approximations and are not calibrated models of physical camera hardware.
- The current materialized training augmentation differs from the manuscript's stated on-the-fly strategy.
- The location split must be independently prepared and checked.
- No real-farm deployment or real-camera-fault validation is provided by this code.
- One run per model is insufficient for claims of statistical significance; use multiple seeds and report uncertainty.
- The dataset's source license and image-level terms must be checked before redistribution.

## Citation

See `CITATION.cff`. Cite the associated manuscript and the exact software release/commit used in your work.
