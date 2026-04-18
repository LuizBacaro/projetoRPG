#!/usr/bin/env python3
"""Gera XLSX da Tabela 7-5: Armas a partir do texto extraído do LdJ D&D 3.5 (PDF)."""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Tabela_7-5_Armas_EQUIPAMENTOS.xlsx"

# Colunas alinhadas ao cabeçalho do livro (ajuste de ordem: Crítico antes de alcance)
HEADERS = [
    "Categoria",
    "Subcategoria",
    "Arma",
    "Custo",
    "Dano (P)",
    "Dano (M)",
    "Crítico",
    "Alcance / incremento",
    "Peso",
    "Tipo de dano",
]

# Tuplas: (categoria, subcategoria, arma, custo, dP, dM, crit, alcance, peso, tipo)
ROWS = [
    ("Armas simples", "—", "Ataque desarmado", "—", "1d2", "1d3", "×2", "—", "—", "Concussão"),
    ("Armas simples", "—", "Manopla", "2 PO", "1d2", "1d3", "×2", "—", "0,5 kg", "Concussão"),
    ("Armas simples", "Armas leves – corpo a corpo", "Adaga", "2 PO", "1d3", "1d4", "19–20/×2", "3 m", "0,5 kg", "Perfurante ou cortante"),
    ("Armas simples", "Armas leves – corpo a corpo", "Adaga de soco", "2 PO", "1d3", "1d4", "×3", "—", "0,5 kg", "Perfurante"),
    ("Armas simples", "Armas leves – corpo a corpo", "Foice curta", "6 PO", "1d4", "1d6", "×2", "—", "1 kg", "Cortante"),
    ("Armas simples", "Armas leves – corpo a corpo", "Maça leve", "5 PO", "1d4", "1d6", "×2", "—", "2 kg", "Concussão"),
    ("Armas simples", "Armas leves – corpo a corpo", "Manopla com cravos", "5 PO", "1d3", "1d4", "×2", "—", "0,5 kg", "Perfurante"),
    ("Armas simples", "Armas de uma mão – corpo a corpo", "Clava", "—", "1d4", "1d6", "×2", "3 m", "1,5 kg", "Concussão"),
    ("Armas simples", "Armas de uma mão – corpo a corpo", "Lança curta", "1 PO", "1d4", "1d6", "×2", "6 m", "1,5 kg", "Perfurante"),
    ("Armas simples", "Armas de uma mão – corpo a corpo", "Maça pesada", "12 PO", "1d6", "1d8", "×2", "—", "4 kg", "Concussão"),
    ("Armas simples", "Armas de uma mão – corpo a corpo", "Maça-estrela", "8 PO", "1d6", "1d8", "×2", "—", "3 kg", "Concussão e perfurante"),
    ("Armas simples", "Armas de duas mãos – corpo a corpo", "Bordão⁵", "—", "1d4/1d4", "1d6/1d6", "×2", "—", "2 kg", "Concussão"),
    ("Armas simples", "Armas de duas mãos – corpo a corpo", "Lança", "2 PO", "1d6", "1d8", "×3", "6 m", "3 kg", "Perfurante"),
    ("Armas simples", "Armas de duas mãos – corpo a corpo", "Lança longa⁴", "5 PO", "1d6", "1d8", "×3", "—", "4,5 kg", "Perfurante"),
    ("Armas simples", "Armas de ataque à distância", "Azagaia", "1 PO", "1d4", "1d6", "×2", "9 m", "1 kg", "Perfurante"),
    ("Armas simples", "Armas de ataque à distância", "Besta leve", "35 PO", "1d6", "1d8", "19–20/×2", "24 m", "2 kg", "Perfurante"),
    ("Armas simples", "Armas de ataque à distância", "Virotes de besta (10)", "1 PO", "—", "—", "—", "—", "0,5 kg", "—"),
    ("Armas simples", "Armas de ataque à distância", "Besta pesada", "50 PO", "1d8", "1d10", "19–20/×2", "36 m", "4 kg", "Perfurante"),
    ("Armas simples", "Armas de ataque à distância", "Virotes de besta (10)", "1 PO", "—", "—", "—", "—", "0,5 kg", "—"),
    ("Armas simples", "Armas de ataque à distância", "Dardo", "5 PP", "1d3", "1d4", "×2", "6 m", "0,5 kg", "Perfurante"),
    ("Armas simples", "Armas de ataque à distância", "Funda", "—", "1d3", "1d4", "×2", "15 m", "0 kg", "Concussão"),
    ("Armas simples", "Armas de ataque à distância", "Balas de funda (10)", "1 PP", "—", "—", "—", "—", "2,5 kg", "—"),
    ("Armas comuns", "Armas leves – corpo a corpo", "Armaduras com cravos", "especial", "1d4", "1d6", "×2", "—", "especial", "Perfurante"),
    ("Armas comuns", "Armas leves – corpo a corpo", "Escudo pequeno", "especial", "1d2", "1d3", "×2", "—", "especial", "Concussão"),
    ("Armas comuns", "Armas leves – corpo a corpo", "Escudo pequeno com cravos", "especial", "1d3", "1d4", "×2", "—", "especial", "Perfurante"),
    ("Armas comuns", "Armas leves – corpo a corpo", "Espada curta", "10 PO", "1d4", "1d6", "19–20/×2", "—", "1 kg", "Perfurante"),
    ("Armas comuns", "Armas leves – corpo a corpo", "Kukri", "8 PO", "1d3", "1d4", "18–20/×2", "—", "1 kg", "Cortante"),
    ("Armas comuns", "Armas leves – corpo a corpo", "Machadinha", "6 PO", "1d4", "1d6", "×3", "—", "1,5 kg", "Cortante"),
    ("Armas comuns", "Armas leves – corpo a corpo", "Machado de arremesso", "8 PO", "1d4", "1d6", "×2", "3 m", "1 kg", "Cortante"),
    ("Armas comuns", "Armas leves – corpo a corpo", "Martelo leve", "1 PO", "1d3", "1d4", "×2", "6 m", "1 kg", "Concussão"),
    ("Armas comuns", "Armas leves – corpo a corpo", "Picareta leve", "4 PO", "1d3", "1d4", "×4", "—", "1,5 kg", "Perfurante"),
    ("Armas comuns", "Armas leves – corpo a corpo", "Porrete", "1 PO", "1d4", "1d6", "×2", "—", "1 kg", "Concussão"),
    ("Armas comuns", "Armas de uma mão – corpo a corpo", "Cimitarra", "15 PO", "1d4", "1d6", "18–20/×2", "—", "2 kg", "Cortante"),
    ("Armas comuns", "Armas de uma mão – corpo a corpo", "Escudo grande", "especial", "1d3", "1d4", "×2", "—", "especial", "Concussão"),
    ("Armas comuns", "Armas de uma mão – corpo a corpo", "Escudo grande com cravos", "especial", "1d4", "1d6", "×2", "—", "especial", "Perfurante"),
    ("Armas comuns", "Armas de uma mão – corpo a corpo", "Espada longa", "15 PO", "1d6", "1d8", "19–20/×2", "—", "2 kg", "Cortante"),
    ("Armas comuns", "Armas de uma mão – corpo a corpo", "Machado de batalha", "10 PO", "1d6", "1d8", "×3", "—", "3 kg", "Cortante"),
    ("Armas comuns", "Armas de uma mão – corpo a corpo", "Mangual", "8 PO", "1d6", "1d8", "×2", "—", "2,5 kg", "Concussão"),
    ("Armas comuns", "Armas de uma mão – corpo a corpo", "Martelo de guerra", "12 PO", "1d6", "1d8", "×3", "—", "2,5 kg", "Concussão"),
    ("Armas comuns", "Armas de uma mão – corpo a corpo", "Picareta pesada", "8 PO", "1d4", "1d6", "×4", "—", "3 kg", "Perfurante"),
    ("Armas comuns", "Armas de uma mão – corpo a corpo", "Sabre", "20 PO", "1d4", "1d6", "18–20/×2", "—", "1 kg", "Perfurante"),
    ("Armas comuns", "Armas de uma mão – corpo a corpo", "Tridente", "15 PO", "1d6", "1d8", "×2", "3 m", "2 kg", "Perfurante"),
    ("Armas comuns", "Armas de duas mãos – corpo a corpo", "Alabarda", "10 PO", "1d8", "1d10", "×3", "—", "11 kg", "Perfurante ou cortante"),
    ("Armas comuns", "Armas de duas mãos – corpo a corpo", "Clava grande", "5 PO", "1d8", "1d10", "×2", "—", "4 kg", "Concussão"),
    ("Armas comuns", "Armas de duas mãos – corpo a corpo", "Espada larga", "50 PO", "1d10", "2d6", "19–20/×2", "—", "4 kg", "Cortante"),
    ("Armas comuns", "Armas de duas mãos – corpo a corpo", "Falcione", "75 PO", "1d6", "2d4", "18–20/×2", "—", "4 kg", "Cortante"),
    ("Armas comuns", "Armas de duas mãos – corpo a corpo", "Foice longa", "18 PO", "1d6", "2d4", "×4", "—", "10 kg", "Perfurante ou cortante"),
    ("Armas comuns", "Armas de duas mãos – corpo a corpo", "Glaive⁴", "8 PO", "1d8", "1d10", "×3", "—", "10 kg", "Cortante"),
    ("Armas comuns", "Armas de duas mãos – corpo a corpo", "Guisarme⁴", "9 PO", "1d6", "2d4", "×3", "—", "11 kg", "Cortante"),
    ("Armas comuns", "Armas de duas mãos – corpo a corpo", "Lança⁴", "10 PO", "1d6", "1d8", "×3", "—", "10 kg", "Perfurante"),
    ("Armas comuns", "Armas de duas mãos – corpo a corpo", "Machado grande", "20 PO", "1d10", "1d12", "×3", "—", "11 kg", "Cortante"),
    ("Armas comuns", "Armas de duas mãos – corpo a corpo", "Mangual pesado", "15 PO", "1d8", "1d10", "19–20/×2", "—", "10 kg", "Concussão"),
    ("Armas comuns", "Armas de duas mãos – corpo a corpo", "Ranseur⁴", "10 PO", "1d6", "2d4", "×3", "—", "11 kg", "Perfurante"),
    ("Armas comuns", "Armas de ataque à distância", "Arco curto", "30 PO", "1d4", "1d6", "×3", "18 m", "1 kg", "Perfurante"),
    ("Armas comuns", "Armas de ataque à distância", "Flechas (20)", "1 PO", "—", "—", "—", "—", "1,5 kg", "—"),
    ("Armas comuns", "Armas de ataque à distância", "Arco curto composto", "75 PO", "1d4", "1d6", "×3", "21 m", "1 kg", "Perfurante"),
    ("Armas comuns", "Armas de ataque à distância", "Flechas (20)", "1 PO", "—", "—", "—", "—", "1,5 kg", "—"),
    ("Armas comuns", "Armas de ataque à distância", "Arco longo", "75 PO", "1d6", "1d8", "×3", "30 m", "1,5 kg", "Perfurante"),
    ("Armas comuns", "Armas de ataque à distância", "Flechas (20)", "1 PO", "—", "—", "—", "—", "1,5 kg", "—"),
    ("Armas comuns", "Armas de ataque à distância", "Arco longo composto", "100 PO", "1d6", "1d8", "×3", "33 m", "1,5 kg", "Perfurante"),
    ("Armas comuns", "Armas de ataque à distância", "Flechas (20)", "1 PO", "—", "—", "—", "—", "1,5 kg", "—"),
    ("Armas exóticas", "Armas leves – corpo a corpo", "Kama", "2 PO", "1d4", "1d6", "×2", "—", "1 kg", "Cortante"),
    ("Armas exóticas", "Armas leves – corpo a corpo", "Nunchaku", "2 PO", "1d4", "1d6", "×2", "—", "1 kg", "Concussão"),
    ("Armas exóticas", "Armas leves – corpo a corpo", "Sai", "1 PO", "1d3", "1d4", "×2", "3 m", "0,5 kg", "Concussão"),
    ("Armas exóticas", "Armas leves – corpo a corpo", "Siangham", "3 PO", "1d4", "1d6", "×2", "—", "0,5 kg", "Perfurante"),
    ("Armas exóticas", "Armas de uma mão – corpo a corpo", "Chicote⁴", "1 PO", "1d2", "1d3", "×2", "—", "1 kg", "Cortante"),
    ("Armas exóticas", "Armas de uma mão – corpo a corpo", "Espada bastarda", "35 PO", "1d8", "1d10", "19–20/×2", "—", "3 kg", "Cortante"),
    ("Armas exóticas", "Armas de uma mão – corpo a corpo", "Machado de guerra anão", "30 PO", "1d8", "1d10", "×3", "—", "4 kg", "Cortante"),
    ("Armas exóticas", "Armas de duas mãos – corpo a corpo", "Corrente com cravos⁴", "25 PO", "1d6", "2d4", "×2", "—", "10 kg", "Perfurante"),
    ("Armas exóticas", "Armas de duas mãos – corpo a corpo", "Espada de duas lâminas⁵", "100 PO", "1d6/1d6", "1d8/1d8", "19–20/×2", "—", "10 kg", "Cortante"),
    ("Armas exóticas", "Armas de duas mãos – corpo a corpo", "Machado orc duplo⁵", "60 PO", "1d6/1d6", "1d8/1d8", "×3", "—", "12,5 kg", "Cortante"),
    ("Armas exóticas", "Armas de duas mãos – corpo a corpo", "Mangual atroz⁵", "90 PO", "1d6/1d6", "1d8/1d8", "×2", "—", "10 kg", "Concussão"),
    ("Armas exóticas", "Armas de duas mãos – corpo a corpo", "Martelo gnomo com gancho⁵", "20 PO", "1d6/1d4", "1d8/1d6", "×3/×4", "—", "3 kg", "Concussão e perfurante"),
    ("Armas exóticas", "Armas de duas mãos – corpo a corpo", "Urgrosh anão⁵", "50 PO", "1d6/1d4", "1d8/1d6", "×3", "—", "11 kg", "Cortante ou perfurante"),
    ("Armas exóticas", "Armas de ataque à distância", "Besta leve de repetição", "250 PO", "1d6", "1d8", "19–20/×2", "24 m", "3 kg", "Perfurante"),
    ("Armas exóticas", "Armas de ataque à distância", "Virotes de besta (5)", "1 PO", "—", "—", "—", "—", "0,5 kg", "—"),
    ("Armas exóticas", "Armas de ataque à distância", "Besta pesada de repetição", "400 PO", "1d8", "1d10", "19–20/×2", "36 m", "11 kg", "Perfurante"),
    ("Armas exóticas", "Armas de ataque à distância", "Virotes de besta (5)", "1 PO", "—", "—", "—", "—", "0,5 kg", "—"),
    ("Armas exóticas", "Armas de ataque à distância", "Besta de mão", "100 PO", "1d3", "1d4", "19–20/×2", "9 m", "1 kg", "Perfurante"),
    ("Armas exóticas", "Armas de ataque à distância", "Virotes de besta (10)", "1 PO", "—", "—", "—", "—", "0,5 kg", "—"),
    ("Armas exóticas", "Armas de ataque à distância", "Boleadeira", "5 PO", "1d3", "1d4", "×2", "3 m", "1 kg", "Concussão"),
    ("Armas exóticas", "Armas de ataque à distância", "Rede", "20 PO", "—", "—", "—", "3 m", "3 kg", "—"),
    ("Armas exóticas", "Armas de ataque à distância", "Shuriken (5)", "1 PO", "1", "1d2", "×2", "3 m", "0,25 kg", "Perfurante"),
]

