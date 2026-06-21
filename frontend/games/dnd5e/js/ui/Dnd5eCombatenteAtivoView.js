import { renderAtaquesFichaHtml } from '../arena/Dnd5eArenaAtaquesHelper.js';

/**
 * Painel do combatente ativo na arena D&D 5e (layout arena-card do dnd35).
 */
export class Dnd5eCombatenteAtivoView {
    static render(
        combatente,
        catalogoCondicoes,
        onDano,
        onCura,
        onCondicao,
        onProximoTurno,
        handlers = {}
    ) {
        const container = document.getElementById('combatenteAtivoContainer');
        if (!container) return;

        if (!combatente) {
            container.innerHTML = '<p class="empty-state">Nenhum combatente ativo</p>';
            return;
        }

        const hpMax = Math.max(1, combatente.hp_maximo || 1);
        const hpAtual = Math.max(0, combatente.hp_atual ?? 0);
        const hpPct = Math.max(0, Math.min(100, (hpAtual / hpMax) * 100));
        const hpCor = hpPct > 50 ? '#4CAF50' : hpPct > 25 ? '#FF9800' : '#F44336';

        const condicoes = combatente.condicoes || [];
        const condHtml = condicoes.length
            ? condicoes
                  .map((c) => {
                      const nome =
                          (catalogoCondicoes || []).find((x) => x.slug === c.slug)?.nome ||
                          c.slug;
                      return `<span class="arena-condicao-badge">${Dnd5eCombatenteAtivoView._esc(nome)}</span>`;
                  })
                  .join('')
            : '<span class="arena-condicao-vazia">Nenhuma condição ativa</span>';

        const saves = combatente.salvamentos || [];
        const savesHtml = saves.length
            ? saves
                  .map((s) => {
                      const bonus = Number(s.bonus) || 0;
                      const txt = bonus >= 0 ? `+${bonus}` : String(bonus);
                      const label = (s.label || '—').slice(0, 6);
                      const slug = label.toLowerCase().replace(/\s+/g, '-');
                      return `<div class="arena-atributo-box" data-resistencia="${Dnd5eCombatenteAtivoView._esc(slug)}">
                        <span class="arena-atributo-nome">${Dnd5eCombatenteAtivoView._esc(label.slice(0, 3))}</span>
                        <span class="arena-atributo-valor">${txt}</span>
                    </div>`;
                  })
                  .join('')
            : `<div class="arena-atributo-box"><span class="arena-atributo-nome">—</span><span class="arena-atributo-valor">+0</span></div>`;

        const tipo = combatente.tipo || 'jogador';
        const metaClasse = [
            combatente.classe_label || combatente.classe || '—',
            `Nível ${combatente.nivel || 1}`,
        ]
            .filter(Boolean)
            .join(' · ');

        const atributosHtml = [
            ['For', combatente.forca],
            ['Des', combatente.destreza],
            ['Con', combatente.constituicao],
            ['Int', combatente.inteligencia],
            ['Sab', combatente.sabedoria],
            ['Car', combatente.carisma],
        ]
            .map(([nome, valor]) => Dnd5eCombatenteAtivoView._attrBox(nome, valor))
            .join('');

        const ini = combatente.iniciativa ?? '—';
        const statusVida = combatente.status_vida || (hpAtual > 0 ? 'vivo' : 'inconsciente');
        const morto = statusVida === 'morto';
        const estabilizado = statusVida === 'estabilizado';
        const morrendo = hpAtual === 0 && statusVida === 'inconsciente';
        const falhas = combatente.death_failures || 0;
        const sucessos = combatente.death_successes || 0;
        const eco = combatente.economia || {};
        const movRest =
            Math.max(0, (eco.velocidade_metros || 9) - (eco.movimento_usado_metros || 0));
        const luckyMax = (combatente.feats || []).some(
            (f) => String(f).toLowerCase() === 'lucky'
        )
            ? 3
            : 0;
        const luckyRest = combatente.lucky_restantes ?? luckyMax;

        const statusBadge = morto
            ? '<span class="dnd5e-status-vida dnd5e-status-morto">☠ Morto</span>'
            : estabilizado
              ? '<span class="dnd5e-status-vida dnd5e-status-estabilizado">💤 Estabilizado</span>'
              : morrendo
                ? '<span class="dnd5e-status-vida dnd5e-status-morrendo">🩸 Morrendo (0 PV)</span>'
                : '';

        let deathHtml = '';
        if (morto) {
            deathHtml = `<div class="dnd5e-arena-death-saves dnd5e-arena-death-morto">
                <p>Combatente morto — remova da ordem ou encerre o combate.</p>
            </div>`;
        } else if (estabilizado) {
            deathHtml = `<div class="dnd5e-arena-death-saves dnd5e-arena-death-estavel">
                <h3 class="arena-secao-titulo">Estabilizado</h3>
                <p class="dnd5e-death-hint">0 PV, sem salvamentos. Qualquer dano volta ao estado morrendo.</p>
            </div>`;
        } else if (morrendo) {
            deathHtml = `<div class="dnd5e-arena-death-saves">
                <h3 class="arena-secao-titulo">Salvamentos contra morte</h3>
                <p class="dnd5e-death-tracker">
                    <span class="dnd5e-death-successes" title="Sucessos">✓ ${sucessos}/3</span>
                    <span class="dnd5e-death-failures" title="Falhas">✗ ${falhas}/3</span>
                </p>
                <div class="dnd5e-death-actions">
                    <label class="dnd5e-medicina-mod-label">
                        Mod. Medicina
                        <input
                            type="number"
                            id="dnd5eModMedicina"
                            class="dnd5e-medicina-mod-input"
                            value="${combatente.mod_medicina ?? 0}"
                            step="1"
                        />
                    </label>
                    <button type="button" class="arena-btn-condicao dnd5e-btn-death-save" data-action="death-save">
                        🎲 Rolar salvamento
                    </button>
                    <button type="button" class="arena-btn-condicao dnd5e-btn-estabilizar" data-action="estabilizar-medicina">
                        🩹 Medicina (CD 10)
                    </button>
                    <button type="button" class="arena-btn-condicao dnd5e-btn-estabilizar" data-action="estabilizar-magia">
                        ✨ Magia
                    </button>
                </div>
            </div>`;
        }

        const alvosAtaque = (handlers.getAlvosAtaque?.() || []).filter((a) => a.id !== combatente.id);
        const ataquesHtml = renderAtaquesFichaHtml(
            combatente,
            alvosAtaque,
            Dnd5eCombatenteAtivoView._esc
        );

        const economiaHtml = `
            <div class="dnd5e-arena-economia">
                <h3 class="arena-secao-titulo">Economia do turno</h3>
                <div class="dnd5e-economia-chips">
                    <span class="dnd5e-eco-chip ${eco.acao_usada ? 'usado' : ''}">Ação</span>
                    <span class="dnd5e-eco-chip ${eco.bonus_acao_usada ? 'usado' : ''}">Bônus</span>
                    <span class="dnd5e-eco-chip ${eco.reacao_usada ? 'usado' : ''}">Reação</span>
                    <span class="dnd5e-eco-chip mov">Mov. ${movRest.toFixed(1)}m</span>
                    ${eco.esquivando ? '<span class="dnd5e-eco-chip usado">Esquivando</span>' : ''}
                    ${eco.desengajado ? '<span class="dnd5e-eco-chip usado">Desengajado</span>' : ''}
                    ${
                        luckyMax
                            ? `<span class="dnd5e-eco-chip mov">Lucky ${luckyRest}/${luckyMax}</span>`
                            : ''
                    }
                </div>
                <div class="dnd5e-economia-btns">
                    <button type="button" class="dnd5e-eco-btn" data-eco="acao">Ação</button>
                    <button type="button" class="dnd5e-eco-btn" data-eco="bonus_acao">Bônus</button>
                    <button type="button" class="dnd5e-eco-btn" data-eco="reacao">Reação</button>
                    <button type="button" class="dnd5e-eco-btn" data-eco="movimento">+1,5m</button>
                </div>
                <div class="dnd5e-economia-btns dnd5e-economia-phb">
                    <button type="button" class="dnd5e-eco-btn" data-eco="dash">Correr</button>
                    <button type="button" class="dnd5e-eco-btn" data-eco="dodge">Esquivar</button>
                    <button type="button" class="dnd5e-eco-btn" data-eco="disengage">Desengajar</button>
                    <button type="button" class="dnd5e-eco-btn" data-eco="help">Ajudar</button>
                    <button type="button" class="dnd5e-eco-btn" data-action="sair-alcance">Sair alcance</button>
                    ${
                        luckyMax
                            ? `<button type="button" class="dnd5e-eco-btn" data-action="lucky">Usar Lucky</button>`
                            : ''
                    }
                </div>
            </div>`;

        container.innerHTML = `
            <div class="arena-card">
                <div class="arena-header">
                    <div class="arena-header-nome">
                        <h2 class="arena-nome">
                            <span class="arena-nome-text">${Dnd5eCombatenteAtivoView._esc(combatente.nome)}</span>
                            <span class="arena-nivel">(${combatente.nivel || 1}° nível)</span>
                        </h2>
                        <span class="arena-raca-classe">
                            <span class="badge badge-${Dnd5eCombatenteAtivoView._esc(tipo)}">${Dnd5eCombatenteAtivoView._esc(tipo)}</span>
                            ${Dnd5eCombatenteAtivoView._esc(metaClasse)}
                            ${statusBadge}
                        </span>
                    </div>
                </div>

                <div class="arena-layout-principal">
                    <div class="arena-coluna-esquerda">
                        <div class="arena-linha-info">
                            <div class="arena-secao arena-secao-atributos">
                                <h3 class="arena-secao-titulo">Atributos</h3>
                                <div class="arena-atributos-grid">${atributosHtml}</div>
                            </div>
                            <div class="arena-secao arena-secao-resistencias">
                                <h3 class="arena-secao-titulo">Salvamentos</h3>
                                <div class="arena-resistencias-grid">${savesHtml}</div>
                            </div>
                            <div class="arena-secao arena-secao-condicoes">
                                <h3 class="arena-secao-titulo">Condições</h3>
                                <div class="arena-condicoes-lista">${condHtml}</div>
                                <button type="button" class="arena-btn-condicao dnd5e-btn-condicao-card" data-action="condicao">
                                    🎭 Gerenciar condição
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="arena-coluna-central dnd5e-arena-col-central">
                        <div id="dnd5eArenaMagiasHost" class="dnd5e-arena-magias-host"></div>
                        ${ataquesHtml}
                        <div class="arena-secao">
                            <h3 class="arena-secao-titulo">Ajuste rápido de PV</h3>
                            <div class="dnd5e-arena-pv-rapido">
                                <input type="number" id="inputDanoAtivo" class="dnd5e-arena-pv-input" placeholder="Valor" min="0" />
                                <button type="button" class="arena-btn-dano-cura dnd5e-arena-pv-btn" data-action="dano">⚔️ Dano</button>
                                <button type="button" class="arena-btn-condicao dnd5e-arena-pv-btn" data-action="cura">✨ Cura</button>
                            </div>
                        </div>
                        ${deathHtml}
                        ${economiaHtml}
                    </div>

                    <div class="arena-coluna-direita">
                        <div class="arena-defesa-box">
                            <div class="arena-ca-principal">
                                <span class="arena-defesa-label">CA</span>
                                <span class="arena-ca-valor">${combatente.ca ?? '—'}</span>
                            </div>
                            <div class="arena-defesa-secundaria">
                                <div class="arena-defesa-item">
                                    <span class="arena-defesa-label-sm">Iniciativa</span>
                                    <span class="arena-defesa-valor-sm">${ini}</span>
                                </div>
                            </div>
                        </div>
                        <div class="arena-pv-box">
                            <span class="arena-defesa-label">PV</span>
                            <div class="arena-pv-linha">
                                <span class="arena-pv-valor">${hpAtual} / ${hpMax}</span>
                            </div>
                            <div class="arena-hp-bar">
                                <div class="arena-hp-fill" style="width:${hpPct}%;background:${hpCor}"></div>
                            </div>
                        </div>
                        <button type="button" class="arena-btn-proximo" id="btnAvancarTurnoArena">
                            Encerrar turno
                        </button>
                    </div>
                </div>
            </div>`;

        container.querySelector('[data-action="dano"]')?.addEventListener('click', () => {
            const v = parseInt(document.getElementById('inputDanoAtivo')?.value, 10);
            if (!v || v <= 0) {
                Toast.error('Digite um valor válido para dano.');
                return;
            }
            onDano(combatente.id, v);
            document.getElementById('inputDanoAtivo').value = '';
        });
        container.querySelector('[data-action="cura"]')?.addEventListener('click', () => {
            const v = parseInt(document.getElementById('inputDanoAtivo')?.value, 10);
            if (!v || v <= 0) {
                Toast.error('Digite um valor válido para cura.');
                return;
            }
            onCura(combatente.id, v);
            document.getElementById('inputDanoAtivo').value = '';
        });
        container.querySelector('[data-action="condicao"]')?.addEventListener('click', () => {
            onCondicao(combatente.id);
        });
        container.querySelector('#btnAvancarTurnoArena')?.addEventListener('click', () => {
            onProximoTurno?.();
        });
        container.querySelector('[data-action="death-save"]')?.addEventListener('click', () => {
            handlers.onDeathSave?.(combatente.id);
        });
        const medInput = container.querySelector('#dnd5eModMedicina');
        medInput?.addEventListener('change', () => {
            handlers.onMedicinaModChange?.(combatente.id, medInput.value);
        });
        container
            .querySelector('[data-action="estabilizar-medicina"]')
            ?.addEventListener('click', () => {
                const mod = medInput ? medInput.value : combatente.mod_medicina ?? 0;
                handlers.onEstabilizar?.(combatente.id, 'medicina', mod);
            });
        container
            .querySelector('[data-action="estabilizar-magia"]')
            ?.addEventListener('click', () => {
                handlers.onEstabilizar?.(combatente.id, 'magia');
            });
        container.querySelectorAll('[data-eco]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const tipo = btn.getAttribute('data-eco');
                const metros = tipo === 'movimento' ? 1.5 : 0;
                handlers.onEconomia?.(tipo, metros);
            });
        });
        container.querySelector('[data-action="sair-alcance"]')?.addEventListener('click', () => {
            handlers.onSairAlcance?.(combatente.id);
        });
        container.querySelector('[data-action="lucky"]')?.addEventListener('click', () => {
            handlers.onUsarLucky?.(combatente.id);
        });
        container.querySelectorAll('[data-ataque-idx]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const idx = parseInt(btn.getAttribute('data-ataque-idx'), 10);
                const alvoId = container.querySelector('#dnd5eAtaqueAlvo')?.value;
                if (!alvoId) {
                    Toast.error('Selecione um alvo.');
                    return;
                }
                handlers.onAtaqueFicha?.(combatente.id, alvoId, idx);
            });
        });
    }

    static _attrBox(nome, valor) {
        const v = Number(valor) || 10;
        const mod = Math.floor((v - 10) / 2);
        const modTexto = mod >= 0 ? `+${mod}` : String(mod);
        return `<div class="arena-atributo-box">
            <span class="arena-atributo-nome">${nome}</span>
            <span class="arena-atributo-valor">${v}</span>
            <span class="arena-atributo-mod">${modTexto}</span>
        </div>`;
    }

    static _esc(str) {
        if (typeof window.escapeHtml === 'function') return window.escapeHtml(String(str ?? ''));
        return String(str ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }
}
