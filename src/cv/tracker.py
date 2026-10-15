"""Rastreio da bola e detecção de quiques (bounce)."""


class BallTracker:
    def __init__(self) -> None:
        self.positions: list[tuple[int, int]] = []

    def update(self, position: tuple[int, int]) -> bool:
        self.positions.append(position)
        return False
