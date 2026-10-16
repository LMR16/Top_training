"""Persistencia de perfis de jogadores (JSON)."""

import json
from pathlib import Path


class ProfileStore:
    def __init__(self, directory="src/data/profiles"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _caminho(self, nome):
        return self.directory / f"{nome}.json"

    def salvar(self, nome, dados):
        caminho = self._caminho(nome)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def carregar(self, nome):
        caminho = self._caminho(nome)
        if not caminho.exists():
            return None
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)

    def listar(self):
        return [p.stem for p in self.directory.glob("*.json")]
