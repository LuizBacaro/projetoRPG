/**
 * RF-T12k — entrada na campanha via ?convite=TOKEN no dashboard.
 */
(function (global) {
    'use strict';

    function esc(s) {
        if (s == null) return '';
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function tokenDaUrl() {
        try {
            return new URLSearchParams(global.location.search).get('convite');
        } catch (_e) {
            return null;
        }
    }

    function limparParamConvite() {
        try {
            const u = new URL(global.location.href);
            u.searchParams.delete('convite');
            const qs = u.searchParams.toString();
            const path = u.pathname + (qs ? `?${qs}` : '') + u.hash;
            global.history.replaceState(null, '', path);
        } catch (_e) {
            /* ignore */
        }
    }

    async function listarPersonagensJogador() {
        const svc = new global.TormentaPersonagemService();
        const rows = await svc.listar({ limit: 500 });
        const arr = Array.isArray(rows) ? rows : rows && rows.items ? rows.items : [];
        return arr.filter((p) => String(p.tipo || '').toLowerCase() === 'jogador');
    }

    function popularSelectPersonagens(select, personagens) {
        if (!select) return;
        if (!personagens.length) {
            select.innerHTML = '<option value="">— Crie um personagem jogador primeiro —</option>';
            select.disabled = true;
            return;
        }
        select.disabled = false;
        select.innerHTML =
            '<option value="">— Escolha o personagem —</option>' +
            personagens
                .map((p) => {
                    const id = Number(p.id);
                    const nome = esc(p.nome || `Personagem #${id}`);
                    const camp = p.campanha_id ? ' (já em campanha)' : '';
                    return `<option value="${id}"${p.campanha_id ? ' disabled' : ''}>${nome}${camp}</option>`;
                })
                .join('');
    }

    async function processarConviteNaUrl() {
        const token = tokenDaUrl();
        if (!token || !String(token).trim()) return;

        const dlg = document.getElementById('t20DialogConviteEntrada');
        const titulo = document.getElementById('t20ConviteCampanhaNome');
        const meta = document.getElementById('t20ConviteCampanhaMeta');
        const sel = document.getElementById('t20ConvitePersonagem');
        const btn = document.getElementById('t20ConviteEntrar');
        const Toast = global.Toast;
        const campSvc = new global.TormentaCampanhaService();

        if (!dlg || typeof dlg.showModal !== 'function') return;

        let info;
        try {
            info = await campSvc.obterInfoConvite(token);
        } catch (e) {
            if (Toast && Toast.error) Toast.error(e.message || 'Convite inválido.');
            limparParamConvite();
            return;
        }

        if (titulo) titulo.textContent = info.nome || 'Campanha';
        if (meta) {
            const parts = [];
            if (info.mestre_nome) parts.push(`Mestre: ${info.mestre_nome}`);
            if (info.descricao) parts.push(info.descricao);
            meta.textContent = parts.join(' · ') || 'Você foi convidado para esta mesa.';
        }

        try {
            const ps = await listarPersonagensJogador();
            popularSelectPersonagens(sel, ps);
        } catch (e) {
            if (Toast && Toast.warning) Toast.warning(e.message || 'Erro ao listar personagens.');
            popularSelectPersonagens(sel, []);
        }

        document.getElementById('t20ConviteFechar')?.addEventListener('click', () => {
            dlg.close();
            limparParamConvite();
        }, { once: true });
        document.getElementById('t20ConviteCancelar')?.addEventListener('click', () => {
            dlg.close();
            limparParamConvite();
        }, { once: true });

        if (btn && !btn.dataset.boundConvite) {
            btn.dataset.boundConvite = '1';
            btn.addEventListener('click', async () => {
                const pid = Number(sel && sel.value);
                if (!Number.isFinite(pid) || pid <= 0) {
                    if (Toast && Toast.error) Toast.error('Escolha um personagem.');
                    return;
                }
                btn.disabled = true;
                try {
                    const res = await campSvc.entrarViaConvite(token, pid);
                    dlg.close();
                    limparParamConvite();
                    const nomeCamp = (res && res.campanha_nome) || info.nome || 'campanha';
                    if (Toast && Toast.success) {
                        Toast.success(`Personagem vinculado à campanha «${nomeCamp}».`);
                    }
                    global.location.href = `ficha-personagem.html?id=${encodeURIComponent(String(pid))}`;
                } catch (e) {
                    if (Toast && Toast.error) Toast.error(e.message || 'Erro ao entrar');
                } finally {
                    btn.disabled = false;
                }
            });
        }

        document.querySelectorAll('.t20-dash-nav button[data-tab="campanhas"]').forEach((b) => {
            b.click();
        });
        dlg.showModal();
    }

    function init() {
        void processarConviteNaUrl();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    global.T20ConviteCampanhaEntrada = { processarConviteNaUrl, limparParamConvite };
})(typeof window !== 'undefined' ? window : globalThis);
