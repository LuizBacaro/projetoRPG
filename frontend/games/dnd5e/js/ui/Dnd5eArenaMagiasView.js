/**
 * Dnd5eArenaMagiasView — renderiza a secção de magias do combatente
 * ativo na arena D&D 5e seguindo o padrão visual da arena 3.5
 * (lista por nível com 🔥/↩️ para preparadores; grelha NIV 0–9 com +/-
 * para conjuradores espontâneos; chip único para Bruxo).
 *
 * SRP: apenas geração de HTML e binding de eventos. Nenhuma chamada HTTP
 * é feita aqui — o controller injecta callbacks (`onLancar`, `onRestaurar`,
 * `onSlotDelta`).
 */

import { MODO_CONJURADOR } from '../arena/Dnd5eArenaMagiasHelper.js';

const esc = (str) => {
    if (typeof window !== 'undefined' && typeof window.escapeHtml === 'function') {
        return window.escapeHtml(String(str ?? ''));
    }
    return String(str ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
};

export class Dnd5eArenaMagiasView {
    static render(grupos, modo, slotBruxo) {
        if (modo === MODO_CONJURADOR.NENHUM) {
            return '';
        }
        if (modo === MODO_CONJURADOR.BRUXO) {
            return Dnd5eArenaMagiasView._renderBruxo(grupos, slotBruxo);
        }
        if (modo === MODO_CONJURADOR.PREPARADO) {
            return Dnd5eArenaMagiasView._renderPreparado(grupos);
        }
        return Dnd5eArenaMagiasView._renderConhecido(grupos);
    }

    static bindEvents(container, callbacks) {
        if (!container) return;
        const { onLancar, onRestaurar, onSlotDelta } = callbacks || {};

        container.querySelectorAll('.arena-prep-btn').forEach((btn) => {
            btn.addEventListener('click', () => {
                const magiaId = Number(btn.getAttribute('data-magia-id'));
                const nivel = Number(btn.getAttribute('data-nivel'));
                const acao = btn.getAttribute('data-acao') || 'usar';
                if (!Number.isFinite(magiaId)) return;
                if (acao === 'restaurar' && typeof onRestaurar === 'function') {
                    onRestaurar(magiaId, nivel);
                } else if (typeof onLancar === 'function') {
                    onLancar(magiaId, nivel);
                }
            });
        });

        container.querySelectorAll('.arena-magia-btn').forEach((btn) => {
            btn.addEventListener('click', () => {
                const nivel = Number(btn.getAttribute('data-nivel'));
                const acao = btn.getAttribute('data-acao');
                if (!Number.isFinite(nivel) || !acao) return;
                const delta = acao === 'aumentar' ? 1 : -1;
                if (typeof onSlotDelta === 'function') {
                    onSlotDelta(nivel, delta);
                }
            });
        });
    }

    // ---------- helpers internos ----------

    static _renderPreparado(grupos) {
        const niveis = Object.keys(grupos)
            .map(Number)
            .filter((n) => Number.isFinite(n))
            .sort((a, b) => a - b);

        if (!niveis.length) {
            return `
                <div class="arena-secao">
                    <h3 class="arena-secao-titulo">🔮 Magias Preparadas</h3>
                    <div class="arena-magia-vazio">
                        Nenhuma magia preparada hoje.<br>
                        <small>Abra o Grimório na ficha do personagem.</small>
                    </div>
                </div>`;
        }

        let html =
            '<div class="arena-secao">' +
            '<h3 class="arena-secao-titulo">🔮 Magias Preparadas</h3>' +
            '<div class="arena-magias-preparadas-lista">';

        for (const nivel of niveis) {
            const grupo = grupos[nivel];
            html += Dnd5eArenaMagiasView._renderGrupoPreparado(grupo);
        }

        html += '</div></div>';
        return html;
    }

    static _renderConhecido(grupos) {
        const niveis = Object.keys(grupos)
            .map(Number)
            .filter((n) => Number.isFinite(n))
            .sort((a, b) => a - b);

        let html =
            '<div class="arena-secao">' +
            '<h3 class="arena-secao-titulo">📖 Magias Conhecidas</h3>';

        if (!niveis.length) {
            html +=
                '<div class="arena-magia-vazio">' +
                'Nenhuma magia registada no grimório.<br>' +
                '<small>Abra o Grimório na ficha do personagem.</small>' +
                '</div></div>';
            return html;
        }

        html += '<div class="arena-magias-preparadas-lista">';
        for (const nivel of niveis) {
            html += Dnd5eArenaMagiasView._renderGrupoPreparado(grupos[nivel]);
        }
        html += '</div></div>';
        return html;
    }

    static _renderBruxo(grupos, slotBruxo) {
        let html =
            '<div class="arena-secao">' +
            '<h3 class="arena-secao-titulo">📜 Magias do Pacto</h3>';

        if (slotBruxo && slotBruxo.total > 0) {
            const corDisp =
                slotBruxo.disponiveis === 0
                    ? '#f87171'
                    : slotBruxo.usados > 0
                      ? '#facc15'
                      : '#4ade80';
            const disAumentar = slotBruxo.usados >= slotBruxo.total ? 'disabled' : '';
            const disDiminuir = slotBruxo.usados <= 0 ? 'disabled' : '';
            html +=
                '<div class="dnd5e-arena-bruxo-slot">' +
                `<span class="arena-prep-nivel-label">Nv ${slotBruxo.nivel}</span>` +
                `<button class="arena-magia-btn arena-magia-btn-diminuir" data-acao="diminuir" data-nivel="${slotBruxo.nivel}" ${disDiminuir}>−</button>` +
                `<span class="arena-magia-valor" data-nivel="${slotBruxo.nivel}" style="color:${corDisp}">${slotBruxo.disponiveis}/${slotBruxo.total}</span>` +
                `<button class="arena-magia-btn arena-magia-btn-aumentar" data-acao="aumentar" data-nivel="${slotBruxo.nivel}" ${disAumentar}>+</button>` +
                '</div>';
        }

        const niveis = Object.keys(grupos)
            .map(Number)
            .filter((n) => Number.isFinite(n))
            .sort((a, b) => a - b);

        if (!niveis.length) {
            html +=
                '<div class="arena-magia-vazio">' +
                'Nenhuma magia registada no grimório.<br>' +
                '<small>Abra o Grimório na ficha do personagem.</small>' +
                '</div></div>';
            return html;
        }

        html += '<div class="arena-magias-preparadas-lista">';
        for (const nivel of niveis) {
            const grupo = { ...grupos[nivel] };
            // No bruxo o contador do grupo vem do slot único; oculta nele.
            grupo._ocultarContador = true;
            html += Dnd5eArenaMagiasView._renderGrupoPreparado(grupo);
        }
        html += '</div></div>';
        return html;
    }

    static _renderGrupoPreparado(grupo) {
        const nivel = Number(grupo.nivel) || 0;
        const truque = nivel === 0;
        const disponiveis = Math.max(0, grupo.disponiveis || 0);
        const total = Math.max(0, grupo.total || 0);

        let cabecalho =
            '<div class="arena-prep-nivel-header">' +
            `<span class="arena-prep-nivel-label">${
                truque ? 'TRUQUES' : `NIV ${nivel}`
            }</span>`;
        if (!truque && !grupo._ocultarContador) {
            const corDisp =
                disponiveis === 0
                    ? '#f87171'
                    : grupo.usados > 0
                      ? '#facc15'
                      : '#4ade80';
            cabecalho +=
                `<span class="arena-prep-disponiveis" style="color:${corDisp}">` +
                `${disponiveis}/${total}` +
                '</span>';
        }
        cabecalho += '</div>';

        let linhas = '';
        for (const m of grupo.magias || []) {
            const usada = !truque && m.lancada;
            const acaoBtn = usada ? 'restaurar' : 'usar';
            const icone = truque ? '✨' : usada ? '↩️' : '🔥';
            const titulo = truque
                ? 'Conjurar truque (sem gasto)'
                : usada
                  ? 'Restaurar (devolver espaço)'
                  : 'Lançar magia (gastar espaço)';
            linhas +=
                `<div class="arena-prep-magia-row ${usada ? 'arena-prep-usada' : ''}">` +
                `<span class="arena-prep-nome ${usada ? 'arena-prep-nome-usada' : ''}" data-magia-id="${m.magia_id}">` +
                esc(m.magia_nome) +
                '</span>';
            if (m.magia_escola) {
                linhas += `<span class="arena-prep-escola">${esc(m.magia_escola)}</span>`;
            }
            linhas +=
                `<button class="arena-prep-btn ${usada ? 'arena-prep-btn-usada' : ''}"` +
                ` data-magia-id="${m.magia_id}" data-nivel="${nivel}" data-acao="${acaoBtn}"` +
                ` title="${titulo}">${icone}</button>` +
                '</div>';
        }

        return (
            `<div class="arena-magia-preparada-nivel" data-nivel="${nivel}">` +
            cabecalho +
            linhas +
            '</div>'
        );
    }
}
