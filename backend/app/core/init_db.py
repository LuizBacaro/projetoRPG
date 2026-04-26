"""
init_db.py
SRP: Inicializar banco de dados e seed de dados padrão
SOLID: Single Responsibility — responsável APENAS por inicialização
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..core.config import settings  # ✅ MUDADO: relativa em vez de absoluta
from .bonus_base_ataque import (
    calcular_bonus_base_ataque,
    calcular_habilidades_especiais,
    calcular_habilidades_especiais_por_nivel,
    calcular_resistencias_base,
)
import json
from .classes_tables_catalog import initialize_classes_tables_catalog
from ..models.usuario import Usuario, PerfilUsuario
from ..games.dnd35.models.combatente import Combatente
from ..models.game import Game, UserGameMembership
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


GAME_CATALOG_SEED = [
    {
        "slug": "dnd35",
        "nome": "D&D 3.5 — Arena TTRPG",
        "descricao": (
            "Sistema completo da Arena TTRPG com regras de combate, magias, "
            "ficha por classe e gerenciamento de campanhas no D&D 3.5."
        ),
        "status": "disponivel",
        "icone": "🐉",
        "ordem": 10,
    },
    {
        "slug": "dnd5e",
        "nome": "D&D 5e",
        "descricao": (
            "Sistema D&D 5e com ficha simplificada e proficiências. "
            "Em breve: stack independente."
        ),
        "status": "em_breve",
        "icone": "🛡️",
        "ordem": 20,
    },
    {
        "slug": "gurps",
        "nome": "GURPS",
        "descricao": (
            "Sistema genérico GURPS com pontos de personagem e vantagens. "
            "Em breve: stack independente."
        ),
        "status": "em_breve",
        "icone": "⚙️",
        "ordem": 30,
    },
]


def inicializar_catalogo_jogos(db: Session) -> None:
    """
    Sincroniza o catálogo global de jogos suportados pela plataforma.

    Idempotente: insere jogos novos e atualiza metadados (nome, descrição,
    status, ícone, ordem) sem quebrar memberships já existentes.
    """
    try:
        existentes = {g.slug: g for g in db.query(Game).all()}
        criados = 0
        atualizados = 0

        for entrada in GAME_CATALOG_SEED:
            slug = entrada["slug"]
            game = existentes.get(slug)
            if game is None:
                db.add(
                    Game(
                        slug=slug,
                        nome=entrada["nome"],
                        descricao=entrada.get("descricao", ""),
                        status=entrada.get("status", "disponivel"),
                        icone=entrada.get("icone", ""),
                        ordem=int(entrada.get("ordem", 0)),
                    )
                )
                criados += 1
                continue

            mudou = False
            for campo in ("nome", "descricao", "status", "icone", "ordem"):
                novo = entrada.get(campo)
                if novo is not None and getattr(game, campo) != novo:
                    setattr(game, campo, novo)
                    mudou = True
            if mudou:
                atualizados += 1

        if criados or atualizados:
            db.commit()
            logger.info(
                "✅ games_catalog: %s criados, %s atualizados", criados, atualizados
            )
        else:
            logger.info("✅ games_catalog já sincronizado (%s jogos)", len(existentes))
    except Exception:
        db.rollback()
        raise


def garantir_membership_dnd35_para_usuarios_legados(db: Session) -> None:
    """
    Para todos os usuários ativos sem nenhum membership, cria automaticamente o
    membership do jogo `dnd35` com o perfil global do usuário. Garante que a
    base legada continue acessando o D&D 3.5 sem precisar passar por seleção
    explícita de jogo.
    """
    try:
        dnd35 = db.query(Game).filter(Game.slug == "dnd35").first()
        if dnd35 is None:
            logger.warning(
                "garantir_membership_dnd35_para_usuarios_legados: jogo dnd35 ausente; "
                "pulando enrolamento."
            )
            return

        ja_com_membership = {
            uid for (uid,) in db.query(UserGameMembership.usuario_id).distinct()
        }

        usuarios = db.query(Usuario).filter(Usuario.ativo == True).all()  # noqa: E712
        criados = 0
        for usuario in usuarios:
            if usuario.id in ja_com_membership:
                continue
            perfil_valor = (
                usuario.perfil.value
                if hasattr(usuario.perfil, "value")
                else str(usuario.perfil)
            )
            db.add(
                UserGameMembership(
                    usuario_id=usuario.id,
                    game_id=dnd35.id,
                    perfil_no_jogo=perfil_valor,
                    ativo=True,
                )
            )
            criados += 1

        if criados:
            db.commit()
            logger.info(
                "✅ Auto-enroll dnd35: %s usuário(s) legados vinculados", criados
            )
        else:
            logger.info("✅ Auto-enroll dnd35: nenhum usuário legado pendente")
    except Exception:
        db.rollback()
        raise


def inicializar_talentos(db: Session) -> None:
    """
    Sincroniza o catálogo LdJ com `talentos_importacao_limpo.json` (raiz do repo),
    gerado por `processar_talentos_excel.py` a partir de `Tabela_5-1_Talentos_LdJ.xlsx`.

    Em cada startup: upsert por nome + remove legado fora do JSON (soft-delete se não usado em fichas).
    Se o JSON não existir no deploy, usa seed mínimo só quando a tabela está vazia.
    """
    from datetime import datetime, timezone

    from ..games.dnd35.models.talento import Talento
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
        habilidades_grouped = calcular_habilidades_especiais_por_nivel(combatente.classe, combatente.nivel)
        if habilidades_grouped:
            habilidades_txt = json.dumps(habilidades_grouped, ensure_ascii=False)
        else:
            habilidades = calcular_habilidades_especiais(combatente.classe, combatente.nivel)
            habilidades_txt = " | ".join(habilidades) if habilidades else ""
        novas_resistencias = calcular_resistencias_base(combatente.classe, combatente.nivel)
        mudou = False

        if (combatente.bonus_base_ataque or "") != novo_bba:
            combatente.bonus_base_ataque = novo_bba
            mudou = True
        if (combatente.habilidades_especiais or "") != habilidades_txt:
            combatente.habilidades_especiais = habilidades_txt
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

        else:
            # Classes sem mapeamento no catálogo/fallback: preservar totais legados
            # e preencher base de forma derivada para evitar nulls em responses.
            base_fort = (combatente.fortitude or 0) - _modificador_atributo(combatente.constituicao)
            base_ref = (combatente.reflexos or 0) - _modificador_atributo(combatente.destreza)
            base_vont = (combatente.vontade or 0) - _modificador_atributo(combatente.sabedoria)

            if combatente.fortitude_base is None:
                combatente.fortitude_base = base_fort
                mudou = True
            if combatente.reflexos_base is None:
                combatente.reflexos_base = base_ref
                mudou = True
            if combatente.vontade_base is None:
                combatente.vontade_base = base_vont
                mudou = True

        # Defesa automática: Toque/Surpresa/CA
        mod_des = _modificador_atributo(combatente.destreza)
        bonus_armadura = max(0, int(combatente.ca or 10) - (10 + mod_des))
        novo_toque = 10 + mod_des
        nova_surpresa = 10 + bonus_armadura
        nova_ca = 10 + mod_des + bonus_armadura
        if combatente.toque != novo_toque:
            combatente.toque = novo_toque
            mudou = True
        if combatente.surpresa != nova_surpresa:
            combatente.surpresa = nova_surpresa
            mudou = True
        if combatente.ca != nova_ca:
            combatente.ca = nova_ca
            mudou = True

        if mudou:
            atualizados += 1

    if atualizados:
        db.commit()
        logger.info("✅ Progressão base (BBA/TRs) sincronizada para %s combatente(s).", atualizados)


def inicializar_catalogo_magias_se_vazio(db: Session) -> None:
    """
    Garante catálogo PHB em `magias` / `magias_classes` quando o banco está vazio.

    - **SQLite (dev):** se `magias` estiver vazia, executa `scripts/seed_magias.py` no startup
      (primeira subida pode levar ~20–40s).
    - **PostgreSQL / outros:** só popula automaticamente se `SEED_MAGIAS_ON_EMPTY=1` no `.env`;
      caso contrário apenas avisa — use `cd backend && python scripts/seed_magias.py` manualmente.
    """
    from app.games.dnd35.models.magia import Magia
    from scripts.seed_magias import seed_magias

    try:
        total = db.query(Magia).count()
    except Exception as exc:  # pragma: no cover - schema ainda não pronto
        logger.warning("Não foi possível verificar tabela magias: %s", exc)
        return

    if total > 0:
        return

    url = (settings.DATABASE_URL or "").lower()
    is_sqlite = "sqlite" in url
    if not is_sqlite and not settings.SEED_MAGIAS_ON_EMPTY:
        msg = (
            "Tabela `magias` vazia — grimório e escolas ficam vazios. "
            "Execute no servidor: cd backend && python scripts/seed_magias.py "
            "ou defina SEED_MAGIAS_ON_EMPTY=1 uma vez no .env e reinicie."
        )
        logger.warning(msg)
        print(f"⚠️  {msg}")
        return

    logger.info("Tabela magias vazia — executando seed PHB (aguarde ~20–40s)…")
    print("📚 Populando catálogo de magias (primeira execução pode demorar)…")
    try:
        seed_magias(db, force=False)
        logger.info("✅ Catálogo de magias (seed PHB) concluído.")
        print("✅ Catálogo de magias inicializado.")
    except Exception as exc:
        logger.exception("Falha ao executar seed_magias: %s", exc)
        print(f"❌ Falha ao popular magias: {exc}")
        raise


def _modificador_atributo(valor: int | None) -> int:
    try:
        return (int(valor) - 10) // 2
    except (TypeError, ValueError):
        return 0