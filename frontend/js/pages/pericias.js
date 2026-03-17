/**
 * pericias.js
 * Entry point para página de perícias
 */

import { PericiaController } from '../controllers/PericiaController.js';
import { apiConfig } from '../config/api.config.js';
import { NotificationService } from '../services/NotificationService.js';

console.log('🎮 Carregando página de perícias...');

const token = localStorage.getItem('token');
if (!token) {
    console.warn('⚠️ Sem autenticação');
    window.location.href = 'login.html';
}

const controller = new PericiaController(apiConfig);

document.addEventListener('DOMContentLoaded', async () => {
    try {
        await controller.inicializar();
        setupEventListeners(controller);
    } catch (error) {
        console.error('❌ Erro:', error);
        NotificationService.mostrarErro(error.message);
    }
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