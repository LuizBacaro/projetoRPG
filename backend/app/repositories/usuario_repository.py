"""
Repositório de Usuário
SRP: apenas acesso ao banco de dados para a entidade Usuario
OCP: extensível sem modificar a lógica de negócio
"""
from sqlalchemy.orm import Session
from typing import Optional
from .base import commit_with_rollback
from ..models.usuario import Usuario, PerfilUsuario


class UsuarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self, apenas_ativos: bool = False, skip: int = 0, limit: int = 50) -> list[Usuario]:
        query = self.db.query(Usuario)
        if apenas_ativos:
            query = query.filter(Usuario.ativo == True)
        return query.order_by(Usuario.nome).offset(skip).limit(limit).all()

    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def listar_por_perfil(self, perfil: PerfilUsuario) -> list[Usuario]:
        return (
            self.db.query(Usuario)
            .filter(Usuario.perfil == perfil)
            .order_by(Usuario.nome)
            .all()
        )

    def criar(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        commit_with_rollback(self.db)
        self.db.refresh(usuario)
        return usuario

    def atualizar(self, usuario: Usuario) -> Usuario:
        commit_with_rollback(self.db)
        self.db.refresh(usuario)
        return usuario

    def excluir(self, usuario: Usuario) -> None:
        self.db.delete(usuario)
        commit_with_rollback(self.db)

    def count(self, apenas_ativos: bool = False) -> int:
        query = self.db.query(Usuario)
        if apenas_ativos:
            query = query.filter(Usuario.ativo == True)
        return query.count()

    def contar_admins_ativos(self) -> int:
        return (
            self.db.query(Usuario)
            .filter(
                Usuario.perfil == PerfilUsuario.ADMINISTRADOR,
                Usuario.ativo == True,
            )
            .count()
        )