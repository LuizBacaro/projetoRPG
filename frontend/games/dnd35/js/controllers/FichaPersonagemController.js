/**
 * FichaPersonagemController.js
 * SRP: Controlar renderização da ficha do personagem
 * SOLID: DIP via constructor injection de services
 * ✅ NOVO: BroadcastChannel sync arena→ficha em tempo real
 */

import { CombatenteService } from '../services/CombatenteService.js';
import { EquipamentoService } from '../services/EquipamentoService.js';
import { ArmaduraProtecaoService } from '../services/ArmaduraProtecaoService.js';
import { TalentoService } from '../services/TalentoService.js?v=3';
import { PericiaService } from '../services/PericiaService.js';
import { getApiUrl } from '../config/api.config.js';
import { escapeHtml } from '../utils/formatters.js';
import {
    installGlobalErrorGuards,
    safeBootstrap,
    safeBootstrapAsync,
} from '../utils/graceful-degradation.js';
import {
    resolveCombatenteSpellSlots,
    isClasseConjuradora,
    normalizeClasseConjuradora,
    textoSlotsClerigoBreakdown,
} from '../utils/combat-rules.js?v=20260419a';
import { modificadorPericiaPreferindoDomFicha } from '../utils/dnd.js?v=20260420b';
import { resolverBonusRaciaisPorPericia } from '../utils/pericia-racial.js?v=20260421a';

const DOMINIOS_PERMITIDOS_FALLBACK = [
    'Ar', 'Bem', 'Caos', 'Conhecimento', 'Cura', 'Destruição', 'Enganação', 'Fogo', 'Força',
    'Guerra', 'Magia', 'Mal', 'Morte', 'Proteção', 'Sol', 'Sorte', 'Terra', 'Viagem',
];

// Fallback do catalogo de divindades (Tabela 3-7 do Livro do Jogador 3.5).
// Usado apenas quando o endpoint /magias/divindades/catalogo estiver offline.
// Campos: { nome, titulo, label, tendencia, dominios }
const DIVINDADES_CATALOGO_FALLBACK = [
    { nome: 'Heironeous',         titulo: 'Deus do Heroísmo',          tendencia: 'Leal e Bom',       dominios: ['Bem', 'Ordem', 'Guerra'] },
    { nome: 'Moradin',            titulo: 'Deus dos Anões',            tendencia: 'Leal e Bom',       dominios: ['Terra', 'Bem', 'Ordem', 'Proteção'] },
    { nome: 'Yondalla',           titulo: 'Deusa dos Halflings',       tendencia: 'Leal e Bom',       dominios: ['Bem', 'Ordem', 'Proteção'] },
    { nome: 'Ehlonna',            titulo: 'Deusa das Florestas',       tendencia: 'Neutro e Bom',     dominios: ['Animal', 'Bem', 'Planta', 'Sol'] },
    { nome: 'Garl Glittergold',   titulo: 'Deus dos Gnomos',           tendencia: 'Neutro e Bom',     dominios: ['Bem', 'Proteção', 'Enganação'] },
    { nome: 'Pelor',              titulo: 'Deus do Sol',               tendencia: 'Neutro e Bom',     dominios: ['Bem', 'Cura', 'Força', 'Sol'] },
    { nome: 'Corellon Larethian', titulo: 'Deus dos Elfos',            tendencia: 'Caótico e Bom',    dominios: ['Caos', 'Bem', 'Proteção', 'Guerra'] },
    { nome: 'Kord',               titulo: 'Deus da Força',             tendencia: 'Caótico e Bom',    dominios: ['Caos', 'Bem', 'Sorte', 'Força'] },
    { nome: 'Wee Jas',            titulo: 'Deusa da Morte e da Magia', tendencia: 'Leal e Neutro',    dominios: ['Morte', 'Ordem', 'Magia'] },
    { nome: 'St. Cuthbert',       titulo: 'Deus da Retribuição',       tendencia: 'Leal e Neutro',    dominios: ['Destruição', 'Ordem', 'Proteção', 'Força'] },
    { nome: 'Boccob',             titulo: 'Deus da Magia',             tendencia: 'Neutro',           dominios: ['Conhecimento', 'Magia', 'Enganação'] },
    { nome: 'Fharlanghn',         titulo: 'Deus das Estradas',         tendencia: 'Neutro',           dominios: ['Sorte', 'Proteção', 'Viagem'] },
    { nome: 'Obad-Hai',           titulo: 'Deus da Natureza',          tendencia: 'Neutro',           dominios: ['Ar', 'Animal', 'Terra', 'Fogo', 'Planta', 'Água'] },
    { nome: 'Olidammara',         titulo: 'Deus dos Ladrões',          tendencia: 'Caótico e Neutro', dominios: ['Caos', 'Sorte', 'Enganação'] },
    { nome: 'Hextor',             titulo: 'Deus da Tirania',           tendencia: 'Leal e Mau',       dominios: ['Destruição', 'Mal', 'Ordem', 'Guerra'] },
    { nome: 'Nerull',             titulo: 'Deus da Morte',             tendencia: 'Neutro e Mau',     dominios: ['Morte', 'Mal', 'Enganação', 'Guerra'] },
    { nome: 'Vecna',              titulo: 'Deus dos Segredos',         tendencia: 'Neutro e Mau',     dominios: ['Mal', 'Conhecimento', 'Magia'] },
    { nome: 'Erythnul',           titulo: 'Deus da Matança',           tendencia: 'Caótico e Mau',    dominios: ['Caos', 'Mal', 'Enganação', 'Guerra'] },
    { nome: 'Gruumsh',            titulo: 'Deus dos Orcs',             tendencia: 'Caótico e Mau',    dominios: ['Caos', 'Mal', 'Força', 'Guerra'] },
].map((item) => ({ ...item, label: `${item.nome}, ${item.titulo}` }));

export class FichaPersonagemController {

    constructor() {
        this.combatenteService = new CombatenteService();
        this.equipamentoService = new EquipamentoService();
        this.armaduraProtecaoService = new ArmaduraProtecaoService();
        this.talentoService = new TalentoService();
        this.periciaService = new PericiaService();
        this.combatente        = null;
        this.bonusCaProtecao   = 0;
        this.dominiosPermitidos = [...DOMINIOS_PERMITIDOS_FALLBACK];
        this.divindadesCatalogo = DIVINDADES_CATALOGO_FALLBACK.map((item) => ({ ...item }));
        this.fonteDivindades = 'fallback';
        this._dadosDivinosCarregados = false;

        // ✅ NOVO: canal de escuta arena → ficha
        this._canal = null;
        this._configurarCanalSync();

        // ✅ NOVO: paginação para talentos
        this.talentosDisponiveis = [];
        this.talentosSkip = 0;
        this.talentosLimit = 20;
        this.talentosCarregados = false;

        // Paginação modais: equipamentos e armaduras (catálogo)
        this.equipamentosSkip = 0;
        this.equipamentosLimit = 20;
        this.equipamentosCarregados = false;

        this.armadurasProtecaoSkip = 0;
        this.armadurasProtecaoLimit = 20;
        this.armadurasProtecaoCarregados = false;

        this.equipamentosDisponiveis = [];
        this.armadurasProtecaoDisponiveis = [];
        this.talentosJogador = [];
        this.idiomasFichaDraft = [];

    }

    get token() {
        return localStorage.getItem('token');
    }

    set token(_value) {
        // Compatibilidade: token sempre lido ao vivo do localStorage.
    }

    async inicializar() {
        try {
            const params       = new URLSearchParams(window.location.search);
            const combatenteId = params.get('id');

            if (!combatenteId) throw new Error('ID do combatente não fornecido');


            this.combatente = await this.combatenteService.obterCombatente(parseInt(combatenteId));

            // ✅ Expor globalmente para debug no console
            window._fichaController = this;


            // ── Renderizar tudo ──
            this.renderizarIdentidade();
            this._atualizarHeaderNome();
            this.renderizarAtributos();
            this.renderizarDefesa();
            this.renderizarDinheiro();
            this.renderizarResistencias();
            this.renderizarHabilidadesEspeciais();
            this.renderizarIdiomas();
            this.renderizarCaracteristicasRaciais();
            this.renderizarAtaques();
            this.renderizarSlotsDeMapia();

            // ── Skeleton enquanto os 4 requests paralelos carregam ──
            this._mostrarSkeletonFicha();
            await Promise.all([
                this.carregarRenderizarPericias(parseInt(combatenteId)),
                this.carregarRenderizarEquipamentos(parseInt(combatenteId)),
                this.carregarRenderizarArmadurasProtecao(parseInt(combatenteId)),
                this.carregarRenderizarTalentos(parseInt(combatenteId)),
            ]);

            // ── Configurar eventos ──
            this._configurarEventos();


        } catch (error) {
            console.error('❌ Erro ao inicializar ficha:', error);
            const msg = String(error?.message || '');
            if (msg.includes('401')) {
                return;
            }
            this.mostrarErro('Erro ao carregar ficha: ' + error.message);
        }
    }

    _configurarEventos() {
        const btnEditarAtaques = document.getElementById('btnEditarAtaques');
        if (btnEditarAtaques) {
            btnEditarAtaques.addEventListener('click', () => this._abrirEditorAtaques());
        }

        const btnAdicionarLinhaAtaque = document.getElementById('btnAdicionarLinhaAtaque');
        if (btnAdicionarLinhaAtaque) {
            btnAdicionarLinhaAtaque.addEventListener('click', () => this._adicionarLinhaAtaqueEditor());
        }

        const btnSalvarAtaques = document.getElementById('btnSalvarAtaques');
        if (btnSalvarAtaques) {
            btnSalvarAtaques.addEventListener('click', () => this._salvarAtaques());
        }

        const btnCancelarAtaques = document.getElementById('btnCancelarAtaques');
        if (btnCancelarAtaques) {
            btnCancelarAtaques.addEventListener('click', () => {
                document.getElementById('fichaAtaquesEditor').style.display = 'none';
            });
        }

        const btnVoltar = document.getElementById('btnVoltarFicha');
        if (btnVoltar) {
            btnVoltar.addEventListener('click', () => {
                window.location.href = '/games/dnd35/pages/dashboard.html';
            });
        }

        const btnAdicionarEq = document.getElementById('btnAdicionarEquipamento');
        if (btnAdicionarEq) {
            btnAdicionarEq.addEventListener('click', () => this.abrirModalEquipamentos());
        }

        const btnAdicionarProtecao = document.getElementById('btnAdicionarArmaduraProtecao');
        if (btnAdicionarProtecao) {
            btnAdicionarProtecao.addEventListener('click', () => this.abrirModalArmadurasProtecao());
        }

        const btnAdicionarTal = document.getElementById('btnAdicionarTalento');
        if (btnAdicionarTal) {
            btnAdicionarTal.addEventListener('click', () => this.abrirModalTalentos());
        }
        const btnAdicionarIdiomaFicha = document.getElementById('btnAdicionarIdiomaFicha');
        if (btnAdicionarIdiomaFicha) {
            btnAdicionarIdiomaFicha.addEventListener('click', () => this.adicionarIdiomaFicha());
        }
        const inputNovoIdiomaFicha = document.getElementById('inputNovoIdiomaFicha');
        if (inputNovoIdiomaFicha) {
            inputNovoIdiomaFicha.addEventListener('keydown', (event) => {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    this.adicionarIdiomaFicha();
                }
            });
        }

        const btnEditarPerfilMagico = document.getElementById('btnEditarPerfilMagico');
        if (btnEditarPerfilMagico) {
            btnEditarPerfilMagico.addEventListener('click', () => this.abrirModalPerfilMagico());
        }
        const btnAbrirCaracteristicasRaciais = document.getElementById('btnAbrirCaracteristicasRaciais');
        if (btnAbrirCaracteristicasRaciais) {
            btnAbrirCaracteristicasRaciais.addEventListener('click', () => this.abrirModalCaracteristicasRaciais());
        }

        const btnFecharModalPerfilMagico = document.getElementById('btnFecharModalPerfilMagico');
        if (btnFecharModalPerfilMagico) {
            btnFecharModalPerfilMagico.addEventListener('click', () => this.fecharModalPerfilMagico());
        }

        const btnCancelarPerfilMagico = document.getElementById('btnCancelarPerfilMagico');
        if (btnCancelarPerfilMagico) {
            btnCancelarPerfilMagico.addEventListener('click', () => this.fecharModalPerfilMagico());
        }

        const btnSalvarPerfilMagico = document.getElementById('btnSalvarPerfilMagico');
        if (btnSalvarPerfilMagico) {
            btnSalvarPerfilMagico.addEventListener('click', () => this.salvarPerfilMagico());
        }

        const modalPerfilMagico = document.getElementById('modalPerfilMagico');
        if (modalPerfilMagico) {
            modalPerfilMagico.addEventListener('click', (event) => {
                if (event.target === modalPerfilMagico) this.fecharModalPerfilMagico();
            });
        }
        const btnFecharModalCaracteristicasRaciais = document.getElementById('btnFecharModalCaracteristicasRaciais');
        if (btnFecharModalCaracteristicasRaciais) {
            btnFecharModalCaracteristicasRaciais.addEventListener('click', () => this.fecharModalCaracteristicasRaciais());
        }
        const btnFecharModalCaracteristicasRaciaisRodape = document.getElementById('btnFecharModalCaracteristicasRaciaisRodape');
        if (btnFecharModalCaracteristicasRaciaisRodape) {
            btnFecharModalCaracteristicasRaciaisRodape.addEventListener('click', () => this.fecharModalCaracteristicasRaciais());
        }
        const modalCaracteristicasRaciais = document.getElementById('modalCaracteristicasRaciais');
        if (modalCaracteristicasRaciais) {
            modalCaracteristicasRaciais.addEventListener('click', (event) => {
                if (event.target === modalCaracteristicasRaciais) this.fecharModalCaracteristicasRaciais();
            });
        }
        const btnAbrirModalDinheiro = document.getElementById('btnAbrirModalDinheiro');
        if (btnAbrirModalDinheiro) {
            btnAbrirModalDinheiro.addEventListener('click', () => this.abrirModalDinheiro());
        }
        const btnFecharModalDinheiro = document.getElementById('btnFecharModalDinheiro');
        if (btnFecharModalDinheiro) {
            btnFecharModalDinheiro.addEventListener('click', () => this.fecharModalDinheiro());
        }
        const btnCancelarModalDinheiro = document.getElementById('btnCancelarModalDinheiro');
        if (btnCancelarModalDinheiro) {
            btnCancelarModalDinheiro.addEventListener('click', () => this.fecharModalDinheiro());
        }
        const btnSalvarModalDinheiro = document.getElementById('btnSalvarModalDinheiro');
        if (btnSalvarModalDinheiro) {
            btnSalvarModalDinheiro.addEventListener('click', () => this.salvarModalDinheiro());
        }
        ['inputDinheiroPC', 'inputDinheiroPP', 'inputDinheiroPO', 'inputDinheiroPL'].forEach((id) => {
            const el = document.getElementById(id);
            if (el) el.addEventListener('input', () => this._atualizarTotalDinheiroPo());
        });
        const modalDinheiro = document.getElementById('modalDinheiro');
        if (modalDinheiro) {
            modalDinheiro.addEventListener('click', (event) => {
                if (event.target === modalDinheiro) this.fecharModalDinheiro();
            });
        }

        const btnGrimorio = document.getElementById('btnGrimorio');
        if (btnGrimorio) {
            btnGrimorio.addEventListener('click', () => window._grimorioController?.abrirGrimorio());
        }

        const btnAbrirGrimorio = document.getElementById('btnAbrirGrimorio');
        if (btnAbrirGrimorio) {
            btnAbrirGrimorio.addEventListener('click', () => window._grimorioController?.abrirGrimorio());
        }

        const btnFecharGrimorio = document.getElementById('btnFecharGrimorio');
        if (btnFecharGrimorio) {
            btnFecharGrimorio.addEventListener('click', () => window._grimorioController?.fecharGrimorio());
        }

        const grimorioBusca = document.getElementById('grimorioBusca');
        if (grimorioBusca) {
            grimorioBusca.addEventListener('input', () => window._grimorioController?.filtrar());
        }

        const btnAbrirPericias = document.getElementById('btnAbrirPericiasFicha');
        if (btnAbrirPericias) {
            btnAbrirPericias.addEventListener('click', () => this.abrirPaginaPericias());
        }

        const btnFecharModalEquipamentos = document.getElementById('btnFecharModalEquipamentos');
        if (btnFecharModalEquipamentos) {
            btnFecharModalEquipamentos.addEventListener('click', () => this.fecharModalEquipamentos());
        }

        const btnFecharModalArmadurasProtecao = document.getElementById('btnFecharModalArmadurasProtecao');
        if (btnFecharModalArmadurasProtecao) {
            btnFecharModalArmadurasProtecao.addEventListener('click', () => this.fecharModalArmadurasProtecao());
        }

        const equipamentosBusca = document.getElementById('equipamentosBusca');
        if (equipamentosBusca) {
            equipamentosBusca.addEventListener('input', () => {
                void this.filtrarEquipamentos();
            });
        }

        const armadurasProtecaoBusca = document.getElementById('armadurasProtecaoBusca');
        if (armadurasProtecaoBusca) {
            armadurasProtecaoBusca.addEventListener('input', () => {
                void this.filtrarArmadurasProtecao();
            });
        }

        const abaListar = document.getElementById('abaListar');
        if (abaListar) {
            abaListar.addEventListener('click', () => this.abrirAbaListar());
        }

