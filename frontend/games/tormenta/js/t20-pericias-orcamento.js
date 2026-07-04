/**
 * Orçamento de perícias na criação MB (API `/tormenta/regras/pericias/validar-criacao`).
 */
(function () {
    const regras = () => new TormentaRegrasService();

    function q(id) {
        return document.getElementById(id);
    }

    function nivelPersonagem() {
        const n = Number(q('f_nivel') && q('f_nivel').value);
        return Number.isFinite(n) && n >= 1 ? n : 1;
    }

    function intValor() {
        const el = q('fichaIntResumo') || q('f_dlg_attr_int');
        const n = Number(el && el.value);
        return Number.isFinite(n) ? n : 10;
    }

    function classeSlug() {
        const sel = q('f_classe_mb');
        return sel && sel.value ? String(sel.value).trim().toLowerCase() : '';
    }

    function slugRaca() {
        const sel = q('f_raca_select');
        const v = sel && sel.value;
        if (!v || v === '__livre__') return '';
        return v;
    }

    function humanoVersatilOrcamento() {
        const el = q('f_humano_versatil');
        const v = el && el.value ? String(el.value).trim() : '';
        if (!v || v === 'duas_pericias') return null;
        return v;
    }

    function coletarPericiasOrcamento() {
        if (typeof window.coletarPericias === 'function') {
            return window.coletarPericias();
        }
        const rows = document.querySelectorAll('#tblPericias tbody tr');
        const out = [];
        rows.forEach((tr) => {
            const nomeEl = tr.querySelector('.t20-p-nome');
            const nome = nomeEl ? nomeEl.textContent.trim() : '';
            if (!nome || nome === '—') return;
            out.push({
                nome,
                treinado: Boolean(tr.querySelector('.p-treinado')?.checked),
                graduacao: Number(tr.querySelector('.p-total')?.value || 0) || 0,
            });
        });
        return out;
    }

    function getRegraVersaoOrcamento() {
        if (typeof window.getRegraVersaoAtiva === 'function') {
            return window.getRegraVersaoAtiva();
        }
        return window.T20RegraVersao ? window.T20RegraVersao.DEFAULT_NOVA_FICHA : 'v13';
    }

    function labelVersaoOrcamento() {
        return window.T20RegraVersao
            ? window.T20RegraVersao.labelVersaoCurta(getRegraVersaoOrcamento())
            : 'MB';
    }

    function origemBeneficiosOrcamento() {
        const picks = window.__t20OrigemBeneficios;
        return Array.isArray(picks) && picks.length ? picks.slice() : null;
    }

    function origemSlugOrcamento() {
        const sel = q('f_origem_slug');
        return sel && sel.value ? String(sel.value).trim().toLowerCase() : null;
    }

    function origemTrocasOrcamento() {
        if (window.T20OrigemTrocasFichaV13 && window.T20OrigemTrocasFichaV13.origemTrocasMap) {
            const m = window.T20OrigemTrocasFichaV13.origemTrocasMap();
            return Object.keys(m).length ? m : null;
        }
        return null;
    }

    function formatarResumo(p) {
        if (!p || p.vagas_treinadas == null) {
            return `Orçamento perícias: selecione classe em Editar ficha (${labelVersaoOrcamento()}).`;
        }
        const tr = `${p.usadas_treinadas}/${p.vagas_treinadas} treinadas`;
        const ok = p.valido ? 'OK' : 'inválido';
        const lv = labelVersaoOrcamento();
        if (window.T20RegraVersao && window.T20RegraVersao.isV13(getRegraVersaoOrcamento())) {
            const cfg = p.pericias_classe_config || p.pericias_classe || {};
            const vc = cfg.vagas_classe != null ? cfg.vagas_classe : '—';
            const extraOrig = p.pericias_treinadas_extra_origem
                ? ` + origem (+${p.pericias_treinadas_extra_origem})`
                : '';
            return `Orçamento ${lv} (${ok}): ${tr} · classe ${vc} + INT + racial${extraOrig}.`;
        }
        const gtr = `${p.gasto_grad_treinadas}/${p.pontos_grad_treinadas} grad. tr.`;
        const gnt = `${p.gasto_grad_nao_treinadas}/${p.pontos_grad_nao_treinadas} grad. n-tr`;
        return `Orçamento ${lv} (${ok}): ${tr}; ${gtr}; ${gnt}`;
    }

    async function validarPericiasOrcamentoMb() {
        const slug = classeSlug();
        const hint = q('fichaPericiasOrcamento');
        const tipo = (q('f_tipo') && q('f_tipo').value) || 'jogador';
        if (tipo !== 'jogador' || !slug) {
            window.__t20PericiasOrcamentoOk = true;
            window.__t20PericiasOrcamentoMsg = '';
            if (hint) {
                hint.className = 't20-hint';
                hint.textContent = slug
                    ? ''
                    : `Orçamento perícias: selecione classe em Editar ficha (${labelVersaoOrcamento()}).`;
            }
            return { ok: true, preview: null };
        }
        try {
            const preview = await regras().validarPericiasCriacao({
                nivel: nivelPersonagem(),
                classe_slug: slug,
                int_valor: intValor(),
                slug_raca: slugRaca() || null,
                pericias: coletarPericiasOrcamento(),
                regraVersao: getRegraVersaoOrcamento(),
                humanoVersatil: humanoVersatilOrcamento(),
                origem_beneficios: origemBeneficiosOrcamento(),
                origemSlug: origemSlugOrcamento(),
                origemTrocasPericia: origemTrocasOrcamento(),
            });
            if (hint) {
                hint.textContent = formatarResumo(preview);
                hint.className = preview.valido
                    ? 't20-hint t20-compra-pontos-ok'
                    : 't20-hint t20-compra-pontos-erro';
            }
            window.__t20PericiasOrcamentoOk = Boolean(preview.valido);
            window.__t20PericiasOrcamentoMsg = preview.motivo || '';
            if (typeof window.t20AtualizarEstadoBotaoSalvar === 'function') {
                window.t20AtualizarEstadoBotaoSalvar();
            }
            return {
                ok: Boolean(preview.valido),
                msg: preview.motivo || `Orçamento de perícias inválido (${labelVersaoOrcamento()}).`,
                preview,
            };
        } catch (e) {
            window.__t20PericiasOrcamentoOk = false;
            window.__t20PericiasOrcamentoMsg = e.message || 'Erro ao validar perícias.';
            if (hint) {
                hint.textContent = e.message || 'Erro ao validar perícias.';
                hint.className = 't20-hint t20-compra-pontos-erro';
            }
            return { ok: false, msg: e.message || 'Erro ao validar perícias.' };
        }
    }

    function init() {
        const tbl = q('tblPericias');
        if (tbl) {
            tbl.addEventListener('change', () => {
                validarPericiasOrcamentoMb();
                if (typeof window.t20AtualizarEstadoBotaoSalvar === 'function') {
                    window.t20AtualizarEstadoBotaoSalvar();
                }
            });
            tbl.addEventListener('input', () => {
                validarPericiasOrcamentoMb();
                if (typeof window.t20AtualizarEstadoBotaoSalvar === 'function') {
                    window.t20AtualizarEstadoBotaoSalvar();
                }
            });
        }
        ['f_nivel', 'f_classe_mb', 'f_raca_select', 'fichaIntResumo', 'f_humano_versatil', 'f_origem_slug'].forEach((id) => {
            const el = q(id);
            if (el) {
                el.addEventListener('change', () => validarPericiasOrcamentoMb());
                el.addEventListener('input', () => validarPericiasOrcamentoMb());
            }
        });
        validarPericiasOrcamentoMb();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window.t20ValidarPericiasOrcamentoMb = validarPericiasOrcamentoMb;
})();
