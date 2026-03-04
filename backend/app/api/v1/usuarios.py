"""
Router de Usuários
SRP: apenas rotas HTTP para usuários
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...repositories.usuario_repository import UsuarioRepository
from ...services.usuario_service import UsuarioService
from ...schemas.usuario import (
    UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioListResponse
)

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


def get_service(db: Session = Depends(get_db)) -> UsuarioService:
    return UsuarioService(UsuarioRepository(db))


@router.get("", response_model=UsuarioListResponse)
def listar_usuarios(
    apenas_ativos: bool = Query(False, description="Filtrar apenas usuários ativos"),
    service: UsuarioService = Depends(get_service)
):
    """Lista todos os usuários."""
    usuarios = service.listar(apenas_ativos=apenas_ativos)
    return {"total": len(usuarios), "usuarios": usuarios}


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario(
    usuario_id: int,
    service: UsuarioService = Depends(get_service)
):
    """Busca um usuário por ID."""
    return service.buscar_por_id(usuario_id)


@router.post("", response_model=UsuarioResponse, status_code=201)
def criar_usuario(
    dados: UsuarioCreate,
    service: UsuarioService = Depends(get_service)
):
    """Cria um novo usuário."""
    return service.criar(dados, usuario_responsavel="admin")


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    usuario_id: int,
    dados: UsuarioUpdate,
    service: UsuarioService = Depends(get_service)
):
    """Atualiza dados de um usuário."""
    return service.atualizar(usuario_id, dados, usuario_responsavel="admin")


@router.delete("/{usuario_id}", response_model=UsuarioResponse)
def inativar_usuario(
    usuario_id: int,
    service: UsuarioService = Depends(get_service)
):
    """Exclusão lógica — muda Status para Inativo."""
    return service.inativar(usuario_id, usuario_responsavel="admin")