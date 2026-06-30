/**
 * Wizard de criação v1.3 no dashboard — passos: identidade → raça/classe → atributos → origem → kit → revisão.
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

    let ORIGENS = [];
    let KIT_OPCOES = null;
    let stepAtual = 1;
    let cfg = null;

    function q(id) {
        return document.getElementById(id);
    }

    function isV13() {
        return cfg && cfg.regraVersao === 'v13';
    }

    function isWizardAtivo() {
        const tipo = q('cadTipo') && q('cadTipo').value;
        return isV13() && String(tipo || '').toLowerCase() === 'jogador';
    }

    function totalPassos() {
        return isWizardAtivo() ? 6 : 1;
    }

    function slugParaLabel(slug) {
        return String(slug || '')
            .replace(/_/g, ' ')
            .replace(/\b\w/g, (c) => c.toUpperCase());
    }

    async function carregarCatalogos() {
        if (!isV13()) return;
        try {
            const svc = new TormentaRegrasService();
            const data = await svc.obterOrigens({ regraVersao: 'v13' });
            ORIGENS = Array.isArray(data.origens) ? data.origens : [];
        } catch (_e) {
            ORIGENS = [];
        }
    }

    function origemPorSlug(slug) {
        const s = String(slug || '').trim().toLowerCase();
        return ORIGENS.find((o) => o.slug === s) || null;
    }

    async function carregarKitOpcoes() {
        if (!isV13()) return;
        const slug = q('cadClasseMb') && q('cadClasseMb').value;
        try {
            const svc = new TormentaRegrasService();
            const data = await svc.obterKitInicial({
                tormentaClasseMbSlug: slug,
                regraVersao: 'v13',
            });
            KIT_OPCOES = data && data.opcoes ? data.opcoes : null;
        } catch (_e) {
            KIT_OPCOES = null;
        }
    }

    function preencherSelectOrigens() {
        const sel = q('cadOrigemSlug');
        if (!sel) return;
        const prev = sel.value;
        sel.innerHTML = '<option value="">— Escolha a origem —</option>';
        ORIGENS.forEach((o) => {
            const op = document.createElement('option');
            op.value = o.slug;
            op.textContent = o.nome;
            sel.appendChild(op);
        });
        if (prev) sel.value = prev;
    }

    function renderBeneficiosOrigem() {
        const host = q('cadOrigemBeneficiosHost');
        const sel = q('cadOrigemSlug');
        if (!host || !sel) return;
        const row = origemPorSlug(sel.value);
        if (!row) {
            host.innerHTML = '';
            return;
        }
        const saved = global.__cadOrigemBeneficios || [];
        const opts = [];
        (row.beneficios_pericias || []).forEach((p) => {
            opts.push({ id: `pericia:${p}`, label: `Perícia: ${slugParaLabel(p)}` });
        });
        (row.beneficios_poderes || []).forEach((p) => {
            opts.push({ id: `poder:${p}`, label: `Poder: ${slugParaLabel(p)}` });
        });
        if (row.poder_unico) {
            opts.push({
                id: `poder:${row.poder_unico}`,
                label: `Poder único: ${slugParaLabel(row.poder_unico)}`,
            });
        }
        host.innerHTML =
            '<p class="t20-dash-hint" style="margin:0 0 .35rem">Escolha <strong>2</strong> benefícios:</p>' +
            opts
                .map(
                    (o) =>
                        `<label style="display:block;margin:.15rem 0"><input type="checkbox" class="cad-origem-ben-cb" value="${o.id}" ${saved.includes(o.id) ? 'checked' : ''}/> ${o.label}</label>`
                )
                .join('');
        host.querySelectorAll('.cad-origem-ben-cb').forEach((cb) => {
            cb.addEventListener('change', () => {
                const picks = Array.from(host.querySelectorAll('.cad-origem-ben-cb:checked')).map(
                    (x) => x.value
                );
                if (picks.length > 2) {
                    cb.checked = false;
                    if (cfg && cfg.Toast) cfg.Toast.error('Máximo 2 benefícios da origem.');
                    return;
                }
                global.__cadOrigemBeneficios = picks;
                renderResumo();
            });
        });
        renderOrigemItensEscolha(row);
        renderOrigemItensLista(row);
    }

    function renderOrigemItensEscolha(row) {
        const host = q('cadOrigemItensEscolhaHost');
        if (!host) return;
        if (!row || !row.itens_escolha) {
            host.innerHTML = '';
            host.style.display = 'none';
            return;
        }
        const esc = row.itens_escolha;
        const opcoes = esc.opcoes || [];
        const saved =
            (global.__cadOrigemItensEscolha && global.__cadOrigemItensEscolha[row.slug]) ||
            esc.default ||
            '';
        host.style.display = '';
        host.innerHTML =
            '<p class="t20-dash-hint" style="margin:0 0 .35rem">Item da origem:</p>' +
            opcoes
                .map(
                    (o) =>
                        `<label style="display:block;margin:.15rem 0"><input type="radio" name="cadOrigemItemEsc" value="${o.slug}" ${saved === o.slug ? 'checked' : ''}/> ${o.nome}</label>`
                )
                .join('');
        host.querySelectorAll('input[name="cadOrigemItemEsc"]').forEach((rb) => {
            rb.addEventListener('change', () => {
                if (!global.__cadOrigemItensEscolha) global.__cadOrigemItensEscolha = {};
                global.__cadOrigemItensEscolha[row.slug] = rb.value;
                renderResumo();
            });
        });
    }

    function renderOrigemItensLista(row) {
        const el = q('cadOrigemItensLista');
        if (!el) return;
        if (!row) {
            el.textContent = '';
            return;
        }
        const itens = Array.isArray(row.itens) ? row.itens : [];
        if (row.itens_escolha) {
            el.textContent = itens.length
                ? `Itens fixos: ${itens.join(', ')}`
                : 'Escolha o item acima.';
        } else if (itens.length) {
            el.textContent = `Itens grátis: ${itens.join(', ')}`;
        } else {
            el.textContent = 'Sem itens fixos nesta origem.';
        }
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

    function renderUiKit() {
        const wrap = q('cadWizardStepKit');
        const nv = q('cadNivel') ? parseInt(String(q('cadNivel').value || '1'), 10) : 1;
        if (wrap) wrap.style.display = nv <= 1 ? '' : 'none';
        if (!KIT_OPCOES || nv > 1) return;
        const op = KIT_OPCOES;
        const kit = global.__cadKitInicial || {};
        preencherSelect(q('cadKitArmaSimples'), ARMAS_SIMPLES, kit.arma_simples || 'Adaga');
        const wrapM = q('cadWrapKitArmaMarcial');
        if (wrapM) wrapM.style.display = op.arma_marcial ? '' : 'none';
        if (op.arma_marcial) {
            preencherSelect(q('cadKitArmaMarcial'), ARMAS_MARCIAIS, kit.arma_marcial || 'Espada longa');
        }
        const wrapA = q('cadWrapKitArmadura');
        const hintSem = q('cadKitSemArmaduraHint');
        if (wrapA) wrapA.style.display = op.armadura_leve && !op.sem_armadura ? '' : 'none';
        if (hintSem) hintSem.style.display = op.sem_armadura ? '' : 'none';
        if (op.armadura_leve && !op.sem_armadura) {
            const arms = (op.armaduras_leves || []).slice();
            if (op.armadura_pesada_opcao && op.armadura_pesada) arms.push(op.armadura_pesada);
            preencherSelect(q('cadKitArmadura'), arms, kit.armadura || arms[0]);
        }
        const wrapE = q('cadWrapKitEscudo');
        if (wrapE) wrapE.style.display = op.escudo ? '' : 'none';
        const cbE = q('cadKitEscudo');
        if (cbE) cbE.checked = kit.escudo !== false && kit.escudo !== undefined ? !!kit.escudo : !!op.escudo;
        const lbl = q('cadKitDinheiroRolado');
        if (lbl) {
            lbl.textContent =
                kit.dinheiro_pp != null ? `T$ ${kit.dinheiro_pp} (4d6)` : 'Clique em «Rolar T$ 4d6»';
        }
    }

    function rolarDinheiroKit() {
        let s = 0;
        for (let i = 0; i < 4; i++) s += 1 + Math.floor(Math.random() * 6);
        if (!global.__cadKitInicial) global.__cadKitInicial = {};
        global.__cadKitInicial.dinheiro_pp = s;
        renderUiKit();
        renderResumo();
        if (cfg && cfg.Toast) cfg.Toast.success(`T$ ${s} (4d6) rolado.`);
    }

    function renderNav() {
        const nav = q('cadWizardNav');
        if (!nav) return;
        nav.style.display = isWizardAtivo() ? '' : 'none';
        if (!isWizardAtivo()) return;
        const labels = [
            'Identidade',
            'Raça e classe',
            'Atributos',
            'Origem',
            'Equipamento',
            'Revisão',
        ];
        nav.innerHTML = labels
            .map((lab, i) => {
                const n = i + 1;
                const cls =
                    n === stepAtual
                        ? 'cad-wizard-nav__item cad-wizard-nav__item--active'
                        : n < stepAtual
                          ? 'cad-wizard-nav__item cad-wizard-nav__item--done'
                          : 'cad-wizard-nav__item';
                return `<span class="${cls}" data-cad-nav="${n}">${n}. ${lab}</span>`;
            })
            .join('');
    }

    function mostrarPasso(n) {
        stepAtual = Math.max(1, Math.min(totalPassos(), n));
        document.querySelectorAll('.cad-wizard-step').forEach((el) => {
            const s = parseInt(el.getAttribute('data-cad-step') || '0', 10);
            if (!isWizardAtivo()) {
                const v13only = el.classList.contains('cad-wizard-step--v13');
                el.style.display = v13only ? 'none' : '';
                return;
            }
            el.style.display = s === stepAtual ? '' : 'none';
        });
        renderNav();
        atualizarBotoesRodape();
        if (stepAtual === 4) renderBeneficiosOrigem();
        if (stepAtual === 5) renderUiKit();
        if (stepAtual === 6) renderResumo();
    }

    function atualizarBotoesRodape() {
        const prev = q('cadWizardPrev');
        const next = q('cadWizardNext');
        const sub = q('btnConfirmarCadastro');
        if (!isWizardAtivo()) {
            if (prev) prev.style.display = 'none';
            if (next) next.style.display = 'none';
            if (sub) {
                sub.style.display = '';
                sub.textContent = 'Criar e abrir ficha';
            }
            return;
        }
        if (prev) prev.style.display = stepAtual > 1 ? '' : 'none';
        if (next) next.style.display = stepAtual < totalPassos() ? '' : 'none';
        if (sub) {
            sub.style.display = stepAtual === totalPassos() ? '' : 'none';
            sub.textContent = 'Criar e abrir ficha';
        }
    }

    function renderResumo() {
        const host = q('cadWizardResumo');
        if (!host) return;
        const nome = q('cadNome') && q('cadNome').value.trim();
        const nv = q('cadNivel') && q('cadNivel').value;
        const cls = q('cadClasseMb') && q('cadClasseMb').selectedOptions[0];
        const rac = q('cadRacaSelect') && q('cadRacaSelect').selectedOptions[0];
        const orig = q('cadOrigemSlug') && q('cadOrigemSlug').selectedOptions[0];
        const bens = (global.__cadOrigemBeneficios || []).join(', ') || '—';
        const kit = global.__cadKitInicial || {};
        host.innerHTML =
            `<p><strong>${nome || '—'}</strong> · Nv ${nv || '1'}</p>` +
            `<p>Classe: ${cls ? cls.textContent : '—'} · Raça: ${rac ? rac.textContent : '—'}</p>` +
            `<p>Origem: ${orig ? orig.textContent : '—'}</p>` +
            `<p>Benefícios: ${bens}</p>` +
            (parseInt(String(nv || '1'), 10) <= 1
                ? `<p>Kit: ${kit.arma_simples || '—'}${kit.arma_marcial ? ', ' + kit.arma_marcial : ''}${kit.armadura ? ', ' + kit.armadura : ''}${kit.dinheiro_pp != null ? ' · T$ ' + kit.dinheiro_pp : ''}</p>`
                : '');
    }

    function validarPasso(n) {
        if (!cfg) return { ok: true };
        if (n === 1) {
            const nome = q('cadNome') && q('cadNome').value.trim();
            if (!nome) return { ok: false, msg: 'Informe o nome do personagem.' };
            const nivel = Math.floor(Number(q('cadNivel') && q('cadNivel').value));
            if (!Number.isFinite(nivel) || nivel < 0 || nivel > 40) {
                return { ok: false, msg: 'Nível deve estar entre 0 e 40.' };
            }
            const pv = Math.floor(Number(q('cadPvMax') && q('cadPvMax').value));
            if (!Number.isFinite(pv) || pv < 0) return { ok: false, msg: 'PV máximos inválidos.' };
            return { ok: true };
        }
        if (n === 2) {
            if (cfg.validarRaca && typeof cfg.validarRaca === 'function') {
                const vr = cfg.validarRaca();
                if (!vr.ok) return vr;
            }
            return { ok: true };
        }
        if (n === 3) {
            if (cfg.validarAtributos && typeof cfg.validarAtributos === 'function') {
                return cfg.validarAtributos();
            }
            return { ok: true };
        }
        if (n === 4) {
            const slug = q('cadOrigemSlug') && q('cadOrigemSlug').value;
            if (!slug) return { ok: false, msg: 'Escolha a origem do personagem (v1.3).' };
            const bens = global.__cadOrigemBeneficios || [];
            if (bens.length !== 2) {
                return { ok: false, msg: 'Escolha exatamente 2 benefícios da origem.' };
            }
            return { ok: true };
        }
        if (n === 5) {
            const nv = parseInt(String(q('cadNivel') && q('cadNivel').value || '1'), 10);
            if (nv > 1) return { ok: true };
            const arma = q('cadKitArmaSimples') && q('cadKitArmaSimples').value;
            if (!arma) return { ok: false, msg: 'Escolha a arma simples do kit inicial.' };
            return { ok: true };
        }
        return { ok: true };
    }

    function avancar() {
        const v = validarPasso(stepAtual);
        if (!v.ok) {
            if (cfg && cfg.Toast) cfg.Toast.error(v.msg || 'Passo incompleto.');
            return false;
        }
        if (stepAtual < totalPassos()) {
            mostrarPasso(stepAtual + 1);
        }
        return true;
    }

    function voltar() {
        if (stepAtual > 1) mostrarPasso(stepAtual - 1);
    }

    function resetWizard() {
        stepAtual = 1;
        global.__cadOrigemBeneficios = [];
        global.__cadOrigemItensEscolha = {};
        global.__cadKitInicial = {};
        if (q('cadOrigemSlug')) q('cadOrigemSlug').value = '';
        if (q('cadOrigemBeneficiosHost')) q('cadOrigemBeneficiosHost').innerHTML = '';
    }

    function lerPayloadOrigemKit() {
        if (!isV13()) return {};
        const slug = q('cadOrigemSlug') && q('cadOrigemSlug').value;
        const row = origemPorSlug(slug);
        const out = {
            cadastro_wizard_v13: true,
            origem_slug: slug || null,
            origem: row ? row.nome : '',
            origem_beneficios: Array.isArray(global.__cadOrigemBeneficios)
                ? global.__cadOrigemBeneficios.slice()
                : [],
            origem_itens_escolha:
                global.__cadOrigemItensEscolha && typeof global.__cadOrigemItensEscolha === 'object'
                    ? { ...global.__cadOrigemItensEscolha }
                    : {},
        };
        const nv = parseInt(String(q('cadNivel') && q('cadNivel').value || '1'), 10);
        if (nv <= 1) {
            const kit = {
                arma_simples: q('cadKitArmaSimples') && q('cadKitArmaSimples').value,
                escudo: !!(q('cadKitEscudo') && q('cadKitEscudo').checked),
            };
            if (KIT_OPCOES && KIT_OPCOES.arma_marcial && q('cadKitArmaMarcial')) {
                kit.arma_marcial = q('cadKitArmaMarcial').value || null;
            }
            if (KIT_OPCOES && KIT_OPCOES.armadura_leve && !KIT_OPCOES.sem_armadura && q('cadKitArmadura')) {
                kit.armadura = q('cadKitArmadura').value || null;
            }
            const din = global.__cadKitInicial && global.__cadKitInicial.dinheiro_pp;
            if (din != null) kit.dinheiro_pp = din;
            out.kit_inicial_v13 = kit;
            if (din != null) {
                out.dinheiro = { pc: 0, pp: din, po: 0, pl: 0 };
            }
        }
        return out;
    }

    function onAbrirCadastro() {
        resetWizard();
        void carregarCatalogos().then(() => {
            preencherSelectOrigens();
            void carregarKitOpcoes().then(renderUiKit);
            mostrarPasso(1);
        });
    }

    function bindOnce() {
        if (global.__cadWizardV13Bound) return;
        global.__cadWizardV13Bound = true;
        q('cadWizardPrev')?.addEventListener('click', () => voltar());
        q('cadWizardNext')?.addEventListener('click', () => avancar());
        q('cadOrigemSlug')?.addEventListener('change', () => {
            global.__cadOrigemBeneficios = [];
            renderBeneficiosOrigem();
        });
        q('cadClasseMb')?.addEventListener('change', () => {
            void carregarKitOpcoes().then(renderUiKit);
        });
        q('cadNivel')?.addEventListener('change', renderUiKit);
        q('cadBtnKitRolarDinheiro')?.addEventListener('click', () => rolarDinheiroKit());
        q('formCadastroRapido')?.addEventListener(
            'submit',
            (ev) => {
                if (!isWizardAtivo()) return;
                if (stepAtual < totalPassos()) {
                    ev.preventDefault();
                    avancar();
                }
            },
            true
        );
    }

    function init(config) {
        cfg = config || {};
        bindOnce();
    }

    global.T20DashWizardV13 = {
        init,
        onAbrirCadastro,
        isWizardAtivo,
        avancar,
        validarPasso,
        lerPayloadOrigemKit,
        mostrarPasso,
    };
})(typeof window !== 'undefined' ? window : globalThis);
