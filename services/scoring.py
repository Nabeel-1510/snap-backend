WEIGHTS = {
    "effectiveness": 0.45,
    "value": 0.30,
    "longevity": 0.25,
}


def compute_ai_score(effectiveness: float, value: float, longevity: float) -> float:
    raw = (
        effectiveness * WEIGHTS["effectiveness"]
        + value * WEIGHTS["value"]
        + longevity * WEIGHTS["longevity"]
    )
    return round(min(max(raw, 0), 100), 1)
