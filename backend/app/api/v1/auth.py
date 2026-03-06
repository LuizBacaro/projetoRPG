"""
Router de Autenticação
SRP: apenas rotas de login, logout e registro público
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.security import verificar_senha, criar_token, hash_senha
from ...repositories.usuario_repository import UsuarioRepository
from ...schemas.auth import LoginRequest, TokenResponse, RegistroRequest
from ...schemas.usuario import UsuarioResponse
from ...models.usuario import Usuario, PerfilUsuario

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    """Autentica o usuário e retorna JWT."""
    repo    = UsuarioRepository(db)
    usuario = repo.buscar_por_email(dados.email)

    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos"
        )

    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Contate o administrador."
        )

    token = criar_token({
        "sub":    str(usuario.id),
        "email":  usuario.email,
        "perfil": usuario.perfil.value,
        "nome":   usuario.nome,
    })

    return TokenResponse(access_token=token, usuario=usuario)


@router.post("/registro", response_model=UsuarioResponse, status_code=201)
def registro(dados: RegistroRequest, db: Session = Depends(get_db)):
    """
    Registro público — qualquer pessoa pode criar uma conta.
    Perfil padrão: Jogador.
    O Administrador pode promover o perfil depois via /usuarios.
    """
    repo = UsuarioRepository(db)

    # Verifica e-mail duplicado
    if repo.buscar_por_email(dados.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este e-mail já está cadastrado."
        )

    usuario = Usuario(
        perfil              = PerfilUsuario.JOGADOR,   # sempre Jogador no auto-cadastro
        nome                = dados.nome,
        email               = dados.email,
        senha_hash          = hash_senha(dados.senha),
        ativo               = True,
        usuario_responsavel = "auto-cadastro",
    )

    return repo.criar(usuario)


@router.post("/logout")
def logout():
    """Logout simbólico — o cliente descarta o token."""
    return {"mensagem": "Logout realizado com sucesso"}