/**
 * Modal de catálogo (equipamentos / consumíveis) — layout alinhado à ficha 3.5.
 */
const F5E_CAT_ESC = (s) => {
    if (typeof window !== 'undefined' && typeof window.escapeHtml === 'function') {
        return window.escapeHtml(String(s ?? ''));
    }
    return String(s ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
};

class Dnd5eFichaCatalogoModal {
    constructor() {
        this._itens = [];
        this._onConfirm = null;
        this._filtroExtra = null;
        this._ensureDom();
        this._bind();
    }

    _ensureDom() {
        if (document.getElementById('f5eModalCatalogo')) return;
        const wrap = document.createElement('div');
        wrap.id = 'f5eModalCatalogo';
        wrap.className = 'equipamentos-overlay';
        wrap.style.display = 'none';
        wrap.innerHTML = `
            <div class="equipamentos-container">
                <div class="equipamentos-header">
                    <div class="equipamentos-header-esquerda">
                        <span class="equipamentos-icone" id="f5eModalCatalogoIcone">🎒</span>
                        <div>
                            <h2 class="equipamentos-titulo" id="f5eModalCatalogoTitulo">Catálogo</h2>
                            <p class="equipamentos-subtitulo" id="f5eModalCatalogoSub">Selecione um item</p>
                        </div>
                    </div>
                    <button type="button" class="equipamentos-fechar" id="f5eModalCatalogoFechar" aria-label="Fechar">✕</button>
                </div>
                <div class="equipamentos-controles">
                    <div class="equipamentos-busca-wrapper">
                        <span class="equipamentos-busca-label">🔍 Buscar</span>
                        <input type="text" id="f5eModalCatalogoBusca" class="equipamentos-busca" placeholder="Nome do item..." />
                    </div>
                    <div class="equipamentos-quantidade-wrapper">
                        <label class="equipamentos-label" for="f5eModalCatalogoQtd">Quantidade:</label>
                        <input type="number" id="f5eModalCatalogoQtd" class="equipamentos-input-qtd" value="1" min="1" max="999" />
                    </div>
                </div>
                <div id="f5eModalCatalogoFiltros" class="consumiveis-filtros" hidden></div>
                <div class="equipamentos-corpo">
                    <div class="equipamentos-conteudo ativo">
                        <div class="equipamentos-lista talentos-lista-linhas" id="f5eModalCatalogoLista"></div>
                    </div>
                </div>
            </div>`;
        document.body.appendChild(wrap);
    }

    _bind() {
        document.getElementById('f5eModalCatalogoFechar')?.addEventListener('click', () => this.fechar());
        document.getElementById('f5eModalCatalogo')?.addEventListener('click', (e) => {
            if (e.target.id === 'f5eModalCatalogo') this.fechar();
        });
        document.getElementById('f5eModalCatalogoBusca')?.addEventListener('input', () => this._renderLista());
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this._aberto()) this.fechar();
        });
    }

    _aberto() {
        const m = document.getElementById('f5eModalCatalogo');
        return m && m.style.display !== 'none';
    }

    /**
     * @param {object} opts
     * @param {string} opts.titulo
     * @param {string} [opts.subtitulo]
     * @param {string} [opts.icone]
     * @param {Array} opts.itens — catálogo { slug, nome, categoria?, peso_lb?, custo? }
     * @param {function(slug, qtd, item): void} opts.onConfirm
     * @param {Array<{id:string,label:string,fn:Function}>} [opts.filtros]
     */
    abrir(opts) {
        this._itens = opts.itens || [];
        this._onConfirm = opts.onConfirm || null;
        this._filtroAtivo = 'todos';
        this._filtrosConfig = opts.filtros || null;

        const icon = document.getElementById('f5eModalCatalogoIcone');
        const tit = document.getElementById('f5eModalCatalogoTitulo');
        const sub = document.getElementById('f5eModalCatalogoSub');
        const busca = document.getElementById('f5eModalCatalogoBusca');
        const qtd = document.getElementById('f5eModalCatalogoQtd');

        if (icon) icon.textContent = opts.icone || '🎒';
        if (tit) tit.textContent = opts.titulo || 'Catálogo';
        if (sub) sub.textContent = opts.subtitulo || 'Selecione um item para adicionar';
        if (busca) busca.value = '';
        if (qtd) qtd.value = '1';

        this._renderFiltros();
        this._renderLista();

        const modal = document.getElementById('f5eModalCatalogo');
        if (modal) modal.style.display = 'flex';
        busca?.focus();
    }

    fechar() {
        const modal = document.getElementById('f5eModalCatalogo');
        if (modal) modal.style.display = 'none';
        this._onConfirm = null;
    }

    _renderFiltros() {
        const host = document.getElementById('f5eModalCatalogoFiltros');
        if (!host) return;
        if (!this._filtrosConfig?.length) {
            host.hidden = true;
            host.innerHTML = '';
            return;
        }
        host.hidden = false;
        host.innerHTML = this._filtrosConfig
            .map(
                (f) =>
                    `<button type="button" class="consumiveis-filtro-btn${
                        f.id === this._filtroAtivo ? ' ativo' : ''
                    }" data-filtro-id="${F5E_CAT_ESC(f.id)}">${F5E_CAT_ESC(f.label)}</button>`
            )
            .join('');
        host.querySelectorAll('[data-filtro-id]').forEach((btn) => {
            btn.addEventListener('click', () => {
                this._filtroAtivo = btn.dataset.filtroId;
                host.querySelectorAll('.consumiveis-filtro-btn').forEach((b) => b.classList.remove('ativo'));
                btn.classList.add('ativo');
                this._renderLista();
            });
        });
    }

    _itensFiltrados() {
        const termo = String(document.getElementById('f5eModalCatalogoBusca')?.value || '')
            .trim()
            .toLowerCase();
        let lista = [...this._itens];
        if (this._filtrosConfig?.length) {
            const filtro = this._filtrosConfig.find((f) => f.id === this._filtroAtivo);
            if (filtro?.fn) lista = lista.filter(filtro.fn);
        }
        if (termo) {
            lista = lista.filter((i) => {
                const nome = String(i.nome || '').toLowerCase();
                const cat = String(i.categoria || '').toLowerCase();
                return nome.includes(termo) || cat.includes(termo);
            });
        }
        return lista;
    }

    _renderLista() {
        const lista = document.getElementById('f5eModalCatalogoLista');
        if (!lista) return;
        const filtrados = this._itensFiltrados();
        if (!filtrados.length) {
            lista.innerHTML =
                '<p class="equipamentos-vazio">Nenhum item corresponde à busca.</p>';
            return;
        }
        lista.innerHTML = filtrados
            .map((item) => {
                const meta = [item.categoria, item.peso_lb != null ? `${item.peso_lb} lb` : null]
                    .filter(Boolean)
                    .join(' · ');
                const custo = item.custo ? `<span class="talento-linha-secao">${F5E_CAT_ESC(item.custo)}</span>` : '';
                return `<article class="talento-linha equipamento-catalogo-linha">
                    <div class="talento-linha-conteudo">
                        <div class="talento-linha-cabecalho">
                            <span class="talento-linha-nome">${F5E_CAT_ESC(item.nome)}</span>
                            ${custo}
                        </div>
                        ${meta ? `<p class="talento-linha-pre"><span class="talento-linha-rotulo">Tipo:</span> ${F5E_CAT_ESC(meta)}</p>` : ''}
                    </div>
                    <div class="equipamento-catalogo-acoes">
                        <button type="button" class="talento-linha-acao item-btn-primary" data-slug="${F5E_CAT_ESC(item.slug)}">➕ Adicionar</button>
                    </div>
                </article>`;
            })
            .join('');

        lista.querySelectorAll('[data-slug]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const slug = btn.dataset.slug;
                const item = this._itens.find((x) => x.slug === slug);
                const qtd = parseInt(document.getElementById('f5eModalCatalogoQtd')?.value, 10) || 1;
                if (this._onConfirm && item) {
                    this._onConfirm(slug, qtd, item);
                    Toast?.success?.(`${item.nome} adicionado.`);
                }
                this.fechar();
            });
        });
    }
}
