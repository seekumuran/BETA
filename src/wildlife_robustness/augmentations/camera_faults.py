"""Synthetic camera-failure operators.

Images are expected as uint8 NumPy arrays in OpenCV BGR channel order.
These are controllable synthetic approximations, not calibrated sensor models.
"""
from __future__ import annotations

from typing import Callable

import cv2
import numpy as np


def _rng(seed: int | None) -> np.random.Generator:
    return np.random.default_rng(seed)


def motion_blur(image: np.ndarray, severity: str, rng: np.random.Generator) -> np.ndarray:
    ranges = {"low": (5, 9), "medium": (11, 19), "high": (21, 35)}
    lo, hi = ranges[severity]
    length = int(rng.integers(lo, hi + 1))
    angle = float(rng.uniform(0, 180))
    kernel = np.zeros((length, length), dtype=np.float32)
    kernel[length // 2, :] = 1.0
    matrix = cv2.getRotationMatrix2D((length / 2 - 0.5, length / 2 - 0.5), angle, 1.0)
    kernel = cv2.warpAffine(kernel, matrix, (length, length))
    total = float(kernel.sum())
    if total:
        kernel /= total
    return cv2.filter2D(image, -1, kernel)


def sensor_noise(image: np.ndarray, severity: str, rng: np.random.Generator) -> np.ndarray:
    sigmas = {"low": (0.02, 0.04), "medium": (0.05, 0.10), "high": (0.12, 0.20)}
    lo, hi = sigmas[severity]
    sigma = float(rng.uniform(lo, hi))
    x = image.astype(np.float32) / 255.0
    noise = rng.normal(0.0, sigma, size=x.shape).astype(np.float32)
    return (np.clip(x + noise, 0, 1) * 255).astype(np.uint8)


def jpeg_compression(image: np.ndarray, severity: str, rng: np.random.Generator) -> np.ndarray:
    ranges = {"low": (60, 80), "medium": (25, 45), "high": (5, 15)}
    lo, hi = ranges[severity]
    quality = int(rng.integers(lo, hi + 1))
    ok, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("OpenCV JPEG encoding failed")
    decoded = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if decoded is None:
        raise RuntimeError("OpenCV JPEG decoding failed")
    return decoded


def dead_pixels(image: np.ndarray, severity: str, rng: np.random.Generator) -> np.ndarray:
    fractions = {"low": (0.001, 0.003), "medium": (0.005, 0.01), "high": (0.02, 0.04)}
    lo, hi = fractions[severity]
    out = image.copy()
    h, w = out.shape[:2]
    count = max(1, int(h * w * rng.uniform(lo, hi)))
    ys = rng.integers(0, h, count)
    xs = rng.integers(0, w, count)
    values = rng.choice([0, 255], size=count).astype(np.uint8)
    out[ys, xs, :] = values[:, None]
    return out


def lens_obstruction(image: np.ndarray, severity: str, rng: np.random.Generator) -> np.ndarray:
    settings = {
        "low": ((0.05, 0.10), (0.3, 0.5)),
        "medium": ((0.15, 0.25), (0.5, 0.7)),
        "high": ((0.30, 0.45), (0.7, 0.9)),
    }
    (alo, ahi), (olo, ohi) = settings[severity]
    h, w = image.shape[:2]
    area = float(rng.uniform(alo, ahi))
    radius = max(2, int(np.sqrt(area * h * w / np.pi)))
    cx, cy = int(rng.integers(0, w)), int(rng.integers(0, h))
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, (cx, cy), radius, 255, -1)
    # Slight blur makes the synthetic obstruction edge less artificial.
    mask = cv2.GaussianBlur(mask, (0, 0), max(1, radius * 0.08)).astype(np.float32) / 255.0
    opacity = float(rng.uniform(olo, ohi))
    tint = np.full_like(image, int(rng.integers(20, 100)))
    alpha = (mask * opacity)[..., None]
    return np.clip(image.astype(np.float32) * (1 - alpha) + tint * alpha, 0, 255).astype(np.uint8)


def random_occlusion(image: np.ndarray, severity: str, rng: np.random.Generator) -> np.ndarray:
    ranges = {"low": (0.05, 0.10), "medium": (0.15, 0.25), "high": (0.30, 0.40)}
    lo, hi = ranges[severity]
    out = image.copy()
    h, w = out.shape[:2]
    target = float(rng.uniform(lo, hi)) * h * w
    covered = 0
    attempts = 0
    while covered < target and attempts < 20:
        rh = int(rng.uniform(0.08, 0.30) * h)
        rw = int(rng.uniform(0.08, 0.30) * w)
        y = int(rng.integers(0, max(1, h - rh + 1)))
        x = int(rng.integers(0, max(1, w - rw + 1)))
        out[y:y+rh, x:x+rw] = rng.integers(0, 256, size=(1, 1, 3), dtype=np.uint8)
        covered += rh * rw
        attempts += 1
    return out


def frame_corruption(image: np.ndarray, severity: str, rng: np.random.Generator) -> np.ndarray:
    ranges = {"low": (0.02, 0.05), "medium": (0.08, 0.15), "high": (0.20, 0.30)}
    lo, hi = ranges[severity]
    out = image.copy()
    h, w = out.shape[:2]
    target = float(rng.uniform(lo, hi)) * h
    covered = 0
    while covered < target:
        band_h = max(1, int(rng.uniform(0.01, 0.06) * h))
        y = int(rng.integers(0, max(1, h - band_h + 1)))
        if rng.random() < 0.5:
            out[y:y+band_h, :] = 0
        else:
            shift = int(rng.integers(-w // 4, w // 4 + 1))
            out[y:y+band_h, :] = np.roll(out[y:y+band_h, :], shift, axis=1)
        covered += band_h
    return out


_OPERATORS: dict[str, Callable] = {
    "motion_blur": motion_blur,
    "sensor_noise": sensor_noise,
    "jpeg": jpeg_compression,
    "dead_pixels": dead_pixels,
    "lens_obstruction": lens_obstruction,
    "random_occlusion": random_occlusion,
    "frame_corruption": frame_corruption,
}


def degradation_names() -> list[str]:
    return [*_OPERATORS.keys(), "combined"]


def apply_degradation(
    image: np.ndarray,
    fault: str,
    severity: str = "medium",
    seed: int | None = None,
) -> np.ndarray:
    """Apply one synthetic fault or a composition of two/three faults."""
    if image is None or not isinstance(image, np.ndarray) or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("image must be a non-empty HxWx3 NumPy array")
    if severity not in {"low", "medium", "high"}:
        raise ValueError("severity must be low, medium, or high")
    rng = _rng(seed)
    if fault == "combined":
        count = int(rng.integers(2, 4))
        names = rng.choice(list(_OPERATORS), size=count, replace=False).tolist()
        out = image.copy()
        for index, name in enumerate(names):
            # Independent deterministic sub-seeds make the composition repeatable.
            out = _OPERATORS[name](out, severity, _rng(int(rng.integers(0, 2**31 - 1))))
        return out
    if fault not in _OPERATORS:
        raise ValueError(f"Unknown fault '{fault}'. Choose from {degradation_names()}")
    return _OPERATORS[fault](image.copy(), severity, rng)
