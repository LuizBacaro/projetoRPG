/**
 * GrimorioController.js
 * SRP: Grimório de Magias — preparação diária com slots D&D 3.5
 * SOLID: SRP separado da ficha | DIP via parâmetros do constructor
 */

import { getApiUrl } from '../config/api.config.js';

// ── Classes conjuradoras ──
const CLASSES_CONJURADORAS = new Set([
    'Mago', 'Feiticeiro', 'Clérigo', 'Clerigo', 'Druida',
    'Bardo', 'Paladino', 'Ranger',
    'mago', 'feiticeiro', 'clérigo', 'clerigo', 'druida',
    'bardo', 'paladino', 'ranger'
]);

// ── Tabelas de magias por dia D&D 3.5 (base, sem bônus de atributo) ──
const TABELA_MAGIAS_DIA = {
    Mago: [
        [3,1,null,null,null,null,null,null,null,null],
        [4,2,null,null,null,null,null,null,null,null],
        [4,2,1,null,null,null,null,null,null,null],
        [4,3,2,null,null,null,null,null,null,null],
        [4,3,2,1,null,null,null,null,null,null],
        [4,3,3,2,null,null,null,null,null,null],
        [4,4,3,2,1,null,null,null,null,null],
        [4,4,3,3,2,null,null,null,null,null],
        [4,4,4,3,2,1,null,null,null,null],
        [4,4,4,3,3,2,null,null,null,null],
        [4,4,4,4,3,2,1,null,null,null],
        [4,4,4,4,3,3,2,null,null,null],
        [4,4,4,4,4,3,2,1,null,null],
        [4,4,4,4,4,3,3,2,null,null],
        [4,4,4,4,4,4,3,2,1,null],
        [4,4,4,4,4,4,3,3,2,null],
        [4,4,4,4,4,4,4,3,2,1],
        [4,4,4,4,4,4,4,3,3,2],
        [4,4,4,4,4,4,4,4,3,3],
        [4,4,4,4,4,4,4,4,4,4],
    ],
    Clérigo: [
        [3,1,null,null,null,null,null,null,null,null],
        [4,2,null,null,null,null,null,null,null,null],
        [4,2,1,null,null,null,null,null,null,null],
        [5,3,2,null,null,null,null,null,null,null],
        [5,3,2,1,null,null,null,null,null,null],
        [5,3,3,2,null,null,null,null,null,null],
        [6,4,3,2,1,null,null,null,null,null],
        [6,4,3,3,2,null,null,null,null,null],
        [6,4,4,3,2,1,null,null,null,null],
        [6,4,4,3,3,2,null,null,null,null],
        [6,5,4,4,3,2,1,null,null,null],
        [6,5,4,4,3,3,2,null,null,null],
        [6,5,5,4,4,3,2,1,null,null],
        [6,5,5,4,4,3,3,2,null,null],
        [6,5,5,5,4,4,3,2,1,null],
        [6,5,5,5,4,4,3,3,2,null],
        [6,5,5,5,5,4,4,3,2,1],
        [6,5,5,5,5,4,4,3,3,2],
        [6,5,5,5,5,5,4,4,3,3],
        [6,5,5,5,5,5,4,4,4,4],
    ],
    Druida: [
        [3,1,null,null,null,null,null,null,null,null],
        [4,2,null,null,null,null,null,null,null,null],
        [4,2,1,null,null,null,null,null,null,null],
        [5,3,2,null,null,null,null,null,null,null],
        [5,3,2,1,null,null,null,null,null,null],
        [5,3,3,2,null,null,null,null,null,null],
        [6,4,3,2,1,null,null,null,null,null],
        [6,4,3,3,2,null,null,null,null,null],
        [6,4,4,3,2,1,null,null,null,null],
        [6,4,4,3,3,2,null,null,null,null],
        [6,5,4,4,3,2,1,null,null,null],
        [6,5,4,4,3,3,2,null,null,null],
        [6,5,5,4,4,3,2,1,null,null],
        [6,5,5,4,4,3,3,2,null,null],
        [6,5,5,5,4,4,3,2,1,null],
        [6,5,5,5,4,4,3,3,2,null],
        [6,5,5,5,5,4,4,3,2,1],
        [6,5,5,5,5,4,4,3,3,2],
        [6,5,5,5,5,5,4,4,3,3],
        [6,5,5,5,5,5,4,4,4,4],
    ],
    Bardo: [
        [2,null,null,null,null,null,null],
        [3,0,null,null,null,null,null],
        [3,1,null,null,null,null,null],
        [3,2,0,null,null,null,null],
        [3,3,1,null,null,null,null],
        [3,3,2,null,null,null,null],
        [3,3,2,0,null,null,null],
        [3,3,3,1,null,null,null],
        [3,3,3,2,null,null,null],
        [3,3,3,2,0,null,null],
        [3,3,3,3,1,null,null],
        [3,3,3,3,2,null,null],
        [3,3,3,3,2,0,null],
        [4,3,3,3,3,1,null],
        [4,4,3,3,3,2,null],
        [4,4,4,3,3,2,0],
        [4,4,4,4,3,3,1],
        [4,4,4,4,4,3,2],
        [4,4,4,4,4,4,3],
        [4,4,4,4,4,4,4],
    ],
    Paladino: [
        [null,null,null,null],
        [null,null,null,null],
        [null,null,null,null],
        [0,null,null,null],
        [0,null,null,null],
        [1,null,null,null],
        [1,null,null,null],
        [1,0,null,null],
        [1,0,null,null],
        [1,1,null,null],
        [1,1,0,null],
        [1,1,1,null],
        [1,1,1,null],
        [2,1,1,0],
        [2,1,1,1],
        [2,2,1,1],
        [2,2,2,1],
        [3,2,2,1],
        [3,3,3,2],
        [3,3,3,3],
    ],
    Ranger: [
        [null,null,null,null],
        [null,null,null,null],
        [null,null,null,null],
        [0,null,null,null],
        [0,null,null,null],
        [1,null,null,null],
        [1,null,null,null],
        [1,0,null,null],
        [1,0,null,null],
        [1,1,null,null],
        [1,1,0,null],
        [1,1,1,null],
        [1,1,1,null],
        [2,1,1,0],
        [2,1,1,1],
        [2,2,1,1],
        [2,2,2,1],
        [3,2,2,1],
        [3,3,3,2],
        [3,3,3,3],
    ],
};