        const abaCriar = document.getElementById('abaCriar');
        if (abaCriar) {
            abaCriar.addEventListener('click', () => this.abrirAbaCriar());
        }

        const abaListarArmadurasProtecao = document.getElementById('abaListarArmadurasProtecao');
        if (abaListarArmadurasProtecao) {
            abaListarArmadurasProtecao.addEventListener('click', () => this.abrirAbaListarArmadurasProtecao());
        }

        const abaCriarArmaduraProtecao = document.getElementById('abaCriarArmaduraProtecao');
        if (abaCriarArmaduraProtecao) {
            abaCriarArmaduraProtecao.addEventListener('click', () => this.abrirAbaCriarArmaduraProtecao());
        }

        const btnSalvarEquipamentoCustomizado = document.getElementById('btnSalvarEquipamentoCustomizado');
        if (btnSalvarEquipamentoCustomizado) {
            btnSalvarEquipamentoCustomizado.addEventListener('click', () => this.salvarEquipamentoCustomizado());
        }

        const btnSalvarArmaduraProtecaoCustomizada = document.getElementById('btnSalvarArmaduraProtecaoCustomizada');
        if (btnSalvarArmaduraProtecaoCustomizada) {
            btnSalvarArmaduraProtecaoCustomizada.addEventListener('click', () => this.salvarArmaduraProtecaoCustomizada());
        }

        const btnFecharModalTalentos = document.getElementById('btnFecharModalTalentos');
        if (btnFecharModalTalentos) {
            btnFecharModalTalentos.addEventListener('click', () => this.fecharModalTalentos());
        }

        const talentosBusca = document.getElementById('talentosBusca');
        if (talentosBusca) {
            talentosBusca.addEventListener('input', () => this.filtrarTalentos());
        }

        const abaListarTalentos = document.getElementById('abaListarTalentos');
        if (abaListarTalentos) {
            abaListarTalentos.addEventListener('click', () => this.abrirAbaListarTalentos());
        }

        const abaCriarTalento = document.getElementById('abaCriarTalento');
        if (abaCriarTalento) {
            abaCriarTalento.addEventListener('click', () => this.abrirAbaCriarTalento());
        }

