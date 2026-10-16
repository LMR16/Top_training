"""Estilos, cores e utilitários compartilhados da interface."""

import tkinter as tk

# ---------------------------------------------------------------------------
# Paleta de cores (moderna / flat / dark)
# ---------------------------------------------------------------------------
COR_FUNDO = "#1A1C23"      # Fundo principal escuro/azulado
COR_PAINEL = "#21242D"     # Fundo dos paineis secundarios
COR_BOTAO = "#2980B9"      # Azul profissional
COR_BOTAO_HOVER = "#3498DB"
COR_BOTAO_ATIVO = "#1F618D"
COR_TEXTO = "#DCDCE1"      # Texto suave
COR_TEXTO_MUTADO = "#969CA5"
COR_ACERTO = "#2ECC71"     # Verde suave
COR_ERRO = "#E74C3C"       # Vermelho suave
COR_BORDA = "#3C4150"
COR_DESTAQUE = "#1ABC9C"


def aplicar_estilo_botao(widget, comando=None):
    """Aplica estilo flat a um botao tkinter."""
    widget.configure(
        bg=COR_BOTAO,
        fg="white",
        activebackground=COR_BOTAO_HOVER,
        activeforeground="white",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
        command=comando,
    )
    widget.bind("<Enter>", lambda e: widget.config(bg=COR_BOTAO_HOVER))
    widget.bind("<Leave>", lambda e: widget.config(bg=COR_BOTAO))
    return widget


def criar_label_pai(pai, texto, cor=COR_TEXTO, tamanho=11, negrito=False, anchor="w"):
    """Cria um Label com estilo padrao."""
    lbl = tk.Label(
        pai,
        text=texto,
        bg=COR_PAINEL,
        fg=cor,
        font=("Segoe UI", tamanho, "bold" if negrito else "normal"),
        anchor=anchor,
    )
    return lbl


def criar_separador(pai):
    """Cria uma linha separadora sutil."""
    sep = tk.Frame(pai, bg=COR_BORDA, height=1)
    sep.pack(fill="x", padx=20, pady=(0, 15))
    return sep
