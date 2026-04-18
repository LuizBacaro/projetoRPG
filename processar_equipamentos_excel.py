"""
Script para processar planilha Excel de equipamentos D&D 3.5
Gera seed atualizado com novos campos da tabela 7-5
"""

import pandas as pd
import json
from pathlib import Path

def processar_planilha_equipamentos():
    """Processa a planilha Excel e retorna dados estruturados"""

    # Caminho da planilha
    planilha_path = Path('Tabela_7-5_Armas_EQUIPAMENTOS.xlsx')

    if not planilha_path.exists():
        raise FileNotFoundError(f"Planilha não encontrada: {planilha_path}")

    # Ler planilha (header=3 para começar da linha 4, 0-indexed)
    df = pd.read_excel(planilha_path, header=3)

    # Filtrar linhas válidas
    df_clean = df.dropna(subset=['Arma']).copy()

    # Remover linhas de notas
    df_clean = df_clean[~df_clean['Categoria'].str.contains(r'^[¹²³⁴⁵]', na=False, regex=True)]
    df_clean = df_clean[~df_clean['Categoria'].str.contains('Notas da tabela', na=False)]
    df_clean = df_clean[~df_clean['Arma'].str.contains(r'^[¹²³⁴⁵]', na=False, regex=True)]

    # Remover linhas completamente vazias
    df_clean = df_clean.dropna(how='all')

    print(f"📊 Processando {len(df_clean)} equipamentos válidos")

    # Converter para lista de dicionários
    equipamentos = []
    for _, row in df_clean.iterrows():
        equipamento = {
            'nome': str(row['Arma']).strip(),
            'categoria': str(row['Categoria']).strip() if pd.notna(row['Categoria']) else None,
            'subcategoria': str(row['Subcategoria']).strip() if pd.notna(row['Subcategoria']) and row['Subcategoria'] != '—' else None,
            'custo': str(row['Custo']).strip() if pd.notna(row['Custo']) and row['Custo'] != '—' else None,
            'dano_pequeno': str(row['Dano (P)']).strip() if pd.notna(row['Dano (P)']) and row['Dano (P)'] != '—' else None,
            'dano_medio': str(row['Dano (M)']).strip() if pd.notna(row['Dano (M)']) and row['Dano (M)'] != '—' else None,
            'critico': str(row['Crítico']).strip() if pd.notna(row['Crítico']) and row['Crítico'] != '—' else None,
            'alcance_incremento': str(row['Alcance / incremento']).strip() if pd.notna(row['Alcance / incremento']) and row['Alcance / incremento'] != '—' else None,
            'peso': str(row['Peso']).strip() if pd.notna(row['Peso']) and row['Peso'] != '—' else None,
            'tipo_dano': str(row['Tipo de dano']).strip() if pd.notna(row['Tipo de dano']) and row['Tipo de dano'] != '—' else None,
            'pagina_referencia': 'PHB p.120-126',  # Página padrão da tabela de armas
            'ativo': True
        }
        equipamentos.append(equipamento)

    return equipamentos

def gerar_seed_script(equipamentos):
    """Gera o script de seed atualizado"""

    # Template do script
    template = '''"""
Seed de equipamentos D&D 3.5 atualizado com dados da Tabela 7-5
Gerado automaticamente a partir da planilha Excel
"""

EQUIPAMENTOS_PADRAO = [
{equipamentos_list}
]

EQUIPAMENTOS_DADOS = [
{equipamentos_dados}
]

def seed_equipamentos(db):
    """
    Popula a tabela de equipamentos com dados da Tabela 7-5.
    """
    from app.models.equipamento import Equipamento
    from datetime import datetime, timezone

    # Verificar se já existem equipamentos
    count = db.query(Equipamento).count()
    if count > 0:
        print(f"✅ Equipamentos já existem ({{count}}). Pulando seed.")
        return

    print("📦 Iniciando seed de equipamentos da Tabela 7-5...")

    for equipamento_data in EQUIPAMENTOS_DADOS:
        equipamento = Equipamento(
            nome=equipamento_data['nome'],
            categoria=equipamento_data.get('categoria'),
            subcategoria=equipamento_data.get('subcategoria'),
            custo=equipamento_data.get('custo'),
            dano_pequeno=equipamento_data.get('dano_pequeno'),
            dano_medio=equipamento_data.get('dano_medio'),
            critico=equipamento_data.get('critico'),
            alcance_incremento=equipamento_data.get('alcance_incremento'),
            peso=equipamento_data.get('peso'),
            tipo_dano=equipamento_data.get('tipo_dano'),
            pagina_referencia=equipamento_data.get('pagina_referencia'),
            ativo=equipamento_data.get('ativo', True),
            criado_em=datetime.now(timezone.utc)
        )
        db.add(equipamento)

    db.commit()
    print(f"✅ {{len(EQUIPAMENTOS_DADOS)}} equipamentos inseridos com sucesso!")
'''

    # Gerar lista formatada para EQUIPAMENTOS_PADRAO (formato antigo)
    equipamentos_padrao = []
    for eq in equipamentos[:10]:  # Apenas primeiros 10 para compatibilidade
        nome = eq['nome']
        desc_parts = []
        if eq.get('categoria'):
            desc_parts.append(f"Categoria: {eq['categoria']}")
        if eq.get('custo'):
            desc_parts.append(f"Custo: {eq['custo']}")
        if eq.get('dano_medio'):
            desc_parts.append(f"Dano: {eq['dano_medio']}")
        descricao = "; ".join(desc_parts) if desc_parts else "Equipamento D&D 3.5"
        pag_ref = eq.get('pagina_referencia', 'PHB p.120-126')

        equipamentos_padrao.append(f"    (\"{nome}\", \"{descricao}\", \"{pag_ref}\"),")

    equipamentos_padrao_str = "\n".join(equipamentos_padrao)

    # Gerar lista completa para EQUIPAMENTOS_DADOS
    equipamentos_dados = []
    for eq in equipamentos:
        eq_str = "    {\n"
        for key, value in eq.items():
            if value is None:
                eq_str += f"        '{key}': None,\n"
            elif isinstance(value, str):
                eq_str += f"        '{key}': \"{value}\",\n"
            else:
                eq_str += f"        '{key}': {value},\n"
        eq_str = eq_str.rstrip(',\n') + "\n    },"
        equipamentos_dados.append(eq_str)

    equipamentos_dados_str = "\n".join(equipamentos_dados)

    # Preencher template
    script_content = template.format(
        equipamentos_list=equipamentos_padrao_str,
        equipamentos_dados=equipamentos_dados_str
    )

    return script_content

if __name__ == "__main__":
    try:
        # Processar planilha
        equipamentos = processar_planilha_equipamentos()

        # Gerar script de seed
        seed_script = gerar_seed_script(equipamentos)

        # Salvar script
        output_path = Path('backend/scripts/seed_equipamentos_atualizado.py')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(seed_script)

        print(f"✅ Script de seed gerado: {output_path}")
        print(f"📊 {len(equipamentos)} equipamentos processados")

        # Mostrar preview
        print("\n🔍 Preview dos primeiros 3 equipamentos:")
        for i, eq in enumerate(equipamentos[:3]):
            print(f"  {i+1}. {eq['nome']} ({eq.get('categoria', 'N/A')})")

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()