/**
 * CombatenteCard
 * SRP: apenas renderizar cards de combatente na tela de configuração
 * Edição foi movida para o Dashboard — este componente não tem mais responsabilidade de editar
 */
import { Combatente } from '../models/Combatente.js';

export class CombatenteCard {

    /**
     * Renderiza card de combatente disponível (tela de configuração)
     * REMOVIDO: parâmetro onEdit e botão "✏️ Editar"
     */
    static render(combatente, selecionado = false, onSelect) {
        const card       = document.createElement('div');
        card.className   = `combatente-card ${selecionado ? 'selected' : ''}`;
        card.dataset.id  = combatente.id;
        card.style.cursor = 'pointer';

        card.innerHTML = `
            <div style="display:flex; gap:1rem; align-items:center; flex:1;">
                ${combatente.foto_url
                    ? `<img src="${combatente.foto_url}" alt="${combatente.nome}" class="combatente-foto">`
                    : '<div class="combatente-foto combatente-foto-placeholder">👤</div>'
                }
                <div class="combatente-info">
                    <div class="combatente-header">
                        <h3>${combatente.nome}</h3>
                        <span class="badge ${combatente.getBadgeClass()}">${combatente.tipo}</span>
                    </div>
                    <p class="combatente-classe">${combatente.classe}</p>
                    <div class="combatente-stats">
                        <div class="stat">
                            <span class="stat-label">HP:</span>
                            <span class="stat-value">${combatente.hp_atual}/${combatente.hp_maximo}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Ini:</span>
                            <span class="stat-value">${combatente.iniciativa}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Nv:</span>
                            <span class="stat-value">${combatente.nivel}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Clique em qualquer parte do card seleciona/desseleciona
        card.addEventListener('click', () => onSelect(combatente.id));

        return card;
    }

    /**
     * Renderiza card de combatente selecionado (painel direito)
     */
    static renderSelecionado(combatente, onRemove, onUpdateHP, onUpdateIni) {
        const isCritico  = combatente.estaCritico();
        const card       = document.createElement('div');
        card.className   = 'combatente-selecionado-card';

        card.innerHTML = `
            <div class="selecionado-foto-container">
                ${combatente.foto_url
                    ? `<img src="${combatente.foto_url}" alt="${combatente.nome}" class="selecionado-foto">`
                    : '<div class="selecionado-foto-placeholder">👤</div>'
                }
            </div>
            <div class="selecionado-info">
                <div class="selecionado-header">
                    <h4>${combatente.nome}</h4>
                    <span class="badge ${combatente.getBadgeClass()}">${combatente.tipo}</span>
                </div>
                <div class="selecionado-stats">
                    <div class="selecionado-stat-hp">
                        <span class="stat-icon">❤️</span>
                        <span class="stat-label">HP:</span>
                        <span class="stat-value ${isCritico ? 'hp-critical-text' : ''}">${combatente.hp_atual}</span>
                        <span class="stat-separator">/</span>
                        <input
                            type="number"
                            class="hp-input-selecionado"
                            value="${combatente.hp_maximo}"
                            min="1"
                            data-id="${combatente.id}"
                            data-field="hp"
                            title="HP Máximo (editável)"
                        />
                    </div>
                    <div class="selecionado-stat-ini">
                        <span class="stat-icon">⚡</span>
                        <span class="stat-label">Ini:</span>
                        <input
                            type="number"
                            class="ini-input-selecionado"
                            value="${combatente.iniciativa}"
                            min="0"
                            data-id="${combatente.id}"
                            data-field="iniciativa"
                            title="Iniciativa (editável)"
                        />
                    </div>
                </div>
            </div>
            <button class="btn-remove-selecionado" title="Remover">✕</button>
        `;

        // Event listeners
        card.querySelector('.hp-input-selecionado').addEventListener('change', (e) => {
            e.stopPropagation();
            onUpdateHP(combatente.id, combatente.hp_atual, parseInt(e.target.value));
        });

        card.querySelector('.ini-input-selecionado').addEventListener('change', (e) => {
            e.stopPropagation();
            onUpdateIni(combatente.id, parseInt(e.target.value));
        });

        card.querySelector('.btn-remove-selecionado')
            .addEventListener('click', () => onRemove(combatente.id));

        return card;
    }
}