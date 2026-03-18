from __future__ import annotations

import heapq
from typing import Any


class ProductGraph:

    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}
        self._edges: dict[str, list[tuple[str, float]]] = {}

    def add_product(self, product_id: str, data: dict[str, Any]) -> None:
        self._nodes[product_id] = data
        self._edges.setdefault(product_id, [])

    def add_edge(self, from_id: str, to_id: str, weight: float = 1.0) -> None:
        self._edges.setdefault(from_id, []).append((to_id, weight))

    def build_from_products(self, products: list[dict[str, Any]]) -> None:
        for p in products:
            self.add_product(p["id"], p)

        product_ids = [p["id"] for p in products]
        total = len(product_ids)

        for i in range(total):
            for j in range(i + 1, total):
                id_a = product_ids[i]
                id_b = product_ids[j]
                node_a = self._nodes[id_a]
                node_b = self._nodes[id_b]

                if node_a.get("category_id") == node_b.get("category_id"):
                    score_a = float(node_a.get("ai_score", 0))
                    score_b = float(node_b.get("ai_score", 0))
                    diff = abs(score_a - score_b)
                    weight = round(1.0 - diff / 100.0, 4)

                    self.add_edge(id_a, id_b, weight)
                    self.add_edge(id_b, id_a, weight)

    def best_first_search(
        self,
        start_id: str,
        max_results: int = 10,
        min_score: float = 0.0,
    ) -> list[dict[str, Any]]:
        if start_id not in self._nodes:
            return []

        visited: set[str] = {start_id}
        results: list[dict[str, Any]] = []
        heap: list[tuple[float, str, dict[str, Any]]] = []

        for neighbour_id, _w in self._edges.get(start_id, []):
            if neighbour_id not in visited:
                neighbour = self._nodes[neighbour_id]
                score = float(neighbour.get("ai_score", 0.0))
                heapq.heappush(heap, (-score, neighbour_id, neighbour))

        while heap and len(results) < max_results:
            _priority, pid, _data = heapq.heappop(heap)

            if pid in visited:
                continue
            visited.add(pid)

            node_data = self._nodes[pid]
            node_score = float(node_data.get("ai_score", 0.0))

            if node_score >= min_score:
                results.append(node_data)

            for neighbour_id, _w in self._edges.get(pid, []):
                if neighbour_id not in visited:
                    neighbour = self._nodes[neighbour_id]
                    score = float(neighbour.get("ai_score", 0.0))
                    heapq.heappush(heap, (-score, neighbour_id, neighbour))

        return results