// ── Bônus de magias por dia por modificador de atributo ──
const BONUS_ATRIBUTO = {
    1: [1,0,0,0,0,0,0,0,0],
    2: [1,1,0,0,0,0,0,0,0],
    3: [1,1,1,0,0,0,0,0,0],
    4: [1,1,1,1,0,0,0,0,0],
    5: [2,1,1,1,1,0,0,0,0],
    6: [2,2,1,1,1,1,0,0,0],
    7: [2,2,2,1,1,1,1,0,0],
    8: [2,2,2,2,1,1,1,1,0],
    9: [2,2,2,2,2,1,1,1,1],
};

// ── Atributo chave por classe ──
const ATRIBUTO_CHAVE = {
    Mago: 'inteligencia', Feiticeiro: 'carisma',
    Clérigo: 'sabedoria', Clerigo: 'sabedoria',
    Druida: 'sabedoria',  Bardo: 'carisma',
    Paladino: 'sabedoria', Ranger: 'sabedoria',
};

// ── Emojis por escola ──
const EMOJI_ESCOLA = {
    'Abjuração':'🛡️','Adivinhação':'🔮','Conjuração':'✨',
    'Encantamento':'💫','Evocação':'⚡','Ilusão':'🌀',
    'Necromancia':'💀','Transmutação':'🔄','Universal':'⭐',
};