        const btnSalvarTalentoCustomizado = document.getElementById('btnSalvarTalentoCustomizado');
        if (btnSalvarTalentoCustomizado) {
            btnSalvarTalentoCustomizado.addEventListener('click', () => this.salvarTalentoCustomizado());
        }
    }

    // ─────────────────────────────────────────────────────────
    // ✅ NOVO: SINCRONIZAÇÃO COM ARENA
    // ─────────────────────────────────────────────────────────

    /**
     * ✅ NOVO: Configura escuta do BroadcastChannel
     * SRP: apenas setup do canal — processamento delegado a _processarEventoMagia()
     */
    _configurarCanalSync() {
        try {
            this._canal = new BroadcastChannel('magias-rpg');
            this._canal.onmessage = (event) => {
                if (event.data?.tipo === 'magia-usada') {
                    this._processarEventoMagia(event.data);
                }
                if (event.data?.tipo === 'magia-preparada-atualizada' && event.data?.resetSlots) {
                    this._processarDescansoLongoMagias(event.data);
                }
            };
        } catch (err) {
            console.warn('⚠️ BroadcastChannel indisponível:', err.message);
        }
    }

    /**
     * ✅ NOVO: Processa evento de magia lançada na arena
     * Atualiza o painel de slots (fichaMagiasGrid) em tempo real
     * SRP: apenas roteamento — atualização de UI delegada a métodos específicos
     * @param {{ combatenteId, magiaId, nivel, usada, disponiveis, total }} payload
     */
    _processarEventoMagia(payload) {
        // Ignora eventos de outros combatentes
        if (!this.combatente || this.combatente.id !== payload.combatenteId) {
            return;
        }


        // 1. Atualiza painel de slots na ficha
        this._atualizarPainelSlotsFicha(payload.nivel, payload.disponiveis, payload.total);

        // 2. Pulsa o slot para dar feedback visual
        this._pulsarSlot(payload.nivel);

        // 3. Atualiza painel de slots no grimório (se estiver aberto)
        if (window._grimorioController) {
            this._atualizarPainelSlotsGrimorio(payload.nivel, payload.disponiveis, payload.total);
        }
    }

    _processarDescansoLongoMagias(payload) {
        if (!this.combatente || this.combatente.id !== payload.combatenteId) {
            return;
        }

        if (Array.isArray(this.combatente.magias_slots)) {
            this.combatente.magias_slots = this.combatente.magias_slots.map((slot) => ({
                ...slot,
                usados: 0,
            }));
        }

        this.renderizarSlotsDeMapia();
    }

    /**
     * ✅ NOVO: Atualiza o painel de slots na ficha (fichaMagiasGrid)
     * SRP: apenas DOM da ficha — sem lógica de negócio
     * @param {number} nivel
     * @param {number} disponiveis
     * @param {number} total
     */
    _atualizarPainelSlotsFicha(nivel, disponiveis, total) {
        const grid = document.getElementById('fichaMagiasGrid');
        if (!grid) return;

        // Encontra a linha do slot por nível
        const linhas = grid.querySelectorAll('.ficha-slot-linha');
        let slotLinha = null;

        for (const linha of linhas) {
            const nivelSpan = linha.querySelector('.ficha-slot-nivel');
            if (!nivelSpan) continue;

            const labelNivel = nivel === 0 ? 'Truques' : `${nivel}° Nível`;
            if (nivelSpan.textContent.trim() === labelNivel) {
                slotLinha = linha;
                break;
            }
        }

        if (!slotLinha) return; // Slot não existe na ficha

        // Atualiza contagem
        const contagemEl = slotLinha.querySelector('.ficha-slot-contagem');
        if (contagemEl) {
            contagemEl.textContent = `${disponiveis}/${total}`;
        }

        // Atualiza barra de progresso
        const fill = slotLinha.querySelector('.ficha-slot-barra-fill');
        if (fill) {
            const pct = total > 0 ? (disponiveis / total) * 100 : 0;
            fill.style.width = `${pct}%`;

            // Cor baseada na disponibilidade
            let cor = '#4ade80'; // Verde
            if (pct <= 50) cor = '#facc15'; // Amarelo
            if (pct <= 25) cor = '#f87171'; // Vermelho
            fill.style.background = cor;
        }

    }

    /**
     * ✅ NOVO: Atualiza painel de slots no grimório (se aberto)
     * SRP: apenas integração com GrimorioController
     * @param {number} nivel
     * @param {number} disponiveis
     * @param {number} total
     */
    _atualizarPainelSlotsGrimorio(nivel, disponiveis, total) {
        try {
            const gc = window._grimorioController;
            if (!gc || !gc.slotsDisponiveis) return;

            if (gc.slotsDisponiveis[nivel]) {
                gc.slotsDisponiveis[nivel].total = total;
                gc.slotsDisponiveis[nivel].usadas = Math.max(0, total - disponiveis);
                gc.slotsDisponiveis[nivel].disponivel = Math.max(
                    gc.slotsDisponiveis[nivel].total - gc.slotsDisponiveis[nivel].preparadas,
                    0
                );
                gc._renderizarPainelSlots();
            }
        } catch (err) {
            console.warn('⚠️ Erro ao sincronizar grimório:', err.message);
        }
    }

    /**
     * ✅ NOVO: Pulsa visualmente o slot que foi alterado
     * SRP: apenas feedback visual — sem lógica de estado
     * @param {number} nivel
     */
    _pulsarSlot(nivel) {
        const grid = document.getElementById('fichaMagiasGrid');
        if (!grid) return;

        const linhas = grid.querySelectorAll('.ficha-slot-linha');
        for (const linha of linhas) {
            const nivelSpan = linha.querySelector('.ficha-slot-nivel');
            if (!nivelSpan) continue;

            const labelNivel = nivel === 0 ? 'Truques' : `${nivel}° Nível`;
            if (nivelSpan.textContent.trim() === labelNivel) {
                // Força reflow para reiniciar animação
                linha.classList.remove('ficha-slot-pulse');
                void linha.offsetWidth;
                linha.classList.add('ficha-slot-pulse');

                // Remove classe após animação
                setTimeout(() => {
                    linha.classList.remove('ficha-slot-pulse');
                }, 600);
                break;
            }
        }
    }

    // ─────────────────────────────────────────────────────────
    // IDENTIDADE
    // ─────────────────────────────────────────────────────────

    renderizarIdentidade() {
        const nomeHeader  = document.getElementById('fichaHeaderNome');
        const raca        = document.getElementById('fichaRaca');
        const classe      = document.getElementById('fichaClasse');
        const tipo        = document.getElementById('fichaTipo');
        const nivel       = document.getElementById('fichaNivel');
        const alinhamento = document.getElementById('fichaAlinhamento');
        const divindade   = document.getElementById('fichaDivindade');
        const campanha    = document.getElementById('fichaCampanha');
        const dominios    = document.getElementById('fichaDominios');
        const placeholder = document.getElementById('fichaFotoPlaceholder');
        const foto        = document.getElementById('fichaFoto');

        if (nomeHeader) nomeHeader.textContent = this.combatente.nome;
        if (raca)   raca.textContent   = this._normalizarNomeRacaParaExibicao(this.combatente.raca) || '—';
        if (classe) classe.textContent = this.combatente.classe || '—';
        if (tipo) {
            const tipoVal = this.combatente.tipo || 'jogador';
            tipo.textContent = tipoVal;
            // Remover classes antigas e aplicar classe específica do tipo
            tipo.classList.remove('ficha-tag-jogador', 'ficha-tag-monstro', 'ficha-tag-npc');
            tipo.classList.add(`ficha-tag-${tipoVal}`);
        }
        if (nivel)  nivel.textContent  = this.combatente.nivel  || 1;
        if (alinhamento) alinhamento.textContent = `Alinhamento: ${this.combatente.alinhamento || '—'}`;
        if (divindade) divindade.textContent = `Divindade: ${this._formatarDivindadeExibicao(this.combatente.divindade)}`;
        if (campanha) campanha.textContent = `Campanha: ${this.combatente.campanha_nome || '—'}`;
        if (dominios) {
            if (this._ehClasseClerigo()) {
                dominios.textContent = `Domínios: ${this._formatarDominios(this.combatente.dominios)}`;
            } else {
                dominios.textContent = 'Domínios: —';
            }
        }

        this._atualizarUIPerfilDominios();

        if (this.combatente.foto_url) {
            if (foto) {
                foto.src = this.combatente.foto_url;
                foto.classList.add('carregada');
            }
            if (placeholder) placeholder.style.display = 'none';
        } else {
            const emojiMap = { jogador: '🧙', npc: '🤝', monstro: '👹' };
            if (placeholder) placeholder.textContent = emojiMap[this.combatente.tipo] || '⚔️';
        }

    }

    _formatarDominios(valor) {
        const texto = String(valor || '').trim();
        return texto || '—';
    }

    _normalizarClasse(valor) {
        return String(valor || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .trim()
            .toUpperCase();
    }

    _ehClasseClerigo(classe = this.combatente?.classe) {
        return this._normalizarClasse(classe) === 'CLERIGO';
    }

    /**
     * Normaliza um nome de domínio bruto (vindo do banco) para a forma canônica
     * em `this.dominiosPermitidos`, usando comparação sem acento/maiúsculas.
     * Retorna o valor original se não encontrar correspondência.
     * @param {string} raw
     * @returns {string}
     */
    _canonicalizarDominio(raw) {
        if (!raw) return '';
        const chave = String(raw).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase().trim();
        const mapa = new Map(
            this.dominiosPermitidos.map(d => [
                d.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase(),
                d,
            ])
        );
        return mapa.get(chave) || raw;
    }

    _formatarPreRequisitos(valor) {
        const raw = String(valor ?? '').trim();
        if (!raw || raw.toLowerCase() === 'none') {
            return 'N/A';
        }
        return raw;
    }

    _atualizarUIPerfilDominios() {
        const clerigo = this._ehClasseClerigo();
        const tagDominios = document.getElementById('fichaDominios');
        const grupoDominios = document.getElementById('grupoPerfilDominios');
        const btnPerfil = document.getElementById('btnEditarPerfilMagico');

        if (tagDominios) tagDominios.style.display = clerigo ? '' : 'none';
        if (grupoDominios) grupoDominios.style.display = clerigo ? '' : 'none';
        if (btnPerfil) {
            btnPerfil.textContent = clerigo
                ? 'Editar alinhamento, divindade e domínios'
                : 'Editar alinhamento e divindade';
        }
    }

    _getAuthHeader() {
        if (window.AuthService && typeof window.AuthService.getAuthHeader === 'function') {
            return window.AuthService.getAuthHeader();
        }
        return {};
    }

    async _carregarDominiosPermitidos() {
        try {
            const response = await fetch(getApiUrl('/magias/dominios'), {
                headers: this._getAuthHeader(),
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const dominios = await response.json();
            if (Array.isArray(dominios) && dominios.length > 0) {
                this.dominiosPermitidos = dominios
                    .map((dominio) => String(dominio).trim())
                    .filter(Boolean);
            }
        } catch (error) {
            console.warn('⚠️ Não foi possível carregar domínios do backend para a ficha:', error);
            this.dominiosPermitidos = [...DOMINIOS_PERMITIDOS_FALLBACK];
        }

        this._renderizarListaDominiosPerfil();
    }

    async _carregarDivindadesSugeridas() {
        try {
            const response = await fetch(getApiUrl('/magias/divindades/catalogo'), {
                headers: this._getAuthHeader(),
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const catalogo = await response.json();
            if (Array.isArray(catalogo) && catalogo.length > 0) {
                this.divindadesCatalogo = catalogo
                    .map((item) => ({
                        nome: String(item?.nome || '').trim(),
                        titulo: String(item?.titulo || '').trim(),
                        label: String(item?.label || '').trim() || `${String(item?.nome || '').trim()}, ${String(item?.titulo || '').trim()}`,
                        tendencia: String(item?.tendencia || '').trim(),
                        dominios: Array.isArray(item?.dominios)
                            ? item.dominios.map((d) => String(d).trim()).filter(Boolean)
                            : [],
                        descricao: String(item?.descricao || '').trim(),
                    }))
                    .filter((item) => item.nome);
                this.fonteDivindades = 'catalogo';
            }
        } catch (error) {
            console.warn('⚠️ Não foi possível carregar o catálogo de divindades do backend para a ficha:', error);
            this.divindadesCatalogo = DIVINDADES_CATALOGO_FALLBACK.map((item) => ({ ...item }));
            this.fonteDivindades = 'fallback';
        }

        this._renderizarListaDivindadesPerfil();
        this._atualizarHintDivindadesPerfil();
    }

    /**
     * Localiza uma divindade no catálogo por nome ou label (case/acento-insensitive).
     * @param {string} valor
     * @returns {object|null}
     */
    _buscarDivindadePorNome(valor) {
        if (!valor) return null;
        const chave = String(valor).normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().toLowerCase();
        if (!chave) return null;
        const match = (this.divindadesCatalogo || []).find((item) => {
            const chaveNome = String(item.nome || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().toLowerCase();
            const chaveLabel = String(item.label || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().toLowerCase();
            return chaveNome === chave || chaveLabel === chave;
        });
        return match || null;
    }

    /**
     * Formata a divindade para exibição, preferindo "Nome, Título" quando conhecida.
     * @param {string} valor
     * @returns {string}
     */
    _formatarDivindadeExibicao(valor) {
        const texto = String(valor || '').trim();
        if (!texto) return '—';
        const encontrada = this._buscarDivindadePorNome(texto);
        return encontrada ? encontrada.label : texto;
    }

    // ─────────────────────────────────────────────────────────
    // Helpers de alinhamento (regra "um passo" D&D 3.5)
    // Mantem paridade com backend/app/core/divindades_catalogo.py
    // ─────────────────────────────────────────────────────────

    _normalizarTexto(valor) {
        return String(valor || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().toLowerCase();
    }

    /**
     * Converte uma tendência ("Leal e Bom", "Caótico e Mal", "Neutro", ...) em
     * [eixoOrdem, eixoMoral] com valores 1 / 0 / -1. Retorna null se indefinida.
     * Trata "Mal" e "Mau" como sinônimos.
     */
    _parseAlinhamento(valor) {
        const chave = this._normalizarTexto(valor);
        if (!chave) return null;
        if (chave === 'neutro' || chave === 'verdadeiro neutro' || chave === 'neutro neutro') {
            return [0, 0];
        }
        let ordem = 0;
        let moral = 0;
        if (chave.includes('leal')) ordem = 1;
        else if (chave.includes('caotico')) ordem = -1;
        if (chave.includes('bom') || chave.includes('bem')) moral = 1;
        else if (chave.includes('mau') || chave.includes('mal')) moral = -1;
        if (ordem === 0 && moral === 0 && !chave.includes('neutro')) return null;
        return [ordem, moral];
    }

    /** True se a divindade é compatível com o alinhamento (1-step rule). */
    _alinhamentoCompativelComDivindade(tendencia, alinhamento) {
        const a = this._parseAlinhamento(tendencia);
        const b = this._parseAlinhamento(alinhamento);
        if (!a || !b) return true;
        return Math.abs(a[0] - b[0]) <= 1 && Math.abs(a[1] - b[1]) <= 1;
    }

    /**
     * Conjunto de chaves canônicas (sem acento, minúsculas) dos domínios de
     * alinhamento proibidos pelo alinhamento do personagem (Bem/Mal/Ordem/Caos).
     */
    _chavesDominiosProibidosPorAlinhamento(alinhamento) {
        const parsed = this._parseAlinhamento(alinhamento);
        if (!parsed) return new Set();
        const [ordem, moral] = parsed;
        const proibidos = new Set();
        // Eixo moral: Bem exige não-Mau; Mal exige não-Bom.
        if (moral > 0) proibidos.add('mal');
        if (moral < 0) proibidos.add('bem');
        // Eixo ordem: Ordem exige não-Caótico; Caos exige não-Leal.
        if (ordem > 0) proibidos.add('caos');
        if (ordem < 0) proibidos.add('ordem');
        return proibidos;
    }

    /**
     * Lê o alinhamento efetivamente em edição no modal (se aberto) ou o
     * persistido no combatente como fallback.
     */
    _lerAlinhamentoEmEdicao() {
        const input = document.getElementById('inputPerfilAlinhamento');
        if (input && typeof input.value === 'string' && input.value.trim()) {
            return input.value.trim();
        }
        return String(this.combatente?.alinhamento || '').trim();
    }

    /**
     * Lê a divindade efetivamente em edição no modal (se aberto) ou a
     * persistida no combatente como fallback.
     */
    _lerDivindadeEmEdicao() {
        const select = document.getElementById('selectPerfilDivindade');
        if (select && typeof select.value === 'string' && select.value.trim()) {
            return select.value.trim();
        }
        return String(this.combatente?.divindade || '').trim();
    }

    /**
     * Calcula a lista de domínios disponíveis para o <select> considerando:
     *   1. Domínios permitidos globalmente (this.dominiosPermitidos).
     *   2. Se houver divindade catalogada selecionada → interseção com os
     *      domínios dela (nomes canônicos do Livro do Jogador).
     *   3. Remove domínios alinhamentais proibidos pelo alinhamento do
     *      personagem (ex.: "Mal" e "Caos" para um clérigo Leal e Bom).
     */
    _computarDominiosDisponiveis(alinhamento, divindade) {
        const base = Array.isArray(this.dominiosPermitidos)
            ? this.dominiosPermitidos.slice()
            : [];
        let candidatos = base;

        const divindadeInfo = this._buscarDivindadePorNome(divindade);
        if (divindadeInfo && Array.isArray(divindadeInfo.dominios) && divindadeInfo.dominios.length) {
            const chavesDoDeus = new Set(divindadeInfo.dominios.map((d) => this._normalizarTexto(d)));
            candidatos = base.filter((dominio) => chavesDoDeus.has(this._normalizarTexto(dominio)));
        }

        const proibidos = this._chavesDominiosProibidosPorAlinhamento(alinhamento);
        if (proibidos.size > 0) {
            candidatos = candidatos.filter((dominio) => !proibidos.has(this._normalizarTexto(dominio)));
        }
        return candidatos;
    }

    _renderizarListaDominiosPerfil() {
        const selectDominio1 = document.getElementById('selectPerfilDominio1');
        const selectDominio2 = document.getElementById('selectPerfilDominio2');
        const hint = document.getElementById('hintPerfilDominios');
        const clerigo = this._ehClasseClerigo();

        this._atualizarUIPerfilDominios();

        if (!clerigo) {
            if (selectDominio1) selectDominio1.innerHTML = '<option value="">Selecione o primeiro domínio</option>';
            if (selectDominio2) selectDominio2.innerHTML = '<option value="">Selecione o segundo domínio</option>';
            if (hint) hint.textContent = 'Disponível apenas para personagens da classe Clérigo.';
            return;
        }

        const alinhamento = this._lerAlinhamentoEmEdicao();
        const divindade = this._lerDivindadeEmEdicao();
        const divindadeInfo = this._buscarDivindadePorNome(divindade);
        const disponiveis = this._computarDominiosDisponiveis(alinhamento, divindade);

        const opcoes = disponiveis
            .map((dominio) => `<option value="${escapeHtml(dominio)}">${escapeHtml(dominio)}</option>`)
            .join('');

        if (selectDominio1) {
            const valorAtual = selectDominio1.value;
            selectDominio1.innerHTML = `<option value="">Selecione o primeiro domínio</option>${opcoes}`;
            if (valorAtual && disponiveis.some((d) => this._normalizarTexto(d) === this._normalizarTexto(valorAtual))) {
                selectDominio1.value = valorAtual;
            } else {
                selectDominio1.value = '';
            }
        }
        if (selectDominio2) {
            const valorAtual = selectDominio2.value;
            selectDominio2.innerHTML = `<option value="">Selecione o segundo domínio</option>${opcoes}`;
            if (valorAtual && disponiveis.some((d) => this._normalizarTexto(d) === this._normalizarTexto(valorAtual))) {
                selectDominio2.value = valorAtual;
            } else {
                selectDominio2.value = '';
            }
        }

        if (hint) {
            if (!disponiveis.length) {
                hint.textContent = divindadeInfo
                    ? `Nenhum domínio de "${divindadeInfo.label}" é compatível com o alinhamento "${alinhamento || '—'}".`
                    : 'Nenhum domínio disponível para o alinhamento atual.';
            } else if (divindadeInfo) {
                hint.textContent = `Permitidos por ${divindadeInfo.label}`
                    + (alinhamento ? ` e alinhamento "${alinhamento}"` : '')
                    + `: ${disponiveis.join(', ')}. Selecione dois domínios diferentes.`;
            } else if (alinhamento) {
                hint.textContent = `Permitidos para o alinhamento "${alinhamento}": ${disponiveis.join(', ')}.`;
            } else {
                hint.textContent = `Permitidos: ${disponiveis.join(', ')}. Selecione dois domínios diferentes.`;
            }
        }
    }

    _renderizarListaDivindadesPerfil() {
        const select = document.getElementById('selectPerfilDivindade');
        if (!select) return;

        const alinhamento = this._lerAlinhamentoEmEdicao();
        const valorSelectAtual = (select.value && select.value.trim()) || '';
        const valorCombatente = String(this.combatente?.divindade || '').trim();
        const valorAtual = valorSelectAtual || valorCombatente;
        const existente = this._buscarDivindadePorNome(valorAtual);

        const catalogoFiltrado = (this.divindadesCatalogo || []).filter((item) =>
            this._alinhamentoCompativelComDivindade(item.tendencia, alinhamento)
        );

        const opcoes = [];
        opcoes.push('<option value="">Nenhuma / Não aplicável</option>');

        // Preserva valor legado/personalizado fora do catálogo
        if (valorAtual && !existente) {
            opcoes.push(
                `<option value="${escapeHtml(valorAtual)}">${escapeHtml(valorAtual)} (personalizada)</option>`
            );
        }

        // Preserva divindade catalogada atual mesmo quando incompatível com o
        // alinhamento escolhido — marca como "(fora do alinhamento)" para o
        // usuário saber que precisa trocar uma das duas coisas antes de salvar.
        if (existente && !catalogoFiltrado.some((item) => item.nome === existente.nome)) {
            opcoes.push(
                `<option value="${escapeHtml(existente.nome)}">${escapeHtml(existente.label)} (fora do alinhamento)</option>`
            );
        }

        catalogoFiltrado.forEach((item) => {
            opcoes.push(
                `<option value="${escapeHtml(item.nome)}">${escapeHtml(item.label)}</option>`
            );
        });

        select.innerHTML = opcoes.join('');
        select.value = existente ? existente.nome : valorAtual;
    }

    _atualizarHintDivindadesPerfil() {
        const hint = document.getElementById('hintPerfilDivindade');
        if (!hint) return;

        const total = Array.isArray(this.divindadesCatalogo) ? this.divindadesCatalogo.length : 0;
        const veioDoCatalogo = this.fonteDivindades === 'catalogo';

        if (total === 0) {
            hint.textContent = 'Nenhuma divindade disponível no momento.';
            hint.classList.toggle('is-fallback', true);
            return;
        }

        const alinhamento = this._lerAlinhamentoEmEdicao();
        const compativeis = alinhamento
            ? (this.divindadesCatalogo || []).filter((item) =>
                this._alinhamentoCompativelComDivindade(item.tendencia, alinhamento))
            : this.divindadesCatalogo;
        const quantidade = compativeis.length;

        let textoBase;
        if (alinhamento) {
            textoBase = quantidade
                ? `${quantidade} de ${total} divindades compatíveis com o alinhamento "${alinhamento}" (regra do um passo).`
                : `Nenhuma divindade do catálogo é compatível com "${alinhamento}".`;
        } else {
            textoBase = veioDoCatalogo
                ? `${total} divindades carregadas do catálogo (Tabela 3-7).`
                : `${total} divindades em cache local (catálogo offline no momento).`;
        }

        hint.textContent = textoBase;
        hint.classList.toggle('is-fallback', !veioDoCatalogo);
    }

    /**
     * ✅ NOVO: Helper centralizado para leitura do perfil divino/moral
     * SRP: garante mapeamento consistente de divindade, alinhamento, domínios
     * Evita leitura direta e duplicada em vários pontos do controller
     * @returns {{ alinhamento: string, divindade: string, dominio1: string, dominio2: string }}
     */
    _lerPerfilDivino() {
        const alinhamento = String(this.combatente?.alinhamento || '').trim();
        const divindade = String(this.combatente?.divindade || '').trim();
        
        const dominioParts = String(this.combatente?.dominios || '')
            .split(',')
            .map(item => item.trim())
            .filter(Boolean);
        
        const dominio1 = dominioParts[0] || '';
        const dominio2 = dominioParts[1] || '';
        
        return { alinhamento, divindade, dominio1, dominio2 };
    }

    abrirModalPerfilMagico() {
        const modal = document.getElementById('modalPerfilMagico');
        const inputAlinhamento = document.getElementById('inputPerfilAlinhamento');
        const selectDivindade = document.getElementById('selectPerfilDivindade');
        const selectDominio1 = document.getElementById('selectPerfilDominio1');
        const selectDominio2 = document.getElementById('selectPerfilDominio2');
        const clerigo = this._ehClasseClerigo();
        if (!modal || !this.combatente) return;

        // Lazy load: abre imediatamente com valores fallback/cache, atualiza dropdowns em background
        if (!this._dadosDivinosCarregados) {
            this._dadosDivinosCarregados = true;
            Promise.all([
                this._carregarDivindadesSugeridas(),
                this._carregarDominiosPermitidos(),
            ]).catch(() => { /* fallback já está no estado */ });
        }

        // ✅ Usar helper centralizado para ler perfil divino
        const { alinhamento, divindade, dominio1, dominio2 } = this._lerPerfilDivino();

        // Preenche o alinhamento ANTES do render dos selects em cascata,
        // para que o filtro já considere o alinhamento atual do personagem.
        if (inputAlinhamento) inputAlinhamento.value = alinhamento;

        this._renderizarListaDivindadesPerfil();
        if (selectDivindade) {
            const encontrada = this._buscarDivindadePorNome(divindade);
            selectDivindade.value = encontrada ? encontrada.nome : divindade;
        }
        this._atualizarHintDivindadesPerfil();

        this._renderizarListaDominiosPerfil();
        if (selectDominio1) selectDominio1.value = clerigo ? this._canonicalizarDominio(dominio1) : '';
        if (selectDominio2) selectDominio2.value = clerigo ? this._canonicalizarDominio(dominio2) : '';

        this._ligarListenersCascataPerfilMagico();
        modal.style.display = 'flex';
    }

    /**
     * Registra (idempotentemente) os listeners que propagam as mudanças de
     * alinhamento/divindade para os outros selects:
     *   alinhamento → filtra divindades e domínios
     *   divindade   → filtra domínios
     */
    _ligarListenersCascataPerfilMagico() {
        const inputAlinhamento = document.getElementById('inputPerfilAlinhamento');
        const selectDivindade = document.getElementById('selectPerfilDivindade');

        if (inputAlinhamento && !inputAlinhamento.dataset.cascataLigada) {
            inputAlinhamento.addEventListener('change', () => {
                this._renderizarListaDivindadesPerfil();
                this._atualizarHintDivindadesPerfil();
                this._renderizarListaDominiosPerfil();
            });
            inputAlinhamento.dataset.cascataLigada = '1';
        }

        if (selectDivindade && !selectDivindade.dataset.cascataLigada) {
            selectDivindade.addEventListener('change', () => {
                this._renderizarListaDominiosPerfil();
            });
            selectDivindade.dataset.cascataLigada = '1';
        }
    }

    fecharModalPerfilMagico() {
        const modal = document.getElementById('modalPerfilMagico');
        if (modal) modal.style.display = 'none';
    }

    _normalizarDominiosPerfilSelecionados(dominio1Raw, dominio2Raw) {
        if (!this._ehClasseClerigo()) return '';

        const itens = [String(dominio1Raw || '').trim(), String(dominio2Raw || '').trim()].filter(Boolean);

        if (itens.length !== 2) {
            throw new Error('Clérigo deve escolher exatamente dois domínios.');
        }

        const mapa = new Map(
            this.dominiosPermitidos.map((dominio) => [
                dominio.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase(),
                dominio,
            ]),
        );

        const vistos = new Set();
        const normalizados = [];
        const invalidos = [];

        itens.forEach((item) => {
            const chave = item.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase();
            const canonico = mapa.get(chave);
            if (!canonico) {
                invalidos.push(item);
                return;
            }
            if (vistos.has(chave)) return;
            vistos.add(chave);
            normalizados.push(canonico);
        });

        if (invalidos.length) {
            throw new Error(`Domínio inválido: ${invalidos.join(', ')}.`);
        }

        if (normalizados.length !== 2) {
            throw new Error('Clérigo deve escolher exatamente dois domínios.');
        }

        if (normalizados[0] === normalizados[1]) {
            throw new Error('Selecione dois domínios diferentes.');
        }

        return normalizados.join(', ');
    }

    /**
     * Valida (pre-submit) a coerência entre alinhamento, divindade e domínios.
     * A validação definitiva acontece no backend (CombatenteService), mas
     * aqui ganhamos feedback imediato para o usuário.
     *
     * @param {string} alinhamento
     * @param {string} divindade
     * @param {string} dominiosCsv
     */
    _validarPerfilMagico(alinhamento, divindade, dominiosCsv) {
        // 1. Alinhamento × divindade (regra do um passo)
        if (alinhamento && divindade) {
            const encontrada = this._buscarDivindadePorNome(divindade);
            if (encontrada && !this._alinhamentoCompativelComDivindade(encontrada.tendencia, alinhamento)) {
                throw new Error(
                    `Alinhamento "${alinhamento}" é incompatível com a divindade "${encontrada.label}" `
                    + `(tendência ${encontrada.tendencia}). A diferença em cada eixo (ordem/moral) deve ser `
                    + 'de no máximo um passo.'
                );
            }
        }

        if (!this._ehClasseClerigo()) return;
        if (!dominiosCsv) return;

        const escolhidas = dominiosCsv.split(',').map((item) => item.trim()).filter(Boolean);
        const normalizar = (s) => this._normalizarTexto(s);

        // 2. Domínios × divindade catalogada
        if (divindade) {
            const encontrada = this._buscarDivindadePorNome(divindade);
            if (encontrada) {
                const permitidas = new Set((encontrada.dominios || []).map(normalizar));
                const invalidos = escolhidas.filter((d) => !permitidas.has(normalizar(d)));
                if (invalidos.length) {
                    const permitidosTxt = (encontrada.dominios || []).join(', ');
                    throw new Error(
                        `Divindade "${encontrada.label}" não permite o(s) domínio(s): ${invalidos.join(', ')}. `
                        + `Domínios aceitos: ${permitidosTxt}.`
                    );
                }
            }
        }

        // 3. Domínios alinhamentais (Bem/Mal/Ordem/Caos) × alinhamento do clérigo
        if (alinhamento) {
            const proibidos = this._chavesDominiosProibidosPorAlinhamento(alinhamento);
            if (proibidos.size) {
                const conflitantes = escolhidas.filter((d) => proibidos.has(normalizar(d)));
                if (conflitantes.length) {
                    throw new Error(
                        `Domínio(s) ${conflitantes.join(', ')} é(são) incompatível(is) com o `
                        + `alinhamento "${alinhamento}".`
                    );
                }
            }
        }
    }

    /**
     * Alias retrocompatível: mantém a assinatura antiga usada em testes/util.
     * @deprecated use _validarPerfilMagico()
     */
    _validarDominiosContraDivindade(divindade, dominiosCsv) {
        this._validarPerfilMagico(this._lerAlinhamentoEmEdicao(), divindade, dominiosCsv);
    }

    _buildFormDataAtualizacaoCombatente(overrides = {}) {
        const formData = new FormData();
        const payload = {
            nome: this.combatente.nome || '',
            hp_maximo: this.combatente.hp_maximo ?? 1,
            iniciativa: this.combatente.iniciativa ?? 0,
            tipo: this.combatente.tipo || 'jogador',
            classe: this.combatente.classe || 'Aventureiro',
            raca: this.combatente.raca || '',
            divindade: this.combatente.divindade || '',
            alinhamento: this.combatente.alinhamento || '',
            dominios: this.combatente.dominios || '',
            pagina_referencia: this.combatente.pagina_referencia || '',
            ca: this.combatente.ca ?? 10,
            toque: this.combatente.toque ?? 10,
            surpresa: this.combatente.surpresa ?? 10,
            pc: this.combatente.pc ?? 0,
            pp: this.combatente.pp ?? 0,
            po: this.combatente.po ?? 0,
            pl: this.combatente.pl ?? 0,
            forca: this.combatente.forca ?? 10,
            destreza: this.combatente.destreza ?? 10,
            constituicao: this.combatente.constituicao ?? 10,
            inteligencia: this.combatente.inteligencia ?? 10,
            sabedoria: this.combatente.sabedoria ?? 10,
            carisma: this.combatente.carisma ?? 10,
            fortitude: this.combatente.fortitude ?? 0,
            reflexos: this.combatente.reflexos ?? 0,
            vontade: this.combatente.vontade ?? 0,
            nivel: this.combatente.nivel ?? 1,
            pontos: this.combatente.pontos ?? 0,
            idiomas_customizados: JSON.stringify(
                Array.isArray(this.combatente.idiomas_customizados)
                    ? this.combatente.idiomas_customizados
                    : [],
            ),
            ...overrides,
        };

        Object.entries(payload).forEach(([key, value]) => {
            formData.append(key, value == null ? '' : String(value));
        });
        return formData;
    }

    async salvarPerfilMagico() {
        if (!this.combatente?.id) return;

        const inputAlinhamento = document.getElementById('inputPerfilAlinhamento');
        const selectDivindade = document.getElementById('selectPerfilDivindade');
        const selectDominio1 = document.getElementById('selectPerfilDominio1');
        const selectDominio2 = document.getElementById('selectPerfilDominio2');
        const alinhamento = inputAlinhamento?.value || '';
        const divindade = (selectDivindade?.value || '').trim();

        try {
            const dominios = this._normalizarDominiosPerfilSelecionados(
                selectDominio1?.value || '',
                selectDominio2?.value || '',
            );
            this._validarPerfilMagico(alinhamento, divindade, dominios);
            const formData = this._buildFormDataAtualizacaoCombatente({ alinhamento, divindade, dominios });
            this.combatente = await this.combatenteService.atualizar(this.combatente.id, formData);

            this.renderizarIdentidade();
            this.fecharModalPerfilMagico();

            if (window._grimorioController && document.getElementById('modalGrimorio')?.classList.contains('show')) {
                await window._grimorioController._recarregarDados();
            }

            window.NotificationService?.sucesso('Perfil mágico atualizado com sucesso.');
        } catch (error) {
            console.error('❌ Erro ao salvar perfil mágico:', error);
            window.NotificationService?.erro(error.message || 'Erro ao salvar perfil mágico.');
        }
    }

    _atualizarHeaderNome() {
        const el = document.getElementById('fichaHeaderNome');
        if (el && this.combatente?.nome) {
            el.textContent = this.combatente.nome;
        }
    }

    // ─────────────────────────────────────────────────────────
    // ATRIBUTOS
    // ─────────────────────────────────────────────────────────

    renderizarAtributos() {
        const map = {
            forca:         'For',
            destreza:      'Des',
            constituicao:  'Con',
            inteligencia:  'Int',
            sabedoria:     'Sab',
            carisma:       'Car',
        };

        Object.entries(map).forEach(([attr, abrev]) => {
            const valor   = this.combatente[attr] || 10;
            const mod     = Math.floor((valor - 10) / 2);
            
            // Renderizar na coluna central
            const elValor = document.getElementById(`ficha${abrev}`);
            const elMod   = document.getElementById(`ficha${abrev}Mod`);
            if (elValor) elValor.textContent = valor;
            if (elMod)   elMod.textContent   = mod >= 0 ? `+${mod}` : `${mod}`;
            
            // Renderizar na coluna esquerda (resumo)
            const elValorResumo = document.getElementById(`ficha${abrev}Resumo`);
            const elModResumo   = document.getElementById(`ficha${abrev}ModResumo`);
            if (elValorResumo) elValorResumo.textContent = valor;
            if (elModResumo)   elModResumo.textContent   = mod >= 0 ? `+${mod}` : `${mod}`;
        });

    }

    // ─────────────────────────────────────────────────────────
    // DEFESA
    // ─────────────────────────────────────────────────────────

    renderizarDefesa() {
        const ca         = document.getElementById('fichaCa');
        const toque      = document.getElementById('fichaToque');
        const surpresa   = document.getElementById('fichaSurpresa');
        const pv         = document.getElementById('fichaPv');
        const pvFill     = document.getElementById('fichaPvFill');
        const iniciativa = document.getElementById('fichaIniciativa');
        const iniciativaBreakdown = document.getElementById('fichaIniciativaBreakdown');
        const bba        = document.getElementById('fichaBba');
        const bbaBreakdown = document.getElementById('fichaBbaBreakdown');

        const caBase = this.combatente.ca ?? 10;
        const surpresaBase = this.combatente.surpresa ?? 10;
        const bonusProtecao = Number(this.bonusCaProtecao || 0);
        if (ca) {
            ca.textContent = caBase + bonusProtecao;
            ca.title = bonusProtecao
                ? `CA base ${caBase} + bônus de proteção ${bonusProtecao}`
                : `CA base ${caBase}`;
        }
        if (toque)    toque.textContent    = this.combatente.toque    ?? 10;
        if (surpresa) {
            surpresa.textContent = surpresaBase + bonusProtecao;
            surpresa.title = bonusProtecao
                ? `Surpresa base ${surpresaBase} + bônus de proteção ${bonusProtecao}`
                : `Surpresa base ${surpresaBase}`;
        }

        if (pv) pv.textContent = `${this.combatente.hp_atual ?? 0}/${this.combatente.hp_maximo ?? 0}`;

        if (pvFill) {
            const pct = (this.combatente.hp_maximo || 0) > 0
                ? ((this.combatente.hp_atual || 0) / this.combatente.hp_maximo) * 100
                : 0;
            pvFill.style.width = `${Math.max(0, Math.min(100, pct))}%`;
        }

        if (iniciativa) {
            const ini = this.combatente.iniciativa || 0;
            iniciativa.textContent = ini >= 0 ? `+${ini}` : `${ini}`;
            if (iniciativaBreakdown) {
                const modDes = this._calcularModificador(this.combatente.destreza ?? 10);
                const bonusTalento = this._bonusIniciativaTalento();
                const bonusOutros = ini - modDes - bonusTalento;
                const partes = [`DES ${modDes >= 0 ? `+${modDes}` : modDes}`];
                if (bonusTalento !== 0) {
                    partes.push(`talento ${bonusTalento >= 0 ? `+${bonusTalento}` : bonusTalento}`);
                }
                if (bonusOutros !== 0) {
                    partes.push(`outros ${bonusOutros >= 0 ? `+${bonusOutros}` : bonusOutros}`);
                }
                iniciativaBreakdown.textContent = partes.join(' + ').replace(/\+ -/g, '- ');
            }
        }
        if (bba) {
            const bbaTexto = this._resolverBbaFicha();
            bba.textContent = bbaTexto;
            bba.title = 'BBA define ataques iterativos: a cada +5 no bônus base, você ganha um ataque adicional com -5.';
            if (bbaBreakdown) {
                const ataques = String(bbaTexto)
                    .split('/')
                    .map((p) => p.trim())
                    .filter(Boolean);
                const qtdAtaques = Math.max(1, ataques.length);
                const pluralAtaques = qtdAtaques === 1 ? 'ataque' : 'ataques';
                const classe = this.combatente.classe || '—';
                const nivel = this.combatente.nivel || 1;
                bbaBreakdown.textContent = `Classe ${classe} • Nível ${nivel} • ${qtdAtaques} ${pluralAtaques}`;
                bbaBreakdown.title = 'Ataques iterativos em D&D 3.5: +5 no BBA concede um ataque extra com penalidade de -5.';
            }
        }

    }

    _bonusIniciativaTalento() {
        const talentos = Array.isArray(this.talentosJogador) ? this.talentosJogador : [];
        for (const talento of talentos) {
            const nome = String(talento?.nome || '')
                .normalize('NFD')
                .replace(/[\u0300-\u036f]/g, '')
                .trim()
                .toUpperCase();
            if (nome === 'INICIATIVA APRIMORADA') return 4;
        }
        return 0;
    }

    _calcularModificador(valorAtributo) {
        const valor = Number(valorAtributo ?? 10);
        if (!Number.isFinite(valor)) return 0;
        return Math.floor((valor - 10) / 2);
    }

    _resolverBbaFicha() {
        const bbaApi = String(this.combatente?.bonus_base_ataque || '').trim();
        if (bbaApi) return bbaApi;
        return this._calcularBbaPorClasseNivel(
            this.combatente?.classe,
            Number(this.combatente?.nivel || 1),
        );
    }

    _calcularBbaPorClasseNivel(classe, nivel) {
        const cls = String(classe || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .trim()
            .toUpperCase();
        const nvl = Math.max(1, Math.min(20, Number.isFinite(nivel) ? nivel : 1));

        const good = new Set(['BARBARO', 'GUERREIRO', 'PALADINO', 'RANGER', 'PATRULHEIRO']);
        const medium = new Set(['BARDO', 'CLERIGO', 'DRUIDA', 'LADINO', 'MONGE']);
        const poor = new Set(['MAGO', 'FEITICEIRO']);

        let total = 0;
        if (good.has(cls)) total = nvl;
        else if (medium.has(cls)) total = Math.floor((3 * nvl) / 4);
        else if (poor.has(cls)) total = Math.floor(nvl / 2);
        else return '+0';

        const ataques = [];
        for (let atual = total; atual >= 1; atual -= 5) {
            ataques.push(`+${atual}`);
        }
        return ataques.length ? ataques.join('/') : '+0';
    }

    // ─────────────────────────────────────────────────────────
    // RESISTÊNCIAS
    // ─────────────────────────────────────────────────────────

    renderizarResistencias() {
        const fort   = document.getElementById('fichaFort');
        const reflex = document.getElementById('fichaReflex');
        const vont   = document.getElementById('fichaVont');
        const fortBreakdown = document.getElementById('fichaFortBreakdown');
        const reflexBreakdown = document.getElementById('fichaReflexBreakdown');
        const vontBreakdown = document.getElementById('fichaVontBreakdown');

        const fmt = v => v >= 0 ? `+${v}` : `${v}`;
        if (fort) {
            fort.textContent = fmt(this.combatente.fortitude || 0);
            fort.title = `Base: ${fmt(this.combatente.fortitude_base || 0)}`;
            if (fortBreakdown) {
                const modCon = Math.floor(((this.combatente.constituicao ?? 10) - 10) / 2);
                fortBreakdown.textContent = `Base ${fmt(this.combatente.fortitude_base || 0)} • CON ${fmt(modCon)}`;
            }
        }
        if (reflex) {
            reflex.textContent = fmt(this.combatente.reflexos || 0);
            reflex.title = `Base: ${fmt(this.combatente.reflexos_base || 0)}`;
            if (reflexBreakdown) {
                const modDes = Math.floor(((this.combatente.destreza ?? 10) - 10) / 2);
                reflexBreakdown.textContent = `Base ${fmt(this.combatente.reflexos_base || 0)} • DES ${fmt(modDes)}`;
            }
        }
        if (vont) {
            vont.textContent = fmt(this.combatente.vontade || 0);
            vont.title = `Base: ${fmt(this.combatente.vontade_base || 0)}`;
            if (vontBreakdown) {
                const modSab = Math.floor(((this.combatente.sabedoria ?? 10) - 10) / 2);
                vontBreakdown.textContent = `Base ${fmt(this.combatente.vontade_base || 0)} • SAB ${fmt(modSab)}`;
            }
        }

    }

    renderizarHabilidadesEspeciais() {
        const container = document.getElementById('fichaHabilidadesEspeciais');
        if (!container) return;

        // Preferência: campo enriquecido vindo do catálogo canônico.
        // Fallback: JSON/legado persistido em `habilidades_especiais`.
        const detalhadas = Array.isArray(this.combatente?.habilidades_especiais_detalhadas)
            ? this.combatente.habilidades_especiais_detalhadas
            : [];

        if (detalhadas.length) {
            container.innerHTML = detalhadas
                .map((grupo) => {
                    const itens = Array.isArray(grupo?.habilidades) ? grupo.habilidades : [];
                    if (!itens.length) return '';
                    const spans = itens
                        .map((h) => this._renderHabilidadeEnriquecida(h))
                        .join(', ');
                    return `
                        <div class="ficha-habilidade-especial-item">
                            <span class="ficha-habilidade-especial-nivel">Nível ${Number(grupo.nivel || 0)}:</span>
                            <span>${spans}</span>
                        </div>
                    `;
                })
                .join('');
            return;
        }

        const raw = String(this.combatente?.habilidades_especiais || '').trim();
        if (!raw) {
            container.innerHTML = '<span class="ficha-vazio">Nenhuma habilidade especial mapeada para classe/nível atual.</span>';
            return;
        }
        const agrupadas = this._normalizarHabilidadesEspeciais(raw);
        if (!agrupadas.length) {
            container.innerHTML = '<span class="ficha-vazio">Nenhuma habilidade especial mapeada para classe/nível atual.</span>';
            return;
        }
        container.innerHTML = agrupadas
            .map((item) => `
                <div class="ficha-habilidade-especial-item">
                    <span class="ficha-habilidade-especial-nivel">Nível ${item.nivel}:</span>
                    <span>${escapeHtml(item.habilidades.join(', '))}</span>
                </div>
            `)
            .join('');
    }

    _renderHabilidadeEnriquecida(habilidade) {
        const raw = String(habilidade?.raw || '').trim();
        const titulo = String(habilidade?.titulo || '').trim();
        const descricao = String(habilidade?.descricao || '').trim();
        const rotulo = raw || titulo;
        if (!rotulo) return '';
        if (!descricao) {
            return `<span class="ficha-habilidade-especial-chip">${escapeHtml(rotulo)}</span>`;
        }
        return `<span class="ficha-habilidade-especial-chip" data-slug="${escapeHtml(habilidade.slug || '')}" title="${escapeHtml(descricao)}">${escapeHtml(rotulo)}</span>`;
    }

    _normalizarNomeRacaParaExibicao(nomeRaca) {
        const nome = String(nomeRaca || '').trim();
        if (!nome) return '';
        const mapaSingular = {
            humanos: 'Humano',
            elfos: 'Elfo',
            anoes: 'Anão',
            'anões': 'Anão',
            halflings: 'Halfling',
            gnomos: 'Gnomo',
            meioelfos: 'Meio-elfo',
            'meio-elfos': 'Meio-elfo',
            meioorcs: 'Meio-orc',
            'meio-orcs': 'Meio-orc',
        };
        const chave = nome.toLowerCase();
        return mapaSingular[chave] || nome;
    }

    _extrairIdiomasDePassivosRaciais() {
        const passivos = Array.isArray(this.combatente?.passivos_raciais) ? this.combatente.passivos_raciais : [];
        const encontrados = [];
        passivos.forEach((item) => {
            const texto = String(item || '').trim();
            if (!texto) return;
            const match = texto.match(/^idiomas?\s*:\s*(.+)$/i);
            if (!match || !match[1]) return;
            match[1]
                .split(',')
                .map((idioma) => String(idioma || '').trim())
                .filter(Boolean)
                .forEach((idioma) => encontrados.push(idioma));
        });
        return encontrados;
    }

    _obterIdiomasConhecidos() {
        const idiomasBase = this._obterIdiomasBaseRaciais();
        const idiomasExtras = Array.isArray(this.combatente?.idiomas_customizados)
            ? this.combatente.idiomas_customizados
            : [];
        const unicos = [];
        [...idiomasBase, ...idiomasExtras]
            .forEach((idioma) => {
                const jaExiste = unicos.some((existente) => existente.localeCompare(idioma, 'pt-BR', { sensitivity: 'accent' }) === 0);
                if (!jaExiste) unicos.push(idioma);
            });
        return unicos;
    }

    _obterIdiomasBaseRaciais() {
        // A API envia `idiomas_raciais` já mesclado (catálogo + extras). Para saber o que é
        // "só racial", removemos uma ocorrência de cada item persistido em `idiomas_customizados`.
        const merged = Array.isArray(this.combatente?.idiomas_raciais)
            ? this.combatente.idiomas_raciais.map((x) => String(x || '').trim()).filter(Boolean)
            : [];
        const custom = Array.isArray(this.combatente?.idiomas_customizados)
            ? this.combatente.idiomas_customizados.map((x) => String(x || '').trim()).filter(Boolean)
            : [];
        const racialApenas = [...merged];
        for (const c of custom) {
            const idx = racialApenas.findIndex(
                (x) => x.localeCompare(c, 'pt-BR', { sensitivity: 'accent' }) === 0,
            );
            if (idx >= 0) racialApenas.splice(idx, 1);
        }
        const idiomasPassivos = this._extrairIdiomasDePassivosRaciais();
        const unicos = [];
        [...racialApenas, ...idiomasPassivos].forEach((idioma) => {
            const jaExiste = unicos.some(
                (existente) => existente.localeCompare(idioma, 'pt-BR', { sensitivity: 'accent' }) === 0,
            );
            if (!jaExiste) unicos.push(idioma);
        });
        return unicos;
    }

    renderizarIdiomas() {
        if (!Array.isArray(this.idiomasFichaDraft) || !this.idiomasFichaDraft.length) {
            this.idiomasFichaDraft = this._obterIdiomasConhecidos();
        }
        const container = document.getElementById('fichaIdiomas');
        if (!container) return;
        if (!this.idiomasFichaDraft.length) {
            container.innerHTML = '<span class="ficha-vazio">Nenhum idioma cadastrado.</span>';
            return;
        }
        container.innerHTML = this.idiomasFichaDraft
            .map((idioma) => `
                <span class="ficha-idioma-chip">
                    ${escapeHtml(idioma)}
                    <button class="ficha-idioma-remover" data-idioma-remove="${escapeHtml(idioma)}" title="Remover idioma" aria-label="Remover idioma ${escapeHtml(idioma)}">✕</button>
                </span>
            `)
            .join('');
        container.querySelectorAll('[data-idioma-remove]').forEach((btn) => {
            btn.addEventListener('click', () => this.removerIdiomaFicha(btn.getAttribute('data-idioma-remove')));
        });
    }

    async adicionarIdiomaFicha() {
        const input = document.getElementById('inputNovoIdiomaFicha');
        if (!input) return;
        const idioma = String(input.value || '').trim();
        if (!idioma) return;
        const jaExiste = this.idiomasFichaDraft.some(
            (item) => item.localeCompare(idioma, 'pt-BR', { sensitivity: 'accent' }) === 0,
        );
        if (jaExiste) {
            window.NotificationService?.info?.('Esse idioma já está na lista.');
            return;
        }
        const draftAnterior = [...this.idiomasFichaDraft];
        this.idiomasFichaDraft.push(idioma);
        input.value = '';
        this.renderizarIdiomas();
        try {
            await this._persistirIdiomasExtrasFicha();
        } catch (_err) {
            this.idiomasFichaDraft = draftAnterior;
            this.renderizarIdiomas();
        }
    }

    async removerIdiomaFicha(idioma) {
        const alvo = String(idioma || '').trim();
        if (!alvo) return;
        const draftAnterior = [...this.idiomasFichaDraft];
        this.idiomasFichaDraft = this.idiomasFichaDraft.filter(
            (item) => item.localeCompare(alvo, 'pt-BR', { sensitivity: 'accent' }) !== 0,
        );
        this.renderizarIdiomas();
        try {
            await this._persistirIdiomasExtrasFicha();
        } catch (_err) {
            this.idiomasFichaDraft = draftAnterior;
            this.renderizarIdiomas();
        }
    }

    async _persistirIdiomasExtrasFicha() {
        if (!this.combatente?.id) return;
        try {
            const idiomasBase = this._obterIdiomasBaseRaciais();
            const idiomasExtras = this.idiomasFichaDraft.filter(
                (idioma) => !idiomasBase.some((base) => base.localeCompare(idioma, 'pt-BR', { sensitivity: 'accent' }) === 0),
            );
            const formData = this._buildFormDataAtualizacaoCombatente({
                idiomas_customizados: JSON.stringify(idiomasExtras),
            });
            this.combatente = await this.combatenteService.atualizar(this.combatente.id, formData);
            this.idiomasFichaDraft = this._obterIdiomasConhecidos();
            this.renderizarIdiomas();
        } catch (error) {
            console.error('❌ Erro ao salvar idiomas da ficha:', error);
            window.NotificationService?.erro(error.message || 'Não foi possível salvar os idiomas.');
            throw error;
        }
    }

    renderizarCaracteristicasRaciais() {
        // Conteúdo racial é exibido em modal; aqui atualizamos o badge de contagem no botão.
        const countEl = document.getElementById('fichaRaciaisCount');
        const resumoEl = document.getElementById('fichaRaciaisResumo');
        if (!countEl) return;
        const total = this._coletarCaracteristicasRaciais().length;
        countEl.textContent = String(total);
        if (resumoEl) {
            resumoEl.textContent = total > 0 ? 'Clique para ver' : 'Sem dados';
        }
    }

    renderizarDinheiro() {
        const poEl = document.getElementById('fichaDinheiroPo');
        const resumoEl = document.getElementById('fichaDinheiroResumo');
        const pc = Number(this.combatente?.pc || 0);
        const pp = Number(this.combatente?.pp || 0);
        const po = Number(this.combatente?.po || 0);
        const pl = Number(this.combatente?.pl || 0);
        if (poEl) poEl.textContent = `PO ${po}`;
        if (resumoEl) resumoEl.textContent = `PC ${pc} • PP ${pp} • PL ${pl}`;
    }

    abrirModalDinheiro() {
        const modal = document.getElementById('modalDinheiro');
        if (!modal || !this.combatente) return;
        const setVal = (id, v) => {
            const el = document.getElementById(id);
            if (el) el.value = String(Math.max(0, Number(v || 0)));
        };
        setVal('inputDinheiroPC', this.combatente.pc);
        setVal('inputDinheiroPP', this.combatente.pp);
        setVal('inputDinheiroPO', this.combatente.po);
        setVal('inputDinheiroPL', this.combatente.pl);
        this._atualizarTotalDinheiroPo();
        modal.style.display = 'flex';
    }

    fecharModalDinheiro() {
        const modal = document.getElementById('modalDinheiro');
        if (modal) modal.style.display = 'none';
    }

    async salvarModalDinheiro() {
        if (!this.combatente?.id) return;
        const getVal = (id) => {
            const el = document.getElementById(id);
            return Math.max(0, Number.parseInt(el?.value ?? '0', 10) || 0);
        };
        const pc = getVal('inputDinheiroPC');
        const pp = getVal('inputDinheiroPP');
        const po = getVal('inputDinheiroPO');
        const pl = getVal('inputDinheiroPL');
        try {
            const formData = this._buildFormDataAtualizacaoCombatente({ pc, pp, po, pl });
            await this.combatenteService.atualizar(this.combatente.id, formData);
            // Recarrega do backend para garantir estado persistido (evita falso positivo visual).
            this.combatente = await this.combatenteService.obterCombatente(this.combatente.id);
            this.renderizarDinheiro();
            this.fecharModalDinheiro();
            window.NotificationService?.sucesso('Dinheiro atualizado com sucesso.');
        } catch (error) {
            console.error('❌ Erro ao salvar dinheiro:', error);
            window.NotificationService?.erro(error.message || 'Erro ao salvar dinheiro.');
        }
    }

    _atualizarTotalDinheiroPo() {
        const getVal = (id) => {
            const el = document.getElementById(id);
            return Math.max(0, Number.parseInt(el?.value ?? '0', 10) || 0);
        };
        const pc = getVal('inputDinheiroPC');
        const pp = getVal('inputDinheiroPP');
        const po = getVal('inputDinheiroPO');
        const pl = getVal('inputDinheiroPL');
        // D&D 3.5: 10 pc = 1 pp; 10 pp = 1 po; 10 po = 1 pl.
        const totalPo = po + (pp / 10) + (pc / 100) + (pl * 10);
        const totalEl = document.getElementById('modalDinheiroTotalPo');
        if (!totalEl) return;
        const txt = totalPo.toLocaleString('pt-BR', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 2,
        });
        totalEl.textContent = `Total equivalente: PO ${txt}`;
    }

    _coletarCaracteristicasRaciais() {
        const itens = [];
        if (this.combatente?.tamanho_racial) {
            itens.push(`Tamanho: ${this.combatente.tamanho_racial}`);
        }
        if (Number.isFinite(Number(this.combatente?.deslocamento_racial_metros))) {
            itens.push(`Deslocamento: ${this.combatente.deslocamento_racial_metros}m`);
        }
        const idiomas = Array.isArray(this.combatente?.idiomas_raciais) ? this.combatente.idiomas_raciais : [];
        if (idiomas.length) {
            itens.push(`Idiomas: ${idiomas.join(', ')}`);
        }
        const passivos = Array.isArray(this.combatente?.passivos_raciais) ? this.combatente.passivos_raciais : [];
        itens.push(...passivos);

        const unicos = [];
        for (const item of itens.map((x) => String(x).trim()).filter(Boolean)) {
            if (!unicos.includes(item)) unicos.push(item);
        }
        return unicos;
    }

    abrirModalCaracteristicasRaciais() {
        const modal = document.getElementById('modalCaracteristicasRaciais');
        const subtitulo = document.getElementById('modalCaracteristicasRaciaisSubtitulo');
        const conteudo = document.getElementById('modalCaracteristicasRaciaisConteudo');
        if (!modal || !conteudo) return;

        const raca = this._normalizarNomeRacaParaExibicao(this.combatente?.raca);
        if (subtitulo) {
            subtitulo.textContent = raca
                ? `Resumo da raça ${raca} (não é progressão de classe).`
                : 'Resumo da raça atual do personagem (não é progressão de classe).';
        }

        const itens = this._coletarCaracteristicasRaciais();
        if (!itens.length) {
            conteudo.innerHTML = '<span class="ficha-vazio">Nenhuma característica racial mapeada para esta raça.</span>';
        } else {
            conteudo.innerHTML = itens
                .map((item) => `<div class="ficha-habilidade-especial-item">${escapeHtml(item)}</div>`)
                .join('');
        }
        modal.style.display = 'flex';
    }

    fecharModalCaracteristicasRaciais() {
        const modal = document.getElementById('modalCaracteristicasRaciais');
        if (modal) modal.style.display = 'none';
    }

    _normalizarHabilidadesEspeciais(raw) {
        try {
            const parsed = JSON.parse(raw);
            if (Array.isArray(parsed)) {
                return parsed
                    .map((item) => ({
                        nivel: Number(item?.nivel || 0),
                        habilidades: Array.isArray(item?.habilidades)
                            ? item.habilidades.map((h) => String(h).trim()).filter(Boolean)
                            : [],
                    }))
                    .filter((item) => item.nivel > 0 && item.habilidades.length > 0)
                    .sort((a, b) => a.nivel - b.nivel);
            }
        } catch (_err) {
            // Compatibilidade com formato legado string separado por pipe.
        }
        const legacy = raw
            .split('|')
            .map((item) => item.trim())
            .filter(Boolean);
        if (!legacy.length) return [];
        return [{ nivel: Number(this.combatente?.nivel || 1), habilidades: legacy }];
    }

    // ─────────────────────────────────────────────────────────
    // ATAQUES
    // ─────────────────────────────────────────────────────────

    renderizarAtaques() {
        const lista = document.getElementById('fichaAtaquesLista');
        if (!lista) return;

        const ataques = this.combatente.ataques || [];

        if (ataques.length === 0) {
            lista.innerHTML = '<div class="ficha-ataque-vazio">Nenhum ataque cadastrado</div>';
            return;
        }

        lista.innerHTML = ataques.map(a => `
            <div class="ficha-ataque-linha">
                <span class="ficha-ataque-nome">${escapeHtml(a.nome) || '—'}</span>
                <span class="ficha-ataque-bonus">${escapeHtml(a.bonus_ataque) || '+0'}</span>
                <span class="ficha-ataque-dano">${escapeHtml(a.dano) || '—'}</span>
            </div>
        `).join('');

    }

    _abrirEditorAtaques() {
        const editor = document.getElementById('fichaAtaquesEditor');
        const listaEl = document.getElementById('fichaAtaquesEditorLista');
        if (!editor || !listaEl) return;

        listaEl.innerHTML = '';
        const ataques = this.combatente.ataques || [];
        if (ataques.length === 0) {
            this._adicionarLinhaAtaqueEditor();
        } else {
            ataques.forEach(a => this._adicionarLinhaAtaqueEditor(a));
        }
        editor.style.display = 'block';
    }

    _adicionarLinhaAtaqueEditor(ataque = {}) {
        const lista = document.getElementById('fichaAtaquesEditorLista');
        if (!lista) return;
        const div = document.createElement('div');
        div.className = 'ataque-linha';
        div.style.cssText = 'display:grid; grid-template-columns:1fr 70px 90px 120px 36px; gap:.4rem; margin-bottom:.3rem;';
        div.innerHTML = `
            <input type="text" class="ataque-nome ficha-input-ataque" placeholder="Nome" value="${escapeHtml(ataque.nome || '')}" style="padding:.3rem .4rem; border:1px solid #334155; background:#0f172a; color:#e2e8f0; border-radius:4px; font-size:.82rem;">
            <input type="text" class="ataque-bonus ficha-input-ataque" placeholder="+0" value="${escapeHtml(ataque.bonus_ataque || '+0')}" style="padding:.3rem .4rem; border:1px solid #334155; background:#0f172a; color:#e2e8f0; border-radius:4px; font-size:.82rem;">
            <input type="text" class="ataque-dano ficha-input-ataque" placeholder="1d6" value="${escapeHtml(ataque.dano || '')}" style="padding:.3rem .4rem; border:1px solid #334155; background:#0f172a; color:#e2e8f0; border-radius:4px; font-size:.82rem;">
            <input type="text" class="ataque-tipo ficha-input-ataque" placeholder="tipo" value="${escapeHtml(ataque.tipo_dano || '')}" style="padding:.3rem .4rem; border:1px solid #334155; background:#0f172a; color:#e2e8f0; border-radius:4px; font-size:.82rem;">
            <button type="button" style="background:#ef4444; color:#fff; border:none; border-radius:4px; cursor:pointer; font-size:.8rem;">✕</button>
        `;
        div.querySelector('button').addEventListener('click', () => div.remove());
        lista.appendChild(div);
    }

    _coletarAtaquesEditor() {
        return Array.from(document.querySelectorAll('#fichaAtaquesEditorLista .ataque-linha'))
            .map(l => ({
                nome: l.querySelector('.ataque-nome').value.trim(),
                bonus_ataque: l.querySelector('.ataque-bonus').value.trim() || '+0',
                dano: l.querySelector('.ataque-dano').value.trim() || '1d6',
                tipo_dano: l.querySelector('.ataque-tipo').value.trim(),
            }))
            .filter(a => a.nome);
    }

    async _salvarAtaques() {
        const combatenteId = this.combatente?.id;
        if (!combatenteId) return;
        const ataques = this._coletarAtaquesEditor();
        try {
            const res = await fetch(getApiUrl(`/combatentes/${combatenteId}/ataques`), {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${this.token}` },
                body: JSON.stringify({ ataques }),
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            this.combatente.ataques = ataques;
            this.renderizarAtaques();
            document.getElementById('fichaAtaquesEditor').style.display = 'none';
        } catch (err) {
            console.error('❌ Erro ao salvar ataques:', err);
            alert('Erro ao salvar ataques: ' + err.message);
        }
    }

    // ─────────────────────────────────────────────────────────
    // SLOTS DE MAGIA
    // ─────────────────────────────────────────────────────────

    renderizarSlotsDeMapia() {
        const grid      = document.getElementById('fichaMagiasGrid');
        const secao     = document.getElementById('secaoMagias');
        if (!grid) {
            console.warn('⚠️ #fichaMagiasGrid não encontrado no DOM');
            return;
        }

        const slots = resolveCombatenteSpellSlots(this.combatente);
        const slotsAtivos = slots.filter(s => (s.total || 0) > 0);
        const ehClerigo = normalizeClasseConjuradora(this.combatente?.classe) === 'Clérigo';

        if (this.combatente) {
            this.combatente.magias_slots = slots;
        }


        if (secao) {
            const temMagia = this.combatente.tipo === 'jogador' && isClasseConjuradora(this.combatente.classe);
            secao.style.display = temMagia ? 'flex' : 'none';
        }

        const legendaClerigo = document.getElementById('fichaMagiasLegendaClerigo');
        if (legendaClerigo) {
            const mostrarLegenda = ehClerigo && slotsAtivos.length > 0;
            legendaClerigo.style.display = mostrarLegenda ? 'block' : 'none';
            if (mostrarLegenda) legendaClerigo.removeAttribute('hidden');
            else legendaClerigo.setAttribute('hidden', '');
        }

        if (slotsAtivos.length === 0) {
            grid.innerHTML = '<div class="ficha-magia-vazio">Nenhum slot cadastrado</div>';
            return;
        }

        slotsAtivos.sort((a, b) => a.nivel - b.nivel);

        grid.innerHTML = slotsAtivos.map(slot => {
            const usados      = slot.usados || 0;
            const total       = slot.total  || 0;
            const disponiveis = total - usados;
            const pct         = total > 0 ? (disponiveis / total) * 100 : 0;
            const labelNivel  = slot.nivel === 0 ? 'Truques' : `${slot.nivel}° Nível`;

            const corBarra = pct > 50 ? '#4ade80' : pct > 25 ? '#facc15' : '#f87171';

            const linhaClerigo = ehClerigo && textoSlotsClerigoBreakdown(slot)
                ? `<p class="ficha-slot-cleric-origem">${textoSlotsClerigoBreakdown(slot)}</p>`
                : '';

            return `
                <div class="ficha-slot-linha">
                    <div class="ficha-slot-topo">
                        <span class="ficha-slot-nivel">${labelNivel}</span>
                        <span class="ficha-slot-contagem">${disponiveis}/${total}</span>
                    </div>
                    ${linhaClerigo}
                    <div class="ficha-slot-barra-wrap">
                        <div class="ficha-slot-barra-fill"
                            style="width:${pct}%; background:${corBarra}">
                        </div>
                    </div>
                </div>
            `;
        }).join('');

    }

    // ─────────────────────────────────────────────────────────
    // PERÍCIAS
    // ─────────────────────────────────────────────────────────

    async carregarRenderizarPericias(combatenteId) {
        try {
            const url = getApiUrl(`/pericias/${combatenteId}/listar`);
            const res = await fetch(url, {
                headers: {
                    'Content-Type':  'application/json',
                    'Authorization': `Bearer ${this.token}`,
                }
            });

            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data    = await res.json();
            const pericias = data.pericias || [];
            this.renderizarPericiasNaFicha(pericias);

        } catch (error) {
            console.warn('⚠️ Erro ao carregar perícias:', error);
            this.renderizarPericiasVazias();
        }
    }

    renderizarPericiasNaFicha(pericias) {
        const container = document.getElementById('fichaPericiasLista');
        if (!container) return;

        if (pericias.length === 0) {
            container.innerHTML = '<span class="ficha-vazio">Nenhuma perícia selecionada</span>';
            return;
        }

        container.innerHTML = '';

        // Catálogo mínimo com {id,nome} a partir do payload do jogador, para
        // casar os bônus raciais declarados pela raça com as perícias da ficha.
        const catalogoPericias = pericias
            .map((pj) => ({ id: pj.pericia?.id, nome: pj.pericia?.nome }))
            .filter((p) => p.id && p.nome);
        const bonusRacialPorId = resolverBonusRaciaisPorPericia(
            this.combatente,
            catalogoPericias,
        );

        pericias.forEach(pj => {
            const modAtr = modificadorPericiaPreferindoDomFicha(this.combatente, pj.pericia?.atributo);
            const bonusOutros = pj.bonus_outros || 0;
            const bonusRacial = bonusRacialPorId.get(pj.pericia?.id) || 0;
            const total = pj.graduacao + modAtr + bonusOutros + bonusRacial;
            const item  = document.createElement('div');
            item.className = 'ficha-pericia-item';
            item.title     = pj.pericia?.descricao || '';
            const racialHtml = bonusRacial
                ? `<span class="ficha-pericia-mod-valor">+${bonusRacial}</span>`
                : `<span class="ficha-pericia-mod-valor">—</span>`;
            item.innerHTML = `
                <span class="ficha-pericia-nome">${escapeHtml(pj.pericia?.nome) || '—'}</span>
                <span class="ficha-pericia-atributo">${escapeHtml(pj.pericia?.atributo) || '—'}</span>
                <div class="ficha-pericia-mods">
                    <div class="ficha-pericia-mod">
                        <span class="ficha-pericia-mod-label">Gra</span>
                        <span class="ficha-pericia-mod-valor">${pj.graduacao}</span>
                    </div>
                    <div class="ficha-pericia-mod">
                        <span class="ficha-pericia-mod-label">Atr</span>
                        <span class="ficha-pericia-mod-valor">${modAtr >= 0 ? '+' : ''}${modAtr}</span>
                    </div>
                    <div class="ficha-pericia-mod" title="Bônus racial aplicado automaticamente">
                        <span class="ficha-pericia-mod-label">Rac</span>
                        ${racialHtml}
                    </div>
                    <div class="ficha-pericia-mod">
                        <span class="ficha-pericia-mod-label">Bôn</span>
                        <span class="ficha-pericia-mod-valor">${bonusOutros >= 0 ? '+' : ''}${bonusOutros}</span>
                    </div>
                    <div class="ficha-pericia-mod">
                        <span class="ficha-pericia-mod-label">Total</span>
                        <span class="ficha-pericia-total-valor ${total >= 0 ? 'positivo' : 'negativo'}">
                            ${total >= 0 ? '+' : ''}${total}
                        </span>
                    </div>
                </div>
            `;
            container.appendChild(item);
        });

    }

    renderizarPericiasVazias() {
        const container = document.getElementById('fichaPericiasLista');
        if (container) container.innerHTML = '<span class="ficha-vazio">Nenhuma perícia selecionada</span>';
    }

    // ─────────────────────────────────────────────────────────
    // SKELETON LOADER
    // ─────────────────────────────────────────────────────────

    _mostrarSkeletonFicha() {
        // Item genérico: ícone circular + duas linhas de texto
        const itemSkeleton = (largura1 = 'w-3-4', largura2 = 'w-1-2') => `
            <div class="sk-item">
                <div class="sk-circle"></div>
                <div class="sk-item-body">
                    <div class="sk-line ${largura1}"></div>
                    <div class="sk-line ${largura2} sm"></div>
                </div>
            </div>`;

        // Linha simples (perícias)
        const linhaSkeleton = (largura1 = 'w-full', largura2 = 'w-1-3') => `
            <div class="sk-item">
                <div class="sk-item-body">
                    <div class="sk-line ${largura1}"></div>
                    <div class="sk-line ${largura2} sm"></div>
                </div>
            </div>`;

        const mapas = [
            { id: 'fichaTalentos',          html: [itemSkeleton(), itemSkeleton('w-1-2', 'w-1-3'), itemSkeleton()].join('') },
            { id: 'fichaEquipamentos',      html: [itemSkeleton(), itemSkeleton('w-3-4', 'w-1-2'), itemSkeleton('w-1-2', 'w-1-3')].join('') },
            { id: 'fichaArmadurasProtecao', html: [itemSkeleton(), itemSkeleton('w-1-2', 'w-1-3')].join('') },
            { id: 'fichaPericiasLista',     html: [linhaSkeleton(), linhaSkeleton('w-3-4', 'w-1-2'), linhaSkeleton(), linhaSkeleton('w-1-2', 'w-1-3'), linhaSkeleton()].join('') },
        ];

        mapas.forEach(({ id, html }) => {
            const el = document.getElementById(id);
            if (el) el.innerHTML = html;
        });
    }

    // ─────────────────────────────────────────────────────────
    // ERRO
    // ─────────────────────────────────────────────────────────

    mostrarErro(mensagem) {
        console.error('❌', mensagem);
        const container = document.getElementById('fichaPericiasLista');
        if (container) container.innerHTML = `<span class="ficha-vazio">❌ ${mensagem}</span>`;
    }

    async carregarRenderizarEquipamentos(combatenteId) {
        try {
            const equipamentos = await this.equipamentoService.listarEquipamentosJogador(combatenteId);
            
            this.renderizarEquipamentos(equipamentos);
        } catch (error) {
            console.error('❌ Erro ao carregar equipamentos:', error);
            this.mostrarErroEquipamentos('Erro ao carregar equipamentos');
        }
    }

    /**
     * Resumo curto na tabela da ficha (Tabela 7-5: dano M, tipo, custo).
     */
    _resumoEquipamentoInventario(eq) {
        const parts = [eq.dano_medio, eq.tipo_dano, eq.custo].filter(
            (v) => v != null && String(v).trim() !== ''
        );
        if (parts.length) {
            return parts.map((p) => escapeHtml(String(p))).join(' · ');
        }
        if (eq.descricao && String(eq.descricao).trim() !== '') {
            return escapeHtml(eq.descricao);
        }
        return '—';
    }

    /**
     * Grade de campos do catálogo (modal), alinhada às colunas da planilha — sem duplicar descricao.
     */
    _htmlSpecEquipamentoCatalogo(eq) {
        const pares = [
            ['Custo', eq.custo],
            ['Dano (P)', eq.dano_pequeno],
            ['Dano (M)', eq.dano_medio],
            ['Tipo de dano', eq.tipo_dano],
            ['Crítico', eq.critico],
            ['Alcance / incremento', eq.alcance_incremento],
            ['Peso', eq.peso],
        ].filter(([, v]) => v != null && String(v).trim() !== '');
        if (!pares.length) {
            return '<p class="talento-linha-pre equipamento-spec-vazio">—</p>';
        }

        const blocoPar = ([lbl, val]) => `
            <div class="equipamento-spec-par" role="listitem">
                <span class="equipamento-spec-lbl">${escapeHtml(lbl)}</span>
                <span class="equipamento-spec-val">${escapeHtml(String(val))}</span>
            </div>`;

        let colEsq;
        let colDir;
        if (pares.length < 4) {
            colEsq = pares;
            colDir = [];
        } else if (pares.length === 4) {
            colEsq = pares.slice(0, 2);
            colDir = pares.slice(2);
        } else {
            colEsq = pares.slice(0, 4);
            colDir = pares.slice(4);
        }

        if (!colDir.length) {
            return `<div class="equipamento-spec-grid equipamento-spec-grid--unica" role="list">${colEsq.map(blocoPar).join('')}</div>`;
        }

        return `<div class="equipamento-spec-grid equipamento-spec-grid--duas">
            <div class="equipamento-spec-col" role="list">${colEsq.map(blocoPar).join('')}</div>
            <div class="equipamento-spec-col" role="list">${colDir.map(blocoPar).join('')}</div>
        </div>`;
    }

    renderizarEquipamentos(equipamentos) {
        const lista = document.getElementById('fichaEquipamentos');
        if (!lista) return;

        if (!equipamentos || equipamentos.length === 0) {
            lista.innerHTML = '<span class="ficha-vazio">Nenhum equipamento cadastrado</span>';
            return;
        }

        lista.innerHTML = `
            <div class="ficha-equipamentos-tabela">
                <div class="ficha-equipamento-header">
                    <span>Item</span>
                    <span>Resumo</span>
                    <span>Pág.</span>
                    <span>Qtd</span>
                    <span>Ação</span>
                </div>
                <div class="ficha-equipamentos-lista-items">
                    ${equipamentos.map((eq) => {
                        const pag =
                            eq.pagina_referencia && String(eq.pagina_referencia).trim() !== ''
                                ? escapeHtml(eq.pagina_referencia)
                                : '—';
                        return `
                        <div class="ficha-equipamento-linha">
                            <span class="ficha-equipamento-nome">${escapeHtml(eq.nome)}</span>
                            <span class="ficha-equipamento-desc">${this._resumoEquipamentoInventario(eq)}</span>
                            <span class="ficha-equipamento-pag">${pag}</span>
                            <span class="ficha-equipamento-qtd">${eq.quantidade}</span>
                            <button class="btn-deletar-eq" data-eq-id="${eq.id}" data-eq-nome="${escapeHtml(eq.nome)}" title="Deletar ${escapeHtml(eq.nome)}">🗑️</button>
                        </div>`;
                    }).join('')}
                </div>
            </div>
        `;

        // Configurar eventos dos botões de deletar
        const self = this;
        lista.querySelectorAll('.btn-deletar-eq').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const eqId = e.target.dataset.eqId;
                const eqNome = e.target.dataset.eqNome;
                self.deletarEquipamento(eqId, eqNome);
            });
        });

    }

    mostrarErroEquipamentos(mensagem) {
        console.error('❌', mensagem);
        const container = document.getElementById('fichaEquipamentos');
        if (container) container.innerHTML = `<span class="ficha-vazio">❌ ${mensagem}</span>`;
    }

    async carregarRenderizarArmadurasProtecao(combatenteId) {
        try {
            const itens = await this.armaduraProtecaoService.listarItensJogador(combatenteId);
            this.renderizarArmadurasProtecao(itens);
        } catch (error) {
            console.error('❌ Erro ao carregar armaduras/itens de proteção:', error);
            this.mostrarErroArmadurasProtecao('Erro ao carregar armaduras/itens de proteção');
        }
    }

    renderizarArmadurasProtecao(itens) {
        const lista = document.getElementById('fichaArmadurasProtecao');
        if (!lista) return;

        const colecao = Array.isArray(itens) ? itens : [];
        this.bonusCaProtecao = colecao.reduce((acc, item) => acc + Number(item.bonus_ca || 0), 0);
        this.renderizarDefesa();

        if (!colecao.length) {
            lista.innerHTML = '<span class="ficha-vazio">Nenhuma armadura/item de proteção cadastrado</span>';
            return;
        }

        lista.innerHTML = `
            <div class="ficha-equipamentos-tabela">
                <div class="ficha-equipamento-header">
                    <span>Item</span>
                    <span>Tipo</span>
                    <span>Bônus CA</span>
                    <span>Det.</span>
                    <span>Ação</span>
                </div>
                <div class="ficha-equipamentos-lista-items">
                    ${colecao.map((item) => `
                        <div class="ficha-equipamento-linha">
                            <span class="ficha-equipamento-nome">${escapeHtml(item.nome)}</span>
                            <span class="ficha-equipamento-desc">${escapeHtml(item.tipo) || '—'}</span>
                            <span class="ficha-equipamento-pag">${Number(item.bonus_ca || 0) >= 0 ? '+' : ''}${Number(item.bonus_ca || 0)}</span>
                            <span class="ficha-equipamento-desc" title="DES Máx: ${escapeHtml(item.des_max || '—')} | Penalidade: ${Number(item.penalidade || 0)} | Falha Arcana: ${escapeHtml(item.falha_arcana || '—')} | Deslocamento: ${escapeHtml(item.deslocamento || '—')} | Peso: ${item.peso ?? '—'} | Propriedades: ${escapeHtml(item.propriedades_especiais || '—')}">DES ${escapeHtml(item.des_max || '—')} • PEN ${Number(item.penalidade || 0)}</span>
                            <button class="btn-deletar-eq" data-item-id="${item.id}" data-item-nome="${escapeHtml(item.nome)}" title="Remover ${escapeHtml(item.nome)}">🗑️</button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        lista.querySelectorAll('.btn-deletar-eq').forEach((btn) => {
            btn.addEventListener('click', (event) => {
                const itemId = Number(event.currentTarget.dataset.itemId);
                const itemNome = event.currentTarget.dataset.itemNome || 'Item de proteção';
                this.deletarArmaduraProtecao(itemId, itemNome);
            });
        });
    }

    mostrarErroArmadurasProtecao(mensagem) {
        const container = document.getElementById('fichaArmadurasProtecao');
        if (container) container.innerHTML = `<span class="ficha-vazio">❌ ${mensagem}</span>`;
    }

    async abrirModalArmadurasProtecao() {
        try {
            const modal = document.getElementById('modalArmadurasProtecao');
            if (!modal) return;

            const busca = document.getElementById('armadurasProtecaoBusca');
            if (busca) busca.value = '';

            this.armadurasProtecaoSkip = 0;
            this.armadurasProtecaoDisponiveis = [];
            this.armadurasProtecaoCarregados = false;

            await this._carregarMaisArmadurasProtecao();

            const filtrados = this.armaduraProtecaoService.filtrarPorBusca(
                this.armadurasProtecaoDisponiveis,
                ''
            );
            this.renderizarListaArmadurasProtecao(filtrados);

            modal.style.display = 'flex';
        } catch (error) {
            console.error('❌ Erro ao abrir modal de armaduras/itens de proteção:', error);
            window.NotificationService?.mostrarErro('❌ Erro ao carregar armaduras/itens de proteção');
        }
    }

    async _carregarMaisArmadurasProtecao() {
        try {
            const novos = await this.armaduraProtecaoService.listarItens(
                this.armadurasProtecaoSkip,
                this.armadurasProtecaoLimit
            );

            if (novos.length > 0) {
                this.armadurasProtecaoDisponiveis = [...this.armadurasProtecaoDisponiveis, ...novos];
                this.armadurasProtecaoSkip += this.armadurasProtecaoLimit;
            }

            if (novos.length < this.armadurasProtecaoLimit) {
                this.armadurasProtecaoCarregados = true;
            }
        } catch (error) {
            console.error('❌ Erro ao carregar mais itens de proteção:', error);
            throw error;
        }
    }

    fecharModalArmadurasProtecao() {
        const modal = document.getElementById('modalArmadurasProtecao');
        if (modal) modal.style.display = 'none';
    }

    renderizarListaArmadurasProtecao(itens) {
        const lista = document.getElementById('armadurasProtecaoLista');
        if (!lista) return;

        const filtroAtivo = String(document.getElementById('armadurasProtecaoBusca')?.value || '').trim();
        const mostrarMais = !this.armadurasProtecaoCarregados && !filtroAtivo;

        if (!itens || !itens.length) {
            const temItensCarregados = (this.armadurasProtecaoDisponiveis || []).length > 0;
            const msg = temItensCarregados && filtroAtivo
                ? '<p class="equipamentos-vazio">Nenhum item corresponde à busca.</p>'
                : '<p class="equipamentos-vazio">Nenhum item de proteção encontrado</p>';
            lista.innerHTML = `${msg}${
                mostrarMais
                    ? `
                <div class="talentos-paginacao talentos-paginacao--lista">
                    <button id="btnCarregarMaisArmadurasProtecao" type="button" class="btn-carregar-mais">
                        Carregar mais itens
                    </button>
                </div>`
                    : ''
            }`;
            const btnCarregarMais = lista.querySelector('#btnCarregarMaisArmadurasProtecao');
            if (btnCarregarMais) {
                btnCarregarMais.addEventListener('click', async () => {
                    try {
                        btnCarregarMais.disabled = true;
                        btnCarregarMais.textContent = 'Carregando...';
                        await this._carregarMaisArmadurasProtecao();
                        const termo = document.getElementById('armadurasProtecaoBusca')?.value || '';
                        const filtrados = this.armaduraProtecaoService.filtrarPorBusca(
                            this.armadurasProtecaoDisponiveis,
                            termo
                        );
                        this.renderizarListaArmadurasProtecao(filtrados);
                    } catch (error) {
                        console.error('❌ Erro ao carregar mais itens de proteção:', error);
                        window.NotificationService?.mostrarErro('❌ Erro ao carregar mais itens');
                        btnCarregarMais.disabled = false;
                        btnCarregarMais.textContent = 'Carregar mais itens';
                    }
                });
            }
            return;
        }

        lista.innerHTML = `${itens.map((item) => {
            const tipoTxt = String(item.tipo || '').trim();
            const bonus = `${Number(item.bonus_ca || 0) >= 0 ? '+' : ''}${Number(item.bonus_ca || 0)}`;
            const detalhes = [
                item.des_max != null && String(item.des_max).trim() !== '' ? `DES máx ${escapeHtml(item.des_max)}` : null,
                `Pen ${Number(item.penalidade || 0)}`,
                item.falha_arcana ? `Falha arc. ${escapeHtml(item.falha_arcana)}` : null,
                item.deslocamento ? `Desloc. ${escapeHtml(item.deslocamento)}` : null,
                item.peso != null && item.peso !== '' ? `Peso ${escapeHtml(String(item.peso))}` : null,
                item.propriedades_especiais ? escapeHtml(item.propriedades_especiais) : null,
            ].filter(Boolean).join(' · ');
            return `
            <article class="talento-linha">
                <div class="talento-linha-conteudo">
                    <div class="talento-linha-cabecalho">
                        <span class="talento-linha-nome">${escapeHtml(item.nome)}</span>
                        <span class="talento-linha-secao">${escapeHtml(tipoTxt || '—')}</span>
                    </div>
                    <p class="talento-linha-beneficio"><span class="talento-linha-rotulo">Bônus CA:</span> ${bonus}</p>
                    <p class="talento-linha-pre"><span class="talento-linha-rotulo">Detalhes:</span> ${detalhes || '—'}</p>
                </div>
                <button type="button" class="talento-linha-acao item-btn-primary" data-item-id="${item.id}">➕ Adicionar</button>
            </article>`;
        }).join('')}
            ${mostrarMais ? `
                <div class="talentos-paginacao talentos-paginacao--lista">
                    <button id="btnCarregarMaisArmadurasProtecao" type="button" class="btn-carregar-mais">
                        Carregar mais itens
                    </button>
                </div>` : ''}
        `;

        lista.querySelectorAll('.talento-linha-acao[data-item-id]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const itemId = Number(btn.dataset.itemId);
                if (Number.isFinite(itemId)) this.adicionarArmaduraProtecaoClic(itemId);
            });
        });

        const btnCarregarMais = lista.querySelector('#btnCarregarMaisArmadurasProtecao');
        if (btnCarregarMais) {
            btnCarregarMais.addEventListener('click', async () => {
                try {
                    btnCarregarMais.disabled = true;
                    btnCarregarMais.textContent = 'Carregando...';

                    await this._carregarMaisArmadurasProtecao();
                    const termo = document.getElementById('armadurasProtecaoBusca')?.value || '';
                    const filtrados = this.armaduraProtecaoService.filtrarPorBusca(
                        this.armadurasProtecaoDisponiveis,
                        termo
                    );
                    this.renderizarListaArmadurasProtecao(filtrados);
                } catch (error) {
                    console.error('❌ Erro ao carregar mais itens de proteção:', error);
                    window.NotificationService?.mostrarErro('❌ Erro ao carregar mais itens');
                    btnCarregarMais.disabled = false;
                    btnCarregarMais.textContent = 'Carregar mais itens';
                }
            });
        }
    }

    async filtrarArmadurasProtecao() {
        const termo = document.getElementById('armadurasProtecaoBusca')?.value || '';
        const filtroAtivo = termo.trim();

        if (filtroAtivo && !this.armadurasProtecaoCarregados) {
            try {
                while (!this.armadurasProtecaoCarregados) {
                    await this._carregarMaisArmadurasProtecao();
                }
            } catch (error) {
                console.error('❌ Erro ao carregar itens de proteção para filtro:', error);
            }
        }

        const filtrados = this.armaduraProtecaoService.filtrarPorBusca(
            this.armadurasProtecaoDisponiveis || [],
            termo
        );
        this.renderizarListaArmadurasProtecao(filtrados);
    }

    async adicionarArmaduraProtecaoClic(itemId) {
        try {
            if (!this.combatente?.id) {
                window.NotificationService?.mostrarErro('❌ ID do combatente não encontrado');
                return;
            }

            await this.armaduraProtecaoService.adicionarItem(this.combatente.id, itemId);
            await this.carregarRenderizarArmadurasProtecao(this.combatente.id);
            window.NotificationService?.mostrarSucesso('✅ Item de proteção adicionado!');
        } catch (error) {
            console.error('❌ Erro ao adicionar item de proteção:', error);
            window.NotificationService?.mostrarErro('❌ Erro ao adicionar item de proteção');
        }
    }

    async deletarArmaduraProtecao(itemId, nomeItem) {
        if (!this.combatente?.id) {
            window.NotificationService?.mostrarErro('❌ ID do combatente não encontrado');
            return;
        }

        window.ModalConfirm.mostrar({
            icone: '🛡️',
            titulo: 'Remover Armadura/Item de Proteção',
            texto: `Tem certeza que deseja remover <strong>"${nomeItem}"</strong>?`,
            textoConfirmar: '🗑️ Remover',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar: async () => {
                try {
                    await this.armaduraProtecaoService.removerItem(this.combatente.id, itemId);
                    await this.carregarRenderizarArmadurasProtecao(this.combatente.id);
                    window.NotificationService?.mostrarSucesso(`✅ ${nomeItem} removido!`);
                } catch (error) {
                    console.error('❌ Erro ao remover item de proteção:', error);
                    window.NotificationService?.mostrarErro('❌ Erro ao remover item de proteção');
                }
            },
        });
    }

    abrirAbaListarArmadurasProtecao() {
        document.getElementById('abaListarArmadurasProtecao')?.classList.add('ativa');
        document.getElementById('abaCriarArmaduraProtecao')?.classList.remove('ativa');
        document.getElementById('conteudoListarArmadurasProtecao')?.classList.add('ativo');
        document.getElementById('conteudoCriarArmaduraProtecao')?.classList.remove('ativo');
    }

    abrirAbaCriarArmaduraProtecao() {
        document.getElementById('abaCriarArmaduraProtecao')?.classList.add('ativa');
        document.getElementById('abaListarArmadurasProtecao')?.classList.remove('ativa');
        document.getElementById('conteudoCriarArmaduraProtecao')?.classList.add('ativo');
        document.getElementById('conteudoListarArmadurasProtecao')?.classList.remove('ativo');
    }

    async salvarArmaduraProtecaoCustomizada() {
        try {
            const nome = document.getElementById('criarProtecaoNome')?.value || '';
            const tipo = document.getElementById('criarProtecaoTipo')?.value || '';
            const bonusCa = Number(document.getElementById('criarProtecaoBonusCa')?.value || 0);
            const desMax = document.getElementById('criarProtecaoDesMax')?.value || '';
            const penalidade = Number(document.getElementById('criarProtecaoPenalidade')?.value || 0);
            const falhaArcana = document.getElementById('criarProtecaoFalhaArcana')?.value || '';
            const deslocamento = document.getElementById('criarProtecaoDeslocamento')?.value || '';
            const peso = document.getElementById('criarProtecaoPeso')?.value;
            const propriedadesEspeciais = document.getElementById('criarProtecaoPropriedades')?.value || '';

            if (!nome.trim() || !tipo.trim()) {
                window.NotificationService?.mostrarAviso('⚠️ Nome e tipo são obrigatórios');
                return;
            }

            const novoItem = await this.armaduraProtecaoService.criarItem({
                nome: nome.trim(),
                tipo: tipo.trim(),
                bonus_ca: Number.isFinite(bonusCa) ? bonusCa : 0,
                des_max: desMax.trim() || null,
                penalidade: Number.isFinite(penalidade) ? penalidade : 0,
                falha_arcana: falhaArcana.trim() || null,
                deslocamento: deslocamento.trim() || null,
                peso: peso !== '' ? Number(peso) : null,
                propriedades_especiais: propriedadesEspeciais.trim() || null,
                ativo: true,
            });

            await this.armaduraProtecaoService.adicionarItem(this.combatente.id, novoItem.id);
            await this.carregarRenderizarArmadurasProtecao(this.combatente.id);

            document.getElementById('formCriarArmaduraProtecao')?.reset();
            this.abrirAbaListarArmadurasProtecao();
            window.NotificationService?.mostrarSucesso(`✅ Item de proteção "${nome}" criado e adicionado!`);
        } catch (error) {
            console.error('❌ Erro ao criar item de proteção:', error);
            window.NotificationService?.mostrarErro('❌ Erro ao criar item de proteção: ' + error.message);
        }
    }

    async abrirModalEquipamentos() {
        try {
            const modal = document.getElementById('modalEquipamentos');
            if (!modal) return;

            const busca = document.getElementById('equipamentosBusca');
            if (busca) busca.value = '';

            this.equipamentosSkip = 0;
            this.equipamentosDisponiveis = [];
            this.equipamentosCarregados = false;

            await this._carregarMaisEquipamentos();

            const filtrados = this.equipamentoService.filtrarPorBusca(
                this.equipamentosDisponiveis,
                ''
            );
            this.renderizarListaEquipamentos(filtrados);

            modal.style.display = 'flex';

        } catch (error) {
            console.error('❌ Erro ao abrir modal:', error);
            if (window.NotificationService) {
                window.NotificationService.mostrarErro('❌ Erro ao carregar equipamentos');
            }
        }
    }

    async _carregarMaisEquipamentos() {
        try {
            const novos = await this.equipamentoService.listarEquipamentos(
                this.equipamentosSkip,
                this.equipamentosLimit
            );

            if (novos.length > 0) {
                this.equipamentosDisponiveis = [...this.equipamentosDisponiveis, ...novos];
                this.equipamentosSkip += this.equipamentosLimit;
            }

            if (novos.length < this.equipamentosLimit) {
                this.equipamentosCarregados = true;
            }
        } catch (error) {
            console.error('❌ Erro ao carregar mais equipamentos:', error);
            throw error;
        }
    }

    fecharModalEquipamentos() {
        const modal = document.getElementById('modalEquipamentos');
        if (modal) modal.style.display = 'none';
    }

    renderizarListaEquipamentos(equipamentos) {
        const lista = document.getElementById('equipamentosLista');
        if (!lista) return;

        const filtroAtivo = String(document.getElementById('equipamentosBusca')?.value || '').trim();
        const mostrarMais = !this.equipamentosCarregados && !filtroAtivo;

        if (!equipamentos || equipamentos.length === 0) {
            const temItensCarregados = (this.equipamentosDisponiveis || []).length > 0;
            const msg = temItensCarregados && filtroAtivo
                ? '<p class="equipamentos-vazio">Nenhum equipamento corresponde à busca.</p>'
                : '<p class="equipamentos-vazio">Nenhum equipamento encontrado</p>';
            lista.innerHTML = `${msg}${
                mostrarMais
                    ? `
                <div class="talentos-paginacao talentos-paginacao--lista">
                    <button id="btnCarregarMaisEquipamentos" type="button" class="btn-carregar-mais">
                        Carregar mais equipamentos
                    </button>
                </div>`
                    : ''
            }`;
            const btnCarregarMais = lista.querySelector('#btnCarregarMaisEquipamentos');
            if (btnCarregarMais) {
                btnCarregarMais.addEventListener('click', async () => {
                    try {
                        btnCarregarMais.disabled = true;
                        btnCarregarMais.textContent = 'Carregando...';
                        await this._carregarMaisEquipamentos();
                        const termo = document.getElementById('equipamentosBusca')?.value || '';
                        const filtrados = this.equipamentoService.filtrarPorBusca(
                            this.equipamentosDisponiveis,
                            termo
                        );
                        this.renderizarListaEquipamentos(filtrados);
                    } catch (error) {
                        console.error('❌ Erro ao carregar mais equipamentos:', error);
                        window.NotificationService?.mostrarErro('❌ Erro ao carregar mais equipamentos');
                        btnCarregarMais.disabled = false;
                        btnCarregarMais.textContent = 'Carregar mais equipamentos';
                    }
                });
            }
            return;
        }

        const mostrarExcluirCatalogo =
            typeof window !== 'undefined' && typeof window.AuthService?.isAdmin === 'function'
                ? window.AuthService.isAdmin()
                : false;

        lista.innerHTML = `${equipamentos.map((eq) => {
            const catParts = [eq.categoria, eq.subcategoria].filter(Boolean).map((s) => String(s).trim());
            const secaoTxt = catParts.length ? catParts.join(' · ') : '—';
            const pagBloco =
                eq.pagina_referencia && String(eq.pagina_referencia).trim() !== ''
                    ? `<p class="talento-linha-pre equipamento-pag-ref"><span class="talento-linha-rotulo">Referência:</span> ${escapeHtml(eq.pagina_referencia)}</p>`
                    : '';
            const btnRemoverCatalogo = mostrarExcluirCatalogo
                ? `<button type="button" class="talento-linha-acao item-btn-danger" data-equipamento-id="${eq.id}" data-acao-catalogo="remover" title="Remove este item do catálogo global para todos os jogadores">🗑️ Catálogo</button>`
                : '';
            return `
            <article class="talento-linha equipamento-catalogo-linha">
                <div class="talento-linha-conteudo">
                    <div class="talento-linha-cabecalho">
                        <span class="talento-linha-nome">${escapeHtml(eq.nome)}</span>
                        <span class="talento-linha-secao">${escapeHtml(secaoTxt)}</span>
                    </div>
                    ${this._htmlSpecEquipamentoCatalogo(eq)}
                    ${pagBloco}
                </div>
                <div class="equipamento-catalogo-acoes">
                    <button type="button" class="talento-linha-acao item-btn-primary" data-equipamento-id="${eq.id}">➕ Adicionar</button>
                    ${btnRemoverCatalogo}
                </div>
            </article>`;
        }).join('')}
            ${mostrarMais ? `
                <div class="talentos-paginacao talentos-paginacao--lista">
                    <button id="btnCarregarMaisEquipamentos" type="button" class="btn-carregar-mais">
                        Carregar mais equipamentos
                    </button>
                </div>` : ''}
        `;

        lista.querySelectorAll('.equipamento-catalogo-acoes .item-btn-primary[data-equipamento-id]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const equipamentoId = Number(btn.dataset.equipamentoId);
                if (Number.isFinite(equipamentoId)) {
                    this.adicionarEquipamentoClic(equipamentoId);
                }
            });
        });

        lista.querySelectorAll('.equipamento-catalogo-acoes .item-btn-danger[data-acao-catalogo="remover"]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const equipamentoId = Number(btn.dataset.equipamentoId);
                if (!Number.isFinite(equipamentoId)) return;
                const nome =
                    (this.equipamentosDisponiveis || []).find((e) => Number(e.id) === equipamentoId)?.nome ||
                    'Equipamento';
                this.confirmarRemocaoEquipamentoCatalogo(equipamentoId, nome);
            });
        });

        const btnCarregarMais = lista.querySelector('#btnCarregarMaisEquipamentos');
        if (btnCarregarMais) {
            btnCarregarMais.addEventListener('click', async () => {
                try {
                    btnCarregarMais.disabled = true;
                    btnCarregarMais.textContent = 'Carregando...';

                    await this._carregarMaisEquipamentos();
                    const termo = document.getElementById('equipamentosBusca')?.value || '';
                    const filtrados = this.equipamentoService.filtrarPorBusca(
                        this.equipamentosDisponiveis,
                        termo
                    );
                    this.renderizarListaEquipamentos(filtrados);
                } catch (error) {
                    console.error('❌ Erro ao carregar mais equipamentos:', error);
                    window.NotificationService?.mostrarErro('❌ Erro ao carregar mais equipamentos');
                    btnCarregarMais.disabled = false;
                    btnCarregarMais.textContent = 'Carregar mais equipamentos';
                }
            });
        }
    }

    async filtrarEquipamentos() {
        const termo = document.getElementById('equipamentosBusca')?.value || '';
        const filtroAtivo = termo.trim();

        if (filtroAtivo && !this.equipamentosCarregados) {
            try {
                while (!this.equipamentosCarregados) {
                    await this._carregarMaisEquipamentos();
                }
            } catch (error) {
                console.error('❌ Erro ao carregar equipamentos para filtro:', error);
            }
        }

        const filtrados = this.equipamentoService.filtrarPorBusca(
            this.equipamentosDisponiveis || [],
            termo
        );
        this.renderizarListaEquipamentos(filtrados);
    }

    async adicionarEquipamentoClic(equipamentoId) {
        try {
            const qntdInput = document.getElementById('equipamentosQuantidade');
            const quantidade = parseInt(qntdInput?.value || '1');

            if (!this.combatente?.id) {
                if (window.NotificationService) {
                    window.NotificationService.mostrarErro('❌ ID do combatente não encontrado');
                }
                return;
            }

            const nomeEquipamento =
                (this.equipamentosDisponiveis || []).find((e) => Number(e.id) === Number(equipamentoId))?.nome ||
                'Equipamento';

            await this.equipamentoService.adicionarEquipamento(this.combatente.id, {
                equipamento_id: equipamentoId,
                quantidade: quantidade
            });

            await this.carregarRenderizarEquipamentos(this.combatente.id);

            qntdInput.value = '1';

            if (window.NotificationService) {
                window.NotificationService.mostrarSucesso(
                    `✅ ${nomeEquipamento} adicionado ao inventário!`
                );
            }

        } catch (error) {
            console.error('❌ Erro ao adicionar equipamento:', error);
            if (window.NotificationService) {
                window.NotificationService.mostrarErro('❌ Erro ao adicionar equipamento');
            }
        }
    }

    /**
     * Admin: remove o item do catálogo global (não afeta apenas a ficha atual).
     */
    confirmarRemocaoEquipamentoCatalogo(equipamentoId, nomeEquipamento) {
        const self = this;
        const opcoes = {
            icone: '🗑️',
            titulo: 'Remover do catálogo',
            texto:
                `Isso remove <strong>"${escapeHtml(nomeEquipamento)}"</strong> do catálogo global ` +
                '(soft delete). Não é possível desfazer pela interface. Continuar?',
            textoConfirmar: 'Remover do catálogo',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar: async () => {
                try {
                    await self.equipamentoService.deletarEquipamentoDoCatalogo(equipamentoId);
                    self.equipamentosDisponiveis = (self.equipamentosDisponiveis || []).filter(
                        (e) => Number(e.id) !== Number(equipamentoId)
                    );
                    const termo = document.getElementById('equipamentosBusca')?.value || '';
                    const filtrados = self.equipamentoService.filtrarPorBusca(
                        self.equipamentosDisponiveis,
                        termo
                    );
                    self.renderizarListaEquipamentos(filtrados);
                    if (window.NotificationService) {
                        window.NotificationService.mostrarSucesso(`✅ "${nomeEquipamento}" removido do catálogo.`);
                    }
                } catch (error) {
                    console.error('❌ Erro ao remover equipamento do catálogo:', error);
                    const msg =
                        error?.message && String(error.message).trim() !== ''
                            ? error.message
                            : 'Erro ao remover do catálogo';
                    if (window.NotificationService) {
                        window.NotificationService.mostrarErro(`❌ ${msg}`);
                    }
                }
            },
        };
        window.ModalConfirm.mostrar(opcoes);
    }

    async deletarEquipamento(equipamentoId, nomeEquipamento) {
        if (!this.combatente?.id) {
            if (window.NotificationService) {
                window.NotificationService.mostrarErro('❌ ID do combatente não encontrado');
            }
            return;
        }

        const self = this;

        // Usar ModalConfirm em vez de confirm()
        const opcoes = {
            icone: '🗑️',
            titulo: 'Deletar Equipamento',
            texto: `Tem certeza que deseja deletar <strong>"${nomeEquipamento}"</strong>?`,
            textoConfirmar: '🗑️ Deletar',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar: async () => {
                try {
                    await self.equipamentoService.removerEquipamento(self.combatente.id, equipamentoId);


                    // Recarregar equipamentos
                    await self.carregarRenderizarEquipamentos(self.combatente.id);

                    // Mostrar notificação
                    if (window.NotificationService) {
                        window.NotificationService.mostrarSucesso(`✅ ${nomeEquipamento} removido!`);
                    }

                } catch (error) {
                    console.error('❌ Erro ao deletar equipamento:', error);
                    if (window.NotificationService) {
                        window.NotificationService.mostrarErro('❌ Erro ao remover equipamento');
                    }
                }
            }
        };
        
        window.ModalConfirm.mostrar(opcoes);
    }

    abrirAbaListar() {
        document.getElementById('abaListar').classList.add('ativa');
        document.getElementById('abaCriar').classList.remove('ativa');
        document.getElementById('conteudoListar').classList.add('ativo');
        document.getElementById('conteudoCriar').classList.remove('ativo');
    }

    abrirAbaCriar() {
        document.getElementById('abaCriar').classList.add('ativa');
        document.getElementById('abaListar').classList.remove('ativa');
        document.getElementById('conteudoCriar').classList.add('ativo');
        document.getElementById('conteudoListar').classList.remove('ativo');
    }

    async salvarEquipamentoCustomizado() {
        try {
            const nome = document.getElementById('criarNome')?.value || '';
            const descricao = document.getElementById('criarDescricao')?.value || '';
            const paginaRef = document.getElementById('criarPaginaRef')?.value || '';
            const quantidade = parseInt(document.getElementById('criarQuantidade')?.value || '1');

            if (!nome.trim()) {
                if (window.NotificationService) {
                    window.NotificationService.mostrarAviso('⚠️ Nome do equipamento é obrigatório');
                }
                return;
            }

            // Criar equipamento via API
            const novoEquipamento = await this.equipamentoService.criarEquipamento({
                nome: nome.trim(),
                descricao: descricao.trim(),
                pagina_referencia: paginaRef.trim(),
                ativo: true
            });


            // Adicionar ao combatente
            await this.equipamentoService.adicionarEquipamento(this.combatente.id, {
                equipamento_id: novoEquipamento.id,
                quantidade: quantidade
            });

            // Recarregar equipamentos
            await this.carregarRenderizarEquipamentos(this.combatente.id);

            // Limpar formulário
            document.getElementById('formCriarEquipamento').reset();

            // Voltar para aba de listar
            this.abrirAbaListar();

            // Notificação
            if (window.NotificationService) {
                window.NotificationService.mostrarSucesso(`✅ Equipamento "${nome}" criado e adicionado!`);
            }

        } catch (error) {
            console.error('❌ Erro ao criar equipamento:', error);
            if (window.NotificationService) {
                window.NotificationService.mostrarErro('❌ Erro ao criar equipamento: ' + error.message);
            }
        }
    }

    // ── TALENTOS ──

    async carregarRenderizarTalentos(combatenteId) {
        try {
            const talentos = await this.talentoService.listarTalentosJogador(combatenteId);
            this.talentosJogador = talentos || [];
            this.renderizarTalentos(talentos);
            this.renderizarDefesa();
        } catch (error) {
            console.error('❌ Erro ao carregar talentos:', error);
            this.mostrarErroTalentos('Erro ao carregar talentos');
        }
    }

    renderizarTalentos(talentos) {
        const lista = document.getElementById('fichaTalentos');
        if (!lista) {
            console.error('❌ Elemento fichaTalentos não encontrado');
            return;
        }

        if (!talentos || talentos.length === 0) {
            lista.innerHTML = '<span class="ficha-vazio">Nenhum talento cadastrado</span>';
            return;
        }

        // Usar layout de cards em grid como os equipamentos no modal
        lista.innerHTML = `
            <div class="ficha-talentos-grid">
                ${talentos.map(tal => `
                    <div class="ficha-talento-card">
                        <div class="ficha-talento-card-header">
                            <h4 class="ficha-talento-card-title">${tal.nome || 'N/A'}</h4>
                        </div>
                        
                        <div class="ficha-talento-card-body">
                            ${tal.descricao ? `
                                <div class="ficha-talento-card-field">
                                    <span class="ficha-talento-card-label">Benefício</span>
                                    <p class="ficha-talento-card-value">${tal.descricao}</p>
                                </div>
                            ` : ''}
                            
                            ${tal.pagina_referencia ? `
                                <div class="ficha-talento-card-field">
                                    <span class="ficha-talento-card-label">Página</span>
                                    <p class="ficha-talento-card-value">${tal.pagina_referencia}</p>
                                </div>
                            ` : ''}
                        </div>
                        
                        <div class="ficha-talento-card-footer">
                            <button class="btn-deletar-tal" data-tal-id="${tal.id}" data-tal-nome="${tal.nome || 'N/A'}" title="Deletar ${tal.nome || 'N/A'}">🗑️</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        console.log('✅ HTML dos talentos renderizado');

        // Configurar eventos dos botões de deletar
        const self = this;
        lista.querySelectorAll('.btn-deletar-tal').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const talId = e.target.dataset.talId;
                const talNome = e.target.dataset.talNome;
                self.deletarTalento(talId, talNome);
            });
        });

    }

    mostrarErroTalentos(mensagem) {
        console.error('❌', mensagem);
        const container = document.getElementById('fichaTalentos');
        if (container) container.innerHTML = `<span class="ficha-vazio">❌ ${mensagem}</span>`;
    }

    async abrirModalTalentos() {
        try {
            const modal = document.getElementById('modalTalentos');
            if (!modal) {
                if (window.NotificationService) {
                    window.NotificationService.mostrarErro('❌ Modal de talentos não encontrado');
                }
                return;
            }

            // Reset paginação
            this.talentosSkip = 0;
            this.talentosDisponiveis = [];
            this.talentosCarregados = false;

            // Carregar primeira página
            await this._carregarMaisTalentos();

            // Renderizar lista inicial
            this.renderizarListaTalentos(this.talentosDisponiveis);

            // Mostrar modal
            modal.style.display = 'flex';

        } catch (error) {
            console.error('❌ Erro ao abrir modal:', error);
            if (window.NotificationService) {
                window.NotificationService.mostrarErro('❌ Erro ao carregar talentos');
            }
        }
    }

    async _carregarMaisTalentos() {
        try {
            const novosTalentos = await this.talentoService.listarTalentos(this.talentosSkip, this.talentosLimit);
            
            if (novosTalentos.length > 0) {
                this.talentosDisponiveis = [...this.talentosDisponiveis, ...novosTalentos];
                this.talentosSkip += this.talentosLimit;
            }
            
            // Se carregou menos que o limite, significa que chegamos ao fim
            if (novosTalentos.length < this.talentosLimit) {
                this.talentosCarregados = true;
            }
            
        } catch (error) {
            console.error('❌ Erro ao carregar mais talentos:', error);
            throw error;
        }
    }

    renderizarListaTalentos(talentos) {
        const container = document.getElementById('talentosList');
        if (!container) return;

        if (!talentos || talentos.length === 0) {
            container.innerHTML = '<p class="equipamentos-vazio">Nenhum talento disponível</p>';
            return;
        }

        /* Lista em linhas (#talentosList usa .talentos-lista-linhas no HTML) */
        container.innerHTML = `
                ${talentos.map((tal) => {
                    const secaoTxt = String(tal.secao || tal.section || '').trim();
                    const preRaw = tal.prerequisitos ?? tal.prerequisites;
                    const preTxt =
                        preRaw == null || String(preRaw).trim() === ''
                            ? '—'
                            : this._formatarPreRequisitos(preRaw);
                    const nome = escapeHtml(tal.nome || tal.talento || 'N/A');
                    return `
                    <article class="talento-linha">
                        <div class="talento-linha-conteudo">
                            <div class="talento-linha-cabecalho">
                                <span class="talento-linha-nome">${nome}</span>
                                <span class="talento-linha-secao">${escapeHtml(secaoTxt || '—')}</span>
                            </div>
                            ${tal.descricao ? `
                                <p class="talento-linha-beneficio"><span class="talento-linha-rotulo">Benefício:</span> ${escapeHtml(tal.descricao)}</p>
                            ` : ''}
                            <p class="talento-linha-pre"><span class="talento-linha-rotulo">Pré-requisitos:</span> ${escapeHtml(preTxt)}</p>
                        </div>
                        <button type="button" class="talento-linha-acao item-btn-primary" data-talento-id="${tal.id}">
                            ➕ Adicionar
                        </button>
                    </article>
                `;
                }).join('')}
                
                ${!this.talentosCarregados ? `
                    <div class="talentos-paginacao talentos-paginacao--lista">
                        <button id="btnCarregarMaisTalentos" class="btn-carregar-mais">
                            Carregar Mais Talentos
                        </button>
                    </div>
                ` : ''}
        `;

        container.querySelectorAll('.talento-linha-acao').forEach((btn) => {
            btn.addEventListener('click', () => {
                const talentoId = Number(btn.dataset.talentoId);
                if (Number.isFinite(talentoId)) {
                    this.adicionarTalentoClic(talentoId);
                }
            });
        });

        // Configurar botão de carregar mais
        const btnCarregarMais = container.querySelector('#btnCarregarMaisTalentos');
        if (btnCarregarMais) {
            btnCarregarMais.addEventListener('click', async () => {
                try {
                    btnCarregarMais.disabled = true;
                    btnCarregarMais.textContent = 'Carregando...';
                    
                    await this._carregarMaisTalentos();
                    this.renderizarListaTalentos(this.talentosDisponiveis);
                    
                } catch (error) {
                    console.error('❌ Erro ao carregar mais talentos:', error);
                    if (window.NotificationService) {
                        window.NotificationService.mostrarErro('❌ Erro ao carregar mais talentos');
                    }
                    btnCarregarMais.disabled = false;
                    btnCarregarMais.textContent = 'Carregar Mais Talentos';
                }
            });
        }

    }

    async filtrarTalentos() {
        const filtro = document.getElementById('talentosBusca')?.value?.toLowerCase() || '';
        
        // Se há filtro e ainda não carregamos todos os talentos, carregar tudo primeiro
        if (filtro && !this.talentosCarregados) {
            try {
                while (!this.talentosCarregados) {
                    await this._carregarMaisTalentos();
                }
            } catch (error) {
                console.error('❌ Erro ao carregar todos os talentos para filtro:', error);
            }
        }

        if (!this.talentosDisponiveis) return;

        const filtrados = this.talentosDisponiveis.filter(tal => 
            tal.nome.toLowerCase().includes(filtro) || 
            (tal.descricao && tal.descricao.toLowerCase().includes(filtro))
        );

        this.renderizarListaTalentos(filtrados);
    }

    async adicionarTalentoClic(talentoId) {
        try {
            if (!this.combatente?.id) {
                if (window.NotificationService) {
                    window.NotificationService.mostrarErro('❌ ID do combatente não encontrado');
                }
                return;
            }

            await this.talentoService.adicionarTalento(this.combatente.id, {
                talento_id: talentoId
            });


            // Recarregar talentos
            await this.carregarRenderizarTalentos(this.combatente.id);

            // Mostrar notificação de sucesso
            if (window.NotificationService) {
                window.NotificationService.mostrarSucesso(`✅ Talento adicionado!`);
            }

        } catch (error) {
            console.error('❌ Erro ao adicionar talento:', error);
            if (window.NotificationService) {
                window.NotificationService.mostrarErro('❌ Erro ao adicionar talento');
            }
        }
    }

    async deletarTalento(talentoId, nomeTalento) {
        if (!this.combatente?.id) {
            if (window.NotificationService) {
                window.NotificationService.mostrarErro('❌ ID do combatente não encontrado');
            }
            return;
        }

        const self = this;

        // Usar ModalConfirm em vez de confirm()
        const opcoes = {
            icone: '🗑️',
            titulo: 'Deletar Talento',
            texto: `Tem certeza que deseja deletar <strong>"${nomeTalento}"</strong>?`,
            textoConfirmar: '🗑️ Deletar',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar: async () => {
                try {
                    await self.talentoService.removerTalento(self.combatente.id, talentoId);


                    // Recarregar talentos
                    await self.carregarRenderizarTalentos(self.combatente.id);

                    // Mostrar notificação
                    if (window.NotificationService) {
                        window.NotificationService.mostrarSucesso(`✅ ${nomeTalento} removido!`);
                    }

                } catch (error) {
                    console.error('❌ Erro ao deletar talento:', error);
                    if (window.NotificationService) {
                        window.NotificationService.mostrarErro('❌ Erro ao remover talento');
                    }
                }
            }
        };

        window.ModalConfirm.mostrar(opcoes);
    }

    fecharModalTalentos() {
        const modal = document.getElementById('modalTalentos');
        if (modal) modal.style.display = 'none';
    }

    abrirAbaListarTalentos() {
        const abaLista = document.getElementById('abaListarTalentos');
        const abaCriar = document.getElementById('abaCriarTalento');
        if (abaLista) abaLista.classList.add('ativa');
        if (abaCriar) abaCriar.classList.remove('ativa');
        
        const conteudoLista = document.getElementById('conteudoListarTalentos');
        const conteudoCriar = document.getElementById('conteudoCriarTalento');
        if (conteudoLista) conteudoLista.classList.add('ativo');
        if (conteudoCriar) conteudoCriar.classList.remove('ativo');
    }

    abrirAbaCriarTalento() {
        const abaLista = document.getElementById('abaListarTalentos');
        const abaCriar = document.getElementById('abaCriarTalento');
        if (abaCriar) abaCriar.classList.add('ativa');
        if (abaLista) abaLista.classList.remove('ativa');
        
        const conteudoLista = document.getElementById('conteudoListarTalentos');
        const conteudoCriar = document.getElementById('conteudoCriarTalento');
        if (conteudoCriar) conteudoCriar.classList.add('ativo');
        if (conteudoLista) conteudoLista.classList.remove('ativo');
    }

    async salvarTalentoCustomizado() {
        try {
            const nome = document.getElementById('criarNomeTalento')?.value || '';
            const descricao = document.getElementById('criarDescricaoTalento')?.value || '';
            const paginaRef = document.getElementById('criarPaginaRefTalento')?.value || '';

            if (!nome.trim()) {
                if (window.NotificationService) {
                    window.NotificationService.mostrarAviso('⚠️ Nome do talento é obrigatório');
                }
                return;
            }

            // Criar talento via API
            const novoTalento = await this.talentoService.criarTalento({
                nome: nome.trim(),
                descricao: descricao.trim(),
                pagina_referencia: paginaRef.trim(),
                ativo: true
            });


            // Adicionar ao combatente
            await this.talentoService.adicionarTalento(this.combatente.id, {
                talento_id: novoTalento.id
            });

            // Recarregar talentos
            await this.carregarRenderizarTalentos(this.combatente.id);

            // Limpar formulário
            document.getElementById('formCriarTalento').reset();

            // Voltar para aba de listar
            this.abrirAbaListarTalentos();

            // Notificação
            if (window.NotificationService) {
                window.NotificationService.mostrarSucesso(`✅ Talento "${nome}" criado e adicionado!`);
            }

        } catch (error) {
            console.error('❌ Erro ao criar talento:', error);
            if (window.NotificationService) {
                window.NotificationService.mostrarErro('❌ Erro ao criar talento: ' + error.message);
            }
        }
    }

    // ─────────────────────────────────────────────────────────
    // PERÍCIAS
    // ─────────────────────────────────────────────────────────


    abrirPaginaPericias() {
        if (!this.combatente?.id) {
            window.NotificationService?.erro('❌ Selecione um combatente primeiro');
            return;
        }

        try {
            const params = new URLSearchParams({
                combatente_id: this.combatente.id,
                return_to: encodeURIComponent(window.location.pathname + window.location.search)
            });

            window.location.href = `/games/dnd35/pages/pericias-ficha.html?${params.toString()}`;
        } catch (err) {
            window.NotificationService?.erro('❌ Erro ao abrir perícias');
            console.error(err);
        }
    }

    }

// ── Inicializar quando DOM estiver pronto ──
document.addEventListener('DOMContentLoaded', async () => {
    installGlobalErrorGuards('ficha-page');
    const controller = safeBootstrap(
        'ficha-controller',
        () => new FichaPersonagemController(),
        'Falha ao iniciar a ficha do personagem.'
    );
    if (!controller) return;

    window._fichaController = controller;
    await safeBootstrapAsync(
        'ficha-inicializacao',
        () => controller.inicializar(),
        'Nao foi possivel carregar os dados completos da ficha.'
    );
});
