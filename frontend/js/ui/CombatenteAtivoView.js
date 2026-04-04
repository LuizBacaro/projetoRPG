/**
 * Componente de Visualização do Combatente Ativo
 * Princípio SOLID: Single Responsibility - renderizar combatente ativo
 */
export class CombatenteAtivoView {
    
    /**
     * Renderiza o combatente ativo na arena
     */
    static render(combatente, onAplicarDano, onAplicarCura, onAplicarCondicao) {
        const container = document.getElementById('combatenteAtivoContainer');
        
        if (!container) return;
        
        if (!combatente) {
            container.innerHTML = '<p class="empty-state">Nenhum combatente ativo</p>';
            return;
        }
        
        const isMorto = combatente.hp_atual <= 0;
        const isCritico = combatente.hp_atual < combatente.hp_maximo * 0.25;
        const hpPercent = (combatente.hp_atual / combatente.hp_maximo) * 100;
        
        // Cor da barra de HP
        let corHP = '#32CD32'; // Verde
        if (isCritico) {
            corHP = '#DC143C'; // Vermelho
        } else if (hpPercent < 50) {
            corHP = '#FFA500'; // Laranja
        } else if (hpPercent < 75) {
            corHP = '#FFD700'; // Amarelo
        }
        
        container.innerHTML = `
            <div class="combatente-ativo-card ${isMorto ? 'morto' : ''}">
                <!-- FOTO VERTICAL LATERAL -->
                <div class="combatente-foto-vertical">
                    ${combatente.foto_url 
                        ? `<img src="${combatente.foto_url}" alt="${combatente.nome}">` 
                        : '<div class="foto-placeholder">👤</div>'}
                </div>
                
                <!-- INFORMAÇÕES PRINCIPAIS -->
                <div class="combatente-conteudo">
                    <!-- HEADER -->
                    <div class="combatente-header-ativo">
                        <div>
                            <h2>${combatente.nome}</h2>
                            <span class="badge badge-${combatente.tipo}">${combatente.tipo}</span>
                            <span class="combatente-classe">${combatente.classe} - Nível ${combatente.nivel}</span>
                        </div>
                    </div>
                    
                    <!-- GRID PRINCIPAL -->
                    <div class="combatente-grid-principal">
                        <!-- SEÇÃO HP -->
                        <div class="secao-hp">
                            <h3>❤️ Pontos de Vida</h3>
                            <div class="hp-display">
                                <div class="hp-bar-grande">
                                    <div class="hp-fill-grande" style="width: ${hpPercent}%; background: ${corHP};"></div>
                                </div>
                                <div class="hp-valor-grande ${isCritico ? 'hp-critical-text' : ''}">
                                    ${combatente.hp_atual} / ${combatente.hp_maximo}
                                </div>
                            </div>
                            
                            <div class="hp-acoes">
                                <div class="hp-input-group">
                                    <input 
                                        type="number" 
                                        id="inputDanoAtivo" 
                                        class="input-hp" 
                                        placeholder="Valor"
                                        min="0"
                                    >
                                    <button class="btn-dano" data-action="dano" ${isMorto ? 'disabled' : ''}>
                                        ⚔️ Aplicar Dano
                                    </button>
                                    <button class="btn-cura" data-action="cura" ${combatente.hp_atual >= combatente.hp_maximo ? 'disabled' : ''}>
                                        ✨ Aplicar Cura
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- SEÇÃO RESISTÊNCIAS -->
                        <div class="secao-resistencias">
                            <h3>🛡️ Resistências</h3>
                            <div class="resistencias-grid">
                                <div class="resistencia-item">
                                    <span class="resistencia-label">Fortitude:</span>
                                    <span class="resistencia-valor">${combatente.fortitude >= 0 ? '+' : ''}${combatente.fortitude}</span>
                                </div>
                                <div class="resistencia-item">
                                    <span class="resistencia-label">Reflexos:</span>
                                    <span class="resistencia-valor">${combatente.reflexos >= 0 ? '+' : ''}${combatente.reflexos}</span>
                                </div>
                                <div class="resistencia-item">
                                    <span class="resistencia-label">Vontade:</span>
                                    <span class="resistencia-valor">${combatente.vontade >= 0 ? '+' : ''}${combatente.vontade}</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- SEÇÃO ATRIBUTOS -->
                        <div class="secao-atributos">
                            <h3>📊 Atributos</h3>
                            <div class="atributos-compacto">
                                ${this.renderAtributo('FOR', combatente.forca)}
                                ${this.renderAtributo('DES', combatente.destreza)}
                                ${this.renderAtributo('CON', combatente.constituicao)}
                                ${this.renderAtributo('INT', combatente.inteligencia)}
                                ${this.renderAtributo('SAB', combatente.sabedoria)}
                                ${this.renderAtributo('CAR', combatente.carisma)}
                            </div>
                        </div>
                        
                        <!-- SEÇÃO AÇÕES -->
                        <div class="secao-acoes">
                            <h3>⚡ Ações</h3>
                            <button class="btn-condicao" data-action="condicao">
                                🎭 Aplicar Condição
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Event listeners
        const btnDano = container.querySelector('[data-action="dano"]');
        const btnCura = container.querySelector('[data-action="cura"]');
        const btnCondicao = container.querySelector('[data-action="condicao"]');
        const inputDano = container.querySelector('#inputDanoAtivo');
        
        if (btnDano) {
            btnDano.addEventListener('click', () => {
                const valor = parseInt(inputDano.value);
                if (!valor || valor <= 0) {
                    if (window.Toast?.error) {
                        window.Toast.error('Digite um valor válido para aplicar dano.');
                    }
                    return;
                }
                onAplicarDano(combatente.id, valor);
                inputDano.value = '';
            });
        }
        
        if (btnCura) {
            btnCura.addEventListener('click', () => {
                const valor = parseInt(inputDano.value);
                if (!valor || valor <= 0) {
                    if (window.Toast?.error) {
                        window.Toast.error('Digite um valor válido para aplicar cura.');
                    }
                    return;
                }
                onAplicarCura(combatente.id, valor);
                inputDano.value = '';
            });
        }
        
        if (btnCondicao) {
            btnCondicao.addEventListener('click', () => {
                onAplicarCondicao(combatente.id);
            });
        }
    }
    
    /**
     * Renderiza um atributo compacto
     */
    static renderAtributo(nome, valor) {
        const modificador = Math.floor((valor - 10) / 2);
        const modTexto = modificador >= 0 ? `+${modificador}` : `${modificador}`;
        
        return `
            <div class="atributo-compacto">
                <span class="atributo-nome">${nome}</span>
                <span class="atributo-valor">${valor}</span>
                <span class="atributo-mod">${modTexto}</span>
            </div>
        `;
    }
}