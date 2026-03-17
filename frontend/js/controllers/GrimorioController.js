/**
 * GrimorioController.js
 * SRP: Controlar o Grimório de Magias na ficha do personagem
 * SOLID: SRP — apenas lógica do grimório
 *        DIP — recebe classe via parâmetro, não acessa DOM direto para dados
 * Carregado como module em ficha-personagem.html
 */

import { getApiUrl } from '../config/api.config.js';

// ── Classes que podem usar magias ──
const CLASSES_CONJURADORAS = new Set([
    'Mago', 'Feiticeiro', 'Clérigo', 'Druida', 'Bardo', 'Paladino', 'Ranger',
    'mago', 'feiticeiro', 'clérigo', 'clerigo', 'druida', 'bardo', 'paladino', 'ranger'
]);

// ── Emojis por escola ──
const EMOJI_ESCOLA = {
    'Abjuração':    '🛡️',
    'Adivinhação':  '🔮',
    'Conjuração':   '✨',
    'Encantamento': '💫',
    'Evocação':     '⚡',
    'Ilusão':       '🌀',
    'Necromancia':  '💀',
    'Transmutação': '🔄',
    'Universal':    '⭐',
};


class GrimorioController {
    /**
     * @param {string} classe  — Classe do personagem (ex: "Mago")
     * @param {string} nome    — Nome do personagem para exibir no subtítulo
     * @param {string} token   — JWT para autenticação
     */
    constructor(classe, nome, token) {
        this.classe       = this._normalizarClasse(classe);
        this.nome         = nome;
        this.token        = token;
        this.magias       = [];        // todas as magias carregadas
        this.magiasFiltro = [];        // após filtro ativo
        this.nivelAtivo   = 'todos';
        this.cardsAbertos = new Set(); // IDs de cards expandidos
        this._carregado   = false;
        console.log('✅ GrimorioController inicializado — classe:', this.classe);
    }

    // ─────────────────────────────────────────────
    // PÚBLICO
    // ─────────────────────────────────────────────

    /** Abre o grimório; carrega magias se ainda não carregou */
    async abrirGrimorio() {
        const overlay = document.getElementById('modalGrimorio');
        if (!overlay) return;

        // Subtítulo
        const sub = document.getElementById('grimorioSubtitulo');
        if (sub) sub.textContent = `${this.nome} · ${this.classe}`;

        overlay.classList.add('show');
        document.body.style.overflow = 'hidden';

        if (!this._carregado) {
            await this._carregarMagias();
        } else {
            this._renderizarLista();
        }

        this._configurarFiltros();
    }

    /** Fecha o grimório */
    fecharGrimorio() {
        const overlay = document.getElementById('modalGrimorio');
        if (overlay) overlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    /** Filtrar por busca de texto */
    filtrar() {
        const busca = document.getElementById('grimorioBusca')?.value.toLowerCase().trim() || '';
        this.magiasFiltro = this.magias.filter(m => {
            const matchNivel = this.nivelAtivo === 'todos' || String(m.nivel) === String(this.nivelAtivo);
            const matchBusca = !busca ||
                m.nome.toLowerCase().includes(busca) ||
                (m.escola || '').toLowerCase().includes(busca) ||
                (m.descricao || '').toLowerCase().includes(busca);
            return matchNivel && matchBusca;
        });
        this._renderizarLista();
    }

    // ─────────────────────────────────────────────
    // PRIVADO
    // ─────────────────────────────────────────────

    /** Normaliza nome de classe para match com API */
    _normalizarClasse(classe) {
        if (!classe) return '';
        const mapa = {
            'clerigo': 'Clérigo', 'clérigo': 'Clérigo',
            'mago': 'Mago', 'feiticeiro': 'Feiticeiro',
            'druida': 'Druida', 'bardo': 'Bardo',
            'paladino': 'Paladino', 'ranger': 'Ranger',
        };
        return mapa[classe.toLowerCase()] || classe;
    }

    /** Carrega magias da classe via API */
    async _carregarMagias() {
        this._mostrarLoading(true);
        try {
            const url = getApiUrl(`/magias?classe=${encodeURIComponent(this.classe)}&limit=500`);
            const res = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json',
                }
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            this.magias       = await res.json();
            this.magiasFiltro = [...this.magias];
            this._carregado   = true;
            console.log(`✅ Grimório: ${this.magias.length} magias de ${this.classe} carregadas`);
        } catch (err) {
            console.error('❌ Erro ao carregar magias:', err);
            this._mostrarErro();
            return;
        } finally {
            this._mostrarLoading(false);
        }
        this._renderizarLista();
    }

