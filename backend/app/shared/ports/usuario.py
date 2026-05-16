"""Contrato estrutural (Protocol) para `UsuarioRepository`."""

from __future__ import annotations

from typing import List, Optional, Protocol

from sqlalchemy.orm import Session

from app.shared.models.usuario import PerfilUsuario, Usuario


class UsuarioRepositoryProtocol(Protocol):
    """Superfície usada por `UsuarioService`."""

    db: Session

    def listar(
        self, apenas_ativos: bool = False, skip: int = 0, limit: int = 50
    ) -> List[Usuario]:
        ...

    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        ...

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        ...

    def criar(self, usuario: Usuario) -> Usuario:
        ...

    def atualizar(self, usuario: Usuario) -> Usuario:
        ...

    def excluir(self, usuario: Usuario) -> None:
        ...

    def count(self, apenas_ativos: bool = False) -> int:
        ...

    def contar_admins_ativos(self) -> int:
        ...
