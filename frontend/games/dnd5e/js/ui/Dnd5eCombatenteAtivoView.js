/**
 * Painel do combatente ativo na arena D&D 5e (layout arena-card do dnd35).
 */
export class Dnd5eCombatenteAtivoView {
    static render(combatente, catalogoCondicoes, onDano, onCura, onCondicao, onProximoTurno) {
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
                        <div class="arena-secao">
                            <h3 class="arena-secao-titulo">Ajuste rápido de PV</h3>
                            <div class="dnd5e-arena-pv-rapido">
                                <input type="number" id="inputDanoAtivo" class="dnd5e-arena-pv-input" placeholder="Valor" min="0" />
                                <button type="button" class="arena-btn-dano-cura dnd5e-arena-pv-btn" data-action="dano">⚔️ Dano</button>
                                <button type="button" class="arena-btn-condicao dnd5e-arena-pv-btn" data-action="cura">✨ Cura</button>
                            </div>
                        </div>
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
