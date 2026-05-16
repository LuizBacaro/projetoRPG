"""
processar_talentos_excel.py
Script para processar e importar talentos da Tabela 5-1 do Livro do Jogador (D&D 3.5)
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime, timezone

# Caminho para o arquivo Excel
PLANILHA_PATH = Path("Tabela_5-1_Talentos_LdJ.xlsx")

def processar_talentos_excel() -> List[Dict[str, Any]]:
    """
    Processa o arquivo Excel de talentos e retorna lista de dicionários
    com os dados normalizados.
    """
    print(f"📖 Processando arquivo: {PLANILHA_PATH}")

    if not PLANILHA_PATH.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {PLANILHA_PATH}")

    # Ler Excel (assumindo que os cabeçalhos estão na linha 0)
    df = pd.read_excel(PLANILHA_PATH, header=0)

    print(f"📊 Shape do DataFrame: {df.shape}")
    print(f"📋 Colunas encontradas: {df.columns.tolist()}")

    talentos = []

    for idx, row in df.iterrows():
        try:
            # Mapear colunas do Excel para campos do modelo
            talento_data = {
                'nome': str(row.get('Talento', '')).strip(),
                'beneficios': str(row.get('Benefícios', '')).strip(),
                'prerequisitos': str(row.get('Pré-requisitos', '')).strip(),
                'secao': str(row.get('Seção', '')).strip(),
                'pagina_referencia': '',  # Não tem coluna Página no Excel
            }

            # Limpar valores vazios
            for key, value in talento_data.items():
                if value == 'nan' or value == 'NaN':
                    talento_data[key] = ''

            # Validar dados mínimos
            if not talento_data['nome']:
                print(f"⚠️  Linha {idx + 2}: talento sem nome, pulando")
                continue

            # Normalizar secao (remover "Seção" se estiver presente)
            secao = talento_data['secao']
            if secao.startswith('Seção'):
                secao = secao.replace('Seção', '').strip()
            talento_data['secao'] = secao

            talentos.append(talento_data)

        except Exception as e:
            print(f"❌ Erro na linha {idx + 2}: {e}")
            continue

    print(f"✅ Processados {len(talentos)} talentos válidos")
    return talentos

def salvar_json(talentos: List[Dict[str, Any]], output_file: str = 'talentos_importacao_limpo.json'):
    """Salva os dados processados em arquivo JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(talentos, f, ensure_ascii=False, indent=2)

    print(f"💾 Dados salvos em: {output_file}")

def main():
    """Função principal"""
    try:
        # Processar Excel
        talentos = processar_talentos_excel()

        # Salvar JSON
        salvar_json(talentos)

        # Mostrar preview
        print("\n📋 Preview dos primeiros 3 talentos:")
        for i, talento in enumerate(talentos[:3]):
            print(f"{i+1}. {talento['nome']}")
            print(f"   Benefícios: {talento['beneficios'][:50]}...")
            print(f"   Pré-requisitos: {talento['prerequisitos']}")
            print(f"   Seção: {talento['secao']}")
            print()

    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())