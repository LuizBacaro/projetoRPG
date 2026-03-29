/**
 * GrimorioController.js
 * SRP: Grimório de Magias — preparação diária com slots D&D 3.5
 * SOLID: SRP separado da ficha | DIP via parâmetros do constructor
 * ✅ FIX: Usa MagiaService para buscar magias com normalização de classe
 */

import { getApiUrl } from '../config/api.config.js';
import { MagiaService } from '../services/MagiaService.js';

// ── Classes conjuradoras ──
const CLASSES_CONJURADORAS = new Set([
    'Mago', 'Feiticeiro', 'Clérigo', 'Clerigo', 'Druida',
    'Bardo', 'Paladino', 'Ranger',
    'mago', 'feiticeiro', 'clérigo', 'clerigo', 'druida',
    'bardo', 'paladino', 'ranger'
]);

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
        [null,null,null,null],[null,null,null,null],[null,null,null,null],
        [0,null,null,null],[0,null,null,null],[1,null,null,null],
        [1,null,null,null],[1,0,null,null],[1,0,null,null],[1,1,null,null],
        [1,1,0,null],[1,1,1,null],[1,1,1,null],[2,1,1,0],[2,1,1,1],
        [2,2,1,1],[2,2,2,1],[3,2,2,1],[3,3,3,2],[3,3,3,3],
    ],
    Ranger: [
        [null,null,null,null],[null,null,null,null],[null,null,null,null],
        [0,null,null,null],[0,null,null,null],[1,null,null,null],
        [1,null,null,null],[1,0,null,null],[1,0,null,null],[1,1,null,null],
        [1,1,0,null],[1,1,1,null],[1,1,1,null],[2,1,1,0],[2,1,1,1],
        [2,2,1,1],[2,2,2,1],[3,2,2,1],[3,3,3,2],[3,3,3,3],
    ],
};

const BONUS_ATRIBUTO = {
    1:[1,0,0,0,0,0,0,0,0], 2:[1,1,0,0,0,0,0,0,0],
    3:[1,1,1,0,0,0,0,0,0], 4:[1,1,1,1,0,0,0,0,0],
    5:[2,1,1,1,1,0,0,0,0], 6:[2,2,1,1,1,1,0,0,0],
    7:[2,2,2,1,1,1,1,0,0], 8:[2,2,2,2,1,1,1,1,0],
    9:[2,2,2,2,2,1,1,1,1],
};

const ATRIBUTO_CHAVE = {
    Mago:'inteligencia', Feiticeiro:'carisma',
    Clérigo:'sabedoria', Clerigo:'sabedoria',
    Druida:'sabedoria',  Bardo:'carisma',
    Paladino:'sabedoria', Ranger:'sabedoria',
};

const EMOJI_ESCOLA = {
    'Abjuração':'🛡️','Adivinhação':'🔮','Conjuração':'✨',
    'Encantamento':'💫','Evocação':'⚡','Ilusão':'🌀',
    'Necromancia':'💀','Transmutação':'🔄','Universal':'⭐',
};

const ESCOLAS_ORDEM = [
    'Abjuração','Adivinhação','Conjuração','Encantamento',
    'Evocação','Ilusão','Necromancia','Transmutação','Universal'
];


class GrimorioController {
    constructor(combatente, token, magiaService = null) {
        this.combatente = combatente;
        this.classe = this._normalizarClasse(combatente.classe);
        this.token = token;
        this.magiaService = magiaService || new MagiaService(token);
        this.magias = [];
        this.magiasFiltro = [];
        this.preparadas = new Set();
        this.usadas = new Set();
        this.slotsDisponiveis = {};
        this.nivelAtivo = 'todos';
        this.escolaAtiva = 'todas';
        this.filtroPrepAtivo = false;
        this.cardsAbertos = new Set();
        this._carregado = false;
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
            await this._carregarMagias();
            await this._carregarPreparadas();
            // Inicializar slots se estiverem vazios
            if (!this.combatente.magias_slots || this.combatente.magias_slots.length === 0) {
                await this._inicializarSlots();
            }
            this._calcularSlotsDisponiveis();
            this._carregado = true;
            this._mostrarLoading(false);
        }

