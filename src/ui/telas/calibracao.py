"""Tela de Calibracao da Quadra (mapeamento do poligono)."""

import tkinter as tk
from src.ui.estilos import (
    COR_FUNDO, COR_PAINEL, COR_BOTAO, COR_BOTAO_HOVER, COR_TEXTO,
    COR_TEXTO_MUTADO, COR_DESTAQUE, aplicar_estilo_botao, criar_label_pai,
    criar_separador,
)


class TelaCalibracao:
    def __init__(self, pai, controle) -> None:
        self.controle = controle
        self.frame = tk.Frame(pai, bg=COR_FUNDO)
        self.pontos = []
        self._construir()

    def _construir(self) -> None:
        # Layout horizontal: camera esquerda, controles direita
        container = tk.Frame(self.frame, bg=COR_FUNDO)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # ===== Coluna esquerda: Area da camera =====
        cam_panel = tk.Frame(container, bg=COR_PAINEL, highlightbackground="#3C4150", highlightthickness=1)
        cam_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        lbl_cam = criar_label_pai(cam_panel, "Feed da Camera (Iriun Webcam)", cor=COR_DESTAQUE, tamanho=14, negrito=True)
        lbl_cam.pack(fill="x", padx=20, pady=(15, 5))

        self.canvas = tk.Canvas(cam_panel, width=640, height=480, bg="#0A0B0F", highlightthickness=0)
        self.canvas.pack(padx=20, pady=10)
        self.canvas.create_text(
            320, 240,
            text="Aguardando captura de video...",
            fill="#64646E",
            font=("Segoe UI", 12),
        )

        txt_info = criar_label_pai(
            cam_panel,
            "Clique na area da camera para definir os vertices do poligono da quadra oposta.",
            cor=COR_TEXTO_MUTADO,
            tamanho=10,
        )
        txt_info.pack(fill="x", padx=20, pady=(0, 15))

        # ===== Coluna direita: Controles de calibracao =====
        ctrl_panel = tk.Frame(container, bg=COR_PAINEL, width=340, highlightbackground="#3C4150", highlightthickness=1)
        ctrl_panel.pack(side="right", fill="y", padx=(10, 0))
        ctrl_panel.pack_propagate(False)

        lbl_ctrl = criar_label_pai(ctrl_panel, "Calibracao", cor=COR_DESTAQUE, tamanho=14, negrito=True)
        lbl_ctrl.pack(fill="x", padx=20, pady=(15, 5))

        criar_separador(ctrl_panel)

        lbl_pontos = criar_label_pai(ctrl_panel, "Pontos do poligono:", cor=COR_TEXTO, tamanho=11)
        lbl_pontos.pack(fill="x", padx=20, pady=(0, 5))

        self.lbl_contador = tk.Label(
            ctrl_panel,
            text="0 pontos selecionados",
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        )
        self.lbl_contador.pack(fill="x", padx=20, pady=(0, 15))

        btn_add = tk.Button(ctrl_panel, text="Adicionar Ponto (clique na camera)", width=30)
        aplicar_estilo_botao(btn_add, comando=self._adicionar_ponto)
        btn_add.pack(fill="x", padx=20, pady=5, ipady=6)

        btn_limpar = tk.Button(ctrl_panel, text="Limpar Pontos", width=30)
        aplicar_estilo_botao(btn_limpar, comando=self._limpar_pontos)
        btn_limpar.pack(fill="x", padx=20, pady=5, ipady=6)

        criar_separador(ctrl_panel)

        btn_confirmar = tk.Button(ctrl_panel, text="Confirmar Poligono", width=30, height=2)
        aplicar_estilo_botao(btn_confirmar, comando=self._confirmar)
        btn_confirmar.pack(fill="x", padx=20, pady=10, ipady=8)

        btn_voltar = tk.Button(ctrl_panel, text="Voltar", width=30)
        aplicar_estilo_botao(btn_voltar, comando=lambda: self.controle.mostrar_tela("inicial"))
        btn_voltar.pack(fill="x", padx=20, pady=5, ipady=6)

    def _atualizar_contador(self) -> None:
        self.lbl_contador.config(text=f"{len(self.pontos)} pontos selecionados")

    def _adicionar_ponto(self) -> None:
        self.pontos.append((0, 0))
        self._atualizar_contador()

    def _limpar_pontos(self) -> None:
        self.pontos = []
        self.controle.state.poligono_quadra = []
        self._atualizar_contador()

    def _confirmar(self) -> None:
        if len(self.pontos) < 3:
            self.lbl_contador.config(text="Minimo 3 pontos para o poligono.", fg="#E74C3C")
            return
        self.controle.state.poligono_quadra = self.pontos.copy()
        self.controle.mostrar_tela("inicial")

    def mostrar(self) -> None:
        self.frame.pack(fill="both", expand=True)

    def ocultar(self) -> None:
        self.frame.pack_forget()
