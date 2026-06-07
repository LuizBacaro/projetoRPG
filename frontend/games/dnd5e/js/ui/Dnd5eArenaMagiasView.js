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

const HAB_LABEL = { int: 'INT', wis: 'SAB', cha: 'CAR', dex: 'DES' };
const MODO_LABEL = {
    preparado: 'Preparado',
    conhecido: 'Conhecido',
    bruxo: 'Pacto (Bruxo)',
};

export class Dnd5eArenaMagiasView {
    static render(grupos, modo, slotBruxo, estado = null) {
        if (modo === MODO_CONJURADOR.NENHUM) {
            return '';
        }
        const perfil = Dnd5eArenaMagiasView._renderPerfil(estado);
        if (modo === MODO_CONJURADOR.BRUXO) {
            return perfil + Dnd5eArenaMagiasView._renderBruxo(grupos, slotBruxo);
        }
        if (modo === MODO_CONJURADOR.PREPARADO) {
            return perfil + Dnd5eArenaMagiasView._renderPreparado(grupos);
        }
        return perfil + Dnd5eArenaMagiasView._renderConhecido(grupos);
    }

    static _renderPerfil(estado) {
        if (!estado) return '';
        const hab = HAB_LABEL[estado.habilidade_primaria] || String(estado.habilidade_primaria || '').toUpperCase();
        const modo = MODO_LABEL[estado.modo_lista] || estado.modo_lista || '—';
        const maxNiv = estado.max_nivel_magia ?? '—';
        const truques = estado.truque_multiplicador_dados || 1;
        const partes = [`${modo}`, `CD: ${hab}`, `máx. ${maxNiv}º`, `truques ×${truques}`];
        if (estado.magias_conhecidas_max != null) {
            partes.push(`conhecidas ${estado.magias_conhecidas_atual ?? 0}/${estado.magias_conhecidas_max}`);
        }
        if (estado.magias_preparadas_max != null) {
            const prep = (estado.magias_preparadas_ids || []).length;
            partes.push(`preparadas ${prep}/${estado.magias_preparadas_max}`);
        }
        if (estado.recupera_slots_repouso_curto) {
            partes.push('repouso curto ↻');
        }
        if (estado.magia_concentracao_id) {
            partes.push(`concentrando #${estado.magia_concentracao_id}`);
        }
        return `<p class="dnd5e-conj-perfil">${esc(partes.join(' · '))}</p>`;
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
            const semEspacos = !truque && disponiveis <= 0;
            const marcouSessao = Boolean(m.lancada);
            const acaoBtn = semEspacos ? 'restaurar' : 'usar';
            const icone = truque
                ? marcouSessao
                    ? '↩️'
                    : '✨'
                : semEspacos
                  ? '↩️'
                  : '🔥';
            const titulo = truque
                ? marcouSessao
                    ? 'Limpar marcação do truque (at-will — não gasta espaço)'
                    : 'Conjurar truque (at-will — sem gasto de espaço)'
                : semEspacos
                  ? 'Devolver um espaço deste nível'
                  : marcouSessao
                    ? `Lançar novamente (${disponiveis} espaço(s) de NIV ${nivel})`
                    : `Lançar magia (gasta 1 espaço de NIV ${nivel})`;
            linhas +=
                `<div class="arena-prep-magia-row ${marcouSessao ? 'arena-prep-marcada' : ''} ${semEspacos ? 'arena-prep-sem-espaco' : ''}">` +
                `<span class="arena-prep-nome ${marcouSessao ? 'arena-prep-nome-marcada' : ''}" data-magia-id="${m.magia_id}">` +
                esc(m.magia_nome) +
                '</span>';
            if (m.magia_escola) {
                linhas += `<span class="arena-prep-escola">${esc(m.magia_escola)}</span>`;
            }
            if (!truque && marcouSessao && !semEspacos) {
                linhas += '<span class="arena-prep-slot-hint">−1 slot</span>';
            }
            linhas +=
                `<button class="arena-prep-btn ${semEspacos ? 'arena-prep-btn-esgotado' : ''} ${marcouSessao && truque ? 'arena-prep-btn-marcada' : ''}"` +
                ` data-magia-id="${m.magia_id}" data-nivel="${nivel}" data-acao="${acaoBtn}"` +
                ` title="${esc(titulo)}">${icone}</button>` +
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
