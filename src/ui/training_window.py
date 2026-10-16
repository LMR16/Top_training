"""Interface de treino: mapa 2D, feedback visual e painel de contadores."""

import dearpygui.dearpygui as dpg
from src.ui.app_state import AppState
from src.ui.components import (
    aplicar_tema_global,
    painel_titulo,
    texto_placar,
    COR_QUADRA,
    COR_LINHA,
    COR_ACERTO,
    COR_ERRO,
    COR_DESTAQUE,
    COR_FUNDO,
)


class TrainingWindow:
    def __init__(self, state: AppState, navegar_para: callable) -> None:
        self.state = state
        self.navegar_para = navegar_para
        self.largura_mapa = 420
        self.altura_mapa = 560

    def run(self) -> None:
        with dpg.window(label="Treino", tag="tela_treino", width=1250, height=750, no_collapse=True, no_move=True, no_close=True):
            # Barra superior
            with dpg.group(horizontal=True):
                dpg.add_text(f"Perfil: {self.state.perfil_atual}", color=[200, 220, 255])
                dpg.add_spacer(width=40)
                dpg.add_text(f"Dificuldade: {self.state.dificuldade}", color=[255, 220, 150])
                dpg.add_spacer(width=40)
                dpg.add_button(label="Voltar", width=100, callback=lambda: self.navegar_para("menu"))
                dpg.add_spacer(width=10)
                dpg.add_button(label="Salvar Treino", width=120, callback=self._salvar)
                dpg.add_spacer(width=10)
                dpg.add_button(label="Trocar Dificuldade", width=140, callback=lambda: self.navegar_para("dificuldade"))

            dpg.add_separator()
            dpg.add_spacer(height=10)

            with dpg.group(horizontal=True):
                # Coluna esquerda: mapa 2D
                with dpg.child_window(width=self.largura_mapa + 40, height=600, border=True):
                    dpg.add_text("Mapa 2D da Quadra", color=COR_DESTAQUE)
                    with dpg.drawlist(tag="draw_mapa", width=self.largura_mapa, height=self.altura_mapa):
                        self._desenhar_quadra()

                # Coluna centro: feed da camera (placeholder)
                with dpg.child_window(width=520, height=600, border=True):
                    dpg.add_text("Feed da Camera", color=COR_DESTAQUE)
                    dpg.add_spacer(height=20)
                    dpg.add_text("Aguardando captura de video", color=[140, 140, 140])
                    dpg.add_spacer(height=30)
                    dpg.add_text("Detecao de quiques em tempo real", color=[140, 140, 140])

                # Coluna direita: painel de contadores
                with dpg.child_window(width=260, height=600, border=True):
                    dpg.add_text("Painel de Placar", color=COR_DESTAQUE)
                    dpg.add_spacer(height=10)
                    texto_placar("Acertos", self.state.acertos, COR_ACERTO)
                    texto_placar("Erros", self.state.erros, COR_ERRO)
                    texto_placar("Pontuacao", self.state.pontuacao, COR_DESTAQUE)
                    dpg.add_spacer(height=20)
                    dpg.add_separator()
                    dpg.add_text("Quiques recentes:", color=[160, 160, 160])
                    dpg.add_text("Nenhum", tag="lista_quiques", color=[200, 200, 200])

        self._atualizar_placar()

    def _desenhar_quadra(self) -> None:
        # Linhas de marcador da quadra (representacao vertical simplificada)
        cx = self.largura_mapa / 2
        dpg.draw_line([cx, 0], [cx, self.altura_mapa], color=COR_LINHA, thickness=2, parent="draw_mapa")  # rede ao meio
        dpg.draw_line([40, 40], [self.largura_mapa - 40, 40], color=COR_LINHA, thickness=2, parent="draw_mapa")  # linha de fundo superior
        dpg.draw_line([40, self.altura_mapa - 40], [self.largura_mapa - 40, self.altura_mapa - 40], color=COR_LINHA, thickness=2, parent="draw_mapa")  # linha de fundo inferior

    def _salvar(self) -> None:
        from src.data.sessions import SessionStore
        store = SessionStore()
        store.salvar(
            perfil_nome=self.state.perfil_atual or "desconhecido",
            dificuldade=self.state.dificuldade,
            acertos=self.state.acertos,
            erros=self.state.erros,
            pontuacao=self.state.pontuacao,
            quiques=self.state.quiques,
        )
        dpg.set_value("lista_quiques", "Treino salvo com sucesso.")

    def _atualizar_placar(self) -> None:
        # Atualiza textos do placar se existirem
        try:
            pass  # textos sao estaticos; atualizacao real vem do controlador
        except Exception:
            pass