class GrimorioController {
    constructor(combatente, token) {
        this.combatente       = combatente;
        this.classe           = this._normalizarClasse(combatente.classe);
        this.token            = token;
        this.magias           = [];
        this.magiasFiltro     = [];
        this.preparadas       = new Set();
        this.slotsDisponiveis = {};
        this.nivelAtivo       = 'todos';
        this.cardsAbertos     = new Set();
        this._carregado       = false;
        console.log('✅ GrimorioController inicializado — classe:', this.classe);
    }

    // 
    // PÚBLICO
    // 

    async abrirGrimorio() {
        const overlay = document.getElementById('modalGrimorio');
        if (!overlay) return;

        const sub = document.getElementById('grimorioSubtitulo');
        if (sub) sub.textContent = `${this.combatente.nome} · ${this.classe} · Nível ${this.combatente.nivel}`;

        overlay.classList.add('show');
        document.body.style.overflow = 'hidden';

        if (!this._carregado) {
            this._mostrarLoading(true);

            // ✅ FIX 1: SEQUENCIAL — magias primeiro, depois preparadas, depois calcula
            // Promise.all causava _calcularSlotsDisponiveis() rodar com this.magias vazio
            await this._carregarMagias();
            await this._carregarPreparadas();
            this._calcularSlotsDisponiveis();

            this._carregado = true;
            this._mostrarLoading(false);
        }

        this._renderizarPainelSlots();
        this._renderizarLista();
        this._configurarFiltros();
    }

    fecharGrimorio() {
        const overlay = document.getElementById('modalGrimorio');
        if (overlay) overlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    filtrar() {
        const busca = document.getElementById('grimorioBusca')?.value.toLowerCase().trim() || '';
        this.magiasFiltro = this.magias.filter(m => {
            const matchNivel = this.nivelAtivo === 'todos' || String(m.nivel) === String(this.nivelAtivo);
            const matchBusca = !busca
                || m.nome.toLowerCase().includes(busca)
                || (m.escola || '').toLowerCase().includes(busca)
                || (m.descricao || '').toLowerCase().includes(busca);
            return matchNivel && matchBusca;
        });
        this._renderizarLista();
    }

    async descansoLongo() {
        if (!confirm('🌙 Realizar descanso longo?\nIsso resetará todas as magias preparadas e slots usados.')) return;
        try {
            const url = getApiUrl(`/magias-preparadas/${this.combatente.id}/descanso`);
            const res = await fetch(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ confirmar: true }),
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            this.preparadas = new Set();
            this._calcularSlotsDisponiveis();
            this._renderizarPainelSlots();
            this._renderizarLista();
            this._mostrarToast('🌙 Descanso longo! Magias prontas para preparação.', 'sucesso');
        } catch (err) {
            console.error('❌ Erro no descanso longo:', err);
            this._mostrarToast('Erro ao realizar descanso longo.', 'erro');
        }
    }

    // 
    // PRIVADO — CARREGAMENTO
    // 

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

