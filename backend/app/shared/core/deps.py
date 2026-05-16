"""
deps.py
SRP: Dependências de autenticação/autorização para injeção no FastAPI
SOLID: Dependency Injection — desacoplamento de segurança da lógica
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from starlette.requests import Request

from ...games.dnd5e.models.personagem import Dnd5ePersonagem
from ...games.dnd35.models.ataque import MagiaSlot
from ...games.dnd35.models.combatente import Combatente
from ...games.gurps.models.personagem import GurpsPersonagem
from ...games.tormenta.models.personagem import TormentaPersonagem
from ...shared.core.config import settings
from ...shared.core.database import get_db
from ...shared.repositories.usuario_repository import UsuarioRepository
from ..constants import (
    GAME_SLUG_DND5E,
    GAME_SLUG_DND35,
    GAME_SLUG_GURPS,
    GAME_SLUG_TORMENTA,
)
from ..models.usuario import PerfilUsuario, Usuario
from .security import decodificar_token
from .security_audit import log_security_event

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(
    bearerFormat="JWT",
    scheme_name="JWTBearer",
    description="Informe o token JWT no formato: Bearer <token>",
    auto_error=False,
)

# `get_db` vem só de `database.py` — um único objeto para `Depends(get_db)` em todo o app.
# Re-exportado aqui para quem importa de `app.shared.core.deps` (auth, etc.).

# Alias histórico (nome com typo) — preferir GAME_SLUG_DND35 em código novo.
GAME_SLUG_DNDD35 = GAME_SLUG_DND35


def extrair_game_slug_do_token(request: Request) -> Optional[str]:
    """
    Lê o claim `game_slug` do token Bearer, se houver. Retorna None quando o
    token não traz o claim (compatibilidade com tokens antigos pré-multi-jogo).
    """
    auth_header = request.headers.get("authorization") or ""
    partes = auth_header.split()
    if len(partes) != 2 or partes[0].lower() != "bearer":
        return None
    payload = decodificar_token(partes[1], settings.SECRET_KEY)
    if not payload:
        return None
    slug = payload.get("game_slug")
    if isinstance(slug, str) and slug.strip():
        return slug.strip().lower()
    return None


def extrair_token_do_header(request: Request) -> Optional[str]:
    """
    Extrai o token Bearer do header Authorization.

    Args:
        request: Request do FastAPI

    Returns:
        Token ou None se não encontrado

    Example:
        Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
    """
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return None

    partes = auth_header.split()
    if len(partes) != 2 or partes[0].lower() != "bearer":
        return None

    return partes[1]


def get_usuario_atual(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """
    Dependency: Extrai e valida o usuário autenticado do token JWT.

    FLUXO:
    1. Extrai token do header Authorization
    2. Token é decodificado via JWT
    3. Email é extraído do payload
    4. Usuário é buscado no banco
    5. Validações (token válido, usuário existe, está ativo)

    Args:
        request: Request do FastAPI (contém headers)
        db: Sessão do banco de dados

    Returns:
        Objeto Usuario autenticado

    Raises:
        HTTPException 401: Token inválido/expirado/ausente
        HTTPException 404: Usuário não encontrado
        HTTPException 403: Usuário inativo

    Example:
        @app.get("/profile")
        def meu_perfil(usuario = Depends(get_usuario_atual)):
            return {"nome": usuario.nome, "email": usuario.email}
    """
    # ✅ Extrai token do header
    token = credentials.credentials if credentials else None
    if not token:
        log_security_event(
            "access_token",
            "failure",
            request=request,
            reason="missing_token",
            level=logging.WARNING,
        )
        logger.warning("❌ Tentativa de acesso sem token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Decodifica token
    payload = decodificar_token(token, settings.SECRET_KEY)
    if payload is None:
        log_security_event(
            "access_token",
            "failure",
            request=request,
            reason="invalid_or_expired_token",
            level=logging.WARNING,
        )
        logger.warning("❌ Tentativa de acesso com token inválido/expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Extrai email do token
    email = payload.get("sub")
    if not email:
        log_security_event(
            "access_token",
            "failure",
            request=request,
            reason="missing_subject",
            level=logging.WARNING,
        )
        logger.warning("❌ Token não contém email (sub)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não contém email",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Busca usuário no banco
    repo = UsuarioRepository(db)
    usuario = repo.buscar_por_email(email)

    if not usuario:
        log_security_event(
            "access_token",
            "failure",
            request=request,
            user_email=email,
            reason="user_not_found",
            level=logging.WARNING,
        )
        logger.warning(f"❌ Usuário não encontrado: {email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )

    if not usuario.ativo:
        log_security_event(
            "access_token",
            "blocked",
            request=request,
            user_email=email,
            reason="inactive_user",
            level=logging.WARNING,
        )
        logger.warning(f"⚠️  Usuário inativo tentou acessar: {email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo"
        )

    logger.info(f"✅ Acesso autorizado: {email}")
    return usuario


def requer_game_dnd35(
    request: Request,
    usuario=Depends(get_usuario_atual),
) -> Usuario:
    """
    Garante que o token Bearer carrega o claim `game_slug=dnd35` quando o
    modo estrito multi-jogo está ativo (`settings.MULTI_GAME_STRICT_MODE`).

    Comportamento:
      - Modo estrito off (padrão até estabilizar): apenas registra divergência
        em log (compatível com tokens antigos sem `game_slug`).
      - Modo estrito on: retorna 409 quando `game_slug` ausente (token antigo)
        e 403 quando `game_slug` diverge de `dnd35`. O frontend redireciona
        para o seletor de jogo (header `X-Game-Slug-Required`).
    """
    slug = extrair_game_slug_do_token(request)

    if not settings.MULTI_GAME_STRICT_MODE:
        if slug and slug != GAME_SLUG_DND35:
            logger.warning(
                "⚠️  Acesso a endpoint D&D 3.5 com game_slug='%s' (esperado '%s')",
                slug,
                GAME_SLUG_DND35,
            )
        return usuario

    if slug is None:
        log_security_event(
            "game_slug_required",
            "denied",
            request=request,
            user_email=getattr(usuario, "email", None),
            reason="missing_game_slug_claim",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Sessão sem jogo selecionado. Volte ao seletor de jogo "
                "para entrar no D&D 3.5."
            ),
            headers={"X-Game-Slug-Required": GAME_SLUG_DND35},
        )

    if slug != GAME_SLUG_DND35:
        log_security_event(
            "game_slug_mismatch",
            "denied",
            request=request,
            user_email=getattr(usuario, "email", None),
            target=f"game_slug:{slug}",
            reason="wrong_game_slug",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Token vinculado ao jogo '{slug}'. Este endpoint pertence "
                f"ao D&D 3.5 ('{GAME_SLUG_DND35}')."
            ),
            headers={"X-Game-Slug-Required": GAME_SLUG_DND35},
        )

    return usuario


def requer_game_dnd5e(
    request: Request,
    usuario=Depends(get_usuario_atual),
) -> Usuario:
    """Garante `game_slug=dnd5e` quando `MULTI_GAME_STRICT_MODE` está ativo."""
    slug = extrair_game_slug_do_token(request)

    if not settings.MULTI_GAME_STRICT_MODE:
        if slug and slug != GAME_SLUG_DND5E:
            logger.warning(
                "⚠️  Acesso a endpoint D&D 5e com game_slug='%s' (esperado '%s')",
                slug,
                GAME_SLUG_DND5E,
            )
        return usuario

    if slug is None:
        log_security_event(
            "game_slug_required",
            "denied",
            request=request,
            user_email=getattr(usuario, "email", None),
            reason="missing_game_slug_claim",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Sessão sem jogo selecionado. Volte ao seletor de jogo "
                "para entrar no D&D 5e."
            ),
            headers={"X-Game-Slug-Required": GAME_SLUG_DND5E},
        )

    if slug != GAME_SLUG_DND5E:
        log_security_event(
            "game_slug_mismatch",
            "denied",
            request=request,
            user_email=getattr(usuario, "email", None),
            target=f"game_slug:{slug}",
            reason="wrong_game_slug",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Token vinculado ao jogo '{slug}'. Este endpoint pertence "
                f"ao D&D 5e ('{GAME_SLUG_DND5E}')."
            ),
            headers={"X-Game-Slug-Required": GAME_SLUG_DND5E},
        )

    return usuario


def requer_game_gurps(
    request: Request,
    usuario=Depends(get_usuario_atual),
) -> Usuario:
    """Garante `game_slug=gurps` quando `MULTI_GAME_STRICT_MODE` está ativo."""
    slug = extrair_game_slug_do_token(request)

    if not settings.MULTI_GAME_STRICT_MODE:
        if slug and slug != GAME_SLUG_GURPS:
            logger.warning(
                "⚠️  Acesso a endpoint GURPS com game_slug='%s' (esperado '%s')",
                slug,
                GAME_SLUG_GURPS,
            )
        return usuario

    if slug is None:
        log_security_event(
            "game_slug_required",
            "denied",
            request=request,
            user_email=getattr(usuario, "email", None),
            reason="missing_game_slug_claim",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Sessão sem jogo selecionado. Volte ao seletor de jogo "
                "para entrar no GURPS."
            ),
            headers={"X-Game-Slug-Required": GAME_SLUG_GURPS},
        )

    if slug != GAME_SLUG_GURPS:
        log_security_event(
            "game_slug_mismatch",
            "denied",
            request=request,
            user_email=getattr(usuario, "email", None),
            target=f"game_slug:{slug}",
            reason="wrong_game_slug",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Token vinculado ao jogo '{slug}'. Este endpoint pertence "
                f"ao GURPS ('{GAME_SLUG_GURPS}')."
            ),
            headers={"X-Game-Slug-Required": GAME_SLUG_GURPS},
        )

    return usuario


def requer_game_tormenta(
    request: Request,
    usuario=Depends(get_usuario_atual),
) -> Usuario:
    """Garante `game_slug=tormenta` quando `MULTI_GAME_STRICT_MODE` está ativo."""
    slug = extrair_game_slug_do_token(request)

    if not settings.MULTI_GAME_STRICT_MODE:
        if slug and slug != GAME_SLUG_TORMENTA:
            logger.warning(
                "⚠️  Acesso a endpoint Tormenta com game_slug='%s' (esperado '%s')",
                slug,
                GAME_SLUG_TORMENTA,
            )
        return usuario

    if slug is None:
        log_security_event(
            "game_slug_required",
            "denied",
            request=request,
            user_email=getattr(usuario, "email", None),
            reason="missing_game_slug_claim",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Sessão sem jogo selecionado. Volte ao seletor de jogo "
                "para entrar no Tormenta."
            ),
            headers={"X-Game-Slug-Required": GAME_SLUG_TORMENTA},
        )

    if slug != GAME_SLUG_TORMENTA:
        log_security_event(
            "game_slug_mismatch",
            "denied",
            request=request,
            user_email=getattr(usuario, "email", None),
            target=f"game_slug:{slug}",
            reason="wrong_game_slug",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Token vinculado ao jogo '{slug}'. Este endpoint pertence "
                f"ao Tormenta ('{GAME_SLUG_TORMENTA}')."
            ),
            headers={"X-Game-Slug-Required": GAME_SLUG_TORMENTA},
        )

    return usuario


def requer_admin(request: Request, usuario=Depends(get_usuario_atual)) -> Usuario:
    """
    Dependency: Valida se o usuário é ADMINISTRADOR.

    Args:
        usuario: Usuário autenticado (via get_usuario_atual)

    Returns:
        Usuario se for admin

    Raises:
        HTTPException 403: Usuário não é administrador
    """
    if usuario.perfil != PerfilUsuario.ADMINISTRADOR:
        log_security_event(
            "rbac_admin",
            "denied",
            request=request,
            user_email=usuario.email,
            reason="insufficient_role",
            level=logging.WARNING,
        )
        logger.warning(
            f"⚠️  Acesso negado — usuário sem permissão admin: {usuario.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem acessar este recurso",
        )
    logger.info(f"✅ Admin autorizado: {usuario.email}")
    return usuario


def requer_mestre_ou_admin(
    request: Request, usuario=Depends(get_usuario_atual)
) -> Usuario:
    """
    Dependency: Valida se é MESTRE ou ADMINISTRADOR.

    Args:
        usuario: Usuário autenticado

    Returns:
        Usuario se tiver permissão

    Raises:
        HTTPException 403: Sem permissão adequada
    """
    if usuario.perfil not in [PerfilUsuario.ADMINISTRADOR, PerfilUsuario.MESTRE]:
        log_security_event(
            "rbac_mestre_admin",
            "denied",
            request=request,
            user_email=usuario.email,
            reason="insufficient_role",
            level=logging.WARNING,
        )
        logger.warning(
            f"⚠️  Acesso negado — sem permissão mestre/admin: {usuario.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas mestres e administradores podem acessar",
        )
    logger.info(f"✅ Mestre/Admin autorizado: {usuario.email}")
    return usuario


def requer_jogador(request: Request, usuario=Depends(get_usuario_atual)) -> Usuario:
    """
    Dependency: Valida se é JOGADOR (ou superior).

    Args:
        usuario: Usuário autenticado

    Returns:
        Usuario se for jogador

    Raises:
        HTTPException 403: Não é jogador
    """
    if usuario.perfil not in [
        PerfilUsuario.JOGADOR,
        PerfilUsuario.MESTRE,
        PerfilUsuario.ADMINISTRADOR,
    ]:
        log_security_event(
            "rbac_jogador",
            "denied",
            request=request,
            user_email=usuario.email,
            reason="insufficient_role",
            level=logging.WARNING,
        )
        logger.warning(f"⚠️  Acesso negado — não é jogador: {usuario.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a jogadores e superiores",
        )
    logger.info(f"✅ Jogador autorizado: {usuario.email}")
    return usuario


def requer_dono_ou_admin_combatente(
    combatente_id: int,
    request: Request,
    usuario=Depends(get_usuario_atual),
    db: Session = Depends(get_db),
) -> Usuario:
    """Dependency: garante que o usuário é dono do combatente ou admin/mestre."""
    combatente = db.query(Combatente).filter(Combatente.id == combatente_id).first()
    if not combatente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Combatente {combatente_id} não encontrado",
        )

    if usuario.perfil in (PerfilUsuario.ADMINISTRADOR, PerfilUsuario.MESTRE):
        return usuario

    if combatente.dono_id != usuario.id:
        log_security_event(
            "combatente_access",
            "denied",
            request=request,
            user_email=usuario.email,
            target=f"combatente:{combatente_id}",
            reason="not_owner",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar este combatente",
        )

    return usuario


def requer_dono_ou_admin_slot_magia(
    slot_id: int,
    request: Request,
    usuario=Depends(get_usuario_atual),
    db: Session = Depends(get_db),
) -> Usuario:
    """Dependency: garante acesso por propriedade para endpoints de slot por ID."""
    slot = db.query(MagiaSlot).filter(MagiaSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot não encontrado",
        )

    combatente = (
        db.query(Combatente).filter(Combatente.id == slot.combatente_id).first()
    )
    if not combatente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Combatente {slot.combatente_id} não encontrado",
        )

    if usuario.perfil in (PerfilUsuario.ADMINISTRADOR, PerfilUsuario.MESTRE):
        return usuario

    if combatente.dono_id != usuario.id:
        log_security_event(
            "magia_slot_access",
            "denied",
            request=request,
            user_email=usuario.email,
            target=f"slot:{slot_id}",
            reason="not_owner",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para alterar este slot",
        )

    return usuario


def validar_combatentes_do_usuario(
    combatente_ids: list[int],
    usuario,
    db: Session,
) -> None:
    """Valida lista de combatentes para operações em lote (ex.: iniciar combate)."""
    if usuario.perfil in (PerfilUsuario.ADMINISTRADOR, PerfilUsuario.MESTRE):
        return

    ids_unicos = list(set(combatente_ids))
    if not ids_unicos:
        return

    combatentes = db.query(Combatente).filter(Combatente.id.in_(ids_unicos)).all()

    encontrados = {c.id for c in combatentes}
    faltantes = [cid for cid in ids_unicos if cid not in encontrados]
    if faltantes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Combatentes não encontrados: {faltantes}",
        )

    sem_acesso = [c.id for c in combatentes if c.dono_id != usuario.id]
    if sem_acesso:
        log_security_event(
            "combatente_batch_access",
            "denied",
            user_email=usuario.email,
            target="combatentes",
            reason="not_owner",
            details={"combatente_ids": sem_acesso},
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para os combatentes: {sem_acesso}",
        )


def validar_gurps_personagens_do_usuario(
    personagem_ids: list[int],
    usuario,
    db: Session,
) -> None:
    """Valida lista de personagens GURPS para operações em lote (ex.: combate)."""
    if usuario.perfil in (PerfilUsuario.ADMINISTRADOR, PerfilUsuario.MESTRE):
        return

    ids_unicos = list(set(personagem_ids))
    if not ids_unicos:
        return

    personagens = (
        db.query(GurpsPersonagem).filter(GurpsPersonagem.id.in_(ids_unicos)).all()
    )

    encontrados = {p.id for p in personagens}
    faltantes = [pid for pid in ids_unicos if pid not in encontrados]
    if faltantes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personagens não encontrados: {faltantes}",
        )

    sem_acesso = [p.id for p in personagens if p.dono_id != usuario.id]
    if sem_acesso:
        log_security_event(
            "gurps_personagem_batch_access",
            "denied",
            user_email=usuario.email,
            target="gurps_personagens",
            reason="not_owner",
            details={"personagem_ids": sem_acesso},
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para os personagens: {sem_acesso}",
        )


def validar_tormenta_personagens_do_usuario(
    personagem_ids: list[int],
    usuario,
    db: Session,
) -> None:
    """Valida lista de personagens Tormenta para operações em lote (ex.: combate na Arena)."""
    if usuario.perfil in (PerfilUsuario.ADMINISTRADOR, PerfilUsuario.MESTRE):
        return

    ids_unicos = list(set(personagem_ids))
    if not ids_unicos:
        return

    personagens = (
        db.query(TormentaPersonagem).filter(TormentaPersonagem.id.in_(ids_unicos)).all()
    )

    encontrados = {p.id for p in personagens}
    faltantes = [pid for pid in ids_unicos if pid not in encontrados]
    if faltantes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personagens não encontrados: {faltantes}",
        )

    sem_acesso = [p.id for p in personagens if p.dono_id != usuario.id]
    if sem_acesso:
        log_security_event(
            "tormenta_personagem_batch_access",
            "denied",
            user_email=usuario.email,
            target="tormenta_personagens",
            reason="not_owner",
            details={"personagem_ids": sem_acesso},
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para os personagens: {sem_acesso}",
        )


def requer_dono_ou_admin_gurps_personagem(
    personagem_id: int,
    request: Request,
    usuario=Depends(get_usuario_atual),
    db: Session = Depends(get_db),
) -> Usuario:
    """Garante que o usuário é dono do personagem GURPS ou mestre/admin."""
    personagem = (
        db.query(GurpsPersonagem).filter(GurpsPersonagem.id == personagem_id).first()
    )
    if not personagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personagem {personagem_id} não encontrado",
        )

    if usuario.perfil in (PerfilUsuario.ADMINISTRADOR, PerfilUsuario.MESTRE):
        return usuario

    if personagem.dono_id != usuario.id:
        log_security_event(
            "gurps_personagem_access",
            "denied",
            request=request,
            user_email=usuario.email,
            target=f"gurps_personagem:{personagem_id}",
            reason="not_owner",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar este personagem",
        )

    return usuario


def requer_dono_ou_admin_dnd5e_personagem(
    personagem_id: int,
    request: Request,
    usuario=Depends(get_usuario_atual),
    db: Session = Depends(get_db),
) -> Usuario:
    """Garante que o usuário é dono do personagem D&D 5e ou mestre/admin."""
    personagem = (
        db.query(Dnd5ePersonagem).filter(Dnd5ePersonagem.id == personagem_id).first()
    )
    if not personagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personagem {personagem_id} não encontrado",
        )

    if usuario.perfil in (PerfilUsuario.ADMINISTRADOR, PerfilUsuario.MESTRE):
        return usuario

    if personagem.dono_id != usuario.id:
        log_security_event(
            "dnd5e_personagem_access",
            "denied",
            request=request,
            user_email=usuario.email,
            target=f"dnd5e_personagem:{personagem_id}",
            reason="not_owner",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar este personagem",
        )

    return usuario


def requer_dono_ou_admin_tormenta_personagem(
    personagem_id: int,
    request: Request,
    usuario=Depends(get_usuario_atual),
    db: Session = Depends(get_db),
) -> Usuario:
    """Garante que o usuário é dono do personagem Tormenta ou mestre/admin."""
    personagem = (
        db.query(TormentaPersonagem)
        .filter(TormentaPersonagem.id == personagem_id)
        .first()
    )
    if not personagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personagem {personagem_id} não encontrado",
        )

    if usuario.perfil in (PerfilUsuario.ADMINISTRADOR, PerfilUsuario.MESTRE):
        return usuario

    if personagem.dono_id != usuario.id:
        log_security_event(
            "tormenta_personagem_access",
            "denied",
            request=request,
            user_email=usuario.email,
            target=f"tormenta_personagem:{personagem_id}",
            reason="not_owner",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar este personagem",
        )

    return usuario
