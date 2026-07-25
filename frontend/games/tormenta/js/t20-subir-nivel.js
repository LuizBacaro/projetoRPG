/**
 * Assistente «Subir nível» — 3 passos (quem sobe → o que muda → confirmar).
 */
(function () {
    const svc = () => new TormentaPersonagemService();

    let passo = 1;
    let previewCache = null;

    function q(id) {
        return document.getElementById(id);
    }

    function escHtml(s) {
        if (typeof window.escHtml === 'function') return window.escHtml(s);
        const d = document.createElement('div');
        d.textContent = s == null ? '' : String(s);
        return d.innerHTML;
    }

    function labelVersao() {
        if (typeof window.t20LabelVersao === 'function') return window.t20LabelVersao();
        if (window.T20RegraVersao && typeof window.getRegraVersaoAtiva === 'function') {
            return window.T20RegraVersao.isV13(window.getRegraVersaoAtiva()) ? 'v1.3' : 'MB';
        }
        return 'MB';
    }

    function isV13() {
        return labelVersao() === 'v1.3';
    }

    function nivelAtual() {
        const nv = Math.floor(Number((q('f_nivel') && q('f_nivel').value) || '1'));
        return Number.isFinite(nv) && nv >= 0 ? nv : 1;
    }

    function nivelAlvo() {
        return Math.min(40, Math.max(1, nivelAtual() + 1));
    }

    function classePrincipalSlug() {
        const sel = q('f_classe_mb');
        return sel && sel.value ? String(sel.value).trim().toLowerCase() : '';
    }

    function labelClasse(slug) {
        const s = String(slug || '').trim().toLowerCase();
        if (!s) return '—';
        const cat =
            window.T20MulticlasseV13 && typeof window.T20MulticlasseV13.catalogoClasses === 'function'
                ? window.T20MulticlasseV13.catalogoClasses()
                : [];
        const row = (cat || []).find((c) => String(c.slug || '').toLowerCase() === s);
        if (row && window.T20ClassesVariantesV13 && typeof window.T20ClassesVariantesV13.labelClasseMb === 'function') {
            return window.T20ClassesVariantesV13.labelClasseMb(row);
        }
        if (row && row.nome) return String(row.nome);
        return s.charAt(0).toUpperCase() + s.slice(1).replace(/_/g, ' ');
    }

    function linhasMulticlasseEfetivas() {
        if (window.T20MulticlasseV13 && typeof window.T20MulticlasseV13.niveisEfetivosParaPm === 'function') {
            return window.T20MulticlasseV13.niveisEfetivosParaPm() || [];
        }
        const slug = classePrincipalSlug();
        if (!slug) return [];
        return [{ slug, nivel: Math.max(1, nivelAtual()) }];
    }

    function motivoBloqueio() {
        const pid = q('fichaId') && q('fichaId').value;
        if (!pid) return 'Salve a ficha antes de subir de nível.';
        if (!String(classePrincipalSlug()).trim()) {
            return `Escolha a classe (${labelVersao()}) em Editar ficha.`;
        }
        if (nivelAtual() >= 40) return 'Nível máximo (40) já atingido.';
        return '';
    }

    function atualizarBotoesEntrada() {
        const motivo = motivoBloqueio();
        const nv = nivelAlvo();
        const texto = motivo ? `⬆ Subir nível` : `⬆ Subir para o nível ${nv}`;
        const title = motivo || `Aplicar nível ${nv} (${labelVersao()}) — PV, PM e benefícios`;
        ['btnT20SubirNivelMb', 'btnT20SubirNivelMbDlg', 'btnT20SubirNivelMbRodape'].forEach((id) => {
            const btn = q(id);
            if (!btn) return;
            btn.textContent = texto;
            btn.title = title;
            btn.disabled = !!motivo;
            btn.setAttribute('aria-disabled', motivo ? 'true' : 'false');
        });
        const tit = q('tituloModalSubirNivel');
        if (tit) tit.textContent = `Subir nível (${labelVersao()})`;
        const lead = q('subirNivelLead');
        if (lead) {
            lead.textContent = isV13()
                ? 'v1.3 — escolha a classe, revise ganhos e confirme.'
                : 'MB — revise ganhos do próximo nível e confirme.';
        }
    }

    function fecharModal() {
        const ov = q('modalSubirNivelTormenta');
        if (!ov) return;
        ov.classList.remove('is-open');
        ov.setAttribute('aria-hidden', 'true');
        passo = 1;
        previewCache = null;
    }

    function classeAlvoSelecionada() {
        const checked = document.querySelector('input[name="subirNivelClasseRadio"]:checked');
        if (checked && checked.value) return String(checked.value).trim().toLowerCase();
        const sel = q('subirNivelClasseAlvo');
        if (sel && sel.value) return String(sel.value).trim().toLowerCase();
        return classePrincipalSlug();
    }

    function montarOpcoesClasse() {
        const host = q('subirNivelClasseOpcoes');
        const hint = q('subirNivelHintClasse');
        if (!host) return;

        const prefer =
            (window.__t20SubirNivelClassePick && String(window.__t20SubirNivelClassePick).trim().toLowerCase()) ||
            classePrincipalSlug();

        if (!isV13()) {
            if (hint) hint.textContent = 'A classe da ficha sobe +1 nível.';
            const slug = classePrincipalSlug();
            host.innerHTML = `<div class="t20-subir-nivel-card t20-subir-nivel-card--static">
                <strong>${escHtml(labelClasse(slug))}</strong>
                <span class="t20-hint">Nível de personagem ${nivelAtual()} → ${nivelAlvo()}</span>
            </div>`;
            return;
        }

        if (hint) {
            hint.textContent = 'Qual classe recebe este nível? (multiclasse: pode continuar uma existente ou iniciar outra.)';
        }

        const linhas = linhasMulticlasseEfetivas();
        const existentes = new Set(linhas.map((r) => String(r.slug || '').trim().toLowerCase()).filter(Boolean));
        const parts = [];

        linhas.forEach((r, idx) => {
            const s = String(r.slug || '').trim().toLowerCase();
            if (!s) return;
            const nv = r.nivel != null ? Number(r.nivel) : 1;
            const id = `subirNivelCls_${s}_${idx}`;
            const sel = s === prefer || (!prefer && idx === 0);
            parts.push(`<label class="t20-subir-nivel-card${sel ? ' is-selected' : ''}" for="${id}">
                <input type="radio" name="subirNivelClasseRadio" id="${id}" value="${escHtml(s)}"${sel ? ' checked' : ''} />
                <span class="t20-subir-nivel-card__body">
                    <strong>${escHtml(labelClasse(s))}</strong>
                    <span class="t20-hint">Continuar · nv ${nv} → ${nv + 1}</span>
                </span>
            </label>`);
        });

        const cat =
            window.T20MulticlasseV13 && typeof window.T20MulticlasseV13.catalogoClasses === 'function'
                ? window.T20MulticlasseV13.catalogoClasses()
                : [];
        const novas = (cat || [])
            .map((c) => String(c.slug || '').trim().toLowerCase())
            .filter((s) => s && !existentes.has(s));

        if (novas.length) {
            parts.push('<p class="t20-subir-nivel-secao-lbl">Ou iniciar nova classe</p>');
            const selOpts = novas
                .map((s) => {
                    const sel = s === prefer && !existentes.has(prefer);
                    return `<option value="${escHtml(s)}"${sel ? ' selected' : ''}>${escHtml(labelClasse(s))}</option>`;
                })
                .join('');
            const novaId = 'subirNivelCls_nova';
            const novaChecked = prefer && !existentes.has(prefer);
            parts.push(`<label class="t20-subir-nivel-card${novaChecked ? ' is-selected' : ''}" for="${novaId}">
                <input type="radio" name="subirNivelClasseRadio" id="${novaId}" value="__nova__"${novaChecked ? ' checked' : ''} />
                <span class="t20-subir-nivel-card__body">
                    <strong>Nova classe (1º nível)</strong>
                    <select id="subirNivelClasseNovaSelect" class="t20-input" ${novaChecked ? '' : 'disabled'}>${selOpts}</select>
                </span>
            </label>`);
        }

        if (!parts.length) {
            const pri = classePrincipalSlug();
            parts.push(`<label class="t20-subir-nivel-card is-selected" for="subirNivelCls_pri">
                <input type="radio" name="subirNivelClasseRadio" id="subirNivelCls_pri" value="${escHtml(pri)}" checked />
                <span class="t20-subir-nivel-card__body"><strong>${escHtml(labelClasse(pri))}</strong></span>
            </label>`);
        }

        host.innerHTML = parts.join('');
        host.querySelectorAll('input[name="subirNivelClasseRadio"]').forEach((inp) => {
            inp.addEventListener('change', () => {
                host.querySelectorAll('.t20-subir-nivel-card').forEach((c) => c.classList.remove('is-selected'));
                const lab = inp.closest('.t20-subir-nivel-card');
                if (lab) lab.classList.add('is-selected');
                const novaSel = q('subirNivelClasseNovaSelect');
                if (novaSel) novaSel.disabled = inp.value !== '__nova__';
                previewCache = null;
            });
        });
        const novaSel = q('subirNivelClasseNovaSelect');
        if (novaSel) {
            novaSel.addEventListener('change', () => {
                previewCache = null;
            });
        }
    }

    function resolverClasseSlug() {
        if (!isV13()) return classePrincipalSlug();
        const checked = document.querySelector('input[name="subirNivelClasseRadio"]:checked');
        if (!checked) return classePrincipalSlug();
        if (checked.value === '__nova__') {
            const sel = q('subirNivelClasseNovaSelect');
            return sel && sel.value ? String(sel.value).trim().toLowerCase() : '';
        }
        return String(checked.value).trim().toLowerCase();
    }

    function cardHtml(titulo, corpo, tom) {
        const cls = tom ? ` t20-subir-nivel-stat--${tom}` : '';
        return `<article class="t20-subir-nivel-stat${cls}">
            <h3 class="t20-subir-nivel-stat__t">${escHtml(titulo)}</h3>
            <div class="t20-subir-nivel-stat__b">${corpo}</div>
        </article>`;
    }

    function montarHtmlPreview(p) {
        if (!p) return '<p class="t20-hint">Sem dados.</p>';
        if (!p.permitido) {
            return `<div class="t20-subir-nivel-erro">${escHtml(p.motivo || 'Não permitido.')}</div>`;
        }
        const lv = labelVersao();
        const cards = [];

        cards.push(
            cardHtml(
                'Nível',
                `<p class="t20-subir-nivel-delta"><strong>${p.nivel_atual}</strong> → <strong>${p.nivel_alvo}</strong></p>
                <p class="t20-hint">${escHtml(labelClasse(p.classe_slug || resolverClasseSlug()))}${
                    p.classe_nivel_atual != null && p.classe_nivel_novo != null
                        ? ` · classe ${p.classe_nivel_atual}→${p.classe_nivel_novo}`
                        : ''
                }</p>${
                    p.classe_nova_multiclasse
                        ? '<p class="t20-hint">Nova classe na multiclasse (PV = ganho subsequente).</p>'
                        : ''
                }`
            )
        );

        if (p.pv_ganho != null) {
            cards.push(
                cardHtml(
                    'Pontos de vida',
                    `<p class="t20-subir-nivel-delta">${p.pv_max_atual} → <strong>${p.pv_max_novo}</strong> <span class="t20-subir-nivel-plus">+${p.pv_ganho}</span></p>`,
                    'pv'
                )
            );
        }

        if (p.pa_ganho != null && p.pa_ganho > 0) {
            cards.push(
                cardHtml(
                    'Pontos de mana',
                    `<p class="t20-subir-nivel-delta">${p.pa_max_atual} → <strong>${p.pa_max_novo}</strong> <span class="t20-subir-nivel-plus">+${p.pa_ganho}</span></p>`,
                    'pm'
                )
            );
        } else if (p.pa_max_novo != null && p.pa_max_atual != null && p.pa_max_novo !== p.pa_max_atual) {
            cards.push(
                cardHtml(
                    'Pontos de mana',
                    `<p class="t20-subir-nivel-delta">${p.pa_max_atual} → <strong>${p.pa_max_novo}</strong></p>`,
                    'pm'
                )
            );
        }

        if (p.talentos_ganho > 0) {
            const rotulo = lv === 'v1.3' ? 'Poderes gerais' : 'Talentos';
            cards.push(
                cardHtml(
                    rotulo,
                    `<p>Total acumulado: <strong>${p.talentos_totais_novo}</strong> <span class="t20-subir-nivel-plus">+${p.talentos_ganho}</span> neste nível</p>
                    <p class="t20-hint">Escolha o poder na ficha após confirmar.</p>`
                )
            );
        }

        if (p.graduacao_pericias_nova) {
            const rotGrad = lv === 'v1.3' ? 'Bônus em perícias' : 'Graduações de perícias';
            cards.push(cardHtml(rotGrad, `<p><strong>${escHtml(p.graduacao_pericias_nova)}</strong></p>`));
        }

        const magias = [];
        if (p.magias_livro_ganho != null && p.magias_livro_ganho > 0) {
            magias.push(
                `Livro do mago: +${p.magias_livro_ganho} magia(s) (teto ${p.magias_livro_max_novo}).`
            );
        }
        if (p.magias_conhecidas_max_novo != null) {
            magias.push(`Conhecidas (teto): ${p.magias_conhecidas_max_novo}.`);
        }
        if (p.magias_preparadas_teto_novo != null) {
            magias.push(`Preparadas/dia (teto): ${p.magias_preparadas_teto_novo}.`);
        }
        if (p.bardo_pode_trocar_magia) {
            magias.push('Bardo: pode trocar uma magia conhecida neste nível.');
        }
        if (magias.length) {
            cards.push(cardHtml('Magias', `<ul class="t20-subir-nivel-lista">${magias.map((m) => `<li>${escHtml(m)}</li>`).join('')}</ul>`));
        }

        if (p.habilidade_classe) {
            cards.push(
                cardHtml(
                    `Poder / habilidade de classe (${lv})`,
                    `<p>${escHtml(p.habilidade_classe)}</p>`,
                    'hab'
                )
            );
        }

        if (isV13()) {
            cards.push(
                cardHtml(
                    'Atributos',
                    '<p class="t20-hint">Não mudam ao subir de nível na escala v1.3.</p>'
                )
            );
        }

        let avisos = '';
        if (Array.isArray(p.avisos) && p.avisos.length) {
            avisos = `<aside class="t20-subir-nivel-avisos"><strong>Avisos</strong><p>${escHtml(p.avisos.join(' '))}</p></aside>`;
        }

        return `<div class="t20-subir-nivel-grid">${cards.join('')}</div>${avisos}`;
    }

    function montarChecklistPos(p) {
        const ul = q('subirNivelChecklistPos');
        if (!ul) return;
        const items = [];
        if (p && p.talentos_ganho > 0) {
            items.push(isV13() ? 'Escolher o poder geral ganho (modal Poderes).' : 'Escolher o talento ganho.');
        }
        if (p && p.magias_livro_ganho > 0) {
            items.push('Aprender magia(s) no grimório / livro.');
        }
        if (p && p.bardo_pode_trocar_magia) {
            items.push('Se quiser, trocar uma magia conhecida (bardo).');
        }
        if (p && p.habilidade_classe) {
            items.push('Conferir o poder de classe deste nível na ficha.');
        }
        items.push('Salvar a ficha se fizer mais ajustes.');
        ul.innerHTML = items.map((t) => `<li>${escHtml(t)}</li>`).join('');
    }

    function montarResumoFinal(p) {
        const el = q('subirNivelResumoFinal');
        if (!el || !p) return;
        const cls = labelClasse(p.classe_slug || resolverClasseSlug());
        el.innerHTML = `
            <p class="t20-subir-nivel-resumo-final__titulo">Confirmar subida</p>
            <p><strong>Nível ${p.nivel_atual} → ${p.nivel_alvo}</strong> · ${escHtml(cls)}</p>
            <ul class="t20-subir-nivel-lista">
                ${p.pv_ganho != null ? `<li>PV máx. +${p.pv_ganho} → ${p.pv_max_novo}</li>` : ''}
                ${p.pa_ganho > 0 ? `<li>PM máx. +${p.pa_ganho} → ${p.pa_max_novo}</li>` : ''}
                ${p.talentos_ganho > 0 ? `<li>+${p.talentos_ganho} poder(es)/talento(s)</li>` : ''}
            </ul>`;
    }

    function atualizarHeroNivel() {
        const de = q('subirNivelHeroNivel') && q('subirNivelHeroNivel').querySelector('.t20-subir-nivel-hero__de');
        const para = q('subirNivelHeroNivel') && q('subirNivelHeroNivel').querySelector('.t20-subir-nivel-hero__para');
        if (de) de.textContent = `Nível ${nivelAtual()}`;
        if (para) para.textContent = `Nível ${nivelAlvo()}`;
    }

    function setPasso(n) {
        passo = Math.max(1, Math.min(3, n));
        [1, 2, 3].forEach((i) => {
            const painel = q(`subirNivelPainel${i}`);
            const tab = q(`subirNivelStepTab${i}`);
            if (painel) {
                const ativo = i === passo;
                painel.hidden = !ativo;
                painel.classList.toggle('is-active', ativo);
            }
            if (tab) {
                tab.classList.toggle('is-active', i === passo);
                tab.classList.toggle('is-done', i < passo);
                tab.disabled = i > passo && !(i === 2 && previewCache && previewCache.permitido);
            }
        });
        const btnVoltar = q('btnSubirNivelVoltar');
        const btnAvancar = q('btnSubirNivelAvancar');
        const btnConf = q('btnSubirNivelConfirmar');
        if (btnVoltar) btnVoltar.hidden = passo === 1;
        if (btnAvancar) {
            btnAvancar.hidden = passo === 3;
            btnAvancar.textContent = passo === 1 ? 'Ver o que muda' : 'Revisar e confirmar';
            btnAvancar.disabled = false;
        }
        if (btnConf) {
            btnConf.hidden = passo !== 3;
            btnConf.disabled = !(previewCache && previewCache.permitido);
            if (previewCache && previewCache.nivel_alvo != null) {
                btnConf.textContent = `Confirmar nível ${previewCache.nivel_alvo}`;
            } else {
                btnConf.textContent = `Confirmar nível ${nivelAlvo()}`;
            }
        }
    }

    async function carregarPreview() {
        const corpo = q('subirNivelTormentaCorpo');
        const pid = q('fichaId') && q('fichaId').value;
        if (!corpo || !pid) return null;
        const slug = resolverClasseSlug();
        if (!slug) {
            corpo.innerHTML = '<div class="t20-subir-nivel-erro">Selecione a classe que sobe.</div>';
            return null;
        }
        window.__t20SubirNivelClassePick = slug;
        corpo.innerHTML = '<p class="t20-hint t20-subir-nivel-loading">Calculando ganhos…</p>';
        try {
            const opts = {};
            if (isV13()) opts.classeSlug = slug;
            const p = await svc().previewSubirNivel(pid, nivelAlvo(), opts);
            previewCache = p;
            window.__t20SubirNivelPreview = p;
            corpo.innerHTML = montarHtmlPreview(p);
            montarChecklistPos(p);
            montarResumoFinal(p);
            const btn = q('btnSubirNivelConfirmar');
            if (btn) btn.disabled = !(p && p.permitido);
            return p;
        } catch (e) {
            previewCache = null;
            corpo.innerHTML = `<div class="t20-subir-nivel-erro">${escHtml(e.message || 'Erro ao carregar preview')}</div>`;
            const btn = q('btnSubirNivelConfirmar');
            if (btn) btn.disabled = true;
            return null;
        }
    }

    async function avancar() {
        if (passo === 1) {
            const p = await carregarPreview();
            if (!p || !p.permitido) {
                setPasso(2);
                return;
            }
            setPasso(2);
            return;
        }
        if (passo === 2) {
            if (!previewCache) await carregarPreview();
            if (previewCache) {
                montarResumoFinal(previewCache);
                montarChecklistPos(previewCache);
            }
            setPasso(3);
        }
    }

    function voltar() {
        if (passo > 1) setPasso(passo - 1);
    }

    async function abrirModal() {
        atualizarBotoesEntrada();
        const motivo = motivoBloqueio();
        if (motivo) {
            if (typeof Toast !== 'undefined') Toast.error(motivo);
            else alert(motivo);
            return;
        }
        if (isV13() && window.T20MulticlasseV13 && typeof window.T20MulticlasseV13.carregarSlugsClasses === 'function') {
            await window.T20MulticlasseV13.carregarSlugsClasses();
        }
        const ov = q('modalSubirNivelTormenta');
        if (ov) {
            ov.classList.add('is-open');
            ov.setAttribute('aria-hidden', 'false');
        }
        const chk = q('subirNivelAplicarPv');
        if (chk) chk.checked = true;
        previewCache = null;
        atualizarHeroNivel();
        montarOpcoesClasse();
        setPasso(1);
        const first = document.querySelector('#subirNivelClasseOpcoes input[type="radio"]');
        if (first && typeof first.focus === 'function') {
            setTimeout(() => first.focus(), 50);
        }
    }

    async function confirmarSubirNivel() {
        const pid = q('fichaId') && q('fichaId').value;
        const prev = previewCache || window.__t20SubirNivelPreview;
        const lv = labelVersao();
        if (!pid || !prev) {
            if (typeof Toast !== 'undefined') Toast.error('Revise os ganhos antes de confirmar.');
            return;
        }
        if (!prev.permitido) {
            if (typeof Toast !== 'undefined') Toast.error(prev.motivo || 'Subida de nível não permitida.');
            return;
        }
        const btn = q('btnSubirNivelConfirmar');
        if (btn) {
            btn.disabled = true;
            btn.textContent = 'Aplicando…';
        }
        const aplicarPv = !!(q('subirNivelAplicarPv') && q('subirNivelAplicarPv').checked);
        const body = { aplicar_ganhos_vida: aplicarPv };
        if (isV13()) {
            body.classe_slug = resolverClasseSlug() || prev.classe_slug || undefined;
        }
        try {
            const res = await svc().aplicarSubirNivel(pid, body);
            const p = res.personagem;
            if (typeof window.t20PreencherFormPersonagem === 'function') {
                window.t20PreencherFormPersonagem(p);
            } else {
                if (q('f_nivel')) q('f_nivel').value = String(p.nivel);
                if (typeof window.t20WritePairSlash === 'function') {
                    window.t20WritePairSlash('fichaPv', p.pv_atual, p.pv_max);
                    window.t20WritePairSlash('fichaPm', p.pa_atual, p.pa_max);
                }
            }
            if (window.T20MulticlasseV13 && typeof window.T20MulticlasseV13.aplicarPayload === 'function') {
                window.T20MulticlasseV13.aplicarPayload(p.ficha_json || {});
            }
            if (typeof window.atualizarResumoClasseMb === 'function') {
                window.atualizarResumoClasseMb();
            }
            if (typeof Toast !== 'undefined') Toast.success(`Nível ${p.nivel} aplicado (${lv}).`);
            fecharModal();
            atualizarBotoesEntrada();
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro ao subir de nível');
            else alert(e.message || 'Erro');
            if (btn) {
                btn.disabled = false;
                btn.textContent = `Confirmar nível ${nivelAlvo()}`;
            }
        }
    }

    function init() {
        ['btnT20SubirNivelMb', 'btnT20SubirNivelMbDlg', 'btnT20SubirNivelMbRodape'].forEach((id) => {
            q(id)?.addEventListener('click', () => abrirModal());
        });
        q('btnSubirNivelConfirmar')?.addEventListener('click', () => confirmarSubirNivel());
        q('btnSubirNivelAvancar')?.addEventListener('click', () => avancar());
        q('btnSubirNivelVoltar')?.addEventListener('click', () => voltar());
        q('btnFecharModalSubirNivel')?.addEventListener('click', () => fecharModal());
        q('btnFecharModalSubirNivel2')?.addEventListener('click', () => fecharModal());
        const ov = q('modalSubirNivelTormenta');
        if (ov) {
            ov.addEventListener('click', (e) => {
                if (e.target === ov) fecharModal();
            });
        }
        document.addEventListener('keydown', (e) => {
            if (e.key !== 'Escape') return;
            const modal = q('modalSubirNivelTormenta');
            if (modal && modal.classList.contains('is-open')) {
                e.preventDefault();
                fecharModal();
            }
        });
        q('f_nivel')?.addEventListener('change', () => atualizarBotoesEntrada());
        q('f_classe_mb')?.addEventListener('change', () => atualizarBotoesEntrada());
        atualizarBotoesEntrada();
        // Reavalia após carregar ficha
        const idEl = q('fichaId');
        if (idEl) {
            const obs = new MutationObserver(() => atualizarBotoesEntrada());
            obs.observe(idEl, { attributes: true, attributeFilter: ['value'] });
        }
        setTimeout(atualizarBotoesEntrada, 800);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window.t20AbrirModalSubirNivelMb = abrirModal;
    window.t20AtualizarBotoesSubirNivel = atualizarBotoesEntrada;
})();
