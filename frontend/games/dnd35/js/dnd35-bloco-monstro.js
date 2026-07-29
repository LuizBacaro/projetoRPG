/**
 * RF-M07 — bloco de estatísticas estilo Livro dos Monstros (cliente).
 * Entrada: detalhe do catálogo GET /dnd35/regras/bestiario/{slug}
 * ou objeto com os mesmos campos + ficha parcial.
 */
(function (global) {
    'use strict';

    function _s(v) {
        if (v == null || v === '') return '';
        return String(v).trim();
    }

    function _joinList(arr) {
        if (!Array.isArray(arr) || !arr.length) return '';
        return arr.map(_s).filter(Boolean).join(', ');
    }

    function _attrs(det) {
        const parts = [
            ['For', det.for_valor],
            ['Des', det.des_valor],
            ['Con', det.con_valor],
            ['Int', det.int_valor],
            ['Sab', det.sab_valor],
            ['Car', det.car_valor],
        ]
            .filter(([, v]) => v != null && v !== '')
            .map(([k, v]) => `${k} ${v}`);
        return parts.join(', ');
    }

    /**
     * @param {object} det — detalhe do catálogo ou ficha enriquecida
     * @returns {string} bloco texto multilinha
     */
    function gerarBlocoEstatisticas35(det) {
        if (!det || typeof det !== 'object') return '';
        const nome = _s(det.nome) || 'Criatura';
        const tam = _s(det.tamanho);
        const tipo = _s(det.tipo_criatura);
        const sub = _joinList(det.subtipos);
        const linhaTipo = [tam, tipo + (sub ? ` (${sub})` : '')].filter(Boolean).join(' ');
        const nd =
            _s(det.nd_rotulo) ||
            (det.nd != null && det.nd !== '' ? String(det.nd) : '');
        const caParts = [];
        if (det.ca != null) caParts.push(String(det.ca));
        if (det.toque != null) caParts.push(`toque ${det.toque}`);
        if (det.surpresa != null) caParts.push(`surpresa ${det.surpresa}`);

        const linhas = [nome];
        if (linhaTipo) linhas.push(linhaTipo);
        if (_s(det.dv)) linhas.push(`Dados de Vida: ${_s(det.dv)}${det.hp_maximo != null ? ` (${det.hp_maximo} PV)` : ''}`);
        if (det.iniciativa != null) linhas.push(`Iniciativa: ${det.iniciativa}`);
        if (_s(det.deslocamento)) linhas.push(`Deslocamento: ${_s(det.deslocamento)}`);
        if (caParts.length) linhas.push(`Classe de Armadura: ${caParts.join(', ')}`);
        if (_s(det.ataque_base) || _s(det.agarrar)) {
            linhas.push(
                `Ataque Base/Agarrar: ${_s(det.ataque_base) || '—'} / ${_s(det.agarrar) || '—'}`
            );
        }
        if (_s(det.ataque_total)) {
            linhas.push(`Ataque: ${_s(det.ataque_total)}`);
        } else if (Array.isArray(det.ataques) && det.ataques.length) {
            const atq = det.ataques
                .map((a) => {
                    const n = _s(a.nome) || 'Ataque';
                    const b = _s(a.bonus_ataque);
                    const d = _s(a.dano);
                    return `${n}${b ? ` ${b}` : ''}${d ? ` (${d})` : ''}`;
                })
                .join(' ou ');
            linhas.push(`Ataque: ${atq}`);
        }
        if (_s(det.espaco_alcance)) linhas.push(`Espaço/Alcance: ${_s(det.espaco_alcance)}`);
        const espAtq = _joinList(det.ataques_especiais);
        if (espAtq) linhas.push(`Ataques Especiais: ${espAtq}`);
        const qual = _joinList(det.qualidades_especiais);
        if (qual) linhas.push(`Qualidades Especiais: ${qual}`);
        if (det.fortitude != null || det.reflexos != null || det.vontade != null) {
            linhas.push(
                `Testes de Resistência: Fort ${det.fortitude ?? '—'}, Ref ${det.reflexos ?? '—'}, Von ${det.vontade ?? '—'}`
            );
        }
        const attrs = _attrs(det);
        if (attrs) linhas.push(`Habilidades: ${attrs}`);
        if (_s(det.pericias_resumo)) linhas.push(`Perícias: ${_s(det.pericias_resumo)}`);
        if (_s(det.talentos_resumo)) linhas.push(`Talentos: ${_s(det.talentos_resumo)}`);
        if (_s(det.ambiente)) linhas.push(`Ambiente: ${_s(det.ambiente)}`);
        if (_s(det.organizacao)) linhas.push(`Organização: ${_s(det.organizacao)}`);
        if (_s(det.tesouro)) linhas.push(`Tesouro: ${_s(det.tesouro)}`);
        if (_s(det.tendencia)) linhas.push(`Tendência: ${_s(det.tendencia)}`);
        if (nd) linhas.push(`Nível de Desafio: ${nd}`);
        if (_s(det.ajuste_nivel)) linhas.push(`Ajuste de Nível: ${_s(det.ajuste_nivel)}`);
        if (_s(det.pagina_referencia)) linhas.push(_s(det.pagina_referencia));
        return linhas.join('\n');
    }

    global.DnD35BlocoMonstro = {
        gerar: gerarBlocoEstatisticas35,
        gerarBlocoEstatisticas35,
    };
})(typeof window !== 'undefined' ? window : globalThis);
