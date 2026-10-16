"""Estado compartilhado entre as telas da aplicacao."""

from typing import Optional


class AppState:
    def __init__(self) -> None:
        self.perfil_atual: Optional[str] = None
        self.dificuldade: str = "Basico"
        self.lado_selecionado: Optional[str] = None  # 'esquerda', 'centro', 'direita'
        self.acertos: int = 0
        self.erros: int = 0
        self.pontuacao: int = 0
        self.quiques: list[dict] = []
        self.poligono_quadra: list[tuple[int, int]] = []
        # Numero de zonas por dificuldade (mais zonas = mais dificil)
        self.zonas_por_dificuldade = {
            "Basico": 3,
            "Medio": 5,
            "Avancado": 7,
        }

    def reset_placar(self) -> None:
        self.acertos = 0
        self.erros = 0
        self.pontuacao = 0
        self.quiques = []
