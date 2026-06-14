"""Regras de negócio — magias MB vinculadas ao personagem (grimório / conhecidas / preparadas)."""

from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.games.tormenta.models.magia_personagem import TormentaMagiaPersonagem
from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.rules.catalogo_t20 import (
    magia_mb_slug_no_catalogo,
    metadados_magia_mb_por_slug,
    papel_padrao_migracao_magias_mb,
    resolver_magia_mb_slug_por_texto,
)
from app.games.tormenta.rules.conjuracao_combate_t20 import (
    aplicar_concentracao_ao_lancar,
    ler_concentracao_mb,
    limpar_concentracao_mb,
    magia_mb_exige_concentracao,
)
from app.games.tormenta.rules.devocao_divindade_t20 import (
    divindade_mb_slug_de_ficha,
    magia_e_truque_devocao_mb,
)
from app.games.tormenta.rules.grimorio_conjuracao_t20 import (
    validar_papel_magia_para_classe,
)
from app.games.tormenta.rules.grimorio_elegibilidade_t20 import (
    nivel_efetivo_conjuracao_mb,
    resumo_elegibilidade_grimorio_mb,
)
from app.games.tormenta.rules.magias_conhecidas_progressao_t20 import (
    bardo_pode_trocar_magia_mb,
    preview_magias_conhecidas_mb,
    validar_adicionar_conhecida_mb,
)
from app.games.tormenta.rules.magias_grimorio_aprendizado_t20 import (
    preview_grimorio_mb as preview_grimorio_mb_regra,
)
from app.games.tormenta.rules.magias_grimorio_aprendizado_t20 import (
    validar_adicionar_grimorio_mb,
)
from app.games.tormenta.rules.magias_preparadas_t20 import (
    preview_preparadas_mb as preview_preparadas_mb_regra,
)
from app.games.tormenta.rules.magias_preparadas_t20 import (
    validar_adicionar_preparada_mb,
    validar_lancar_magia_preparador_mb,
)
from app.games.tormenta.rules.magias_progressao_mb_t20 import (
    circulo_maximo_magias_lancaveis_mb,
    tipo_lista_magias_por_classe_mb,
)
from app.games.tormenta.rules.magias_repertorio_aprendido_t20 import (
    preview_repertorio_mb as preview_repertorio_mb_regra,
)
from app.games.tormenta.rules.magias_repertorio_aprendido_t20 import (
    validar_adicionar_repertorio_mb,
)
from app.games.tormenta.schemas.magia_personagem import (
    TormentaEncerrarConcentracaoResponse,
    TormentaMagiaPersonagemItem,
    TormentaMagiaTrocaRequest,
    TormentaMagiaTrocaResponse,
    TormentaMagiaVinculoCreate,
    TormentaMigrarMagiasJsonResponse,
)
from app.repositories.base import commit_with_rollback
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos

_PAPEIS = frozenset({"grimorio", "conhecida", "preparada"})


