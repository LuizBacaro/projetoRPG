"""HTTP — personagens Tormenta 20 (ficha Módulo Básico)."""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile
from pydantic import ValidationError

from app.core.dependencies import (
    get_file_service,
    get_tormenta_personagem_consumiveis_service,
    get_tormenta_personagem_equipamentos_service,
    get_tormenta_personagem_inventario_legado_service,
    get_tormenta_personagem_magias_service,
    get_tormenta_personagem_progressao_service,
    get_tormenta_personagem_service,
    get_tormenta_personagem_talentos_service,
)
from app.games.tormenta.schemas.consumivel_personagem import (
    TormentaConsumivelPersonagemItem,
    TormentaConsumivelVinculoCreate,
    TormentaConsumivelVinculoPatch,
    TormentaMigrarConsumiveisJsonResponse,
)
from app.games.tormenta.schemas.equipamento_personagem import (
    TormentaEquipamentoPersonagemItem,
    TormentaEquipamentoVinculoCreate,
    TormentaEquipamentoVinculoPatch,
    TormentaMigrarEquipJsonResponse,
)
from app.games.tormenta.schemas.inventario_legado import (
    TormentaInventarioLegadoImportResponse,
)
from app.games.tormenta.schemas.magia_personagem import (
    TormentaEncerrarConcentracaoResponse,
    TormentaMagiaLancarRequest,
    TormentaMagiaLancarResponse,
    TormentaMagiaPersonagemItem,
    TormentaMagiasConhecidasPreviewResponse,
    TormentaMagiasGrimorioPreviewResponse,
    TormentaMagiasLimparPreparadasResponse,
    TormentaMagiasPreparadasPreviewResponse,
    TormentaMagiasRepertorioPreviewResponse,
    TormentaMagiaTrocaRequest,
    TormentaMagiaTrocaResponse,
    TormentaMagiaVinculoCreate,
    TormentaMigrarMagiasJsonRequest,
    TormentaMigrarMagiasJsonResponse,
)
from app.games.tormenta.schemas.personagem import (
    TormentaPersonagemCreate,
    TormentaPersonagemResponse,
    TormentaPersonagemUpdate,
)
from app.games.tormenta.schemas.progressao import (
    TormentaSubirNivelAplicarRequest,
    TormentaSubirNivelAplicarResponse,
    TormentaSubirNivelPreviewResponse,
)
from app.games.tormenta.schemas.talento_personagem import (
    TormentaMigrarTalentosJsonResponse,
    TormentaTalentoPersonagemItem,
    TormentaTalentoVinculoCreate,
)
from app.games.tormenta.services.personagem_consumiveis_service import (
    TormentaPersonagemConsumiveisService,
)
from app.games.tormenta.services.personagem_equipamentos_service import (
    TormentaPersonagemEquipamentosService,
)
from app.games.tormenta.services.personagem_inventario_legado_service import (
    TormentaPersonagemInventarioLegadoService,
)
from app.games.tormenta.services.personagem_magias_service import (
    TormentaPersonagemMagiasService,
)
from app.games.tormenta.services.personagem_progressao_service import (
    TormentaPersonagemProgressaoService,
)
from app.games.tormenta.services.personagem_service import TormentaPersonagemService
from app.games.tormenta.services.personagem_talentos_service import (
    TormentaPersonagemTalentosService,
)
from app.services.file_service import FileService
from app.shared.core.deps import (
    get_usuario_atual,
    requer_dono_ou_admin_tormenta_personagem,
    requer_game_tormenta,
)
from app.shared.exceptions.custom_exceptions import (
    ArenaBaseException,
    DadosInvalidos,
    InvalidFileError,
)
from app.shared.models.usuario import Usuario

router = APIRouter(
    prefix="/tormenta/personagens",
    tags=["Tormenta — Personagens"],
    dependencies=[Depends(requer_game_tormenta)],
)


