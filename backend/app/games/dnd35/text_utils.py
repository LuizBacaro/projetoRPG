"""
Normalização de texto para classes e listas de magia (D&D 3.5).

Usado por routers, repositórios e services do pacote `app.games.dnd35`.
"""

import re
import unicodedata

# Aliases canônicos de classe — mapeiam variantes para o nome normalizado no contexto de acesso
# (ex.: Feiticeiro usa lista de magias do Mago em D&D 3.5)
_ALIASES_ACESSO: dict[str, str] = {
    "FEITICEIRO": "MAGO",
    "PATRULHEIRO": "RANGER",
}


def normalizar_classe(valor: str) -> str:
    """Remove acentos e converte para maiúsculo.

    Use para normalizar nomes de classe armazenados no banco de dados.

    Exemplos:
        "Clérigo" → "CLERIGO"
        "mago" → "MAGO"
        "Feiticeiro" → "FEITICEIRO"  (preservado — sem aliases)
    """
    if not valor:
        return ""
    normalizado = unicodedata.normalize("NFD", str(valor))
    normalizado = "".join(ch for ch in normalizado if unicodedata.category(ch) != "Mn")
    return normalizado.strip().upper()


def normalizar_classe_acesso(valor: str) -> str:
    """Remove acentos, converte para maiúsculo e aplica aliases de acesso D&D 3.5.

    Use para verificar se um conjurador tem acesso a uma magia (ex.: magias preparadas).
    FEITICEIRO é tratado como MAGO para efeito de lista de magias disponíveis.

    Exemplos:
        "Feiticeiro" → "MAGO"
        "Clérigo" → "CLERIGO"
    """
    base = normalizar_classe(valor)
    return _ALIASES_ACESSO.get(base, base)


def classes_magia(valor: str) -> set[str]:
    """Extrai e normaliza (com aliases de acesso) um conjunto de classes a partir de string separada por vírgula/barra/ponto-e-vírgula."""
    partes = [p.strip() for p in re.split(r"[,/;|]", valor or "") if p.strip()]
    return {normalizar_classe_acesso(p) for p in partes if p}
