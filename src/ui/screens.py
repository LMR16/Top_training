"""Telas (Views) da aplicacao Top Training - Treino Real com Camera.

Cada tela herda de ctk.CTkFrame e recebe o Controller para troca de telas.
"""

from __future__ import annotations

import os
import cv2
from typing import TYPE_CHECKING, Optional, List, Tuple

import customtkinter as ctk
from PIL import Image

from src.cv.pipeline import CVPPipeline

if TYPE_CHECKING:
    from src.ui.app import AppController


# ---------------------------------------------------------------------------
# Configuracao visual global
# ---------------------------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COR_FUNDO = "#1A1A2E"
COR_TEXTO_DESTAQUE = "#00D4FF"
COR_ACERTO = "#00FF88"
COR_ERRO = "#FF4444"

INPUT_VIDEOS_DIR = os.path.join(os.path.dirname(__file__), "..", "input_videos")


def frame_to_ctkimage(frame, width: int, height: int) -> ctk.CTkImage:
    """Converte frame OpenCV (BGR) para CTkImage."""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(frame_rgb)
    pil_image = pil_image.resize((width, height), Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(width, height))


# ===========================================================================
# 1. MenuScreen - Login / Criacao de Perfil
# ===========================================================================
class MenuScreen(ctk.CTkFrame):
    """Tela de login: criar ou selecionar perfil do jogador."""

    def __init__(self, parent: ctk.CTk, controller: "AppController") -> None:
        super().__init__(parent, fg_color=COR_FUNDO)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            container,
            text="TOP TRAINING",
            font=ctk.CTkFont(family="Segoe UI", size=30, weight="bold"),
            text_color=COR_TEXTO_DESTAQUE,
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            container,
            text="Analisador de Treino de Tenis",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#888888",
        ).pack(pady=(0, 40))

        ctk.CTkLabel(
            container, text="Nome do Jogador",
            font=ctk.CTkFont(family="Segoe UI", size=12),
        ).pack(pady=(0, 8))

        self.entry_nome = ctk.CTkEntry(
            container,
            width=280, height=40,
            placeholder_text="Digite seu nome...",
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        self.entry_nome.pack(pady=(0, 20))

        ctk.CTkButton(
            container,
            text="Criar / Selecionar Perfil",
            width=280, height=45,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            command=self._ao_confirmar,
        ).pack(pady=(0, 10), ipady=2)

        # Lista de perfis salvos
        self.lbl_perfis = ctk.CTkLabel(
            container, text="Perfis salvos:",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#888888",
        )
        self.lbl_perfis.pack(pady=(20, 5))

        self.lista_frame = ctk.CTkFrame(container, fg_color="#161625", corner_radius=8)
        self.lista_frame.pack(pady=(0, 20), padx=10, fill="x")

        self._atualizar_lista_perfis()

    def _atualizar_lista_perfis(self) -> None:
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        from src.data.profiles import ProfileStore
        store = ProfileStore()
        perfis = store.listar()

        if not perfis:
            ctk.CTkLabel(
                self.lista_frame, text="Nenhum perfil encontrado.",
                font=ctk.CTkFont(size=11), text_color="#888888",
            ).pack(pady=10)
            return

        for nome in perfis:
            btn = ctk.CTkButton(
                self.lista_frame, text=nome, width=200, height=32,
                font=ctk.CTkFont(size=12),
                fg_color="#161625", hover_color="#2A2D38",
                text_color="#CCCCCC",
                command=lambda n=nome: self._selecionar_perfil(n),
            )
            btn.pack(pady=3, padx=10)

    def _selecionar_perfil(self, nome: str) -> None:
        self.entry_nome.delete(0, "end")
        self.entry_nome.insert(0, nome)

    def _ao_confirmar(self) -> None:
        nome = self.entry_nome.get().strip()
        if not nome:
            return
        from src.data.profiles import ProfileStore
        store = ProfileStore()
        if nome not in store.listar():
            store.salvar(nome, {"nome": nome, "vitorias": 0, "treinos": 0})
            self._atualizar_lista_perfis()
        self.controller.jogador_nome = nome
        self.controller.show_frame(InicialScreen)


# ===========================================================================
# 2. InicialScreen - Menu Inicial
# ===========================================================================
class InicialScreen(ctk.CTkFrame):
    """Menu inicial: iniciar treino, recalibrar quadra, gerenciar perfis."""

    def __init__(self, parent: ctk.CTk, controller: "AppController") -> None:
        super().__init__(parent, fg_color=COR_FUNDO)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            container, text="MENU INICIAL",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=COR_TEXTO_DESTAQUE,
        ).pack(pady=(0, 20))

        ctk.CTkLabel(
            container, text="Selecione uma opcao:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#888888",
        ).pack(pady=(0, 40))

        botoes = [
            ("Iniciar Treino", lambda: self.controller.show_frame(TreinoScreen)),
            ("Recalibrar Quadra", lambda: self.controller.show_frame(CalibracaoScreen)),
            ("Gerenciar Perfis", lambda: self.controller.show_frame(MenuScreen)),
            ("Sair", self.controller.quit),
        ]

        for texto, comando in botoes:
            ctk.CTkButton(
                container, text=texto, width=260, height=40,
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                command=comando,
            ).pack(pady=10)


