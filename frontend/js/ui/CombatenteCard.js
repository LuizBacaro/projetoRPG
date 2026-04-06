/*
   CombatenteCard.js
   SRP: renderizar card visual de combatente
   ✅ HP para Jogadores
   ✅ Iniciativa para TODOS (Jogadores, NPCs, Monstros)
   ✅ Regra por TIPO — independente do perfil do usuário
*/

export class CombatenteCard {

    static render(combatente, selecionado, onToggle) {
        const card = document.createElement('div');
        card.className = 'combatente-card' + (selecionado ? ' selecionado' : '');

        const isJogador = combatente.tipo === 'jogador';

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

                ${isJogador ? `
                    <div class="card-stats">
                        <div class="card-stat">
                            <span class="card-stat-label">HP</span>
                            <span class="card-stat-valor">${combatente.hp_maximo}</span>
                        </div>
                        <div class="card-stat">
                            <span class="card-stat-label">Iniciativa</span>
                            <span class="card-stat-valor">${combatente.iniciativa}</span>
                        </div>
                        <div class="card-stat">
                            <span class="card-stat-label">Nível</span>
                            <span class="card-stat-valor">${combatente.nivel || 1}</span>
                        </div>
                    </div>
                ` : `
                    <div class="card-stats">
                        <div class="card-stat">
                            <span class="card-stat-label">Nível</span>
                            <span class="card-stat-valor">${combatente.nivel || 1}</span>
                        </div>
                    </div>
                `}
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
        const card = document.createElement('div');
        card.className = 'combatente-selecionado-card';

        // ✅ CORRIGIDO: Apenas jogadores exibem HP
        const isJogador = combatente.tipo === 'jogador';
        
        // ✅ NOVO: Todos (Jogador, NPC, Monstro) exibem Iniciativa
        const mostraIniciativa = true;

        // Mestre ainda pode editar HP/Ini
        const isMestre = window.AuthService
            ? window.AuthService.isMestre()
            : true;

        card.innerHTML = `
            <div class="selecionado-header">
                <div class="selecionado-identidade">
                    <span class="selecionado-nome">${combatente.nome}</span>
                    <span class="badge badge-${combatente.tipo}">${combatente.tipo}</span>
                </div>
                <button class="btn-remover-selecionado" title="Remover">✕</button>
            </div>

            <div class="selecionado-stats">
                ${isJogador ? `
                    <div class="selecionado-stat-hp">
                        <span>❤️</span>
                        ${isMestre
                            ? `<input type="number"
                                      class="stat-input stat-input-hp"
                                      value="${combatente.hp_maximo}"
                                      min="1"
                                      data-original="${combatente.hp_maximo}"
                                      title="HP Máximo">
                               <span class="stat-label">/ ${combatente.hp_atual} atual</span>`
                            : `<span>${combatente.hp_maximo}</span>`
                        }
                    </div>
                ` : ''}

                ${mostraIniciativa ? `
                    <div class="selecionado-stat-ini">
                        <span>🎲</span>
                        ${isMestre
                            ? `<input type="number"
                                      class="stat-input stat-input-ini"
                                      value="${combatente.iniciativa || 0}"
                                      min="-10"
                                      max="30"
                                      title="Iniciativa"
                                      data-combatente-id="${combatente.id}">`
                            : `<span>${combatente.iniciativa || 0}</span>`
                        }
                    </div>
                ` : ''}
            </div>
        `;

        // Botão Remover
        card.querySelector('.btn-remover-selecionado')
            .addEventListener('click', (e) => {
                e.stopPropagation();
                onRemover(combatente.id);
            });

        // Listener para HP (apenas Jogadores)
        if (isJogador && isMestre) {
            const inputHP = card.querySelector('.stat-input-hp');
            if (inputHP) {
                inputHP.addEventListener('change', () => {
                    const novoHP = parseInt(inputHP.value) || combatente.hp_maximo;
                    onAtualizarHP(combatente.id, combatente.hp_atual, novoHP);
                });
            }
        }

        // Listener para Iniciativa (TODOS: Jogador, NPC, Monstro)
        if (mostraIniciativa && isMestre) {
            const inputIni = card.querySelector('.stat-input-ini');
            if (inputIni) {
                inputIni.addEventListener('change', () => {
                    const novaIniciativa = parseInt(inputIni.value) || 0;
                    onAtualizarIniciativa(combatente.id, novaIniciativa);
                });
            }
        }

        return card;
    }

    static _emojiTipo(tipo) {
        const mapa = { jogador: '🧙', monstro: '👹', npc: '🤝' };
        return mapa[tipo] || '⚔️';
    }
}