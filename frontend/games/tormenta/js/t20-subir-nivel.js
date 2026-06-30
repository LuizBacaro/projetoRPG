/**
 * Wizard «Subir nível» — preview e aplicação via API (MB ou v1.3).
 */
(function () {
    const svc = () => new TormentaPersonagemService();

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

    function fecharModal() {
        const ov = q('modalSubirNivelTormenta');
        if (!ov) return;
        ov.classList.remove('is-open');
        ov.setAttribute('aria-hidden', 'true');
    }

    function classePrincipalSlug() {
        const sel = q('f_classe_mb');
        return sel && sel.value ? String(sel.value).trim().toLowerCase() : '';
    }

    function linhasMulticlasseEfetivas() {
        if (window.T20MulticlasseV13 && typeof window.T20MulticlasseV13.niveisEfetivosParaPm === 'function') {
            return window.T20MulticlasseV13.niveisEfetivosParaPm() || [];
        }
        const slug = classePrincipalSlug();
        if (!slug) return [];
        const nv = Math.floor(Number((q('f_nivel') && q('f_nivel').value) || '1'));
        return [{ slug, nivel: Number.isFinite(nv) && nv >= 1 ? nv : 1 }];
    }

    function montarSelectClasseAlvo() {
        if (!isV13()) return '';
        const prefer =
            (window.__t20SubirNivelClassePick && String(window.__t20SubirNivelClassePick).trim().toLowerCase()) ||
            classeAlvoSelecionada() ||
            classePrincipalSlug();
        const linhas = linhasMulticlasseEfetivas();
        const slugsExistentes = new Set(linhas.map((r) => String(r.slug || '').trim().toLowerCase()).filter(Boolean));
        const opts = [];
        linhas.forEach((r) => {
            const s = String(r.slug || '').trim().toLowerCase();
            if (!s) return;
            const nv = r.nivel != null ? r.nivel : 1;
            opts.push(
                `<option value="${escHtml(s)}"${s === prefer ? ' selected' : ''}>${escHtml(s)} (nv ${nv} → ${Number(nv) + 1})</option>`
            );
        });
        const slugsV13 =
            window.T20MulticlasseV13 && Array.isArray(window.T20MulticlasseV13._slugsCache)
                ? window.T20MulticlasseV13._slugsCache
                : [];
        slugsV13.forEach((s) => {
            const slug = String(s || '').trim().toLowerCase();
            if (!slug || slugsExistentes.has(slug)) return;
            opts.push(
                `<option value="${escHtml(slug)}"${slug === prefer ? ' selected' : ''}>${escHtml(slug)} (nova classe, 1º nível)</option>`
            );
        });
        if (!opts.length) {
            const pri = classePrincipalSlug();
            if (pri) {
                opts.push(`<option value="${escHtml(pri)}" selected>${escHtml(pri)}</option>`);
            }
        }
        return `<label class="t20-hint" style="display:block;margin:0 0 .65rem">Classe que sobe +1 (multiclasse v1.3)
            <select id="subirNivelClasseAlvo" class="t20-input" style="width:100%;margin-top:.25rem">${opts.join('')}</select>
        </label>`;
    }

    function classeAlvoSelecionada() {
        const sel = q('subirNivelClasseAlvo');
        if (sel && sel.value) return String(sel.value).trim().toLowerCase();
        return classePrincipalSlug();
    }

    function montarHtmlPreview(p) {
        if (!p) return '<p class="t20-hint">Sem dados.</p>';
        if (!p.permitido) {
            return `<p class="t20-hint" style="color:var(--t20-danger,#a33)">${escHtml(p.motivo || 'Não permitido.')}</p>`;
        }
        const lv = labelVersao();
        const linhas = [];
        if (isV13()) {
            linhas.push(montarSelectClasseAlvo());
        }
        const clsTxt = p.classe_slug || '';
        const nvCls =
            p.classe_nivel_atual != null && p.classe_nivel_novo != null
                ? ` · ${escHtml(clsTxt)} ${p.classe_nivel_atual}→${p.classe_nivel_novo}`
                : clsTxt
                  ? ` (${escHtml(clsTxt)})`
                  : '';
        linhas.push(`<p><strong>Nível total ${p.nivel_atual} → ${p.nivel_alvo}</strong>${nvCls}</p>`);
        if (p.classe_nova_multiclasse) {
            linhas.push('<p class="t20-hint">Nova classe na multiclasse (PV = ganho subsequente, p.34).</p>');
        }
        if (p.pv_ganho != null) {
            linhas.push(`<p>PV: ${p.pv_max_atual} → <strong>${p.pv_max_novo}</strong> (+${p.pv_ganho})</p>`);
        }
        if (p.pa_ganho != null && p.pa_ganho > 0) {
            linhas.push(`<p>PM: ${p.pa_max_atual} → <strong>${p.pa_max_novo}</strong> (+${p.pa_ganho})</p>`);
        } else if (p.pa_max_novo != null && p.pa_max_atual != null && p.pa_max_novo !== p.pa_max_atual) {
            linhas.push(`<p>PM: ${p.pa_max_atual} → <strong>${p.pa_max_novo}</strong></p>`);
        }
        if (p.talentos_ganho > 0) {
            const rotulo =
                lv === 'v1.3' ? 'Poderes gerais (acumulado)' : `Talentos (total ${lv})`;
            linhas.push(
                `<p>${rotulo}: <strong>${p.talentos_totais_novo}</strong> (+${p.talentos_ganho} neste nível)</p>`
            );
        }
        if (p.graduacao_pericias_nova) {
            const rotGrad =
                lv === 'v1.3' ? 'Bônus em perícias (tr / n-tr)' : 'Graduações de perícias';
            linhas.push(`<p>${rotGrad}: <strong>${escHtml(p.graduacao_pericias_nova)}</strong></p>`);
        }
        if (p.magias_livro_ganho != null && p.magias_livro_ganho > 0) {
            linhas.push(
                `<p>Livro do mago: pode aprender <strong>+${p.magias_livro_ganho}</strong> magia(s) (teto no livro: ${p.magias_livro_max_novo}).</p>`
            );
        }
        if (p.magias_conhecidas_max_novo != null) {
            linhas.push(`<p>Magias conhecidas (teto): <strong>${p.magias_conhecidas_max_novo}</strong></p>`);
        }
        if (p.magias_preparadas_teto_novo != null) {
            linhas.push(`<p>Preparadas por dia (teto): <strong>${p.magias_preparadas_teto_novo}</strong></p>`);
        }
        if (p.bardo_pode_trocar_magia) {
            linhas.push('<p>Bardo: <strong>troca de magia conhecida</strong> disponível neste nível.</p>');
        }
        if (p.habilidade_classe) {
            linhas.push(
                `<p class="t20-hint" style="margin-top:.5rem"><strong>Poder de classe (${lv}):</strong> ${escHtml(p.habilidade_classe)}</p>`
            );
        }
        if (Array.isArray(p.avisos) && p.avisos.length) {
            linhas.push(`<p class="t20-hint">${escHtml(p.avisos.join(' '))}</p>`);
        }
        return linhas.join('');
    }

    function bindSelectClasseAlvo() {
        const sel = q('subirNivelClasseAlvo');
        if (!sel || sel.dataset.t20Bound) return;
        sel.dataset.t20Bound = '1';
        sel.addEventListener('change', () => {
            void carregarPreview();
        });
    }

    async function carregarPreview() {
        const corpo = q('subirNivelTormentaCorpo');
        const pid = q('fichaId') && q('fichaId').value;
        if (!corpo || !pid) return;
        const pick = classeAlvoSelecionada();
        if (pick) window.__t20SubirNivelClassePick = pick;
        corpo.innerHTML = '<p class="t20-hint">Carregando…</p>';
        try {
            const nv = Math.floor(Number((q('f_nivel') && q('f_nivel').value) || '1'));
            const alvo = Number.isFinite(nv) ? nv + 1 : 2;
            const opts = {};
            if (isV13()) {
                opts.classeSlug = classeAlvoSelecionada();
            }
            const p = await svc().previewSubirNivel(pid, alvo, opts);
            window.__t20SubirNivelPreview = p;
            corpo.innerHTML = montarHtmlPreview(p);
            bindSelectClasseAlvo();
            const btn = q('btnSubirNivelConfirmar');
            if (btn) btn.disabled = !(p && p.permitido);
        } catch (e) {
            corpo.innerHTML = `<p class="t20-hint">${escHtml(e.message || 'Erro ao carregar preview')}</p>`;
            const btn = q('btnSubirNivelConfirmar');
            if (btn) btn.disabled = true;
        }
    }

    async function abrirModal() {
        const pid = q('fichaId') && q('fichaId').value;
        if (!pid) {
            if (typeof Toast !== 'undefined') Toast.error('Salve a ficha antes de subir de nível.');
            else alert('Salve a ficha antes de subir de nível.');
            return;
        }
        const slug = classePrincipalSlug();
        if (!String(slug).trim()) {
            const lv = labelVersao();
            if (typeof Toast !== 'undefined') Toast.error(`Selecione a classe (${lv}) em Editar ficha.`);
            else alert(`Selecione a classe (${lv}).`);
            return;
        }
        if (isV13() && window.T20MulticlasseV13 && typeof window.T20MulticlasseV13.carregarSlugsClasses === 'function') {
            const slugs = await window.T20MulticlasseV13.carregarSlugsClasses();
            window.T20MulticlasseV13._slugsCache = slugs;
        }
        const ov = q('modalSubirNivelTormenta');
        if (ov) {
            ov.classList.add('is-open');
            ov.setAttribute('aria-hidden', 'false');
        }
        const chk = q('subirNivelAplicarPv');
        if (chk) chk.checked = true;
        await carregarPreview();
    }

    async function confirmarSubirNivel() {
        const pid = q('fichaId') && q('fichaId').value;
        const prev = window.__t20SubirNivelPreview;
        const lv = labelVersao();
        if (!pid || !prev) {
            if (typeof Toast !== 'undefined') Toast.error(`Abra o assistente «Subir nível (${lv})» antes de confirmar.`);
            return;
        }
        if (!prev.permitido) {
            if (typeof Toast !== 'undefined') Toast.error(prev.motivo || 'Subida de nível não permitida.');
            return;
        }
        const aplicarPv = !!(q('subirNivelAplicarPv') && q('subirNivelAplicarPv').checked);
        const body = { aplicar_ganhos_vida: aplicarPv };
        if (isV13()) {
            body.classe_slug = classeAlvoSelecionada() || prev.classe_slug || undefined;
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
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro ao subir de nível');
            else alert(e.message || 'Erro');
        }
    }

    function init() {
        const btn = q('btnT20SubirNivelMb');
        if (btn) btn.addEventListener('click', () => abrirModal());
        const btnC = q('btnSubirNivelConfirmar');
        if (btnC) btnC.addEventListener('click', () => confirmarSubirNivel());
        const btnF = q('btnFecharModalSubirNivel');
        if (btnF) btnF.addEventListener('click', () => fecharModal());
        const btnF2 = q('btnFecharModalSubirNivel2');
        if (btnF2) btnF2.addEventListener('click', () => fecharModal());
        const ov = q('modalSubirNivelTormenta');
        if (ov) {
            ov.addEventListener('click', (e) => {
                if (e.target === ov) fecharModal();
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window.t20AbrirModalSubirNivelMb = abrirModal;
})();