# ===========================================================================
# 3. CalibracaoScreen - Mapeamento da Quadra
# ===========================================================================
class CalibracaoScreen(ctk.CTkFrame):
    """Tela de calibracao: video da camera e selecao de vertices do poligono."""

    def __init__(self, parent: ctk.CTk, controller: "AppController") -> None:
        super().__init__(parent, fg_color=COR_FUNDO)
        self.controller = controller
        self.pipeline = CVPPipeline()
        self.cap: Optional[cv2.VideoCapture] = None
        self.playing = False
        self.after_id: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        # Esquerda: video
        self.video_panel = ctk.CTkFrame(main, fg_color="#0A0A0F", corner_radius=12)
        self.video_panel.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        self.video_panel.grid_columnconfigure(0, weight=1)
        self.video_panel.grid_rowconfigure(0, weight=1)

        self.video_label = ctk.CTkLabel(
            self.video_panel,
            text="FEED DA CAMERA (Iriun Webcam)\n\n"
                 "Clique no video para definir os vertices do poligono da quadra.\n"
                 "Minimo 3 pontos necessarios.",
            width=800, height=520,
            fg_color="#050508", corner_radius=10,
            text_color="#666666",
            font=ctk.CTkFont(family="Segoe UI", size=14),
        )
        self.video_label.grid(row=0, column=0, pady=20, padx=20, sticky="nsew")
        self.video_label.bind("<Button-1>", self._ao_clicar_video)

        self.btn_camera = ctk.CTkButton(
            self.video_panel, text="Iniciar Camera",
            width=200, height=36, command=self._iniciar_camera,
        )
        self.btn_camera.grid(row=1, column=0, pady=(0, 10))

        self.lbl_pontos = ctk.CTkLabel(
            self.video_panel, text="Pontos: 0",
            font=ctk.CTkFont(size=12), text_color="#888888",
        )
        self.lbl_pontos.grid(row=2, column=0, pady=(0, 20))

        # Direita: controles
        self.ctrl_panel = ctk.CTkFrame(main, fg_color="#161625", corner_radius=12, width=320)
        self.ctrl_panel.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        self.ctrl_panel.grid_propagate(False)
        self.ctrl_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.ctrl_panel, text="Calibracao da Quadra",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COR_TEXTO_DESTAQUE,
        ).pack(pady=(25, 10))

        ctk.CTkLabel(
            self.ctrl_panel,
            text="1. Inicie a camera\n"
                 "2. Clique no video para marcar vertices\n"
                 "3. Confirme o poligono",
            font=ctk.CTkFont(size=12), text_color="#CCCCCC",
            justify="left",
        ).pack(pady=(0, 20), padx=20)

        self.btn_limpar = ctk.CTkButton(
            self.ctrl_panel, text="Limpar Pontos",
            width=200, height=40, command=self._limpar_pontos,
        )
        self.btn_limpar.pack(pady=8)

        self.btn_confirmar = ctk.CTkButton(
            self.ctrl_panel, text="Confirmar Mapeamento",
            width=200, height=45,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            command=self._ao_confirmar, state="disabled",
        )
        self.btn_confirmar.pack(pady=15)

        ctk.CTkButton(
            self.ctrl_panel, text="Voltar ao Menu",
            width=200, height=40,
            fg_color="#444444", hover_color="#555555",
            command=lambda: self.controller.show_frame(InicialScreen),
        ).pack(pady=8)

    # ------------------------------------------------------------------
    # Logica
    # ------------------------------------------------------------------
    def _iniciar_camera(self) -> None:
        """Tenta abrir a camera (indice 0 = Iriun Webcam)."""
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.video_label.configure(text="Nao foi possivel abrir a camera.\nVerifique o Iriun Webcam.")
            return
        self.playing = True
        self.btn_camera.configure(text="Camera Ativa")
        self._atualizar_frame()

    def _atualizar_frame(self) -> None:
        if not self.playing or self.cap is None:
            return
        ret, frame = self.cap.read()
        if not ret:
            return

        # Anota pontos do poligono no frame
        annotated = frame.copy()
        pts = self.pipeline.court.polygon
        if len(pts) >= 2:
            import numpy as np
            pts_arr = np.array(pts, np.int32).reshape((-1, 1, 2))
            cv2.polylines(annotated, [pts_arr], isClosed=True, color=(0, 255, 255), thickness=2)
        for p in pts:
            cv2.circle(annotated, p, 6, (0, 255, 255), -1)

        ctk_img = frame_to_ctkimage(annotated, 800, 520)
        self.video_label.configure(image=ctk_img, text="")
        self.video_label.image = ctk_img

        self.lbl_pontos.configure(text=f"Pontos: {len(pts)}")
        if len(pts) >= 3:
            self.btn_confirmar.configure(state="normal")

        self.after_id = self.after(33, self._atualizar_frame)

    def _ao_clicar_video(self, event) -> None:
        if self.cap is None:
            return
        x, y = event.x, event.y
        frame_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        label_w, label_h = 800, 520
        fx = int(x * frame_w / label_w)
        fy = int(y * frame_h / label_h)
        self.pipeline.court.add_point(fx, fy)

    def _limpar_pontos(self) -> None:
        self.pipeline.court.clear()
        self.lbl_pontos.configure(text="Pontos: 0")
        self.btn_confirmar.configure(state="disabled")

    def _ao_confirmar(self) -> None:
        if len(self.pipeline.court.polygon) < 3:
            return
        self.pipeline.court.finalize()
        self.controller.pipeline = self.pipeline
        self.controller.show_frame(TreinoScreen)

    def _parar_camera(self) -> None:
        self.playing = False
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def destruir(self) -> None:
        self._parar_camera()

    def mostrar(self) -> None:
        self.grid(row=0, column=0, sticky="nsew")

    def ocultar(self) -> None:
        self._parar_camera()
        self.grid_forget()


