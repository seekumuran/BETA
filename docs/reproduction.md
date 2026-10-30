# Reproduction and experiment checklist

- [ ] Verify dataset name, release/version, access date and license.
- [ ] Verify six-class mapping and all filtering/merging rules.
- [ ] Recover or regenerate camera-location split manifests.
- [ ] Confirm there is no location overlap between train, validation and test.
- [ ] Confirm image and bounding-box counts.
- [ ] Verify augmentation parameter ranges against the historical implementation.
- [ ] Record exact package versions, OS, hardware and training command.
- [ ] Run baseline and failure-aware models with at least 3–5 seeds.
- [ ] Preserve checkpoints, logs, metrics JSON/CSV and configuration snapshots.
- [ ] Evaluate each model on the same fixed clean and degraded test images.
- [ ] Run ablations for individual fault families and combined corruption.
- [ ] Run severity generalization outside the training parameter ranges.
- [ ] Rebuild every manuscript table from raw machine-readable evaluation outputs.

## Important implementation difference

`scripts/build_training_dataset.py` materializes one stochastic degraded/clean view per training image before training. The manuscript describes online augmentation during training. These are not equivalent. An online augmentation integration must be implemented and validated before claiming exact methodological reproduction.
