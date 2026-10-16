"""Tela de Login / Criacao e Selecao de Perfil do Jogador."""

import tkinter as tk
from src.ui.estilos import (
    COR_FUNDO, COR_PAINEL, COR_BOTAO, COR_BOTAO_HOVER, COR_TEXTO,
    COR_TEXTO_MUTADO, COR_DESTAQUE, COR_ACERTO, COR_ERRO, aplicar_estilo_botao,
    criar_label_pai, criar_separador,
)
from src.data.profiles import ProfileStore


class TelaLogin:
    def __init__(self, pai, controle) -> None:
        self.controle = controle
        self.frame = tk.Frame(pai, bg=COR_FUNDO)
        self._construir()

    def _construir(self) -> None:
        container = tk.Frame(self.frame, bg=COR_FUNDO)
        container.place(relx=0.5, rely=0.5, anchor="center")

        lbl = tk.Label(
            container,
            text="TOP TRAINING",
            bg=COR_FUNDO,
            fg=COR_DESTAQUE,
            font=("Segoe UI", 30, "bold"),
        )
        lbl.pack(pady=(0, 10))

        lbl_sub = tk.Label(
            container,
            text="Analisador de Treino de Tenis",
            bg=COR_FUNDO,
            fg=COR_TEXTO_MUTADO,
            font=("Segoe UI", 13),
        )
        lbl_sub.pack(pady=(0, 40))

        # --- Criar novo perfil ---
        lbl_nome = criar_label_pai(container, "Criar ou selecionar perfil:", cor=COR_TEXTO, tamanho=12, negrito=True)
        lbl_nome.pack(pady=(0, 5))

        self.entrada_nome = tk.Entry(
            container,
            bg="#2A2D38",
            fg=COR_TEXTO,
            insertbackground=COR_TEXTO,
            font=("Segoe UI", 12),
            relief="flat",
            bd=0,
            width=30,
            justify="center",
        )
        self.entrada_nome.pack(pady=(0, 8), ipady=8)

        btn_criar = tk.Button(container, text="Criar / Selecionar Perfil", width=28)
        aplicar_estilo_botao(btn_criar, comando=self._confirmar)
        btn_criar.pack(pady=(0, 20), ipady=8)

        # --- Perfis salvos ---
        lbl_perfis = criar_label_pai(container, "Perfis salvos:", cor=COR_TEXTO_MUTADO, tamanho=11)
        lbl_perfis.pack(pady=(0, 8))

        self.lista_frame = tk.Frame(container, bg=COR_PAINEL, highlightbackground="#3C4150", highlightthickness=1)
        self.lista_frame.pack(pady=(0, 20), padx=10)

        self.btn_perfil_selecionado = None
        self._atualizar_lista_perfis()

    def _atualizar_lista_perfis(self) -> None:
        # Limpa botoes antigos
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        store = ProfileStore()
        perfis = store.listar()

        if not perfis:
            lbl_vazio = tk.Label(
                self.lista_frame,
                text="Nenhum perfil encontrado.",
                bg=COR_PAINEL,
                fg=COR_TEXTO_MUTADO,
                font=("Segoe UI", 10),
            )
            lbl_vazio.pack(pady=10)
            return

        for nome in perfis:
            btn = tk.Button(
                self.lista_frame,
                text=nome,
                width=25,
                bg=COR_PAINEL,
                fg=COR_TEXTO,
                activebackground=COR_BOTAO_HOVER,
                activeforeground="white",
                font=("Segoe UI", 10),
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda n=nome: self._selecionar_perfil_existente(n),
            )
            btn.pack(pady=3, padx=10, ipady=5)

            # Efeito hover
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COR_BOTAO, fg="white"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=COR_PAINEL, fg=COR_TEXTO))

    def _selecionar_perfil_existente(self, nome: str) -> None:
        self.controle.state.perfil_atual = nome
        self.entrada_nome.delete(0, tk.END)
        self.entrada_nome.insert(0, nome)
        # Destaca visualmente o selecionado
        for widget in self.lista_frame.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == nome:
                widget.config(bg=COR_DESTAQUE, fg="white")
            elif isinstance(widget, tk.Button):
                widget.config(bg=COR_PAINEL, fg=COR_TEXTO)

    def _confirmar(self) -> None:
        nome = self.entrada_nome.get().strip()
        if not nome:
            return
        store = ProfileStore()
        if nome not in store.listar():
            store.salvar(nome, {"nome": nome, "vitorias": 0, "treinos": 0})
            self._atualizar_lista_perfis()
        self.controle.state.perfil_atual = nome
        self._selecionar_perfil_existente(nome)
        self.controle.mostrar_tela("inicial")

    def mostrar(self) -> None:
        self.frame.pack(fill="both", expand=True)

    def ocultar(self) -> None:
        self.frame.pack_forget()
