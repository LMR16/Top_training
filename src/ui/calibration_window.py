"""Calibracao da quadra: feed da camera + selecao de pontos do poligono."""

import dearpygui.dearpygui as dpg
from src.ui.app_state import AppState
from src.ui.components import (
    aplicar_tema_global,
    painel_titulo,
    COR_DESTAQUE,
    COR_LINHA,
)


class CalibrationWindow:
    def __init__(self, state: AppState, navegar_para: callable) -> None:
        self.state = state
        self.navegar_para = navegar_para
        self.pontos_temp: list[tuple[int, int]] = []

    def run(self) -> None:
        with dpg.window(label="Calibracao da Quadra", tag="tela_calibracao", width=1100, height=700, no_collapse=True, no_move=True, no_close=True):
            painel_titulo("Mapeamento da Quadra (Calibracao)", 1100)
            dpg.add_spacer(height=10)
            dpg.add_text("Clique na area da camera para definir os vertices do poligono da quadra oposta.", color=[160, 160, 160])

            with dpg.group(horizontal=True):
                # Area da camera (placeholder)
                with dpg.child_window(width=700, height=500, border=True):
                    dpg.add_text("FEED DA CAMERA (Iriun Webcam)", color=[120, 120, 120])
                    dpg.add_text("Aguardando modulo de captura (Fase 3).", color=[120, 120, 120])
                    dpg.add_spacer(height=40)
                    dpg.add_text("Area de selecao de pontos do poligono", color=[160, 160, 160])
                    with dpg.drawlist(tag="draw_calibracao", width=680, height=380):
                        dpg.draw_rectangle([0, 0], [680, 380], color=[60, 60, 60], fill=[30, 30, 30], parent="draw_calibracao")

                # Painel de controle da calibracao
                with dpg.child_window(width=360, height=500, border=True):
                    dpg.add_text("Pontos do poligono:", color=COR_DESTAQUE)
                    dpg.add_text("0 pontos selecionados", tag="contador_pontos", color=[200, 200, 200])
                    dpg.add_spacer(height=10)
                    dpg.add_button(label="Adicionar Ponto (clique no mapa)", width=300, callback=self._adicionar_ponto_manual)
                    dpg.add_button(label="Limpar Pontos", width=300, callback=self._limpar_pontos)
                    dpg.add_spacer(height=10)
                    dpg.add_separator()
                    dpg.add_button(label="Confirmar Poligono", width=300, height=36, callback=self._confirmar)
                    dpg.add_button(label="Voltar", width=300, callback=lambda: self.navegar_para("menu"))

    def _adicionar_ponto_manual(self) -> None:
        self.pontos_temp.append((0, 0))
        self._atualizar_contador()
        self._redesenhar()

    def _limpar_pontos(self) -> None:
        self.pontos_temp = []
        self.state.poligono_quadra = []
        self._atualizar_contador()
        self._redesenhar()

    def _confirmar(self) -> None:
        if len(self.pontos_temp) < 3:
            dpg.set_value("contador_pontos", "Minimo 3 pontos para o poligono.")
            return
        self.state.poligono_quadra = self.pontos_temp.copy()
        self.navegar_para("dificuldade")

    def _atualizar_contador(self) -> None:
        dpg.set_value("contador_pontos", f"{len(self.pontos_temp)} pontos selecionados")

    def _redesenhar(self) -> None:
        dpg.delete_item("draw_calibracao", children_only=True)
        dpg.draw_rectangle([0, 0], [680, 380], color=[60, 60, 60], fill=[30, 30, 30], parent="draw_calibracao")
        for i, (x, y) in enumerate(self.pontos_temp):
            px = min(max(x, 10), 670)
            py = min(max(y, 10), 370)
            dpg.draw_circle([px, py], 6, color=[0, 255, 255], fill=[0, 255, 255], parent="draw_calibracao")
            if i > 0:
                px_ant, py_ant = self.pontos_temp[i - 1]
                dpg.draw_line([min(max(px_ant, 10), 670), min(max(py_ant, 10), 370)], [px, py], color=[0, 255, 255], parent="draw_calibracao")
