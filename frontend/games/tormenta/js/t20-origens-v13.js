/**
 * Origens e devoção v1.3 — catálogo, benefícios e poder concedido.
 */
(function (global) {
    'use strict';

    let ORIGENS_V13 = [];
    let DIVINIDADES_META = [];
    const CLASSES_DEVOTO_OBRIGATORIO = new Set(['clerigo', 'druida', 'paladino']);

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

    function slugParaLabel(slug) {
        return String(slug || '')
            .replace(/_/g, ' ')
            .replace(/\b\w/g, (c) => c.toUpperCase());
    }

    function suplementoAtivo() {
        if (typeof global.t20GetSuplementoFichaAtivo === 'function') {
            return global.t20GetSuplementoFichaAtivo();
        }
        return null;
    }

    async function carregarCatalogos() {
        if (!isV13()) return;
        try {
            const svc = new TormentaRegrasService();
            const sup = suplementoAtivo();
            const [orig, ident] = await Promise.all([
                svc.obterOrigens({ regraVersao: 'v13', suplemento: sup }),
                svc.obterIdentidadeMb(),
            ]);
            ORIGENS_V13 = Array.isArray(orig.origens) ? orig.origens : [];
            DIVINIDADES_META = Array.isArray(ident.divindades) ? ident.divindades : [];
        } catch (_e) {
            ORIGENS_V13 = [];
            DIVINIDADES_META = [];
        }
    }

    function origemPorSlug(slug) {
        const s = String(slug || '').trim().toLowerCase();
        return ORIGENS_V13.find((o) => o.slug === s) || null;
    }

    function divindadePorSlug(slug) {
        const s = String(slug || '').trim().toLowerCase();
        return DIVINIDADES_META.find((d) => d.slug === s) || null;
    }

    function preencherSelectOrigens() {
        const sel = q('f_origem_slug');
        const leg = q('f_origem');
        if (!sel) return;
        const prev = sel.value;
        sel.innerHTML = '<option value="">— Escolha a origem —</option>';
        ORIGENS_V13.forEach((o) => {
            const op = document.createElement('option');
            op.value = o.slug;
            op.textContent = o.nome;
            sel.appendChild(op);
        });
        if (prev) sel.value = prev;
        if (leg && sel.value) {
            const row = origemPorSlug(sel.value);
            if (row) leg.value = row.nome;
        }
    }

    function atualizarUiOrigemItens() {
        const sel = q('f_origem_slug');
        const row = sel ? origemPorSlug(sel.value) : null;
        if (global.T20KitInicialV13) {
            global.T20KitInicialV13.renderOrigemItensLista(row);
            global.T20KitInicialV13.renderOrigemItensEscolha(row);
        }
        if (typeof global.t20AplicarEquipamentosAutomaticosNaLista === 'function') {
            global.t20AplicarEquipamentosAutomaticosNaLista();
        }
    }

    function renderBeneficiosOrigem() {
        const host = q('t20OrigemBeneficiosHost');
        const sel = q('f_origem_slug');
        if (!host || !sel) return;
        const row = origemPorSlug(sel.value);
        if (!row || !isV13()) {
            host.innerHTML = '';
            host.style.display = 'none';
            return;
        }
        host.style.display = '';
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
        const saved = global.__t20OrigemBeneficios || [];
        host.innerHTML =
            '<p class="t20-hint" style="margin:0 0 .35rem">Escolha <strong>2</strong> benefícios da origem:</p>' +
            opts
                .map(
                    (o) =>
                        `<label style="display:block;margin:.15rem 0"><input type="checkbox" class="t20-origem-ben-cb" value="${o.id}" ${saved.includes(o.id) ? 'checked' : ''}/> ${o.label}</label>`
                )
                .join('');
        host.querySelectorAll('.t20-origem-ben-cb').forEach((cb) => {
            cb.addEventListener('change', () => {
                const picks = Array.from(host.querySelectorAll('.t20-origem-ben-cb:checked')).map(
                    (x) => x.value
                );
                if (picks.length > 2) {
                    cb.checked = false;
                    if (typeof Toast !== 'undefined') Toast.error('Máximo 2 benefícios da origem.');
                    return;
                }
                global.__t20OrigemBeneficios = picks;
                if (typeof global.t20AplicarPericiasOrigemBeneficios === 'function') {
                    global.t20AplicarPericiasOrigemBeneficios();
                }
                if (global.T20OrigemTrocasFichaV13 && global.T20OrigemTrocasFichaV13.renderUi) {
                    global.T20OrigemTrocasFichaV13.renderUi();
                }
                if (typeof global.t20AplicarPoderesAutomaticosNaLista === 'function') {
                    global.t20AplicarPoderesAutomaticosNaLista();
                }
                atualizarUiOrigemItens();
            });
        });
        atualizarUiOrigemItens();
    }

    function classeExigeDevocao() {
        const sel = q('f_classe_mb');
        const slug = sel ? String(sel.value || '').trim().toLowerCase() : '';
        return CLASSES_DEVOTO_OBRIGATORIO.has(slug);
    }

    function sincronizarDevotoObrigatorio() {
        const exige = classeExigeDevocao();
        const cb = q('f_devoto');
        if (exige && cb) cb.checked = true;
        const hint = q('t20DevocaoHint');
        if (hint) {
            let txt = exige
                ? 'Clérigo, druida e paladino devem escolher divindade e poder concedido.'
                : 'Devoção opcional: marque Devoto e escolha um poder da divindade (Os Vinte).';
            if (String((q('f_classe_mb') && q('f_classe_mb').value) || '').toLowerCase() === 'paladino') {
                txt += ' Paladinos são campeões do bem e da ordem (narrativo).';
            }
            hint.textContent = txt;
        }
        return exige;
    }

    function renderObrigacoesDivindade(row, hostId) {
        const host = q(hostId);
        if (!host) return;
        if (!row || !isV13()) {
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
        const lista = flags
            .map((f) => `<li>${String(f.rotulo || f.slug || '').trim()}</li>`)
            .join('');
        const nimb = row.sem_penalidade_obrigacao
            ? '<p class="t20-hint t20-obrig-nimb" style="margin:.35rem 0 0">Nimb: violar O&R não causa perda de PM.</p>'
            : '';
        host.innerHTML =
            `<p class="t20-hint" style="margin:0 0 .35rem"><strong>Obrigações & Restrições</strong>${pag}</p>` +
            `<ul class="t20-obrig-list">${lista}</ul>` +
            nimb;
    }

    function atualizarPoderesConcedidos() {
        const selDiv = q('f_divindade');
        const selPod = q('f_poder_concedido');
        if (!selPod) return;
        const slug =
            selDiv && selDiv.selectedOptions && selDiv.selectedOptions[0]
                ? selDiv.selectedOptions[0].getAttribute('data-slug')
                : '';
        const row = divindadePorSlug(slug);
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
        if (prev) selPod.value = prev;
        const wrap = q('wrapPoderConcedido');
        if (wrap) wrap.style.display = isV13() ? '' : 'none';
        renderObrigacoesDivindade(row, 't20DivindadeObrigacoesHost');
        sincronizarDevotoObrigatorio();
    }

    function atualizarUiOrigemV13() {
        const v13 = isV13();
        const wrapSlug = q('wrapOrigemSlug');
        const wrapBen = q('wrapOrigemBeneficios');
        const wrapDev = q('wrapDevoto');
        const wrapHint = q('wrapDevocaoHint');
        if (wrapSlug) wrapSlug.style.display = v13 ? '' : 'none';
        if (wrapBen) wrapBen.style.display = v13 ? '' : 'none';
        if (wrapDev) wrapDev.style.display = v13 ? '' : 'none';
        if (wrapHint) wrapHint.style.display = v13 ? '' : 'none';
        const leg = q('f_origem');
        if (leg) leg.style.display = v13 ? 'none' : '';
        if (v13) {
            preencherSelectOrigens();
            renderBeneficiosOrigem();
            atualizarUiOrigemItens();
            atualizarPoderesConcedidos();
        }
    }

    function lerOrigemPayload() {
        if (!isV13()) {
            return {
                origem: q('f_origem') ? q('f_origem').value || '' : '',
            };
        }
        const slug = q('f_origem_slug') ? q('f_origem_slug').value : '';
        const row = origemPorSlug(slug);
        const trocasPayload =
            global.T20OrigemTrocasFichaV13 && global.T20OrigemTrocasFichaV13.lerPayload
                ? global.T20OrigemTrocasFichaV13.lerPayload()
                : {};
        return {
            origem: row ? row.nome : q('f_origem') ? q('f_origem').value || '' : '',
            origem_slug: slug || null,
            origem_beneficios: Array.isArray(global.__t20OrigemBeneficios)
                ? global.__t20OrigemBeneficios.slice()
                : [],
            ...(trocasPayload.origem_trocas_pericia
                ? { origem_trocas_pericia: trocasPayload.origem_trocas_pericia }
                : {}),
            origem_itens_escolha:
                global.__t20OrigemItensEscolha && typeof global.__t20OrigemItensEscolha === 'object'
                    ? { ...global.__t20OrigemItensEscolha }
                    : {},
            poder_concedido_slug:
                q('f_poder_concedido') && q('f_poder_concedido').value
                    ? String(q('f_poder_concedido').value).trim()
                    : null,
            devoto: !!(q('f_devoto') && q('f_devoto').checked) || classeExigeDevocao(),
        };
    }

    function aplicarOrigemPayload(fj) {
        if (!fj || typeof fj !== 'object') return;
        global.__t20OrigemBeneficios = Array.isArray(fj.origem_beneficios)
            ? fj.origem_beneficios.slice()
            : [];
        global.__t20OrigemItensEscolha =
            fj.origem_itens_escolha && typeof fj.origem_itens_escolha === 'object'
                ? { ...fj.origem_itens_escolha }
                : {};
        if (global.T20OrigemTrocasFichaV13 && global.T20OrigemTrocasFichaV13.aplicarPayload) {
            global.T20OrigemTrocasFichaV13.aplicarPayload(fj);
        }
        if (isV13()) {
            preencherSelectOrigens();
            atualizarPoderesConcedidos();
        }
        if (q('f_origem_slug') && fj.origem_slug) q('f_origem_slug').value = fj.origem_slug;
        if (q('f_origem') && fj.origem) q('f_origem').value = fj.origem;
        if (q('f_poder_concedido') && fj.poder_concedido_slug) {
            q('f_poder_concedido').value = fj.poder_concedido_slug;
        }
        if (q('f_devoto')) q('f_devoto').checked = !!fj.devoto;
        renderBeneficiosOrigem();
        if (typeof global.t20AplicarPericiasOrigemBeneficios === 'function') {
            global.t20AplicarPericiasOrigemBeneficios();
        }
        if (typeof global.t20AplicarPoderesAutomaticosNaLista === 'function') {
            global.t20AplicarPoderesAutomaticosNaLista();
        }
        if (global.T20OrigemTrocasFichaV13 && global.T20OrigemTrocasFichaV13.renderUi) {
            global.T20OrigemTrocasFichaV13.renderUi();
        }
    }

    function wireEvents() {
        if (global.__t20OrigensV13Bound) return;
        global.__t20OrigensV13Bound = true;
        q('f_origem_slug')?.addEventListener('change', () => {
            const row = origemPorSlug(q('f_origem_slug').value);
            if (q('f_origem') && row) q('f_origem').value = row.nome;
            global.__t20OrigemBeneficios = [];
            global.__t20OrigemTrocasPericia = {};
            renderBeneficiosOrigem();
            atualizarUiOrigemItens();
            if (typeof global.t20AplicarPericiasOrigemBeneficios === 'function') {
                global.t20AplicarPericiasOrigemBeneficios();
            }
            if (global.T20OrigemTrocasFichaV13 && global.T20OrigemTrocasFichaV13.renderUi) {
                global.T20OrigemTrocasFichaV13.renderUi();
            }
            if (typeof global.t20AplicarPoderesAutomaticosNaLista === 'function') {
                global.t20AplicarPoderesAutomaticosNaLista();
            }
        });
        q('f_divindade')?.addEventListener('change', () => {
            atualizarPoderesConcedidos();
            if (typeof global.t20AplicarPoderesAutomaticosNaLista === 'function') {
                global.t20AplicarPoderesAutomaticosNaLista();
            }
        });
        q('f_poder_concedido')?.addEventListener('change', () => {
            const pod = q('f_poder_concedido') && q('f_poder_concedido').value;
            if (pod && q('f_devoto')) q('f_devoto').checked = true;
            if (typeof global.t20AplicarPoderesAutomaticosNaLista === 'function') {
                global.t20AplicarPoderesAutomaticosNaLista();
            }
        });
        q('f_devoto')?.addEventListener('change', sincronizarDevotoObrigatorio);
        q('f_classe_mb')?.addEventListener('change', () => {
            sincronizarDevotoObrigatorio();
            atualizarPoderesConcedidos();
        });
    }

    async function init() {
        wireEvents();
        await carregarCatalogos();
        atualizarUiOrigemV13();
    }

    global.T20OrigensV13 = {
        init,
        carregarCatalogos,
        atualizarUiOrigemV13,
        lerOrigemPayload,
        aplicarOrigemPayload,
        atualizarPoderesConcedidos,
        renderObrigacoesDivindade,
        origemPorSlug,
        classeExigeDevocao,
        sincronizarDevotoObrigatorio,
    };
})(typeof window !== 'undefined' ? window : globalThis);
