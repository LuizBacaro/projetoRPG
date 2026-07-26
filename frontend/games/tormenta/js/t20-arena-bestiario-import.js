/**
 * RF-T12g — importar criatura do bestiário T20 v1.3 → combatente na arena.
 *
 * A API pagina (skip/limit); o modal busca o resultado filtrado completo
 * (até LIST_LIMIT) para a barra de rolagem listar todas as criaturas.
 */
(function (global) {
    'use strict';

    /** Limite da API (max 200); cobre o catálogo v1.3 (~80). */
    const LIST_LIMIT = 200;
    const TIPOS = [
        '',
        'Animal',
        'Construto',
        'Criatura',
        'Dragão',
        'Espírito',
        'Humanoide',
        'Monstro',
        'Morto-vivo',
    ];

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

    function rotuloNd(item) {
        if (item && item.nd_rotulo) return String(item.nd_rotulo);
        if (item && item.nd != null) return String(item.nd);
        return '';
    }

    let slugSelecionado = null;
    let debounceTimer = null;
    let total = 0;
    let lastTermo = '';
    let carregando = false;

    function filtrosAtuais() {
        const tipo = q('t20BestiarioFiltroTipo')?.value?.trim() || '';
        const ndMinRaw = q('t20BestiarioNdMin')?.value;
        const ndMaxRaw = q('t20BestiarioNdMax')?.value;
        const ndMin = ndMinRaw !== '' && ndMinRaw != null ? Number(ndMinRaw) : undefined;
        const ndMax = ndMaxRaw !== '' && ndMaxRaw != null ? Number(ndMaxRaw) : undefined;
        return {
            tipo: tipo || undefined,
            nd_min: Number.isFinite(ndMin) ? ndMin : undefined,
            nd_max: Number.isFinite(ndMax) ? ndMax : undefined,
        };
    }

    function atualizarContagem(visiveis) {
        const info = q('t20BestiarioPagerInfo');
        if (!info) return;
        if (!total) {
            info.textContent = '0 criaturas';
            return;
        }
        if (visiveis < total) {
            info.textContent = `${visiveis} de ${total} (role a lista · filtros ativos)`;
        } else {
            info.textContent = `${total} criatura${total === 1 ? '' : 's'} — role a lista`;
        }
    }

    function renderLista(itens) {
        const host = q('t20BestiarioLista');
        if (!host) return;
        if (!itens.length) {
            host.innerHTML = '<p class="t20-dash-hint">Nenhuma criatura encontrada.</p>';
            atualizarContagem(0);
            return;
        }
        host.innerHTML = itens
            .map((item) => {
                const slug = esc(item.slug);
                const nome = esc(item.nome);
                const nd = rotuloNd(item) ? `ND ${esc(rotuloNd(item))}` : '';
                const tipo = item.tipo_criatura ? esc(item.tipo_criatura) : '';
                const meta = [
                    nd,
                    tipo,
                    item.pv_max != null ? `PV ${esc(item.pv_max)}` : '',
                    item.ca != null ? `Defesa ${esc(item.ca)}` : '',
                ]
                    .filter(Boolean)
                    .join(' · ');
                const active = slugSelecionado === item.slug ? ' is-active' : '';
                return `<button type="button" class="t20-bestiario-item${active}" data-slug="${slug}" title="${esc(item.descricao_curta || '')}"><span class="t20-bestiario-item-nome">${nome}</span><span class="t20-bestiario-item-meta">${meta}</span></button>`;
            })
            .join('');
        host.querySelectorAll('.t20-bestiario-item').forEach((btn) => {
            if (btn.dataset.bound) return;
            btn.dataset.bound = '1';
            btn.addEventListener('click', () => {
                void selecionarCriatura(btn.getAttribute('data-slug'));
            });
        });
        atualizarContagem(itens.length);
        host.scrollTop = 0;
    }

    function renderPreview(det) {
        const host = q('t20BestiarioPreview');
        const btn = q('t20BestiarioBtnImportar');
        if (!host) return;
        if (!det) {
            host.innerHTML = '<p class="t20-dash-hint">Selecione uma criatura para ver os detalhes.</p>';
            if (btn) btn.disabled = true;
            return;
        }
        const ndLabel = rotuloNd(det);
        const attrs = `FOR ${det.for_valor} · DES ${det.des_valor} · CON ${det.con_valor} · INT ${det.int_valor} · SAB ${det.sab_valor} · CAR ${det.car_valor}`;
        const resist = `Fort ${det.fort_total} · Ref ${det.ref_total} · Von ${det.von_total}`;
        const ataques = Array.isArray(det.ataques) ? det.ataques : [];
        const atqHtml = ataques.length
            ? `<table class="t20-bestiario-atq-table"><thead><tr><th>Ataque</th><th>Bônus</th><th>Dano</th></tr></thead><tbody>${ataques
                  .map(
                      (a) =>
                          `<tr><td>${esc(a.nome)}</td><td>${esc(a.bonus_ataque)}</td><td>${esc(a.dano)}</td></tr>`
                  )
                  .join('')}</tbody></table>`
            : '<p class="t20-dash-hint">Sem ataques catalogados.</p>';
        host.innerHTML = `
            <h4 class="t20-bestiario-prev-nome">${esc(det.nome)}</h4>
            <p class="t20-bestiario-prev-meta">${esc(det.tipo_criatura || '')}${ndLabel ? ` · ND ${esc(ndLabel)}` : ''} · PV ${esc(det.pv_max)} · Defesa ${esc(det.ca)} · Ini ${esc(det.iniciativa)}</p>
            <p class="t20-bestiario-prev-linha">${esc(attrs)}</p>
            <p class="t20-bestiario-prev-linha">${esc(resist)}</p>
            ${det.descricao_curta ? `<p class="t20-bestiario-prev-desc">${esc(det.descricao_curta)}</p>` : ''}
            ${det.pagina_referencia ? `<p class="t20-bestiario-prev-linha">${esc(det.pagina_referencia)}</p>` : ''}
            ${atqHtml}
        `;
        if (btn) btn.disabled = false;
    }

    async function buscarLista(termo) {
        if (carregando) return;
        carregando = true;
        lastTermo = termo || '';
        const host = q('t20BestiarioLista');
        if (host) host.innerHTML = '<p class="t20-dash-hint">Buscando…</p>';
        try {
            const filtros = filtrosAtuais();
            const data = await new global.TormentaRegrasService().listarBestiarioCatalogo({
                q: lastTermo || undefined,
                skip: 0,
                limit: LIST_LIMIT,
                tipo: filtros.tipo,
                nd_min: filtros.nd_min,
                nd_max: filtros.nd_max,
            });
            const itens = data && Array.isArray(data.itens) ? data.itens : [];
            total = data && data.total != null ? Number(data.total) : itens.length;
            if (!Number.isFinite(total)) total = itens.length;
            renderLista(itens);
            if (slugSelecionado && !itens.some((x) => x.slug === slugSelecionado)) {
                slugSelecionado = null;
                renderPreview(null);
            }
        } catch (e) {
            if (host) host.innerHTML = `<p class="t20-dash-hint">${esc(e.message || 'Erro na busca')}</p>`;
            total = 0;
            atualizarContagem(0);
        } finally {
            carregando = false;
        }
    }

    async function selecionarCriatura(slug) {
        slugSelecionado = String(slug || '').trim() || null;
        document.querySelectorAll('.t20-bestiario-item').forEach((btn) => {
            btn.classList.toggle('is-active', btn.getAttribute('data-slug') === slugSelecionado);
        });
        const prev = q('t20BestiarioPreview');
        if (prev) prev.innerHTML = '<p class="t20-dash-hint">Carregando…</p>';
        if (!slugSelecionado) {
            renderPreview(null);
            return;
        }
        try {
            const det = await new global.TormentaRegrasService().obterBestiarioDetalhe(slugSelecionado);
            renderPreview(det);
        } catch (e) {
            if (prev) prev.innerHTML = `<p class="t20-dash-hint">${esc(e.message || 'Erro')}</p>`;
        }
    }

    function popularFiltroTipo() {
        const sel = q('t20BestiarioFiltroTipo');
        if (!sel || sel.dataset.ready) return;
        sel.innerHTML = TIPOS.map((t) =>
            t ? `<option value="${esc(t)}">${esc(t)}</option>` : '<option value="">Todos os tipos</option>'
        ).join('');
        sel.dataset.ready = '1';
    }

    function abrirModal() {
        const dlg = q('t20DialogBestiario');
        if (!dlg || typeof dlg.showModal !== 'function') return;
        slugSelecionado = null;
        total = 0;
        popularFiltroTipo();
        const nomeInp = q('t20BestiarioNomeOverride');
        const busca = q('t20BestiarioBusca');
        const tipo = q('t20BestiarioFiltroTipo');
        const ndMin = q('t20BestiarioNdMin');
        const ndMax = q('t20BestiarioNdMax');
        if (nomeInp) nomeInp.value = '';
        if (busca) busca.value = '';
        if (tipo) tipo.value = '';
        if (ndMin) ndMin.value = '';
        if (ndMax) ndMax.value = '';
        renderPreview(null);
        void buscarLista('');
        dlg.showModal();
    }

    function fecharModal() {
        const dlg = q('t20DialogBestiario');
        if (dlg && typeof dlg.close === 'function') dlg.close();
    }

    global.__t20ArenaBestiarioImport = {
        _bound: false,

        bindOnce(opts) {
            if (this._bound) return;
            this._bound = true;
            const Toast = (opts && opts.Toast) || global.Toast;
            const getCampanhaId = opts && opts.getCampanhaId;
            const onImported = opts && opts.onImported;

            q('t20ArenaBtnBestiario')?.addEventListener('click', () => {
                const cid = getCampanhaId ? getCampanhaId() : null;
                if (!cid) {
                    if (Toast && Toast.warning) Toast.warning('Selecione uma campanha como mestre primeiro.');
                    return;
                }
                abrirModal();
            });

            q('t20BestiarioFechar')?.addEventListener('click', fecharModal);
            q('t20BestiarioCancelar')?.addEventListener('click', fecharModal);

            const busca = q('t20BestiarioBusca');
            busca?.addEventListener('input', () => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    void buscarLista(busca.value.trim());
                }, 280);
            });

            ['t20BestiarioFiltroTipo', 't20BestiarioNdMin', 't20BestiarioNdMax'].forEach((id) => {
                q(id)?.addEventListener('change', () => {
                    void buscarLista(busca?.value?.trim() || '');
                });
            });

            q('t20BestiarioBtnImportar')?.addEventListener('click', async () => {
                const slug = slugSelecionado;
                const cid = getCampanhaId ? Number(getCampanhaId()) : null;
                if (!slug) {
                    if (Toast && Toast.error) Toast.error('Selecione uma criatura.');
                    return;
                }
                if (!Number.isFinite(cid) || cid <= 0) {
                    if (Toast && Toast.error) Toast.error('Campanha inválida.');
                    return;
                }
                const btn = q('t20BestiarioBtnImportar');
                const nomeOverride = q('t20BestiarioNomeOverride')?.value?.trim() || undefined;
                if (btn) btn.disabled = true;
                try {
                    const payload = {
                        slug,
                        tipo: 'monstro',
                        campanha_id: cid,
                    };
                    if (nomeOverride) payload.nome_override = nomeOverride;
                    const criado = await new global.TormentaPersonagemService().importarBestiario(payload);
                    fecharModal();
                    if (Toast && Toast.success) {
                        Toast.success(`«${criado.nome || slug}» adicionado à mesa.`);
                    }
                    if (typeof onImported === 'function') {
                        await onImported(criado);
                    }
                } catch (e) {
                    if (Toast && Toast.error) Toast.error(e.message || 'Erro ao importar');
                } finally {
                    if (btn) btn.disabled = !slugSelecionado;
                }
            });
        },
    };
})(typeof window !== 'undefined' ? window : globalThis);
