/**
 * Kit inicial e itens de origem v1.3 — equipamento p.140 + itens grátis da origem.
 */
(function (global) {
    'use strict';

    const ARMAS_SIMPLES = [
        'Adaga',
        'Clava',
        'Maça',
        'Lança',
        'Bordão',
        'Cajado',
        'Azagaia',
        'Dardo',
        'Funda',
        'Estilingue',
    ];
    const ARMAS_MARCIAIS = [
        'Espada longa',
        'Espada curta',
        'Machado de batalha',
        'Martelo de guerra',
        'Tridente',
        'Arco curto',
        'Arco longo',
    ];

    let KIT_OPCOES = null;

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

    function nivelAtual() {
        const n = q('f_nivel') && parseInt(String(q('f_nivel').value || '1'), 10);
        return Number.isFinite(n) && n > 0 ? n : 1;
    }

    function slugClasseAtual() {
        return q('f_classe_mb') && q('f_classe_mb').value ? String(q('f_classe_mb').value).trim().toLowerCase() : '';
    }

    async function carregarOpcoesKit() {
        if (!isV13()) return null;
        const slug = slugClasseAtual();
        try {
            const svc = new TormentaRegrasService();
            const data = await svc.obterKitInicial({ tormentaClasseMbSlug: slug, regraVersao: 'v13' });
            KIT_OPCOES = data && data.opcoes ? data.opcoes : null;
        } catch (_e) {
            KIT_OPCOES = null;
        }
        return KIT_OPCOES;
    }

    function preencherSelect(el, opcoes, prev) {
        if (!el) return;
        el.innerHTML = '';
        (opcoes || []).forEach((nome) => {
            const op = document.createElement('option');
            op.value = nome;
            op.textContent = nome;
            el.appendChild(op);
        });
        if (prev && opcoes && opcoes.includes(prev)) el.value = prev;
    }

    function renderUiKitInicial() {
        const wrap = q('wrapKitInicialV13');
        if (!wrap) return;
        const v13 = isV13();
        const nv1 = nivelAtual() <= 1;
        wrap.style.display = v13 && nv1 ? '' : 'none';
        if (!v13 || !nv1 || !KIT_OPCOES) return;

        const op = KIT_OPCOES;
        const kit = global.__t20KitInicialV13 || {};

        preencherSelect(q('f_kit_arma_simples'), ARMAS_SIMPLES, kit.arma_simples || 'Adaga');

        const wrapMarc = q('wrapKitArmaMarcial');
        const selMarc = q('f_kit_arma_marcial');
        if (wrapMarc) wrapMarc.style.display = op.arma_marcial ? '' : 'none';
        if (op.arma_marcial) preencherSelect(selMarc, ARMAS_MARCIAIS, kit.arma_marcial || 'Espada longa');

        const wrapArm = q('wrapKitArmadura');
        const selArm = q('f_kit_armadura');
        if (wrapArm) wrapArm.style.display = op.armadura_leve && !op.sem_armadura ? '' : 'none';
        if (op.sem_armadura && q('t20KitSemArmaduraHint')) {
            q('t20KitSemArmaduraHint').style.display = '';
        } else if (q('t20KitSemArmaduraHint')) {
            q('t20KitSemArmaduraHint').style.display = 'none';
        }
        if (op.armadura_leve && !op.sem_armadura) {
            const arms = (op.armaduras_leves || []).slice();
            if (op.armadura_pesada_opcao && op.armadura_pesada) arms.push(op.armadura_pesada);
            preencherSelect(selArm, arms, kit.armadura || arms[0]);
        }

        const wrapEsc = q('wrapKitEscudo');
        const cbEsc = q('f_kit_escudo');
        if (wrapEsc) wrapEsc.style.display = op.escudo ? '' : 'none';
        if (cbEsc) cbEsc.checked = kit.escudo !== false && kit.escudo !== undefined ? !!kit.escudo : !!op.escudo;

        const lblDin = q('t20KitDinheiroRolado');
        if (lblDin) {
            lblDin.textContent =
                kit.dinheiro_pp != null ? `T$ ${kit.dinheiro_pp} (4d6)` : 'Clique em «Rolar T$ 4d6»';
        }
    }

    function renderOrigemItensEscolha(row) {
        const host = q('t20OrigemItensEscolhaHost');
        if (!host) return;
        if (!row || !row.itens_escolha || !isV13()) {
            host.innerHTML = '';
            host.style.display = 'none';
            return;
        }
        const cfg = row.itens_escolha;
        const opcoes = cfg.opcoes || [];
        const saved = (global.__t20OrigemItensEscolha || {})[row.slug] || cfg.default || '';
        host.style.display = '';
        host.innerHTML =
            `<p class="t20-hint" style="margin:0 0 .35rem">Item da origem (escolha):</p>` +
            opcoes
                .map(
                    (o) =>
                        `<label style="display:block;margin:.15rem 0"><input type="radio" name="t20OrigemItemEsc" value="${o.slug}" ${saved === o.slug ? 'checked' : ''}/> ${o.nome}</label>`
                )
                .join('');
        host.querySelectorAll('input[name="t20OrigemItemEsc"]').forEach((rb) => {
            rb.addEventListener('change', () => {
                if (!global.__t20OrigemItensEscolha) global.__t20OrigemItensEscolha = {};
                global.__t20OrigemItensEscolha[row.slug] = rb.value;
                if (typeof global.t20AplicarEquipamentosAutomaticosNaLista === 'function') {
                    global.t20AplicarEquipamentosAutomaticosNaLista();
                }
            });
        });
    }

    function renderOrigemItensLista(row) {
        const el = q('t20OrigemItensLista');
        if (!el) return;
        if (!row || !isV13()) {
            el.textContent = '';
            return;
        }
        const itens = Array.isArray(row.itens) ? row.itens : [];
        if (row.itens_escolha) {
            el.textContent = itens.length ? `Itens fixos: ${itens.join(', ')}` : 'Escolha um item acima.';
        } else if (itens.length) {
            el.textContent = `Itens grátis: ${itens.join(', ')}`;
        } else {
            el.textContent = 'Sem itens fixos (ex.: Amnésico — mestre define).';
        }
    }

    function lerKitPayload() {
        if (!isV13() || nivelAtual() > 1) return null;
        const kit = global.__t20KitInicialV13 || {};
        return {
            arma_simples: q('f_kit_arma_simples') ? q('f_kit_arma_simples').value : kit.arma_simples || null,
            arma_marcial:
                KIT_OPCOES && KIT_OPCOES.arma_marcial && q('f_kit_arma_marcial')
                    ? q('f_kit_arma_marcial').value || null
                    : null,
            armadura:
                KIT_OPCOES && KIT_OPCOES.armadura_leve && !KIT_OPCOES.sem_armadura && q('f_kit_armadura')
                    ? q('f_kit_armadura').value || null
                    : null,
            escudo: !!(KIT_OPCOES && KIT_OPCOES.escudo && q('f_kit_escudo') && q('f_kit_escudo').checked),
            dinheiro_pp: kit.dinheiro_pp != null ? kit.dinheiro_pp : null,
        };
    }

    function aplicarKitPayload(fj) {
        if (!fj || typeof fj !== 'object') return;
        global.__t20KitInicialV13 =
            fj.kit_inicial_v13 && typeof fj.kit_inicial_v13 === 'object' ? { ...fj.kit_inicial_v13 } : {};
        global.__t20OrigemItensEscolha =
            fj.origem_itens_escolha && typeof fj.origem_itens_escolha === 'object'
                ? { ...fj.origem_itens_escolha }
                : {};
        if (fj.dinheiro && fj.dinheiro.pp && !global.__t20KitInicialV13.dinheiro_pp) {
            global.__t20KitInicialV13.dinheiro_pp = fj.dinheiro.pp;
        }
    }

    function rolarDinheiroKit() {
        let s = 0;
        for (let i = 0; i < 4; i++) s += 1 + Math.floor(Math.random() * 6);
        if (!global.__t20KitInicialV13) global.__t20KitInicialV13 = {};
        global.__t20KitInicialV13.dinheiro_pp = s;
        if (typeof global.t20AplicarDinheiroDoJson === 'function') {
            const prev = global.__t20DinheiroPersist || { pc: 0, pp: 0, po: 0, pl: 0 };
            global.t20AplicarDinheiroDoJson({ ...prev, pp: s }, {});
        }
        renderUiKitInicial();
        if (typeof Toast !== 'undefined') Toast.success(`T$ ${s} (4d6) — salve a ficha para persistir.`);
    }

    async function atualizarUiKitV13() {
        await carregarOpcoesKit();
        renderUiKitInicial();
    }

    function wireEvents() {
        if (global.__t20KitV13Bound) return;
        global.__t20KitV13Bound = true;
        q('f_classe_mb')?.addEventListener('change', () => atualizarUiKitV13());
        q('f_nivel')?.addEventListener('change', () => renderUiKitInicial());
        q('btnKitRolarDinheiro')?.addEventListener('click', () => rolarDinheiroKit());
        ['f_kit_arma_simples', 'f_kit_arma_marcial', 'f_kit_armadura', 'f_kit_escudo'].forEach((id) => {
            q(id)?.addEventListener('change', () => {
                if (typeof global.t20AplicarEquipamentosAutomaticosNaLista === 'function') {
                    global.t20AplicarEquipamentosAutomaticosNaLista();
                }
            });
        });
    }

    function resolverItensOrigemPreview(row) {
        if (!row) return [];
        const fixos = Array.isArray(row.itens) ? row.itens.slice() : [];
        if (row.itens_escolha && Array.isArray(row.itens_escolha.opcoes)) {
            const slug = row.slug;
            const pick =
                (global.__t20OrigemItensEscolha && global.__t20OrigemItensEscolha[slug]) ||
                row.itens_escolha.default ||
                '';
            const op =
                row.itens_escolha.opcoes.find((x) => x.slug === pick) || row.itens_escolha.opcoes[0];
            const escolhidos = op && Array.isArray(op.itens) ? op.itens.slice() : [];
            return fixos.concat(escolhidos);
        }
        return fixos;
    }

    function coletarEquipamentosPreview() {
        const nomes = [];
        const seen = new Set();
        const add = (nome, qtd) => {
            const n = String(nome || '').trim();
            const k = n.toLowerCase();
            if (n.length >= 1 && !seen.has(k)) {
                seen.add(k);
                nomes.push({ nome: n, qtd: Math.max(1, parseInt(String(qtd || 1), 10) || 1) });
            }
        };
        if (global.T20OrigensV13 && typeof global.T20OrigensV13.origemPorSlug === 'function') {
            const slug = q('f_origem_slug') && q('f_origem_slug').value;
            const row = global.T20OrigensV13.origemPorSlug(slug);
            resolverItensOrigemPreview(row).forEach((n) => add(n, 1));
        }
        if (KIT_OPCOES && isV13() && nivelAtual() <= 1) {
            (KIT_OPCOES.fixos || []).forEach((n) => add(n, 1));
            const kit = lerKitPayload() || {};
            if (kit.arma_simples) add(kit.arma_simples, 1);
            if (kit.arma_marcial) add(kit.arma_marcial, 1);
            if (kit.armadura) add(kit.armadura, 1);
            if (kit.escudo) add('Escudo leve de madeira', 1);
        }
        return nomes;
    }

    async function init() {
        wireEvents();
        await atualizarUiKitV13();
    }

    global.T20KitInicialV13 = {
        init,
        atualizarUiKitV13,
        renderOrigemItensLista,
        renderOrigemItensEscolha,
        lerKitPayload,
        aplicarKitPayload,
        rolarDinheiroKit,
        coletarEquipamentosPreview,
    };
})(typeof window !== 'undefined' ? window : globalThis);