@router.get("", response_model=List[TormentaPersonagemResponse])
def listar(
    tipo: Optional[str] = None,
    meus: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    response: Response = None,
    service: TormentaPersonagemService = Depends(get_tormenta_personagem_service),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    total = service.contar_todos(tipo, usuario=usuario_atual, apenas_meus=meus)
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Skip"] = str(skip)
        response.headers["X-Limit"] = str(limit)
    return service.listar_todos(
        tipo,
        usuario=usuario_atual,
        skip=skip,
        limit=limit,
        apenas_meus=meus,
    )


@router.get("/{personagem_id}", response_model=TormentaPersonagemResponse)
def obter(
    personagem_id: int,
    service: TormentaPersonagemService = Depends(get_tormenta_personagem_service),
    talentos_svc: TormentaPersonagemTalentosService = Depends(
        get_tormenta_personagem_talentos_service
    ),
    equip_svc: TormentaPersonagemEquipamentosService = Depends(
        get_tormenta_personagem_equipamentos_service
    ),
    consum_svc: TormentaPersonagemConsumiveisService = Depends(
        get_tormenta_personagem_consumiveis_service
    ),
    magias_svc: TormentaPersonagemMagiasService = Depends(
        get_tormenta_personagem_magias_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        ent = service.obter_por_id_sincronizando_pm_mb(personagem_id)
        base = TormentaPersonagemResponse.model_validate(ent)
        itens_t = talentos_svc.listar_por_personagem(personagem_id)
        itens_e = equip_svc.listar_por_personagem(personagem_id)
        itens_c = consum_svc.listar_por_personagem(personagem_id)
        itens_m = magias_svc.listar_por_personagem(personagem_id)
        return base.model_copy(
            update={
                "talentos": itens_t,
                "equipamentos": itens_e,
                "consumiveis": itens_c,
                "magias": itens_m,
            }
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Dados da ficha inválidos para resposta da API: {e.errors()[:3]}",
        ) from e
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/{personagem_id}/talentos",
    response_model=List[TormentaTalentoPersonagemItem],
)
def listar_talentos_do_personagem(
    personagem_id: int,
    talentos_svc: TormentaPersonagemTalentosService = Depends(
        get_tormenta_personagem_talentos_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    return talentos_svc.listar_por_personagem(personagem_id)


@router.post(
    "/{personagem_id}/talentos",
    response_model=TormentaTalentoPersonagemItem,
    status_code=201,
)
def adicionar_talento_ao_personagem(
    personagem_id: int,
    payload: TormentaTalentoVinculoCreate,
    talentos_svc: TormentaPersonagemTalentosService = Depends(
        get_tormenta_personagem_talentos_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return talentos_svc.adicionar_vinculo(personagem_id, payload)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=e.message)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/{personagem_id}/talentos/migrar-do-json",
    response_model=TormentaMigrarTalentosJsonResponse,
)
def migrar_talentos_mb_lista_do_json(
    personagem_id: int,
    talentos_svc: TormentaPersonagemTalentosService = Depends(
        get_tormenta_personagem_talentos_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return talentos_svc.migrar_talentos_mb_lista_do_json(personagem_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{personagem_id}/talentos/{vinculo_id}", status_code=204)
def remover_talento_do_personagem(
    personagem_id: int,
    vinculo_id: int,
    talentos_svc: TormentaPersonagemTalentosService = Depends(
        get_tormenta_personagem_talentos_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        talentos_svc.remover_vinculo(personagem_id, vinculo_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/{personagem_id}/magias",
    response_model=List[TormentaMagiaPersonagemItem],
)
def listar_magias_do_personagem(
    personagem_id: int,
    magias_svc: TormentaPersonagemMagiasService = Depends(
        get_tormenta_personagem_magias_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    return magias_svc.listar_por_personagem(personagem_id)


@router.post(
    "/{personagem_id}/magias",
    response_model=TormentaMagiaPersonagemItem,
    status_code=201,
)
def adicionar_magia_ao_personagem(
    personagem_id: int,
    payload: TormentaMagiaVinculoCreate,
    magias_svc: TormentaPersonagemMagiasService = Depends(
        get_tormenta_personagem_magias_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return magias_svc.adicionar_vinculo(personagem_id, payload)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=e.message)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{personagem_id}/magias/{vinculo_id}", status_code=204)
def remover_magia_do_personagem(
    personagem_id: int,
    vinculo_id: int,
    magias_svc: TormentaPersonagemMagiasService = Depends(
        get_tormenta_personagem_magias_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        magias_svc.remover_vinculo(personagem_id, vinculo_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/{personagem_id}/magias/lancar",
    response_model=TormentaMagiaLancarResponse,
)
def lancar_magia_gastando_pm(
    personagem_id: int,
    payload: TormentaMagiaLancarRequest,
    magias_svc: TormentaPersonagemMagiasService = Depends(
        get_tormenta_personagem_magias_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        data = magias_svc.lancar_magia_gastando_pm(personagem_id, payload.magia_slug)
        return TormentaMagiaLancarResponse(**data)
    except ValidationError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Resposta de lançamento inválida: {e.errors()[:3]}",
        ) from e
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=e.message)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/{personagem_id}/magias/migrar-do-json",
    response_model=TormentaMigrarMagiasJsonResponse,
)
def migrar_magias_do_json(
    personagem_id: int,
    body: TormentaMigrarMagiasJsonRequest = TormentaMigrarMagiasJsonRequest(),
    magias_svc: TormentaPersonagemMagiasService = Depends(
        get_tormenta_personagem_magias_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return magias_svc.migrar_magias_do_json(
            personagem_id, magias_texto_override=body.magias_texto
        )
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/{personagem_id}/magias/encerrar-concentracao",
    response_model=TormentaEncerrarConcentracaoResponse,
)
def encerrar_concentracao_magia_mb(
    personagem_id: int,
    magias_svc: TormentaPersonagemMagiasService = Depends(
        get_tormenta_personagem_magias_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return magias_svc.encerrar_concentracao_mb(personagem_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/{personagem_id}/magias/conhecidas-preview",
    response_model=TormentaMagiasConhecidasPreviewResponse,
)
def preview_magias_conhecidas_personagem(
    personagem_id: int,
    magias_svc: TormentaPersonagemMagiasService = Depends(
        get_tormenta_personagem_magias_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        data = magias_svc.preview_conhecidas_mb(personagem_id)
        return TormentaMagiasConhecidasPreviewResponse(**data)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/{personagem_id}/magias/trocar",
    response_model=TormentaMagiaTrocaResponse,
)
def trocar_magia_conhecida_bardo(
    personagem_id: int,
    payload: TormentaMagiaTrocaRequest,
    magias_svc: TormentaPersonagemMagiasService = Depends(
        get_tormenta_personagem_magias_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return magias_svc.trocar_magia_conhecida_bardo(personagem_id, payload)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=e.message)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/{personagem_id}/magias/grimorio-preview",
    response_model=TormentaMagiasGrimorioPreviewResponse,
)
def preview_grimorio_personagem(
    personagem_id: int,
    magias_svc: TormentaPersonagemMagiasService = Depends(
        get_tormenta_personagem_magias_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        data = magias_svc.preview_grimorio_mb(personagem_id)
        return TormentaMagiasGrimorioPreviewResponse(**data)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/{personagem_id}/magias/repertorio-preview",
    response_model=TormentaMagiasRepertorioPreviewResponse,
)
def preview_repertorio_personagem(
    personagem_id: int,
    magias_svc: TormentaPersonagemMagiasService = Depends(
        get_tormenta_personagem_magias_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        data = magias_svc.preview_repertorio_mb(personagem_id)
        return TormentaMagiasRepertorioPreviewResponse(**data)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/{personagem_id}/magias/preparadas-preview",
    response_model=TormentaMagiasPreparadasPreviewResponse,
)
def preview_preparadas_personagem(
    personagem_id: int,
    magias_svc: TormentaPersonagemMagiasService = Depends(
        get_tormenta_personagem_magias_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        data = magias_svc.preview_preparadas_mb(personagem_id)
        return TormentaMagiasPreparadasPreviewResponse(**data)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/{personagem_id}/magias/limpar-preparadas",
    response_model=TormentaMagiasLimparPreparadasResponse,
)
def limpar_magias_preparadas_personagem(
    personagem_id: int,
    magias_svc: TormentaPersonagemMagiasService = Depends(
        get_tormenta_personagem_magias_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        n = magias_svc.limpar_preparadas(personagem_id)
        return TormentaMagiasLimparPreparadasResponse(removidas=n)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/{personagem_id}/subir-nivel-preview",
    response_model=TormentaSubirNivelPreviewResponse,
)
def preview_subir_nivel_personagem(
    personagem_id: int,
    nivel_alvo: int = Query(
        ..., ge=1, le=40, description="Próximo nível (deve ser atual + 1)."
    ),
    prog_svc: TormentaPersonagemProgressaoService = Depends(
        get_tormenta_personagem_progressao_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return prog_svc.preview_subir_nivel(personagem_id, nivel_alvo)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=e.message)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/{personagem_id}/subir-nivel",
    response_model=TormentaSubirNivelAplicarResponse,
)
def aplicar_subir_nivel_personagem(
    personagem_id: int,
    payload: TormentaSubirNivelAplicarRequest,
    prog_svc: TormentaPersonagemProgressaoService = Depends(
        get_tormenta_personagem_progressao_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return prog_svc.aplicar_subir_nivel(personagem_id, payload)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=e.message)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/{personagem_id}/inventario/importar-legado",
    response_model=TormentaInventarioLegadoImportResponse,
)
def importar_inventario_legado_do_json(
    personagem_id: int,
    legado_svc: TormentaPersonagemInventarioLegadoService = Depends(
        get_tormenta_personagem_inventario_legado_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return legado_svc.importar_legado(personagem_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/{personagem_id}/equipamentos",
    response_model=List[TormentaEquipamentoPersonagemItem],
)
def listar_equipamentos_do_personagem(
    personagem_id: int,
    equip_svc: TormentaPersonagemEquipamentosService = Depends(
        get_tormenta_personagem_equipamentos_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    return equip_svc.listar_por_personagem(personagem_id)


@router.post(
    "/{personagem_id}/equipamentos",
    response_model=TormentaEquipamentoPersonagemItem,
    status_code=201,
)
def adicionar_equipamento_ao_personagem(
    personagem_id: int,
    payload: TormentaEquipamentoVinculoCreate,
    equip_svc: TormentaPersonagemEquipamentosService = Depends(
        get_tormenta_personagem_equipamentos_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return equip_svc.adicionar_vinculo(personagem_id, payload)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=e.message)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch(
    "/{personagem_id}/equipamentos/{vinculo_id}",
    response_model=TormentaEquipamentoPersonagemItem,
)
def atualizar_quantidade_equipamento(
    personagem_id: int,
    vinculo_id: int,
    payload: TormentaEquipamentoVinculoPatch,
    equip_svc: TormentaPersonagemEquipamentosService = Depends(
        get_tormenta_personagem_equipamentos_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return equip_svc.atualizar_quantidade(personagem_id, vinculo_id, payload)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/{personagem_id}/equipamentos/migrar-do-json",
    response_model=TormentaMigrarEquipJsonResponse,
)
def migrar_equipamentos_do_json(
    personagem_id: int,
    equip_svc: TormentaPersonagemEquipamentosService = Depends(
        get_tormenta_personagem_equipamentos_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return equip_svc.migrar_equipamentos_do_json(personagem_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{personagem_id}/equipamentos/{vinculo_id}", status_code=204)
def remover_equipamento_do_personagem(
    personagem_id: int,
    vinculo_id: int,
    equip_svc: TormentaPersonagemEquipamentosService = Depends(
        get_tormenta_personagem_equipamentos_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        equip_svc.remover_vinculo(personagem_id, vinculo_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/{personagem_id}/consumiveis",
    response_model=List[TormentaConsumivelPersonagemItem],
)
def listar_consumiveis_do_personagem(
    personagem_id: int,
    consum_svc: TormentaPersonagemConsumiveisService = Depends(
        get_tormenta_personagem_consumiveis_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    return consum_svc.listar_por_personagem(personagem_id)


@router.post(
    "/{personagem_id}/consumiveis",
    response_model=TormentaConsumivelPersonagemItem,
    status_code=201,
)
def adicionar_consumivel_ao_personagem(
    personagem_id: int,
    payload: TormentaConsumivelVinculoCreate,
    consum_svc: TormentaPersonagemConsumiveisService = Depends(
        get_tormenta_personagem_consumiveis_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return consum_svc.adicionar_vinculo(personagem_id, payload)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=e.message)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch(
    "/{personagem_id}/consumiveis/{vinculo_id}",
    response_model=TormentaConsumivelPersonagemItem,
)
def atualizar_quantidade_consumivel(
    personagem_id: int,
    vinculo_id: int,
    payload: TormentaConsumivelVinculoPatch,
    consum_svc: TormentaPersonagemConsumiveisService = Depends(
        get_tormenta_personagem_consumiveis_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return consum_svc.atualizar_quantidade(personagem_id, vinculo_id, payload)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/{personagem_id}/consumiveis/migrar-do-json",
    response_model=TormentaMigrarConsumiveisJsonResponse,
)
def migrar_consumiveis_do_json(
    personagem_id: int,
    consum_svc: TormentaPersonagemConsumiveisService = Depends(
        get_tormenta_personagem_consumiveis_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return consum_svc.migrar_consumiveis_do_json(personagem_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{personagem_id}/consumiveis/{vinculo_id}", status_code=204)
def remover_consumivel_do_personagem(
    personagem_id: int,
    vinculo_id: int,
    consum_svc: TormentaPersonagemConsumiveisService = Depends(
        get_tormenta_personagem_consumiveis_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        consum_svc.remover_vinculo(personagem_id, vinculo_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("", response_model=TormentaPersonagemResponse, status_code=201)
def criar(
    payload: TormentaPersonagemCreate,
    service: TormentaPersonagemService = Depends(get_tormenta_personagem_service),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    try:
        return service.criar(usuario_atual, payload)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=e.message)
    except ArenaBaseException as e:
        code = getattr(e, "status_code", 400)
        raise HTTPException(status_code=code, detail=getattr(e, "message", str(e)))


@router.patch("/{personagem_id}", response_model=TormentaPersonagemResponse)
def atualizar(
    personagem_id: int,
    payload: TormentaPersonagemUpdate,
    service: TormentaPersonagemService = Depends(get_tormenta_personagem_service),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return service.atualizar(personagem_id, payload)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=e.message)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{personagem_id}/foto", response_model=TormentaPersonagemResponse)
def upload_foto(
    personagem_id: int,
    foto: UploadFile = File(...),
    service: TormentaPersonagemService = Depends(get_tormenta_personagem_service),
    file_service: FileService = Depends(get_file_service),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    """Envia retrato (mesmo fluxo de arquivo que GURPS / combatentes D&D 3.5)."""
    if not foto.filename:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado")
    try:
        ent = service.obter_por_id(personagem_id)
        if ent.foto_url:
            file_service.deletar_arquivo(ent.foto_url)
        url = file_service.salvar_arquivo(foto)
        return service.atualizar(personagem_id, TormentaPersonagemUpdate(foto_url=url))
    except InvalidFileError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.delete("/{personagem_id}", status_code=204)
def excluir(
    personagem_id: int,
    service: TormentaPersonagemService = Depends(get_tormenta_personagem_service),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        service.excluir(personagem_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
