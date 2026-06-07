/**
 * Ataques da ficha na arena — parse de bônus/dano e execução via API de combate.
 */

export function parseBonusAtaque(valor) {
    const s = String(valor ?? '').trim();
    const m = s.match(/[+-]?\d+/);
    return m ? parseInt(m[0], 10) : 0;
}

/** Separa expressão "1d8+3" em dados e modificador para a API /dano. */
export function parseDanoFicha(expressao) {
    const s = String(expressao || '').trim().toLowerCase();
    const m = s.match(/^(\d+d\d+)([+-]\d+)?$/);
    if (!m) {
        return { dano: s || '1d4', mod: 0 };
    }
    return {
        dano: m[1],
        mod: m[2] ? parseInt(m[2], 10) : 0,
    };
}

export function renderAtaquesFichaHtml(combatente, alvos, esc) {
    const ataques = combatente?.ataques || [];
    const fn = esc || ((x) => String(x ?? ''));

    if (!ataques.length) {
        return `<div class="arena-secao dnd5e-arena-secao-ataques">
            <h3 class="arena-secao-titulo">⚔️ Ataques</h3>
            <div class="arena-ataques-lista">
                <div class="arena-ataque-item arena-ataque-placeholder">
                    <span>Cadastre ataques na ficha do personagem</span>
                </div>
            </div>
        </div>`;
    }

    const alvosHtml =
        alvos.length > 0
            ? `<label class="dnd5e-arena-alvo-label">Alvo do ataque
                <select id="dnd5eAtaqueAlvo" class="dnd5e-arena-alvo-select">
                    ${alvos
                        .map(
                            (a) =>
                                `<option value="${fn(a.id)}">${fn(a.nome)} (CA ${a.ca ?? '—'})</option>`
                        )
                        .join('')}
                </select>
               </label>`
            : `<p class="dnd5e-arena-alvo-vazio">Adicione outro combatente para atacar.</p>`;

    const linhas = ataques
        .map((a, i) => {
            const tipo = a.tipo_dano ? ` (${a.tipo_dano})` : '';
            const disabled = alvos.length ? '' : ' disabled';
            return `<button type="button" class="arena-ataque-item dnd5e-arena-ataque-btn" data-ataque-idx="${i}"${disabled}>
                <span>${fn(a.nome) || '—'}</span>
                <span>${fn(a.bonus_ataque) || '+0'}</span>
                <span>${fn(a.dano) || '—'}${fn(tipo)}</span>
                <span class="dnd5e-arena-ataque-roll" aria-hidden="true">🎲</span>
            </button>`;
        })
        .join('');

    return `<div class="arena-secao dnd5e-arena-secao-ataques">
        <h3 class="arena-secao-titulo">⚔️ Ataques</h3>
        ${alvosHtml}
        <div class="arena-ataques-lista">
            <div class="arena-ataque-header dnd5e-arena-ataque-header">
                <span>Nome</span><span>Ataque</span><span>Dano</span><span></span>
            </div>
            ${linhas}
        </div>
    </div>`;
}
