"""Tela de Treino (interface principal com camera, mapa 2D e placar)."""

import tkinter as tk
from src.ui.estilos import (
    COR_FUNDO, COR_PAINEL, COR_BOTAO, COR_BOTAO_HOVER, COR_TEXTO,
    COR_TEXTO_MUTADO, COR_DESTAQUE, COR_ACERTO, COR_ERRO, aplicar_estilo_botao,
    criar_label_pai, criar_separador,
)
from src.data.sessions import SessionStore


class TelaTreino:
    def __init__(self, pai, controle) -> None:
        self.controle = controle
        self.frame = tk.Frame(pai, bg=COR_FUNDO)
        self.acertos = 0
        self.erros = 0
        self.quiques = []
        self._construir()

    def _construir(self) -> None:
        container = tk.Frame(self.frame, bg=COR_FUNDO)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # ===== Barra superior =====
        barra = tk.Frame(container, bg=COR_PAINEL, highlightbackground="#3C4150", highlightthickness=1)
        barra.pack(fill="x", pady=(0, 10))

        lbl_perfil = criar_label_pai(
            barra,
            f"Perfil: {self.controle.state.perfil_atual or '-'}",
            cor=COR_DESTAQUE, tamanho=12, negrito=True,
        )
        lbl_perfil.pack(side="left", padx=20, pady=10)

        lbl_dif = criar_label_pai(
            barra,
            f"Dificuldade: {self.controle.state.dificuldade}",
            cor="#F1C40F", tamanho=12, negrito=True,
        )
        lbl_dif.pack(side="left", padx=40, pady=10)

        lbl_lado = criar_label_pai(
            barra,
            f"Lado: {(self.controle.state.lado_selecionado or '-').title()}",
            cor=COR_ACERTO, tamanho=12, negrito=True,
        )
        lbl_lado.pack(side="left", padx=40, pady=10)

        btn_voltar = tk.Button(barra, text="Voltar", width=12)
        aplicar_estilo_botao(btn_voltar, comando=lambda: self.controle.mostrar_tela("dificuldade"))
        btn_voltar.pack(side="right", padx=10, pady=8, ipady=4)

        btn_salvar = tk.Button(barra, text="Salvar Treino", width=14)
        aplicar_estilo_botao(btn_salvar, comando=self._salvar)
        btn_salvar.pack(side="right", padx=10, pady=8, ipady=4)

        # ===== Area principal (3 colunas) =====
        area = tk.Frame(container, bg=COR_FUNDO)
        area.pack(fill="both", expand=True)

        # --- Coluna esquerda: Mapa 2D (40%) ---
        mapa_panel = tk.Frame(area, bg=COR_PAINEL, highlightbackground="#3C4150", highlightthickness=1)
        mapa_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        lbl_mapa = criar_label_pai(mapa_panel, "Mapa 2D da Quadra", cor=COR_DESTAQUE, tamanho=13, negrito=True)
        lbl_mapa.pack(fill="x", padx=20, pady=(15, 5))

        self.canvas_mapa = tk.Canvas(mapa_panel, width=420, height=560, bg="#0A0B0F", highlightthickness=0)
        self.canvas_mapa.pack(padx=20, pady=10)
        self._desenhar_quadra()

        # --- Coluna centro: Camera (40%) ---
        cam_panel = tk.Frame(area, bg=COR_PAINEL, highlightbackground="#3C4150", highlightthickness=1)
        cam_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        lbl_cam = criar_label_pai(cam_panel, "Feed da Camera", cor=COR_DESTAQUE, tamanho=13, negrito=True)
        lbl_cam.pack(fill="x", padx=20, pady=(15, 5))

        self.canvas_camera = tk.Canvas(cam_panel, width=640, height=480, bg="#0A0B0F", highlightthickness=0)
        self.canvas_camera.pack(padx=20, pady=10)
        self.canvas_camera.create_text(
            320, 240,
            text="Feed da camera sera renderizado aqui",
            fill="#64646E",
            font=("Segoe UI", 12),
        )

        # --- Coluna direita: Painel de controle (20%) ---
        ctrl_panel = tk.Frame(area, bg=COR_PAINEL, width=260, highlightbackground="#3C4150", highlightthickness=1)
        ctrl_panel.pack(side="right", fill="y", padx=(10, 0))
        ctrl_panel.pack_propagate(False)

        lbl_ctrl = criar_label_pai(ctrl_panel, "Painel de Placar", cor=COR_DESTAQUE, tamanho=13, negrito=True)
        lbl_ctrl.pack(fill="x", padx=20, pady=(15, 5))

        criar_separador(ctrl_panel)

        self.lbl_acertos = tk.Label(
            ctrl_panel,
            text="Acertos: 0",
            bg=COR_PAINEL,
            fg=COR_ACERTO,
            font=("Segoe UI", 16, "bold"),
            anchor="w",
        )
        self.lbl_acertos.pack(fill="x", padx=20, pady=(0, 5))

        self.lbl_erros = tk.Label(
            ctrl_panel,
            text="Erros: 0",
            bg=COR_PAINEL,
            fg=COR_ERRO,
            font=("Segoe UI", 16, "bold"),
            anchor="w",
        )
        self.lbl_erros.pack(fill="x", padx=20, pady=(0, 25))

        lbl_quiques = criar_label_pai(ctrl_panel, "Quiques recentes:", cor=COR_TEXTO_MUTADO, tamanho=10)
        lbl_quiques.pack(fill="x", padx=20, pady=(0, 5))

        self.lbl_lista_quiques = tk.Label(
            ctrl_panel,
            text="Nenhum",
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 10),
            anchor="w",
            justify="left",
        )
        self.lbl_lista_quiques.pack(fill="x", padx=20, pady=(0, 20))

    def _desenhar_quadra(self) -> None:
        c = self.canvas_mapa
        cx = 210
        c.create_line(cx, 20, cx, 540, fill="#3C4150", width=2)  # rede
        c.create_line(40, 40, 380, 40, fill="#3C4150", width=2)  # linha cima
        c.create_line(40, 520, 380, 520, fill="#3C4150", width=2)  # linha baixo

    def _salvar(self) -> None:
        store = SessionStore()
        store.salvar(
            perfil_nome=self.controle.state.perfil_atual or "desconhecido",
            dificuldade=self.controle.state.dificuldade,
            acertos=self.acertos,
            erros=self.erros,
            pontuacao=self.acertos - self.erros,
            quiques=self.quiques,
        )
        self.lbl_lista_quiques.config(text="Treino salvo com sucesso.", fg=COR_DESTAQUE)

    def atualizar_placar(self, acertos: int, erros: int) -> None:
        self.acertos = acertos
        self.erros = erros
        self.lbl_acertos.config(text=f"Acertos: {acertos}")
        self.lbl_erros.config(text=f"Erros: {erros}")

    def adicionar_quique(self, x: int, y: int, dentro_zona: bool) -> None:
        cor = "#2ECC71" if dentro_zona else "#E74C3C"
        self.canvas_mapa.create_oval(x-6, y-6, x+6, y+6, fill=cor, outline="")
        self.quiques.append({"x": x, "y": y, "acerto": dentro_zona})
        self.lbl_lista_quiques.config(
            text=f"Ultimo quique: {'Acerto' if dentro_zona else 'Erro'}",
            fg=cor,
        )

    def mostrar(self) -> None:
        self.frame.pack(fill="both", expand=True)

    def ocultar(self) -> None:
        self.frame.pack_forget()
