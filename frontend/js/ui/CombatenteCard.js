/*
   CombatenteCard.js
   SRP: renderizar card visual de combatente
   ✅ import AuthService — sem depender de window global
*/

import { AuthService } from '../services/AuthService.js';

export class CombatenteCard {

    static render(combatente, selecionado, onToggle) {
        const card = document.createElement('div');
        card.className = 'combatente-card' + (selecionado ? ' selecionado' : '');

        const podeVerStats    = AuthService.podeVerStatsDe(combatente.tipo);
        const hpTexto         = podeVerStats ? combatente.hp_maximo : '???';
        const iniciativaTexto = podeVerStats ? combatente.iniciativa : '???';

        card.innerHTML = `
            <div class="card-foto-wrapper">
                ${combatente.foto_url
                    ? `<img src="${combatente.foto_url}"
                            alt="${combatente.nome}"
                            class="card-foto"
                            onerror="this.style.display='none';
                                     this.nextElementSibling.style.display='flex'">`
                    : ''}
                <div class="card-foto-placeholder"
                     style="${combatente.foto_url ? 'display:none' : ''}">
                    ${CombatenteCard._emojiTipo(combatente.tipo)}
                </div>
            </div>

            <div class="card-info">
                <div class="card-header">
                    <span class="card-nome">${combatente.nome}</span>
                    <span class="badge badge-${combatente.tipo}">${combatente.tipo}</span>
                </div>

                <div class="card-meta">
                    ${combatente.classe ? `<span class="card-classe">${combatente.classe}</span>` : ''}
                    ${combatente.raca   ? `<span class="card-raca">${combatente.raca}</span>`     : ''}
                </div>

                <div class="card-stats">
                    <div class="card-stat">
                        <span class="card-stat-label">HP</span>
                        <span class="card-stat-valor ${podeVerStats ? '' : 'stat-oculto'}">
                            ${hpTexto}
                        </span>
                    </div>
                    <div class="card-stat">
                        <span class="card-stat-label">Iniciativa</span>
                        <span class="card-stat-valor ${podeVerStats ? '' : 'stat-oculto'}">
                            ${iniciativaTexto}
                        </span>
                    </div>
                    <div class="card-stat">
                        <span class="card-stat-label">Nível</span>
                        <span class="card-stat-valor">${combatente.nivel || 1}</span>
                    </div>
                </div>
            </div>

            <button class="btn-selecionar ${selecionado ? 'selecionado' : ''}">
                ${selecionado ? '✓ Selecionado' : '+ Selecionar'}
            </button>
        `;

        card.addEventListener('click', () => onToggle(combatente.id));
        card.querySelector('.btn-selecionar')
            .addEventListener('click', (e) => {
                e.stopPropagation();
                onToggle(combatente.id);
            });

        return card;
    }

    static renderSelecionado(combatente, onRemover, onAtualizarHP, onAtualizarIniciativa) {
        const card     = document.createElement('div');
        card.className = 'combatente-selecionado-card';

        const podeVerStats = AuthService.podeVerStatsDe(combatente.tipo);
        const isMestre     = AuthService.isMestre();

        card.innerHTML = `
            <div class="selecionado-header">
                <div class="selecionado-identidade">
                    <span class="selecionado-nome">${combatente.nome}</span>
                    <span class="badge badge-${combatente.tipo}">${combatente.tipo}</span>
                </div>
                <button class="btn-remover-selecionado" title="Remover">✕</button>
            </div>

            <div class="selecionado-stats">
                <div class="selecionado-stat-hp">
                    <span>❤️</span>
                    ${isMestre
                        ? `<input type="number"
                                  class="stat-input"
                                  value="${combatente.hp_maximo}"
                                  min="1"
                                  data-original="${combatente.hp_maximo}"
                                  title="HP Máximo">
                           <span class="stat-label">/ ${combatente.hp_atual} atual</span>`
                        : `<span class="${podeVerStats ? '' : 'stat-oculto'}">
                               ${podeVerStats ? combatente.hp_maximo : '???'}
                           </span>`
                    }
                </div>

                <div class="selecionado-stat-ini">
                    <span>🎲</span>
                    ${isMestre
                        ? `<input type="number"
                                  class="stat-input stat-input-ini"
                                  value="${combatente.iniciativa}"
                                  title="Iniciativa">`
                        : `<span class="${podeVerStats ? '' : 'stat-oculto'}">
                               ${podeVerStats ? combatente.iniciativa : '???'}
                           </span>`
                    }
                </div>
            </div>
        `;

        card.querySelector('.btn-remover-selecionado')
            .addEventListener('click', (e) => {
                e.stopPropagation();
                onRemover(combatente.id);
            });

        if (isMestre) {
            const inputHP = card.querySelector('input[data-original]');
            if (inputHP) {
                inputHP.addEventListener('change', () =>
                    onAtualizarHP(combatente.id, combatente.hp_atual, parseInt(inputHP.value) || 1)
                );
            }
            const inputIni = card.querySelector('.stat-input-ini');
            if (inputIni) {
                inputIni.addEventListener('change', () =>
                    onAtualizarIniciativa(combatente.id, parseInt(inputIni.value) || 0)
                );
            }
        }

        return card;
    }

    static _emojiTipo(tipo) {
        const mapa = { jogador: '🧙', monstro: '👹', npc: '🤝' };
        return mapa[tipo] || '⚔️';
    }
}