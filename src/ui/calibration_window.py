"""Calibração da quadra: feed da câmera + seleção de pontos do polígono."""

import dearpygui.dearpygui as dpg


class CalibrationWindow:
    def __init__(self) -> None:
        self.points: list[tuple[int, int]] = []

    def run(self) -> None:
        with dpg.window(label="Calibração da Quadra", width=900, height=600):
            dpg.add_text("Selecione os pontos do polígono da quadra")
            dpg.add_button(label="Voltar")