class TormentaPersonagemMagiasService:
    """Vínculos `tormenta_magias_personagem` + validação contra catálogo JSON MB."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_item(row: TormentaMagiaPersonagem) -> TormentaMagiaPersonagemItem:
        meta = metadados_magia_mb_por_slug(row.magia_slug)
        nome = str(meta["nome"]) if meta and meta.get("nome") else None
        circulo = (
            int(meta["circulo"]) if meta and meta.get("circulo") is not None else None
        )
        tipo = str(meta["tipo"]) if meta and meta.get("tipo") else None
        escola = str(meta["escola"]) if meta and meta.get("escola") else None
        return TormentaMagiaPersonagemItem(
            id=row.id,
            magia_slug=row.magia_slug,
            papel=row.papel,
            nome=nome,
            circulo=circulo,
            tipo=tipo,
            escola=escola,
            notas=row.notas,
            adicionado_em=row.adicionado_em,
        )

    def listar_por_personagem(
        self, personagem_id: int
    ) -> List[TormentaMagiaPersonagemItem]:
        rows = (
            self.db.query(TormentaMagiaPersonagem)
            .filter(TormentaMagiaPersonagem.personagem_id == personagem_id)
            .order_by(
                TormentaMagiaPersonagem.papel.asc(),
                TormentaMagiaPersonagem.adicionado_em.asc(),
            )
            .all()
        )
        return [self._to_item(r) for r in rows]

    def _vinculos_dict_por_personagem(self, personagem_id: int) -> List[Dict[str, Any]]:
        rows = (
            self.db.query(TormentaMagiaPersonagem)
            .filter(TormentaMagiaPersonagem.personagem_id == personagem_id)
            .all()
        )
        out: List[Dict[str, Any]] = []
        for r in rows:
            meta = metadados_magia_mb_por_slug(r.magia_slug) or {}
            circ = None
            try:
                circ = int(meta.get("circulo", 0) or 0)
            except (TypeError, ValueError):
                circ = 0
            out.append(
                {
                    "magia_slug": r.magia_slug,
                    "papel": r.papel,
                    "circulo": circ,
                }
            )
        return out

    def adicionar_vinculo(
        self, personagem_id: int, payload: TormentaMagiaVinculoCreate
    ) -> TormentaMagiaPersonagemItem:
        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)

        ok_g, motivo_g = resumo_elegibilidade_grimorio_mb(
            tipo=str(p.tipo or ""),
            nivel=int(p.nivel or 1),
            ficha_json=p.ficha_json if isinstance(p.ficha_json, dict) else {},
        )
        if not ok_g:
            raise DadosInvalidos(motivo_g)

        slug = str(payload.magia_slug or "").strip().lower()[:80]
        if len(slug) < 2:
            raise DadosInvalidos("magia_slug invalido")
        if not magia_mb_slug_no_catalogo(slug):
            raise DadosInvalidos(
                "Magia nao encontrada no catalogo MB (slug desconhecido)"
            )

        papel = str(payload.papel or "").strip().lower()
        if papel not in _PAPEIS:
            raise DadosInvalidos("papel deve ser grimorio, conhecida ou preparada")

        fj = p.ficha_json if isinstance(p.ficha_json, dict) else {}
        slug_classe = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
        manual = fj.get("tormenta_conjuracao_manual_mb") is True
        if slug_classe and not manual:
            from app.games.tormenta.rules.grimorio_conjuracao_t20 import (
                modo_conjuracao_classe_mb,
                validar_papel_magia_para_classe,
            )

            ok_p, motivo_p = validar_papel_magia_para_classe(
                slug_classe, papel, conjuracao_manual=manual
            )
            if not ok_p:
                raise DadosInvalidos(motivo_p)

        meta = metadados_magia_mb_por_slug(slug)
        circulo_mag = int(meta.get("circulo", 0) or 0) if meta else 0
        tipo_mag = str(meta.get("tipo") or "").strip().lower() if meta else ""
        nv_conj = nivel_efetivo_conjuracao_mb(fj, int(p.nivel or 1))
        existentes = self._vinculos_dict_por_personagem(personagem_id)
        if (
            slug_classe
            and not manual
            and papel == "conhecida"
            and modo_conjuracao_classe_mb(slug_classe) == "espontaneo"
        ):
            ok_c, motivo_c = validar_adicionar_conhecida_mb(
                slug_classe=slug_classe,
                nivel=nv_conj,
                circulo_magia=circulo_mag,
                vinculos_existentes=existentes,
            )
            if not ok_c:
                raise DadosInvalidos(motivo_c)
        if slug_classe and not manual and papel == "conhecida":
            from app.games.tormenta.rules.magias_repertorio_aprendido_t20 import (
                classe_usa_limite_repertorio_mb,
            )

            if classe_usa_limite_repertorio_mb(slug_classe):
                ok_rep, motivo_rep = validar_adicionar_repertorio_mb(
                    slug_classe=slug_classe,
                    nivel=nv_conj,
                    circulo_magia=circulo_mag,
                    tipo_magia=tipo_mag or None,
                    vinculos_existentes=existentes,
                    for_valor=int(p.for_valor or 10),
                    des_valor=int(p.des_valor or 10),
                    con_valor=int(p.con_valor or 10),
                    int_valor=int(p.int_valor or 10),
                    sab_valor=int(p.sab_valor or 10),
                    car_valor=int(p.car_valor or 10),
                )
                if not ok_rep:
                    raise DadosInvalidos(motivo_rep)
        if slug_classe and not manual and papel == "grimorio":
            ok_gm, motivo_gm = validar_adicionar_grimorio_mb(
                slug_classe=slug_classe,
                nivel=nv_conj,
                circulo_magia=circulo_mag,
                tipo_magia=tipo_mag or None,
                vinculos_existentes=existentes,
                for_valor=int(p.for_valor or 10),
                des_valor=int(p.des_valor or 10),
                con_valor=int(p.con_valor or 10),
                int_valor=int(p.int_valor or 10),
                sab_valor=int(p.sab_valor or 10),
                car_valor=int(p.car_valor or 10),
            )
            if not ok_gm:
                raise DadosInvalidos(motivo_gm)
        if slug_classe and not manual and papel == "preparada":
            ok_pr, motivo_pr = validar_adicionar_preparada_mb(
                slug_classe=slug_classe,
                nivel=nv_conj,
                magia_slug=slug,
                circulo_magia=circulo_mag,
                vinculos_existentes=existentes,
                for_valor=int(p.for_valor or 10),
                des_valor=int(p.des_valor or 10),
                con_valor=int(p.con_valor or 10),
                int_valor=int(p.int_valor or 10),
                sab_valor=int(p.sab_valor or 10),
                car_valor=int(p.car_valor or 10),
            )
            if not ok_pr:
                raise DadosInvalidos(motivo_pr)

        dup = (
            self.db.query(TormentaMagiaPersonagem)
            .filter(
                TormentaMagiaPersonagem.personagem_id == personagem_id,
                TormentaMagiaPersonagem.magia_slug == slug,
                TormentaMagiaPersonagem.papel == papel,
            )
            .first()
        )
        if dup:
            raise ArenaBaseException(
                "Esta magia ja esta vinculada ao personagem com o mesmo papel",
                status_code=409,
            )

        v = TormentaMagiaPersonagem(
            personagem_id=personagem_id,
            magia_slug=slug,
            papel=papel,
            notas=(payload.notas or "").strip() or None,
        )
        self.db.add(v)
        commit_with_rollback(self.db)
        self.db.refresh(v)
        return self._to_item(v)

    def remover_vinculo(self, personagem_id: int, vinculo_id: int) -> None:
        row = self.db.get(TormentaMagiaPersonagem, vinculo_id)
        if not row or row.personagem_id != personagem_id:
            raise ArenaBaseException("Vinculo nao encontrado", status_code=404)
        self.db.delete(row)
        commit_with_rollback(self.db)

    def lancar_magia_gastando_pm(
        self, personagem_id: int, magia_slug: str
    ) -> Dict[str, Any]:
        """Debita PM conforme círculo da magia MB; valida saldo."""
        from app.games.tormenta.rules.grimorio_conjuracao_t20 import simular_gasto_pm

        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)

        slug = str(magia_slug or "").strip().lower()[:80]
        if not magia_mb_slug_no_catalogo(slug):
            raise DadosInvalidos("Magia nao encontrada no catalogo MB")

        fj = p.ficha_json if isinstance(p.ficha_json, dict) else {}
        classe_slug = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
        manual = fj.get("tormenta_conjuracao_manual_mb") is True
        meta = metadados_magia_mb_por_slug(slug)
        circulo_mag = int(meta.get("circulo", 0) or 0) if meta else 0
        truque_devocao = False
        if classe_slug and not manual:
            vinculos = self._vinculos_dict_por_personagem(personagem_id)
            div_slug = divindade_mb_slug_de_ficha(fj, p.divindade)
            ok_l, motivo_l = validar_lancar_magia_preparador_mb(
                slug_classe=classe_slug,
                magia_slug=slug,
                circulo_magia=circulo_mag,
                vinculos=vinculos,
                divindade_slug=div_slug,
            )
            if not ok_l:
                raise DadosInvalidos(motivo_l)

        div_slug_lanc = divindade_mb_slug_de_ficha(fj, p.divindade)
        truque_devocao = (
            circulo_mag == 0
            and div_slug_lanc
            and magia_e_truque_devocao_mb(div_slug_lanc, slug)
        )

        sim = simular_gasto_pm(
            classe_slug=classe_slug or "mago",
            nivel=int(p.nivel or 1),
            for_valor=int(p.for_valor or 10),
            des_valor=int(p.des_valor or 10),
            con_valor=int(p.con_valor or 10),
            int_valor=int(p.int_valor or 10),
            sab_valor=int(p.sab_valor or 10),
            car_valor=int(p.car_valor or 10),
            pa_atual=int(p.pa_atual or 0),
            magia_slug=slug,
            custo_pm_override=0 if truque_devocao else None,
        )
        if not sim["permitido"]:
            raise DadosInvalidos(str(sim.get("motivo") or "PM insuficientes"))

        p.pa_atual = int(sim["pa_atual_depois"])
        fj_atual = p.ficha_json if isinstance(p.ficha_json, dict) else {}
        p.ficha_json = aplicar_concentracao_ao_lancar(
            fj_atual, magia_slug=slug, meta=meta
        )
        commit_with_rollback(self.db)
        self.db.refresh(p)
        conc = ler_concentracao_mb(p.ficha_json)
        return {
            "magia_slug": slug,
            "custo_pm": int(sim["custo_pm"]),
            "pa_atual_antes": int(sim["pa_atual_antes"]),
            "pa_atual_depois": int(sim["pa_atual_depois"]),
            "pa_max": sim.get("pa_max"),
            "permitido": True,
            "motivo": "",
            "truque_devocao": truque_devocao,
            "exige_concentracao": magia_mb_exige_concentracao(meta),
            "concentracao_ativa": conc.get("nome") if conc else None,
        }

    def migrar_magias_do_json(
        self, personagem_id: int
    ) -> TormentaMigrarMagiasJsonResponse:
        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        fj = p.ficha_json if isinstance(p.ficha_json, dict) else {}
        texto = str(fj.get("magias_texto") or "").strip()
        if not texto:
            return TormentaMigrarMagiasJsonResponse(
                vinculos_criados=0, ignorados_duplicados=0, nao_encontrados=[]
            )

        slug_classe = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
        manual = fj.get("tormenta_conjuracao_manual_mb") is True
        papel_padrao = (
            papel_padrao_migracao_magias_mb(slug_classe) if slug_classe else "conhecida"
        )
        tipo_pref = (
            tipo_lista_magias_por_classe_mb(slug_classe) if slug_classe else None
        )

        import re

        tokens = [t.strip() for t in re.split(r"[\n,;]+", texto) if t.strip()]
        criados = 0
        dup = 0
        nao_encontrados: List[str] = []
        vistos: set[tuple[str, str]] = set()

        for token in tokens:
            slug = resolver_magia_mb_slug_por_texto(token, tipo_preferido=tipo_pref)
            if not slug:
                nao_encontrados.append(token[:120])
                continue
            papel = papel_padrao
            if slug_classe and not manual:
                ok_p, _ = validar_papel_magia_para_classe(
                    slug_classe, papel, conjuracao_manual=False
                )
                if not ok_p:
                    papel = "conhecida" if papel == "grimorio" else "grimorio"
                    ok_p2, motivo2 = validar_papel_magia_para_classe(
                        slug_classe, papel, conjuracao_manual=False
                    )
                    if not ok_p2:
                        nao_encontrados.append(f"{token} ({motivo2})"[:120])
                        continue
            chave = (slug, papel)
            if chave in vistos:
                dup += 1
                continue
            exist = (
                self.db.query(TormentaMagiaPersonagem)
                .filter(
                    TormentaMagiaPersonagem.personagem_id == personagem_id,
                    TormentaMagiaPersonagem.magia_slug == slug,
                    TormentaMagiaPersonagem.papel == papel,
                )
                .first()
            )
            if exist:
                dup += 1
                vistos.add(chave)
                continue
            self.db.add(
                TormentaMagiaPersonagem(
                    personagem_id=personagem_id,
                    magia_slug=slug,
                    papel=papel,
                    notas="migrado de magias_texto",
                )
            )
            vistos.add(chave)
            criados += 1
            self.db.flush()

        if criados:
            commit_with_rollback(self.db)
        return TormentaMigrarMagiasJsonResponse(
            vinculos_criados=criados,
            ignorados_duplicados=dup,
            nao_encontrados=nao_encontrados[:50],
        )

    def encerrar_concentracao_mb(
        self, personagem_id: int
    ) -> TormentaEncerrarConcentracaoResponse:
        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        fj = p.ficha_json if isinstance(p.ficha_json, dict) else {}
        antes = ler_concentracao_mb(fj)
        if not antes:
            return TormentaEncerrarConcentracaoResponse(
                encerrada=False, concentracao_anterior=None
            )
        p.ficha_json = limpar_concentracao_mb(fj)
        commit_with_rollback(self.db)
        return TormentaEncerrarConcentracaoResponse(
            encerrada=True,
            concentracao_anterior=str(antes.get("nome") or ""),
        )

    def preview_conhecidas_mb(self, personagem_id: int) -> Dict[str, Any]:
        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        fj = p.ficha_json if isinstance(p.ficha_json, dict) else {}
        slug_classe = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
        nv = nivel_efetivo_conjuracao_mb(fj, int(p.nivel or 1))
        vinculos = [
            {
                "magia_slug": r.magia_slug,
                "papel": r.papel,
            }
            for r in self.db.query(TormentaMagiaPersonagem)
            .filter(TormentaMagiaPersonagem.personagem_id == personagem_id)
            .all()
        ]
        return preview_magias_conhecidas_mb(
            slug_classe=slug_classe,
            nivel=nv,
            vinculos=vinculos,
        )

    def preview_grimorio_mb(self, personagem_id: int) -> Dict[str, Any]:
        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        fj = p.ficha_json if isinstance(p.ficha_json, dict) else {}
        slug_classe = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
        nv = nivel_efetivo_conjuracao_mb(fj, int(p.nivel or 1))
        vinculos = self._vinculos_dict_por_personagem(personagem_id)
        return preview_grimorio_mb_regra(
            slug_classe=slug_classe,
            nivel=nv,
            vinculos=vinculos,
            for_valor=int(p.for_valor or 10),
            des_valor=int(p.des_valor or 10),
            con_valor=int(p.con_valor or 10),
            int_valor=int(p.int_valor or 10),
            sab_valor=int(p.sab_valor or 10),
            car_valor=int(p.car_valor or 10),
        )

    def preview_repertorio_mb(self, personagem_id: int) -> Dict[str, Any]:
        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        fj = p.ficha_json if isinstance(p.ficha_json, dict) else {}
        slug_classe = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
        nv = nivel_efetivo_conjuracao_mb(fj, int(p.nivel or 1))
        vinculos = self._vinculos_dict_por_personagem(personagem_id)
        return preview_repertorio_mb_regra(
            slug_classe=slug_classe,
            nivel=nv,
            vinculos=vinculos,
            for_valor=int(p.for_valor or 10),
            des_valor=int(p.des_valor or 10),
            con_valor=int(p.con_valor or 10),
            int_valor=int(p.int_valor or 10),
            sab_valor=int(p.sab_valor or 10),
            car_valor=int(p.car_valor or 10),
        )

    def preview_preparadas_mb(self, personagem_id: int) -> Dict[str, Any]:
        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        fj = p.ficha_json if isinstance(p.ficha_json, dict) else {}
        slug_classe = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
        nv = nivel_efetivo_conjuracao_mb(fj, int(p.nivel or 1))
        vinculos = self._vinculos_dict_por_personagem(personagem_id)
        return preview_preparadas_mb_regra(
            slug_classe=slug_classe,
            nivel=nv,
            vinculos=vinculos,
            for_valor=int(p.for_valor or 10),
            des_valor=int(p.des_valor or 10),
            con_valor=int(p.con_valor or 10),
            int_valor=int(p.int_valor or 10),
            sab_valor=int(p.sab_valor or 10),
            car_valor=int(p.car_valor or 10),
        )

    def limpar_preparadas(self, personagem_id: int) -> int:
        rows = (
            self.db.query(TormentaMagiaPersonagem)
            .filter(
                TormentaMagiaPersonagem.personagem_id == personagem_id,
                TormentaMagiaPersonagem.papel == "preparada",
            )
            .all()
        )
        n = len(rows)
        for row in rows:
            self.db.delete(row)
        if n:
            commit_with_rollback(self.db)
        return n

    def trocar_magia_conhecida_bardo(
        self, personagem_id: int, payload: TormentaMagiaTrocaRequest
    ) -> TormentaMagiaTrocaResponse:
        """Bardo MB: troca uma magia conhecida por outra (níveis 5, 8, 11, 14, 17, 20)."""
        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)

        fj = p.ficha_json if isinstance(p.ficha_json, dict) else {}
        if fj.get("tormenta_conjuracao_manual_mb") is True:
            raise DadosInvalidos(
                "Troca de magia conhecida MB nao se aplica com conjuracao manual ativa."
            )
        slug_classe = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
        if slug_classe != "bardo":
            raise DadosInvalidos(
                "Troca de magia conhecida MB disponivel apenas para bardo."
            )

        nv = nivel_efetivo_conjuracao_mb(fj, int(p.nivel or 1))
        if not bardo_pode_trocar_magia_mb(nv):
            raise DadosInvalidos(
                "Bardo so pode trocar magia conhecida nos niveis 5, 8, 11, 14, 17 e 20 (MB)."
            )

        slug_rem = str(payload.magia_slug_removida or "").strip().lower()[:80]
        slug_nov = str(payload.magia_slug_nova or "").strip().lower()[:80]
        if not slug_rem or not slug_nov:
            raise DadosInvalidos(
                "magia_slug_removida e magia_slug_nova sao obrigatorios"
            )
        if slug_rem == slug_nov:
            raise DadosInvalidos("A magia nova deve ser diferente da removida")
        if not magia_mb_slug_no_catalogo(slug_rem) or not magia_mb_slug_no_catalogo(
            slug_nov
        ):
            raise DadosInvalidos("Magia nao encontrada no catalogo MB")

        row_rem = (
            self.db.query(TormentaMagiaPersonagem)
            .filter(
                TormentaMagiaPersonagem.personagem_id == personagem_id,
                TormentaMagiaPersonagem.magia_slug == slug_rem,
                TormentaMagiaPersonagem.papel == "conhecida",
            )
            .first()
        )
        if not row_rem:
            raise ArenaBaseException(
                "Magia removida nao encontrada como conhecida", status_code=404
            )

        dup = (
            self.db.query(TormentaMagiaPersonagem)
            .filter(
                TormentaMagiaPersonagem.personagem_id == personagem_id,
                TormentaMagiaPersonagem.magia_slug == slug_nov,
                TormentaMagiaPersonagem.papel == "conhecida",
            )
            .first()
        )
        if dup:
            raise ArenaBaseException(
                "A magia nova ja esta na lista de conhecidas", status_code=409
            )

        meta_rem = metadados_magia_mb_por_slug(slug_rem) or {}
        meta_nov = metadados_magia_mb_por_slug(slug_nov) or {}
        circ_rem = int(meta_rem.get("circulo", 0) or 0)
        circ_nov = int(meta_nov.get("circulo", 0) or 0)
        cmax = circulo_maximo_magias_lancaveis_mb(slug_classe, nv)
        limite_troca = max(0, cmax - 1)
        if circ_nov > circ_rem:
            raise DadosInvalidos(
                f"A magia nova ({circ_nov}º) nao pode ser de circulo maior que a removida ({circ_rem}º)."
            )
        if circ_nov > limite_troca:
            raise DadosInvalidos(
                f"A magia nova deve ser de circulo <= {limite_troca} "
                f"(um abaixo do maximo conjuravel no nivel {nv})."
            )

        row_rem.magia_slug = slug_nov
        row_rem.notas = (payload.notas or row_rem.notas or "").strip() or row_rem.notas
        commit_with_rollback(self.db)
        self.db.refresh(row_rem)
        item = self._to_item(row_rem)
        return TormentaMagiaTrocaResponse(
            removida_slug=slug_rem,
            nova_slug=slug_nov,
            vinculo=item,
        )
