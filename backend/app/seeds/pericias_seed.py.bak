"""
Seed para popular perícias iniciais
"""

from sqlalchemy.orm import Session
from app.models.pericia import Pericia, TipoPericiaEnum


PERICIAS_PADRAO = [
    # Destreza
    {"nome": "Acrobacia", "descricao": "Equilibrar-se, saltar, cambalhotas.", "atributo": "DES", "tipo": "comum"},
    {"nome": "Abrir Fechaduras", "descricao": "Usar ferramentas de ladino.", "atributo": "DES", "tipo": "comum", "requer_treinamento": 1},
    {"nome": "Cavalgar", "descricao": "Controlar montarias.", "atributo": "DES", "tipo": "comum"},
    {"nome": "Esconder-se", "descricao": "Ficar fora de vista.", "atributo": "DES", "tipo": "comum"},
    {"nome": "Furtividade", "descricao": "Mover-se silenciosamente.", "atributo": "DES", "tipo": "comum"},
    {"nome": "Equilíbrio", "descricao": "Manter-se em pé em superfícies instáveis.", "atributo": "DES", "tipo": "comum"},
    {"nome": "Usar Cordas", "descricao": "Amarrar e soltar nós.", "atributo": "DES", "tipo": "comum"},

    # Força
    {"nome": "Escalar", "descricao": "Subir paredes e obstáculos.", "atributo": "FOR", "tipo": "comum"},
    {"nome": "Natação", "descricao": "Nadar.", "atributo": "FOR", "tipo": "comum"},
    {"nome": "Saltar", "descricao": "Distância de salto.", "atributo": "FOR", "tipo": "comum"},

    # Inteligência
    {"nome": "Alquimia", "descricao": "Criar itens alquímicos.", "atributo": "INT", "tipo": "comum", "requer_treinamento": 1},
    {"nome": "Apreciar", "descricao": "Avaliar o valor de itens.", "atributo": "INT", "tipo": "comum"},
    {"nome": "Decifrar Escrita", "descricao": "Traduzir línguas antigas ou códigos.", "atributo": "INT", "tipo": "comum", "requer_treinamento": 1},
    {"nome": "Falsificação", "descricao": "Criar documentos falsos.", "atributo": "INT", "tipo": "comum"},
    {"nome": "Identificar Magia", "descricao": "Reconhecer efeitos mágicos.", "atributo": "INT", "tipo": "comum"},
    {"nome": "Operar Mecanismo", "descricao": "Desativar armadilhas ou dispositivos.", "atributo": "INT", "tipo": "comum", "requer_treinamento": 1},
    {"nome": "Pesquisa", "descricao": "Encontrar informações em bibliotecas.", "atributo": "INT", "tipo": "comum"},
    {"nome": "Procurar", "descricao": "Achar itens escondidos ou armadilhas.", "atributo": "INT", "tipo": "comum"},
    
    # Conhecimento (INT)
    {"nome": "Conhecimento: Arcano", "descricao": "Magia, monstros mágicos.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
    {"nome": "Conhecimento: Arquitetura", "descricao": "Construções e engenharia.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
    {"nome": "Conhecimento: Geografia", "descricao": "Terras, climas.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
    {"nome": "Conhecimento: História", "descricao": "Eventos passados.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
    {"nome": "Conhecimento: Local", "descricao": "Notícias, fofocas.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
    {"nome": "Conhecimento: Natureza", "descricao": "Animais, plantas, clima.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
    {"nome": "Conhecimento: Nobreza", "descricao": "Linhas de sangue, títulos.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
    {"nome": "Conhecimento: Plano", "descricao": "Outras dimensões.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
    {"nome": "Conhecimento: Religião", "descricao": "Divindades, ritos.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},

    # Sabedoria
    {"nome": "Cura", "descricao": "Tratar ferimentos e doenças.", "atributo": "SAB", "tipo": "comum"},
    {"nome": "Intuição", "descricao": "Perceber mentiras e intenções.", "atributo": "SAB", "tipo": "comum"},
    {"nome": "Navegação", "descricao": "Orientar-se.", "atributo": "SAB", "tipo": "comum"},
    {"nome": "Ouvir", "descricao": "Detectar sons.", "atributo": "SAB", "tipo": "comum"},
    {"nome": "Sobrevivência", "descricao": "Rastrear e viver na natureza.", "atributo": "SAB", "tipo": "comum"},
    {"nome": "Profissão", "descricao": "Ofício específico.", "atributo": "SAB", "tipo": "profissao"},

    # Carisma
    {"nome": "Adestrar Animais", "descricao": "Treinar e controlar animais.", "atributo": "CAR", "tipo": "comum", "requer_treinamento": 1},
    {"nome": "Atuação", "descricao": "Dividida em subcategorias (Canto, Dança, Oratória, Instrumentos).", "atributo": "CAR", "tipo": "performance"},
    {"nome": "Diplomacia", "descricao": "Negociar e influenciar.", "atributo": "CAR", "tipo": "comum"},
    {"nome": "Disfarce", "descricao": "Mudar a aparência.", "atributo": "CAR", "tipo": "comum"},
    {"nome": "Intimidação", "descricao": "Ameaçar e coagir.", "atributo": "CAR", "tipo": "comum"},
    {"nome": "Uso de Dispositivos Mágicos", "descricao": "Usar itens de classes diferentes.", "atributo": "CAR", "tipo": "comum", "requer_treinamento": 1},
]


def seed_pericias(db: Session):
    """Popula a tabela de perícias"""
    # Verificar se já existem perícias
    if db.query(Pericia).first():
        print("Perícias já existem no banco de dados")
        return

    pericias = []
    for pericia_data in PERICIAS_PADRAO:
        pericia = Pericia(**pericia_data)
        pericias.append(pericia)
        db.add(pericia)

    db.commit()
    print(f"{len(pericias)} perícias foram criadas com sucesso!")