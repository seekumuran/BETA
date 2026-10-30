param(
  [Parameter(Mandatory=$true)][string]$DataYaml,
  [string]$Output = "datasets/failure_aware",
  [string]$Device = "cpu"
)
$ErrorActionPreference = "Stop"

Write-Host "Validating source dataset..."
python scripts/validate_yolo_dataset.py --data $DataYaml
if ($LASTEXITCODE -ne 0) { throw "Dataset validation failed" }

Write-Host "Training baseline..."
python scripts/train.py --data $DataYaml --name baseline --device $Device
if ($LASTEXITCODE -ne 0) { throw "Baseline training failed" }

Write-Host "Building materialized failure-aware training set..."
python scripts/build_training_dataset.py --data $DataYaml --output $Output --probability 0.5 --seed 42
if ($LASTEXITCODE -ne 0) { throw "Dataset materialization failed" }

Write-Host "Training failure-aware model..."
python scripts/train.py --data "$Output/dataset.yaml" --name failure_aware --device $Device
if ($LASTEXITCODE -ne 0) { throw "Failure-aware training failed" }

Write-Host "Evaluate each model separately with scripts/evaluate_robustness.py."
