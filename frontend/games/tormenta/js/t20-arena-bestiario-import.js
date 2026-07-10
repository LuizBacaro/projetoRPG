/**
 * RF-T12g — importar criatura do bestiário stub → combatente na arena.
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

    let slugSelecionado = null;
    let debounceTimer = null;

    function renderLista(itens) {
        const host = q('t20BestiarioLista');
        if (!host) return;
        if (!itens.length) {
            host.innerHTML = '<p class="t20-dash-hint">Nenhuma criatura encontrada.</p>';
            return;
        }
        host.innerHTML = itens
            .map((item) => {
                const slug = esc(item.slug);
                const nome = esc(item.nome);
                const nd = item.nd != null ? `ND ${esc(item.nd)}` : '';
                const tipo = item.tipo_criatura ? esc(item.tipo_criatura) : '';
                const meta = [nd, tipo, item.pv_max != null ? `PV ${esc(item.pv_max)}` : '', item.ca != null ? `CA ${esc(item.ca)}` : '']
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
            <p class="t20-bestiario-prev-meta">${esc(det.tipo_criatura || '')}${det.nd != null ? ` · ND ${esc(det.nd)}` : ''} · PV ${esc(det.pv_max)} · CA ${esc(det.ca)} · Ini ${esc(det.iniciativa)}</p>
            <p class="t20-bestiario-prev-linha">${esc(attrs)}</p>
            <p class="t20-bestiario-prev-linha">${esc(resist)}</p>
            ${det.descricao_curta ? `<p class="t20-bestiario-prev-desc">${esc(det.descricao_curta)}</p>` : ''}
            ${atqHtml}
        `;
        if (btn) btn.disabled = false;
    }

    async function buscarLista(termo) {
        const host = q('t20BestiarioLista');
        if (host) host.innerHTML = '<p class="t20-dash-hint">Buscando…</p>';
        try {
            const data = await new global.TormentaRegrasService().listarBestiarioCatalogo({
                q: termo || undefined,
                limit: 50,
            });
            const itens = data && Array.isArray(data.itens) ? data.itens : [];
            renderLista(itens);
            if (slugSelecionado && !itens.some((x) => x.slug === slugSelecionado)) {
                slugSelecionado = null;
                renderPreview(null);
            }
        } catch (e) {
            if (host) host.innerHTML = `<p class="t20-dash-hint">${esc(e.message || 'Erro na busca')}</p>`;
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

    function abrirModal() {
        const dlg = q('t20DialogBestiario');
        if (!dlg || typeof dlg.showModal !== 'function') return;
        slugSelecionado = null;
        const nomeInp = q('t20BestiarioNomeOverride');
        const busca = q('t20BestiarioBusca');
        if (nomeInp) nomeInp.value = '';
        if (busca) busca.value = '';
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
