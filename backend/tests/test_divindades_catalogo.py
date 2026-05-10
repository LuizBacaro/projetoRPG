"""Testes unitarios dos helpers do catalogo de divindades (Tabela 3-7)."""

from app.games.dnd35.catalogs import divindades_catalogo as cat

# ---------------------------------------------------------------------------
# parse_alinhamento / alinhamento_compativel
# ---------------------------------------------------------------------------


def test_parse_alinhamento_reconhece_variantes_mal_e_mau():
    assert cat.parse_alinhamento("Leal e Bom") == (1, 1)
    assert cat.parse_alinhamento("Caotico e Mau") == (-1, -1)
    assert cat.parse_alinhamento("Caótico e Mal") == (-1, -1)  # aceita "Mal" e acento
    assert cat.parse_alinhamento("Neutro") == (0, 0)
    assert cat.parse_alinhamento("Leal e Neutro") == (1, 0)
    assert cat.parse_alinhamento("Neutro e Bom") == (0, 1)


def test_parse_alinhamento_valor_vazio_ou_invalido_retorna_none():
    assert cat.parse_alinhamento("") is None
    assert cat.parse_alinhamento(None) is None  # type: ignore[arg-type]
    assert cat.parse_alinhamento("xyz") is None


def test_alinhamento_compativel_regra_um_passo():
    # Heironeous (LG) aceita LG, LN, NG e TN (até um passo em cada eixo).
    assert cat.alinhamento_compativel("Leal e Bom", "Leal e Bom") is True
    assert cat.alinhamento_compativel("Leal e Bom", "Leal e Neutro") is True
    assert cat.alinhamento_compativel("Leal e Bom", "Neutro e Bom") is True
    assert cat.alinhamento_compativel("Leal e Bom", "Neutro") is True

    # ...mas não aceita Caótico (2 passos na ordem) ou Mau (2 passos na moral).
    assert cat.alinhamento_compativel("Leal e Bom", "Caotico e Bom") is False
    assert cat.alinhamento_compativel("Leal e Bom", "Leal e Mau") is False
    assert cat.alinhamento_compativel("Leal e Bom", "Caotico e Mau") is False


def test_alinhamento_compativel_valores_indefinidos_nao_bloqueiam():
    # Por decisão de UX: dado ausente não deve bloquear (retorna True).
    assert cat.alinhamento_compativel("", "Leal e Bom") is True
    assert cat.alinhamento_compativel("Leal e Bom", "") is True


# ---------------------------------------------------------------------------
# filtrar_por_alinhamento
# ---------------------------------------------------------------------------


def test_filtrar_por_alinhamento_respeita_um_passo():
    compat = cat.filtrar_por_alinhamento("Leal e Bom")
    nomes = {item["nome"] for item in compat}

    # Divindades LG, LN, NG, TN esperadas.
    assert "Heironeous" in nomes  # LG
    assert "Moradin" in nomes  # LG
    assert "Wee Jas" in nomes  # LN
    assert "Pelor" in nomes  # NG
    assert "Boccob" in nomes  # TN

    # Fora do um-passo não aparecem.
    assert "Gruumsh" not in nomes  # CE
    assert "Hextor" not in nomes  # LE
    assert "Olidammara" not in nomes  # CN
    assert "Corellon Larethian" not in nomes  # CG


def test_filtrar_por_alinhamento_vazio_retorna_catalogo_completo():
    resultado = cat.filtrar_por_alinhamento("")
    assert len(resultado) == len(cat.DIVINDADES)


# ---------------------------------------------------------------------------
# dominios_proibidos_por_alinhamento / validar_dominios_contra_alinhamento
# ---------------------------------------------------------------------------


def test_dominios_proibidos_por_alinhamento_leal_e_bom():
    proibidos = set(cat.dominios_proibidos_por_alinhamento("Leal e Bom"))
    # Clérigo LG não pode tomar Mal nem Caos.
    assert proibidos == {"mal", "caos"}


def test_dominios_proibidos_por_alinhamento_caotico_e_mau():
    proibidos = set(cat.dominios_proibidos_por_alinhamento("Caotico e Mau"))
    assert proibidos == {"bem", "ordem"}


def test_dominios_proibidos_por_alinhamento_neutro_nao_bloqueia():
    assert cat.dominios_proibidos_por_alinhamento("Neutro") == []


def test_validar_dominios_contra_alinhamento_detecta_conflitos():
    invalidos = cat.validar_dominios_contra_alinhamento(
        "Leal e Bom", ["Mal", "Ordem", "Bem"]
    )
    assert invalidos == ["Mal"]

    # Clérigo CE escolhendo Bem/Ordem conflita nos dois descritores.
    invalidos2 = cat.validar_dominios_contra_alinhamento(
        "Caotico e Mau", ["Bem", "Ordem", "Guerra"]
    )
    assert set(invalidos2) == {"Bem", "Ordem"}


def test_validar_dominios_contra_alinhamento_ignora_alinhamento_vazio():
    assert cat.validar_dominios_contra_alinhamento("", ["Mal", "Ordem"]) == []
