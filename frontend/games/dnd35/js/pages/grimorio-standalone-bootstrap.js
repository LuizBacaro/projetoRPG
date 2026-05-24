/**
 * grimorio-standalone-bootstrap.js
 *
 * Bootstrap da pagina /games/dnd35/pages/grimorio.html (versao dedicada do
 * Grimorio, aberta na mesma janela — mesmo fluxo de pericias-ficha).
 *
 * Responsabilidades:
 *  - Ler o id do combatente da URL (?id=)
 *  - Buscar o combatente via CombatenteService
 *  - Popular o contrato esperado pelo bootstrap do GrimorioController:
 *      * window._fichaController.combatente
 *      * #fichaClasse com a classe do combatente
 *  - Quando window._grimorioController estiver disponivel, chamar
 *    abrirGrimorio() e adaptar os comportamentos de "fechar" para voltar
 *    para a ficha original (em vez de apenas esconder o modal).
 *
 * Esta camada NAO duplica logica do GrimorioController; apenas adapta o
 * ambiente da pagina standalone para reutilizar 100% do controller existente.
 */

import { CombatenteService } from '../services/CombatenteService.js';
import { installGlobalErrorGuards, reportDegradedMode } from '../utils/graceful-degradation.js';

const COMBATENTE_ID_PARAM = 'id';
const URL_FICHA_BASE = '/games/dnd35/pages/ficha-personagem.html';

function getCombatenteIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const raw = params.get(COMBATENTE_ID_PARAM);
    const parsed = Number.parseInt(raw, 10);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
}

function urlVoltarParaFicha(combatenteId) {
    return combatenteId
        ? `${URL_FICHA_BASE}?id=${combatenteId}`
        : URL_FICHA_BASE;
}

function urlVoltarParaOrigem(combatenteId) {
    const params = new URLSearchParams(window.location.search);
    const returnTo = params.get('return_to');
    if (returnTo) {
        return decodeURIComponent(returnTo);
    }
    return urlVoltarParaFicha(combatenteId);
}

function exibirErroFatal(mensagem) {
    const overlay = document.getElementById('modalGrimorio');
    if (overlay) {
        overlay.innerHTML = `
            <div class="grimorio-container" style="padding:32px; text-align:center; color:#f3e5c1;">
                <h2 style="margin-top:0;">⚠️ Não foi possível abrir o Grimório</h2>
                <p style="margin: 12px 0 24px;">${mensagem}</p>
                <a href="${URL_FICHA_BASE}" class="grimorio-btn-descanso" style="text-decoration:none;">
                    ← Voltar para a Ficha
                </a>
            </div>
        `;
    } else {
        document.body.innerHTML = `<p style="color:#f3e5c1; padding:24px;">${mensagem}</p>`;
    }
}

function preencherTopbar(combatente) {
    const nomeEl = document.getElementById('grimorioPageNomePersonagem');
    const classeEl = document.getElementById('grimorioPageClassePersonagem');
    if (nomeEl) {
        nomeEl.textContent = combatente?.nome || `Personagem #${combatente?.id ?? '?'}`;
    }
    if (classeEl) {
        const classe = String(combatente?.classe || '').trim();
        classeEl.textContent = classe ? `· ${classe}` : '';
    }
}

function configurarLinkVoltar(combatenteId) {
    const link = document.getElementById('linkVoltarFicha');
    if (!link) return;
    link.setAttribute('href', urlVoltarParaOrigem(combatenteId));
}

/**
 * Aguarda o bootstrap do GrimorioController criar a instancia global.
 */
function aguardarGrimorioController(timeoutMs = 15000) {
    return new Promise((resolve, reject) => {
        const t0 = Date.now();
        const interval = setInterval(() => {
            if (window._grimorioController) {
                clearInterval(interval);
                resolve(window._grimorioController);
                return;
            }
            if (Date.now() - t0 > timeoutMs) {
                clearInterval(interval);
                reject(new Error('Timeout aguardando GrimorioController.'));
            }
        }, 100);
    });
}

/**
 * Em pagina dedicada, "fechar" volta para a ficha (mesmo fluxo de pericias-ficha).
 */
function instalarFecharStandalone(grimorioController, combatenteId) {
    if (!grimorioController) return;

    const voltar = () => {
        window.location.href = urlVoltarParaOrigem(combatenteId);
    };

    grimorioController.fecharGrimorio = voltar;

    const btnFecharGrimorio = document.getElementById('btnFecharGrimorio');
    if (btnFecharGrimorio) {
        btnFecharGrimorio.addEventListener('click', () => grimorioController.fecharGrimorio());
    }

    const grimorioBusca = document.getElementById('grimorioBusca');
    if (grimorioBusca) {
        grimorioBusca.addEventListener('input', () => grimorioController.filtrar?.());
    }
}

/**
 * Em pagina inteira nao queremos que clicar no fundo da overlay dispare "fechar".
 */
function bloquearFechamentoAcidental() {
    const overlay = document.getElementById('modalGrimorio');
    if (overlay) {
        overlay.addEventListener(
            'click',
            (event) => {
                if (event.target?.id === 'modalGrimorio') {
                    event.stopImmediatePropagation();
                }
            },
            true
        );
    }

    document.addEventListener(
        'keydown',
        (event) => {
            if (event.key !== 'Escape') return;
            const modalDetalhes = document.getElementById('grimorioModalDetalhes');
            if (!modalDetalhes) {
                event.stopImmediatePropagation();
            }
        },
        true
    );
}

async function inicializar() {
    installGlobalErrorGuards('grimorio-standalone');

    const combatenteId = getCombatenteIdFromUrl();
    configurarLinkVoltar(combatenteId);

    if (!combatenteId) {
        exibirErroFatal('Nenhum personagem informado na URL (parâmetro <code>?id</code> ausente).');
        return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
        exibirErroFatal('Sessão expirada. Faça login novamente para acessar o grimório.');
        return;
    }

    let combatente = null;
    try {
        const service = new CombatenteService();
        combatente = await service.obterCombatente(combatenteId);
    } catch (error) {
        console.error('[grimorio-standalone] Falha ao carregar combatente:', error);
        exibirErroFatal(
            `Não foi possível carregar o personagem #${combatenteId}: ${error?.message || error}`
        );
        return;
    }

    // O bootstrap interno do GrimorioController.js espera estes dois pontos
    // de extensao: o classe no DOM e o combatente em window._fichaController.
    window._fichaController = {
        combatente,
        renderizarSlotsDeMapia: () => {
            /* no-op: a ficha real renderiza os slots; em standalone nao ha o painel. */
        },
    };

    const classeEl = document.getElementById('fichaClasse');
    if (classeEl) {
        classeEl.textContent = String(combatente?.classe || '—');
    }

    preencherTopbar(combatente);
    bloquearFechamentoAcidental();

    try {
        const grimorio = await aguardarGrimorioController();
        instalarFecharStandalone(grimorio, combatenteId);

        // Garante que o ciclo completo de carregamento do grimorio rode
        // (recarregar dados, configurar filtros, renderizar listas).
        await grimorio.abrirGrimorio();
    } catch (error) {
        reportDegradedMode(
            'grimorio-standalone-bootstrap',
            error,
            'Falha ao iniciar o grimório nesta página. Tente recarregar.'
        );
    }
}

document.addEventListener('DOMContentLoaded', () => {
    inicializar().catch((error) => {
        console.error('[grimorio-standalone] Erro inesperado no bootstrap:', error);
        exibirErroFatal('Erro inesperado ao iniciar o grimório.');
    });
});
