/**
 * Dnd5eArenaMagiasHelper — classificação de classe conjuradora e
 * agrupamento de magias por nível para a arena 5e (padrão visual 3.5).
 *
 * SRP: regras puras (sem fetch, sem DOM). Reaproveita o estado
 * `Dnd5eConjuracaoEstadoResponse` + listagem do grimório e devolve
 * estruturas prontas para a view.
 *
 * Paladino (preparado PHB: CAR + nível/2) e patrulheiro (conhecido, tabela
 * própria) — ver docs/dnd5e/issue-conjuracao-paladino-patrulheiro.md.
 * Preferir `estado.prepara_magias` do backend; slugs abaixo são fallback.
 */

const SLUGS_PREPARADORES = new Set(['mago', 'clerigo', 'druida', 'paladino']);
const SLUGS_CONHECIDOS = new Set([
    'bardo',
    'feiticeiro',
    'patrulheiro',
    'ranger',
]);
const SLUG_BRUXO = 'bruxo';

export const MODO_CONJURADOR = Object.freeze({
    PREPARADO: 'preparado',
    CONHECIDO: 'conhecido',
    BRUXO: 'bruxo',
    NENHUM: 'nenhum',
});

export class Dnd5eArenaMagiasHelper {
    static normalizarClasse(classe) {
        return String(classe || '').trim().toLowerCase();
    }

    /**
     * Decide o modo de UI a partir da classe e do estado de conjuração.
     * Quando o backend já devolve `prepara_magias`, ele prevalece.
     */
    static modo(classe, estado) {
        const slug = Dnd5eArenaMagiasHelper.normalizarClasse(classe);
        if (!slug) return MODO_CONJURADOR.NENHUM;
        if (slug === SLUG_BRUXO) return MODO_CONJURADOR.BRUXO;
        if (estado && typeof estado.prepara_magias === 'boolean') {
            return estado.prepara_magias
                ? MODO_CONJURADOR.PREPARADO
                : MODO_CONJURADOR.CONHECIDO;
        }
        if (SLUGS_PREPARADORES.has(slug)) return MODO_CONJURADOR.PREPARADO;
        if (SLUGS_CONHECIDOS.has(slug)) return MODO_CONJURADOR.CONHECIDO;
        return MODO_CONJURADOR.NENHUM;
    }

    static ehConjurador(classe, estado) {
        return (
            Dnd5eArenaMagiasHelper.modo(classe, estado) !== MODO_CONJURADOR.NENHUM
        );
    }

    /**
     * Indexa os slots por nível para acesso O(1) na view.
     * Garante linhas para níveis 0–9 (5e). Truque (nível 0) tem total=0.
     */
    static normalizarSlots(estado) {
        const porNivel = new Map();
        const lista = Array.isArray(estado?.slots) ? estado.slots : [];
        for (const slot of lista) {
            const nivel = Number(slot?.nivel);
            if (!Number.isFinite(nivel)) continue;
            porNivel.set(nivel, {
                nivel,
                total: Math.max(0, Number(slot.total) || 0),
                usados: Math.max(0, Number(slot.usados) || 0),
                disponiveis: Math.max(0, Number(slot.disponiveis) || 0),
            });
        }
        const result = [];
        for (let n = 0; n <= 9; n += 1) {
            if (porNivel.has(n)) {
                result.push(porNivel.get(n));
            } else {
                result.push({ nivel: n, total: 0, usados: 0, disponiveis: 0 });
            }
        }
        return result;
    }

    /**
     * Para o modo Bruxo, devolve o único nível de slot relevante e o total
     * (todos os slots viram no mesmo nível conforme PHB 5e).
     */
    static slotBruxo(estado) {
        const slots = (estado?.slots || []).filter((s) => Number(s.total) > 0);
        if (!slots.length) return null;
        const ativo = slots.reduce(
            (acc, s) => (Number(s.nivel) > Number(acc.nivel) ? s : acc),
            slots[0]
        );
        return {
            nivel: Number(ativo.nivel) || 1,
            total: Number(ativo.total) || 0,
            usados: Number(ativo.usados) || 0,
            disponiveis: Math.max(
                0,
                (Number(ativo.total) || 0) - (Number(ativo.usados) || 0)
            ),
        };
    }

    /**
     * Agrupa magias do grimório por nível, marcando como "usada" aquelas
     * em `magias_lancadas_sessao` (rastreio leve em memória).
     *
     * No modo PREPARADO, filtra apenas as magias com id em
     * `magias_preparadas_ids` (truques sempre aparecem).
     */
    static agruparPorNivel(magias, estado, modo, lancadasSessao) {
        const preparadasIds = new Set(
            (estado?.magias_preparadas_ids || []).map((x) => Number(x))
        );
        const lancadas = new Set(
            (Array.isArray(lancadasSessao) ? lancadasSessao : []).map((x) => Number(x))
        );
        const grupos = {};

        for (const magia of magias || []) {
            const magiaId = Number(magia?.magia_id);
            if (!Number.isFinite(magiaId)) continue;
            const nivel = Number(magia.magia_nivel || 0);
            const truque = nivel === 0;

            if (modo === MODO_CONJURADOR.PREPARADO && !truque) {
                if (!preparadasIds.has(magiaId)) continue;
            }

            if (!grupos[nivel]) {
                grupos[nivel] = {
                    nivel,
                    magias: [],
                    total: 0,
                    usados: 0,
                    disponiveis: 0,
                };
            }
            grupos[nivel].magias.push({
                magia_id: magiaId,
                magia_nome: magia.magia_nome || `Magia #${magiaId}`,
                magia_escola: magia.magia_escola || '',
                magia_nivel: nivel,
                truque,
                lancada: lancadas.has(magiaId),
            });
        }

        const slotsPorNivel = Dnd5eArenaMagiasHelper.normalizarSlots(estado);
        for (const slot of slotsPorNivel) {
            const grupo = grupos[slot.nivel];
            if (!grupo) continue;
            grupo.total = slot.total;
            grupo.usados = slot.usados;
            grupo.disponiveis = slot.disponiveis;
        }

        return grupos;
    }
}
