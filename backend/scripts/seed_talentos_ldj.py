"""
seed_talentos_ldj.py
Script para importar talentos da Tabela 5-1 do Livro do Jogador (D&D 3.5)
para o banco de dados.
"""

import json
import os
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text

# Importar models e database
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from app.core.database import SessionLocal, engine
from app.games.dnd35.models.talento import Talento


def _validar_e_normalizar_talento(talento_data: dict) -> dict:
    """
    Valida e normaliza dados de um talento para evitar erros de validação.
    
    Regras:
    - nome: max 100 caracteres
    - descricao: max 1000 caracteres
    - prerequisitos: max 500 caracteres
    - secao: max 200 caracteres
    
    Args:
        talento_data: Dicionário com dados do talento
        
    Returns:
        Dicionário normalizado
    """
    normalized = {}
    
    # Nome (obrigatório, max 100)
    nome = str(talento_data.get('nome', '')).strip()
    if len(nome) > 100:
        print(f"  ⚠️ Nome truncado: {nome[:50]}... ({len(nome)} → 100 chars)")
        nome = nome[:100]
    normalized['nome'] = nome
    
    # Descrição (max 1000)
    descricao = talento_data.get('descricao') or talento_data.get('beneficios')
    descricao = str(descricao or '').strip()
    if len(descricao) > 1000:
        print(f"  ⚠️ Descrição truncada de {len(descricao)} → 1000 chars")
        descricao = descricao[:1000]
    normalized['descricao'] = descricao or None
    
    # Pré-requisitos (max 500)
    prerequisitos = str(talento_data.get('prerequisitos', '')).strip()
    if prerequisitos and prerequisitos != '-':
        if len(prerequisitos) > 500:
            print(f"  ⚠️ Pré-requisitos truncados de {len(prerequisitos)} → 500 chars")
            prerequisitos = prerequisitos[:500]
        normalized['prerequisitos'] = prerequisitos
    else:
        normalized['prerequisitos'] = None
    
    # Seção (max 200)
    secao = str(talento_data.get('secao', '')).strip()
    if len(secao) > 200:
        # Se seção está muito grande, é provável um erro de importação
        # Mover para descrição
        print(f"  ⚠️ Seção com {len(secao)} chars (esperado < 200), movendo para descrição")
        if not normalized['descricao']:
            normalized['descricao'] = secao
        normalized['secao'] = None
    else:
        normalized['secao'] = secao or None
    
    return normalized


def seed_talentos_from_json(json_file: str = 'talentos_importacao_limpo.json'):
    """
    Importa talentos do arquivo JSON gerado a partir da tabela Excel.
    
    Args:
        json_file: Caminho relativo ao arquivo JSON de importação
    """
    
    # Caminho absoluto do arquivo
    file_path = os.path.join(os.path.dirname(__file__), '..', '..', json_file)
    
    if not os.path.exists(file_path):
        print(f"❌ Arquivo {file_path} não encontrado")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            talentos_data = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler arquivo JSON: {e}")
        return False
    
    db = SessionLocal()
    
    try:
        # Limpar talentos existentes (opcional)
        # db.query(Talento).delete()
        # db.commit()
        
        talentos_criados = 0
        talentos_atualizados = 0
        talentos_com_aviso = 0
        
        for idx, talento_data in enumerate(talentos_data):
            # Validar e normalizar dados
            normalized = _validar_e_normalizar_talento(talento_data)
            
            if not normalized['nome']:
                print(f"  ⚠️ Talento #{idx} sem nome, pulando")
                continue
            
            # Verificar se talento já existe pelo nome
            talento_existente = db.query(Talento).filter(
                Talento.nome == normalized['nome']
            ).first()
            
            if talento_existente:
                # Atualizar campos se ainda não tinha informação
                if not talento_existente.prerequisitos:
                    talento_existente.prerequisitos = normalized['prerequisitos']
                if not talento_existente.secao:
                    talento_existente.secao = normalized['secao']
                if not talento_existente.descricao:
                    talento_existente.descricao = normalized['descricao']
                
                talentos_atualizados += 1
            else:
                # Criar novo talento
                novo_talento = Talento(
                    nome=normalized['nome'],
                    descricao=normalized['descricao'],
                    prerequisitos=normalized['prerequisitos'],
                    secao=normalized['secao'],
                    pagina_referencia=None,  # Não há página de referência na tabela
                    ativo=True,
                    criado_em=datetime.now(timezone.utc)
                )
                db.add(novo_talento)
                talentos_criados += 1
        
        db.commit()
        
        print(f"✅ Seed de talentos concluído!")
        print(f"   • {talentos_criados} novos talentos criados")
        print(f"   • {talentos_atualizados} talentos atualizados")
        print(f"   • Total: {len(talentos_data)} talentos processados")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro durante seed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == '__main__':
    print("🎲 Iniciando seed de talentos D&D 3.5...")
    seed_talentos_from_json()
