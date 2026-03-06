/**
 * ArenaAtaquesMagias
 * SRP: renderiza as seções de Ataques e Controle de Magias na arena
 * Substitui as divs hardcode do index.html
 * Export para ES module (usado no ArenaController)
 */
export class ArenaAtaquesMagias {

    /**
     * Renderiza seção de ataques.
     * @param {Array} ataques - lista de objetos AtaqueResponse
     * @param {string} containerId - id do elemento que receberá o HTML
     */
    static renderAtaques(ataques, containerId = 'arenaAtaquesContainer') {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (!ataques || ataques.length === 0) {
            container.innerHTML = `
                <div class="arena-secao">
                    <h3 class="arena-secao-titulo">Ataques</h3>
                    <div class="arena-ataques-lista">
                        <div class="arena-ataque-header">
                            <span>Nome</span><span>Ataque</span><span>Dano</span>
                        </div>
                        <div class="arena-ataque-item arena-ataque-placeholder">
                            <span>— Nenhum ataque cadastrado —</span>
                        </div>
                    </div>
                </div>`;
            return;
        }

        const linhas = ataques.map(a => `
            <div class="arena-ataque-item">
                <span>${a.nome}</span>
                <span>${a.bonus_ataque}</span>
                <span>${a.dano}${a.tipo_dano ? ` <small>(${a.tipo_dano})</small>` : ''}</span>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="arena-secao">
                <h3 class="arena-secao-titulo">Ataques</h3>
                <div class="arena-ataques-lista">
                    <div class="arena-ataque-header">
                        <span>Nome</span><span>Ataque</span><span>Dano</span>
                    </div>
                    ${linhas}
                </div>
            </div>`;
    }

    /**
     * Renderiza seção de controle de magias.
     * @param {Array}  slots       - lista de MagiaSlotResponse
     * @param {string} containerId - id do elemento que receberá o HTML
     * @param {Function} onUsadosChange - callback(slotId, novoUsados)
     */
    static renderMagias(slots, containerId = 'arenaMagiasContainer',
                        onUsadosChange = null) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Garante níveis 0–9 mesmo que o banco só tenha os preenchidos
        const grid = Array.from({ length: 10 }, (_, i) => {
            const slot = slots?.find(s => s.nivel === i);
            return { nivel: i, id: slot?.id ?? null,
                     total: slot?.total ?? 0, usados: slot?.usados ?? 0 };
        });

        const linhas = grid.map(s => `
            <div class="arena-magia-linha" data-nivel="${s.nivel}">
                <span class="arena-magia-nivel">NÍV ${s.nivel}</span>
                <div class="arena-magia-controle">
                    <button class="arena-magia-btn"
                            data-slot-id="${s.id}"
                            data-acao="diminuir"
                            data-nivel="${s.nivel}"
                            ${s.total === 0 ? 'disabled' : ''}>−</button>
                    <span class="arena-magia-valor"
                          data-nivel="${s.nivel}">${s.usados}</span>
                    <button class="arena-magia-btn"
                            data-slot-id="${s.id}"
                            data-acao="aumentar"
                            data-nivel="${s.nivel}"
                            ${s.total === 0 ? 'disabled' : ''}>+</button>
                </div>
                <span class="arena-magia-usados"
                      data-nivel-total="${s.nivel}">${s.total}</span>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="arena-secao">
                <h3 class="arena-secao-titulo">Controle de Magias</h3>
                <div class="arena-magias-grid">${linhas}</div>
            </div>`;

        // Eventos dos botões +/−
        if (onUsadosChange) {
            container.querySelectorAll('.arena-magia-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const nivel   = parseInt(btn.dataset.nivel);
                    const slotId  = btn.dataset.slotId !== 'null'
                                    ? parseInt(btn.dataset.slotId) : null;
                    const acao    = btn.dataset.acao;
                    const spanVal = container.querySelector(`[data-nivel="${nivel}"]`);
                    const spanTot = container.querySelector(`[data-nivel-total="${nivel}"]`);
                    const total   = parseInt(spanTot?.textContent || 0);
                    let   usados  = parseInt(spanVal?.textContent || 0);

                    if (acao === 'aumentar' && usados < total) usados++;       // ← < literal
                    else if (acao === 'diminuir' && usados > 0) usados--;
                    else return;

                    if (spanVal) spanVal.textContent = usados;
                    onUsadosChange(slotId, nivel, usados);
                });
            });
        }
    }
}