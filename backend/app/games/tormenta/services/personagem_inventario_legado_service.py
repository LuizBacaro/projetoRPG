"""Importa inventário ainda guardado em ficha_json para as tabelas SQL e remove as chaves legadas."""

from __future__ import annotations

from typing import Set

from sqlalchemy.orm import Session

from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.schemas.inventario_legado import TormentaInventarioLegadoImportResponse
from app.games.tormenta.services.personagem_consumiveis_service import TormentaPersonagemConsumiveisService
from app.games.tormenta.services.personagem_equipamentos_service import TormentaPersonagemEquipamentosService
from app.games.tormenta.services.personagem_talentos_service import TormentaPersonagemTalentosService
from app.repositories.base import commit_with_rollback
from app.shared.exceptions.custom_exceptions import ArenaBaseException

_CHAVES_INVENTARIO_JSON: Set[str] = {
    "talentos_mb_lista",
    "equipamentos",
    "consumiveis",
    "consumiveis_lista",
}


def sanear_ficha_json_inventario(fj: dict | None) -> dict:
    out = dict(fj or {})
    for k in _CHAVES_INVENTARIO_JSON:
        out.pop(k, None)
    return out


class TormentaPersonagemInventarioLegadoService:
    def __init__(self, db: Session):
        self.db = db

    def importar_legado(self, personagem_id: int) -> TormentaInventarioLegadoImportResponse:
        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)

        st = TormentaPersonagemTalentosService(self.db)
        se = TormentaPersonagemEquipamentosService(self.db)
        sc = TormentaPersonagemConsumiveisService(self.db)

        rt = st.migrar_talentos_mb_lista_do_json(personagem_id)
        re = se.migrar_equipamentos_do_json(personagem_id)
        rc = sc.migrar_consumiveis_do_json(personagem_id)

        p.ficha_json = sanear_ficha_json_inventario(p.ficha_json)
        commit_with_rollback(self.db)

        return TormentaInventarioLegadoImportResponse(
            talentos_criados=rt.vinculos_criados,
            talentos_duplicados=rt.ignorados_duplicados,
            equipamentos_criados=re.vinculos_criados,
            equipamentos_duplicados=re.ignorados_duplicados,
            consumiveis_criados=rc.vinculos_criados,
            consumiveis_duplicados=rc.ignorados_duplicados,
        )
