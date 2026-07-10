/**
 * RF-T12k — convite de campanha (mestre: gerar/copiar/revogar link).
 */
(function (global) {
    'use strict';

    function q(id) {
        return document.getElementById(id);
    }

    function esc(s) {
        if (s == null) return '';
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function urlCompletaConvite(urlPath) {
        const p = String(urlPath || '').trim();
        if (!p) return '';
        try {
            return new URL(p, global.location.href).href;
        } catch (_e) {
            return p;
        }
    }

    global.__t20DashCampanhaConvite = {
        campanhaId: null,
        _bound: false,

        async aoEditarCampanha(campanhaId) {
            this.campanhaId = Number(campanhaId);
            const wrap = q('t20campConviteWrap');
            if (!wrap) return;
            wrap.hidden = false;
            await this.recarregar();
        },

        aoResetForm() {
            this.campanhaId = null;
            const wrap = q('t20campConviteWrap');
            if (wrap) wrap.hidden = true;
            this._renderVazio();
        },

        _renderVazio() {
            const st = q('t20campConviteStatus');
            const inp = q('t20campConviteUrl');
            if (st) st.textContent = 'Nenhum link ativo.';
            if (inp) inp.value = '';
        },

        async recarregar() {
            const cid = this.campanhaId;
            const st = q('t20campConviteStatus');
            const inp = q('t20campConviteUrl');
            if (!cid || !Number.isFinite(cid)) {
                this._renderVazio();
                return;
            }
            try {
                const data = await new global.TormentaCampanhaService().obterStatusConvite(cid);
                if (st) {
                    st.innerHTML = data.ativo
                        ? '<span class="t20-camp-convite-ativo">Link ativo</span> — envie aos jogadores.'
                        : 'Nenhum link ativo. Gere um novo convite.';
                }
                if (inp) {
                    inp.value = data.ativo && data.url_path ? urlCompletaConvite(data.url_path) : '';
                }
            } catch (e) {
                if (st) st.textContent = esc(e.message || 'Erro ao carregar convite');
                if (inp) inp.value = '';
            }
        },

        bindOnce(opts) {
            if (this._bound) return;
            this._bound = true;
            const Toast = (opts && opts.Toast) || global.Toast;
            const svc = () => new global.TormentaCampanhaService();

            q('t20campBtnGerarConvite')?.addEventListener('click', async () => {
                const cid = this.campanhaId;
                if (!cid) return;
                try {
                    await svc().gerarConvite(cid);
                    if (Toast && Toast.success) Toast.success('Link de convite gerado.');
                    await this.recarregar();
                } catch (e) {
                    if (Toast && Toast.error) Toast.error(e.message || 'Erro ao gerar');
                }
            });

            q('t20campBtnCopiarConvite')?.addEventListener('click', async () => {
                const inp = q('t20campConviteUrl');
                const txt = inp && inp.value ? inp.value.trim() : '';
                if (!txt) {
                    if (Toast && Toast.warning) Toast.warning('Gere o link antes de copiar.');
                    return;
                }
                try {
                    if (navigator.clipboard && navigator.clipboard.writeText) {
                        await navigator.clipboard.writeText(txt);
                    } else if (inp) {
                        inp.select();
                        document.execCommand('copy');
                    }
                    if (Toast && Toast.success) Toast.success('Link copiado.');
                } catch (_e) {
                    if (Toast && Toast.error) Toast.error('Não foi possível copiar.');
                }
            });

            q('t20campBtnRevogarConvite')?.addEventListener('click', async () => {
                const cid = this.campanhaId;
                if (!cid) return;
                if (!global.confirm('Revogar o link? Jogadores com o link antigo não poderão entrar.')) return;
                try {
                    await svc().revogarConvite(cid);
                    if (Toast && Toast.success) Toast.success('Convite revogado.');
                    await this.recarregar();
                } catch (e) {
                    if (Toast && Toast.error) Toast.error(e.message || 'Erro ao revogar');
                }
            });
        },
    };
})(typeof window !== 'undefined' ? window : globalThis);
