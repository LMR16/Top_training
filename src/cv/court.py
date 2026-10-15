"""Mapeamento e calibração da quadra (polígono definido pelo usuário)."""


class Court:
    def __init__(self) -> None:
        self.polygon: list[tuple[int, int]] = []

    def contains(self, point: tuple[int, int]) -> bool:
        return False
