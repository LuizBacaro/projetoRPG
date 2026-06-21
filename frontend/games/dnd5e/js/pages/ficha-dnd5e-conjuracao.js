/**
 * Painel de conjuração na ficha D&D 5e — perfil, slots, PF, recuperação arcana.
 */
import { Dnd5eConjuracaoFichaService } from '../services/Dnd5eConjuracaoFichaService.js';

const svc = new Dnd5eConjuracaoFichaService();

const HAB_LABEL = { int: 'INT', wis: 'SAB', cha: 'CAR', dex: 'DES' };
const MODO_LABEL = {
    preparado: 'Preparado',
    conhecido: 'Conhecido',
    bruxo: 'Pacto (Bruxo)',
    nenhum: '—',
};

function esc(text) {
    if (typeof escapeHtml === 'function') return escapeHtml(String(text ?? ''));
    return String(text ?? '');
}

function ensureHosts() {
    const secao = document.getElementById('secaoMagias');
    if (!secao) return null;
    let perfil = document.getElementById('fichaConjPerfil');
    if (!perfil) {
        perfil = document.createElement('div');
        perfil.id = 'fichaConjPerfil';
        perfil.className = 'ficha-conj-perfil';
        secao.insertBefore(perfil, document.getElementById('fichaMagiasGrid'));
    }
    let recursos = document.getElementById('fichaConjRecursos');
    if (!recursos) {
        recursos = document.createElement('div');
        recursos.id = 'fichaConjRecursos';
        recursos.className = 'ficha-conj-recursos';
        const grid = document.getElementById('fichaMagiasGrid');
        if (grid) secao.insertBefore(recursos, grid);
    }
    let acoes = document.getElementById('fichaConjAcoes');
    if (!acoes) {
        acoes = document.createElement('div');
        acoes.id = 'fichaConjAcoes';
        acoes.className = 'ficha-conj-acoes';
        const btnGrim = document.getElementById('btnAbrirGrimorio');
        if (btnGrim) secao.insertBefore(acoes, btnGrim);
    }
    return { perfil, recursos, acoes };
}

function renderPerfil(estado) {
    const hosts = ensureHosts();
    if (!hosts?.perfil || !estado) return;
    const hab = HAB_LABEL[estado.habilidade_primaria] || String(estado.habilidade_primaria || '').toUpperCase();
    const modo = MODO_LABEL[estado.modo_lista] || estado.modo_lista;
    const partes = [
        `<strong>${esc(modo)}</strong>`,
        `CD: ${esc(hab)}`,
        `máx. ${estado.max_nivel_magia ?? 0}º`,
        `truques ×${estado.truque_multiplicador_dados || 1}`,
    ];
    if (estado.magias_conhecidas_max != null) {
        partes.push(
            `conhecidas ${estado.magias_conhecidas_atual}/${estado.magias_conhecidas_max}`
        );
    }
    if (estado.magias_preparadas_max != null) {
        const prep = (estado.magias_preparadas_ids || []).length;
        partes.push(`preparadas ${prep}/${estado.magias_preparadas_max}`);
    }
    hosts.perfil.innerHTML = `<p class="ficha-conj-perfil-text">${partes.join(' · ')}</p>`;
}

