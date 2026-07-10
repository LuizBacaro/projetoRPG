/**
 * RF-T12f — Handouts de campanha (mestre CRUD + leitura jogador).
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

    function fmtData(iso) {
        if (!iso) return '—';
        try {
            const d = new Date(iso);
            return Number.isFinite(d.getTime()) ? d.toLocaleString('pt-BR') : '—';
        } catch (_e) {
            return '—';
        }
    }

    function renderCorpoMd(texto) {
        const t = esc(texto || '').replace(/\n/g, '<br>');
        return t || '<span class="tormenta-cell-muted">(sem texto)</span>';
    }

    global.__t20DashHandoutsInit = function (opts) {
        if (!opts) return;
        const Toast = opts.Toast || global.Toast;
        const getPersonagens = typeof opts.getPersonagens === 'function' ? opts.getPersonagens : () => [];
        const campSvc = new global.TormentaCampanhaService();
        let handouts = [];
        let handoutEdicaoId = null;
        let jogadoresCampanha = [];

        function q(id) {
            return document.getElementById(id);
        }

        function idsRevelacaoSelecionados() {
            return Array.from(document.querySelectorAll('#t20campHandoutJogadores .t20-camp-cb-inp:checked'))
                .map((el) => Number(el.value))
                .filter((id) => Number.isFinite(id) && id > 0);
        }

        function renderChecklistJogadores(selecionados) {
            const host = q('t20campHandoutJogadores');
            if (!host) return;
            const set = new Set(selecionados || []);
            if (!jogadoresCampanha.length) {
                host.innerHTML =
                    '<p class="t20-dash-hint">Nenhum jogador com dono na campanha selecionada.</p>';
                return;
            }
            host.innerHTML = jogadoresCampanha
                .map((j) => {
                    const uid = Number(j.dono_id);
                    const ck = set.has(uid) ? ' checked' : '';
                    const nome = esc(j.dono_nome || j.jogador_nome || j.nome || `Usuário #${uid}`);
                    const pers = esc(j.nome || '');
                    return `<label class="t20-camp-cb-item"><input type="checkbox" class="t20-camp-cb-inp" value="${uid}"${ck} /><span class="t20-camp-cb-nome">${nome}${pers ? ` · ${pers}` : ''}</span></label>`;
                })
                .join('');
        }

        async function carregarJogadoresCampanha(campanhaId) {
            const cid = Number(campanhaId);
            if (!Number.isFinite(cid) || cid <= 0) {
                jogadoresCampanha = [];
                renderChecklistJogadores([]);
                return;
            }
            try {
                const ps = new global.TormentaPersonagemService();
                const rows = await ps.listar({ campanha_id: cid, limit: 500 });
                const map = new Map();
                (Array.isArray(rows) ? rows : [])
                    .filter((p) => String(p.tipo || '').toLowerCase() === 'jogador')
                    .forEach((p) => {
                        const uid = Number(p.dono_id);
                        if (!Number.isFinite(uid) || uid <= 0 || map.has(uid)) return;
                        map.set(uid, p);
                    });
                jogadoresCampanha = Array.from(map.values());
            } catch (_e) {
                jogadoresCampanha = [];
            }
            renderChecklistJogadores(idsRevelacaoSelecionados());
        }

        function popularSelectCampanhasHandout() {
            const sel = q('t20campHandoutCampanhaId');
            if (!sel || !global.__t20DashCampanhas) return;
            const campanhas = global.__t20DashCampanhas.getCampanhas() || [];
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

        function resetFormHandout() {
            handoutEdicaoId = null;
            const hid = q('t20campHandoutId');
            const badge = q('t20campHandoutEdicaoBadge');
            const btnC = q('t20campBtnCancelarHandout');
            const salvar = q('t20campBtnSalvarHandout');
            if (hid) hid.value = '';
            if (badge) badge.style.display = 'none';
            if (btnC) btnC.style.display = 'none';
            if (q('t20campHandoutTitulo')) q('t20campHandoutTitulo').value = '';
            if (q('t20campHandoutCorpo')) q('t20campHandoutCorpo').value = '';
            if (q('t20campHandoutImagem')) q('t20campHandoutImagem').value = '';
            if (salvar) salvar.textContent = 'Criar handout';
            renderChecklistJogadores([]);
        }

        function editarHandout(hid) {
            const h = handouts.find((x) => Number(x.id) === hid);
            if (!h) return;
            handoutEdicaoId = hid;
            if (q('t20campHandoutId')) q('t20campHandoutId').value = String(hid);
            const badge = q('t20campHandoutEdicaoBadge');
            if (badge) {
                badge.style.display = '';
                badge.textContent = `Editando handout #${hid}`;
            }
            if (q('t20campBtnCancelarHandout')) q('t20campBtnCancelarHandout').style.display = '';
            if (q('t20campHandoutCampanhaId')) q('t20campHandoutCampanhaId').value = String(h.campanha_id || '');
            if (q('t20campHandoutTitulo')) q('t20campHandoutTitulo').value = h.titulo || '';
            if (q('t20campHandoutCorpo')) q('t20campHandoutCorpo').value = h.corpo_md || '';
            if (q('t20campHandoutImagem')) q('t20campHandoutImagem').value = h.imagem_url || '';
            if (q('t20campBtnSalvarHandout')) q('t20campBtnSalvarHandout').textContent = 'Salvar handout';
            void carregarJogadoresCampanha(h.campanha_id).then(() => {
                renderChecklistJogadores(h.visivel_para_user_ids || []);
            });
            const sub = q('t20campSubabaHandouts');
            const paneC = q('t20campSubabaCadastro');
            document.querySelectorAll('#t20campSubAbas [data-t20camp-sub]').forEach((b) => {
                b.classList.toggle('t20-camp-subaba-btn--active', b.getAttribute('data-t20camp-sub') === 'handouts');
            });
            if (sub) sub.classList.add('t20-camp-subaba-pane--active');
            if (paneC) paneC.classList.remove('t20-camp-subaba-pane--active');
        }

        async function excluirHandout(hid) {
            if (!global.confirm('Excluir este handout?')) return;
            try {
                await campSvc.deletarHandout(hid);
                Toast.success('Handout excluído.');
                await carregarHandouts();
                if (handoutEdicaoId === hid) resetFormHandout();
                void carregarLeituraJogador();
            } catch (e) {
                Toast.error(e.message || 'Erro ao excluir');
            }
        }

        function renderListaHandouts() {
            const lista = q('t20campListaHandouts');
            if (!lista) return;
            if (!handouts.length) {
                lista.innerHTML = '<p class="tormenta-cell-muted">Nenhum handout cadastrado.</p>';
                return;
            }
            lista.innerHTML = handouts
                .map((h) => {
                    const n = Array.isArray(h.visivel_para_user_ids) ? h.visivel_para_user_ids.length : 0;
                    const rev = n ? `Revelado para ${n} jogador(es)` : 'Rascunho (não revelado)';
                    return `<div class="t20-camp-card" data-hid="${h.id}">
                        <div class="t20-camp-card__hd"><strong>${esc(h.titulo)}</strong><span class="t20-camp-card__meta">${esc(h.campanha_nome || 'Campanha')} · ${rev}</span></div>
                        <div class="t20-handout-corpo-preview">${renderCorpoMd(h.corpo_md)}</div>
                        ${h.imagem_url ? `<p class="t20-dash-hint" style="margin:0.35rem 0 0"><a href="${esc(h.imagem_url)}" target="_blank" rel="noopener noreferrer">Ver imagem</a></p>` : ''}
                        <div class="t20-camp-card__ac">
                            <button type="button" class="tormenta-btn t20-camp-hand-editar" data-id="${h.id}">Editar / revelar</button>
                            <button type="button" class="tormenta-btn t20-camp-hand-excluir" data-id="${h.id}">Excluir</button>
                        </div>
                    </div>`;
                })
                .join('');
            lista.querySelectorAll('.t20-camp-hand-editar').forEach((btn) => {
                btn.addEventListener('click', () => editarHandout(Number(btn.getAttribute('data-id'))));
            });
            lista.querySelectorAll('.t20-camp-hand-excluir').forEach((btn) => {
                btn.addEventListener('click', () => excluirHandout(Number(btn.getAttribute('data-id'))));
            });
        }

        async function carregarHandouts() {
            const lista = q('t20campListaHandouts');
            if (!lista) return;
            lista.innerHTML = '<p class="tormenta-cell-muted">Carregando…</p>';
            try {
                handouts = await campSvc.listarHandouts();
                if (!Array.isArray(handouts)) handouts = [];
                renderListaHandouts();
                popularSelectCampanhasHandout();
            } catch (e) {
                lista.innerHTML = `<p class="tormenta-cell-muted">${esc(e.message || 'Erro')}</p>`;
            }
        }

        async function carregarLeituraJogador() {
            const host = q('t20campLeituraJogador');
            const listaH = q('t20campListaHandoutsJogador');
            const listaS = q('t20campListaSessoesJogador');
            if (!host) return;
            let temConteudo = false;
            if (listaH) {
                listaH.innerHTML = '<p class="tormenta-cell-muted">Carregando handouts…</p>';
            }
            if (listaS) {
                listaS.innerHTML = '<p class="tormenta-cell-muted">Carregando sessões…</p>';
            }
            try {
                const [hands, sess] = await Promise.all([
                    campSvc.listarHandoutsVisiveis(),
                    campSvc.listarSessoesVisiveis(),
                ]);
                const arrH = Array.isArray(hands) ? hands : [];
                const arrS = Array.isArray(sess) ? sess : [];
                temConteudo = arrH.length > 0 || arrS.length > 0;
                if (listaH) {
                    if (!arrH.length) {
                        listaH.innerHTML =
                            '<p class="tormenta-cell-muted">Nenhum handout revelado para você.</p>';
                    } else {
                        listaH.innerHTML = arrH
                            .map(
                                (h) => `<div class="t20-camp-card t20-camp-card--leitura">
                            <div class="t20-camp-card__hd"><strong>${esc(h.titulo)}</strong><span class="t20-camp-card__meta">${esc(h.campanha_nome || '')}</span></div>
                            <div class="t20-handout-corpo-preview">${renderCorpoMd(h.corpo_md)}</div>
                            ${h.imagem_url ? `<figure class="t20-handout-fig"><img src="${esc(h.imagem_url)}" alt="" loading="lazy" referrerpolicy="no-referrer" /></figure>` : ''}
                            <p class="t20-dash-hint" style="margin:0.35rem 0 0">${fmtData(h.updated_at || h.created_at)}</p>
                        </div>`
                            )
                            .join('');
                    }
                }
                if (listaS) {
                    if (!arrS.length) {
                        listaS.innerHTML =
                            '<p class="tormenta-cell-muted">Nenhum resumo de sessão disponível.</p>';
                    } else {
                        listaS.innerHTML = arrS
                            .map(
                                (s) => `<div class="t20-camp-card t20-camp-card--leitura">
                            <div class="t20-camp-card__hd"><strong>${esc(s.campanha_nome || 'Campanha')}</strong></div>
                            <p class="t20-camp-card__desc">${esc(s.resumo || '')}</p>
                            <p class="t20-dash-hint" style="margin:0.35rem 0 0">${fmtData(s.created_at)}</p>
                        </div>`
                            )
                            .join('');
                    }
                }
            } catch (e) {
                if (listaH) listaH.innerHTML = `<p class="tormenta-cell-muted">${esc(e.message)}</p>`;
                if (listaS) listaS.innerHTML = '';
            }
            host.hidden = !temConteudo;
        }

        q('t20campHandoutCampanhaId')?.addEventListener('change', (ev) => {
            void carregarJogadoresCampanha(ev.target.value);
        });

        q('t20campBtnRevelarTodosHandout')?.addEventListener('click', () => {
            document
                .querySelectorAll('#t20campHandoutJogadores .t20-camp-cb-inp')
                .forEach((inp) => {
                    inp.checked = true;
                });
        });

        q('t20campBtnOcultarTodosHandout')?.addEventListener('click', () => {
            document
                .querySelectorAll('#t20campHandoutJogadores .t20-camp-cb-inp')
                .forEach((inp) => {
                    inp.checked = false;
                });
        });

        q('t20campFormHandout')?.addEventListener('submit', async (ev) => {
            ev.preventDefault();
            const campanhaId = Math.floor(Number(q('t20campHandoutCampanhaId')?.value || 0));
            const titulo = (q('t20campHandoutTitulo')?.value || '').trim();
            const corpo_md = (q('t20campHandoutCorpo')?.value || '').trim();
            const imagem_url = (q('t20campHandoutImagem')?.value || '').trim();
            const visivel_para_user_ids = idsRevelacaoSelecionados();
            if (!campanhaId) {
                Toast.error('Selecione a campanha.');
                return;
            }
            if (!titulo) {
                Toast.error('Informe o título.');
                return;
            }
            if (!corpo_md && !imagem_url) {
                Toast.error('Informe texto ou URL de imagem.');
                return;
            }
            const payload = {
                campanha_id: campanhaId,
                titulo,
                corpo_md,
                imagem_url: imagem_url || null,
                visivel_para_user_ids,
            };
            try {
                if (handoutEdicaoId) {
                    await campSvc.atualizarHandout(handoutEdicaoId, payload);
                    Toast.success('Handout atualizado.');
                } else {
                    await campSvc.criarHandout(payload);
                    Toast.success('Handout criado.');
                }
                resetFormHandout();
                await carregarHandouts();
                void carregarLeituraJogador();
            } catch (e) {
                Toast.error(e.message || 'Erro ao salvar');
            }
        });

        q('t20campBtnCancelarHandout')?.addEventListener('click', () => resetFormHandout());

        global.__t20DashHandouts = {
            carregarHandouts,
            carregarLeituraJogador,
            resetFormHandout,
        };

        resetFormHandout();
    };
})(typeof window !== 'undefined' ? window : globalThis);
