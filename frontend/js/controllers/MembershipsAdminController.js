/*
 * MembershipsAdminController.js
 * SRP: orquestra o painel admin de memberships multi-jogo na tela
 * `/pages/usuarios.html`.
 *
 * Reutiliza:
 *   - window.MembershipsAdminService → cliente HTTP
 *   - window.UsuarioService.listar() → para popular o select de usuários
 *     ao conceder acesso
 *   - window.Toast e window.ModalConfirm → feedback consistente
 */
(function (global) {
    const PERFIS_VALIDOS = ['jogador', 'mestre', 'administrador'];

    let cacheCatalogo = null;
    let slugAtual = 'dnd35';
    let usuariosCache = [];

    function el(id) {
        return document.getElementById(id);
    }

    function escape(texto) {
        return String(texto ?? '').replace(/[&<>"']/g, (c) => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;',
        })[c]);
    }

    function rotuloStatusAcesso(ativo) {
        return ativo
            ? '<span class="badge badge-ativo">Ativo</span>'
            : '<span class="badge badge-inativo">Inativo</span>';
    }

    function classeBadgePerfil(perfil) {
        if (perfil === 'administrador') return 'badge badge-admin';
        if (perfil === 'mestre') return 'badge badge-mestre';
        return 'badge badge-jogador';
    }

    function popularSelectJogos(catalogo) {
        const sel = el('filtroGameSlug');
        if (!sel) return;
        sel.innerHTML = '';
        (catalogo.jogos || []).forEach((jogo) => {
            const opt = document.createElement('option');
            opt.value = jogo.slug;
            const sufixo = jogo.status === 'disponivel' ? '' : ` — ${jogo.status}`;
            opt.textContent = `${jogo.nome}${sufixo}`;
            if (jogo.slug === slugAtual) opt.selected = true;
            sel.appendChild(opt);
        });
    }

    function renderizarTabela(resp) {
        const tbody = el('tabelaMemberships');
        if (!tbody) return;
        tbody.innerHTML = '';
        const items = resp.items || [];
        if (items.length === 0) {
            tbody.innerHTML =
                '<tr><td colspan="6" class="usuarios-loading">Nenhum acesso cadastrado para este jogo.</td></tr>';
            return;
        }

        items.forEach((m) => {
            const tr = document.createElement('tr');
            const opcoesPerfilNoJogo = PERFIS_VALIDOS.map((p) => {
                const sel = p === m.perfil_no_jogo ? 'selected' : '';
                return `<option value="${p}" ${sel}>${p}</option>`;
            }).join('');
            tr.innerHTML = `
                <td>${escape(m.usuario_nome)}</td>
                <td>${escape(m.usuario_email)}</td>
                <td><span class="${classeBadgePerfil(m.usuario_perfil_global)}">${escape(m.usuario_perfil_global)}</span></td>
                <td>
                    <select class="select-perfil-no-jogo" data-id="${m.id}">
                        ${opcoesPerfilNoJogo}
                    </select>
                </td>
                <td>${rotuloStatusAcesso(m.ativo)}</td>
                <td>
                    <button class="btn-acao ${m.ativo ? 'btn-acao-inativar' : 'btn-acao-reativar'} btn-toggle-membership" data-id="${m.id}" data-ativo="${m.ativo ? '1' : '0'}" type="button">
                        ${m.ativo ? 'Desativar' : 'Reativar'}
                    </button>
                    <button class="btn-acao btn-acao-excluir btn-revogar-membership" data-id="${m.id}" data-email="${escape(m.usuario_email)}" type="button">
                        Revogar
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        ligarEventosDaTabela();
    }

    function ligarEventosDaTabela() {
        document.querySelectorAll('.select-perfil-no-jogo').forEach((selectEl) => {
            selectEl.addEventListener('change', async (ev) => {
                const id = Number(ev.target.dataset.id);
                const novoPerfil = ev.target.value;
                try {
                    await global.MembershipsAdminService.atualizar(slugAtual, id, {
                        perfil_no_jogo: novoPerfil,
                    });
                    global.Toast?.success('Perfil no jogo atualizado.');
                } catch (err) {
                    global.Toast?.error(err.message || 'Falha ao atualizar.');
                    await recarregar();
                }
            });
        });

        document.querySelectorAll('.btn-toggle-membership').forEach((btn) => {
            btn.addEventListener('click', async () => {
                const id = Number(btn.dataset.id);
                const ativo = btn.dataset.ativo === '1';
                try {
                    await global.MembershipsAdminService.atualizar(slugAtual, id, {
                        ativo: !ativo,
                    });
                    global.Toast?.success(
                        !ativo ? 'Acesso reativado.' : 'Acesso desativado.'
                    );
                    await recarregar();
                } catch (err) {
                    global.Toast?.error(err.message || 'Falha ao alterar status.');
                }
            });
        });

        document.querySelectorAll('.btn-revogar-membership').forEach((btn) => {
            btn.addEventListener('click', async () => {
                const id = Number(btn.dataset.id);
                const email = btn.dataset.email;
                const ok = await confirmar(
                    `Revogar acesso de ${email} a este jogo?`,
                    'Esta operação não exclui a conta global; apenas remove o acesso a este jogo. Pode ser concedido de novo depois.'
                );
                if (!ok) return;
                try {
                    await global.MembershipsAdminService.revogar(slugAtual, id);
                    global.Toast?.success('Acesso revogado.');
                    await recarregar();
                } catch (err) {
                    global.Toast?.error(err.message || 'Falha ao revogar.');
                }
            });
        });
    }

    async function confirmar(titulo, descricao) {
        if (global.ModalConfirm?.show) {
            return global.ModalConfirm.show({ title: titulo, message: descricao });
        }
        return window.confirm(`${titulo}\n\n${descricao}`);
    }

    async function recarregar() {
        const tbody = el('tabelaMemberships');
        if (tbody) {
            tbody.innerHTML =
                '<tr><td colspan="6" class="usuarios-loading">Carregando…</td></tr>';
        }
        try {
            const resp = await global.MembershipsAdminService.listarMemberships(
                slugAtual
            );
            renderizarTabela(resp);
        } catch (err) {
            global.Toast?.error(err.message || 'Falha ao carregar acessos.');
            if (tbody) {
                tbody.innerHTML = `<tr><td colspan="6" class="usuarios-loading">${escape(err.message)}</td></tr>`;
            }
        }
    }

    // ── Modal: conceder acesso ─────────────────────────────────────────

    function abrirModalConceder(jogos) {
        const modal = el('modalConcederMembership');
        if (!modal) return;

        const jogo = (jogos || []).find((j) => j.slug === slugAtual);
        const nomeEl = el('modalConcederJogoNome');
        if (nomeEl && jogo) nomeEl.textContent = jogo.nome;

        const sel = el('selectUsuarioMembership');
        if (sel) {
            sel.innerHTML = '<option value="">— selecione —</option>';
            usuariosCache.forEach((u) => {
                const opt = document.createElement('option');
                opt.value = u.id;
                opt.textContent = `${u.nome} <${u.email}> (${u.perfil})`;
                sel.appendChild(opt);
            });
        }

        const perfilSel = el('selectPerfilNoJogo');
        if (perfilSel) perfilSel.value = '';
        const ativoChk = el('checkAtivoMembership');
        if (ativoChk) ativoChk.checked = true;

        modal.classList.add('show');
    }

    function fecharModalConceder() {
        const modal = el('modalConcederMembership');
        if (!modal) return;
        modal.classList.remove('show');
    }

    async function carregarUsuariosParaSelect() {
        // UsuarioService é uma `class` declarada via <script> clássico —
        // o identificador é global mas não aparece em `window` em browsers
        // modernos. Resolvemos pelo nome direto, com try/catch defensivo.
        let ServiceClass = null;
        try {
            // eslint-disable-next-line no-undef
            ServiceClass = UsuarioService;
        } catch (_e) {
            ServiceClass = global.UsuarioService || null;
        }
        if (typeof ServiceClass !== 'function') {
            console.warn('UsuarioService indisponível: select de usuários ficará vazio.');
            usuariosCache = [];
            return;
        }
        try {
            const svc = new ServiceClass();
            const resp = await svc.listar(true);
            usuariosCache = Array.isArray(resp?.usuarios) ? resp.usuarios : [];
        } catch (err) {
            console.warn('Falha ao listar usuários para select:', err);
            usuariosCache = [];
        }
    }

    async function concederAcesso() {
        const usuario_id = Number(el('selectUsuarioMembership')?.value || 0);
        const perfil_no_jogo = el('selectPerfilNoJogo')?.value || null;
        const ativo = !!el('checkAtivoMembership')?.checked;

        if (!usuario_id) {
            global.Toast?.error('Selecione um usuário.');
            return;
        }

        const payload = { usuario_id, ativo };
        if (perfil_no_jogo) payload.perfil_no_jogo = perfil_no_jogo;

        try {
            await global.MembershipsAdminService.conceder(slugAtual, payload);
            global.Toast?.success('Acesso concedido.');
            fecharModalConceder();
            await recarregar();
        } catch (err) {
            global.Toast?.error(err.message || 'Falha ao conceder acesso.');
        }
    }

    // ── Bootstrap ───────────────────────────────────────────────────────

    async function iniciar() {
        const filtro = el('filtroGameSlug');
        const btnConceder = el('btnConcederAcesso');
        const btnFechar = el('btnFecharModalMembership');
        const btnCancelar = el('btnCancelarModalMembership');
        const btnSalvar = el('btnSalvarModalMembership');

        try {
            cacheCatalogo = await global.MembershipsAdminService.listarCatalogo();
            popularSelectJogos(cacheCatalogo);
        } catch (err) {
            console.warn('Falha ao carregar catálogo de jogos:', err);
        }

        await carregarUsuariosParaSelect();
        await recarregar();

        filtro?.addEventListener('change', async (ev) => {
            slugAtual = ev.target.value || 'dnd35';
            await recarregar();
        });

        btnConceder?.addEventListener('click', () => {
            abrirModalConceder(cacheCatalogo?.jogos || []);
        });

        btnFechar?.addEventListener('click', fecharModalConceder);
        btnCancelar?.addEventListener('click', fecharModalConceder);
        btnSalvar?.addEventListener('click', concederAcesso);
    }

    global.MembershipsAdminController = { iniciar, recarregar };
})(window);
