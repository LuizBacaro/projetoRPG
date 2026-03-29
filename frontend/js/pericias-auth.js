/**
 * pericias-auth.js
 * SRP: Validar autenticação antes de carregar página de perícias
 * Executar PRIMEIRO na página de perícias
 */

class PericiaAuthGuard {
    constructor() {
        this.token = localStorage.getItem('token');
        this.combatenteId = new URLSearchParams(window.location.search).get('combatente_id');
        
        this._validar();
    }

    _validar() {
        console.log('🔐 Validando autenticação para perícias...');
        
        // ✅ Verificar token
        if (!this.token) {
            console.error('❌ Token não encontrado');
            this._redirecionar();
            return;
        }

        // ✅ Verificar combatente_id
        if (!this.combatenteId) {
            console.error('❌ combatente_id não encontrado na URL');
            this._redirecionar();
            return;
        }

        console.log('✅ Autenticação válida para perícias');
        // ✅ Armazenar combatente_id para uso pelos controllers
        localStorage.setItem('combatente_id', this.combatenteId);
    }

    _redirecionar() {
        console.warn('⚠️ Redirecionando para login...');
        window.location.href = '/login.html?redirect=/pages/pericias.html';
    }

    static validar() {
        return new PericiaAuthGuard();
    }
}

// ✅ Executar validação imediatamente ao carregar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        PericiaAuthGuard.validar();
    });
} else {
    PericiaAuthGuard.validar();
}