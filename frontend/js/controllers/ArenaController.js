/**
 * Controller da Arena de Combate
 * Princípio SOLID: SRP - Gerencia apenas a tela de arena
 */
import { CombatenteService } from '../services/CombatenteService.js';
import { Toast } from '../ui/Toast.js';

export class ArenaController {
    constructor() {
        this.combatenteService = new CombatenteService();
        this.combatentes = [];
        this.turnoAtual = 0;
        this.rodadaAtual = 1;
        this.hpVisivel = false; // ← Inicia OCULTO
        
        this.inicializar();
    }

    /**
     * Inicializa o controller
     */
    inicializar() {
        this.configurarEventos();
    }

    /**
     * Configura event listeners
     */
    configurarEventos() {
        // Evento: Iniciar Combate
        document.addEventListener('iniciarCombate', (e) => {
            console.log('🎮 Evento iniciarCombate recebido:', e.detail);
            
            if (e.detail && e.detail.combatentes) {
                this.iniciarCombate(e.detail.combatentes);
            } else {
                console.error('❌ Dados de combatentes inválidos:', e.detail);
                Toast.error('Erro: Dados de combatentes inválidos');
            }
        });

        // Botão: Avançar Turno
        const btnAvancar = document.getElementById('btnAvancarTurno');
        if (btnAvancar) {
            btnAvancar.addEventListener('click', () => this.avancarTurno());
        }

        // Botão: Resetar Combate
        const btnResetar = document.getElementById('btnResetarCombate');
        if (btnResetar) {
            btnResetar.addEventListener('click', () => this.resetarCombate());
        }

        // Botão: Finalizar Combate
        const btnFinalizar = document.getElementById('btnFinalizarCombate');
        if (btnFinalizar) {
            btnFinalizar.addEventListener('click', () => this.finalizarCombate());
        }
    }

    /**
     * Inicia o combate com os combatentes selecionados
     */
    iniciarCombate(combatentes) {
        console.log('⚔️ Iniciando combate com:', combatentes);
        
        if (!combatentes || !Array.isArray(combatentes) || combatentes.length === 0) {
            console.error('❌ Combatentes inválidos:', combatentes);
            Toast.error('Erro: Nenhum combatente válido para iniciar combate');
            return;
        }

        this.combatentes = combatentes.sort((a, b) => b.iniciativa - a.iniciativa);
        this.turnoAtual = 0;
        this.rodadaAtual = 1;
        this.hpVisivel = false; // ← Reseta para OCULTO ao iniciar
        
        console.log('📊 Ordem de iniciativa:', this.combatentes.map(c => `${c.nome} (${c.iniciativa})`));
        
        this.atualizarRodada();
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
    }

    /**
     * Avança para o próximo turno
     */
    avancarTurno() {
        const combatenteAtual = this.combatentes[this.turnoAtual];
        
        console.log(`➡️ Avançando turno. Turno atual: ${this.turnoAtual}, Combatente: ${combatenteAtual?.nome}`);
        
        this.turnoAtual++;
        
        if (this.turnoAtual >= this.combatentes.length) {
            this.turnoAtual = 0;
            this.rodadaAtual++;
            this.atualizarRodada();
            Toast.success(`🎯 Rodada ${this.rodadaAtual} iniciada!`);
            console.log(`🔄 Nova rodada iniciada: ${this.rodadaAtual}`);
        }
        
        const proximoCombatente = this.combatentes[this.turnoAtual];
        console.log(`✅ Próximo combatente: ${proximoCombatente?.nome}`);
        
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
    }

    /**
     * Alterna visibilidade dos valores de HP (APENAS do combatente ativo)
     */
    toggleVisibilidadeHP() {
        this.hpVisivel = !this.hpVisivel;
        console.log(`👁️ Visibilidade HP (combatente ativo): ${this.hpVisivel ? 'Visível' : 'Oculto'}`);
        
        // Re-renderizar combatente ativo E lista de ordem
        this.renderizarOrdemIniciativa(); // ← ADICIONADO
        this.renderizarCombatenteAtivo();
        
        Toast.success(this.hpVisivel ? '👁️ HP do Combatente Ativo Visível' : '🙈 HP do Combatente Ativo Oculto');
    }

