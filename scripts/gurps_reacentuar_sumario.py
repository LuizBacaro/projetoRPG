#!/usr/bin/env python3
"""
Aplica acentuacao portuguesa canonica aos nomes de vantagens e desvantagens
no ``gurps_personagens_sumario_catalogo.json``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = (
    ROOT
    / "backend"
    / "app"
    / "games"
    / "gurps"
    / "catalogs"
    / "gurps_personagens_sumario_catalogo.json"
)

# Mapeamento canonico nome_sem_acento -> nome_com_acento (baseado no
# Modulo Basico - Personagens, tabelas de referencia pags. 298-301).
NOMES = {
    # ------- Vantagens -------
    "Abencoado": "Abençoado",
    "Acessorios": "Acessórios",
    "Adaptabilidade Cultural": "Adaptabilidade Cultural",
    "Adaptacao ao Terreno": "Adaptação ao Terreno",
    "Aderencia": "Aderência",
    "Anfibio": "Anfíbio",
    "Aparencia": "Aparência",
    "Aptidao Magica": "Aptidão Mágica",
    "Artifice": "Artífice",
    "Atribulacao": "Atribulação",
    "Audicao Agucada": "Audição Aguçada",
    "Audicao Discriminatoria": "Audição Discriminatória",
    "Audicao Parabolica": "Audição Parabólica",
    "Audicao Subsonica": "Audição Subsônica",
    "Bracos Adicionais": "Braços Adicionais",
    "Cabeca Adicional": "Cabeça Adicional",
    "Calculos Instantaneos": "Cálculos Instantâneos",
    "Camaleao": "Camaleão",
    "Camaleao Social": "Camaleão Social",
    "Caminhar sobre Liquidos": "Caminhar sobre Líquidos",
    "Canalizacao": "Canalização",
    "Carga Util": "Carga Útil",
    "Cibernetica": "Cibernética",
    "Clarisenciencia": "Clarisenciência",
    "Controle Termico": "Controle Térmico",
    "Cronolocalizacao": "Cronolocalização",
    "Detectar": "Detectar",
    "Dificil de Subjugar": "Difícil de Subjugar",
    "Digestao Universal": "Digestão Universal",
    "Dominacao": "Dominação",
    "Duplicacao": "Duplicação",
    "Empatia com Espiritos": "Empatia com Espíritos",
    "Equilibrio Perfeito": "Equilíbrio Perfeito",
    "Equipamento Caracteristico": "Equipamento Característico",
    "Escavacao": "Escavação",
    "Estatica Psiquica": "Estática Psíquica",
    "Experiencia-G": "Experiência-G",
    "Fe": "Fé",
    "Habilidade Matematica": "Habilidade Matemática",
    "Hierarquia Honoraria": "Hierarquia Honorária",
    "Idade Imutavel": "Idade Imutável",
    "Impossivel de Matar": "Impossível de Matar",
    "Indomavel": "Indomável",
    "Inercia Temporal": "Inércia Temporal",
    "Infravisao": "Infravisão",
    "Interposicao": "Interposição",
    "Intuicao": "Intuição",
    "Investidura de Poder": "Investidura de Poder",
    "Lamentavel": "Lamentável",
    "Lingua Ferina": "Língua Ferina",
    "Matematico Intuitivo": "Matemático Intuitivo",
    "Medium": "Médium",
    "Memoria Eidetica": "Memória Eidética",
    "Memoria Fotografica": "Memória Fotográfica",
    "Memoria Racial": "Memória Racial",
    "Metabolismo Impoluto": "Metabolismo Impoluto",
    "Nao Come nem Bebe": "Não Come nem Bebe",
    "Nao Dorme": "Não Dorme",
    "Nao Respira": "Não Respira",
    "Nocao do Perigo": "Noção do Perigo",
    "Nocao do Tempo Ampliado": "Noção do Tempo Ampliado",
    "Nocao Exata do Tempo": "Noção Exata do Tempo",
    "Nocao Tridimensional do Espaco": "Noção Tridimensional do Espaço",
    "Olfato Discriminatorio": "Olfato Discriminatório",
    "Oraculo": "Oráculo",
    "Padrao de Tempo Alterado": "Padrão de Tempo Alterado",
    "Paladar Discriminatorio": "Paladar Discriminatório",
    "Permissao de Seguranca": "Permissão de Segurança",
    "Precognicao": "Precognição",
    "Prender a Respiracao": "Prender a Respiração",
    "Proposito Maior": "Propósito Maior",
    "Pulmoes com Filtro": "Pulmões com Filtro",
    "Reconhecimento Social": "Reconhecimento Social",
    "Recuperacao Acelerada": "Recuperação Acelerada",
    "Recuperacao da Consciencia": "Recuperação da Consciência",
    "Recuperacao Muito Acelerada": "Recuperação Muito Acelerada",
    "Reivindicar Hospitalidade": "Reivindicar Hospitalidade",
    "Renda Propria": "Renda Própria",
    "Reputacao": "Reputação",
    "Resistencia a Dano": "Resistência a Dano",
    "Resistencia a Pressao": "Resistência à Pressão",
    "Resistencia ao Vacuo": "Resistência ao Vácuo",
    "Regeneracao": "Regeneração",
    "Retencao": "Retenção",
    "Senso de Direcao": "Senso de Direção",
    "Sensivel": "Sensível",
    "Sentido de Vibracao": "Sentido de Vibração",
    "Sentido Protegido": "Sentido Protegido",
    "Silencio": "Silêncio",
    "ST Bracal": "ST Braçal",
    "Superaudicao": "Superaudição",
    "Tato Apurado": "Tato Apurado",
    "Telecomunicacao": "Telecomunicação",
    "Titere": "Títere",
    "Tolerancia a Ferimentos": "Tolerância a Ferimentos",
    "Tolerancia a Radiacao": "Tolerância à Radiação",
    "Tolerancia a Temperatura": "Tolerância à Temperatura",
    "Tolerancia ao Alcool": "Tolerância ao Álcool",
    "Tolerancia-G Ampliada": "Tolerância-G Ampliada",
    "Toque Sensivel": "Toque Sensível",
    "Ultraflexibilidade das Juntas": "Ultraflexibilidade das Juntas",
    "Ultravisao": "Ultravisão",
    "Ver o Invisivel": "Ver o Invisível",
    "Versatil": "Versátil",
    "Vinculo Especial": "Vínculo Especial",
    "Visao 360 Graus": "Visão 360 Graus",
    "Visao Agucada": "Visão Aguçada",
    "Visao Hiperespectral": "Visão Hiperespectral",
    "Visao Microscopica": "Visão Microscópica",
    "Visao no Escuro": "Visão no Escuro",
    "Visao Noturna": "Visão Noturna",
    "Visao Penetrante": "Visão Penetrante",
    "Visao Periferica": "Visão Periférica",
    "Visao Telescopica": "Visão Telescópica",
    "Visualizacao": "Visualização",
    "Xeno-adaptabilidade": "Xeno-adaptabilidade",
    "Fala Subsonica": "Fala Subsônica",
    "Fala Ultrassonica": "Fala Ultrassônica",
    "Fala Subaquatica": "Fala Subaquática",
    "Membrana Nictitante": "Membrana Nictitante",
    "Encolhimento": "Encolhimento",
    "Escorregadio": "Escorregadio",
    "Investidura de Poder": "Investidura de Poder",
    # ------- Desvantagens -------
    "Altruismo": "Altruísmo",
    "Amigavel": "Amigável",
    "Amnesia": "Amnésia",
    "Antipatico": "Antipático",
    "Apetite Incontrolavel": "Apetite Incontrolável",
    "Aversao": "Aversão",
    "Aversoes": "Aversões",
    "Autodestruicao": "Autodestruição",
    "Avareza": "Avareza",
    "Bioquimica Incomum": "Bioquímica Incomum",
    "Cegueira": "Cegueira",
    "Circunspeccao": "Circunspecção",
    "Cobica": "Cobiça",
    "Codigo de Honra": "Código de Honra",
    "Compulsao": "Compulsão",
    "Convulsoes Pos-combate": "Convulsões Pós-combate",
    "Corcunda": "Corcunda",
    "Curiosidade": "Curiosidade",
    "Deficiencia Fisica": "Deficiência Física",
    "Deficiencias Menores": "Deficiências Menores",
    "Dependencia": "Dependência",
    "Depressao Cronica": "Depressão Crônica",
    "Disopia": "Disopia",
    "Distracao": "Distração",
    "Distraido": "Distraído",
    "Disturbio Neurologico": "Distúrbio Neurológico",
    "Dividas": "Dívidas",
    "Doenca Contagiosa": "Doença Contagiosa",
    "Dor Cronica": "Dor Crônica",
    "Doutrinas Religiosas": "Doutrinas Religiosas",
    "Egoismo": "Egoísmo",
    "Eletrico": "Elétrico",
    "Enjoadico": "Enjoadiço",
    "Epilepsia": "Epilepsia",
    "Estomago Sensivel": "Estômago Sensível",
    "Excesso de Confianca": "Excesso de Confiança",
    "Facil de Decifrar": "Fácil de Decifrar",
    "Facil de Matar": "Fácil de Matar",
    "Feicoes Estranhas": "Feições Estranhas",
    "Fobias": "Fobias",
    "Furia": "Fúria",
    "Gregario": "Gregário",
    "Habitos Detestaveis": "Hábitos Detestáveis",
    "Habitos ou Expressoes": "Hábitos ou Expressões",
    "Identidade Secreta": "Identidade Secreta",
    "Indulgente": "Indulgente",
    "Inimigos": "Inimigos",
    "Insensivel": "Insensível",
    "Intolerancia": "Intolerância",
    "Intolerancia ao Alcool": "Intolerância ao Álcool",
    "Intolerancia-G": "Intolerância-G",
    "Lunatico": "Lunático",
    "Luxuria": "Luxúria",
    "Maldicao": "Maldição",
    "Maldicao Divina": "Maldição Divina",
    "Maneta (Um Braco)": "Maneta (Um Braço)",
    "Maneta (Uma Mao)": "Maneta (Uma Mão)",
    "Maniaco-depressivo": "Maníaco-depressivo",
    "Manuseadores Precarios": "Manuseadores Precários",
    "Manutencao": "Manutenção",
    "Mao Fraca": "Mão Fraca",
    "Megalomania": "Megalomania",
    "Mentalidade de Escravo": "Mentalidade de Escravo",
    "Mudanca de Personalidade": "Mudança de Personalidade",
    "Nao-iconografico": "Não-iconográfico",
    "Oblivio": "Oblívio",
    "Obsessao": "Obsessão",
    "Pacifismo": "Pacifismo",
    "Padrao de Tempo Reduzido": "Padrão de Tempo Reduzido",
    "Paralisia Frente ao Combate": "Paralisia Frente ao Combate",
    "Paranoia": "Paranoia",
    "Preferencias": "Preferências",
    "Preguica": "Preguiça",
    "Recuperacao Lenta": "Recuperação Lenta",
    "Refeicao Demorada": "Refeição Demorada",
    "Reprogramavel": "Reprogramável",
    "Repugnancia": "Repugnância",
    "Ressacas Terriveis": "Ressacas Terríveis",
    "Sanguinolencia": "Sanguinolência",
    "Sem Imaginacao": "Sem Imaginação",
    "Sem Nocao de Profundidade": "Sem Noção de Profundidade",
    "Simpatico": "Simpático",
    "Solitario": "Solitário",
    "Sono Complementar": "Sono Complementar",
    "Sonolento": "Sonolento",
    "Supersensitivo": "Supersensitivo",
    "Susceptibilidade a Magia": "Susceptibilidade à Magia",
    "Suscetivel": "Suscetível",
    "Temor": "Temor",
    "Tetraplegico": "Tetraplégico",
    "Timidez": "Timidez",
    "Unico": "Único",
    "Vicio": "Vício",
    "Visao Restrita": "Visão Restrita",
    "Vulnerabilidade": "Vulnerabilidade",
    "Xenofilia": "Xenofilia",
    "Zarolho": "Zarolho",
    # Rotulos de opcoes discretas (Pacifismo, Fobias, etc.)
    "Legitima Defesa": "Legítima Defesa",
    "Nao-Violencia Total": "Não-Violência Total",
    "Delirio serio": "Delírio sério",
    "Delirio grave": "Delírio grave",
    "Assassino Relutante": "Assassino Relutante",
    "Incapaz de Ferir Inocentes": "Incapaz de Ferir Inocentes",
    "Incapaz de Matar": "Incapaz de Matar",
    "Tunel": "Túnel",
    "Peculiaridade": "Peculiaridade",
    "Estrito": "Estrito",
    "Profissional": "Profissional",
    "Pessoal": "Pessoal",
    "Menor": "Menor",
    "Moderado": "Moderado",
    "Grande": "Grande",
    "Sutil": "Sutil",
    "Assinatura": "Assinatura",
    "Marca elaborada": "Marca elaborada",
    "Passiva": "Passiva",
    "Ativa": "Ativa",
    "Legal": "Legal",
    "Ilegal": "Ilegal",
    "Alcoolismo severo": "Alcoolismo severo",
    "Parcial": "Parcial",
    "Total": "Total",
    "Um olho": "Um olho",
    "Leve": "Leve",
    "Grave": "Grave",
    "6 meses a 2 anos": "6 meses a 2 anos",
    "1 semana a 6 meses": "1 semana a 6 meses",
    "menos de 1 semana": "menos de 1 semana",
    "Curto prazo": "Curto prazo",
    "Longo prazo": "Longo prazo",
    "Fantasia": "Fantasia",
}


def aplicar(item: dict[str, Any]) -> None:
    nome = item.get("nome", "")
    if nome in NOMES:
        item["nome"] = NOMES[nome]
    if "opcoes_custo" in item:
        for o in item["opcoes_custo"]:
            r = o.get("rotulo")
            if r and r in NOMES:
                o["rotulo"] = NOMES[r]


def main() -> None:
    d = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    for it in d.get("vantagens", []):
        aplicar(it)
    for it in d.get("desvantagens", []):
        aplicar(it)

    import unicodedata

    def sort_key(item: dict[str, Any]) -> str:
        s = item.get("nome") or ""
        s = unicodedata.normalize("NFD", s)
        return "".join(c for c in s if not unicodedata.combining(c)).lower()

    d["vantagens"].sort(key=sort_key)
    d["desvantagens"].sort(key=sort_key)

    JSON_PATH.write_text(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Reacentuado {JSON_PATH.name}: "
        f"{len(d['vantagens'])} vantagens, {len(d['desvantagens'])} desvantagens"
    )


if __name__ == "__main__":
    main()
