/**
 * Poderes v1.3 — filtro por categoria, custo PM e ativação na ficha.
 */
(function (global) {
    'use strict';

    const CATEGORIAS = [
        { slug: '', label: 'Todas as categorias' },
        { slug: 'geral', label: 'Gerais' },
        { slug: 'combate', label: 'Combate' },
        { slug: 'destino', label: 'Destino' },
        { slug: 'magia', label: 'Magia' },
        { slug: 'concedido', label: 'Concedidos' },
        { slug: 'tormenta', label: 'Tormenta' },
        { slug: 'classe', label: 'Classe' },
    ];

    function q(id) {
        return document.getElementById(id);
    }

    function isV13() {
        return (
            global.T20RegraVersao &&
            typeof global.getRegraVersaoAtiva === 'function' &&
            global.T20RegraVersao.isV13(global.getRegraVersaoAtiva())
        );
    }

    function labelCategoria(slug) {
        const s = String(slug || '').trim().toLowerCase();
        const row = CATEGORIAS.find((c) => c.slug === s);
        return row ? row.label : slug || '';
    }

    function montarFiltroCategoriaModal() {
        const host = q('talentosMbControlesV13');
        const sel = q('talentosMbCategoriaV13');
        if (!host || !sel) return;
        if (!isV13()) {
            host.style.display = 'none';
            return;
        }
        host.style.display = '';
        if (sel.options.length > 1) return;
        CATEGORIAS.forEach((c) => {
            const op = document.createElement('option');
            op.value = c.slug;
            op.textContent = c.label;
            sel.appendChild(op);
        });
    }

    function paramsCatalogoPoderes(base) {
        const p = Object.assign({}, base || {});
        if (isV13()) {
            const cat = q('talentosMbCategoriaV13');
            if (cat && cat.value) p.categoria_v13 = cat.value;
        }
        return p;
    }

    function atualizarPmNaFicha(depois, max) {
        const el = q('fichaPm');
        if (!el) return;
        const s = `${depois} / ${max}`;
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') el.value = s;
        else el.textContent = s;
    }

    async function ativarPoder(vinculoId, custoPm) {
        const fid = q('fichaId') && q('fichaId').value;
        if (!fid) throw new Error('Salve a ficha antes de ativar poderes.');
        const svc = new TormentaPersonagemService();
        const res = await svc.ativarPoder(fid, { vinculo_id: vinculoId, custo_pm: custoPm });
        atualizarPmNaFicha(res.pa_atual_depois, res.pa_max);
        if (global.Toast && global.Toast.success) {
            global.Toast.success(
                `${res.nome}: −${res.custo_pm} PM (restam ${res.pa_atual_depois}/${res.pa_max}).`
            );
        }
        return res;
    }

    function decorarLinha(row, opts) {
        if (!row || !isV13()) return;
        const o = opts || {};
        const custo = Number(o.custo_pm);
        if (!Number.isFinite(custo) || custo <= 0 || !o.vinculoId) return;
        if (row.querySelector('.t20-poder-ativar-btn')) return;

        const badge = document.createElement('span');
        badge.className = 't20-hint t20-poder-pm-badge';
        badge.style.marginLeft = '0.35rem';
        badge.textContent = `${custo} PM`;
        const inp = row.querySelector('.t20-tal-nome');
        if (inp && inp.parentNode) inp.parentNode.insertBefore(badge, inp.nextSibling);

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'tormenta-btn t20-poder-ativar-btn';
        btn.textContent = 'Ativar';
        btn.title = `Gasta ${custo} PM ao ativar`;
        btn.addEventListener('click', async () => {
            btn.disabled = true;
            try {
                await ativarPoder(o.vinculoId, custo);
            } catch (e) {
                if (global.Toast && global.Toast.error) {
                    global.Toast.error(e.message || 'Erro ao ativar poder');
                }
            } finally {
                btn.disabled = false;
            }
        });
        const pick = row.querySelector('.t20-eq-pick');
        if (pick && pick.parentNode) {
            pick.parentNode.insertBefore(btn, pick);
        } else {
            row.appendChild(btn);
        }
    }

    function wireModalFiltro() {
        if (global.__t20PoderesV13ModalBound) return;
        global.__t20PoderesV13ModalBound = true;
        q('talentosMbCategoriaV13')?.addEventListener('change', () => {
            if (typeof global.carregarTalCatalogoTormenta === 'function') {
                global.carregarTalCatalogoTormenta(true);
            }
        });
    }

    function coletarNomesPoderesFicha() {
        const nomes = [];
        document.querySelectorAll('#t20FichaTalentosMb .t20-tal-nome').forEach((inp) => {
            const v = (inp.value || '').trim();
            if (v.length >= 2) nomes.push(v);
        });
        return nomes;
    }

    async function validarAntesDeAdicionar(nome, getContext) {
        if (!isV13()) return { valido: true };
        const ctx = typeof getContext === 'function' ? getContext() : null;
        if (!ctx) return { valido: true };
        const regras = new TormentaRegrasService();
        const res = await regras.validarPreRequisitosPoder({
            nome_poder: nome,
            regra_versao: 'v13',
            nivel: ctx.nivel,
            for_valor: ctx.for_valor,
            des_valor: ctx.des_valor,
            con_valor: ctx.con_valor,
            int_valor: ctx.int_valor,
            sab_valor: ctx.sab_valor,
            car_valor: ctx.car_valor,
            ficha_json: ctx.ficha_json,
            poderes_escolhidos: ctx.poderes_escolhidos || [],
        });
        if (!res.valido && global.Toast && global.Toast.error) {
            const msg =
                res.motivo ||
                (res.faltando || []).map((f) => f.descricao).filter(Boolean).join('; ') ||
                'Pré-requisitos não atendidos';
            global.Toast.error(`«${nome}»: ${msg}`);
        }
        return res;
    }

    function init() {
        montarFiltroCategoriaModal();
        wireModalFiltro();
    }

    global.T20PoderesV13 = {
        init,
        decorarLinha,
        paramsCatalogoPoderes,
        labelCategoria,
        validarAntesDeAdicionar,
        coletarNomesPoderesFicha,
        CATEGORIAS,
    };
})(typeof window !== 'undefined' ? window : globalThis);
