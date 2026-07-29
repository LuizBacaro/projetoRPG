/**
 * RF-M06 — importar criatura do Livro dos Monstros → combatente monstro.
 */
(function (global) {
    'use strict';

    const LIST_LIMIT = 200;
    const TIPOS = [
        '',
        'Animal',
        'Dragão',
        'Elemental',
        'Extra-planar',
        'Gigante',
        'Humanoide',
        'Inseto',
        'Limo',
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

    function importavel(det) {
        if (!det) return false;
        if (det.nd == null && !det.categoria_idade) return false;
        return true;
    }

    let slugSelecionado = null;
    let detalheAtual = null;
    let debounceTimer = null;
    let total = 0;
    let lastTermo = '';
    let carregando = false;

    function filtrosAtuais() {
        const tipo = q('d35BestiarioFiltroTipo')?.value?.trim() || '';
        const ndMinRaw = q('d35BestiarioNdMin')?.value;
        const ndMaxRaw = q('d35BestiarioNdMax')?.value;
        const ndMin = ndMinRaw !== '' && ndMinRaw != null ? Number(ndMinRaw) : undefined;
        const ndMax = ndMaxRaw !== '' && ndMaxRaw != null ? Number(ndMaxRaw) : undefined;
        return {
            tipo: tipo || undefined,
            nd_min: Number.isFinite(ndMin) ? ndMin : undefined,
            nd_max: Number.isFinite(ndMax) ? ndMax : undefined,
        };
    }

    function atualizarContagem(visiveis) {
        const info = q('d35BestiarioPagerInfo');
        if (!info) return;
        if (!total) {
            info.textContent = '0 criaturas';
            return;
        }
        if (visiveis < total) {
            info.textContent = `${visiveis} de ${total} (filtros ativos)`;
        } else {
            info.textContent = `${total} criatura${total === 1 ? '' : 's'}`;
        }
    }

    function renderLista(itens) {
        const host = q('d35BestiarioLista');
        if (!host) return;
        if (!itens.length) {
            host.innerHTML = '<p class="d35-bestiario-hint">Nenhuma criatura encontrada.</p>';
            atualizarContagem(0);
            return;
        }
        host.innerHTML = itens
            .map((item) => {
                const slug = esc(item.slug);
                const nome = esc(item.nome);
                const nd = rotuloNd(item) ? `ND ${esc(rotuloNd(item))}` : 'espécie-pai';
                const tipo = item.tipo_criatura ? esc(item.tipo_criatura) : '';
                const meta = [
                    nd,
                    tipo,
                    item.hp_maximo != null ? `PV ${esc(item.hp_maximo)}` : '',
                    item.ca != null ? `CA ${esc(item.ca)}` : '',
                ]
                    .filter(Boolean)
                    .join(' · ');
                const active = slugSelecionado === item.slug ? ' is-active' : '';
                return `<button type="button" class="d35-bestiario-item${active}" data-slug="${slug}"><span class="d35-bestiario-item-nome">${nome}</span><span class="d35-bestiario-item-meta">${meta}</span></button>`;
            })
            .join('');
        host.querySelectorAll('.d35-bestiario-item').forEach((btn) => {
            if (btn.dataset.bound) return;
            btn.dataset.bound = '1';
            btn.addEventListener('click', () => {
                void selecionarCriatura(btn.getAttribute('data-slug'));
            });
        });
        atualizarContagem(itens.length);
        host.scrollTop = 0;
    }

    function renderBloco(det) {
        const pre = q('d35BestiarioBloco');
        if (!pre) return;
        const gerador = global.DnD35BlocoMonstro;
        if (!det || !gerador || typeof gerador.gerar !== 'function') {
            pre.textContent = '';
            return;
        }
        pre.textContent = gerador.gerar(det);
    }

    function renderPreview(det) {
        const host = q('d35BestiarioPreview');
        const btn = q('d35BestiarioBtnImportar');
        detalheAtual = det || null;
        if (!host) return;
        if (!det) {
            host.innerHTML = '<p class="d35-bestiario-hint">Selecione uma criatura para ver os detalhes.</p>';
            if (btn) btn.disabled = true;
            renderBloco(null);
            return;
        }
        const ndLabel = rotuloNd(det);
        const attrs = `FOR ${det.for_valor} · DES ${det.des_valor} · CON ${det.con_valor} · INT ${det.int_valor} · SAB ${det.sab_valor} · CAR ${det.car_valor}`;
        const resist = `Fort ${det.fortitude} · Ref ${det.reflexos} · Von ${det.vontade}`;
        const def =
            det.ca != null
                ? `CA ${det.ca} (toque ${det.toque ?? '—'}, surpresa ${det.surpresa ?? '—'})`
                : '';
        const ataques = Array.isArray(det.ataques) ? det.ataques : [];
        const atqHtml = ataques.length
            ? `<table class="d35-bestiario-atq-table"><thead><tr><th>Ataque</th><th>Bônus</th><th>Dano</th></tr></thead><tbody>${ataques
                  .map(
                      (a) =>
                          `<tr><td>${esc(a.nome)}</td><td>${esc(a.bonus_ataque)}</td><td>${esc(a.dano)}</td></tr>`
                  )
                  .join('')}</tbody></table>`
            : '<p class="d35-bestiario-hint">Sem ataques catalogados.</p>';
        const avisoPai =
            !importavel(det)
                ? '<p class="d35-bestiario-aviso">Espécie-pai: importe uma linha por idade (ex.: jovem).</p>'
                : '';
        host.innerHTML = `
            <h4 class="d35-bestiario-prev-nome">${esc(det.nome)}</h4>
            <p class="d35-bestiario-prev-meta">${esc(det.tipo_criatura || '')}${ndLabel ? ` · ND ${esc(ndLabel)}` : ''}${det.hp_maximo != null ? ` · PV ${esc(det.hp_maximo)}` : ''} · Ini ${esc(det.iniciativa ?? '—')}</p>
            <p class="d35-bestiario-prev-linha">${esc(def)}</p>
            <p class="d35-bestiario-prev-linha">${esc(attrs)}</p>
            <p class="d35-bestiario-prev-linha">${esc(resist)}</p>
            ${det.pagina_referencia ? `<p class="d35-bestiario-prev-linha">${esc(det.pagina_referencia)}</p>` : ''}
            ${avisoPai}
            ${atqHtml}
        `;
        renderBloco(det);
        if (btn) btn.disabled = !importavel(det);
    }

    async function buscarLista(termo) {
        if (carregando) return;
        carregando = true;
        lastTermo = termo || '';
        const host = q('d35BestiarioLista');
        if (host) host.innerHTML = '<p class="d35-bestiario-hint">Buscando…</p>';
        try {
            const filtros = filtrosAtuais();
            const data = await new global.DnD35RegrasService().listarBestiarioCatalogo({
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
            if (host) host.innerHTML = `<p class="d35-bestiario-hint">${esc(e.message || 'Erro na busca')}</p>`;
            total = 0;
            atualizarContagem(0);
        } finally {
            carregando = false;
        }
    }

    async function selecionarCriatura(slug) {
        slugSelecionado = String(slug || '').trim() || null;
        document.querySelectorAll('.d35-bestiario-item').forEach((btn) => {
            btn.classList.toggle('is-active', btn.getAttribute('data-slug') === slugSelecionado);
        });
        const prev = q('d35BestiarioPreview');
        if (prev) prev.innerHTML = '<p class="d35-bestiario-hint">Carregando…</p>';
        if (!slugSelecionado) {
            renderPreview(null);
            return;
        }
        try {
            const det = await new global.DnD35RegrasService().obterBestiarioDetalhe(slugSelecionado);
            renderPreview(det);
        } catch (e) {
            if (prev) prev.innerHTML = `<p class="d35-bestiario-hint">${esc(e.message || 'Erro')}</p>`;
            if (q('d35BestiarioBtnImportar')) q('d35BestiarioBtnImportar').disabled = true;
        }
    }

    function popularFiltroTipo() {
        const sel = q('d35BestiarioFiltroTipo');
        if (!sel || sel.dataset.ready) return;
        sel.innerHTML = TIPOS.map((t) => {
            if (!t) return '<option value="">Todos os tipos</option>';
            return `<option value="${esc(t)}">${esc(t)}</option>`;
        }).join('');
        sel.dataset.ready = '1';
    }

    function limparCamposExtras() {
        const nomeInp = q('d35BestiarioNomeOverride');
        const fotoFile = q('inputFotoBestiario');
        const ph = q('uploadPlaceholderBestiario');
        const pv = q('uploadPreviewBestiario');
        if (nomeInp) nomeInp.value = '';
        if (fotoFile) fotoFile.value = '';
        if (ph) ph.style.display = 'flex';
        if (pv) pv.style.display = 'none';
    }

    function abrirModal() {
        const overlay = q('modalBestiarioMm35');
        if (!overlay) return;
        slugSelecionado = null;
        detalheAtual = null;
        total = 0;
        popularFiltroTipo();
        limparCamposExtras();
        const busca = q('d35BestiarioBusca');
        const tipo = q('d35BestiarioFiltroTipo');
        const ndMin = q('d35BestiarioNdMin');
        const ndMax = q('d35BestiarioNdMax');
        if (busca) busca.value = '';
        if (tipo) tipo.value = '';
        if (ndMin) ndMin.value = '';
        if (ndMax) ndMax.value = '';
        renderPreview(null);
        void buscarLista('');
        overlay.classList.add('show');
    }

    function fecharModal() {
        const overlay = q('modalBestiarioMm35');
        if (overlay) overlay.classList.remove('show');
    }

    global.__d35ArenaBestiarioImport = {
        _bound: false,
        abrir: abrirModal,
        fechar: fecharModal,

        bindOnce(opts) {
            if (this._bound) return;
            this._bound = true;
            const Toast = (opts && opts.Toast) || global.Toast;
            const importarFn = opts && opts.importarBestiario;
            const enviarFotoFn = opts && opts.enviarFoto;
            const onImported = opts && opts.onImported;
            const podeAbrir = opts && opts.podeAbrir;

            q('btnTipoBestiario')?.addEventListener('click', () => {
                if (typeof podeAbrir === 'function' && !podeAbrir()) {
                    if (Toast && Toast.error) {
                        Toast.error('Acesso restrito: apenas Mestre pode importar do bestiário.');
                    }
                    return;
                }
                if (opts && typeof opts.fecharSeletor === 'function') opts.fecharSeletor();
                abrirModal();
            });

            q('d35BestiarioFechar')?.addEventListener('click', fecharModal);
            q('d35BestiarioCancelar')?.addEventListener('click', fecharModal);

            const busca = q('d35BestiarioBusca');
            busca?.addEventListener('input', () => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    void buscarLista(busca.value.trim());
                }, 280);
            });

            ['d35BestiarioFiltroTipo', 'd35BestiarioNdMin', 'd35BestiarioNdMax'].forEach((id) => {
                q(id)?.addEventListener('change', () => {
                    void buscarLista(busca?.value?.trim() || '');
                });
            });

            q('d35BestiarioBtnCopiarBloco')?.addEventListener('click', async () => {
                const texto = q('d35BestiarioBloco')?.textContent || '';
                if (!texto.trim()) {
                    if (Toast && Toast.info) Toast.info('Selecione uma criatura primeiro.');
                    return;
                }
                try {
                    await navigator.clipboard.writeText(texto);
                    if (Toast && Toast.success) Toast.success('Bloco copiado.');
                } catch {
                    if (Toast && Toast.error) Toast.error('Não foi possível copiar.');
                }
            });

            q('d35BestiarioBtnImportar')?.addEventListener('click', async () => {
                const slug = slugSelecionado;
                if (!slug || !importavel(detalheAtual)) {
                    if (Toast && Toast.error) Toast.error('Selecione uma criatura importável.');
                    return;
                }
                if (typeof importarFn !== 'function') {
                    if (Toast && Toast.error) Toast.error('Serviço de importação indisponível.');
                    return;
                }
                const btn = q('d35BestiarioBtnImportar');
                const nomeOverride = q('d35BestiarioNomeOverride')?.value?.trim() || undefined;
                const fotoFile = q('inputFotoBestiario')?.files?.[0] || null;
                if (btn) btn.disabled = true;
                try {
                    const payload = { slug, tipo: 'monstro' };
                    if (nomeOverride) payload.nome_override = nomeOverride;
                    let criado = await importarFn(payload);
                    if (fotoFile && criado && criado.id != null && typeof enviarFotoFn === 'function') {
                        try {
                            criado = await enviarFotoFn(criado.id, fotoFile);
                        } catch (upErr) {
                            if (Toast && Toast.warning) {
                                Toast.warning(
                                    `Criatura adicionada, mas a foto falhou: ${upErr.message || 'erro no upload'}`
                                );
                            } else if (Toast && Toast.info) {
                                Toast.info(
                                    `Criatura adicionada, mas a foto falhou: ${upErr.message || 'erro no upload'}`
                                );
                            }
                        }
                    }
                    fecharModal();
                    if (Toast && Toast.success) {
                        Toast.success(`«${criado.nome || slug}» adicionado.`);
                    }
                    if (typeof onImported === 'function') {
                        await onImported(criado);
                    }
                } catch (e) {
                    if (Toast && Toast.error) Toast.error(e.message || 'Erro ao importar');
                } finally {
                    if (btn) btn.disabled = !importavel(detalheAtual);
                }
            });
        },
    };
})(typeof window !== 'undefined' ? window : globalThis);
