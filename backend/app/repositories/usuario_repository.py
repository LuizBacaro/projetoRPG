"""
Repositório de Usuário
SRP: apenas acesso ao banco de dados para a entidade Usuario
OCP: extensível sem modificar a lógica de negócio
"""
from sqlalchemy.orm import Session
from typing import Optional
from ..models.usuario import Usuario, PerfilUsuario


class UsuarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self, apenas_ativos: bool = False) -> list[Usuario]:
        query = self.db.query(Usuario)
        if apenas_ativos:
            query = query.filter(Usuario.ativo == True)
        return query.order_by(Usuario.nome).all()

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
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def atualizar(self, usuario: Usuario) -> Usuario:
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def count(self) -> int:
        return self.db.query(Usuario).count()