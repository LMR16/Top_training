"""Tela de Selecao de Dificuldade e Lado.

Mostra 3 quadras (uma ao lado da outra) representando as areas da quadra.
Em baixo ficam os botoes de dificuldade. Ao selecionar uma dificuldade,
o usuario escolhe o lado que quer acertar (esquerda / centro / direita).
"""

import tkinter as tk
from src.ui.estilos import (
    COR_FUNDO, COR_PAINEL, COR_BOTAO, COR_BOTAO_HOVER, COR_TEXTO,
    COR_TEXTO_MUTADO, COR_DESTAQUE, COR_ACERTO, COR_ERRO, aplicar_estilo_botao,
    criar_label_pai, criar_separador,
)


class TelaDificuldade:
    def __init__(self, pai, controle) -> None:
        self.controle = controle
        self.frame = tk.Frame(pai, bg=COR_FUNDO)
        self.dificuldade_selecionada = "Basico"
        self.lado_selecionado = None
        self.botoes_lado = {}
        self._construir()

    def _construir(self) -> None:
        container = tk.Frame(self.frame, bg=COR_FUNDO)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Titulo
        lbl = tk.Label(
            container,
            text="SELECIONE A DIFICULDADE E O LADO",
            bg=COR_FUNDO,
            fg=COR_DESTAQUE,
            font=("Segoe UI", 18, "bold"),
        )
        lbl.pack(pady=(0, 10))

        lbl_sub = tk.Label(
            container,
            text="Cada dificuldade divide a quadra em mais zonas alvo (mais dificil).",
            bg=COR_FUNDO,
            fg=COR_TEXTO_MUTADO,
            font=("Segoe UI", 11),
        )
        lbl_sub.pack(pady=(0, 20))

        # ===== 3 Quadras lado a lado =====
        quadras_frame = tk.Frame(container, bg=COR_FUNDO)
        quadras_frame.pack(pady=(0, 30))

        nomes_quadras = ["Esquerda", "Centro", "Direita"]
        for nome in nomes_quadras:
            self._criar_quadra(quadras_frame, nome)

        # ===== Dificuldades em baixo =====
        lbl_dif = criar_label_pai(container, "DIFICULDADE", cor=COR_TEXTO, tamanho=12, negrito=True)
        lbl_dif.pack(pady=(0, 10))

        dif_frame = tk.Frame(container, bg=COR_FUNDO)
        dif_frame.pack()

        botoes_dif = [
            ("Basico", "Basico", 3),
            ("Medio", "Medio", 5),
            ("Avancado", "Avancado", 7),
        ]
        for texto, valor, zonas in botoes_dif:
            btn = tk.Button(
                dif_frame,
                text=f"{texto}\n({zonas} zonas)",
                width=14,
                height=3,
                bg=COR_PAINEL,
                fg=COR_TEXTO,
                activebackground=COR_BOTAO_HOVER,
                activeforeground="white",
                font=("Segoe UI", 10, "bold"),
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda v=valor: self._selecionar_dificuldade(v),
            )
            btn.pack(side="left", padx=8, ipady=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COR_BOTAO, fg="white"))
            btn.bind("<Leave>", lambda e, b=btn, v=valor: b.config(
                bg=COR_BOTAO if v == self.dificuldade_selecionada else COR_PAINEL,
                fg="white" if v == self.dificuldade_selecionada else COR_TEXTO,
            ))

        # Destaca a dificuldade padrao
        self._atualizar_visual_dificuldade()

        # ===== Botoes de acao =====
        btn_frame = tk.Frame(container, bg=COR_FUNDO)
        btn_frame.pack(pady=(30, 0))

        btn_iniciar = tk.Button(btn_frame, text="INICIAR TREINO", width=20, height=2)
        aplicar_estilo_botao(btn_iniciar, comando=self._iniciar)
        btn_iniciar.pack(pady=5, ipady=8)

        btn_voltar = tk.Button(btn_frame, text="Voltar", width=20)
        aplicar_estilo_botao(btn_voltar, comando=lambda: self.controle.mostrar_tela("inicial"))
        btn_voltar.pack(pady=5, ipady=6)

    def _criar_quadra(self, pai, nome) -> None:
        """Cria uma representacao visual de quadra (canvas com retangulo)."""
        panel = tk.Frame(pai, bg=COR_PAINEL, highlightbackground="#3C4150", highlightthickness=1)
        panel.pack(side="left", padx=10, pady=5)

        lbl = tk.Label(
            panel,
            text=nome,
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 12, "bold"),
        )
        lbl.pack(pady=(10, 5))

        canvas = tk.Canvas(panel, width=140, height=180, bg="#0A0B0F", highlightthickness=0)
        canvas.pack(padx=10, pady=(0, 10))

        # Desenha a quadra (metade: rede ao meio, linha de fundo)
        cx = 70
        canvas.create_line(cx, 20, cx, 160, fill="#3C4150", width=2)  # rede
        canvas.create_line(20, 20, 120, 20, fill="#3C4150", width=2)  # linha cima
        canvas.create_line(20, 160, 120, 160, fill="#3C4150", width=2)  # linha baixo

        # Zona alvo destacada (inicialmente cinza)
        ret = canvas.create_rectangle(30, 40, 110, 140, fill="#3C4150", outline="#666666", width=1)
        canvas.create_text(70, 90, text="Zona", fill="#666666", font=("Segoe UI", 9))

        # Botao para selecionar este lado
        btn = tk.Button(panel, text="SELECIONAR LADO", width=16)
        aplicar_estilo_botao(btn, comando=lambda n=nome.lower(): self._selecionar_lado(n))
        btn.pack(pady=(5, 10), ipady=4)

        self.botoes_lado[nome.lower()] = {
            "panel": panel,
            "canvas": canvas,
            "ret": ret,
            "btn": btn,
        }

    def _selecionar_lado(self, lado: str) -> None:
        self.lado_selecionado = lado
        # Atualiza visual dos botoes de lado
        for chave, dados in self.botoes_lado.items():
            if chave == lado:
                dados["canvas"].itemconfig(dados["ret"], fill=COR_DESTAQUE, outline=COR_DESTAQUE)
                dados["btn"].config(bg=COR_DESTAQUE, fg="white")
            else:
                dados["canvas"].itemconfig(dados["ret"], fill="#3C4150", outline="#666666")
                dados["btn"].config(bg=COR_BOTAO, fg="white")
        print(f"[UI] Lado selecionado: {lado}")

    def _selecionar_dificuldade(self, valor: str) -> None:
        self.dificuldade_selecionada = valor
        self.controle.state.dificuldade = valor
        self._atualizar_visual_dificuldade()
        print(f"[UI] Dificuldade selecionada: {valor}")

    def _atualizar_visual_dificuldade(self) -> None:
        # Recria os botoes de dificuldade para destacar o selecionado
        # (simples: apenas imprime; o destaque visual fica por conta do bind)
        pass

    def _iniciar(self) -> None:
        if not self.controle.state.perfil_atual:
            print("[UI] Selecione um perfil primeiro.")
            return
        if not self.lado_selecionado:
            print("[UI] Selecione um lado para iniciar.")
            return
        self.controle.state.reset_placar()
        self.controle.mostrar_tela("treino")

    def mostrar(self) -> None:
        self.frame.pack(fill="both", expand=True)

    def ocultar(self) -> None:
        self.frame.pack_forget()
