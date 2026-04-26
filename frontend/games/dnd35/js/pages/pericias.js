/**
 * pericias.js
 * Entry point para página de perícias
 */

import { PericiaController } from '../controllers/PericiaController.js';
import { apiConfig } from '../config/api.config.js';
import { NotificationService } from '../services/NotificationService.js';
import {
    installGlobalErrorGuards,
    safeBootstrap,
    safeBootstrapAsync,
} from '../utils/graceful-degradation.js';


const token = localStorage.getItem('token');
if (!token) {
    console.warn('⚠️ Sem autenticação');
    window.location.href = 'login.html';
}

let controller = null;

document.addEventListener('DOMContentLoaded', async () => {
    installGlobalErrorGuards('pericias-page');
    controller = safeBootstrap(
        'pericias-controller',
        () => new PericiaController(apiConfig),
        'Falha ao iniciar modulo de pericias. Recarregue a pagina.'
    );
    if (!controller) return;

    const initialized = await safeBootstrapAsync(
        'pericias-inicializacao',
        () => controller.inicializar(),
        'Nao foi possivel carregar dados de pericias para este combatente.'
    );
    if (!initialized) {
        NotificationService.mostrarErro('Nao foi possivel carregar as pericias agora.');
        return;
    }

    setupEventListeners(controller);
});

function setupEventListeners(controller) {
    document.querySelectorAll('.btn-filtro').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.btn-filtro').forEach(b => b.classList.remove('ativo'));
            btn.classList.add('ativo');
        });
    });

    document.querySelectorAll('.btn-fechar-modal, .btn-cancelar').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.target.closest('.modal')?.classList.remove('show');
        });
    });

    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.remove('show');
        });
    });
}