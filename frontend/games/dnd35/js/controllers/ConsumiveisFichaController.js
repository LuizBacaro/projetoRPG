import { ConsumivelService } from '../services/ConsumivelService.js';
import { escapeHtml } from '../utils/formatters.js';

class ConsumiveisFichaController {
    constructor() {
        this.service = new ConsumivelService();
        this.combatenteId = null;
        this.catalogo = [];
        this.catalogoSkip = 0;
        this.catalogoLimit = 30;
        this.catalogoCarregadoCompleto = false;
        this.filtroTipo = 'todos';
    }

    async inicializar() {
        const params = new URLSearchParams(window.location.search);
        this.combatenteId = Number(params.get('id'));
        if (!Number.isFinite(this.combatenteId) || this.combatenteId <= 0) return;

        this._bind();
        await this.carregarInventario();
    }

    _bind() {
        document.getElementById('btnAdicionarConsumivel')?.addEventListener('click', () => this.abrirModal());
        document.getElementById('btnFecharModalConsumiveis')?.addEventListener('click', () => this.fecharModal());
        document.getElementById('consumiveisBusca')?.addEventListener('input', () => void this.filtrarCatalogo());
        document.getElementById('btnSalvarConsumivelCustomizado')?.addEventListener('click', () => this.salvarCustomizado());
        document.getElementById('abaListarConsumiveis')?.addEventListener('click', () => this.abrirAbaListarConsumiveis());
        document.getElementById('abaCriarConsumivel')?.addEventListener('click', () => this.abrirAbaCriarConsumivel());
        document.querySelectorAll('[data-filtro-consumivel]').forEach((btn) => {
            btn.addEventListener('click', () => {
                this.filtroTipo = String(btn.dataset.filtroConsumivel || 'todos').toLowerCase();
                document.querySelectorAll('[data-filtro-consumivel]').forEach((b) => b.classList.remove('ativo'));
                btn.classList.add('ativo');
                this.renderizarCatalogo();
            });
        });
        document.getElementById('modalConsumiveis')?.addEventListener('click', (e) => {
            if (e.target?.id === 'modalConsumiveis') this.fecharModal();
        });
    }

    _nomeExibicaoConsumivel(item) {
        const nomeOriginal = String(item?.nome || '').trim();
        if (!nomeOriginal) return 'Consumível';
        const tipo = String(item?.tipo || '').toLowerCase();
        if (tipo === 'poção' || tipo === 'óleo') {
            return nomeOriginal.replace(/\s*\(poção\s+ou\s+óleo\)\s*$/i, '').trim();
        }
        return nomeOriginal;
    }

    async carregarInventario() {
        const lista = document.getElementById('fichaConsumiveis');
        if (!lista) return;
        try {
            const itens = await this.service.listarConsumiveisJogador(this.combatenteId);
            if (!itens.length) {
                lista.innerHTML = '<span class="ficha-vazio">Nenhum consumível cadastrado</span>';
                return;
            }
            lista.innerHTML = `<div class="ficha-equipamentos-tabela"><div class="ficha-equipamento-header"><span>Item</span><span>Tipo</span><span>Custo</span><span>Qtd</span><span>Ação</span></div><div class="ficha-equipamentos-lista-items">${itens.map((it) => `<div class="ficha-equipamento-linha"><span class="ficha-equipamento-nome">${escapeHtml(this._nomeExibicaoConsumivel(it))}</span><span class="ficha-equipamento-desc">${escapeHtml(it.tipo || it.categoria || '—')}</span><span class="ficha-equipamento-pag">${escapeHtml(it.custo || '—')}</span><span class="ficha-equipamento-qtd">${it.quantidade}</span><button class="btn-deletar-eq" data-cons-id="${it.id}" data-cons-nome="${escapeHtml(this._nomeExibicaoConsumivel(it))}">🗑️</button></div>`).join('')}</div></div>`;
            lista.querySelectorAll('[data-cons-id]').forEach((btn) => {
                btn.addEventListener('click', () => this.remover(Number(btn.dataset.consId), btn.dataset.consNome || 'Consumível'));
            });
        } catch (e) {
            lista.innerHTML = '<span class="ficha-vazio">❌ Erro ao carregar consumíveis</span>';
        }
    }

