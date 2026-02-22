/**
 * CondicaoUI
 * SOLID: SRP - apenas renderização de UI relacionada a condições
 */
export class CondicaoUI {

    /**
     * Renderiza a lista de condições ativas na div .arena-condicoes-lista
     * @param {Array}    condicoes    - lista de objetos { id, nome, efeito }
     * @param {number}   combatenteId - ID do combatente atual
     * @param {Function} onRemover    - callback(combatenteId, condicaoId)
     */
    renderizarCondicoesAtivas(condicoes, combatenteId, onRemover) {
        const container = document.querySelector('.arena-condicoes-lista');
        if (!container) return;

        container.innerHTML = '';

        if (!condicoes.length) {
            container.innerHTML = '<span class="arena-condicao-vazia">Nenhuma condição ativa</span>';
            return;
        }

        condicoes.forEach(c => {
            const slug = c.nome
                .toLowerCase()
                .normalize('NFD')
                .replace(/[\u0300-\u036f]/g, '')
                .replace(/\s+/g, '-');

            const span         = document.createElement('span');
            span.className     = `arena-condicao arena-condicao-${slug}`;
            span.dataset.id    = c.id;
            span.title         = c.efeito;

            span.innerHTML = `
                ${c.nome}
                <button class="btn-remover-condicao" title="Remover ${c.nome}" data-id="${c.id}">✕</button>
            `;

            span.querySelector('.btn-remover-condicao').addEventListener('click', (e) => {
                e.stopPropagation();
                onRemover(combatenteId, c.id);
            });

            container.appendChild(span);
        });
    }

    /**
     * Renderiza badges de condição no card da ordem de iniciativa
     * @param {HTMLElement} cardEl    - elemento do card
     * @param {Array}       condicoes - lista de condições ativas
     */
    renderizarBadgesOrdem(cardEl, condicoes) {
        const wrapper = cardEl.querySelector('.badges-condicao-ordem-wrapper');
        if (!wrapper) return;

        wrapper.innerHTML = '';
        if (!condicoes.length) return;

        const visiveis = condicoes.slice(0, 3);
        const extras   = condicoes.length - visiveis.length;

        visiveis.forEach(c => {
            const badge       = document.createElement('span');
            badge.className   = 'badge-condicao-ordem';
            badge.textContent = c.nome.slice(0, 3).toUpperCase();
            badge.title       = c.efeito;
            wrapper.appendChild(badge);
        });

        if (extras > 0) {
            const mais       = document.createElement('span');
            mais.className   = 'badge-condicao-ordem badge-condicao-mais';
            mais.textContent = `+${extras}`;
            mais.title       = condicoes.slice(3).map(c => c.nome).join(', ');
            wrapper.appendChild(mais);
        }
    }

    /**
     * Popula o select do modal com todas as condições do catálogo
     * @param {Array} todasCondicoes - catálogo completo
     * @param {Array} ativas         - condições já ativas (para desabilitar)
     */
    popularSelectModal(todasCondicoes, ativas = []) {
        const select = document.getElementById('select-condicao');
        if (!select) return;

        const ativasIds    = new Set(ativas.map(c => c.id));
        select.innerHTML   = '<option value="">Selecione uma condição...</option>';

        todasCondicoes.forEach(c => {
            const opt       = document.createElement('option');
            opt.value       = c.id;
            opt.textContent = c.nome;
            opt.title       = c.efeito;
            if (ativasIds.has(c.id)) {
                opt.disabled    = true;
                opt.textContent += ' ✓';
            }
            select.appendChild(opt);
        });
    }

    /**
     * Exibe o efeito da condição selecionada no modal
     * @param {Array}  todasCondicoes
     * @param {number} condicaoId
     */
    mostrarEfeitoNoModal(todasCondicoes, condicaoId) {
        const descEl = document.getElementById('condicao-descricao');
        if (!descEl) return;

        const c            = todasCondicoes.find(c => c.id === Number(condicaoId));
        descEl.textContent = c ? c.efeito : '';
        descEl.style.display = c ? 'block' : 'none';
    }

    abrirModal() {
        const modal = document.getElementById('modal-condicao');
        if (modal) modal.style.display = 'flex';
    }

    fecharModal() {
        const modal  = document.getElementById('modal-condicao');
        if (modal)   modal.style.display = 'none';

        const select = document.getElementById('select-condicao');
        const descEl = document.getElementById('condicao-descricao');
        if (select)  select.value        = '';
        if (descEl) { descEl.textContent = ''; descEl.style.display = 'none'; }
    }
}