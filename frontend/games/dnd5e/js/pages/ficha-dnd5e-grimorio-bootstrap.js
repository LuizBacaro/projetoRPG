/**
 * Inicializa Dnd5eGrimorioController na ficha D&D 5e (APIs 5e + UI de preview PT).
 */
import { Dnd5eGrimorioController } from '../controllers/Dnd5eGrimorioController.js?v=20260519a';
import { Dnd5eGrimorioService } from '../services/Dnd5eGrimorioService.js';
import { Dnd5eMagiaService } from '../services/Dnd5eMagiaService.js?v=2';
import { Dnd5eMagiaPreparadaAdapter } from '../services/Dnd5eMagiaPreparadaAdapter.js';
import {
    isClasseConjuradora,
    normalizeClasseConjuradora,
} from '/games/dnd35/js/utils/combat-rules.js?v=20260518b';
import {
    installGlobalErrorGuards,
    reportDegradedMode,
    safeBootstrap,
} from '/games/dnd35/js/utils/graceful-degradation.js';

const CONJURADORAS_SLUG = new Set([
    'mago',
    'wizard',
    'clerigo',
    'cleric',
    'druida',
    'druid',
    'bardo',
    'bard',
    'feiticeiro',
    'sorcerer',
    'bruxo',
    'warlock',
    'paladino',
    'paladin',
    'patrulheiro',
    'ranger',
]);

function slugConjurador(classeSlug) {
    return (classeSlug || '').trim().toLowerCase();
}

function montarCombatenteDnd5e() {
    const api = window.__dnd5eFichaGrimorioApi;
    if (!api) return null;
    const snap = api.getSnapshot();
    if (!snap?.id) return null;
    const classeSlug = snap.ficha?.classe_slug || '';
    if (!CONJURADORAS_SLUG.has(slugConjurador(classeSlug))) return null;

    const classeCatalogo = api.getClasseNome?.() || classeSlug;
    return {
        id: snap.id,
        nome: snap.nome,
        nivel: snap.nivel,
        classe: classeCatalogo,
        classe_slug: classeSlug,
        sistema: 'dnd5e',
    };
}

function atualizarUiConjurador(combatente) {
    const btnHeader = document.getElementById('btnGrimorio');
    const secao = document.getElementById('secaoMagias');
    const btnAbrir = document.getElementById('btnAbrirGrimorio');
    const show = Boolean(combatente);
    if (btnHeader) btnHeader.style.display = show ? 'inline-flex' : 'none';
    if (secao) secao.style.display = show ? '' : 'none';
    if (btnAbrir) btnAbrir.style.display = show ? '' : 'none';
}

function bindGrimorioUi() {
    const abrir = () => window._grimorioController?.abrirGrimorio();
    const fechar = () => window._grimorioController?.fecharGrimorio();
    document.getElementById('btnGrimorio')?.addEventListener('click', abrir);
    document.getElementById('btnAbrirGrimorio')?.addEventListener('click', abrir);
    document.getElementById('btnFecharGrimorio')?.addEventListener('click', fechar);
}

document.addEventListener('DOMContentLoaded', () => {
    installGlobalErrorGuards('dnd5e-grimorio-ficha');
    const tentar = setInterval(() => {
        try {
            if (!window.__dnd5eFichaGrimorioApi) return;
            const combatente = montarCombatenteDnd5e();
            const fichaClasse = document.getElementById('fichaClasse');
            if (fichaClasse && combatente) {
                fichaClasse.textContent = combatente.classe || '—';
            }
            atualizarUiConjurador(combatente);
            if (!combatente) return;

            clearInterval(tentar);
            const token = localStorage.getItem('token');
            const magiaService = new Dnd5eMagiaService(token);
            const grimorioService = new Dnd5eGrimorioService(token);
            const preparadaAdapter = new Dnd5eMagiaPreparadaAdapter(token);

            window._grimorioController = safeBootstrap(
                'dnd5e-grimorio-controller',
                () =>
                    new Dnd5eGrimorioController(
                        combatente,
                        token,
                        magiaService,
                        grimorioService,
                        preparadaAdapter
                    ),
                'Falha ao iniciar grimório 5e.'
            );
            if (!window._grimorioController) return;

            bindGrimorioUi();

            document.getElementById('modalGrimorio')?.addEventListener('click', (event) => {
                if (event.target.id === 'modalGrimorio') {
                    window._grimorioController.fecharGrimorio();
                }
            });

            document.addEventListener('keydown', (event) => {
                if (event.key !== 'Escape') return;
                window._grimorioController?.fecharGrimorio();
            });
        } catch (error) {
            reportDegradedMode('dnd5e-grimorio-bootstrap', error, 'Grimório indisponível.');
            clearInterval(tentar);
        }
    }, 250);
});

/** Reavalia visibilidade quando classe/nível mudam na ficha. */
window.__dnd5eAtualizarSecaoMagias = function atualizarSecaoMagias() {
    const combatente = montarCombatenteDnd5e();
    const fichaClasse = document.getElementById('fichaClasse');
    if (fichaClasse) {
        fichaClasse.textContent = combatente?.classe || '—';
    }
    atualizarUiConjurador(combatente);
};
