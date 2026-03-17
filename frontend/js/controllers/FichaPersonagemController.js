/**
 * FichaPersonagemController.js
 * SRP: Controlar renderização da ficha do personagem
 * SOLID: DIP via constructor injection de services
 */

import { PericiaService } from '../services/PericiaService.js';
import { CombatenteService } from '../services/CombatenteService.js';

export class FichaPersonagemController {
    constructor() {
        this.periciaService = new PericiaService();
        this.combatenteService = new CombatenteService();
        this.token = localStorage.getItem('token');
        this.combatente = null;
        this.pericias = [];
        
        console.log('✅ FichaPersonagemController inicializado');
    }

    async inicializar() {
        try {
            // Obter ID da URL
            const params = new URLSearchParams(window.location.search);
            const combatenteId = params.get('id');

            if (!combatenteId) {
                throw new Error('ID do combatente não fornecido');
            }

            console.log('🎯 Carregando ficha do combatente:', combatenteId);

            // Carregar combatente
            this.combatente = await this.combatenteService.obterCombatente(parseInt(combatenteId));
            console.log('✅ Combatente carregado:', this.combatente.nome);

            // Renderizar dados básicos
            this.renderizarIdentidade();
            this.renderizarAtributos();
            this.renderizarDefesa();
            this.renderizarResistencias();

            // Carregar e renderizar perícias
            await this.carregarRenderizarPericias(parseInt(combatenteId));

            console.log('✅ Ficha carregada com sucesso');

        } catch (error) {
            console.error('❌ Erro ao inicializar ficha:', error);
            this.mostrarErro('Erro ao carregar ficha: ' + error.message);
        }
    }

    /**
     * Renderiza identidade do combatente
     */
    renderizarIdentidade() {
        const nome = document.getElementById('fichaNome');
        const raca = document.getElementById('fichaRaca');
        const classe = document.getElementById('fichaClasse');
        const tipo = document.getElementById('fichaTipo');
        const nivel = document.getElementById('fichaNivel');
        const placeholder = document.getElementById('fichaFotoPlaceholder');
        const foto = document.getElementById('fichaFoto');

        if (nome) nome.textContent = this.combatente.nome;
        if (raca) raca.textContent = this.combatente.raca || '—';
        if (classe) classe.textContent = this.combatente.classe || '—';
        if (tipo) tipo.textContent = this.combatente.tipo || 'jogador';
        if (nivel) nivel.textContent = this.combatente.nivel || 1;

        // Foto
        if (this.combatente.foto_url) {
            foto.src = this.combatente.foto_url;
            foto.classList.add('carregada');
            if (placeholder) placeholder.style.display = 'none';
        } else {
            const emojiMap = { jogador: '🧙', npc: '🤝', monstro: '👹' };
            if (placeholder) placeholder.textContent = emojiMap[this.combatente.tipo] || '⚔️';
        }

        console.log('✅ Identidade renderizada');
    }

    /**
     * Renderiza atributos em círculos
     */
    renderizarAtributos() {
        const atributos = ['forca', 'destreza', 'constituicao', 'inteligencia', 'sabedoria', 'carisma'];
        const abreviacoes = { forca: 'For', destreza: 'Des', constituicao: 'Con', inteligencia: 'Int', sabedoria: 'Sab', carisma: 'Car' };

        atributos.forEach(attr => {
            const valor = this.combatente[attr] || 10;
            const modificador = Math.floor((valor - 10) / 2);

            const elementoValor = document.getElementById(`ficha${abreviacoes[attr]}`);
            const elementoMod = document.getElementById(`ficha${abreviacoes[attr]}Mod`);

            if (elementoValor) elementoValor.textContent = valor;
            if (elementoMod) elementoMod.textContent = modificador >= 0 ? `+${modificador}` : `${modificador}`;
        });

        console.log('✅ Atributos renderizados');
    }

    /**
     * Renderiza defesa (CA, PV, Iniciativa)
     */
    renderizarDefesa() {
        const ca = document.getElementById('fichaCa');
        const pv = document.getElementById('fichaPv');
        const pvFill = document.getElementById('fichaPvFill');
        const iniciativa = document.getElementById('fichaIniciativa');

        if (ca) ca.textContent = this.combatente.ca || 10;
        if (pv) pv.textContent = `${this.combatente.hp_atual}/${this.combatente.hp_maximo}`;
        
        if (pvFill) {
            const percentual = (this.combatente.hp_atual / this.combatente.hp_maximo) * 100;
            pvFill.style.width = `${percentual}%`;
        }

        if (iniciativa) {
            const ini = this.combatente.iniciativa || 0;
            iniciativa.textContent = ini >= 0 ? `+${ini}` : `${ini}`;
        }

        console.log('✅ Defesa renderizada');
    }

    /**
     * Renderiza resistências
     */
    renderizarResistencias() {
        const fort = document.getElementById('fichaFort');
        const reflex = document.getElementById('fichaReflex');
        const vont = document.getElementById('fichaVont');

        if (fort) fort.textContent = `+${this.combatente.fortitude || 0}`;
        if (reflex) reflex.textContent = `+${this.combatente.reflexos || 0}`;
        if (vont) vont.textContent = `+${this.combatente.vontade || 0}`;

        console.log('✅ Resistências renderizadas');
    }

    /**
     * Carrega e renderiza perícias do combatente
     */
    async carregarRenderizarPericias(combatenteId) {
        try {
            const url = `http://localhost:8000/api/v1/pericias/${combatenteId}/listar`;
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Erro ao carregar perícias`);
            }

            const data = await response.json();
            const pericias = data.pericias || [];

            console.log('✅ Perícias carregadas:', pericias.length);

            this.renderizarPericiasNaFicha(pericias);

        } catch (error) {
            console.warn('⚠️ Erro ao carregar perícias:', error);
            this.renderizarPericiasVazias();
        }
    }

    /**
     * Renderiza perícias na ficha
     */
    renderizarPericiasNaFicha(pericias) {
        const container = document.getElementById('fichaPericiasLista');
        if (!container) return;

        container.innerHTML = '';

        if (pericias.length === 0) {
            container.innerHTML = '<span class="ficha-vazio">Nenhuma perícia selecionada</span>';
            return;
        }

        pericias.forEach(pj => {
            const total = pj.graduacao + pj.modificador_atributo + (pj.bonus_outros || 0);

            const item = document.createElement('div');
            item.className = 'ficha-pericia-item';
            item.title = pj.pericia.descricao || '';

            item.innerHTML = `
                <span class="ficha-pericia-nome">${pj.pericia.nome}</span>
                <span class="ficha-pericia-atributo">${pj.pericia.atributo}</span>
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
                </div>
                <span class="ficha-pericia-total">${total >= 0 ? '+' : ''}${total}</span>
            `;

            container.appendChild(item);
        });

        console.log('✅ Perícias renderizadas na ficha:', pericias.length);
    }

    /**
     * Renderiza perícias vazias
     */
    renderizarPericiasVazias() {
        const container = document.getElementById('fichaPericiasLista');
        if (container) {
            container.innerHTML = '<span class="ficha-vazio">Nenhuma perícia selecionada</span>';
        }
    }

    /**
     * Mostra erro na ficha
     */
    mostrarErro(mensagem) {
        console.error('❌', mensagem);
        const container = document.getElementById('fichaPericiasLista');
        if (container) {
            container.innerHTML = `<span class="ficha-vazio">❌ ${mensagem}</span>`;
        }
    }
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', async () => {
    const controller = new FichaPersonagemController();
    await controller.inicializar();
});