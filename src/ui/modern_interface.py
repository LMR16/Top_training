"""Interface moderna, limpa e flat do Top Training usando tkinter.

Layout:
- Janela principal unica
- Coluna esquerda (70%): area da camera / quadra (placeholder)
- Coluna direita (30%): painel de controle com placar, dificuldade e acoes

Tema: dark mode suave, cantos arredondados onde possivel, cores modernas.
"""

import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------------------
# Paleta de cores (moderna / flat / dark)
# ---------------------------------------------------------------------------
COR_FUNDO = "#1A1C23"      # Fundo principal escuro/azulado
COR_PAINEL = "#21242D"     # Fundo dos painéis secundários
COR_BOTAO = "#2980B9"      # Azul profissional
COR_BOTAO_HOVER = "#3498DB"
COR_BOTAO_ATIVO = "#1F618D"
COR_TEXTO = "#DCDCE1"      # Texto suave
COR_TEXTO_MUTADO = "#969CA5"
COR_ACERTO = "#2ECC71"     # Verde suave
COR_ERRO = "#E74C3C"       # Vermelho suave
COR_BORDA = "#3C4150"


class ModernInterface:
    """Construtor da interface principal em tkinter."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Analise de Tenis - UFSC")
        self.root.geometry("1200x700")
        self.root.configure(bg=COR_FUNDO)

        # Remove barras padrão do SO para visual mais limpo (opcional)
        # self.root.overrideredirect(True)  # descomente para sem bordas do SO

        self.acertos = 0
        self.erros = 0

        self._configurar_estilos()
        self._construir_layout()

    def _configurar_estilos(self) -> None:
        """Configura estilos ttk para visual flat/moderno."""
        style = ttk.Style()
        style.theme_use("clam")

        # Estilo para radio buttons
        style.configure(
            "Modern.TRadiobutton",
            background=COR_PAINEL,
            foreground=COR_TEXTO,
            font=("Segoe UI", 10),
            focuscolor=COR_PAINEL,
        )
        style.map(
            "Modern.TRadiobutton",
            background=[("active", COR_PAINEL)],
            foreground=[("active", COR_TEXTO)],
        )

    def _construir_layout(self) -> None:
        # Container principal com duas colunas
        container = tk.Frame(self.root, bg=COR_FUNDO)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # ==================== COLUNA ESQUERDA (70%) ====================
        cam_panel = tk.Frame(container, bg=COR_PAINEL, highlightbackground=COR_BORDA, highlightthickness=1)
        cam_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Título da câmera
        lbl_cam = tk.Label(
            cam_panel,
            text="Camera / Area de Rastreio",
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 16, "bold"),
            anchor="w",
        )
        lbl_cam.pack(fill="x", padx=20, pady=(15, 5))

        # Separador visual
        sep = tk.Frame(cam_panel, bg=COR_BORDA, height=1)
        sep.pack(fill="x", padx=20, pady=(0, 10))

        # Placeholder da camera (640x480)
        self.canvas_camera = tk.Canvas(
            cam_panel,
            width=640,
            height=480,
            bg="#0A0B0F",
            highlightthickness=0,
        )
        self.canvas_camera.pack(padx=20, pady=10)
        self.canvas_camera.create_text(
            320, 240,
            text="Feed da camera sera renderizado aqui...",
            fill="#64646E",
            font=("Segoe UI", 12),
        )

        txt_feed = tk.Label(
            cam_panel,
            text="Aguardando captura de video (Iriun Webcam)...",
            bg=COR_PAINEL,
            fg=COR_TEXTO_MUTADO,
            font=("Segoe UI", 10),
            anchor="w",
        )
        txt_feed.pack(fill="x", padx=20, pady=(0, 15))

        # ==================== COLUNA DIREITA (30%) ====================
        ctrl_panel = tk.Frame(container, bg=COR_PAINEL, width=340, highlightbackground=COR_BORDA, highlightthickness=1)
        ctrl_panel.pack(side="right", fill="y", padx=(10, 0))
        ctrl_panel.pack_propagate(False)  # mantem largura fixa

        lbl_ctrl = tk.Label(
            ctrl_panel,
            text="Painel de Controle",
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 16, "bold"),
            anchor="w",
        )
        lbl_ctrl.pack(fill="x", padx=20, pady=(15, 5))

        sep2 = tk.Frame(ctrl_panel, bg=COR_BORDA, height=1)
        sep2.pack(fill="x", padx=20, pady=(0, 15))

        # --- SESSAO PLACAR ---
        lbl_stats = tk.Label(
            ctrl_panel,
            text="ESTATISTICAS",
            bg=COR_PAINEL,
            fg=COR_TEXTO_MUTADO,
            font=("Segoe UI", 10),
            anchor="w",
        )
        lbl_stats.pack(fill="x", padx=20, pady=(0, 5))

        placar_container = tk.Frame(ctrl_panel, bg=COR_PAINEL)
        placar_container.pack(fill="x", padx=20, pady=(0, 15))

        self.lbl_acertos = tk.Label(
            placar_container,
            text="Acertos: 0",
            bg=COR_PAINEL,
            fg=COR_ACERTO,
            font=("Segoe UI", 14, "bold"),
            anchor="w",
        )
        self.lbl_acertos.pack(anchor="w")

        self.lbl_erros = tk.Label(
            placar_container,
            text="Erros: 0",
            bg=COR_PAINEL,
            fg=COR_ERRO,
            font=("Segoe UI", 14, "bold"),
            anchor="w",
        )
        self.lbl_erros.pack(anchor="w", pady=(5, 0))

        # --- SESSAO DIFICULDADE ---
        lbl_dif = tk.Label(
            ctrl_panel,
            text="DIFICULDADE",
            bg=COR_PAINEL,
            fg=COR_TEXTO_MUTADO,
            font=("Segoe UI", 10),
            anchor="w",
        )
        lbl_dif.pack(fill="x", padx=20, pady=(0, 5))

        self.var_dificuldade = tk.StringVar(value="Basico")
        frame_dif = tk.Frame(ctrl_panel, bg=COR_PAINEL)
        frame_dif.pack(fill="x", padx=20, pady=(0, 25))

        for texto in ["Basico", "Medio", "Avancado"]:
            rb = tk.Radiobutton(
                frame_dif,
                text=texto,
                variable=self.var_dificuldade,
                value=texto,
                bg=COR_PAINEL,
                fg=COR_TEXTO,
                selectcolor=COR_PAINEL,
                activebackground=COR_PAINEL,
                activeforeground=COR_TEXTO,
                font=("Segoe UI", 11),
                indicatoron=0,
                width=12,
                relief="flat",
                highlightthickness=0,
                command=self._on_dificuldade,
            )
            rb.pack(side="left", padx=(0, 8))

        # --- SESSAO ACOES ---
        lbl_acoes = tk.Label(
            ctrl_panel,
            text="ACOES",
            bg=COR_PAINEL,
            fg=COR_TEXTO_MUTADO,
            font=("Segoe UI", 10),
            anchor="w",
        )
        lbl_acoes.pack(fill="x", padx=20, pady=(0, 5))

        botoes = [
            ("Recalibrar Quadra", self._recalibrar),
            ("Salvar Treino", self._salvar_treino),
            ("Trocar Dificuldade", self._trocar_dificuldade),
            ("Sair do Treino", self._sair),
        ]

        for texto, callback in botoes:
            btn = tk.Button(
                ctrl_panel,
                text=texto,
                bg=COR_BOTAO,
                fg="white",
                activebackground=COR_BOTAO_HOVER,
                activeforeground="white",
                font=("Segoe UI", 11, "bold"),
                relief="flat",
                bd=0,
                cursor="hand2",
                command=callback,
            )
            btn.pack(fill="x", padx=20, pady=4, ipady=6)

            # Efeito hover simples
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COR_BOTAO_HOVER))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=COR_BOTAO))

    # ------------------------------------------------------------------
    # Callbacks (placeholders de UI)
    # ------------------------------------------------------------------
    def _on_dificuldade(self) -> None:
        print(f"[UI] Dificuldade selecionada: {self.var_dificuldade.get()}")

    def _recalibrar(self) -> None:
        print("[UI] Recalibrar Quadra")

    def _salvar_treino(self) -> None:
        print("[UI] Salvar Treino")

    def _trocar_dificuldade(self) -> None:
        print("[UI] Trocar Dificuldade")

    def _sair(self) -> None:
        self.root.destroy()

    def atualizar_placar(self, acertos: int, erros: int) -> None:
        """Atualiza os textos de placar na interface."""
        self.acertos = acertos
        self.erros = erros
        self.lbl_acertos.config(text=f"Acertos: {acertos}")
        self.lbl_erros.config(text=f"Erros: {erros}")

    def executar(self) -> None:
        """Inicia o loop principal do tkinter."""
        self.root.mainloop()


def executar() -> None:
    app = ModernInterface()
    app.executar()


if __name__ == "__main__":
    executar()
