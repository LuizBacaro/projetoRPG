/**
 * NotificationService.js
 * SRP: Apenas gerenciar notificações
 */

export class NotificationService {
    /**
     * Cria container se não existir
     */
    static ensureContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
            console.log('✅ Toast container criado');
        }
        return container;
    }

    /**
     * Mostra notificação de sucesso
     */
    static mostrarSucesso(mensagem, duracao = 3000) {
        this._mostrarToast(mensagem, 'success', duracao);
    }

    /**
     * Mostra notificação de erro
     */
    static mostrarErro(mensagem, duracao = 5000) {
        this._mostrarToast(mensagem, 'error', duracao);
    }

    /**
     * Mostra notificação de aviso
     */
    static mostrarAviso(mensagem, duracao = 3000) {
        this._mostrarToast(mensagem, 'warning', duracao);
    }

    /**
     * Mostra notificação de informação
     */
    static mostrarInfo(mensagem, duracao = 3000) {
        this._mostrarToast(mensagem, 'info', duracao);
    }

    /**
     * Implementação interna
     */
    static _mostrarToast(mensagem, tipo = 'info', duracao = 3000) {
        const container = this.ensureContainer();

        const toast = document.createElement('div');
        toast.className = `toast toast-${tipo}`;
        toast.textContent = mensagem;

        container.appendChild(toast);
        console.log(`📢 Toast ${tipo}:`, mensagem);

        // Animar entrada
        setTimeout(() => toast.classList.add('show'), 10);

        // Remover após duração
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duracao);
    }
}

// Bridge: disponibilizar como global para scripts não-module
window.NotificationService = NotificationService;

// Inicializar container
NotificationService.ensureContainer();