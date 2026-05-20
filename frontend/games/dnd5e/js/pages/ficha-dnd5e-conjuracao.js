/**
 * Painel de slots na ficha D&D 5e + descanso longo (grimório).
 */
import { Dnd5eConjuracaoFichaService } from '../services/Dnd5eConjuracaoFichaService.js';

const svc = new Dnd5eConjuracaoFichaService();

function esc(text) {
    if (typeof escapeHtml === 'function') return escapeHtml(String(text ?? ''));
    return String(text ?? '');
}

function renderSlots(estado) {
    const grid = document.getElementById('fichaMagiasGrid');
    if (!grid) return;
    const slots = estado?.slots || [];
    if (!slots.length) {
        grid.innerHTML = '<span class="ficha-magia-vazio">Sem espaços de magia</span>';
        return;
    }
    const parts = slots.map((s) => {
        const label = `${s.nivel}º`;
        const pct = s.total > 0 ? (s.disponiveis / s.total) * 100 : 0;
        let cor = '#4ade80';
        if (pct <= 50) cor = '#facc15';
        if (pct <= 25) cor = '#f87171';
        const disabled = s.disponiveis <= 0 ? ' disabled' : '';
        const tituloGastar =
            'Gastar 1 espaço de magia de ' + s.nivel + 'º nível (simulação na ficha)';
        return (
            '<motion class="ficha-slot-linha" data-nivel="' +
            s.nivel +
            '">' +
            '<span class="ficha-slot-nivel">' +
            label +
            '</span>' +
            '<span class="ficha-slot-contagem">' +
            s.disponiveis +
            '/' +
            s.total +
            '</span>' +
            '<motion class="ficha-slot-barra"><motion class="ficha-slot-barra-fill" style="width:' +
            pct +
            '%;background:' +
            cor +
            '"></div></div>' +
            '<button type="button" class="ficha-slot-gastar" data-gastar="' +
            s.nivel +
            '"' +
            disabled +
            ' title="' +
            tituloGastar +
            '">Gastar 1</button>' +
            '</div>'
        );
    });
    let html = parts.join('');
    html = html.replace(/<motion/g, '<div').replace(/<\/motion>/g, '</div>');
    grid.innerHTML = html;
    const meta = [];
    if (estado.magias_conhecidas_max != null) {
        meta.push(
            `Conhecidas: ${estado.magias_conhecidas_atual}/${estado.magias_conhecidas_max}`
        );
    }
    if (estado.magias_preparadas_max != null) {
        const prepAtual = (estado.magias_preparadas_ids || []).length;
        meta.push(`Preparadas: ${prepAtual}/${estado.magias_preparadas_max}`);
    }
    if (meta.length) {
        grid.insertAdjacentHTML(
            'beforeend',
            `<p class="ficha-magia-meta">${esc(meta.join(' · '))}</p>`
        );
    }
}

async function recarregar(personagemId) {
    if (!personagemId) return;
    try {
        const estado = await svc.obter(personagemId);
        window.__dnd5eConjuracaoEstado = estado;
        renderSlots(estado);
        const resumo = document.querySelector('.grimorio-slots-grid');
        if (resumo && estado.slots?.length) {
            resumo.innerHTML = estado.slots
                .map(
                    (s) =>
                        `<span class="grimorio-slot-chip">${s.nivel}º: ${s.disponiveis}/${s.total}</span>`
                )
                .join('');
        }
    } catch (e) {
        console.warn('Conjuração:', e.message);
    }
}

function bindGastarSlot(personagemId) {
    const grid = document.getElementById('fichaMagiasGrid');
    if (!grid || grid.dataset.boundGastar) return;
    grid.dataset.boundGastar = '1';
    grid.addEventListener('click', async (ev) => {
        const btn = ev.target.closest('[data-gastar]');
        if (!btn || !personagemId) return;
        const nivel = parseInt(btn.getAttribute('data-gastar'), 10);
        try {
            const estado = await svc.gastarSlot(personagemId, nivel, 1);
            window.__dnd5eConjuracaoEstado = estado;
            renderSlots(estado);
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message);
        }
    });
}

function bindDescansoLongo(personagemId) {
    const btn = document.getElementById('btnDescansoLongoGrimorio');
    if (!btn || btn.dataset.dnd5eDescanso) return;
    btn.dataset.dnd5eDescanso = '1';
    btn.addEventListener(
        'click',
        async (ev) => {
            if (!personagemId) return;
            ev.preventDefault();
            ev.stopImmediatePropagation();
            if (
                !confirm(
                    'Descanso longo restaura todos os espaços e limpa magias preparadas. Continuar?'
                )
            ) {
                return;
            }
            try {
                await svc.descansoLongo(personagemId);
                await recarregar(personagemId);
                if (window._grimorioController?._recarregarDados) {
                    await window._grimorioController._recarregarDados();
                }
                if (typeof Toast !== 'undefined') {
                    Toast.success('Descanso longo aplicado.');
                }
            } catch (e) {
                if (typeof Toast !== 'undefined') Toast.error(e.message);
            }
        },
        true
    );
}

window.__dnd5eRecarregarConjuracao = recarregar;

document.addEventListener('DOMContentLoaded', () => {
    const tick = setInterval(() => {
        const api = window.__dnd5eFichaGrimorioApi;
        if (!api) return;
        const snap = api.getSnapshot?.();
        if (!snap?.id) return;
        clearInterval(tick);
        recarregar(snap.id);
        bindGastarSlot(snap.id);
        bindDescansoLongo(snap.id);
    }, 400);
});
