# Reproduction checklist

- [ ] Confirm dataset access terms and exact dataset version.
- [ ] Recover original annotations, class mapping, and location IDs.
- [ ] Recover train/validation/test location manifests.
- [ ] Recover original training logs and model checkpoints.
- [ ] Recover exact package versions and training commands.
- [ ] Verify the reported image/box/location counts.
- [ ] Unit-test each degradation operator visually and numerically.
- [ ] Confirm bounding boxes remain valid after each transform.
- [ ] Generate fixed degraded test sets with recorded seeds and checksums.
- [ ] Re-run baseline and augmented models.
- [ ] Run multiple seeds and report mean ± standard deviation.
- [ ] Run ablations and out-of-range severity tests.
- [ ] Rebuild every paper table and figure directly from machine-readable outputs.
