# Camera-Failure-Aware Augmentation for Robust Wildlife Detection

**Research project:** *Making Wildlife Detection Survive Bad Cameras: Camera-Failure-Aware Augmentation*  
**Authors:** Avnish Mandlik, Anushka Borkar, Kumaran Chandrashekar, and Om Deshmukh  
**Affiliation:** Vellore Institute of Technology, Chennai, India

[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/) [![Framework](https://img.shields.io/badge/Detector-YOLOv8n-orange)](https://github.com/ultralytics/ultralytics) [![Status](https://img.shields.io/badge/Status-research%20prototype-yellow)]()

## Overview

Wildlife-monitoring cameras may produce degraded images because of motion blur, low-light sensor noise, JPEG compression, defective pixels, lens obstruction, occlusion, or transmission corruption. A detector trained mainly on clean images can lose accuracy when these camera faults occur.

This project studies whether **camera-failure-aware data augmentation** can improve the robustness of a lightweight wildlife object detector. The manuscript uses an unmodified YOLOv8n detector and compares conventional training against training in which camera degradations are applied to training images on the fly.

The work focuses on robustness to image-quality degradation and generalisation to camera locations held out from training. It does not claim a new detection architecture.

## Research question

Can camera-failure-aware augmentation improve wildlife detection under synthetic surveillance-camera degradation while maintaining performance on clean images?

## Dataset described in the paper

The study reports using a filtered subset of **Caltech Camera Traps**, distributed through the LILA BC platform. The paper describes six retained classes:

- Deer
- Wild boar
- Fox
- Coyote
- Raccoon
- Cattle

The manuscript reports **17,000 images**, **21,900 bounding boxes**, and **85 camera locations** after filtering and annotation preparation. These are the reported subset counts, not the size of the complete Caltech Camera Traps dataset.

### Location-based split reported in the paper

| Split | Images | Boxes | Camera locations |
|---|---:|---:|---:|
| Train | 12,000 | 15,400 | 60 |
| Validation | 2,000 | 2,600 | 10 |
| Test | 3,000 | 3,900 | 15 |
| **Total** | **17,000** | **21,900** | **85** |

The split is performed by camera location rather than randomly by image, to reduce leakage between visually similar images from the same camera. The original split manifests are not currently included in this repository.

**Dataset access and licensing:** Obtain the dataset from its official distribution source and check the applicable dataset terms before use or redistribution. Do not upload the dataset or annotations to this repository unless redistribution is explicitly permitted. The manuscript identifies the LILA BC distribution as using the Community Data License Agreement (permissive variant); verify the exact terms for the specific downloaded subset and its component data before relying on that statement.

## Method

### Baseline and proposed training

Both experimental conditions use YOLOv8n initialized from COCO-pretrained weights. The proposed condition adds a camera-degradation step during training; the baseline does not. The manuscript states that the other training settings were kept the same.

For each training image, the manuscript specifies an augmentation probability of **0.5**. When selected, one of the seven individual degradation types is sampled uniformly, along with one of three severity levels (Low, Medium, or High). The degradation parameters are sampled from the ranges in `configs/degradation.yaml`.

### Camera degradation models

| Fault model | Intended camera problem | Severity parameters described in the paper |
|---|---|---|
| Motion blur | Camera shake or movement during exposure | Kernel length: 5–9 / 11–19 / 21–35 px |
| Sensor noise | Increased sensor gain in low light | Gaussian noise σ: 0.02–0.04 / 0.05–0.10 / 0.12–0.20 |
| JPEG compression | Bandwidth-limited video streams | Quality: 60–80 / 25–45 / 5–15 |
| Dead pixels | Defective sensor pixels | Pixel fraction: 0.1–0.3% / 0.5–1% / 2–4% |
| Lens obstruction | Dirt, water drops, or insects on lens | Area: 5–10% / 15–25% / 30–45%; opacity increases by severity |
| Random occlusion | Foliage or objects blocking the view | Area: 5–10% / 15–25% / 30–40% |
| Frame corruption | Transmission errors or damaged frame regions | Band fraction: 2–5% / 8–15% / 20–30% |
| Combined | Co-occurring camera faults | Random composition of two or three faults |

The current code provides deterministic, synthetic approximations of these image transformations. They should not be interpreted as calibrated physical models of specific camera hardware.

## Experimental settings reported in the manuscript

| Setting | Reported value |
|---|---|
| Detector | YOLOv8n |
| Input size | 640 × 640 |
| Training epochs | 50, with early-stopping patience 10 |
| Batch size | 16 |
| Optimizer | SGD |
| Momentum | 0.937 |
| Weight decay | 0.0005 |
| Initial learning rate | 0.01 |
| Final learning-rate factor | 0.01 |
| Learning-rate schedule | Cosine |
| Random seed | 42; one run per model in the reported study |
| Hardware | Intel Core i5-12450H, Intel UHD Graphics, 16 GB RAM |
| Software versions | Python 3.10.12, PyTorch 2.1.2, Ultralytics 8.1.0, OpenCV 4.8.1, Albumentations 1.3.1 |

The manuscript states that test degradations were generated separately from training degradations using a different random seed, and that the validation set was used for model selection on clean images.

## Results reported in the manuscript

The following are the values printed in the accompanying manuscript. **They are manuscript-reported results, not results independently reproduced by the current public code.** The original training machine is currently unavailable, and the original checkpoints, logs, fixed test sets, and split manifests have not yet been recovered into this repository. Do not cite this repository as having independently reproduced these numbers until the experiment artifacts and evaluation pipeline are available.

### Clean test performance

| Model | Precision | Recall | F1 | mAP@0.5 | mAP@0.5:0.95 | FPS |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 0.91 | 0.86 | 0.88 | 0.92 | 0.68 | 142 |
| Proposed | 0.90 | 0.86 | 0.88 | 0.92 | 0.67 | 141 |

### mAP@0.5:0.95 under individual degradations

Values are Low / Medium / High severity.

| Degradation | Baseline | Proposed |
|---|---|---|
| Motion blur | 0.64 / 0.55 / 0.41 | 0.65 / 0.60 / 0.52 |
| Sensor noise | 0.65 / 0.56 / 0.43 | 0.65 / 0.61 / 0.53 |
| JPEG | 0.66 / 0.60 / 0.51 | 0.66 / 0.63 / 0.58 |
| Dead pixels | 0.66 / 0.61 / 0.52 | 0.66 / 0.63 / 0.57 |
| Lens obstruction | 0.63 / 0.52 / 0.38 | 0.64 / 0.57 / 0.47 |
| Random occlusion | 0.62 / 0.52 / 0.40 | 0.63 / 0.57 / 0.48 |
| Frame corruption | 0.64 / 0.55 / 0.44 | 0.65 / 0.60 / 0.52 |

### Combined degradation

| Severity | Baseline | Proposed | Difference |
|---|---:|---:|---:|
| Low | 0.58 | 0.62 | +0.04 |
| Medium | 0.40 | 0.52 | +0.12 |
| High | 0.24 | 0.40 | +0.16 |

The paper reports that, averaged across its eight high-severity conditions (seven individual faults plus combined), the mean absolute mAP@0.5:0.95 drop decreased from 0.26 to 0.16, while mean relative retention increased from 0.61 to 0.76.

### Statistical caveat

The manuscript reports one training run per model (seed 42), without confidence intervals or variation across repeated seeds. Small differences should therefore not be treated as statistically established. The study also uses synthetic degradations from the same implementation family for training and testing, so performance on real camera faults remains unverified.

## Repository contents

```text
wildlife-robustness/
├── configs/
│   └── degradation.yaml
├── docs/
│   ├── methodology.md
│   └── reproduction.md
├── scripts/
│   └── apply_degradation.py
├── src/wildlife_robustness/
│   ├── augmentations/
│   │   └── camera_faults.py
│   ├── data/
│   │   └── splits.py
│   └── evaluation/
│       └── robustness.py
├── tests/
├── CITATION.cff
├── LICENSE
├── pyproject.toml
└── requirements.txt
```

## Installation

Python 3.10 is recommended to align with the software environment described in the manuscript.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## Apply a degradation to an image

```bash
python scripts/apply_degradation.py \
  --input path/to/image.jpg \
  --output preview.jpg \
  --type motion_blur \
  --severity high \
  --seed 42
```

On Windows PowerShell, the command can be entered on one line:

```powershell
python scripts/apply_degradation.py --input path/to/image.jpg --output preview.jpg --type motion_blur --severity high --seed 42
```

Supported `--type` values: `motion_blur`, `sensor_noise`, `jpeg`, `dead_pixels`, `lens_obstruction`, `random_occlusion`, `frame_corruption`, and `combined`.

## Run tests

```bash
python -m pytest -q
```

## Research limitations and next steps

The manuscript acknowledges the following limitations:

1. Synthetic degradations may not represent real camera failures.
2. The dataset is from camera-trap locations in the southwestern United States; conclusions for farms and other geographic regions are indirect.
3. Daytime, rain, and fog conditions were not separately evaluated.
4. Class imbalance may affect aggregate metrics.
5. Single-frame experiments do not model temporal video effects.
6. Only one training run per model was reported.
7. Repeated-seed experiments, matched-volume ablations, out-of-range severity tests, and real-farm validation were not completed.

The current repository is an initial implementation scaffold. It contains degradation operators, a location-split validation helper, and robustness metric helpers. It does **not yet contain** the complete dataset preparation pipeline, YOLO training scripts, fixed degraded test-set generation, or the original experiment artifacts. Those are required before this repository can be described as a complete reproduction package.

## Citation

If you use this repository, cite the associated paper when its final bibliographic details are available. The `CITATION.cff` file is a metadata template and should be updated when a stable release or DOI exists.

## Acknowledgements and third-party software

This project builds on the Ultralytics YOLOv8 implementation and uses common scientific Python and computer-vision libraries. Check and comply with the applicable licenses and attribution requirements for Ultralytics, PyTorch, OpenCV, NumPy, Albumentations, and the dataset before redistribution or deployment. This repository does not include third-party model weights or the wildlife dataset.
