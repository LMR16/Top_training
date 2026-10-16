"""Mapeamento e calibracao da quadra (poligono definido pelo usuario)."""

from __future__ import annotations

from typing import List, Tuple, Optional


class Court:
    """Gerencia a calibracao da quadra via poligono definido pelo usuario."""

    def __init__(self) -> None:
        self.polygon: List[Tuple[int, int]] = []
        self.calibrated = False

    def add_point(self, x: int, y: int) -> None:
        """Adiciona um vertice ao poligono da quadra."""
        self.polygon.append((x, y))

    def clear(self) -> None:
        """Limpa os pontos do poligono."""
        self.polygon = []
        self.calibrated = False

    def finalize(self) -> None:
        """Marca a calibracao como finalizada (minimo 3 pontos)."""
        if len(self.polygon) >= 3:
            self.calibrated = True

    def contains(self, point: Tuple[int, int]) -> bool:
        """Verifica se um ponto esta dentro do poligono da quadra (ray casting)."""
        if not self.calibrated or len(self.polygon) < 3:
            return False

        x, y = point
        inside = False
        n = len(self.polygon)
        j = n - 1
        for i in range(n):
            xi, yi = self.polygon[i]
            xj, yj = self.polygon[j]
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside

    def get_polygon(self) -> List[Tuple[int, int]]:
        return self.polygon.copy()