    async _carregarMagias() {
        try {
            const url = getApiUrl(`/magias/?classe=${encodeURIComponent(this.classe)}&limit=500`);
            const res = await fetch(url, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            this.magias       = await res.json();
            this.magiasFiltro = [...this.magias];
            console.log(`✅ Grimório: ${this.magias.length} magias de ${this.classe}`);
        } catch (err) {
            console.error('❌ Erro ao carregar magias:', err);
            this.magias       = [];
            this.magiasFiltro = [];
        }
    }

    async _carregarPreparadas() {
        try {
            const url = getApiUrl(`/magias-preparadas/${this.combatente.id}`);
            const res = await fetch(url, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const lista = await res.json();
            this.preparadas = new Set(lista.map(p => p.magia_id));
            console.log(`✅ Preparadas carregadas: ${this.preparadas.size}`);
        } catch (err) {
            console.error('❌ Erro ao carregar preparadas:', err);
            this.preparadas = new Set();
        }
    }

    /**
     * Calcula slots disponíveis por nível:
     * base da tabela D&D 3.5 + bônus de atributo
     * SRP: apenas cálculo, sem efeitos colaterais de UI
     */
    _calcularSlotsDisponiveis() {
        const nivel        = Math.max(1, Math.min(20, this.combatente.nivel || 1));
        const tabelaClasse = TABELA_MAGIAS_DIA[this.classe];

        if (!tabelaClasse) {
            console.warn('⚠️ Classe sem tabela de slots:', this.classe);
            this.slotsDisponiveis = {};
            return;
        }

        const linhaNivel = tabelaClasse[nivel - 1] || [];

        // Modificador do atributo chave
        const attrChave = ATRIBUTO_CHAVE[this.classe] || 'inteligencia';
        const valorAttr = this.combatente[attrChave] || 10;
        const mod       = Math.floor((valorAttr - 10) / 2);
        const bonusAttr = BONUS_ATRIBUTO[Math.max(0, mod)] || [];

        this.slotsDisponiveis = {};

        linhaNivel.forEach((base, nivelMagia) => {
            if (base === null || base === undefined) return;

            const bonus = nivelMagia > 0 ? (bonusAttr[nivelMagia - 1] || 0) : 0;
            const total = base + bonus;

            // ✅ FIX 2: Number() garante comparação correta string vs number
            const preparadasNivel = [...this.preparadas].filter(magiaId => {
                const m = this.magias.find(x => x.id === magiaId);
                return m && Number(m.nivel) === Number(nivelMagia);
            }).length;

            this.slotsDisponiveis[nivelMagia] = {
                total,
                preparadas: preparadasNivel,
                disponivel: total - preparadasNivel,
            };
        });

        console.log('📊 Slots calculados:', JSON.stringify(this.slotsDisponiveis));
    }

    // 
    // PRIVADO — PREPARAÇÃO
    // 

    async _togglePreparacao(magiaId, nivelMagia) {
        if (this.preparadas.has(magiaId)) {
            await this._desmarcarMagia(magiaId);
        } else {
            await this._prepararMagia(magiaId, nivelMagia);
        }
        this._calcularSlotsDisponiveis();
        this._renderizarPainelSlots();
        this._atualizarCard(magiaId, nivelMagia);
    }

    /**
     * Valida disponibilidade de slot e chama _persistirPreparacao
     * SRP: apenas validação — persistência delegada ao método abaixo
     */
    async _prepararMagia(magiaId, nivelMagia) {
        // ✅ FIX 3: Recalcular slots frescos antes de validar
        this._calcularSlotsDisponiveis();

        const slot = this.slotsDisponiveis[nivelMagia];
        console.log(`🔍 Validando slot nível ${nivelMagia}:`, slot);

        // ✅ Truques (nível 0) nunca consomem slots — sempre permitidos
        if (Number(nivelMagia) === 0) {
            await this._persistirPreparacao(magiaId, nivelMagia);
            return;
        }

        if (!slot) {
            this._mostrarToast(`⚠️ Nenhum slot configurado para nível ${nivelMagia}.`, 'erro');
            return;
        }

        if (slot.disponivel <= 0) {
            this._mostrarToast(
                `⚠️ Slots de nível ${nivelMagia} esgotados (${slot.preparadas}/${slot.total})!`,
                'erro'
            );
            return;
        }

        await this._persistirPreparacao(magiaId, nivelMagia);
    }

    /**
     * Persiste preparação de magia na API
     * SRP: apenas comunicação HTTP — extraído de _prepararMagia
     */
    async _persistirPreparacao(magiaId, nivelMagia) {
        try {
            const url = getApiUrl(`/magias-preparadas/${this.combatente.id}`);
            const res = await fetch(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ magia_id: magiaId, nivel_slot: nivelMagia }),
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || `HTTP ${res.status}`);
            }

            this.preparadas.add(magiaId);
            this._mostrarToast('✅ Magia preparada!', 'sucesso');

        } catch (err) {
            console.error('❌ Erro ao preparar magia:', err);
            this._mostrarToast(`Erro: ${err.message}`, 'erro');
        }
    }

    async _desmarcarMagia(magiaId) {
        try {
            const url = getApiUrl(`/magias-preparadas/${this.combatente.id}/${magiaId}`);
            const res = await fetch(url, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${this.token}` },
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            this.preparadas.delete(magiaId);
            this._mostrarToast('📖 Magia removida da preparação.', 'info');
        } catch (err) {
            console.error('❌ Erro ao desmarcar magia:', err);
            this._mostrarToast('Erro ao remover magia.', 'erro');
        }
    }

    // 
    // PRIVADO — RENDERIZAÇÃO
    // 

    _configurarFiltros() {
        document.querySelectorAll('.grimorio-nivel-btn').forEach(btn => {
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

        const btnDescanso = document.getElementById('btnDescansoLongo');
        if (btnDescanso) {
            btnDescanso.replaceWith(btnDescanso.cloneNode(true));
            document.getElementById('btnDescansoLongo')
                ?.addEventListener('click', () => this.descansoLongo());
        }
    }

    _renderizarPainelSlots() {
        const painel = document.getElementById('grimorioPainelSlots');
        if (!painel) return;

        const niveis = Object.keys(this.slotsDisponiveis).map(Number).sort((a, b) => a - b);
        if (niveis.length === 0) {
            painel.innerHTML = '<span class="grimorio-slots-vazio">Sem slots configurados</span>';
            return;
        }

        painel.innerHTML = niveis.map(n => {
            const s   = this.slotsDisponiveis[n];
            const pct = s.total > 0 ? (s.preparadas / s.total) * 100 : 0;
            const cor = s.disponivel === 0 ? '#f87171'
                      : s.preparadas > 0   ? '#facc15'
                      :                      '#4ade80';
            return `
                <div class="grimorio-slot-box" title="Nível ${n}: ${s.preparadas}/${s.total} preparadas">
                    <span class="grimorio-slot-nivel">${n === 0 ? '0' : n + 'º'}</span>
                    <div class="grimorio-slot-barra-wrap">
                        <div class="grimorio-slot-barra-fill" style="width:${pct}%;background:${cor}"></div>
                    </div>
                    <span class="grimorio-slot-contagem" style="color:${cor}">
                        ${s.preparadas}/${s.total}
                    </span>
                </div>
            `;
        }).join('');
    }

    _renderizarLista() {
        const lista = document.getElementById('grimorioLista');
        if (!lista) return;

        if (this.magiasFiltro.length === 0) {
            lista.innerHTML = '<div class="grimorio-vazio">🔍 Nenhuma magia encontrada.</div>';
            return;
        }

        const grupos = {};
        this.magiasFiltro.forEach(m => {
            if (!grupos[m.nivel]) grupos[m.nivel] = [];
            grupos[m.nivel].push(m);
        });

        const LABEL_NIVEL = {
            0:'✦ Truques (Cantrips)', 1:'✦ 1° Nível', 2:'✦ 2° Nível',
            3:'✦ 3° Nível', 4:'✦ 4° Nível', 5:'✦ 5° Nível',
            6:'✦ 6° Nível', 7:'✦ 7° Nível', 8:'✦ 8° Nível', 9:'✦ 9° Nível',
        };

        lista.innerHTML = Object.keys(grupos).map(Number).sort((a,b) => a-b).map(nivel => {
            const slot = this.slotsDisponiveis[nivel];
            const slotInfo = slot
                ? `<span class="grimorio-grupo-slots">${slot.preparadas}/${slot.total} preparadas</span>`
                : '';
            return `
                <div class="grimorio-grupo">
                    <div class="grimorio-grupo-titulo">
                        ${LABEL_NIVEL[nivel] || `✦ Nível ${nivel}`}
                        ${slotInfo}
                    </div>
                    ${grupos[nivel].map(m => this._renderizarCard(m)).join('')}
                </div>
            `;
        }).join('');

        lista.querySelectorAll('.grimorio-checkbox').forEach(cb => {
            cb.addEventListener('change', () => {
                const magiaId  = Number(cb.dataset.magiaId);
                const nivelMag = Number(cb.dataset.nivel);
                this._togglePreparacao(magiaId, nivelMag);
            });
        });

        lista.querySelectorAll('.grimorio-expandir-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this._toggleCard(Number(btn.dataset.id));
            });
        });
    }

    _renderizarCard(m) {
        const emoji     = EMOJI_ESCOLA[m.escola] || '📜';
        const preparada = this.preparadas.has(m.id);
        const aberto    = this.cardsAbertos.has(m.id);
        const temDano   = m.dano && m.dano.trim();
        const slot      = this.slotsDisponiveis[m.nivel];
        const semSlot   = slot && !preparada && slot.disponivel <= 0;

        const badges = [
            m.escola      ? `<span class="grimorio-badge grimorio-badge-escola">${emoji} ${m.escola}</span>` : '',
            m.componentes ? `<span class="grimorio-badge grimorio-badge-comp">${m.componentes}</span>` : '',
            temDano       ? `<span class="grimorio-badge grimorio-badge-dano">🗡 ${m.dano}</span>` : '',
            m.teste_resistencia && m.teste_resistencia !== 'Nenhum'
                          ? `<span class="grimorio-badge grimorio-badge-res">🎲 ${m.teste_resistencia}</span>` : '',
        ].filter(Boolean).join('');

        const metaItens = [
            { label: 'Alcance',    valor: m.alcance },
            { label: 'Duração',    valor: m.duracao },
            { label: 'Conjuração', valor: m.tempo_conjuracao },
            { label: 'Área',       valor: m.area_efeito },
        ].filter(i => i.valor?.trim()).map(i => `
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
            <div class="grimorio-magia-card ${preparada ? 'preparada' : ''} ${semSlot ? 'sem-slot' : ''}"
                 data-id="${m.id}">
                <div class="grimorio-card-topo">
                    <label class="grimorio-checkbox-label"
                           title="${semSlot ? 'Sem slots disponíveis neste nível' : preparada ? 'Remover da preparação' : 'Preparar magia'}">
                        <input type="checkbox"
                               class="grimorio-checkbox"
                               data-magia-id="${m.id}"
                               data-nivel="${m.nivel}"
                               ${preparada ? 'checked' : ''}
                               ${semSlot ? 'disabled' : ''}>
                        <span class="grimorio-checkbox-custom ${preparada ? 'checked' : ''} ${semSlot ? 'disabled' : ''}"></span>
                    </label>
                    <span class="grimorio-card-nome ${preparada ? 'preparada-nome' : ''}">${m.nome}</span>
                    <div class="grimorio-card-badges">${badges}</div>
                </div>
                <p class="grimorio-card-descricao">${m.descricao || '—'}</p>
                <div class="grimorio-card-meta">${metaItens}</div>
                ${detalhes}
                <div class="grimorio-card-rodape">
                    <button class="grimorio-expandir-btn" data-id="${m.id}">
                        ${aberto ? '▲ Menos detalhes' : '▼ Ver detalhes'}
                    </button>
                    ${preparada ? '<span class="grimorio-preparada-badge">✦ Preparada</span>' : ''}
                </div>
            </div>
        `;
    }

    _atualizarCard(magiaId, nivelMagia) {
        const card = document.querySelector(`.grimorio-magia-card[data-id="${magiaId}"]`);
        if (!card) { this._renderizarLista(); return; }

        const preparada = this.preparadas.has(magiaId);
        const slot      = this.slotsDisponiveis[nivelMagia];
        const semSlot   = slot && !preparada && slot.disponivel <= 0;

        card.classList.toggle('preparada', preparada);
        card.classList.toggle('sem-slot',  semSlot);

        const cb = card.querySelector('.grimorio-checkbox');
        if (cb) { cb.checked = preparada; cb.disabled = semSlot; }

        const cbCustom = card.querySelector('.grimorio-checkbox-custom');
        if (cbCustom) {
            cbCustom.classList.toggle('checked',  preparada);
            cbCustom.classList.toggle('disabled', semSlot);
        }

        const nome = card.querySelector('.grimorio-card-nome');
        if (nome) nome.classList.toggle('preparada-nome', preparada);

        const rodape = card.querySelector('.grimorio-card-rodape');
        if (rodape) {
            const badgeExistente = rodape.querySelector('.grimorio-preparada-badge');
            if (preparada && !badgeExistente) {
                rodape.insertAdjacentHTML('beforeend', '<span class="grimorio-preparada-badge">✦ Preparada</span>');
            } else if (!preparada && badgeExistente) {
                badgeExistente.remove();
            }
        }
    }

    _toggleCard(id) {
        if (this.cardsAbertos.has(id)) {
            this.cardsAbertos.delete(id);
        } else {
            this.cardsAbertos.add(id);
        }
        const card     = document.querySelector(`.grimorio-magia-card[data-id="${id}"]`);
        if (!card) return;
        const detalhes = card.querySelector('.grimorio-card-detalhes');
        const btn      = card.querySelector('.grimorio-expandir-btn');
        if (detalhes) detalhes.classList.toggle('show', this.cardsAbertos.has(id));
        if (btn)      btn.textContent = this.cardsAbertos.has(id) ? '▲ Menos detalhes' : '▼ Ver detalhes';
    }

    _mostrarToast(msg, tipo = 'sucesso') {
        const toast = document.createElement('div');
        toast.className = `grimorio-toast grimorio-toast-${tipo}`;
        toast.textContent = msg;
        document.body.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 2500);
    }

    _mostrarLoading(visivel) {
        const el    = document.getElementById('grimorioLoading');
        const lista = document.getElementById('grimorioLista');
        if (el)    el.style.display    = visivel ? 'flex' : 'none';
        if (lista) lista.style.display = visivel ? 'none' : 'block';
    }
}


// ── Inicialização ──
document.addEventListener('DOMContentLoaded', () => {
    const tentarInicializar = setInterval(() => {
        const nomeEl   = document.getElementById('fichaNome');
        const classeEl = document.getElementById('fichaClasse');
        if (!nomeEl || !classeEl) return;

        const nome   = nomeEl.textContent?.trim();
        const classe = classeEl.textContent?.trim();
        if (!nome || nome === '—' || !classe || classe === '—') return;

        clearInterval(tentarInicializar);

        const combatente = window._fichaController?.combatente;
        if (!combatente) return;

        const token = localStorage.getItem('token');
        window._grimorioController = new GrimorioController(combatente, token);

        if (CLASSES_CONJURADORAS.has(classe.toLowerCase()) || CLASSES_CONJURADORAS.has(classe)) {
            const btnHeader  = document.getElementById('btnGrimorio');
            const secaoMagia = document.getElementById('secaoMagias');
            if (btnHeader)  btnHeader.style.display  = 'inline-flex';
            if (secaoMagia) secaoMagia.style.display = 'flex';
        }

        document.getElementById('modalGrimorio')?.addEventListener('click', e => {
            if (e.target.id === 'modalGrimorio') window._grimorioController.fecharGrimorio();
        });

        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') window._grimorioController?.fecharGrimorio();
        });

        console.log('✅ GrimorioController pronto para', classe);
    }, 300);
});