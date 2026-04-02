/**
 * FichaPersonagemController.js
 * SRP: Controlar renderização da ficha do personagem
 * SOLID: DIP via constructor injection de services
 * ✅ NOVO: BroadcastChannel sync arena→ficha em tempo real
 */

import { CombatenteService } from '../services/CombatenteService.js';
import { EquipamentoService } from '../services/EquipamentoService.js';
import { ArmaduraProtecaoService } from '../services/ArmaduraProtecaoService.js';
import { TalentoService } from '../services/TalentoService.js';
import { PericiaService } from '../services/PericiaService.js';
import { getApiUrl } from '../config/api.config.js';
import { escapeHtml } from '../utils/formatters.js';
import {
    installGlobalErrorGuards,
    safeBootstrap,
    safeBootstrapAsync,
} from '../utils/graceful-degradation.js';
import { resolveCombatenteSpellSlots } from '../utils/combat-rules.js?v=20260331a';

const DOMINIOS_PERMITIDOS_FALLBACK = [
    'Ar', 'Bem', 'Caos', 'Conhecimento', 'Cura', 'Destruição', 'Enganação', 'Fogo', 'Força',
    'Guerra', 'Magia', 'Mal', 'Morte', 'Proteção', 'Sol', 'Sorte', 'Terra', 'Viagem',
];

export class FichaPersonagemController {

    constructor() {
        this.combatenteService = new CombatenteService();
        this.equipamentoService = new EquipamentoService();
        this.armaduraProtecaoService = new ArmaduraProtecaoService();
        this.talentoService = new TalentoService();
        this.periciaService = new PericiaService();
        this.token             = localStorage.getItem('token');
        this.combatente        = null;
        this.bonusCaProtecao   = 0;
        this.dominiosPermitidos = [...DOMINIOS_PERMITIDOS_FALLBACK];

        // ✅ NOVO: canal de escuta arena → ficha
        this._canal = null;
        this._configurarCanalSync();

        console.log('✅ FichaPersonagemController inicializado');
    }

    async inicializar() {
        try {
            const params       = new URLSearchParams(window.location.search);
            const combatenteId = params.get('id');

            if (!combatenteId) throw new Error('ID do combatente não fornecido');

            console.log('🎯 Carregando ficha do combatente:', combatenteId);

            this.combatente = await this.combatenteService.obterCombatente(parseInt(combatenteId));
            await this._carregarDominiosPermitidos();

            // ✅ Expor globalmente para debug no console
            window._fichaController = this;

            console.log('✅ Combatente carregado:', this.combatente.nome);
            console.log('📦 magias_slots recebidos:', this.combatente.magias_slots);
            console.log('⚔️ ataques recebidos:', this.combatente.ataques);

            // ── Renderizar tudo ──
            this.renderizarIdentidade();
            this._atualizarHeaderNome();
            this.renderizarAtributos();
            this.renderizarDefesa();
            this.renderizarResistencias();
            this.renderizarAtaques();
            this.renderizarSlotsDeMapia();
            await this.carregarRenderizarPericias(parseInt(combatenteId));
            await this.carregarRenderizarEquipamentos(parseInt(combatenteId));
            await this.carregarRenderizarArmadurasProtecao(parseInt(combatenteId));
            await this.carregarRenderizarTalentos(parseInt(combatenteId));

            // ── Configurar eventos ──
            this._configurarEventos();

            console.log('✅ Ficha carregada com sucesso');

        } catch (error) {
            console.error('❌ Erro ao inicializar ficha:', error);
            this.mostrarErro('Erro ao carregar ficha: ' + error.message);
        }
    }

