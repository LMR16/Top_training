"""Interface de treino: mapa 2D, feedback visual e painel de contadores."""

import dearpygui.dearpygui as dpg


class TrainingWindow:
    def __init__(self) -> None:
        self.dificuldade: str = "Basico"

    def run(self) -> None:
        with dpg.window(label="Treino", width=1200, height=700):
            dpg.add_text(f"Dificuldade: {self.dificuldade}")
            dpg.add_button(label="Voltar")
            dpg.add_button(label="Salvar Treino")
            dpg.add_button(label="Trocar Dificuldade")
