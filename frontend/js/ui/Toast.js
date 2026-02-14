/**
 * Componente Toast (Notificações)
 * Princípio SOLID: Single Responsibility - apenas exibir notificações
 */
export class Toast {
    
    /**
     * Exibe uma notificação toast
     */
    static mostrar(texto, tipo = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${tipo}`;
        toast.textContent = texto;
        
        document.body.appendChild(toast);
        
        // Animação de entrada
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Remover após 3 segundos
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    static success(texto) {
        this.mostrar(texto, 'success');
    }
    
    static error(texto) {
        this.mostrar(texto, 'error');
    }
    
    static warning(texto) {
        this.mostrar(texto, 'warning');
    }
    
    static info(texto) {
        this.mostrar(texto, 'info');
    }
}