    async abrirModal() {
        const modal = document.getElementById('modalConsumiveis');
        if (!modal) return;
        this.catalogo = [];
        this.catalogoSkip = 0;
        this.catalogoCarregadoCompleto = false;
        this.filtroTipo = 'todos';
        const inputBusca = document.getElementById('consumiveisBusca');
        if (inputBusca) inputBusca.value = '';
        document.querySelectorAll('[data-filtro-consumivel]').forEach((b) => {
            b.classList.toggle('ativo', String(b.dataset.filtroConsumivel || 'todos').toLowerCase() === 'todos');
        });
        await this._carregarMaisConsumiveis();
        this.renderizarCatalogo();
        this.abrirAbaListarConsumiveis();
        modal.style.display = 'flex';
    }

    fecharModal() {
        const modal = document.getElementById('modalConsumiveis');
        if (modal) modal.style.display = 'none';
    }

    renderizarCatalogo() {
        const lista = document.getElementById('consumiveisLista');
        const termo = document.getElementById('consumiveisBusca')?.value || '';
        if (!lista) return;
        const itens = this.service
            .filtrarPorBusca(this.catalogo, termo)
            .filter((it) => {
                if (this.filtroTipo === 'todos') return true;
                const tipo = String(it.tipo || '').toLowerCase();
                if (this.filtroTipo === 'pergaminho') {
                    return String(it.categoria || '').toLowerCase().includes('pergaminho');
                }
                return tipo === this.filtroTipo;
            });
        const filtroAtivo = String(termo).trim();
        const podeCarregarMais = !this.catalogoCarregadoCompleto && !filtroAtivo;
        if (!itens.length) {
            lista.innerHTML = `<p class="equipamentos-vazio">Nenhum consumível encontrado</p>${
                podeCarregarMais
                    ? `
                <div class="talentos-paginacao talentos-paginacao--lista">
                    <button id="btnCarregarMaisConsumiveis" type="button" class="btn-carregar-mais">
                        Carregar mais consumíveis
                    </button>
                </div>`
                    : ''
            }`;
            const btnCarregarMais = lista.querySelector('#btnCarregarMaisConsumiveis');
            if (btnCarregarMais) {
                btnCarregarMais.addEventListener('click', async () => {
                    btnCarregarMais.disabled = true;
                    btnCarregarMais.textContent = 'Carregando...';
                    await this._carregarMaisConsumiveis();
                    this.renderizarCatalogo();
                });
            }
            return;
        }
        lista.innerHTML = `${itens.map((it) => `<article class="talento-linha"><div class="talento-linha-conteudo"><div class="talento-linha-cabecalho"><span class="talento-linha-nome">${escapeHtml(this._nomeExibicaoConsumivel(it))}</span><span class="talento-linha-secao">${escapeHtml(it.categoria || '—')}</span></div><p class="talento-linha-beneficio"><span class="talento-linha-rotulo">Tipo:</span> ${escapeHtml(it.tipo || '—')}</p><p class="talento-linha-pre"><span class="talento-linha-rotulo">Custo:</span> ${escapeHtml(it.custo || '—')} ${it.pagina_referencia ? `• <span class="talento-linha-rotulo">Ref:</span> ${escapeHtml(it.pagina_referencia)}` : ''}</p></div><button type="button" class="talento-linha-acao item-btn-primary" data-add-id="${it.id}">➕ Adicionar</button></article>`).join('')}
            ${podeCarregarMais ? `
                <div class="talentos-paginacao talentos-paginacao--lista">
                    <button id="btnCarregarMaisConsumiveis" type="button" class="btn-carregar-mais">
                        Carregar mais consumíveis
                    </button>
                </div>` : ''}
        `;
        lista.querySelectorAll('[data-add-id]').forEach((btn) => {
            btn.addEventListener('click', () => this.adicionar(Number(btn.dataset.addId)));
        });
        const btnCarregarMais = lista.querySelector('#btnCarregarMaisConsumiveis');
        if (btnCarregarMais) {
            btnCarregarMais.addEventListener('click', async () => {
                btnCarregarMais.disabled = true;
                btnCarregarMais.textContent = 'Carregando...';
                await this._carregarMaisConsumiveis();
                this.renderizarCatalogo();
            });
        }
    }