    _configurarEventos() {
        const btnVoltar = document.getElementById('btnVoltarFicha');
        if (btnVoltar) {
            btnVoltar.addEventListener('click', () => {
                window.location.href = '/pages/dashboard.html';
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

        const btnEditarPerfilMagico = document.getElementById('btnEditarPerfilMagico');
        if (btnEditarPerfilMagico) {
            btnEditarPerfilMagico.addEventListener('click', () => this.abrirModalPerfilMagico());
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
            equipamentosBusca.addEventListener('input', () => this.filtrarEquipamentos());
        }

        const armadurasProtecaoBusca = document.getElementById('armadurasProtecaoBusca');
        if (armadurasProtecaoBusca) {
            armadurasProtecaoBusca.addEventListener('input', () => this.filtrarArmadurasProtecao());
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
            console.log('✅ FichaController: canal sync arena→ficha ativo');
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

        console.log('📡 Sync magia recebida na ficha:', payload);

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

        console.log(`📊 Slot nível ${nivel} atualizado: ${disponiveis}/${total}`);
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
                console.log(`📖 Grimório: slot nível ${nivel} sincronizado`);
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
        const dominios    = document.getElementById('fichaDominios');
        const placeholder = document.getElementById('fichaFotoPlaceholder');
        const foto        = document.getElementById('fichaFoto');

        if (nomeHeader) nomeHeader.textContent = this.combatente.nome;
        if (raca)   raca.textContent   = this.combatente.raca   || '—';
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
        if (dominios) dominios.textContent = `Domínios: ${this._formatarDominios(this.combatente.dominios)}`;

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

        console.log('✅ Identidade renderizada');
    }

    _formatarDominios(valor) {
        const texto = String(valor || '').trim();
        return texto || '—';
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

    _renderizarListaDominiosPerfil() {
        const lista = document.getElementById('listaPerfilDominios');
        const hint = document.getElementById('hintPerfilDominios');

        if (lista) {
            lista.innerHTML = this.dominiosPermitidos
                .map((dominio) => `<option value="${escapeHtml(dominio)}"></option>`)
                .join('');
        }

        if (hint) {
            hint.textContent = `Permitidos: ${this.dominiosPermitidos.join(', ')}. Separe múltiplos domínios por vírgula.`;
        }
    }

    abrirModalPerfilMagico() {
        const modal = document.getElementById('modalPerfilMagico');
        const inputAlinhamento = document.getElementById('inputPerfilAlinhamento');
        const inputDominios = document.getElementById('inputPerfilDominios');
        if (!modal || !this.combatente) return;

        if (inputAlinhamento) inputAlinhamento.value = this.combatente.alinhamento || '';
        if (inputDominios) inputDominios.value = this.combatente.dominios || '';
        modal.style.display = 'flex';
    }

    fecharModalPerfilMagico() {
        const modal = document.getElementById('modalPerfilMagico');
        if (modal) modal.style.display = 'none';
    }

    _normalizarDominiosPerfil(raw) {
        const itens = String(raw || '')
            .split(',')
            .map((item) => item.trim())
            .filter(Boolean);

        if (!itens.length) return '';

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

        return normalizados.join(', ');
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
            alinhamento: this.combatente.alinhamento || '',
            dominios: this.combatente.dominios || '',
            pagina_referencia: this.combatente.pagina_referencia || '',
            ca: this.combatente.ca ?? 10,
            toque: this.combatente.toque ?? 10,
            surpresa: this.combatente.surpresa ?? 10,
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
        const inputDominios = document.getElementById('inputPerfilDominios');
        const alinhamento = inputAlinhamento?.value || '';

        try {
            const dominios = this._normalizarDominiosPerfil(inputDominios?.value || '');
            const formData = this._buildFormDataAtualizacaoCombatente({ alinhamento, dominios });
            this.combatente = await this.combatenteService.atualizar(this.combatente.id, formData);

            this.renderizarIdentidade();
            this.fecharModalPerfilMagico();

            if (window._grimorioController && document.getElementById('modalGrimorio')?.classList.contains('show')) {
                await window._grimorioController._recarregarDados();
            }

            window.NotificationService?.sucesso('✅ Perfil mágico atualizado.');
        } catch (error) {
            console.error('❌ Erro ao salvar perfil mágico:', error);
            window.NotificationService?.erro(`❌ ${error.message || 'Erro ao salvar perfil mágico.'}`);
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

        console.log('✅ Atributos renderizados');
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

        const caBase = this.combatente.ca ?? 10;
        const bonusProtecao = Number(this.bonusCaProtecao || 0);
        if (ca) {
            ca.textContent = caBase + bonusProtecao;
            ca.title = bonusProtecao
                ? `CA base ${caBase} + bônus de proteção ${bonusProtecao}`
                : `CA base ${caBase}`;
        }
        if (toque)    toque.textContent    = this.combatente.toque    ?? 10;
        if (surpresa) surpresa.textContent = this.combatente.surpresa ?? 10;

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
        }

        console.log('✅ Defesa renderizada');
    }

    // ─────────────────────────────────────────────────────────
    // RESISTÊNCIAS
    // ─────────────────────────────────────────────────────────

    renderizarResistencias() {
        const fort   = document.getElementById('fichaFort');
        const reflex = document.getElementById('fichaReflex');
        const vont   = document.getElementById('fichaVont');

        const fmt = v => v >= 0 ? `+${v}` : `${v}`;
        if (fort)   fort.textContent   = fmt(this.combatente.fortitude || 0);
        if (reflex) reflex.textContent = fmt(this.combatente.reflexos  || 0);
        if (vont)   vont.textContent   = fmt(this.combatente.vontade   || 0);

        console.log('✅ Resistências renderizadas');
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

        console.log('✅ Ataques renderizados:', ataques.length);
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

        if (this.combatente) {
            this.combatente.magias_slots = slots;
        }

        console.log('🔮 Todos os slots:', slots);
        console.log('🔮 Slots ativos (total > 0):', slotsAtivos);

        if (secao && this.combatente.tipo === 'jogador') {
            secao.style.display = 'flex';
        }

        if (slotsAtivos.length === 0) {
            grid.innerHTML = '<div class="ficha-magia-vazio">Nenhum slot cadastrado</div>';
            console.log('ℹ️ Nenhum slot de magia ativo');
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

            return `
                <div class="ficha-slot-linha">
                    <div class="ficha-slot-topo">
                        <span class="ficha-slot-nivel">${labelNivel}</span>
                        <span class="ficha-slot-contagem">${disponiveis}/${total}</span>
                    </div>
                    <div class="ficha-slot-barra-wrap">
                        <div class="ficha-slot-barra-fill"
                            style="width:${pct}%; background:${corBarra}">
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        console.log('✅ Slots de magia renderizados:', slotsAtivos.length);
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
            console.log('✅ Perícias carregadas:', pericias.length);
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
        pericias.forEach(pj => {
            const total = pj.graduacao + pj.modificador_atributo + (pj.bonus_outros || 0);
            const item  = document.createElement('div');
            item.className = 'ficha-pericia-item';
            item.title     = pj.pericia?.descricao || '';
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
                        <span class="ficha-pericia-mod-valor">${pj.modificador_atributo >= 0 ? '+' : ''}${pj.modificador_atributo}</span>
                    </div>
                    <div class="ficha-pericia-mod">
                        <span class="ficha-pericia-mod-label">Bôn</span>
                        <span class="ficha-pericia-mod-valor">${pj.bonus_outros >= 0 ? '+' : ''}${pj.bonus_outros || 0}</span>
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

        console.log('✅ Perícias renderizadas:', pericias.length);
    }

    renderizarPericiasVazias() {
        const container = document.getElementById('fichaPericiasLista');
        if (container) container.innerHTML = '<span class="ficha-vazio">Nenhuma perícia selecionada</span>';
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
            console.log('✅ Equipamentos carregados:', equipamentos.length);
            
            this.renderizarEquipamentos(equipamentos);
        } catch (error) {
            console.error('❌ Erro ao carregar equipamentos:', error);
            this.mostrarErroEquipamentos('Erro ao carregar equipamentos');
        }
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
                    <span>Descrição</span>
                    <span>Pág. Ref</span>
                    <span>Qtd</span>
                    <span>Ação</span>
                </div>
                <div class="ficha-equipamentos-lista-items">
                    ${equipamentos.map(eq => `
                        <div class="ficha-equipamento-linha">
                            <span class="ficha-equipamento-nome">${escapeHtml(eq.nome)}</span>
                            <span class="ficha-equipamento-desc">${escapeHtml(eq.descricao) || '—'}</span>
                            <span class="ficha-equipamento-pag">${escapeHtml(eq.pagina_referencia) || '—'}</span>
                            <span class="ficha-equipamento-qtd">${eq.quantidade}</span>
                            <button class="btn-deletar-eq" data-eq-id="${eq.id}" data-eq-nome="${escapeHtml(eq.nome)}" title="Deletar ${escapeHtml(eq.nome)}">🗑️</button>
                        </div>
                    `).join('')}
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

        console.log('✅ Equipamentos renderizados:', equipamentos.length);
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

            const itens = await this.armaduraProtecaoService.listarItens(0, 200);
            this.armadurasProtecaoDisponiveis = itens;
            this.renderizarListaArmadurasProtecao(itens);
            modal.style.display = 'flex';
        } catch (error) {
            console.error('❌ Erro ao abrir modal de armaduras/itens de proteção:', error);
            window.NotificationService?.mostrarErro('❌ Erro ao carregar armaduras/itens de proteção');
        }
    }

    fecharModalArmadurasProtecao() {
        const modal = document.getElementById('modalArmadurasProtecao');
        if (modal) modal.style.display = 'none';
    }

    renderizarListaArmadurasProtecao(itens) {
        const lista = document.getElementById('armadurasProtecaoLista');
        if (!lista) return;

        if (!itens || !itens.length) {
            lista.innerHTML = '<p class="equipamentos-vazio">Nenhum item de proteção encontrado</p>';
            return;
        }

        lista.innerHTML = itens.map((item) => `
            <div class="equipamento-item">
                <div class="equipamento-info">
                    <div class="equipamento-nome">${escapeHtml(item.nome)}</div>
                    <div class="equipamento-desc">Tipo: ${escapeHtml(item.tipo || '—')} • Bônus CA: ${Number(item.bonus_ca || 0) >= 0 ? '+' : ''}${Number(item.bonus_ca || 0)}</div>
                    <div class="equipamento-desc">DES Máx: ${escapeHtml(item.des_max || '—')} • Penalidade: ${Number(item.penalidade || 0)} • Falha Arcana: ${escapeHtml(item.falha_arcana || '—')}</div>
                    <div class="equipamento-pag">Deslocamento: ${escapeHtml(item.deslocamento || '—')} • Peso: ${item.peso ?? '—'}</div>
                    <div class="equipamento-desc">${escapeHtml(item.propriedades_especiais || '—')}</div>
                </div>
                <button class="equipamento-btn-adicionar" data-item-id="${item.id}">➕</button>
            </div>
        `).join('');

        lista.querySelectorAll('.equipamento-btn-adicionar').forEach((btn) => {
            btn.addEventListener('click', () => {
                const itemId = Number(btn.dataset.itemId);
                if (Number.isFinite(itemId)) this.adicionarArmaduraProtecaoClic(itemId);
            });
        });
    }

    filtrarArmadurasProtecao() {
        const termo = document.getElementById('armadurasProtecaoBusca')?.value || '';
        const filtrados = this.armaduraProtecaoService.filtrarPorBusca(this.armadurasProtecaoDisponiveis || [], termo);
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

            // Carregar lista de equipamentos disponíveis
            const equipamentos = await this.equipamentoService.listarEquipamentos(0, 100);
            console.log('📦 Equipamentos disponíveis:', equipamentos.length);

            // Armazenar para uso no filtro
            this.equipamentosDisponiveis = equipamentos;
            
            // Renderizar lista inicial
            this.renderizarListaEquipamentos(equipamentos);

            // Mostrar modal
            modal.style.display = 'flex';

        } catch (error) {
            console.error('❌ Erro ao abrir modal:', error);
            if (window.NotificationService) {
                window.NotificationService.mostrarErro('❌ Erro ao carregar equipamentos');
            }
        }
    }

    fecharModalEquipamentos() {
        const modal = document.getElementById('modalEquipamentos');
        if (modal) modal.style.display = 'none';
    }

    renderizarListaEquipamentos(equipamentos) {
        const lista = document.getElementById('equipamentosLista');
        if (!lista) return;

        if (!equipamentos || equipamentos.length === 0) {
            lista.innerHTML = '<p class="equipamentos-vazio">Nenhum equipamento encontrado</p>';
            return;
        }

        lista.innerHTML = equipamentos.map(eq => `
            <div class="equipamento-item">
                <div class="equipamento-info">
                    <div class="equipamento-nome">${escapeHtml(eq.nome)}</div>
                    <div class="equipamento-desc">${escapeHtml(eq.descricao) || '—'}</div>
                    <div class="equipamento-pag">${escapeHtml(eq.pagina_referencia) || '—'}</div>
                </div>
                <button class="equipamento-btn-adicionar" data-equipamento-id="${eq.id}">
                    ➕
                </button>
            </div>
        `).join('');

        lista.querySelectorAll('.equipamento-btn-adicionar').forEach((btn) => {
            btn.addEventListener('click', () => {
                const equipamentoId = Number(btn.dataset.equipamentoId);
                if (Number.isFinite(equipamentoId)) {
                    this.adicionarEquipamentoClic(equipamentoId);
                }
            });
        });
    }

    filtrarEquipamentos() {
        const termo = document.getElementById('equipamentosBusca')?.value || '';
        const filtrados = this.equipamentoService.filtrarPorBusca(
            this.equipamentosDisponiveis,
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

            // Pegar o nome do equipamento do modal
            const eqNomeElement = document.querySelector('#conteudoListar .ficha-equipamento-linha:last-child .ficha-equipamento-nome');
            const nomeEquipamento = eqNomeElement?.textContent || 'Equipamento';

            await this.equipamentoService.adicionarEquipamento(this.combatente.id, {
                equipamento_id: equipamentoId,
                quantidade: quantidade
            });

            console.log('✅ Equipamento adicionado');

            // Recarregar equipamentos
            await this.carregarRenderizarEquipamentos(this.combatente.id);

            // Resetar quantidade
            qntdInput.value = '1';

            // Mostrar notificação de sucesso
            if (window.NotificationService) {
                window.NotificationService.mostrarSucesso(`✅ Equipamento adicionado ao inventário!`);
            }

        } catch (error) {
            console.error('❌ Erro ao adicionar equipamento:', error);
            if (window.NotificationService) {
                window.NotificationService.mostrarErro('❌ Erro ao adicionar equipamento');
            }
        }
    }

    async deletarEquipamento(equipamentoId, nomeEquipamento) {
        if (!this.combatente?.id) {
            if (window.NotificationService) {
                window.NotificationService.mostrarErro('❌ ID do combatente não encontrado');
            }
            return;
        }

        const self = this;
        console.log('🗑️ deletarEquipamento chamado com ID:', equipamentoId, 'Nome:', nomeEquipamento);

        // Usar ModalConfirm em vez de confirm()
        const opcoes = {
            icone: '🗑️',
            titulo: 'Deletar Equipamento',
            texto: `Tem certeza que deseja deletar <strong>"${nomeEquipamento}"</strong>?`,
            textoConfirmar: '🗑️ Deletar',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar: async () => {
                try {
                    console.log('🗑️ Deletando equipamento:', equipamentoId, 'do combatente:', self.combatente.id);
                    await self.equipamentoService.removerEquipamento(self.combatente.id, equipamentoId);

                    console.log('✅ Equipamento removido');

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

            console.log('✅ Equipamento criado:', novoEquipamento);

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
            console.log('✅ Talentos carregados:', talentos.length);
            
            this.renderizarTalentos(talentos);
        } catch (error) {
            console.error('❌ Erro ao carregar talentos:', error);
            this.mostrarErroTalentos('Erro ao carregar talentos');
        }
    }

    renderizarTalentos(talentos) {
        const lista = document.getElementById('fichaTalentos');
        if (!lista) return;

        if (!talentos || talentos.length === 0) {
            lista.innerHTML = '<span class="ficha-vazio">Nenhum talento cadastrado</span>';
            return;
        }

        lista.innerHTML = `
            <div class="ficha-talentos-tabela">
                <div class="ficha-talento-header">
                    <span>Talento</span>
                    <span>Descrição</span>
                    <span>Pág. Ref</span>
                    <span>Ação</span>
                </div>
                <div class="ficha-talentos-lista-items">
                    ${talentos.map(tal => `
                        <div class="ficha-talento-linha">
                            <span class="ficha-talento-nome">${escapeHtml(tal.nome)}</span>
                            <span class="ficha-talento-desc">${escapeHtml(tal.descricao) || '—'}</span>
                            <span class="ficha-talento-pag">${escapeHtml(tal.pagina_referencia) || '—'}</span>
                            <button class="btn-deletar-tal" data-tal-id="${tal.id}" data-tal-nome="${escapeHtml(tal.nome)}" title="Deletar ${escapeHtml(tal.nome)}">🗑️</button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        // Configurar eventos dos botões de deletar
        const self = this;
        lista.querySelectorAll('.btn-deletar-tal').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const talId = e.target.dataset.talId;
                const talNome = e.target.dataset.talNome;
                self.deletarTalento(talId, talNome);
            });
        });

        console.log('✅ Talentos renderizados:', talentos.length);
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

            // Carregar lista de talentos disponíveis
            const talentos = await this.talentoService.listarTalentos(0, 100);
            console.log('📦 Talentos disponíveis:', talentos.length);

            // Armazenar para uso no filtro
            this.talentosDisponiveis = talentos;
            
            // Renderizar lista inicial
            this.renderizarListaTalentos(talentos);

            // Mostrar modal
            modal.style.display = 'flex';

        } catch (error) {
            console.error('❌ Erro ao abrir modal:', error);
            if (window.NotificationService) {
                window.NotificationService.mostrarErro('❌ Erro ao carregar talentos: ' + error.message);
            }
        }
    }

    renderizarListaTalentos(talentos) {
        const container = document.getElementById('conteudoListarTalentos');
        if (!container) return;

        if (!talentos || talentos.length === 0) {
            container.innerHTML = '<p class="equipamentos-vazio">Nenhum talento disponível</p>';
            return;
        }

        container.innerHTML = `
            <div class="equipamentos-lista-grid">
                ${talentos.map(tal => `
                    <div class="equipamentos-card">
                        <h4>${escapeHtml(tal.nome)}</h4>
                        <p class="equipamentos-desc">${escapeHtml(tal.descricao) || '—'}</p>
                        <p class="equipamentos-pag">📄 ${escapeHtml(tal.pagina_referencia) || '—'}</p>
                        <button class="equipamentos-btn-adicionar" data-talento-id="${tal.id}">
                            ➕ Adicionar
                        </button>
                    </div>
                `).join('')}
            </div>
        `;

        container.querySelectorAll('.equipamentos-btn-adicionar').forEach((btn) => {
            btn.addEventListener('click', () => {
                const talentoId = Number(btn.dataset.talentoId);
                if (Number.isFinite(talentoId)) {
                    this.adicionarTalentoClic(talentoId);
                }
            });
        });

        console.log('✅ Lista de talentos renderizada:', talentos.length);
    }

    filtrarTalentos() {
        const filtro = document.getElementById('talentosBusca')?.value?.toLowerCase() || '';
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

            console.log('✅ Talento adicionado');

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
        console.log('🗑️ deletarTalento chamado com ID:', talentoId, 'Nome:', nomeTalento);

        // Usar ModalConfirm em vez de confirm()
        const opcoes = {
            icone: '🗑️',
            titulo: 'Deletar Talento',
            texto: `Tem certeza que deseja deletar <strong>"${nomeTalento}"</strong>?`,
            textoConfirmar: '🗑️ Deletar',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar: async () => {
                try {
                    console.log('🗑️ Deletando talento:', talentoId, 'do combatente:', self.combatente.id);
                    await self.talentoService.removerTalento(self.combatente.id, talentoId);

                    console.log('✅ Talento removido');

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

            console.log('✅ Talento criado:', novoTalento);

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

            window.location.href = `/pages/pericias-ficha.html?${params.toString()}`;
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
