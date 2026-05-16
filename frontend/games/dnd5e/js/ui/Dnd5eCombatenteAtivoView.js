/**
 * Painel do combatente ativo na arena D&D 5e (layout alinhado ao dnd35).
 */
export class Dnd5eCombatenteAtivoView {
    static render(combatente, catalogoCondicoes, onDano, onCura, onCondicao) {
        const container = document.getElementById('combatenteAtivoContainer');
        if (!container) return;

        if (!combatente) {
            container.innerHTML = '<p class="empty-state">Nenhum combatente ativo</p>';
            return;
        }

        const hpMax = combatente.hp_maximo || 1;
        const hpAtual = combatente.hp_atual ?? 0;
        const hpPct = Math.max(0, Math.min(100, (hpAtual / hpMax) * 100));
        const isCritico = hpAtual > 0 && hpAtual < hpMax * 0.25;
        let corHP = '#32CD32';
        if (isCritico) corHP = '#DC143C';
        else if (hpPct < 50) corHP = '#FFA500';
        else if (hpPct < 75) corHP = '#FFD700';

        const condicoes = combatente.condicoes || [];
        const condHtml = condicoes.length
            ? `<div class="dnd5e-cond-list">${condicoes
                  .map((c) => {
                      const nome =
                          (catalogoCondicoes || []).find((x) => x.slug === c.slug)?.nome ||
                          c.slug;
                      return `<span class="badge-condicao-arena">${nome}</span>`;
                  })
                  .join('')}</div>`
            : '<span class="ficha-vazio">Sem condições</span>';

        const fotoHtml = combatente.foto_url
            ? `<img src="${combatente.foto_url}" alt="${combatente.nome}">`
            : '<div class="foto-placeholder">👤</div>';

        const saves = combatente.salvamentos || [];
        const savesHtml = saves.length
            ? saves
                  .map(
                      (s) =>
                          `<div class="resistencia-item"><span class="resistencia-label">${s.label}:</span><span class="resistencia-valor">${s.bonus >= 0 ? '+' : ''}${s.bonus}</span></div>`
                  )
                  .join('')
            : '<p class="ficha-vazio">—</p>';

        container.innerHTML = `
            <div class="combatente-ativo-card">
                <div class="combatente-foto-vertical">${fotoHtml}</div>
                <div class="combatente-conteudo">
                    <div class="combatente-header-ativo">
                        <div>
                            <h2>${combatente.nome}</h2>
                            <span class="badge badge-${combatente.tipo || 'jogador'}">${combatente.tipo || 'jogador'}</span>
                            <span class="combatente-classe">${combatente.classe_label || '—'} · Nível ${combatente.nivel || 1}</span>
                        </div>
                    </div>
                    <div class="combatente-grid-principal">
                        <div class="secao-hp">
                            <h3>❤️ Pontos de vida</h3>
                            <div class="hp-display">
                                <div class="hp-bar-grande">
                                    <div class="hp-fill-grande" style="width:${hpPct}%;background:${corHP}"></div>
                                </div>
                                <div class="hp-valor-grande ${isCritico ? 'hp-critical-text' : ''}">${hpAtual} / ${hpMax}</div>
                            </div>
                            <div class="hp-acoes">
                                <div class="hp-input-group">
                                    <input type="number" id="inputDanoAtivo" class="input-hp" placeholder="Valor" min="0" />
                                    <button type="button" class="btn-dano" data-action="dano">⚔️ Dano</button>
                                    <button type="button" class="btn-cura" data-action="cura">✨ Cura</button>
                                </div>
                            </div>
                            <p class="dnd5e-arena-stat-line">CA <strong>${combatente.ca ?? '—'}</strong> · Iniciativa <strong>${combatente.iniciativa ?? '—'}</strong></p>
                        </div>
                        <div class="secao-resistencias">
                            <h3>🛡️ Salvamentos</h3>
                            <div class="resistencias-grid">${savesHtml}</div>
                        </div>
                        <div class="secao-atributos">
                            <h3>📊 Atributos</h3>
                            <div class="atributos-compacto">
                                ${Dnd5eCombatenteAtivoView._attr('FOR', combatente.forca)}
                                ${Dnd5eCombatenteAtivoView._attr('DES', combatente.destreza)}
                                ${Dnd5eCombatenteAtivoView._attr('CON', combatente.constituicao)}
                                ${Dnd5eCombatenteAtivoView._attr('INT', combatente.inteligencia)}
                                ${Dnd5eCombatenteAtivoView._attr('SAB', combatente.sabedoria)}
                                ${Dnd5eCombatenteAtivoView._attr('CAR', combatente.carisma)}
                            </div>
                        </div>
                        <div class="secao-acoes">
                            <h3>🔮 Condições</h3>
                            <div class="dnd5e-cond-badges-wrap">${condHtml}</div>
                            <button type="button" class="btn-condicao" data-action="condicao">🎭 Gerenciar condição</button>
                        </div>
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
    }

    static _attr(nome, valor) {
        const v = Number(valor) || 10;
        const mod = Math.floor((v - 10) / 2);
        const modTexto = mod >= 0 ? `+${mod}` : String(mod);
        return `<div class="atributo-compacto"><span class="atributo-nome">${nome}</span><span class="atributo-valor">${v}</span><span class="atributo-mod">${modTexto}</span></div>`;
    }
}