    /** Configura cliques nos botões de nível */
    _configurarFiltros() {
        document.querySelectorAll('.grimorio-nivel-btn').forEach(btn => {
            // Evitar duplicate listeners
            btn.replaceWith(btn.cloneNode(true));
        });
        document.querySelectorAll('.grimorio-nivel-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.grimorio-nivel-btn').forEach(b => b.classList.remove('ativo'));
                btn.classList.add('ativo');
                this.nivelAtivo = btn.dataset.nivel;
                this.filtrar();
            });
        });
    }

    /** Renderiza lista de magias agrupadas por nível */
    _renderizarLista() {
        const lista = document.getElementById('grimorioLista');
        if (!lista) return;

        if (this.magiasFiltro.length === 0) {
            lista.innerHTML = '<div class="grimorio-vazio">🔍 Nenhuma magia encontrada.</div>';
            return;
        }

        // Agrupar por nível
        const grupos = {};
        this.magiasFiltro.forEach(m => {
            const k = m.nivel;
            if (!grupos[k]) grupos[k] = [];
            grupos[k].push(m);
        });

        const niveisOrdenados = Object.keys(grupos).map(Number).sort((a, b) => a - b);
        const LABEL_NIVEL = {
            0: '✦ Truques (Cantrips)',
            1: '✦ 1° Nível', 2: '✦ 2° Nível', 3: '✦ 3° Nível',
            4: '✦ 4° Nível', 5: '✦ 5° Nível', 6: '✦ 6° Nível',
            7: '✦ 7° Nível', 8: '✦ 8° Nível', 9: '✦ 9° Nível',
        };

        lista.innerHTML = niveisOrdenados.map(nivel => `
            <div class="grimorio-grupo">
                <div class="grimorio-grupo-titulo">${LABEL_NIVEL[nivel] || `✦ Nível ${nivel}`}</div>
                ${grupos[nivel].map(m => this._renderizarCard(m)).join('')}
            </div>
        `).join('');

        // Bind cliques nos cards
        lista.querySelectorAll('.grimorio-magia-card').forEach(card => {
            const id = Number(card.dataset.id);
            card.querySelector('.grimorio-expandir-btn')?.addEventListener('click', (e) => {
                e.stopPropagation();
                this._toggleCard(id);
            });
        });
    }

    /** Renderiza um card individual de magia */
    _renderizarCard(m) {
        const emoji   = EMOJI_ESCOLA[m.escola] || '📜';
        const aberto  = this.cardsAbertos.has(m.id);
        const temDano = m.dano && m.dano.trim();

        const badges = [
            m.escola     ? `<span class="grimorio-badge grimorio-badge-escola">${emoji} ${m.escola}</span>` : '',
            m.componentes? `<span class="grimorio-badge grimorio-badge-comp">${m.componentes}</span>` : '',
            temDano      ? `<span class="grimorio-badge grimorio-badge-dano">🗡 ${m.dano}</span>` : '',
            m.teste_resistencia && m.teste_resistencia !== 'Nenhum'
                         ? `<span class="grimorio-badge grimorio-badge-res">🎲 ${m.teste_resistencia}</span>` : '',
        ].filter(Boolean).join('');

        const metaItens = [
            { label: 'Alcance',      valor: m.alcance },
            { label: 'Duração',      valor: m.duracao },
            { label: 'Conjuração',   valor: m.tempo_conjuracao },
            { label: 'Área',         valor: m.area_efeito },
        ].filter(i => i.valor && i.valor.trim())
         .map(i => `
            <div class="grimorio-meta-item">
                <span class="grimorio-meta-label">${i.label}</span>
                <span class="grimorio-meta-valor">${i.valor}</span>
            </div>
         `).join('');

        const detalhes = `
            <div class="grimorio-card-detalhes ${aberto ? 'show' : ''}">
                ${m.sub_escola ? `
                    <div class="grimorio-detalhe-linha">
                        <span class="grimorio-detalhe-chave">Sub-escola</span>
                        <span class="grimorio-detalhe-valor">${m.sub_escola}</span>
                    </div>` : ''}
                ${temDano ? `
                    <div class="grimorio-detalhe-linha">
                        <span class="grimorio-detalhe-chave">Dano</span>
                        <span class="grimorio-detalhe-valor grimorio-dano-destaque">${m.dano}</span>
                    </div>` : ''}
                ${m.teste_resistencia ? `
                    <div class="grimorio-detalhe-linha">
                        <span class="grimorio-detalhe-chave">Resistência</span>
                        <span class="grimorio-detalhe-valor">${m.teste_resistencia}</span>
                    </div>` : ''}
                <div class="grimorio-detalhe-linha">
                    <span class="grimorio-detalhe-chave">Res. Mágica</span>
                    <span class="grimorio-detalhe-valor">${m.resistencia_magica ? '✅ Sim' : '❌ Não'}</span>
                </div>
            </div>
        `;

        return `
            <div class="grimorio-magia-card" data-id="${m.id}">
                <div class="grimorio-card-topo">
                    <span class="grimorio-card-nome">${m.nome}</span>
                    <div class="grimorio-card-badges">${badges}</div>
                </div>
                <p class="grimorio-card-descricao">${m.descricao || '—'}</p>
                <div class="grimorio-card-meta">${metaItens}</div>
                ${detalhes}
                <div class="grimorio-card-rodape">
                    <button class="grimorio-expandir-btn">
                        ${aberto ? '▲ Menos detalhes' : '▼ Ver detalhes'}
                    </button>
                </div>
            </div>
        `;
    }

    /** Alterna exibição de detalhes de um card */
    _toggleCard(id) {
        if (this.cardsAbertos.has(id)) {
            this.cardsAbertos.delete(id);
        } else {
            this.cardsAbertos.add(id);
        }
        // Re-renderizar apenas o card afetado
        const card = document.querySelector(`.grimorio-magia-card[data-id="${id}"]`);
        if (!card) return;
        const detalhes = card.querySelector('.grimorio-card-detalhes');
        const btn      = card.querySelector('.grimorio-expandir-btn');
        if (detalhes) detalhes.classList.toggle('show', this.cardsAbertos.has(id));
        if (btn)      btn.textContent = this.cardsAbertos.has(id) ? '▲ Menos detalhes' : '▼ Ver detalhes';
    }

    _mostrarLoading(visivel) {
        const el = document.getElementById('grimorioLoading');
        const lista = document.getElementById('grimorioLista');
        if (el)    el.style.display    = visivel ? 'flex' : 'none';
        if (lista) lista.style.display = visivel ? 'none' : 'block';
    }

    _mostrarErro() {
        const lista = document.getElementById('grimorioLista');
        if (lista) lista.innerHTML = `
            <div class="grimorio-vazio">
                ❌ Erro ao carregar magias. Verifique o servidor.
            </div>
        `;
        this._mostrarLoading(false);
    }
}


