"""Persistencia de sessoes de treino (JSON)."""

import json
from datetime import datetime
from pathlib import Path


class SessionStore:
    def __init__(self, directory="src/data/sessions"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def salvar(self, perfil_nome, dificuldade, acertos, erros, pontuacao, quiques):
        dados = {
            "perfil": perfil_nome,
            "dificuldade": dificuldade,
            "data": datetime.now().isoformat(),
            "acertos": acertos,
            "erros": erros,
            "pontuacao": pontuacao,
            "quiques": quiques,
        }
        arquivo = self.directory / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return dados

    def listar(self):
        sessoes = []
        for arquivo in sorted(self.directory.glob("*.json"), reverse=True):
            with open(arquivo, "r", encoding="utf-8") as f:
                sessoes.append(json.load(f))
        return sessoes
