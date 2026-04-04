"""
Router de Usuários
SRP: apenas rotas HTTP para usuários
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.deps import requer_admin, get_usuario_atual
from ...models.usuario import Usuario
from ...core.security_audit import log_security_event
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
    apenas_ativos: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: UsuarioService = Depends(get_service),
    _: Usuario = Depends(get_usuario_atual)   # qualquer usuário logado
):
    usuarios = service.listar(apenas_ativos=apenas_ativos, skip=skip, limit=limit)
    return {
        "total": service.contar(apenas_ativos=apenas_ativos),
        "skip": skip,
        "limit": limit,
        "usuarios": usuarios,
    }


@router.get("/me", response_model=UsuarioResponse)
def meu_perfil(usuario_atual: Usuario = Depends(get_usuario_atual)):
    """Retorna os dados do usuário logado."""
    return usuario_atual


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario(
    usuario_id: int,
    service: UsuarioService = Depends(get_service),
    _: Usuario = Depends(requer_admin)
):
    return service.buscar_por_id(usuario_id)


@router.post("", response_model=UsuarioResponse, status_code=201)
def criar_usuario(
    request: Request,
    dados: UsuarioCreate,
    service: UsuarioService = Depends(get_service),
    usuario_atual: Usuario = Depends(requer_admin)
):
    usuario = service.criar(dados, usuario_responsavel=usuario_atual.email)
    log_security_event(
        "user_create",
        "success",
        request=request,
        actor_email=usuario_atual.email,
        target=f"usuario:{usuario.id}",
        details={"email": usuario.email, "perfil": usuario.perfil},
    )
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    request: Request,
    usuario_id: int,
    dados: UsuarioUpdate,
    service: UsuarioService = Depends(get_service),
    usuario_atual: Usuario = Depends(requer_admin)
):
    usuario = service.atualizar(usuario_id, dados, usuario_responsavel=usuario_atual.email)
    log_security_event(
        "user_update",
        "success",
        request=request,
        actor_email=usuario_atual.email,
        target=f"usuario:{usuario.id}",
        details={"email": usuario.email, "perfil": usuario.perfil, "ativo": usuario.ativo},
    )
    return usuario


@router.delete("/{usuario_id}/definitivo", status_code=204)
def excluir_usuario_definitivo(
    request: Request,
    usuario_id: int,
    service: UsuarioService = Depends(get_service),
    usuario_atual: Usuario = Depends(requer_admin)
):
    usuario = service.buscar_por_id(usuario_id)
    service.excluir_definitivo(usuario_id, usuario_solicitante_id=usuario_atual.id)
    log_security_event(
        "user_delete",
        "success",
        request=request,
        actor_email=usuario_atual.email,
        target=f"usuario:{usuario.id}",
        details={"email": usuario.email},
    )
    return None


@router.delete("/{usuario_id}", response_model=UsuarioResponse)
def inativar_usuario(
    request: Request,
    usuario_id: int,
    service: UsuarioService = Depends(get_service),
    usuario_atual: Usuario = Depends(requer_admin)
):
    usuario = service.inativar(usuario_id, usuario_responsavel=usuario_atual.email)
    log_security_event(
        "user_deactivate",
        "success",
        request=request,
        actor_email=usuario_atual.email,
        target=f"usuario:{usuario.id}",
        details={"email": usuario.email},
    )
    return usuario