// ── Inicialização: aguarda FichaPersonagemController carregar o combatente ──
document.addEventListener('DOMContentLoaded', () => {
    // Verifica a cada 300ms se o combatente já foi carregado pelo FichaController
    const tentarInicializar = setInterval(() => {
        const nomeEl   = document.getElementById('fichaNome');
        const classeEl = document.getElementById('fichaClasse');

        if (!nomeEl || !classeEl) return;
        const nome   = nomeEl.textContent?.trim();
        const classe = classeEl.textContent?.trim();
        if (!nome || nome === '—' || !classe || classe === '—') return;

        clearInterval(tentarInicializar);

        const token = localStorage.getItem('token');

        // ✅ Instância global acessível pelos onclick do HTML
        window._grimorioController = new GrimorioController(classe, nome, token);

        // Mostrar botão Grimório apenas para classes conjuradoras
        if (CLASSES_CONJURADORAS.has(classe.toLowerCase())) {
            const btnHeader  = document.getElementById('btnGrimorio');
            const secaoMagia = document.getElementById('secaoMagias');
            if (btnHeader)  btnHeader.style.display  = 'inline-flex';
            if (secaoMagia) secaoMagia.style.display = 'flex';
        }

        // Fechar ao clicar fora
        document.getElementById('modalGrimorio')?.addEventListener('click', (e) => {
            if (e.target.id === 'modalGrimorio') {
                window._grimorioController.fecharGrimorio();
            }
        });

        // Fechar com ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') window._grimorioController?.fecharGrimorio();
        });

        console.log('✅ GrimorioController pronto para', classe);
    }, 300);
});