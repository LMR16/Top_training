"""Menu inicial: perfis, iniciar treino e recalibrar quadra."""

import dearpygui.dearpygui as dpg
from src.ui.app_state import AppState
from src.ui.components import (
    aplicar_tema_global,
    painel_titulo,
    COR_FUNDO,
    COR_QUADRA,
    COR_LINHA,
    COR_DESTAQUE,
)


class MainWindow:
    def __init__(self, state: AppState, navegar_para: callable) -> None:
        self.state = state
        self.navegar_para = navegar_para

    def run(self) -> None:
        with dpg.window(label="Menu Inicial", tag="menu_principal", width=900, height=600, no_collapse=True, no_move=True, no_close=True):
            dpg.add_text("TOP TRAINING", color=[150, 200, 255])
            dpg.add_text("Analisador de Treino de Tenis", color=[200, 220, 235])
            dpg.add_spacer(height=20)

            with dpg.group(horizontal=False):
                dpg.add_text("Perfil do Jogador", color=COR_DESTAQUE)
                dpg.add_input_text(tag="input_nome_perfil", hint="Digite o nome do jogador", width=300)
                dpg.add_button(label="Criar / Selecionar Perfil", width=300, callback=self._criar_perfil)

            dpg.add_spacer(height=10)
            dpg.add_text("Perfis salvos:", color=[160, 160, 160])
            with dpg.child_window(height=120, border=True):
                dpg.add_text("Nenhum perfil encontrado.", tag="lista_perfis", color=[160, 160, 160])

            dpg.add_spacer(height=20)
            dpg.add_button(label="Iniciar Treino", width=260, height=40, callback=self._iniciar_treino)
            dpg.add_same_line()
            dpg.add_button(label="Recalibrar Quadra", width=260, height=40, callback=self._recalibrar)

            dpg.add_spacer(height=20)
            dpg.add_button(label="Sair", width=120, callback=lambda: dpg.stop_dearpygui())

    def _criar_perfil(self) -> None:
        nome = dpg.get_value("input_nome_perfil").strip()
        if not nome:
            return
        from src.data.profiles import ProfileStore
        store = ProfileStore()
        if nome not in store.listar():
            store.salvar(nome, {"nome": nome, "vitorias": 0, "treinos": 0})
        self.state.perfil_atual = nome
        dpg.set_value("lista_perfis", f"Perfil ativo: {nome}")

    def _iniciar_treino(self) -> None:
        if not self.state.perfil_atual:
            dpg.set_value("lista_perfis", "Selecione ou crie um perfil primeiro.")
            return
        self.navegar_para("dificuldade")

    def _recalibrar(self) -> None:
        self.navegar_para("calibracao")
