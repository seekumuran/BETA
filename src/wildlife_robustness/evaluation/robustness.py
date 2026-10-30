"""Robustness metrics for a scalar detection metric such as mAP."""

def absolute_drop(clean_score: float, degraded_score: float) -> float:
    return clean_score - degraded_score

def relative_retention(clean_score: float, degraded_score: float) -> float:
    if clean_score <= 0:
        raise ValueError("clean_score must be positive")
    return degraded_score / clean_score

def robustness_summary(clean_score: float, degraded_scores: list[float]) -> dict:
    if not degraded_scores:
        raise ValueError("degraded_scores cannot be empty")
    drops = [absolute_drop(clean_score, score) for score in degraded_scores]
    retentions = [relative_retention(clean_score, score) for score in degraded_scores]
    return {
        "mean_absolute_drop": sum(drops) / len(drops),
        "mean_relative_retention": sum(retentions) / len(retentions),
        "conditions": len(degraded_scores),
    }
