"""HTTP — regras de ficha D&D 5e (dados estáticos para o frontend)."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.games.dnd5e.rules.catalogo_regras import (
    listar_antecedentes_catalogo,
    listar_equipamento_catalogo,
    listar_magias_catalogo,
    listar_talentos_catalogo,
    metadados_combate,
    niveis_feat_ganho,
    payload_conjuracao_mb,
)
from app.games.dnd5e.rules.classes import (
    lista_classes_catalogo,
    niveis_com_ganho_feat,
    tabela_xp_por_nivel,
)
from app.games.dnd5e.rules.equipamento import montar_resumo_equipamento
from app.games.dnd5e.rules.ficha import montar_resumo_ficha
from app.games.dnd5e.rules.habilidades import (
    HABILIDADE_MAX,
    HABILIDADE_MIN,
    NIVEL_MAX,
    NIVEL_MIN,
    lista_metadados_habilidades,
    lista_tabela_bonus_proficiencia,
)
from app.games.dnd5e.rules.pericias import listar_pericias_catalogo
from app.games.dnd5e.rules.racas import lista_racas_catalogo
from app.games.dnd5e.rules.subclasses import listar_subclasses
from app.games.dnd5e.schemas.conjuracao import Dnd5eConjuracaoPerfilResponse
from app.games.dnd5e.schemas.progressao import (
    Dnd5eGerarAtributosRequest,
    Dnd5eGerarAtributosResponse,
)
from app.games.dnd5e.services.conjuracao_shared import perfil_conjuracao_classe
from app.games.dnd5e.schemas.regras import (
    Dnd5eAntecedenteCatalogoItem,
    Dnd5eBonusProficienciaItem,
    Dnd5eCalcularAtributosRequest,
    Dnd5eCalcularAtributosResponse,
    Dnd5eCalcularEquipamentoRequest,
    Dnd5eCalcularEquipamentoResponse,
    Dnd5eClasseItem,
    Dnd5eCondicaoItem,
    Dnd5eFeatCatalogoItem,
    Dnd5eHabilidadeMetaItem,
    Dnd5eMagiaCatalogoItem,
    Dnd5ePericiaCatalogoItem,
    Dnd5eRacaItem,
    Dnd5eRegrasAntecedentesResponse,
    Dnd5eRegrasAtributosResponse,
    Dnd5eRegrasClassesResponse,
    Dnd5eRegrasCombateResponse,
    Dnd5eRegrasEquipamentoResponse,
    Dnd5eRegrasMagiasResponse,
    Dnd5eRegrasPericiasResponse,
    Dnd5eRegrasRacasResponse,
    Dnd5eRegrasSubclassesResponse,
    Dnd5eRegrasTalentosResponse,
    Dnd5eSubclasseItem,
    Dnd5eXpNivelItem,
)
from app.core.dependencies import get_dnd5e_progressao_service
from app.games.dnd5e.services.progressao_service import Dnd5eProgressaoService
from app.shared.core.deps import get_usuario_atual, requer_game_dnd5e
from app.shared.models.usuario import Usuario

router = APIRouter(
    prefix="/dnd5e/regras",
    tags=["D&D 5e — Regras"],
    dependencies=[Depends(requer_game_dnd5e)],
)


@router.get(
    "/atributos",
    response_model=Dnd5eRegrasAtributosResponse,
    summary="Habilidades, limites e tabela de bônus de proficiência (PHB)",
)
def obter_regras_atributos(
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eRegrasAtributosResponse:
    habilidades = [
        Dnd5eHabilidadeMetaItem(**row) for row in lista_metadados_habilidades()
    ]
    tabela = [
        Dnd5eBonusProficienciaItem(**row) for row in lista_tabela_bonus_proficiencia()
    ]
    return Dnd5eRegrasAtributosResponse(
        habilidade_min=HABILIDADE_MIN,
        habilidade_max=HABILIDADE_MAX,
        nivel_min=NIVEL_MIN,
        nivel_max=NIVEL_MAX,
        habilidades=habilidades,
        bonus_proficiencia_por_nivel=tabela,
    )


@router.get(
    "/racas",
    response_model=Dnd5eRegrasRacasResponse,
    summary="Nove raças jogáveis PHB (bônus, velocidade, traços)",
)
def obter_regras_racas(
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eRegrasRacasResponse:
    racas = [Dnd5eRacaItem(**row) for row in lista_racas_catalogo()]
    return Dnd5eRegrasRacasResponse(racas=racas)


@router.get(
    "/classes",
    response_model=Dnd5eRegrasClassesResponse,
    summary="Doze classes PHB, tabela de XP e níveis de ganho de feat",
)
def obter_regras_classes(
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eRegrasClassesResponse:
    classes = [Dnd5eClasseItem(**row) for row in lista_classes_catalogo()]
    xp = [Dnd5eXpNivelItem(**row) for row in tabela_xp_por_nivel()]
    return Dnd5eRegrasClassesResponse(
        classes=classes,
        xp_por_nivel=xp,
        niveis_ganho_feat=niveis_com_ganho_feat(),
    )


@router.get(
    "/combate",
    response_model=Dnd5eRegrasCombateResponse,
    summary="Fórmulas de iniciativa/ataque/dano, condições e tipos de dano",
)
def obter_regras_combate(
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eRegrasCombateResponse:
    meta = metadados_combate()
    condicoes = [Dnd5eCondicaoItem(**c) for c in meta["condicoes"]]
    return Dnd5eRegrasCombateResponse(
        formula_iniciativa=meta["formula_iniciativa"],
        formula_ataque=meta["formula_ataque"],
        formula_dano=meta["formula_dano"],
        critico_em=meta["critico_em"],
        rodada_segundos=meta["rodada_segundos"],
        condicoes=condicoes,
        tipos_dano=meta["tipos_dano"],
        acoes_turno=meta["acoes_turno"],
        salvamentos_morte=meta["salvamentos_morte"],
    )


@router.get(
    "/conjuracao-perfil",
    response_model=Dnd5eConjuracaoPerfilResponse,
    summary="Perfil de conjuração por classe e nível (slots, modo de lista, teto)",
)
def obter_conjuracao_perfil(
    classe: str = Query(..., min_length=2, max_length=40),
    nivel: int = Query(..., ge=1, le=20),
    mod_habilidade: int = Query(0, ge=-5, le=20),
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eConjuracaoPerfilResponse:
    perfil = perfil_conjuracao_classe(classe, nivel, mod_habilidade=mod_habilidade)
    return Dnd5eConjuracaoPerfilResponse(**perfil)


@router.get(
    "/magias",
    response_model=Dnd5eRegrasMagiasResponse,
    summary="Catálogo resumido de magias e metadados de conjuração",
)
def obter_regras_magias(
    response: Response,
    nivel: Optional[int] = Query(None, ge=0, le=9),
    escola: Optional[str] = Query(None, max_length=40),
    q: Optional[str] = Query(None, max_length=80),
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eRegrasMagiasResponse:
    rows = listar_magias_catalogo(nivel=nivel, escola=escola, q=q)
    magias = [Dnd5eMagiaCatalogoItem(**row) for row in rows]
    if response is not None:
        response.headers["X-Total-Count"] = str(len(magias))
    return Dnd5eRegrasMagiasResponse(
        magias=magias,
        conjuracao=payload_conjuracao_mb(),
        total=len(magias),
    )


@router.get(
    "/talentos",
    response_model=Dnd5eRegrasTalentosResponse,
    summary="Catálogo de feats (talentos) e níveis de ganho",
)
def obter_regras_talentos(
    response: Response,
    tipo_bonus: Optional[str] = Query(None, max_length=40),
    q: Optional[str] = Query(None, max_length=80),
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eRegrasTalentosResponse:
    rows = listar_talentos_catalogo(tipo_bonus=tipo_bonus, q=q)
    talentos = [Dnd5eFeatCatalogoItem(**row) for row in rows]
    if response is not None:
        response.headers["X-Total-Count"] = str(len(talentos))
    return Dnd5eRegrasTalentosResponse(
        talentos=talentos,
        niveis_ganho_feat=niveis_feat_ganho(),
        total=len(talentos),
    )


@router.get(
    "/equipamento",
    response_model=Dnd5eRegrasEquipamentoResponse,
    summary="Armas, armaduras e escudos (PHB resumido)",
)
def obter_regras_equipamento(
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eRegrasEquipamentoResponse:
    payload = listar_equipamento_catalogo()
    return Dnd5eRegrasEquipamentoResponse(**payload)


@router.get(
    "/antecedentes",
    response_model=Dnd5eRegrasAntecedentesResponse,
    summary="Antecedentes PHB (perícias, equipamento, ouro)",
)
def obter_regras_antecedentes(
    response: Response,
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eRegrasAntecedentesResponse:
    rows = listar_antecedentes_catalogo()
    antecedentes = [Dnd5eAntecedenteCatalogoItem(**row) for row in rows]
    if response is not None:
        response.headers["X-Total-Count"] = str(len(antecedentes))
    return Dnd5eRegrasAntecedentesResponse(
        antecedentes=antecedentes,
        total=len(antecedentes),
    )


@router.get(
    "/pericias",
    response_model=Dnd5eRegrasPericiasResponse,
    summary="Dezoito perícias PHB e habilidade associada",
)
def obter_regras_pericias(
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eRegrasPericiasResponse:
    pericias = [Dnd5ePericiaCatalogoItem(**row) for row in listar_pericias_catalogo()]
    return Dnd5eRegrasPericiasResponse(pericias=pericias)


@router.get(
    "/subclasses",
    response_model=Dnd5eRegrasSubclassesResponse,
    summary="Subclasses PHB (filtro opcional por classe)",
)
def obter_regras_subclasses(
    classe_slug: Optional[str] = Query(None, max_length=40),
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eRegrasSubclassesResponse:
    rows = listar_subclasses(classe_slug)
    return Dnd5eRegrasSubclassesResponse(
        subclasses=[Dnd5eSubclasseItem(**row) for row in rows]
    )


@router.post(
    "/gerar-atributos",
    response_model=Dnd5eGerarAtributosResponse,
    summary="Gera scores base (4d6, matriz PHB ou compra de pontos)",
)
def gerar_atributos(
    payload: Dnd5eGerarAtributosRequest,
    service: Dnd5eProgressaoService = Depends(get_dnd5e_progressao_service),
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eGerarAtributosResponse:
    return service.gerar_atributos(payload.metodo, seed=payload.seed)


@router.post(
    "/calcular-atributos",
    response_model=Dnd5eCalcularAtributosResponse,
    summary="Preview de ficha: atributos, perícias, antecedente, CA com armadura",
)
def calcular_atributos_ficha(
    payload: Dnd5eCalcularAtributosRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eCalcularAtributosResponse:
    try:
        ficha_progressao = None
        if payload.progressao or payload.feats:
            ficha_progressao = {
                "progressao": payload.progressao or {"hp_rolls": [], "marcos": []},
                "feats": payload.feats,
            }
        resumo = montar_resumo_ficha(
            raca_slug=payload.raca_slug,
            classe_slug=payload.classe_slug,
            scores_base=payload.scores_base,
            bonus_habilidade_extra=payload.bonus_habilidade_extra,
            bonus_atributo_feat=payload.bonus_atributo_feat,
            antecedente_slug=payload.antecedente_slug,
            nivel=payload.nivel,
            pericias_classe_escolhidas=payload.pericias_classe_escolhidas,
            pericia_racial_extra=payload.pericia_racial_extra,
            subclasse_slug=payload.subclasse_slug,
            armadura_slug=payload.armadura_slug,
            escudo_slug=payload.escudo_slug,
            ficha_progressao=ficha_progressao,
            feats=payload.feats,
            hp_roll_nivel_1=payload.hp_roll_nivel_1,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return Dnd5eCalcularAtributosResponse(**resumo)


@router.post(
    "/calcular-equipamento",
    response_model=Dnd5eCalcularEquipamentoResponse,
    summary="Resumo de CA, peso, encargo e inventário",
)
def calcular_equipamento_ficha(
    payload: Dnd5eCalcularEquipamentoRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eCalcularEquipamentoResponse:
    resumo = montar_resumo_equipamento(
        armadura_slug=payload.armadura_slug,
        escudo_slug=payload.escudo_slug,
        arma_principal_slug=payload.arma_principal_slug,
        armas_slugs=payload.armas_slugs,
        itens=[i.model_dump() for i in payload.itens],
        forca=payload.forca,
        dex_mod=payload.dex_mod,
        ouro_po=payload.ouro_po,
    )
    return Dnd5eCalcularEquipamentoResponse(**resumo)
