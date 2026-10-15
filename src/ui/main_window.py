"""Menu inicial: perfis, iniciar treino e recalibrar quadra."""

import dearpygui.dearpygui as dpg


class MainWindow:
    def __init__(self) -> None:
        dpg.create_context()
        dpg.create_viewport(title="Top Training", width=900, height=600)
        dpg.setup_dearpygui()

    def run(self) -> None:
        with dpg.window(label="Menu Inicial", width=900, height=600):
            dpg.add_text("Top Training - Analisador de Treino de Tênis")
            dpg.add_button(label="Iniciar Treino")
            dpg.add_button(label="Recalibrar Quadra")
            dpg.add_button(label="Sair", callback=lambda: dpg.stop_dearpygui())
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
