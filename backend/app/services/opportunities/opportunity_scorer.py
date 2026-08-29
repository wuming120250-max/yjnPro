from __future__ import annotations


def impact_score(amount: float | None, level: str = "medium") -> int:
    if amount and amount > 0:
        if amount > 5000:
            return 40
        if amount >= 3000:
            return 30
        if amount >= 1000:
            return 20
        return 10
    return {"high": 40, "medium": 25, "low": 10}.get(level, 25)


def score_opportunity(
    *,
    estimated_impact: float = 0,
    impact_level: str = "medium",
    urgency: int = 15,
    frequency: int = 8,
    executability: int = 10,
    score_inputs: dict | None = None,
) -> tuple[int, str]:
    if score_inputs:
        total = (
            int(score_inputs.get("impact", 0))
            + int(score_inputs.get("urgency", 0))
            + int(score_inputs.get("frequency", 0))
            + int(score_inputs.get("executability", 0))
        )
    else:
        total = (
            impact_score(estimated_impact, impact_level)
            + max(0, min(25, urgency))
            + max(0, min(20, frequency))
            + max(0, min(15, executability))
        )
    total = max(0, min(100, total))
    if total >= 80:
        level = "high"
    elif total >= 60:
        level = "medium"
    else:
        level = "low"
    return total, level
