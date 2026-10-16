"""Tela de selecao de dificuldade antes do treino."""

import dearpygui.dearpygui as dpg
from src.ui.app_state import AppState
from src.ui.components import (
    aplicar_tema_global,
    painel_titulo,
    COR_DESTAQUE,
)


class DificuldadeWindow:
    def __init__(self, state: AppState, navegar_para: callable) -> None:
        self.state = state
        self.navegar_para = navegar_para

    def run(self) -> None:
        with dpg.window(label="Selecao de Dificuldade", tag="tela_dificuldade", width=900, height=600, no_collapse=True, no_move=True, no_close=True):
            painel_titulo("Escolha a Dificuldade", 900)
            dpg.add_spacer(height=20)
            dpg.add_text("Cada dificuldade divide a quadra em zonas alvo diferentes.", color=[160, 160, 160])
            dpg.add_spacer(height=30)

            dificuldades = [
                ("Basico", "3 zonas amplas (esquerda, centro, direita)"),
                ("Medio", "3 zonas, incluindo area profunda central"),
                ("Avancado", "6 zonas curtas e longas, precisao exigida"),
            ]

            for nome, descricao in dificuldades:
                with dpg.group(horizontal=True):
                    dpg.add_button(label=nome, width=120, callback=lambda s, n=nome: self._selecionar(n))
                    dpg.add_text(descricao, color=[200, 200, 200])

            dpg.add_spacer(height=40)
            dpg.add_button(label="Voltar", width=120, callback=lambda: self.navegar_para("menu"))

    def _selecionar(self, nome: str) -> None:
        self.state.dificuldade = nome
        self.state.reset_placar()
        self.navegar_para("treino")