    /**
     * Atualiza o display da rodada atual
     */
    atualizarRodada() {
        const rodadaDisplay = document.getElementById('rodadaAtual');
        if (rodadaDisplay) {
            rodadaDisplay.textContent = this.rodadaAtual;
            console.log(`📊 Rodada atualizada no display: ${this.rodadaAtual}`);
        }
    }

    /**
     * Renderiza a ordem de iniciativa
     */
    renderizarOrdemIniciativa() {
        const container = document.getElementById('ordemIniciativaContainer');
        if (!container) return;

        container.innerHTML = this.combatentes.map((c, index) => {
            const isAtivo = index === this.turnoAtual;
            const isMorto = c.hp_atual <= 0;
            const statusClass = isMorto ? 'ordem-morto' : (isAtivo ? 'ordem-ativo' : '');
            const iconClass = isMorto ? 'ordem-status-morto' : (isAtivo ? 'ordem-status-ativo' : 'ordem-status-aguardando');
            const icon = isMorto ? '💀' : (isAtivo ? '⚔️' : index + 1);
            const hpClass = c.hp_atual <= (c.hp_maximo * 0.25) ? 'ordem-hp-critical' : '';

            // ← ALTERADO: Mostrar HP real apenas se for o combatente ativo E hpVisivel === true
            const hpTexto = (isAtivo && this.hpVisivel)
                ? `HP: ${c.hp_atual}/${c.hp_maximo}`
                : `HP: ???/???`;

            return `
                <div class="ordem-item ${statusClass}">
                    <span class="ordem-status-icon ${iconClass}">${icon}</span>
                    <div class="ordem-info">
                        <div class="ordem-nome">${c.nome}</div>
                        <div class="ordem-detalhes">
                            <span class="ordem-iniciativa">Ini: ${c.iniciativa}</span>
                            <span class="ordem-hp ${hpClass}">
                                ${hpTexto}
                            </span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    /**
     * Renderiza o combatente ativo
     */
    renderizarCombatenteAtivo() {
        const container = document.getElementById('combatenteAtivoContainer');
        if (!container) return;

        const combatente = this.combatentes[this.turnoAtual];
        if (!combatente) return;

        const isMorto = combatente.hp_atual <= 0;
        const hpPercentual = (combatente.hp_atual / combatente.hp_maximo) * 100;
        const hpCor = this.getCorHP(hpPercentual);
        const hpCritical = hpPercentual <= 25;

        // Condicional para exibir ou ocultar valores de HP
        const hpValorTexto = this.hpVisivel 
            ? `${combatente.hp_atual} / ${combatente.hp_maximo}`
            : `??? / ???`;

        const iconVisibilidade = this.hpVisivel ? '👁️' : '🙈';
        const tooltipVisibilidade = this.hpVisivel ? 'Ocultar HP' : 'Mostrar HP';

        container.innerHTML = `
            <div class="combatente-ativo-card ${isMorto ? 'morto' : ''}">
                <div class="combatente-foto-vertical">
                    ${combatente.foto_url 
                        ? `<img src="${combatente.foto_url}" alt="${combatente.nome}">`
                        : `<div class="foto-placeholder">${this.getEmojiTipo(combatente.tipo)}</div>`
                    }
                </div>

                <div class="combatente-conteudo">
                    <div class="combatente-header-ativo">
                        <div>
                            <h2>${combatente.nome}</h2>
                            <span class="combatente-classe">${combatente.classe || 'Aventureiro'} • Nível ${combatente.nivel || 1}</span>
                        </div>
                        <span class="badge ${this.getBadgeClass(combatente.tipo)}">${this.getEmojiTipo(combatente.tipo)} ${combatente.tipo}</span>
                    </div>

                    <div class="combatente-grid-principal">
                        <!-- HP -->
                        <div class="secao-hp">
                            <div class="secao-hp-header">
                                <h3>💚 Pontos de Vida</h3>
                                <button class="btn-toggle-hp" onclick="toggleVisibilidadeHP()" title="${tooltipVisibilidade}">
                                    ${iconVisibilidade}
                                </button>
                            </div>
                            <div class="hp-display">
                                <div class="hp-bar-grande">
                                    <div class="hp-fill-grande" style="width: ${hpPercentual}%; background: ${hpCor};"></div>
                                </div>
                                <div class="hp-valor-grande ${hpCritical ? 'hp-critical-text' : ''} ${!this.hpVisivel ? 'hp-oculto' : ''}">
                                    ${hpValorTexto}
                                </div>
                            </div>
                            <div class="hp-acoes">
                                <div class="hp-input-group">
                                    <input type="number" class="input-hp" id="inputDano" min="0" value="5" placeholder="Dano">
                                    <button class="btn-dano" onclick="aplicarDano(${combatente.id})" ${isMorto ? 'disabled' : ''}>
                                        ⚔️ Aplicar Dano
                                    </button>
                                </div>
                                <div class="hp-input-group">
                                    <input type="number" class="input-hp" id="inputCura" min="0" value="5" placeholder="Cura">
                                    <button class="btn-cura" onclick="aplicarCura(${combatente.id})" ${isMorto ? 'disabled' : ''}>
                                        💚 Aplicar Cura
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Resistências -->
                        <div class="secao-resistencias">
                            <h3>🛡️ Resistências</h3>
                            <div class="resistencias-grid">
                                <div class="resistencia-item">
                                    <span class="resistencia-label">Fortitude</span>
                                    <span class="resistencia-valor">${combatente.fortitude !== undefined ? combatente.fortitude : 0}</span>
                                </div>
                                <div class="resistencia-item">
                                    <span class="resistencia-label">Reflexos</span>
                                    <span class="resistencia-valor">${combatente.reflexos !== undefined ? combatente.reflexos : 0}</span>
                                </div>
                                <div class="resistencia-item">
                                    <span class="resistencia-label">Vontade</span>
                                    <span class="resistencia-valor">${combatente.vontade !== undefined ? combatente.vontade : 0}</span>
                                </div>
                            </div>
                        </div>

                        <!-- Atributos -->
                        <div class="secao-atributos">
                            <h3>⚡ Atributos</h3>
                            <div class="atributos-compacto">
                                ${this.renderizarAtributo('FOR', combatente.forca)}
                                ${this.renderizarAtributo('DES', combatente.destreza)}
                                ${this.renderizarAtributo('CON', combatente.constituicao)}
                                ${this.renderizarAtributo('INT', combatente.inteligencia)}
                                ${this.renderizarAtributo('SAB', combatente.sabedoria)}
                                ${this.renderizarAtributo('CAR', combatente.carisma)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Configurar funções globais para botões
        window.aplicarDano = (id) => this.aplicarDano(id);
        window.aplicarCura = (id) => this.aplicarCura(id);
        window.toggleVisibilidadeHP = () => this.toggleVisibilidadeHP();
    }

    /**
     * Renderiza um atributo
     */
    renderizarAtributo(nome, valor) {
        const mod = this.calcularModificador(valor);
        const modStr = mod >= 0 ? `+${mod}` : `${mod}`;
        
        return `
            <div class="atributo-compacto">
                <div class="atributo-nome">${nome}</div>
                <div class="atributo-valor">${valor}</div>
                <div class="atributo-mod">${modStr}</div>
            </div>
        `;
    }

    /**
     * Calcula modificador de atributo D&D
     */
    calcularModificador(valor) {
        return Math.floor((valor - 10) / 2);
    }

    /**
     * Retorna cor do HP baseado no percentual
     */
    getCorHP(percentual) {
        if (percentual > 50) return 'linear-gradient(90deg, #32CD32 0%, #228B22 100%)';
        if (percentual > 25) return 'linear-gradient(90deg, #FFA500 0%, #FF8C00 100%)';
        return 'linear-gradient(90deg, #DC143C 0%, #8B0000 100%)';
    }

    /**
     * Retorna classe CSS para badge do tipo
     */
    getBadgeClass(tipo) {
        const classes = {
            'jogador': 'badge-jogador',
            'monstro': 'badge-monstro',
            'npc': 'badge-npc'
        };
        return classes[tipo] || 'badge-default';
    }

    /**
     * Retorna emoji para o tipo
     */
    getEmojiTipo(tipo) {
        const emojis = {
            'jogador': '🧙',
            'monstro': '👹',
            'npc': '🤝'
        };
        return emojis[tipo] || '⚔️';
    }

    /**
     * Aplica dano a um combatente
     */
    async aplicarDano(id) {
        const input = document.getElementById('inputDano');
        const dano = parseInt(input.value) || 0;

        if (dano <= 0) {
            Toast.error('Digite um valor de dano válido');
            return;
        }

        const combatente = this.combatentes.find(c => c.id === id);
        if (!combatente) return;

        const novoHP = Math.max(0, combatente.hp_atual - dano);

        try {
            await this.combatenteService.atualizarHP(id, novoHP);
            combatente.hp_atual = novoHP;

            Toast.success(`${combatente.nome} sofreu ${dano} de dano! 💥`);

            if (novoHP === 0) {
                Toast.error(`${combatente.nome} foi derrotado! 💀`);
            }

            this.renderizarOrdemIniciativa();
            this.renderizarCombatenteAtivo();
        } catch (error) {
            Toast.error('Erro ao aplicar dano');
            console.error(error);
        }
    }

    /**
     * Aplica cura a um combatente
     */
    async aplicarCura(id) {
        const input = document.getElementById('inputCura');
        const cura = parseInt(input.value) || 0;

        if (cura <= 0) {
            Toast.error('Digite um valor de cura válido');
            return;
        }

        const combatente = this.combatentes.find(c => c.id === id);
        if (!combatente) return;

        const novoHP = Math.min(combatente.hp_maximo, combatente.hp_atual + cura);

        try {
            await this.combatenteService.atualizarHP(id, novoHP);
            combatente.hp_atual = novoHP;

            Toast.success(`${combatente.nome} recuperou ${cura} HP! 💚`);

            this.renderizarOrdemIniciativa();
            this.renderizarCombatenteAtivo();
        } catch (error) {
            Toast.error('Erro ao aplicar cura');
            console.error(error);
        }
    }

    /**
     * Reseta o combate
     */
    resetarCombate() {
        if (!confirm('⚠️ Deseja realmente resetar o combate?\n\nTodos os combatentes retornarão ao HP máximo.')) {
            return;
        }

        this.combatentes.forEach(c => {
            c.hp_atual = c.hp_maximo;
            this.combatenteService.atualizarHP(c.id, c.hp_maximo).catch(console.error);
        });

        this.turnoAtual = 0;
        this.rodadaAtual = 1;
        this.hpVisivel = false; // ← Resetar para OCULTO
        this.atualizarRodada();
        
        Toast.success('Combate resetado! 🔄');
        
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
    }

    /**
     * Finaliza o combate
     */
    finalizarCombate() {
        if (!confirm('⚠️ Deseja finalizar o combate e voltar para a configuração?')) {
            return;
        }

        document.getElementById('telaArena').classList.remove('ativa');
        document.getElementById('telaConfiguracao').classList.add('ativa');

        Toast.success('Combate finalizado! 🏁');
    }
}