NOTAS = [
    "¹ Peso da coluna: armas Médias; Pequena = metade, Grande = dobro (rodapé 1 da tabela).",
    "² Tipos de dano: ver descrições com «e» ou «ou» no livro (rodapé 2).",
    "³ Arma que causa dano de concussão não letal em vez de letal (rodapé 3).",
    "⁴ Arma de haste (rodapé 4).",
    "⁵ Arma dupla (rodapé 5).",
]


def main() -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "EQUIPAMENTOS"

    ws["A1"] = "Tabela 7-5: Armas — D&D 3.5 Livro do Jogador (extração textual do PDF)"
    ws["A1"].font = Font(bold=True)
    ws.merge_cells("A1:J1")
    ws["A2"] = (
        "Fonte: texto nativo (pdfplumber). No PDF deste arquivo a tabela ocupa as páginas 101–102 (índice 0-based); "
        "rodapés da edição impressa costumam corresponder a ~98–99."
    )
    ws.merge_cells("A2:J2")
    ws.append([])
    ws.append(HEADERS)
    for r in range(4, 5):
        for c in ws[r]:
            c.font = Font(bold=True)

    for row in ROWS:
        ws.append(list(row))

    ws.append([])
    ws.append(["Notas da tabela (livro)", "", "", "", "", "", "", "", "", ""])
    ws.cell(row=ws.max_row, column=1).font = Font(bold=True)
    for n in NOTAS:
        ws.append([n, "", "", "", "", "", "", "", "", ""])

    for idx in range(1, len(HEADERS) + 1):
        letter = get_column_letter(idx)
        maxlen = 12
        for row in ws.iter_rows(
            min_row=1, max_row=ws.max_row, min_col=idx, max_col=idx
        ):
            cell = row[0]
            if getattr(cell, "value", None) is not None:
                maxlen = max(maxlen, len(str(cell.value)))
        ws.column_dimensions[letter].width = min(maxlen + 2, 55)

    for row in ws.iter_rows(min_row=5, max_row=4 + len(ROWS)):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(OUT)
    print(f"Escrito: {OUT} ({len(ROWS)} armas)")


if __name__ == "__main__":
    main()