        this._renderizarPainelSlots();
        this._renderizarFiltroEscolas();
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
            // Normaliza o nível
            const matchNivel = this.nivelAtivo === 'todos' || String(m.nivel) === String(this.nivelAtivo);
            
            // ✅ CORRIGIDO: Normaliza a escola da magia ANTES de comparar
            const escolaMagia = this._normalizarEscola(m.escola);
            const matchEscola = this.escolaAtiva === 'todas' || escolaMagia === this.escolaAtiva;
            
            // Filtro de preparadas
            const matchPrep = !this.filtroPrepAtivo || this.preparadas.has(m.id);
            
            // Filtro de busca
            const matchBusca = !busca
                || m.nome.toLowerCase().includes(busca)
                || escolaMagia.toLowerCase().includes(busca)
                || (m.descricao || '').toLowerCase().includes(busca);
            
            return matchNivel && matchEscola && matchPrep && matchBusca;
        });

        console.log(`🔍 Magias após filtro: ${this.magiasFiltro.length}`);
        this._renderizarLista();
    }

    descansoLongo() {
        this._mostrarModalConfirmacao({
            icone: '🌙',
            titulo: 'Descanso Longo',
            texto: 'Isso resetará todas as magias preparadas e slots usados. Deseja continuar?',
            textoCancelar: 'Cancelar',
            textoConfirmar: '🌙 Confirmar Descanso',
            onConfirmar: () => this._executarDescansoLongo(),
        });
    }

    // 
    // PRIVADO — DESCANSO
    // 

    async _executarDescansoLongo() {
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
            this.usadas = new Set();
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
    // PRIVADO — MODAL DE CONFIRMAÇÃO
    // 

    _mostrarModalConfirmacao(opcoes) {
        const anterior = document.getElementById('grimorioModalConfirmacao');
        if (anterior) anterior.remove();

        const overlay = document.createElement('div');
        overlay.id = 'grimorioModalConfirmacao';
        overlay.className = 'grimorio-confirm-overlay';
        overlay.innerHTML = `
            <div class="grimorio-confirm-box">
                <div class="grimorio-confirm-header">
                    <span class="grimorio-confirm-icone">${opcoes.icone || '⚠️'}</span>
                    <h3 class="grimorio-confirm-titulo">${opcoes.titulo || 'Confirmar'}</h3>
                </div>
                <p class="grimorio-confirm-texto">${opcoes.texto || 'Deseja continuar?'}</p>
                <div class="grimorio-confirm-botoes">
                    <button class="grimorio-confirm-btn grimorio-confirm-cancelar" id="grimorioConfirmCancelar">
                        ${opcoes.textoCancelar || 'Cancelar'}
                    </button>
                    <button class="grimorio-confirm-btn grimorio-confirm-ok" id="grimorioConfirmOk">
                        ${opcoes.textoConfirmar || 'Confirmar'}
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);
        requestAnimationFrame(() => overlay.classList.add('show'));

        const fechar = () => {
            overlay.classList.remove('show');
            setTimeout(() => { if (overlay.parentNode) overlay.remove(); }, 250);
        };

        document.getElementById('grimorioConfirmCancelar').addEventListener('click', () => {
            fechar();
            if (opcoes.onCancelar) opcoes.onCancelar();
        });

        document.getElementById('grimorioConfirmOk').addEventListener('click', () => {
            fechar();
            if (opcoes.onConfirmar) opcoes.onConfirmar();
        });

        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) fechar();
        });

        const onEsc = (e) => {
            if (e.key === 'Escape') { 
                fechar(); 
                document.removeEventListener('keydown', onEsc); 
            }
        };
        document.addEventListener('keydown', onEsc);
    }

    // 
    // PRIVADO — CARREGAMENTO
    // 

    _normalizarClasse(classe) {
        if (!classe) return '';
        
        const classeUpper = classe.toUpperCase();
        
        const mapa = {
            'MAGO': 'Mago',
            'CLÉRIGO': 'Clérigo',
            'CLERIGO': 'Clérigo',
            'FEITICEIRO': 'Feiticeiro',
            'DRUIDA': 'Druida',
            'BARDO': 'Bardo',
            'PALADINO': 'Paladino',
            'RANGER': 'Ranger',
        };
        
        return mapa[classeUpper] || classeUpper;
    }

    async _carregarMagias() {
        try {
            this.magias = await this.magiaService.listarPorClasse(this.classe);
            this.magiasFiltro = [...this.magias];
            console.log(`✅ Grimório: ${this.magias.length} magias de ${this.classe}`);
            
            // ✅ ADICIONE ISTO:
            this._debugMagias();
        } catch (err) {
            console.error('❌ Erro ao carregar magias:', err);
            this.magias = [];
            this.magiasFiltro = [];
            this._mostrarToast('Erro ao carregar magias.', 'erro');
        }
    }

    async _carregarPreparadas() {
        try {
            const url = getApiUrl(`/magias-preparadas/${this.combatente.id}`);
            const res = await fetch(url, { headers: { 'Authorization': `Bearer ${this.token}` } });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const lista = await res.json();
            this.preparadas = new Set(lista.map(p => p.magia_id));
            this.usadas = new Set(lista.filter(p => p.usada).map(p => p.magia_id));
            console.log(`✅ Preparadas: ${this.preparadas.size} | Usadas hoje: ${this.usadas.size}`);
        } catch (err) {
            console.error('❌ Erro ao carregar preparadas:', err);
            this.preparadas = new Set();
            this.usadas = new Set();
        }
    }

    async _inicializarSlots() {
        try {
            const url = getApiUrl(`/combatentes/${this.combatente.id}/inicializar-slots`);
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            console.log(`✅ Slots inicializados: ${data.slots_criados} slots criados`);
            // Recarregar combatente para atualizar magias_slots
            await this._recarregarCombatente();
        } catch (err) {
            console.error('❌ Erro ao inicializar slots:', err);
        }
    }

    async _recarregarCombatente() {
        try {
            const url = getApiUrl(`/combatentes/${this.combatente.id}`);
            const res = await fetch(url, { headers: { 'Authorization': `Bearer ${this.token}` } });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            this.combatente = await res.json();
            console.log(`✅ Combatente recarregado: ${this.combatente.magias_slots.length} slots`);
        } catch (err) {
            console.error('❌ Erro ao recarregar combatente:', err);
        }
    }


    _calcularSlotsDisponiveis() {
        this.slotsDisponiveis = {};
        
        // Usar dados reais do banco de dados se disponíveis
        if (this.combatente.magias_slots && this.combatente.magias_slots.length > 0) {
            console.log('📊 Usando slots do banco de dados:', this.combatente.magias_slots.length);
            
            this.combatente.magias_slots.forEach(slot => {
                const nivelMagia = slot.nivel;
                
                const preparadasNivel = [...this.preparadas].filter(magiaId => {
                    const m = this.magias.find(x => x.id === magiaId);
                    return m && Number(m.nivel) === Number(nivelMagia);
                }).length;

                const usadasNivel = [...this.usadas].filter(magiaId => {
                    const m = this.magias.find(x => x.id === magiaId);
                    return m && Number(m.nivel) === Number(nivelMagia);
                }).length;

                this.slotsDisponiveis[nivelMagia] = {
                    total: slot.total,
                    preparadas: preparadasNivel,
                    usadas: usadasNivel,
                    disponivel: slot.total - preparadasNivel,
                };
            });
        } else {
            // Fallback: calcular baseado em tabela se não houver dados no banco
            console.log('📊 Calculando slots baseado em tabela');
            
            const nivel = Math.max(1, Math.min(20, this.combatente.nivel || 1));
            let classeParaTabela = this.classe;
            
            // Feiticeiro usa os mesmos slots que Mago
            if (classeParaTabela === 'Feiticeiro') {
                classeParaTabela = 'Mago';
            }
            
            const tabelaClasse = TABELA_MAGIAS_DIA[classeParaTabela];

            if (!tabelaClasse) {
                console.warn('⚠️ Classe sem tabela de slots:', this.classe);
                return;
            }

            const linhaNivel = tabelaClasse[nivel - 1] || [];
            const attrChave = ATRIBUTO_CHAVE[this.classe] || 'inteligencia';
            const valorAttr = this.combatente[attrChave] || 10;
            const mod = Math.floor((valorAttr - 10) / 2);
            const bonusAttr = BONUS_ATRIBUTO[Math.max(0, mod)] || [];

            linhaNivel.forEach((base, nivelMagia) => {
                if (base === null || base === undefined) return;

                const bonus = nivelMagia > 0 ? (bonusAttr[nivelMagia - 1] || 0) : 0;
                const total = base + bonus;

                const preparadasNivel = [...this.preparadas].filter(magiaId => {
                    const m = this.magias.find(x => x.id === magiaId);
                    return m && Number(m.nivel) === Number(nivelMagia);
                }).length;

                const usadasNivel = [...this.usadas].filter(magiaId => {
                    const m = this.magias.find(x => x.id === magiaId);
                    return m && Number(m.nivel) === Number(nivelMagia);
                }).length;

                this.slotsDisponiveis[nivelMagia] = {
                    total,
                    preparadas: preparadasNivel,
                    usadas: usadasNivel,
                    disponivel: total - preparadasNivel,
                };
            });
        }

        console.log('📊 Slots disponíveis:', JSON.stringify(this.slotsDisponiveis));
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

    async _toggleUsada(magiaId, nivelMagia) {
        try {
            const url = getApiUrl(`/magias-preparadas/${this.combatente.id}/${magiaId}/usar`);
            const res = await fetch(url, {
                method: 'PATCH',
                headers: { 'Authorization': `Bearer ${this.token}` },
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();

            if (data.usada) {
                this.usadas.add(magiaId);
                this._mostrarToast('🔥 Magia lançada!', 'info');
            } else {
                this.usadas.delete(magiaId);
                this._mostrarToast('↩️ Magia restaurada.', 'sucesso');
            }

            this._calcularSlotsDisponiveis();
            this._renderizarPainelSlots();
            this._atualizarCard(magiaId, nivelMagia);
        } catch (err) {
            console.error('❌ Erro ao marcar usada:', err);
            this._mostrarToast('Erro ao marcar magia como usada.', 'erro');
        }
    }

    async _prepararMagia(magiaId, nivelMagia) {
        this._calcularSlotsDisponiveis();
        const slot = this.slotsDisponiveis[nivelMagia];
        console.log(`🔍 Validando slot nível ${nivelMagia}:`, slot);

        if (Number(nivelMagia) === 0) {
            await this._persistirPreparacao(magiaId, nivelMagia);
            return;
        }

        if (!slot) {
            this._mostrarToast(`⚠️ Nenhum slot configurado para nível ${nivelMagia}.`, 'erro');
            return;
        }

        if (slot.disponivel <= 0) {
            this._mostrarToast(`⚠️ Slots de nível ${nivelMagia} esgotados (${slot.preparadas}/${slot.total})!`, 'erro');
            return;
        }

        await this._persistirPreparacao(magiaId, nivelMagia);
    }

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
            this.usadas.delete(magiaId);
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

        const btnPrep = document.getElementById('btnFiltroPreparadas');
        if (btnPrep) {
            btnPrep.replaceWith(btnPrep.cloneNode(true));
            document.getElementById('btnFiltroPreparadas')?.addEventListener('click', () => {
                this.filtroPrepAtivo = !this.filtroPrepAtivo;
                const btn = document.getElementById('btnFiltroPreparadas');
                if (btn) btn.classList.toggle('ativo', this.filtroPrepAtivo);
                this.filtrar();
            });
        }

        const btnDescanso = document.getElementById('btnDescansoLongo');
        if (btnDescanso) {
            btnDescanso.replaceWith(btnDescanso.cloneNode(true));
            document.getElementById('btnDescansoLongo')
                ?.addEventListener('click', () => this.descansoLongo());
        }
    }

    /**
     * Debug: mostra informações sobre as magias carregadas
     */
    _debugMagias() {
        console.group('🔍 DEBUG - Magias Carregadas');
        console.log('Total de magias:', this.magias.length);
        
        if (this.magias.length > 0) {
            const escolas = new Set(this.magias.map(m => m.escola).filter(Boolean));
            console.log('Escolas encontradas:', Array.from(escolas));
            console.log('Primeira magia:', this.magias[0]);
        }
        
        console.groupEnd();
    }

    _normalizarEscola(escola) {
        if (!escola) return '';
        
        const mapa = {
            // Abreviaturas simples
            'abjur': 'Abjuração',
            'abjru': 'Abjuração',
            'adiv': 'Adivinhação',
            'conj': 'Conjuração',
            'conjur': 'Conjuração',
            'encan': 'Encantamento',
            'encant': 'Encantamento',
            'evoc': 'Evocação',
            'ilus': 'Ilusão',
            'necr': 'Necromancia',
            'trans': 'Transmutação',
            'transm': 'Transmutação',
            'univ': 'Universal',
            
            // Nomes completos
            'conjuração': 'Conjuração',
            'evocação': 'Evocação',
            'ilusão': 'Ilusão',
            'transmutação': 'Transmutação',
            'necromancia': 'Necromancia',
            'encantamento': 'Encantamento',
            'abjuração': 'Abjuração',
            'adivinhação': 'Adivinhação',
            'universal': 'Universal',
            'escola': '',
        };
        
        // Extrai apenas a escola base: pega tudo antes de [, (, espaço, ponto ou quebra de linha
        const base = escola
            .replace(/[\n\r]/g, ' ')
            .split(/[\[\(\.\s]/)[0]
            .toLowerCase()
            .trim();
        
        return mapa[base] || escola.charAt(0).toUpperCase() + escola.slice(1);
    }

    _renderizarFiltroEscolas() {
        const container = document.getElementById('grimorioFiltroEscolas');
        if (!container) {
            console.warn('⚠️ Container grimorioFiltroEscolas não encontrado');
            return;
        }

        // Extrai e normaliza escolas únicas das magias
        const escolasPresentes = new Set();
        this.magias.forEach(m => {
            if (m.escola && m.escola.trim()) {
                const escolaNormalizada = this._normalizarEscola(m.escola);
                escolasPresentes.add(escolaNormalizada);
            }
        });

        console.log(`📚 Escolas encontradas (antes): ${this.magias.map(m => m.escola).filter(Boolean).length}`);
        console.log(`📚 Escolas únicas (depois de normalizar): ${Array.from(escolasPresentes).join(', ')}`);

        // Filtra apenas escolas da ordem padronizada que têm magias
        const escolas = ESCOLAS_ORDEM.filter(e => escolasPresentes.has(e));

        console.log(`📚 Escolas a renderizar: ${escolas.length}`);

        if (escolas.length === 0) {
            console.warn('⚠️ Nenhuma escola encontrada nas magias');
            container.style.display = 'none';
            return;
        }

        // ✅ MOSTRA O CONTAINER
        container.style.display = 'block';

        // Renderiza botões de escolas
        container.innerHTML = `
            <button class="grimorio-escola-btn ativo" data-escola="todas">Todas</button>
            ${escolas.map(e => `
                <button class="grimorio-escola-btn" data-escola="${e}">
                    ${EMOJI_ESCOLA[e] || ''} ${e}
                </button>
            `).join('')}
        `;

        console.log(`✅ ${escolas.length} botões de escola renderizados`);

        // Configura listeners
        container.querySelectorAll('.grimorio-escola-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                container.querySelectorAll('.grimorio-escola-btn').forEach(b => b.classList.remove('ativo'));
                btn.classList.add('ativo');
                this.escolaAtiva = btn.dataset.escola;
                console.log(`🎓 Filtro de escola ativo: ${this.escolaAtiva}`);
                this.filtrar();
            });
        });
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
            const s = this.slotsDisponiveis[n];
            const pct = s.total > 0 ? (s.preparadas / s.total) * 100 : 0;
            const cor = s.disponivel === 0 ? '#f87171'
                      : s.preparadas > 0 ? '#facc15'
                      : '#4ade80';
            const usadasInfo = s.usadas > 0 ? ` · ${s.usadas} lançada(s)` : '';

            return `
                <div class="grimorio-slot-box"
                     title="Nível ${n}: ${s.preparadas}/${s.total} preparadas${usadasInfo}">
                    <span class="grimorio-slot-nivel">${n === 0 ? '0' : n + 'º'}</span>
                    <div class="grimorio-slot-barra-wrap">
                        <div class="grimorio-slot-barra-fill" style="width:${pct}%;background:${cor}"></div>
                    </div>
                    <span class="grimorio-slot-contagem" style="color:${cor}">
                        ${s.preparadas}/${s.total}
                    </span>
                    ${s.usadas > 0 ? `<span class="grimorio-slot-usadas">🔥${s.usadas}</span>` : ''}
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
            0: '✦ Truques (Cantrips)',
            1: '✦ 1° Nível',
            2: '✦ 2° Nível',
            3: '✦ 3° Nível',
            4: '✦ 4° Nível',
            5: '✦ 5° Nível',
            6: '✦ 6° Nível',
            7: '✦ 7° Nível',
            8: '✦ 8° Nível',
            9: '✦ 9° Nível',
        };

        lista.innerHTML = Object.keys(grupos)
            .map(Number)
            .sort((a, b) => a - b)
            .map(nivel => {
                const slot = this.slotsDisponiveis[nivel];
                const slotInfo = slot
                    ? `<span class="grimorio-grupo-slots">${slot.preparadas}/${slot.total} preparadas${slot.usadas > 0 ? ` · 🔥${slot.usadas}` : ''}</span>`
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
            })
            .join('');

        lista.querySelectorAll('.grimorio-checkbox').forEach(cb => {
            cb.addEventListener('change', () => {
                const magiaId = Number(cb.dataset.magiaId);
                const nivelMag = Number(cb.dataset.nivel);
                this._togglePreparacao(magiaId, nivelMag);
            });
        });

        lista.querySelectorAll('.grimorio-checkbox-usada').forEach(cb => {
            cb.addEventListener('change', () => {
                const magiaId = Number(cb.dataset.magiaId);
                const nivelMag = Number(cb.dataset.nivel);
                this._toggleUsada(magiaId, nivelMag);
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
        const escolaNorm = this._normalizarEscola(m.escola);
        const emoji = EMOJI_ESCOLA[escolaNorm] || '📜';
        const preparada = this.preparadas.has(m.id);
        const usada = this.usadas.has(m.id);
        const aberto = this.cardsAbertos.has(m.id);
        const temDano = m.dano && m.dano.trim();
        const slot = this.slotsDisponiveis[m.nivel];
        const semSlot = slot && !preparada && slot.disponivel <= 0;

        const badges = [
            escolaNorm ? `<span class="grimorio-badge grimorio-badge-escola">${emoji} ${escolaNorm}</span>` : '',
            m.componentes ? `<span class="grimorio-badge grimorio-badge-comp">${m.componentes}</span>` : '',
            temDano ? `<span class="grimorio-badge grimorio-badge-dano">🗡 ${m.dano}</span>` : '',
            m.teste_resistencia && m.teste_resistencia !== 'Nenhum'
                ? `<span class="grimorio-badge grimorio-badge-res">🎲 ${m.teste_resistencia}</span>`
                : '',
        ].filter(Boolean).join('');

        const metaItens = [
            { label: 'Alcance', valor: m.alcance },
            { label: 'Duração', valor: m.duracao },
            { label: 'Conjuração', valor: m.tempo_conjuracao },
            { label: 'Área', valor: m.area_efeito },
        ]
            .filter(i => i.valor?.trim())
            .map(i => `
                <div class="grimorio-meta-item">
                    <span class="grimorio-meta-label">${i.label}</span>
                    <span class="grimorio-meta-valor">${i.valor}</span>
                </div>
            `)
            .join('');

        const detalhes = `
            <div class="grimorio-card-detalhes ${aberto ? 'show' : ''}">
                ${m.sub_escola ? `<div class="grimorio-detalhe-linha">
                    <span class="grimorio-detalhe-chave">Sub-escola</span>
                    <span class="grimorio-detalhe-valor">${m.sub_escola}</span>
                </div>` : ''}
                ${temDano ? `<div class="grimorio-detalhe-linha">
                    <span class="grimorio-detalhe-chave">Dano</span>
                    <span class="grimorio-detalhe-valor grimorio-dano-destaque">${m.dano}</span>
                </div>` : ''}
                ${m.teste_resistencia ? `<div class="grimorio-detalhe-linha">
                    <span class="grimorio-detalhe-chave">Resistência</span>
                    <span class="grimorio-detalhe-valor">${m.teste_resistencia}</span>
                </div>` : ''}
                <div class="grimorio-detalhe-linha">
                    <span class="grimorio-detalhe-chave">Res. Mágica</span>
                    <span class="grimorio-detalhe-valor">${m.resistencia_magica ? '✅ Sim' : '❌ Não'}</span>
                </div>
            </div>
        `;

        const checkboxUsada = preparada ? `
            <label class="grimorio-usada-label" title="${usada ? 'Restaurar magia' : 'Marcar como lançada hoje'}">
                <input type="checkbox"
                       class="grimorio-checkbox-usada"
                       data-magia-id="${m.id}"
                       data-nivel="${m.nivel}"
                       ${usada ? 'checked' : ''}>
                <span class="grimorio-usada-custom ${usada ? 'usada' : ''}">🔥</span>
                <span class="grimorio-usada-texto">${usada ? 'Lançada' : 'Lançar'}</span>
            </label>
        ` : '';

        return `
            <div class="grimorio-magia-card
                        ${preparada ? 'preparada' : ''}
                        ${usada ? 'ja-usada' : ''}
                        ${semSlot ? 'sem-slot' : ''}"
                 data-id="${m.id}">
                <div class="grimorio-card-topo">
                    <label class="grimorio-checkbox-label"
                           title="${semSlot ? 'Sem slots disponíveis' : preparada ? 'Remover da preparação' : 'Preparar magia'}">
                        <input type="checkbox"
                               class="grimorio-checkbox"
                               data-magia-id="${m.id}"
                               data-nivel="${m.nivel}"
                               ${preparada ? 'checked' : ''}
                               ${semSlot ? 'disabled' : ''}>
                        <span class="grimorio-checkbox-custom ${preparada ? 'checked' : ''} ${semSlot ? 'disabled' : ''}"></span>
                    </label>
                    <span class="grimorio-card-nome ${preparada ? 'preparada-nome' : ''} ${usada ? 'usada-nome' : ''}">${m.nome}</span>
                    <div class="grimorio-card-badges">${badges}</div>
                </div>
                <p class="grimorio-card-descricao">${m.descricao || '—'}</p>
                <div class="grimorio-card-meta">${metaItens}</div>
                ${detalhes}
                <div class="grimorio-card-rodape">
                    <button class="grimorio-expandir-btn" data-id="${m.id}">
                        ${aberto ? '▲ Menos detalhes' : '▼ Ver detalhes'}
                    </button>
                    <div class="grimorio-rodape-direita">
                        ${checkboxUsada}
                        ${preparada ? '<span class="grimorio-preparada-badge">✦ Preparada</span>' : ''}
                    </div>
                </div>
            </div>
        `;
    }

    _atualizarCard(magiaId, nivelMagia) {
        const card = document.querySelector(`.grimorio-magia-card[data-id="${magiaId}"]`);
        if (!card) {
            this._renderizarLista();
            return;
        }

        const preparada = this.preparadas.has(magiaId);
        const usada = this.usadas.has(magiaId);
        const slot = this.slotsDisponiveis[nivelMagia];
        const semSlot = slot && !preparada && slot.disponivel <= 0;

        card.classList.toggle('preparada', preparada);
        card.classList.toggle('ja-usada', usada);
        card.classList.toggle('sem-slot', semSlot);

        const cb = card.querySelector('.grimorio-checkbox');
        if (cb) {
            cb.checked = preparada;
            cb.disabled = semSlot;
        }

        const cbCustom = card.querySelector('.grimorio-checkbox-custom');
        if (cbCustom) {
            cbCustom.classList.toggle('checked', preparada);
            cbCustom.classList.toggle('disabled', semSlot);
        }

        const nome = card.querySelector('.grimorio-card-nome');
        if (nome) {
            nome.classList.toggle('preparada-nome', preparada);
            nome.classList.toggle('usada-nome', usada);
        }

        const cbUsada = card.querySelector('.grimorio-checkbox-usada');
        if (cbUsada) {
            cbUsada.checked = usada;
            const usadaCustom = card.querySelector('.grimorio-usada-custom');
            if (usadaCustom) usadaCustom.classList.toggle('usada', usada);
            const usadaTexto = card.querySelector('.grimorio-usada-texto');
            if (usadaTexto) usadaTexto.textContent = usada ? 'Lançada' : 'Lançar';
        }

        const rodape = card.querySelector('.grimorio-card-rodape');
        if (rodape) {
            const badgeExistente = rodape.querySelector('.grimorio-preparada-badge');
            if (preparada && !badgeExistente) {
                const dir = rodape.querySelector('.grimorio-rodape-direita') || rodape;
                dir.insertAdjacentHTML('beforeend', '<span class="grimorio-preparada-badge">✦ Preparada</span>');
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

        const card = document.querySelector(`.grimorio-magia-card[data-id="${id}"]`);
        if (!card) return;

        const detalhes = card.querySelector('.grimorio-card-detalhes');
        const btn = card.querySelector('.grimorio-expandir-btn');

        if (detalhes) detalhes.classList.toggle('show', this.cardsAbertos.has(id));
        if (btn) btn.textContent = this.cardsAbertos.has(id) ? '▲ Menos detalhes' : '▼ Ver detalhes';
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
        const el = document.getElementById('grimorioLoading');
        const lista = document.getElementById('grimorioLista');
        if (el) el.style.display = visivel ? 'flex' : 'none';
        if (lista) lista.style.display = visivel ? 'none' : 'block';
    }
}

// ── Inicialização ──
document.addEventListener('DOMContentLoaded', () => {
    const tentarInicializar = setInterval(() => {
        const classeEl = document.getElementById('fichaClasse');
        if (!classeEl) return;

        const classe = classeEl.textContent?.trim();
        if (!classe || classe === '—') return;

        const combatente = window._fichaController?.combatente;
        if (!combatente) return;

        clearInterval(tentarInicializar);

        const token = localStorage.getItem('token');
        const magiaService = new MagiaService(token);
        
        window._grimorioController = new GrimorioController(combatente, token, magiaService);

        if (CLASSES_CONJURADORAS.has(classe.toLowerCase()) || CLASSES_CONJURADORAS.has(classe)) {
            const btnHeader = document.getElementById('btnGrimorio');
            const secaoMagia = document.getElementById('secaoMagias');
            if (btnHeader) btnHeader.style.display = 'inline-flex';
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

export { GrimorioController };