    async _carregarMaisConsumiveis() {
        if (this.catalogoCarregadoCompleto) return;
        const novos = await this.service.listarConsumiveis(this.catalogoSkip, this.catalogoLimit);
        if (novos.length > 0) {
            this.catalogo = [...this.catalogo, ...novos];
            this.catalogoSkip += this.catalogoLimit;
        }
        if (novos.length < this.catalogoLimit) {
            this.catalogoCarregadoCompleto = true;
        }
    }

    async filtrarCatalogo() {
        const termo = document.getElementById('consumiveisBusca')?.value || '';
        if (termo.trim() && !this.catalogoCarregadoCompleto) {
            while (!this.catalogoCarregadoCompleto) {
                await this._carregarMaisConsumiveis();
            }
        }
        this.renderizarCatalogo();
    }

    abrirAbaListarConsumiveis() {
        document.getElementById('abaListarConsumiveis')?.classList.add('ativa');
        document.getElementById('abaCriarConsumivel')?.classList.remove('ativa');
        document.getElementById('conteudoListarConsumiveis')?.classList.add('ativo');
        document.getElementById('conteudoCriarConsumivel')?.classList.remove('ativo');
    }

    abrirAbaCriarConsumivel() {
        document.getElementById('abaCriarConsumivel')?.classList.add('ativa');
        document.getElementById('abaListarConsumiveis')?.classList.remove('ativa');
        document.getElementById('conteudoCriarConsumivel')?.classList.add('ativo');
        document.getElementById('conteudoListarConsumiveis')?.classList.remove('ativo');
    }

    async adicionar(consumivelId) {
        const qtd = Number(document.getElementById('consumiveisQuantidade')?.value || 1);
        await this.service.adicionarConsumivel(this.combatenteId, {
            consumivel_id: consumivelId,
            quantidade: Number.isFinite(qtd) && qtd > 0 ? qtd : 1,
        });
        await this.carregarInventario();
        window.NotificationService?.mostrarSucesso('✅ Consumível adicionado!');
    }

    async remover(consumivelId, nome) {
        window.ModalConfirm?.mostrar({
            icone: '🧪',
            titulo: 'Remover Consumível',
            texto: `Tem certeza que deseja remover <strong>"${nome}"</strong>?`,
            textoConfirmar: '🗑️ Remover',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar: async () => {
                await this.service.removerConsumivel(this.combatenteId, consumivelId);
                await this.carregarInventario();
                window.NotificationService?.mostrarSucesso('✅ Consumível removido!');
            },
        });
    }

    async salvarCustomizado() {
        const nome = (document.getElementById('criarNomeConsumivel')?.value || '').trim();
        if (!nome) return;
        const payload = {
            nome,
            descricao: (document.getElementById('criarDescricaoConsumivel')?.value || '').trim() || null,
            pagina_referencia: (document.getElementById('criarPaginaRefConsumivel')?.value || '').trim() || null,
            categoria: (document.getElementById('criarCategoriaConsumivel')?.value || '').trim() || null,
            tipo: (document.getElementById('criarTipoConsumivel')?.value || '').trim() || null,
            custo: (document.getElementById('criarCustoConsumivel')?.value || '').trim() || null,
            peso: (document.getElementById('criarPesoConsumivel')?.value || '').trim() || null,
            ativo: true,
        };
        const novo = await this.service.criarConsumivel(payload);
        await this.adicionar(novo.id);
        document.getElementById('formCriarConsumivel')?.reset();
        this.abrirAbaListarConsumiveis();
    }
}

window.addEventListener('DOMContentLoaded', async () => {
    const ctrl = new ConsumiveisFichaController();
    await ctrl.inicializar();
});
