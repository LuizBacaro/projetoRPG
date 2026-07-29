/**
 * Motor de efeitos na ficha — agrega bônus/penalidades e exibe painel Fontes.
 */
(function (global) {
    'use strict';

    let cacheAgregado = null;
    let debounceTimer = null;

    function q(id) {
        return document.getElementById(id);
    }

    function montarFichaJsonMinimo() {
        if (typeof global.t20MontarFichaJsonEfeitos === 'function') {
            try {
                return global.t20MontarFichaJsonEfeitos() || {};
            } catch (_e) {
                return {};
            }
        }
        if (typeof global.payloadBase === 'function') {
            try {
                const payload = global.payloadBase();
                return payload && payload.ficha_json ? payload.ficha_json : payload || {};
            } catch (_e) {
                return {};
            }
        }
        return {};
    }

    function coletarPoderesSlugs() {
        const out = [];
        const seen = new Set();
        document.querySelectorAll('#t20FichaTalentosMb .t20-ficha-talento-linha').forEach((row) => {
            const slug = String(row.dataset.t20PoderSlug || row.dataset.slug || '').trim().toLowerCase();
            if (slug && !seen.has(slug)) {
                seen.add(slug);
                out.push(slug);
            }
        });
        return out;
    }

    async function agregarEfeitos(contexto) {
        const svc = new TormentaRegrasService();
        const fj = montarFichaJsonMinimo();
        const body = {
            ficha_json: fj,
            poderes_slugs: coletarPoderesSlugs(),
            contexto: contexto || {},
        };
        try {
            cacheAgregado = await svc.agregarEfeitosFicha(body);
        } catch (_e) {
            cacheAgregado = { fontes: [], totais: {}, condicionais: [], ativos: [] };
        }
        return cacheAgregado;
    }

    function fmtSigned(n) {
        const v = Number(n) || 0;
        return v > 0 ? `+${v}` : String(v);
    }

    function renderPainelFontes(data) {
        const host = q('t20FontesBonusHost');
        if (!host) return;
        const fontes = (data && data.fontes) || [];
        const cond = (data && data.condicionais) || [];
        const ativos = (data && data.ativos) || [];
        const ativosDeEfeito = ativos.filter((f) => f.tipo_ativo !== 'habilidade_origem');
        if (!fontes.length && !cond.length && !ativosDeEfeito.length) {
            host.innerHTML = '<p class="t20-hint" style="margin:0">Nenhum bônus ou penalidade estruturado ativo.</p>';
            return;
        }
        const lines = [];
        fontes.forEach((f) => {
            const cls = f.desvantagem ? 't20-fonte-item t20-fonte-item--pen' : 't20-fonte-item';
            const pag = f.pagina ? ` <span class="t20-fonte-pag">p.${f.pagina}</span>` : '';
            lines.push(`<li class="${cls}">${f.rotulo || f.id}${pag}</li>`);
        });
        cond.forEach((f) => {
            lines.push(
                `<li class="t20-fonte-item t20-fonte-item--cond">${f.rotulo || f.id} <em>(condicional)</em></li>`
            );
        });
        ativosDeEfeito.forEach((f) => {
            lines.push(
                `<li class="t20-fonte-item t20-fonte-item--ativo">${f.rotulo || f.id} <em>(ativa / PM)</em></li>`
            );
        });
        host.innerHTML = `<ul class="t20-fontes-lista">${lines.join('')}</ul>`;
    }

    function aplicarTotaisUi(data) {
        const tot = (data && data.totais) || {};
        const iniEl = q('fichaIniciativa');
        const iniBd = q('fichaIniciativaBreakdown');
        const iniBonus = Number(tot.iniciativa) || 0;
        if (iniBd && iniBonus) {
            const base = String(iniBd.textContent || '');
            if (!base.includes('origem/poder')) {
                iniBd.textContent = `${base} • efeitos ${fmtSigned(iniBonus)}`;
            }
        }
        const pvBd = q('fichaPvBreakdown');
        if (pvBd && tot.pv_max) {
            pvBd.textContent = `${pvBd.textContent.split('•')[0].trim()} • origem/item ${fmtSigned(tot.pv_max)} PV`;
        }
        const pmBd = q('fichaPmBreakdown');
        if (pmBd && tot.pm_max) {
            pmBd.textContent = `${pmBd.textContent.split('•')[0].trim()} • origem/item ${fmtSigned(tot.pm_max)} PM`;
        }
    }

    async function atualizar(contexto) {
        const data = await agregarEfeitos(contexto);
        renderPainelFontes(data);
        aplicarTotaisUi(data);
        if (global.T20HabilidadesOrigem && global.T20HabilidadesOrigem.renderAtivos) {
            global.T20HabilidadesOrigem.renderAtivos((data && data.ativos) || []);
        }
        if (global.T20BreakdownFicha && global.T20BreakdownFicha.atualizarPericias) {
            global.T20BreakdownFicha.atualizarPericias();
        }
        return data;
    }

    function atualizarDebounced(ctx) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => atualizar(ctx), 280);
    }

    function renderPreviewOrigem(origemRow) {
        const host = q('t20OrigemEfeitosPreview');
        if (!host) return;
        if (!origemRow) {
            host.innerHTML = '';
            host.hidden = true;
            return;
        }
        const parts = [];
        (origemRow.efeitos || []).forEach((e) => {
            parts.push(`<span class="t20-chip-efeito">${e.rotulo || e.id}</span>`);
        });
        (origemRow.habilidades_ativas || []).forEach((h) => {
            parts.push(
                `<span class="t20-chip-efeito t20-chip-efeito--ativo">${h.nome}${h.custo_pm ? ` (${h.custo_pm} PM)` : ''}</span>`
            );
        });
        if (origemRow.notas) {
            parts.push(`<span class="t20-chip-efeito t20-chip-efeito--nota">${origemRow.notas}</span>`);
        }
        host.innerHTML = parts.length
            ? `<p class="t20-hint" style="margin:0.25rem 0 0">Efeitos da origem:</p><div class="t20-efeitos-chips">${parts.join('')}</div>`
            : '';
        host.hidden = !parts.length;
    }

    function init() {
        const det = q('t20FontesBonusDetails');
        if (det) {
            det.addEventListener('toggle', () => {
                if (det.open) atualizarDebounced();
            });
        }
        document.addEventListener('t20:ficha-aplicada', () => atualizarDebounced());
        document.addEventListener('t20:origem-alterada', () => atualizarDebounced());
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    global.T20EfeitosFicha = {
        agregar: agregarEfeitos,
        atualizar,
        atualizarDebounced,
        renderPreviewOrigem,
        getCache: () => cacheAgregado,
    };
})(typeof window !== 'undefined' ? window : globalThis);
