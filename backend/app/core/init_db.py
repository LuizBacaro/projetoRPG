"""
init_db.py
SRP: Inicializar banco de dados e seed de dados padrão
SOLID: Single Responsibility — responsável APENAS por inicialização
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..core.config import settings  # ✅ MUDADO: relativa em vez de absoluta
from .bonus_base_ataque import calcular_bonus_base_ataque, calcular_resistencias_base
from .classes_tables_catalog import initialize_classes_tables_catalog
from ..models.usuario import Usuario, PerfilUsuario
from ..models.combatente import Combatente
from .security import hash_senha
import logging

logger = logging.getLogger(__name__)


def inicializar_equipamentos(db: Session) -> None:
    """
    Sincroniza o catálogo de equipamentos com a Tabela 7-5 (planilha / seed gerado).

    Dados em `backend/scripts/seed_equipamentos.py` (regenerar com
    `python processar_equipamentos_excel.py` na raiz do projeto).

    Remove itens legados do seed antigo (sem categoria) que não estejam em uso
    e insere/atualiza entradas da planilha por nome.
    """
    from scripts.seed_equipamentos import seed_equipamentos

    seed_equipamentos(db)


def criar_admin_padrao(db: Session) -> None:
    """
    Cria o usuário administrador padrão se não existir.

    SEGURANÇA:
    - Apenas via logger (não aparece no stdout em produção)
    - Credenciais vêm do config.py (variáveis de ambiente em prod)
    - Aviso forçado para trocar a senha no primeiro acesso

    Args:
        db: Sessão do banco de dados
    """
    from ..repositories.usuario_repository import UsuarioRepository

    repo = UsuarioRepository(db)

    admin_email = (settings.ADMIN_EMAIL or "").strip().lower()
    admin_password = (settings.ADMIN_PASSWORD or "").strip()
    admin_username = (settings.ADMIN_USERNAME or "Administrador").strip() or "Administrador"

    # Se credenciais não configuradas, pular criação
    if not admin_email or not admin_password:
        logger.info("ℹ️  Credenciais de admin não configuradas no .env — pulando criação")
        return

    # ✅ Verifica se admin já existe
    admin_existe = repo.buscar_por_email(admin_email)
    if admin_existe:
        logger.info(f"✅ Admin já cadastrado: {admin_email}")
        return

    # ✅ Cria novo admin
    admin = Usuario(
        perfil=PerfilUsuario.ADMINISTRADOR,
        nome=admin_username,
        email=admin_email,
        senha_hash=hash_senha(admin_password),
        ativo=True,
        usuario_responsavel="sistema",
    )

    try:
        repo.criar(admin)
    except IntegrityError:
        # Idempotência em cenários de corrida: outro processo criou o admin no intervalo.
        admin_existe = repo.buscar_por_email(admin_email)
        if admin_existe:
            logger.info(f"✅ Admin já cadastrado por outra transação: {admin_email}")
            return
        raise

    # ✅ Log seguro — NÃO exibir a senha
    logger.warning(
        f"⚠️  ADMIN CRIADO — Email: {admin_email} "
        f"— ALTERE A SENHA IMEDIATAMENTE via painel de usuários"
    )
    print(
        f"✅ Admin criado com sucesso!\n"
        f"   📧 Email: {admin_email}\n"
        f"   ⚠️  ALTERE A SENHA IMEDIATAMENTE após primeiro acesso\n"
        f"   📍 Acesse: /pages/usuarios.html"
    )


def inicializar_talentos(db: Session) -> None:
    """
    Sincroniza o catálogo LdJ com `talentos_importacao_limpo.json` (raiz do repo),
    gerado por `processar_talentos_excel.py` a partir de `Tabela_5-1_Talentos_LdJ.xlsx`.

    Em cada startup: upsert por nome + remove legado fora do JSON (soft-delete se não usado em fichas).
    Se o JSON não existir no deploy, usa seed mínimo só quando a tabela está vazia.
    """
    from datetime import datetime, timezone

    from ..models.talento import Talento
    from .talentos_catalog_seed import default_json_path, sincronizar_catalogo_talentos_desde_json

    json_path = default_json_path()
    if json_path.is_file():
        sincronizar_catalogo_talentos_desde_json(db, json_path=json_path, remover_legado=True)
        return

    # Fallback: seed mínimo só se o JSON não estiver no deploy e tabela vazia
    count = db.query(Talento).filter(Talento.deleted_at.is_(None)).count()
    if count > 0:
        logger.warning(
            "Sem talentos_importacao_limpo.json e já existem %s talentos — não alterando.", count
        )
        return

    logger.warning("Catálogo JSON ausente em %s — usando seed mínimo de desenvolvimento.", json_path)

    TALENTOS_PADRAO = [
        ("Golpe Poderoso", "Realiza um ataque com + 2 de dano", "PHB p.95"),
        ("Ataque Especial", "Permite um ataque extra uma vez por dia", "PHB p.95"),
        ("Arma Focada", "Aumenta bônus com uma arma específica", "PHB p.93"),
        ("Especialização de Arma", "Aumenta dano com uma arma específica", "PHB p.93"),
        ("Lidar com Corda", "Bônus em testes com corda", "PHB p.95"),
        ("Vitalidade Aumentada", "Aumenta pontos de vida", "PHB p.95"),
        ("Reflexos Rápidos", "Aproveita a iniciativa melhor", "PHB p.95"),
        ("Golpe Girante", "Ataque contra múltiplos inimigos", "PHB p.95"),
        ("Salto Acrobático", "Bônus em testes de acrobacia", "PHB p.93"),
        ("Esquiva Extraordinária", "Evasão melhorada contra ataques", "PHB p.95"),
        ("Defesa Aprimorada", "Aumenta CA permanentemente", "PHB p.95"),
        ("Conjuração Rápida", "Reduz tempo de conjuração", "PHB p.95"),
        ("Magia Silenciosa", "Conjura sem componentes verbais", "PHB p.95"),
        ("Magia Imóvel", "Conjura sem componentes somáticos", "PHB p.95"),
        ("Golpe Certeiro", "Bônus para acertar com armas de melee", "PHB p.95"),
    ]

    for nome, descricao, pagina_ref in TALENTOS_PADRAO:
        db.add(
            Talento(
                nome=nome,
                descricao=descricao,
                pagina_referencia=pagina_ref,
                ativo=True,
                criado_em=datetime.now(timezone.utc),
            )
        )
    db.commit()
    print(f"✅ {len(TALENTOS_PADRAO)} talentos (seed mínimo) inseridos — prefira o JSON no repositório.")


def inicializar_catalogo_tabelas_classes() -> None:
    """
    Inicialização opt-in do catálogo de classes.

    Sem side effects de banco; apenas valida carregamento quando habilitado.
    """
    initialize_classes_tables_catalog()


def sincronizar_bonus_base_ataque_combatentes(db: Session) -> None:
    """
    Recalcula e persiste BBA de combatentes existentes.

    Mantém consistência para registros antigos criados antes da introdução
    do campo `bonus_base_ataque`.
    """
    combatentes = db.query(Combatente).filter(Combatente.deleted_at.is_(None)).all()
    atualizados = 0

    for combatente in combatentes:
        novo_bba = calcular_bonus_base_ataque(combatente.classe, combatente.nivel) or ""
        novas_resistencias = calcular_resistencias_base(combatente.classe, combatente.nivel)
        mudou = False

        if (combatente.bonus_base_ataque or "") != novo_bba:
            combatente.bonus_base_ataque = novo_bba
            mudou = True

        if novas_resistencias is not None:
            nova_fortitude, novo_reflexos, nova_vontade = novas_resistencias
            if combatente.fortitude_base != nova_fortitude:
                combatente.fortitude_base = nova_fortitude
                mudou = True
            if combatente.reflexos_base != novo_reflexos:
                combatente.reflexos_base = novo_reflexos
                mudou = True
            if combatente.vontade_base != nova_vontade:
                combatente.vontade_base = nova_vontade
                mudou = True

            fort_total = nova_fortitude + _modificador_atributo(combatente.constituicao)
            reflex_total = novo_reflexos + _modificador_atributo(combatente.destreza)
            vontade_total = nova_vontade + _modificador_atributo(combatente.sabedoria)

            if combatente.fortitude != fort_total:
                combatente.fortitude = fort_total
                mudou = True
            if combatente.reflexos != reflex_total:
                combatente.reflexos = reflex_total
                mudou = True
            if combatente.vontade != vontade_total:
                combatente.vontade = vontade_total
                mudou = True

        if mudou:
            atualizados += 1

    if atualizados:
        db.commit()
        logger.info("✅ Progressão base (BBA/TRs) sincronizada para %s combatente(s).", atualizados)


def _modificador_atributo(valor: int | None) -> int:
    try:
        return (int(valor) - 10) // 2
    except (TypeError, ValueError):
        return 0