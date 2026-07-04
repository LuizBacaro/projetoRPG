/**
 * Wizard de criação v1.3 no dashboard — identidade → raça/classe → atributos → origem → devoção → kit → revisão.
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
    let TENDENCIAS = [];
    const CLASSES_DEVOTO_OBRIGATORIO = new Set(['clerigo', 'druida', 'paladino']);
    let DIVINIDADES = [];
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
        return isWizardAtivo() ? 8 : 1;
    }

    const PASSO_KIT = 7;

    function nivelCadastro() {
        const n = parseInt(String(q('cadNivel') && q('cadNivel').value || '1'), 10);
        return Number.isFinite(n) && n >= 0 ? n : 1;
    }

    /** Kit inicial v1.3 só se aplica a personagens de 1º nível. */
    function passoKitAplica() {
        return nivelCadastro() <= 1;
    }

    function proximoPasso(de) {
        return Math.min(totalPassos(), de + 1);
    }

    function passoAnterior(de) {
        return Math.max(1, de - 1);
    }

    function slugParaLabel(slug) {
        return String(slug || '')
            .replace(/_/g, ' ')
            .replace(/\b\w/g, (c) => c.toUpperCase());
    }

    function suplementoWizardAtivo() {
        const cb = q('cadUsarHeroisArton');
        if (!cb || !cb.checked) return null;
        return global.T20RegraVersao
            ? global.T20RegraVersao.SUPLEMENTO_HEROIS_ARTON
            : 'herois_arton';
    }

    async function carregarCatalogos() {
        if (!isV13()) return;
        try {
            const svc = new TormentaRegrasService();
            const sup = suplementoWizardAtivo();
            const [orig, ident] = await Promise.all([
                svc.obterOrigens({ regraVersao: 'v13', suplemento: sup }),
                svc.obterIdentidadeMb(),
            ]);
            ORIGENS = Array.isArray(orig.origens) ? orig.origens : [];
            TENDENCIAS = Array.isArray(ident.tendencias) ? ident.tendencias : [];
            DIVINIDADES = Array.isArray(ident.divindades) ? ident.divindades : [];
        } catch (_e) {
            ORIGENS = [];
            TENDENCIAS = [];
            DIVINIDADES = [];
        }
    }

    function divindadePorSlug(slug) {
        const s = String(slug || '').trim().toLowerCase();
        return DIVINIDADES.find((d) => String(d.slug || '').toLowerCase() === s) || null;
    }

    function slugDivindadeSelecionado() {
        const sel = q('cadDivindade');
        if (!sel || !sel.selectedOptions || !sel.selectedOptions[0]) return '';
        return String(sel.selectedOptions[0].getAttribute('data-slug') || '').trim().toLowerCase();
    }

    function classeExigeDevocao() {
        const slug = String((q('cadClasseMb') && q('cadClasseMb').value) || '')
            .trim()
            .toLowerCase();
        return CLASSES_DEVOTO_OBRIGATORIO.has(slug);
    }

    function sincronizarDevotoObrigatorioWizard() {
        const exige = classeExigeDevocao();
        if (exige && q('cadDevoto')) q('cadDevoto').checked = true;
        const hint = q('cadDevocaoHint');
        if (hint) {
            let txt = exige
                ? 'Clérigo, druida e paladino devem escolher divindade e poder concedido.'
                : 'Devoção opcional. Devotos escolhem um deus (Os Vinte) e um poder concedido (Tabela 1-20 v1.3).';
            if (String((q('cadClasseMb') && q('cadClasseMb').value) || '').toLowerCase() === 'paladino') {
                txt += ' Paladinos são campeões do bem e da ordem (narrativo).';
            }
            hint.textContent = txt;
        }
        return exige;
    }

    function preencherSelectTendencias() {
        const sel = q('cadTendencia');
        if (!sel) return;
        const prev = sel.value;
        sel.innerHTML = '<option value="">—</option>';
        TENDENCIAS.forEach((t) => {
            const rotulo = typeof t === 'string' ? t : String(t.rotulo || t.nome || '').trim();
            if (!rotulo) return;
            const op = document.createElement('option');
            op.value = rotulo;
            op.textContent = rotulo;
            sel.appendChild(op);
        });
        if (prev) sel.value = prev;
    }

    function preencherSelectDivindades() {
        const sel = q('cadDivindade');
        if (!sel) return;
        const prev = sel.value;
        sel.innerHTML = '<option value="">— Nenhuma —</option>';
        DIVINIDADES.forEach((d) => {
            const rotulo = String(d.rotulo || d.nome || '').trim();
            const slug = String(d.slug || '').trim();
            if (!rotulo) return;
            const op = document.createElement('option');
            op.value = rotulo;
            op.textContent = rotulo;
            if (slug) op.setAttribute('data-slug', slug);
            sel.appendChild(op);
        });
        if (prev) sel.value = prev;
    }

    function renderPoderesConcedidos() {
        const selPod = q('cadPoderConcedido');
        if (!selPod) return;
        const divSlug = slugDivindadeSelecionado();
        const row = divindadePorSlug(divSlug);
        const prev = selPod.value;
        selPod.innerHTML = '<option value="">— Nenhum / não devoto —</option>';
        if (row && Array.isArray(row.poderes_concedidos)) {
            row.poderes_concedidos.forEach((p) => {
                const op = document.createElement('option');
                op.value = p;
                op.textContent = slugParaLabel(p);
                selPod.appendChild(op);
            });
        }
        if (prev && Array.from(selPod.options).some((o) => o.value === prev)) {
            selPod.value = prev;
        } else {
            selPod.value = '';
        }
        renderObrigacoesDivindadeCad(row);
    }

    function renderObrigacoesDivindadeCad(row) {
        const host = q('cadDivindadeObrigacoesHost');
        if (!host) return;
        if (!row) {
            host.innerHTML = '';
            host.style.display = 'none';
            return;
        }
        const flags = Array.isArray(row.obrigacoes_flags) ? row.obrigacoes_flags : [];
        if (!flags.length) {
            host.innerHTML = '';
            host.style.display = 'none';
            return;
        }
        host.style.display = '';
        const pag = row.pagina ? ` <span class="t20-obrig-pag">(livro p.${row.pagina})</span>` : '';
        host.innerHTML =
            `<p class="t20-dash-hint" style="margin:0 0 .35rem"><strong>Obrigações & Restrições</strong>${pag}</p>` +
            `<ul class="t20-obrig-list cad-obrig-list">${flags
                .map((f) => `<li>${String(f.rotulo || f.slug || '').trim()}</li>`)
                .join('')}</ul>` +
            (row.sem_penalidade_obrigacao
                ? '<p class="t20-dash-hint" style="margin:.35rem 0 0">Nimb: violar O&R não causa perda de PM.</p>'
                : '');
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
            global.__cadOrigemPermiteTroca = false;
            return;
        }
        global.__cadOrigemPermiteTroca = Boolean(row.troca_pericia_treinada);
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
            `<div class="cad-origem-beneficios-list" style="display:grid;gap:0.25rem;max-width:34rem">${opts
                .map(
                    (o) =>
                        `<label class="cad-origem-ben-item" style="display:grid;grid-template-columns:auto minmax(0,1fr);align-items:start;gap:0.6rem;margin:0;padding:0.25rem 0.1rem;cursor:pointer;line-height:1.3;border-radius:0.25rem">` +
                        `<input type="checkbox" class="cad-origem-ben-cb" value="${o.id}" ${saved.includes(o.id) ? 'checked' : ''} style="margin-top:0.18rem"/>` +
                        `<span style="display:block;min-width:0">${o.label}</span></label>`
                )
                .join('')}</div>`;
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
                global.__cadOrigemTrocasPericia = {};
                if (global.T20DashPericiasV13 && global.T20DashPericiasV13.invalidarPericias) {
                    global.T20DashPericiasV13.invalidarPericias();
                }
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
                renderEquipamentosPreview();
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

    function resolverItensOrigemPreview(row) {
        if (!row) return [];
        const fixos = Array.isArray(row.itens) ? row.itens.slice() : [];
        if (row.itens_escolha && Array.isArray(row.itens_escolha.opcoes)) {
            const slug = row.slug;
            const pick =
                (global.__cadOrigemItensEscolha && global.__cadOrigemItensEscolha[slug]) ||
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
        const add = (nome, qtd, tag) => {
            const n = String(nome || '').trim();
            const k = n.toLowerCase();
            if (n.length >= 1 && !seen.has(k)) {
                seen.add(k);
                nomes.push({
                    nome: n,
                    qtd: Math.max(1, parseInt(String(qtd || 1), 10) || 1),
                    tag: tag || '',
                });
            }
        };
        const slugOrig = q('cadOrigemSlug') && q('cadOrigemSlug').value;
        const rowOrig = origemPorSlug(slugOrig);
        resolverItensOrigemPreview(rowOrig).forEach((n) => add(n, 1, 'origem'));
        if (passoKitAplica() && KIT_OPCOES) {
            (KIT_OPCOES.fixos || []).forEach((n) => add(n, 1, 'kit'));
            const kit = global.__cadKitInicial || {};
            const armaS =
                (q('cadKitArmaSimples') && q('cadKitArmaSimples').value) || kit.arma_simples;
            const armaM =
                (q('cadKitArmaMarcial') && q('cadKitArmaMarcial').value) || kit.arma_marcial;
            const arm =
                (q('cadKitArmadura') && q('cadKitArmadura').value) || kit.armadura;
            const esc =
                q('cadKitEscudo') && q('cadKitEscudo').checked !== undefined
                    ? q('cadKitEscudo').checked
                    : kit.escudo !== false;
            if (armaS) add(armaS, 1, 'kit');
            if (KIT_OPCOES.arma_marcial && armaM) add(armaM, 1, 'kit');
            if (KIT_OPCOES.armadura_leve && !KIT_OPCOES.sem_armadura && arm) add(arm, 1, 'kit');
            if (KIT_OPCOES.escudo && esc) add('Escudo leve de madeira', 1, 'kit');
        }
        return nomes;
    }

    function renderEquipamentosPreview() {
        const wrap = q('cadEquipamentosPreviewWrap');
        const lista = q('cadEquipamentosPreviewLista');
        if (!wrap || !lista) return;
        if (!passoKitAplica()) {
            wrap.style.display = 'none';
            return;
        }
        wrap.style.display = '';
        const itens = coletarEquipamentosPreview();
        if (!itens.length) {
            lista.innerHTML =
                '<li class="t20-dash-hint" style="margin:0">Escolha a origem (passo 4) para ver os itens grátis.</li>';
            return;
        }
        lista.innerHTML = itens
            .map((it) => {
                const tag =
                    it.tag === 'origem'
                        ? '<span class="cad-equip-preview-tag cad-equip-preview-tag--origem">origem</span>'
                        : it.tag === 'kit'
                          ? '<span class="cad-equip-preview-tag cad-equip-preview-tag--kit">kit</span>'
                          : '';
                return `<li>${tag}<span>${it.nome}</span>${it.qtd > 1 ? ` ×${it.qtd}` : ''}</li>`;
            })
            .join('');
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
        if (!passoKitAplica() || !KIT_OPCOES) return;
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
        if (global.T20DinheiroTabelaV13 && typeof global.T20DinheiroTabelaV13.atualizarUiWizard === 'function') {
            void global.T20DinheiroTabelaV13.atualizarUiWizard();
        }
        renderEquipamentosPreview();
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
            'Perícias',
            'Devoção',
            nivelCadastro() <= 1 ? 'Equipamento' : 'Dinheiro (T$)',
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
        if (stepAtual === 1 && global.T20DashStep2V13 && global.T20DashStep2V13.atualizarUiPasso2) {
            global.T20DashStep2V13.atualizarUiPasso2();
        }
        if (stepAtual === 2 && global.T20DashStep2V13 && global.T20DashStep2V13.atualizarUiPasso2) {
            global.T20DashStep2V13.atualizarUiPasso2();
        }
        if (stepAtual === 4) renderBeneficiosOrigem();
        if (stepAtual === 5 && global.T20DashPericiasV13 && global.T20DashPericiasV13.prepararPassoPericias) {
            void global.T20DashPericiasV13.prepararPassoPericias();
        }
        if (stepAtual === 6) {
            sincronizarDevotoObrigatorioWizard();
            renderPoderesConcedidos();
        }
        if (stepAtual === 7) {
            renderUiKit();
            renderEquipamentosPreview();
        }
        if (stepAtual === 8) {
            void renderChecklistRevisao();
            renderResumo();
        }
    }

    function escapeHtmlCheck(s) {
        return String(s ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    async function montarItensChecklist() {
        const items = [];
        const v4 = validarPasso(4);
        items.push({
            passo: 4,
            label: 'Origem e benefícios',
            ok: v4.ok,
            msg: v4.msg || '',
            detalhe: v4.ok ? '2 benefícios escolhidos' : '',
        });

        let perOk = false;
        let perMsg = 'Complete o passo Perícias.';
        let perDet = '';
        if (global.T20DashPericiasV13 && global.T20DashPericiasV13.refreshOrcamento) {
            const st = await global.T20DashPericiasV13.refreshOrcamento();
            perOk = Boolean(st.ok);
            perMsg = st.msg || perMsg;
            perDet = st.detalhe || (st.treinadas ? `${st.treinadas} treinadas` : '');
        }
        items.push({
            passo: 5,
            label: 'Perícias treinadas',
            ok: perOk,
            msg: perMsg,
            detalhe: perDet,
        });

        const v6 = validarPasso(6);
        const devoto = !!(q('cadDevoto') && q('cadDevoto').checked);
        items.push({
            passo: 6,
            label: 'Devoção',
            ok: v6.ok,
            msg: v6.msg || '',
            detalhe: devoto ? 'Devoto configurado' : 'Opcional — sem devoção',
            optional: !devoto && v6.ok,
        });

        if (passoKitAplica() || nivelCadastro() > 1) {
            const v7 = validarPasso(7);
            items.push({
                passo: 7,
                label: passoKitAplica() ? 'Kit inicial' : 'Dinheiro (Tabela 3-1)',
                ok: v7.ok,
                msg: v7.msg || '',
                detalhe: v7.ok
                    ? passoKitAplica()
                        ? 'Equipamento de 1º nível'
                        : 'T$ conforme nível'
                    : '',
            });
        }

        return items;
    }

    async function renderChecklistRevisao() {
        const host = q('cadWizardChecklist');
        if (!host || !isWizardAtivo()) return;
        host.innerHTML = '<p class="t20-dash-hint" style="margin:0">Verificando…</p>';
        const items = await montarItensChecklist();
        const pendencias = items.filter((it) => !it.ok);
        global.__cadWizardChecklistOk = pendencias.length === 0;

        host.innerHTML =
            '<p class="cad-wizard-checklist__title">Checklist antes de criar</p>' +
            '<ul class="cad-wizard-checklist">' +
            items
                .map((it) => {
                    const cls = it.ok
                        ? 'cad-wizard-checklist__item cad-wizard-checklist__item--ok'
                        : 'cad-wizard-checklist__item cad-wizard-checklist__item--pendente';
                    const icon = it.ok ? '✓' : '⚠';
                    const det = it.detalhe ? `<span class="cad-wizard-checklist__det">${escapeHtmlCheck(it.detalhe)}</span>` : '';
                    const btn = it.ok
                        ? ''
                        : `<button type="button" class="tormenta-btn cad-wizard-checklist__btn" data-ir-passo="${it.passo}">Ajustar</button>`;
                    return (
                        `<li class="${cls}">` +
                        `<span class="cad-wizard-checklist__lab"><strong>${icon}</strong> ${escapeHtmlCheck(it.label)}</span>` +
                        det +
                        btn +
                        `</li>`
                    );
                })
                .join('') +
            '</ul>' +
            (pendencias.length
                ? `<p class="t20-dash-hint t20-compra-pontos-erro cad-wizard-checklist__aviso">` +
                  `${pendencias.length} item(ns) pendente(s) — corrija antes de criar.</p>`
                : `<p class="t20-dash-hint t20-compra-pontos-ok cad-wizard-checklist__aviso">Tudo pronto para criar a ficha.</p>`);

        host.querySelectorAll('[data-ir-passo]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const n = parseInt(btn.getAttribute('data-ir-passo') || '0', 10);
                if (n >= 1) mostrarPasso(n);
            });
        });

        atualizarBotaoCriarChecklist(pendencias.length === 0);
    }

    function atualizarBotaoCriarChecklist(ok) {
        const sub = q('btnConfirmarCadastro');
        if (!sub || !isWizardAtivo() || stepAtual !== totalPassos()) return;
        if (ok) {
            sub.removeAttribute('aria-disabled');
            sub.title = '';
        } else {
            sub.setAttribute('aria-disabled', 'true');
            sub.title = 'Resolva os itens pendentes no checklist.';
        }
    }

    async function validarAntesCriar() {
        if (!isWizardAtivo()) return { ok: true };
        for (let s = 4; s <= 7; s++) {
            if (s === 7 && !passoKitAplica()) continue;
            if (
                s === 5 &&
                global.T20DashPericiasV13 &&
                typeof global.T20DashPericiasV13.validarPassoPericias === 'function'
            ) {
                const vp = await global.T20DashPericiasV13.validarPassoPericias();
                if (!vp.ok) return { ok: false, msg: vp.msg, passo: 5 };
                continue;
            }
            const vp = validarPasso(s);
            if (!vp.ok) return { ok: false, msg: vp.msg, passo: s };
        }
        const items = await montarItensChecklist();
        const pend = items.filter((it) => !it.ok);
        if (pend.length) {
            return {
                ok: false,
                msg: pend[0].msg || 'Itens pendentes na revisão.',
                passo: pend[0].passo,
            };
        }
        return { ok: true };
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
        const tend = q('cadTendencia') && q('cadTendencia').value;
        const div = q('cadDivindade') && q('cadDivindade').value;
        const devoto = !!(q('cadDevoto') && q('cadDevoto').checked);
        const pod =
            q('cadPoderConcedido') && q('cadPoderConcedido').selectedOptions[0]
                ? q('cadPoderConcedido').selectedOptions[0].textContent
                : '';
        const kit = global.__cadKitInicial || {};
        const eqPrev =
            passoKitAplica() && coletarEquipamentosPreview().length
                ? coletarEquipamentosPreview()
                      .map((it) => it.nome)
                      .join(', ')
                : '';
        const step2Extra =
            global.T20DashStep2V13 && global.T20DashStep2V13.resumoPasso2
                ? global.T20DashStep2V13.resumoPasso2()
                : '';
        const perRes =
            global.T20DashPericiasV13 && global.T20DashPericiasV13.resumoPericias
                ? global.T20DashPericiasV13.resumoPericias()
                : '';
        host.innerHTML =
            `<p><strong>${nome || '—'}</strong> · Nv ${nv || '1'}</p>` +
            `<p>Classe: ${cls ? cls.textContent : '—'} · Raça: ${rac ? rac.textContent : '—'}</p>` +
            (step2Extra ? `<p>${step2Extra}</p>` : '') +
            (perRes ? `<p>${perRes}</p>` : '') +
            `<p>Origem: ${orig ? orig.textContent : '—'}</p>` +
            `<p>Benefícios: ${bens}</p>` +
            `<p>Tendência: ${tend || '—'} · Divindade: ${div || '—'}${devoto ? ' (devoto)' : ''}</p>` +
            (pod ? `<p>Poder concedido: ${pod}</p>` : '') +
            (parseInt(String(nv || '1'), 10) <= 1
                ? `<p>Kit: ${kit.arma_simples || q('cadKitArmaSimples')?.value || '—'}${kit.arma_marcial ? ', ' + kit.arma_marcial : ''}${kit.armadura ? ', ' + kit.armadura : ''}${kit.dinheiro_pp != null ? ' · T$ ' + kit.dinheiro_pp : ''}</p>` +
                  (eqPrev ? `<p>Equipamento: ${eqPrev}</p>` : '')
                : `<p>T$ (Tabela 3-1): ${
                      kit.dinheiro_tabela_pp != null
                          ? kit.dinheiro_tabela_pp
                          : global.__cadDinheiroTabela && global.__cadDinheiroTabela.valor != null
                            ? global.__cadDinheiroTabela.valor
                            : '—'
                  }</p>`);
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
            if (
                global.T20DashPericiasV13 &&
                typeof global.T20DashPericiasV13.validarPassoPericias === 'function'
            ) {
                return global.T20DashPericiasV13.validarPassoPericias();
            }
            return { ok: true };
        }
        if (n === 6) {
            const exige = classeExigeDevocao();
            const devoto = exige || !!(q('cadDevoto') && q('cadDevoto').checked);
            const divSlug = slugDivindadeSelecionado();
            const pod = q('cadPoderConcedido') && q('cadPoderConcedido').value;
            if (devoto && !divSlug) {
                return {
                    ok: false,
                    msg: exige
                        ? 'Clérigo, druida e paladino devem escolher uma divindade.'
                        : 'Devoto: escolha uma divindade (Os Vinte).',
                };
            }
            if (devoto && !pod) {
                return {
                    ok: false,
                    msg: exige
                        ? 'Clérigo, druida e paladino devem escolher um poder concedido.'
                        : 'Devoto: escolha um poder concedido da divindade.',
                };
            }
            if (pod && !divSlug) {
                return { ok: false, msg: 'Poder concedido exige divindade escolhida.' };
            }
            if (pod && divSlug) {
                const row = divindadePorSlug(divSlug);
                const pool = row && Array.isArray(row.poderes_concedidos) ? row.poderes_concedidos : [];
                if (!pool.includes(pod)) {
                    return { ok: false, msg: 'Poder concedido inválido para a divindade escolhida.' };
                }
            }
            return { ok: true };
        }
        if (n === 7) {
            const nv = parseInt(String(q('cadNivel') && q('cadNivel').value || '1'), 10);
            if (nv > 1) {
                if (
                    global.__cadDinheiroTabela &&
                    global.__cadDinheiroTabela.valor != null &&
                    (!global.__cadKitInicial || global.__cadKitInicial.dinheiro_tabela_pp == null)
                ) {
                    if (!global.__cadKitInicial) global.__cadKitInicial = {};
                    global.__cadKitInicial.dinheiro_tabela_pp = global.__cadDinheiroTabela.valor;
                }
                return { ok: true };
            }
            const arma = q('cadKitArmaSimples') && q('cadKitArmaSimples').value;
            if (!arma) return { ok: false, msg: 'Escolha a arma simples do kit inicial.' };
            return { ok: true };
        }
        if (n === 8) {
            if (global.__cadWizardChecklistOk === false) {
                return {
                    ok: false,
                    msg: 'Revise o checklist — há itens pendentes (ex.: perícias).',
                };
            }
            return { ok: true };
        }
        return { ok: true };
    }

    async function avancar() {
        let v;
        if (
            stepAtual === 5 &&
            global.T20DashPericiasV13 &&
            typeof global.T20DashPericiasV13.validarPassoPericias === 'function'
        ) {
            v = await global.T20DashPericiasV13.validarPassoPericias();
        } else {
            v = validarPasso(stepAtual);
        }
        if (!v.ok) {
            if (cfg && cfg.Toast) cfg.Toast.error(v.msg || 'Passo incompleto.');
            return false;
        }
        if (stepAtual < totalPassos()) {
            mostrarPasso(proximoPasso(stepAtual));
        }
        return true;
    }

    function voltar() {
        if (stepAtual > 1) mostrarPasso(passoAnterior(stepAtual));
    }

    function resetWizard() {
        stepAtual = 1;
        global.__cadOrigemBeneficios = [];
        global.__cadOrigemItensEscolha = {};
        global.__cadOrigemTrocasPericia = {};
        global.__cadOrigemPermiteTroca = false;
        global.__cadKitInicial = {};
        global.__cadWizardChecklistOk = null;
        if (q('cadOrigemSlug')) q('cadOrigemSlug').value = '';
        if (q('cadOrigemBeneficiosHost')) q('cadOrigemBeneficiosHost').innerHTML = '';
        if (q('cadTendencia')) q('cadTendencia').value = '';
        if (q('cadDivindade')) q('cadDivindade').value = '';
        if (q('cadDevoto')) q('cadDevoto').checked = false;
        if (q('cadPoderConcedido')) q('cadPoderConcedido').innerHTML = '';
        if (q('cadWizardChecklist')) q('cadWizardChecklist').innerHTML = '';
        global.__cadWizardChecklistOk = null;
        if (global.T20DashStep2V13 && global.T20DashStep2V13.resetPasso2) {
            global.T20DashStep2V13.resetPasso2();
        }
        if (global.T20DashPericiasV13 && global.T20DashPericiasV13.resetPericias) {
            global.T20DashPericiasV13.resetPericias();
        }
    }

    function lerPayloadCamposPersonagem() {
        if (!isV13()) return {};
        const tend = q('cadTendencia') && q('cadTendencia').value.trim();
        const div = q('cadDivindade') && q('cadDivindade').value.trim();
        return {
            tendencia: tend || null,
            divindade: div || null,
        };
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
            devoto: classeExigeDevocao() || !!(q('cadDevoto') && q('cadDevoto').checked),
            poder_concedido_slug:
                q('cadPoderConcedido') && q('cadPoderConcedido').value
                    ? String(q('cadPoderConcedido').value).trim()
                    : null,
            tormenta_divindade_mb_slug: slugDivindadeSelecionado() || null,
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
        } else if (nv > 1) {
            let din =
                global.__cadKitInicial && global.__cadKitInicial.dinheiro_tabela_pp != null
                    ? global.__cadKitInicial.dinheiro_tabela_pp
                    : null;
            if (din == null && global.__cadDinheiroTabela && global.__cadDinheiroTabela.valor != null) {
                din = global.__cadDinheiroTabela.valor;
            }
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
            preencherSelectTendencias();
            preencherSelectDivindades();
            renderPoderesConcedidos();
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
            global.__cadOrigemTrocasPericia = {};
            global.__cadOrigemPermiteTroca = false;
            if (global.T20DashPericiasV13 && global.T20DashPericiasV13.invalidarPericias) {
                global.T20DashPericiasV13.invalidarPericias();
            }
            renderBeneficiosOrigem();
            renderEquipamentosPreview();
        });
        q('cadDivindade')?.addEventListener('change', () => {
            renderPoderesConcedidos();
            renderResumo();
        });
        q('cadDevoto')?.addEventListener('change', () => renderResumo());
        q('cadPoderConcedido')?.addEventListener('change', () => {
            const pod = q('cadPoderConcedido') && q('cadPoderConcedido').value;
            if (pod && q('cadDevoto')) q('cadDevoto').checked = true;
            renderResumo();
        });
        q('cadTendencia')?.addEventListener('change', () => renderResumo());
        q('cadClasseMb')?.addEventListener('change', () => {
            if (typeof global.popularCadClasseMbSelect === 'function') {
                global.popularCadClasseMbSelect();
            }
            if (global.T20DashPericiasV13 && global.T20DashPericiasV13.invalidarPericias) {
                global.T20DashPericiasV13.invalidarPericias();
            }
            sincronizarDevotoObrigatorioWizard();
            void carregarKitOpcoes().then(renderUiKit);
            if (global.T20DashStep2V13 && global.T20DashStep2V13.atualizarUiPasso2) {
                global.T20DashStep2V13.atualizarUiPasso2();
            }
        });
        q('cadNivel')?.addEventListener('change', () => {
            renderUiKit();
            if (global.T20DashStep2V13 && global.T20DashStep2V13.atualizarPvSugerido) {
                void global.T20DashStep2V13.atualizarPvSugerido(false);
            }
            if (isWizardAtivo() && stepAtual === PASSO_KIT) {
                renderNav();
            }
        });
        q('cadBtnKitRolarDinheiro')?.addEventListener('click', () => rolarDinheiroKit());
        ['cadKitArmaSimples', 'cadKitArmaMarcial', 'cadKitArmadura', 'cadKitEscudo'].forEach((id) => {
            q(id)?.addEventListener('change', () => renderEquipamentosPreview());
        });
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
        validarAntesCriar,
        lerPayloadOrigemKit,
        lerPayloadCamposPersonagem,
        passoKitAplica,
        mostrarPasso,
        renderResumo,
        renderChecklistRevisao,
        carregarCatalogos,
    };
})(typeof window !== 'undefined' ? window : globalThis);
