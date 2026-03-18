from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def _build_feature_matrix(
    products: list[dict[str, Any]],
) -> tuple[Any, list[str]]:
    ids: list[str] = []
    rows: list[list[float]] = []

    for p in products:
        ids.append(str(p["id"]))
        rows.append([
            float(p.get("ai_score", 0.0)),
            float(p.get("effectiveness_score", 0.0)),
            float(p.get("value_score", 0.0)),
            float(p.get("longevity_score", 0.0)),
            float(p.get("review_count", 0)),
        ])

    return np.array(rows, dtype=np.float64), ids


def run_pca(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(products) < 2:
        raise ValueError("PCA requires at least 2 products.")

    feature_matrix, ids = _build_feature_matrix(products)

    scaler = StandardScaler()
    scaled = scaler.fit_transform(feature_matrix)

    n_components = min(2, scaled.shape[1])
    pca = PCA(n_components=n_components, random_state=42)
    coords = pca.fit_transform(scaled)

    results: list[dict[str, Any]] = []
    for i, pid in enumerate(ids):
        p = products[i]
        pc1 = float(coords[i, 0])
        pc2 = float(coords[i, 1]) if n_components > 1 else 0.0
        results.append({
            "id": pid,
            "title": p.get("title", ""),
            "pc1": round(pc1, 4),
            "pc2": round(pc2, 4),
            "ai_score": p.get("ai_score", 0.0),
            "category_id": p.get("category_id"),
        })

    variance = [float(v) for v in pca.explained_variance_ratio_]
    results.append({
        "meta": True,
        "explained_variance": [round(v, 4) for v in variance],
        "feature_names": [
            "ai_score",
            "effectiveness_score",
            "value_score",
            "longevity_score",
            "review_count",
        ],
    })

    return results