function renderRecursos(estado, personagemId) {
    const hosts = ensureHosts();
    if (!hosts?.recursos) return;
    let html = '';

    if (estado.pontos_feiticaria_max != null) {
        html += `<div class="ficha-conj-pf">
            <span class="ficha-conj-pf-label">Pontos de feitiçaria</span>
            <span class="ficha-conj-pf-valor">${estado.pontos_feiticaria_atual ?? 0}/${estado.pontos_feiticaria_max}</span>
            <div class="ficha-conj-pf-btns">
                <label>Slot
                    <select id="fichaPfCriarNivel" class="ficha-conj-select">
                        <option value="1">1º (2 PF)</option>
                        <option value="2">2º (3 PF)</option>
                        <option value="3">3º (5 PF)</option>
                        <option value="4">4º (6 PF)</option>
                        <option value="5">5º (7 PF)</option>
                    </select>
                </label>
                <button type="button" class="ficha-conj-btn" data-pf="criar">Criar slot</button>
                <label>Converter
                    <select id="fichaPfConverterNivel" class="ficha-conj-select">
                        <option value="1">1º</option>
                        <option value="2">2º</option>
                        <option value="3">3º</option>
                        <option value="4">4º</option>
                        <option value="5">5º</option>
                    </select>
                </label>
                <button type="button" class="ficha-conj-btn" data-pf="converter">→ PF</button>
            </div>
        </div>`;
    }

    if (estado.classe === 'mago') {
        const disp = estado.recuperacao_arcana_disponivel ? 'disponível' : 'usada';
        html += `<div class="ficha-conj-arcana">
            <span class="ficha-conj-arcana-label">Recuperação arcana (${disp})</span>
            <span class="ficha-conj-arcana-hint">até ${estado.recuperacao_arcana_max_niveis ?? 0} níveis de slot (1º–5º)</span>
            <div class="ficha-conj-arcana-btns">
                <button type="button" class="ficha-conj-btn" data-arcana="1" ${estado.recuperacao_arcana_disponivel ? '' : 'disabled'}>Recuperar 1×1º</button>
                <button type="button" class="ficha-conj-btn" data-arcana="1-1" ${estado.recuperacao_arcana_disponivel ? '' : 'disabled'}>Recuperar 2×1º</button>
                <button type="button" class="ficha-conj-btn" data-arcana="2" ${estado.recuperacao_arcana_disponivel ? '' : 'disabled'}>Recuperar 1×2º</button>
            </div>
        </div>`;
    }

    hosts.recursos.innerHTML = html;
    hosts.recursos.dataset.personagemId = String(personagemId || '');

    hosts.recursos.querySelector('[data-pf="criar"]')?.addEventListener('click', async () => {
        const nivel = parseInt(document.getElementById('fichaPfCriarNivel')?.value, 10);
        try {
            await svc.criarSlotPontosFeiticaria(personagemId, nivel);
            await recarregar(personagemId);
            Toast?.success?.('Slot criado com pontos de feitiçaria.');
        } catch (e) {
            Toast?.error?.(e.message);
        }
    });
    hosts.recursos.querySelector('[data-pf="converter"]')?.addEventListener('click', async () => {
        const nivel = parseInt(document.getElementById('fichaPfConverterNivel')?.value, 10);
        try {
            await svc.converterSlotPontosFeiticaria(personagemId, nivel);
            await recarregar(personagemId);
            Toast?.success?.('Espaço convertido em pontos.');
        } catch (e) {
            Toast?.error?.(e.message);
        }
    });

    hosts.recursos.querySelectorAll('[data-arcana]').forEach((btn) => {
        btn.addEventListener('click', async () => {
            const plano = btn.getAttribute('data-arcana');
            const slots = plano === '1-1' ? { 1: 2 } : { [parseInt(plano, 10)]: 1 };
            try {
                await svc.recuperacaoArcana(personagemId, slots);
                await recarregar(personagemId);
                Toast?.success?.('Recuperação arcana aplicada.');
            } catch (e) {
                Toast?.error?.(e.message);
            }
        });
    });
}

function renderAcoes(personagemId, estado) {
    const hosts = ensureHosts();
    if (!hosts?.acoes) return;
    const curtoLabel = estado.recupera_slots_repouso_curto
        ? '☀️ Repouso curto (recupera slots)'
        : '☀️ Repouso curto';
    hosts.acoes.innerHTML = `
        <button type="button" class="ficha-conj-btn ficha-conj-btn-descanso" id="btnDescansoCurtoFicha">${curtoLabel}</button>
    `;
    hosts.acoes.querySelector('#btnDescansoCurtoFicha')?.addEventListener('click', async () => {
        try {
            const res = await svc.descansoCurto(personagemId);
            await recarregar(personagemId);
            Toast?.success?.(res.mensagem || 'Repouso curto aplicado.');
        } catch (e) {
            Toast?.error?.(e.message);
        }
    });
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
            '<div class="ficha-slot-linha" data-nivel="' +
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
            '<div class="ficha-slot-barra"><div class="ficha-slot-barra-fill" style="width:' +
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
    grid.innerHTML = parts.join('');
}

async function recarregar(personagemId) {
    if (!personagemId) return;
    try {
        const estado = await svc.obter(personagemId);
        window.__dnd5eConjuracaoEstado = estado;
        renderPerfil(estado);
        renderRecursos(estado, personagemId);
        renderAcoes(personagemId, estado);
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
            renderRecursos(estado, personagemId);
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
            if (typeof window.__dnd5eAplicarRepousoLongo === 'function') {
                await window.__dnd5eAplicarRepousoLongo();
                return;
            }
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
