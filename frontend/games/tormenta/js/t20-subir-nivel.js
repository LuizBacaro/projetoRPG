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

    function fecharModal() {
        const ov = q('modalSubirNivelTormenta');
        if (!ov) return;
        ov.classList.remove('is-open');
        ov.setAttribute('aria-hidden', 'true');
    }

    function montarHtmlPreview(p) {
        if (!p) return '<p class="t20-hint">Sem dados.</p>';
        if (!p.permitido) {
            return `<p class="t20-hint" style="color:var(--t20-danger,#a33)">${escHtml(p.motivo || 'Não permitido.')}</p>`;
        }
        const lv = labelVersao();
        const linhas = [];
        linhas.push(`<p><strong>Nível ${p.nivel_atual} → ${p.nivel_alvo}</strong> (${escHtml(p.classe_slug || '')})</p>`);
        if (p.pv_ganho != null) {
            linhas.push(`<p>PV: ${p.pv_max_atual} → <strong>${p.pv_max_novo}</strong> (+${p.pv_ganho})</p>`);
        }
        if (p.pa_ganho != null && p.pa_ganho > 0) {
            linhas.push(`<p>PM: ${p.pa_max_atual} → <strong>${p.pa_max_novo}</strong> (+${p.pa_ganho})</p>`);
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

    async function carregarPreview() {
        const corpo = q('subirNivelTormentaCorpo');
        const pid = q('fichaId') && q('fichaId').value;
        if (!corpo || !pid) return;
        corpo.innerHTML = '<p class="t20-hint">Carregando…</p>';
        try {
            const nv = Math.floor(Number((q('f_nivel') && q('f_nivel').value) || '1'));
            const alvo = Number.isFinite(nv) ? nv + 1 : 2;
            const p = await svc().previewSubirNivel(pid, alvo);
            window.__t20SubirNivelPreview = p;
            corpo.innerHTML = montarHtmlPreview(p);
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
        const slug = (q('f_classe_mb') && q('f_classe_mb').value) || '';
        if (!String(slug).trim()) {
            const lv = labelVersao();
            if (typeof Toast !== 'undefined') Toast.error(`Selecione a classe (${lv}) em Editar ficha.`);
            else alert(`Selecione a classe (${lv}).`);
            return;
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
        try {
            const res = await svc().aplicarSubirNivel(pid, { aplicar_ganhos_vida: aplicarPv });
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
