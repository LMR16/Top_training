"""Controller principal da aplicacao Top Training (Treino Real com Camera).

Herda de ctk.CTk e gerencia a janela principal, instanciando todas as telas
e fornecendo o metodo show_frame() para navegacao entre elas (Frame Switching).
"""

from __future__ import annotations

import customtkinter as ctk
from typing import Dict, Type, Optional

from src.ui.screens import MenuScreen, InicialScreen, CalibracaoScreen, TreinoScreen


class AppController(ctk.CTk):
    """Classe principal da aplicacao. Gerencia a janela e a troca de telas."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Top Training - Analisador de Tenis")
        self.geometry("1400x900")
        self.configure(fg_color="#1A1A2E")

        # Estado compartilhado entre telas
        self.jogador_nome: Optional[str] = None
        self.state_dificuldade: str = "Basico"
        self.state_lado: Optional[str] = None
        self.pipeline = None  # CV pipeline (setado na calibracao)
        self._ultimo_video_path: Optional[str] = None

        # Container que abriga todas as telas (empilhadas na mesma posicao)
        self.container = ctk.CTkFrame(self, fg_color="#1A1A2E")
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dicionario de telas instanciadas
        self.frames: Dict[Type[ctk.CTkFrame], ctk.CTkFrame] = {}

        # Instancia todas as telas
        for tela_cls in (MenuScreen, InicialScreen, CalibracaoScreen, TreinoScreen):
            frame = tela_cls(self.container, self)
            self.frames[tela_cls] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Exibe a tela inicial (menu/login)
        self.show_frame(MenuScreen)

    def show_frame(self, frame_cls: Type[ctk.CTkFrame]) -> None:
        """Eleva a tela desejada ao topo, tornando-a visivel."""
        for cls, frame in self.frames.items():
            if cls != frame_cls and hasattr(frame, "ocultar"):
                frame.ocultar()

        frame = self.frames[frame_cls]
        frame.tkraise()
        if hasattr(frame, "mostrar"):
            frame.mostrar()


def main() -> None:
    """Ponto de entrada da aplicacao."""
    app = AppController()
    app.mainloop()


if __name__ == "__main__":
    main()
