/*
   AuthService.js
   SRP: gerencia token JWT e sessão do usuário no frontend
   ✅ Padrão global (window) — compatível com carregamento dinâmico do dashboard.html
*/

class AuthService {

    static TOKEN_KEY   = 'rpg_token';
    static USUARIO_KEY = 'rpg_usuario';

    // ── Token 
    static getToken() {
        return sessionStorage.getItem(this.TOKEN_KEY);
    }

    static getAuthHeader() {
        const token = this.getToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    static estaLogado() {
        return !!this.getToken();
    }

    // ── Usuário 
    static getUsuario() {
        try {
            return JSON.parse(sessionStorage.getItem(this.USUARIO_KEY)) || null;
        } catch {
            return null;
        }
    }

    static getPerfil() { return this.getUsuario()?.perfil || null; }
    static getNome()   { return this.getUsuario()?.nome   || 'Usuário'; }

    // ── Permissões 
    static isAdmin()   { return this.getPerfil() === 'administrador'; }
    static isMestre()  { return ['mestre', 'administrador'].includes(this.getPerfil()); }
    static isJogador() { return this.getPerfil() === 'jogador'; }

    // ── Navegação 
    static logout() {
        sessionStorage.removeItem(this.TOKEN_KEY);
        sessionStorage.removeItem(this.USUARIO_KEY);
        window.location.href = '/pages/login.html';
    }

    static exigirLogin() {
        if (!this.estaLogado()) {
            window.location.href = '/pages/login.html';
        }
    }

    // ── Controle de UI por perfil ──────────────────────────────
    static configurarVisibilidadeAdmin(elementId = 'linkAdmin') {
        const el = document.getElementById(elementId);
        if (!el) return;
        el.style.display = this.isAdmin() ? '' : 'none';
    }

    static configurarVisibilidadeMestre(...elementIds) {
        const visivel = this.isMestre();
        elementIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = visivel ? '' : 'none';
        });
    }

    static podeVerStatsDe(tipo) {
        if (this.isMestre()) return true;
        return tipo === 'jogador';
    }
}

// ✅ Expõe globalmente — compatível com carregar() do dashboard.html
window.AuthService = AuthService;