/**
 * Painel Campanhas — dashboard Tormenta (qualquer usuário autenticado).
 * Inicializado via window.__t20DashCampanhasInit(opts) a partir de dashboard.html.
 */
(function (global) {
    function esc(s) {
        if (s == null) return '';
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    global.__t20DashCampanhasInit = function (opts) {
        if (!opts) return;

        const getLista = typeof opts.getLista === 'function' ? opts.getLista : () => [];
        const recarregarTabela = opts.recarregarTabela || function () {};
        const onCampanhaCriada = typeof opts.onCampanhaCriada === 'function' ? opts.onCampanhaCriada : null;
        const onSelecionarCampanha =
            typeof opts.onSelecionarCampanha === 'function' ? opts.onSelecionarCampanha : null;
        const onSairCampanha = typeof opts.onSairCampanha === 'function' ? opts.onSairCampanha : null;
        const onCampanhasAtualizadas =
            typeof opts.onCampanhasAtualizadas === 'function' ? opts.onCampanhasAtualizadas : null;
        const Toast = opts.Toast || global.Toast;

        const svc = new global.TormentaCampanhaService();
        let campanhas = [];
        let sessoes = [];
        let campanhaEdicaoId = null;
        let sessaoEdicaoId = null;
        let filtroTipoCamp = 'todos';
        let buscaCamp = '';

        function personagensFiltrados() {
            const lista = getLista() || [];
            const q = (buscaCamp || '').trim().toLowerCase();
            return lista.filter((p) => {
                const tipo = String(p.tipo || '').toLowerCase();
                if (filtroTipoCamp !== 'todos' && tipo !== filtroTipoCamp) return false;
                if (!q) return true;
                const busca = global.PersonagemRotulo
                    ? global.PersonagemRotulo.textoBuscaPersonagem(p)
                    : String(p.nome || '').toLowerCase();
                return busca.includes(q);
            });
        }

        function renderChecklist(selecionados) {
            const host = document.getElementById('t20campPersonagens');
            if (!host) return;
            const set = new Set(selecionados || []);
            const rows = personagensFiltrados();
            if (!rows.length) {
                host.innerHTML = '<p class="t20-dash-hint">Nenhum combatente na lista. Cadastre na aba Combatentes ou ajuste filtros.</p>';
                return;
            }
            host.innerHTML = rows
                .map((p) => {
                    const id = Number(p.id);
                    const ck = set.has(id) ? ' checked' : '';
                    const rotulo = global.PersonagemRotulo
                        ? esc(global.PersonagemRotulo.rotuloPersonagemComDono(p, `Nv ${p.nivel || 1}`))
                        : `${esc(p.nome)} (${esc(p.tipo || '')})`;
                    return `<label class="t20-camp-cb-item"><input type="checkbox" class="t20-camp-cb-inp" value="${id}"${ck} /><span class="t20-camp-cb-nome">${rotulo}</span></label>`;
                })
                .join('');
        }

        function idsSelecionadosChecklist() {
            return Array.from(document.querySelectorAll('#t20campPersonagens .t20-camp-cb-inp:checked'))
                .map((el) => Number(el.value))
                .filter((id) => Number.isFinite(id) && id > 0);
        }

        async function carregarCampanhas() {
            const lista = document.getElementById('t20campListaCampanhas');
            if (!lista) return;
            lista.innerHTML = '<p class="tormenta-cell-muted">Carregando…</p>';
            try {
                campanhas = await svc.listar();
                if (!Array.isArray(campanhas)) campanhas = [];
                renderListaCampanhas();
                if (global.__t20CampanhaWorkspace) {
                    global.__t20CampanhaWorkspace.renderBotoesCampanhas(campanhas);
                }
                if (onCampanhasAtualizadas) onCampanhasAtualizadas(campanhas);
            } catch (e) {
                lista.innerHTML = `<p class="tormenta-cell-muted">${esc(e.message || 'Erro')}</p>`;
            }
        }

        async function carregarSessoes() {
            const lista = document.getElementById('t20campListaSessoes');
            if (!lista) return;
            lista.innerHTML = '<p class="tormenta-cell-muted">Carregando…</p>';
            try {
                sessoes = await svc.listarSessoes();
                if (!Array.isArray(sessoes)) sessoes = [];
                renderListaSessoes();
                popularSelectCampanhasSessao();
            } catch (e) {
                lista.innerHTML = `<p class="tormenta-cell-muted">${esc(e.message || 'Erro')}</p>`;
            }
        }

        function renderListaCampanhas() {
            const lista = document.getElementById('t20campListaCampanhas');
            if (!lista) return;
            if (!campanhas.length) {
                lista.innerHTML = '<p class="tormenta-cell-muted">Nenhuma campanha cadastrada.</p>';
                return;
            }
            lista.innerHTML = campanhas
                .map((c) => {
                    const n = Number(c.total_personagens) || 0;
                    return `<div class="t20-camp-card" data-id="${c.id}">
                        <div class="t20-camp-card__hd"><strong>${esc(c.nome)}</strong><span class="t20-camp-card__meta">${n} personagem(ns)</span></div>
                        <p class="t20-camp-card__desc">${esc(c.descricao || '')}</p>
                        <div class="t20-camp-card__ac">
                            <button type="button" class="tormenta-btn t20-camp-btn-editar" data-id="${c.id}">Editar</button>
                            <button type="button" class="tormenta-btn t20-camp-btn-excluir" data-id="${c.id}">Excluir</button>
                        </div>
                    </div>`;
                })
                .join('');
            lista.querySelectorAll('.t20-camp-btn-editar').forEach((btn) => {
                btn.addEventListener('click', () => editarCampanha(Number(btn.getAttribute('data-id'))));
            });
            lista.querySelectorAll('.t20-camp-btn-excluir').forEach((btn) => {
                btn.addEventListener('click', () => excluirCampanha(Number(btn.getAttribute('data-id'))));
            });
        }

        function popularSelectCampanhasSessao() {
            const sel = document.getElementById('t20campSessaoCampanhaId');
            if (!sel) return;
            const cur = sel.value;
            sel.innerHTML = '<option value="">Selecione a campanha</option>';
            campanhas.forEach((c) => {
                const o = document.createElement('option');
                o.value = String(c.id);
                o.textContent = c.nome || `Campanha #${c.id}`;
                sel.appendChild(o);
            });
            if (cur && Array.from(sel.options).some((o) => o.value === cur)) sel.value = cur;
        }

        function renderListaSessoes() {
            const lista = document.getElementById('t20campListaSessoes');
            if (!lista) return;
            if (!sessoes.length) {
                lista.innerHTML = '<p class="tormenta-cell-muted">Nenhuma sessão registrada.</p>';
                return;
            }
            lista.innerHTML = sessoes
                .map((s) => {
                    const vis = s.visivel_jogadores ? 'Sim' : 'Não';
                    return `<div class="t20-camp-card" data-sid="${s.id}">
                        <div class="t20-camp-card__hd"><strong>${esc(s.campanha_nome || 'Campanha')}</strong><span class="t20-camp-card__meta">Visível jogadores: ${vis}</span></div>
                        <p class="t20-camp-card__desc">${esc(s.resumo || '')}</p>
                        <div class="t20-camp-card__ac">
                            <button type="button" class="tormenta-btn t20-camp-sess-editar" data-id="${s.id}">Editar</button>
                            <button type="button" class="tormenta-btn t20-camp-sess-excluir" data-id="${s.id}">Excluir</button>
                        </div>
                    </div>`;
                })
                .join('');
            lista.querySelectorAll('.t20-camp-sess-editar').forEach((btn) => {
                btn.addEventListener('click', () => editarSessao(Number(btn.getAttribute('data-id'))));
            });
            lista.querySelectorAll('.t20-camp-sess-excluir').forEach((btn) => {
                btn.addEventListener('click', () => excluirSessao(Number(btn.getAttribute('data-id'))));
            });
        }

        function resetFormCampanha() {
            campanhaEdicaoId = null;
            const hid = document.getElementById('t20campIdEdicao');
            const badge = document.getElementById('t20campEdicaoBadge');
            const btnC = document.getElementById('t20campBtnCancelarCampanha');
            const nome = document.getElementById('t20campNome');
            const desc = document.getElementById('t20campDescricao');
            const busca = document.getElementById('t20campBusca');
            const salvar = document.getElementById('t20campBtnSalvarCampanha');
            if (hid) hid.value = '';
            if (badge) badge.style.display = 'none';
            if (btnC) btnC.style.display = 'none';
            if (nome) nome.value = '';
            if (desc) desc.value = '';
            if (busca) busca.value = '';
            if (salvar) salvar.textContent = 'Criar campanha';
            buscaCamp = '';
            filtroTipoCamp = 'todos';
            document.querySelectorAll('#t20campTipoFiltros [data-t20camp-tipo]').forEach((b) => {
                b.classList.toggle('t20-dash-filter--active', b.getAttribute('data-t20camp-tipo') === 'todos');
            });
            renderChecklist([]);
        }

        function editarCampanha(id) {
            const c = campanhas.find((x) => Number(x.id) === id);
            if (!c) return;
            campanhaEdicaoId = id;
            const hid = document.getElementById('t20campIdEdicao');
            const badge = document.getElementById('t20campEdicaoBadge');
            const btnC = document.getElementById('t20campBtnCancelarCampanha');
            const nome = document.getElementById('t20campNome');
            const desc = document.getElementById('t20campDescricao');
            const salvar = document.getElementById('t20campBtnSalvarCampanha');
            if (hid) hid.value = String(id);
            if (badge) {
                badge.style.display = '';
                badge.textContent = `Editando campanha #${id}`;
            }
            if (btnC) btnC.style.display = '';
            if (nome) nome.value = c.nome || '';
            if (desc) desc.value = c.descricao || '';
            if (salvar) salvar.textContent = 'Salvar alterações';
            const sub = document.getElementById('t20campSubabaCadastro');
            const paneS = document.getElementById('t20campSubabaSessoes');
            document.querySelectorAll('#t20campSubAbas [data-t20camp-sub]').forEach((b) => {
                b.classList.toggle('t20-camp-subaba-btn--active', b.getAttribute('data-t20camp-sub') === 'cadastro');
            });
            if (sub) sub.classList.add('t20-camp-subaba-pane--active');
            if (paneS) paneS.classList.remove('t20-camp-subaba-pane--active');
            renderChecklist(c.personagem_ids || []);
            const top = document.getElementById('t20campPanelTop');
            if (top) top.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        async function excluirCampanha(id) {
            if (!global.confirm('Excluir esta campanha? Personagens ficam sem vínculo de campanha.')) return;
            try {
                await svc.deletar(id);
                Toast.success('Campanha excluída.');
                await carregarCampanhas();
                await carregarSessoes();
                recarregarTabela();
                if (campanhaEdicaoId === id) resetFormCampanha();
            } catch (e) {
                Toast.error(e.message || 'Erro ao excluir');
            }
        }

        function resetFormSessao() {
            sessaoEdicaoId = null;
            const hid = document.getElementById('t20campSessaoId');
            const badge = document.getElementById('t20campSessaoEdicaoBadge');
            const btnC = document.getElementById('t20campBtnCancelarSessao');
            const res = document.getElementById('t20campSessaoResumo');
            const vis = document.getElementById('t20campSessaoVisivel');
            const salvar = document.getElementById('t20campBtnSalvarSessao');
            if (hid) hid.value = '';
            if (badge) badge.style.display = 'none';
            if (btnC) btnC.style.display = 'none';
            if (res) res.value = '';
            if (vis) vis.checked = false;
            if (salvar) salvar.textContent = 'Registrar sessão';
        }

        function editarSessao(sid) {
            const s = sessoes.find((x) => Number(x.id) === sid);
            if (!s) return;
            sessaoEdicaoId = sid;
            const hid = document.getElementById('t20campSessaoId');
            const badge = document.getElementById('t20campSessaoEdicaoBadge');
            const btnC = document.getElementById('t20campBtnCancelarSessao');
            const campSel = document.getElementById('t20campSessaoCampanhaId');
            const res = document.getElementById('t20campSessaoResumo');
            const vis = document.getElementById('t20campSessaoVisivel');
            const salvar = document.getElementById('t20campBtnSalvarSessao');
            if (hid) hid.value = String(sid);
            if (badge) {
                badge.style.display = '';
                badge.textContent = `Editando sessão #${sid}`;
            }
            if (btnC) btnC.style.display = '';
            if (campSel) campSel.value = String(s.campanha_id || '');
            if (res) res.value = s.resumo || '';
            if (vis) vis.checked = !!s.visivel_jogadores;
            if (salvar) salvar.textContent = 'Salvar sessão';
            const sub = document.getElementById('t20campSubabaSessoes');
            const paneC = document.getElementById('t20campSubabaCadastro');
            document.querySelectorAll('#t20campSubAbas [data-t20camp-sub]').forEach((b) => {
                b.classList.toggle('t20-camp-subaba-btn--active', b.getAttribute('data-t20camp-sub') === 'sessoes');
            });
            if (sub) sub.classList.add('t20-camp-subaba-pane--active');
            if (paneC) paneC.classList.remove('t20-camp-subaba-pane--active');
        }

        async function excluirSessao(sid) {
            if (!global.confirm('Excluir este registro de sessão?')) return;
            try {
                await svc.deletarSessao(sid);
                Toast.success('Sessão excluída.');
                await carregarSessoes();
                if (sessaoEdicaoId === sid) resetFormSessao();
            } catch (e) {
                Toast.error(e.message || 'Erro ao excluir');
            }
        }

        function ativarSubaba(which) {
            const w = String(which || '');
            const isMesa = w.startsWith('mesa-');
            document.querySelectorAll('#t20campSubAbas [data-t20camp-sub]').forEach((b) => {
                b.classList.toggle('t20-camp-subaba-btn--active', b.getAttribute('data-t20camp-sub') === which);
            });
            const c = document.getElementById('t20campSubabaCadastro');
            const s = document.getElementById('t20campSubabaSessoes');
            const ws = document.getElementById('t20campSubabaWorkspace');
            if (c) c.classList.toggle('t20-camp-subaba-pane--active', which === 'cadastro');
            if (s) s.classList.toggle('t20-camp-subaba-pane--active', which === 'sessoes');
            if (ws) ws.classList.toggle('t20-camp-subaba-pane--active', isMesa);
            if (isMesa) {
                const id = Number(w.replace('mesa-', ''));
                if (onSelecionarCampanha) onSelecionarCampanha(id);
            } else if (onSairCampanha) {
                onSairCampanha();
            }
        }

        document.getElementById('t20campSubAbas')?.addEventListener('click', (ev) => {
            const btn = ev.target.closest('[data-t20camp-sub]');
            if (!btn) return;
            ativarSubaba(btn.getAttribute('data-t20camp-sub'));
        });

        document.getElementById('t20campTipoFiltros')?.addEventListener('click', (ev) => {
            const btn = ev.target.closest('[data-t20camp-tipo]');
            if (!btn) return;
            filtroTipoCamp = btn.getAttribute('data-t20camp-tipo') || 'todos';
            document.querySelectorAll('#t20campTipoFiltros [data-t20camp-tipo]').forEach((b) => {
                b.classList.toggle('t20-dash-filter--active', b === btn);
            });
            const ids = idsSelecionadosChecklist();
            renderChecklist(ids);
        });

        document.getElementById('t20campBusca')?.addEventListener('input', (ev) => {
            buscaCamp = ev.target.value || '';
            const ids = idsSelecionadosChecklist();
            renderChecklist(ids);
        });

        document.getElementById('t20campFormCampanha')?.addEventListener('submit', async (ev) => {
            ev.preventDefault();
            const nome = (document.getElementById('t20campNome')?.value || '').trim();
            const descricao = (document.getElementById('t20campDescricao')?.value || '').trim();
            const ids = idsSelecionadosChecklist();
            if (nome.length < 2) {
                Toast.error('Nome da campanha deve ter ao menos 2 caracteres.');
                return;
            }
            try {
                let criada = null;
                if (campanhaEdicaoId) {
                    await svc.atualizar(campanhaEdicaoId, { nome, descricao, personagem_ids: ids });
                    Toast.success('Campanha atualizada.');
                } else {
                    criada = await svc.criar({ nome, descricao, personagem_ids: ids });
                    Toast.success('Campanha criada. Você é o mestre desta mesa.');
                    if (onCampanhaCriada) onCampanhaCriada(criada);
                }
                resetFormCampanha();
                await carregarCampanhas();
                await carregarSessoes();
                recarregarTabela();
                if (criada && criada.id && global.__t20CampanhaWorkspace) {
                    document.querySelector('.t20-dash-nav button[data-tab="campanhas"]')?.click();
                    global.__t20CampanhaWorkspace.abrirCampanha(criada.id);
                }
            } catch (e) {
                Toast.error(e.message || 'Erro ao salvar');
            }
        });

        document.getElementById('t20campBtnCancelarCampanha')?.addEventListener('click', () => resetFormCampanha());

        document.getElementById('t20campFormSessao')?.addEventListener('submit', async (ev) => {
            ev.preventDefault();
            const campanhaId = Math.floor(Number(document.getElementById('t20campSessaoCampanhaId')?.value || 0));
            const resumo = (document.getElementById('t20campSessaoResumo')?.value || '').trim();
            const visivel = !!document.getElementById('t20campSessaoVisivel')?.checked;
            if (!campanhaId) {
                Toast.error('Selecione a campanha.');
                return;
            }
            if (!resumo) {
                Toast.error('Informe o resumo da sessão.');
                return;
            }
            try {
                if (sessaoEdicaoId) {
                    await svc.atualizarSessao(sessaoEdicaoId, { resumo, visivel_jogadores: visivel });
                    Toast.success('Sessão atualizada.');
                } else {
                    await svc.criarSessao({ campanha_id: campanhaId, resumo, visivel_jogadores: visivel });
                    Toast.success('Sessão registrada.');
                }
                resetFormSessao();
                await carregarSessoes();
            } catch (e) {
                Toast.error(e.message || 'Erro ao salvar sessão');
            }
        });

        document.getElementById('t20campBtnCancelarSessao')?.addEventListener('click', () => resetFormSessao());

        global.__t20DashCampanhas = {
            getCampanhas: () => campanhas.slice(),
            recarregarCampanhas: carregarCampanhas,
            ativarSubaba,
        };

        document.querySelectorAll('.t20-dash-nav button[data-tab]').forEach((b) => {
            if (b.getAttribute('data-tab') === 'campanhas') {
                b.addEventListener('click', () => {
                    void carregarCampanhas();
                    void carregarSessoes();
                    renderChecklist(idsSelecionadosChecklist());
                });
            }
        });

        resetFormCampanha();
        resetFormSessao();
    };
})(typeof window !== 'undefined' ? window : this);
