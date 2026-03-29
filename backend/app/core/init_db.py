"""
init_db.py
SRP: Inicializar banco de dados e seed de dados padrão
SOLID: Single Responsibility — responsável APENAS por inicialização
"""
from sqlalchemy.orm import Session
from ..core.config import settings  # ✅ MUDADO: relativa em vez de absoluta
from ..models.usuario import Usuario, PerfilUsuario
from .security import hash_senha
import logging

logger = logging.getLogger(__name__)


def inicializar_equipamentos(db: Session) -> None:
    """
    Popula os equipamentos padrão de D&D 3.5 se ainda não existirem.
    
    Args:
        db: Sessão do banco de dados
    """
    from ..models.equipamento import Equipamento
    from datetime import datetime
    
    # Verificar se já existem equipamentos
    count = db.query(Equipamento).count()
    if count > 0:
        logger.info(f"✅ Equipamentos já existem ({count}). Pulando seed.")
        return
    
    EQUIPAMENTOS_PADRAO = [
        # ── ARMAS ──
        ("Adaga", "Arma simples de melee", "PHB p.120"),
        ("Espada Longa", "Arma marcial de melee", "PHB p.124"),
        ("Espada Curta", "Arma simples de melee", "PHB p.120"),
        ("Machado Grande", "Arma marcial de melee", "PHB p.124"),
        ("Maça", "Arma simples de melee", "PHB p.120"),
        ("Bastão", "Arma simples de melee", "PHB p.120"),
        ("Arco Longo", "Arma marcial à distância", "PHB p.124"),
        ("Arco Curto", "Arma simples à distância", "PHB p.120"),
        ("Besta Pesada", "Arma simples à distância", "PHB p.120"),
        ("Besta Leve", "Arma simples à distância", "PHB p.120"),
        ("Lança", "Arma simples de melee", "PHB p.120"),
        ("Espada Bastarda", "Arma exótica", "PHB p.126"),
        ("Katana", "Arma exótica", "PHB p.126"),
        
        # ── ARMADURAS ──
        ("Courça de Couro", "Armadura leve", "PHB p.125"),
        ("Armadura de Couro", "Armadura leve", "PHB p.125"),
        ("Corrente de Malha", "Armadura média", "PHB p.125"),
        ("Armadura de Placas", "Armadura pesada", "PHB p.125"),
        ("Escudo de Madeira", "Escudo leve", "PHB p.125"),
        ("Escudo de Aço", "Escudo pesado", "PHB p.125"),
        
        # ── EQUIPAMENTOS AVENTUREIROS ──
        ("Mochila de Aventureiro", "Mochila de viagem", "PHB p.128"),
        ("Moeda (Ouro)", "Moeda de ouro", "PHB p.128"),
        ("Corda (15 pés)", "Corda de sisal", "PHB p.128"),
        ("Lanterna", "Fonte de luz", "PHB p.128"),
        ("Óleo para Lanterna", "Combustível para lanterna", "PHB p.128"),
        ("Marmita", "Utensílio de cozinha", "PHB p.128"),
        ("Tenda", "Abrigo portátil", "PHB p.128"),
        ("Saco de Dormir", "Abrigo para dormir", "PHB p.128"),
        ("Cantil", "Recipiente para água", "PHB p.128"),
        ("Picareta", "Ferramenta de escavação", "PHB p.128"),
        ("Pá", "Ferramenta de escavação", "PHB p.128"),
        ("Martelo", "Ferramenta de trabalho", "PHB p.128"),
        ("Pregos (10)", "Fixadores", "PHB p.128"),
        ("Cadeado", "Segurança", "PHB p.128"),
        ("Chave para Cadeado", "Chave mestre", "PHB p.128"),
        ("Jogo de Ferramentas de Ladrão", "Ferramentas especializadas", "PHB p.128"),
        ("Jogo de Cura", "Kit médico", "PHB p.128"),
        ("Tochas (10)", "Fonte de luz", "PHB p.128"),
        ("Bebida Alcoólica", "Bebida alcóolica", "PHB p.128"),
        ("Pergaminho", "Material de escrita", "PHB p.128"),
        ("Tinta", "Tinta para escrita", "PHB p.128"),
        ("Pena", "Ferramenta de escrita", "PHB p.128"),
        
        # ── POÇÕES E CONSUMÍVEIS ──
        ("Poção de Cura Menor", "Restaura 1d8+1 PV", "PHB p.182"),
        ("Poção de Cura Moderada", "Restaura 2d8+3 PV", "PHB p.182"),
        ("Poção de Cura Séria", "Restaura 3d8+5 PV", "PHB p.182"),
        ("Poção de Resistência", "Aumenta resistências", "PHB p.182"),
        ("Poção de Força do Gigante", "Aumenta FOR", "PHB p.182"),
        ("Poção de Velocidade", "Aumenta DES", "PHB p.182"),
        
        # ── ITENS MÁGICOS MUNDANOS ──
        ("Sacola de Manutenção Eterna", "Bolsa infinita", "DMG p.246"),
        ("Corda de Entanglement", "Corda mágica", "DMG p.246"),
        ("Botas de Leveza", "Reduz peso", "DMG p.246"),
        ("Capa de Invisibilidade", "Torna invisível", "DMG p.246"),
        ("Anel de Proteção", "Aumenta CA", "DMG p.246"),
        ("Amuleto de Proteção", "Aumenta resistências", "DMG p.246"),
        ("Anel da Verdade", "Detecta mentira", "DMG p.246"),
        ("Varinha de Magia de Míssil", "Dispara Magic Missile", "DMG p.246"),
        ("Varinha de Cura", "Cura ferimentos", "DMG p.246"),
    ]
    
    print("📦 Iniciando seed de equipamentos...")
    
    for nome, descricao, pag_ref in EQUIPAMENTOS_PADRAO:
        equipamento = Equipamento(
            nome=nome,
            descricao=descricao,
            pagina_referencia=pag_ref,
            ativo=True,
            criado_em=datetime.utcnow()
        )
        db.add(equipamento)
    
    db.commit()
    print(f"✅ {len(EQUIPAMENTOS_PADRAO)} equipamentos inseridos com sucesso!")


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

    # Se credenciais não configuradas, pular criação
    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        logger.info("ℹ️  Credenciais de admin não configuradas no .env — pulando criação")
        return

    # ✅ Verifica se admin já existe
    admin_existe = repo.buscar_por_email(settings.ADMIN_EMAIL)
    if admin_existe:
        logger.info(f"✅ Admin já cadastrado: {settings.ADMIN_EMAIL}")
        return

    # ✅ Cria novo admin
    admin = Usuario(
        perfil=PerfilUsuario.ADMINISTRADOR,
        nome=settings.ADMIN_USERNAME,
        email=settings.ADMIN_EMAIL,
        senha_hash=hash_senha(settings.ADMIN_PASSWORD),
        ativo=True,
        usuario_responsavel="sistema",
    )

    repo.criar(admin)

    # ✅ Log seguro — NÃO exibir a senha
    logger.warning(
        f"⚠️  ADMIN CRIADO — Email: {settings.ADMIN_EMAIL} "
        f"— ALTERE A SENHA IMEDIATAMENTE via painel de usuários"
    )
    print(
        f"✅ Admin criado com sucesso!\n"
        f"   📧 Email: {settings.ADMIN_EMAIL}\n"
        f"   ⚠️  ALTERE A SENHA IMEDIATAMENTE após primeiro acesso\n"
        f"   📍 Acesse: /pages/usuarios.html"
    )


def inicializar_talentos(db: Session) -> None:
    """
    Popula os talentos padrão de D&D 3.5 se ainda não existirem.
    
    Args:
        db: Sessão do banco de dados
    """
    from ..models.talento import Talento
    from datetime import datetime
    
    # Verificar se já existem talentos
    count = db.query(Talento).count()
    if count > 0:
        logger.info(f"✅ Talentos já existem ({count}). Pulando seed.")
        return
    
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
        talento = Talento(
            nome=nome,
            descricao=descricao,
            pagina_referencia=pagina_ref,
            ativo=True,
            criado_em=datetime.utcnow()
        )
        db.add(talento)
    
    db.commit()
    print(f"✅ {len(TALENTOS_PADRAO)} talentos inseridos com sucesso!")