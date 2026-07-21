"""Utilitário para carregar prompts a partir de arquivos."""

from __future__ import annotations

from pathlib import Path


def load_prompt(path: Path | str) -> str:
    """Lê um arquivo de prompt e devolve o conteúdo sem espaços nas bordas."""
    return Path(path).read_text(encoding="utf-8").strip()
