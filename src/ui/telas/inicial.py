"""Tela Inicial / Menu Principal."""

import tkinter as tk
from src.ui.estilos import (
    COR_FUNDO, COR_PAINEL, COR_BOTAO, COR_BOTAO_HOVER, COR_TEXTO,
    COR_TEXTO_MUTADO, COR_DESTAQUE, aplicar_estilo_botao, criar_label_pai,
    criar_separador,
)


class TelaInicial:
    def __init__(self, pai, controle) -> None:
        self.controle = controle
        self.frame = tk.Frame(pai, bg=COR_FUNDO)
        self._construir()

    def _construir(self) -> None:
        container = tk.Frame(self.frame, bg=COR_FUNDO)
        container.place(relx=0.5, rely=0.5, anchor="center")

        lbl = tk.Label(
            container,
            text="MENU INICIAL",
            bg=COR_FUNDO,
            fg=COR_DESTAQUE,
            font=("Segoe UI", 26, "bold"),
        )
        lbl.pack(pady=(0, 20))

        lbl_sub = tk.Label(
            container,
            text="Selecione uma opcao abaixo:",
            bg=COR_FUNDO,
            fg=COR_TEXTO_MUTADO,
            font=("Segoe UI", 12),
        )
        lbl_sub.pack(pady=(0, 40))

        botoes = [
            ("Iniciar Treino", lambda: self.controle.mostrar_tela("dificuldade")),
            ("Recalibrar Quadra", lambda: self.controle.mostrar_tela("calibracao")),
            ("Gerenciar Perfis", lambda: self.controle.mostrar_tela("login")),
            ("Sair", self.controle.sair),
        ]

        for texto, comando in botoes:
            btn = tk.Button(container, text=texto, width=26)
            aplicar_estilo_botao(btn, comando=comando)
            btn.pack(pady=10, ipady=8)

    def mostrar(self) -> None:
        self.frame.pack(fill="both", expand=True)

    def ocultar(self) -> None:
        self.frame.pack_forget()