# ===========================================================================
# 4. TreinoScreen - Dashboard Principal
# ===========================================================================
class TreinoScreen(ctk.CTkFrame):
    """Dashboard principal do treino: video (70%) + painel controle (30%)."""

    def __init__(self, parent: ctk.CTk, controller: "AppController") -> None:
        super().__init__(parent, fg_color=COR_FUNDO)
        self.controller = controller
        self.pipeline = getattr(controller, "pipeline", None) or CVPPipeline()
        self.cap: Optional[cv2.VideoCapture] = None
        self.playing = False
        self.after_id: Optional[str] = None

        self.acertos = 0
        self.erros = 0
        self.quiques: List[dict] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.grid_columnconfigure(0, weight=7)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # Esquerda: video + mapa 2D
        self.left_panel = ctk.CTkFrame(self, fg_color="#0A0A0F", corner_radius=12)
        self.left_panel.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(1, weight=1)
        self.left_panel.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self.left_panel, text="FEED DA CAMERA / DETECCAO",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COR_TEXTO_DESTAQUE,
        ).grid(row=0, column=0, pady=(15, 10))

        self.canvas_video = ctk.CTkLabel(
            self.left_panel, text="Aguardando camera...",
            width=700, height=340,
            fg_color="#050508", corner_radius=10,
            text_color="#555555", font=ctk.CTkFont(size=13),
        )
        self.canvas_video.grid(row=1, column=0, pady=(0, 10), padx=20, sticky="nsew")

        ctk.CTkLabel(
            self.left_panel, text="MAPA 2D DA QUADRA",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COR_TEXTO_DESTAQUE,
        ).grid(row=2, column=0, pady=(10, 5))

        self.canvas_mapa = ctk.CTkLabel(
            self.left_panel, text="Mapa sera renderizado aqui",
            width=700, height=180,
            fg_color="#050508", corner_radius=10,
            text_color="#555555", font=ctk.CTkFont(size=12),
        )
        self.canvas_mapa.grid(row=3, column=0, pady=(0, 20), padx=20, sticky="nsew")

        # Direita: painel controle
        self.right_panel = ctk.CTkFrame(self, fg_color="#161625", corner_radius=12)
        self.right_panel.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        self.right_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.right_panel, text="Painel de Controle",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COR_TEXTO_DESTAQUE,
        ).pack(pady=(20, 10))

        self.lbl_perfil = ctk.CTkLabel(
            self.right_panel,
            text=f"Perfil: {self.controller.jogador_nome or '-'}",
            font=ctk.CTkFont(size=13), text_color="#CCCCCC",
        )
        self.lbl_perfil.pack(pady=(0, 5))

        self.lbl_dificuldade = ctk.CTkLabel(
            self.right_panel,
            text=f"Dificuldade: {self.controller.state_dificuldade}",
            font=ctk.CTkFont(size=13), text_color="#F1C40F",
        )
        self.lbl_dificuldade.pack(pady=(0, 20))

        # Placar
        frame_placar = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        frame_placar.pack(pady=(0, 20), padx=20, fill="x")

        ctk.CTkLabel(
            frame_placar, text="ACERTOS",
            font=ctk.CTkFont(size=12), text_color=COR_ACERTO,
        ).pack()
        self.lbl_acertos = ctk.CTkLabel(
            frame_placar, text="0",
            font=ctk.CTkFont(size=32, weight="bold"), text_color=COR_ACERTO,
        )
        self.lbl_acertos.pack(pady=(0, 15))

        ctk.CTkLabel(
            frame_placar, text="ERROS",
            font=ctk.CTkFont(size=12), text_color=COR_ERRO,
        ).pack()
        self.lbl_erros = ctk.CTkLabel(
            frame_placar, text="0",
            font=ctk.CTkFont(size=32, weight="bold"), text_color=COR_ERRO,
        )
        self.lbl_erros.pack(pady=(0, 30))

        # Botoes
        btn_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        btn_frame.pack(pady=(30, 20), padx=20, fill="x")

        ctk.CTkButton(
            btn_frame, text="Recalibrar Quadra", width=200, height=40,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._ao_recalibrar,
        ).pack(pady=8)

        ctk.CTkButton(
            btn_frame, text="Finalizar Treino", width=200, height=40,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#444444", hover_color="#555555",
            command=self._ao_finalizar,
        ).pack(pady=8)

    # ------------------------------------------------------------------
    # Logica de treino
    # ------------------------------------------------------------------
    def _iniciar_camera(self) -> None:
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.canvas_video.configure(text="Nao foi possivel abrir a camera.")
            return
        self.playing = True
        self._atualizar_frame()

    def _atualizar_frame(self) -> None:
        if not self.playing or self.cap is None or self.pipeline is None:
            return
        ret, frame = self.cap.read()
        if not ret:
            return

        result = self.pipeline.process_frame(frame)
        annotated = result["annotated_frame"]
        center = result["ball_center"]
        bounce = result["bounce_detected"]
        inside = result["inside_court"]

        ctk_img = frame_to_ctkimage(annotated, 700, 340)
        self.canvas_video.configure(image=ctk_img, text="")
        self.canvas_video.image = ctk_img

        if bounce and center is not None:
            dentro = inside
            if dentro:
                self.acertos += 1
            else:
                self.erros += 1
            self.quiques.append({"x": center[0], "y": center[1], "acerto": dentro})
            self.atualizar_placar(self.acertos, self.erros)
            self._desenhar_quique(center[0], center[1], dentro)

        self.after_id = self.after(33, self._atualizar_frame)

    def _desenhar_quique(self, x: int, y: int, acerto: bool) -> None:
        cor = COR_ACERTO if acerto else COR_ERRO
        texto = f"Quique: {'ACERTO' if acerto else 'ERRO'} em ({x}, {y})\n"
        atual = self.canvas_mapa.cget("text")
        self.canvas_mapa.configure(text=texto + atual, text_color=cor)

    def atualizar_placar(self, acertos: int, erros: int) -> None:
        self.acertos = acertos
        self.erros = erros
        self.lbl_acertos.configure(text=str(acertos))
        self.lbl_erros.configure(text=str(erros))

    def _ao_recalibrar(self) -> None:
        self._parar_camera()
        self.controller.show_frame(CalibracaoScreen)

    def _ao_finalizar(self) -> None:
        self._parar_camera()
        self.controller.show_frame(InicialScreen)

    def _parar_camera(self) -> None:
        self.playing = False
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def destruir(self) -> None:
        self._parar_camera()

    def mostrar(self) -> None:
        self._iniciar_camera()
        self.grid(row=0, column=0, sticky="nsew")

    def ocultar(self) -> None:
        self._parar_camera()
        self.grid_forget()


__all__ = ["MenuScreen", "InicialScreen", "CalibracaoScreen", "TreinoScreen"]
