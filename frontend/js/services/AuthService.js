/*
   AuthService.js
   SRP: gerencia token JWT e sessão do usuário no frontend
   ✅ Padrão global (window) — compatível com carregamento dinâmico do dashboard.html
*/

class AuthService {

    static TOKEN_KEY   = 'token';
    static USUARIO_KEY = 'usuario';

    // ── Token 
    static getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
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
            return JSON.parse(localStorage.getItem(this.USUARIO_KEY)) || null;
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
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USUARIO_KEY);
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

    /**
 * Configura o header do usuário (nome, perfil, visibilidade admin)
 * ✅ Funciona em qualquer página que tenha os elementos
 */
static configurarHeaderUsuario() {
    const usuario = this.getUsuario();
    if (!usuario) {
        console.warn('⚠️ Usuário não encontrado');
        return;
    }


    // ── NOME DO USUÁRIO ──
    const nomeEl = document.getElementById('nomeUsuario') || document.getElementById('nomeUsuarioArena');
    if (nomeEl) {
        nomeEl.textContent = `👤 ${usuario.nome}`;
    }

    // ── BADGE DE PERFIL ──
    const badgeEl = document.getElementById('badgePerfil') || document.getElementById('badgePerfilArena');
    if (badgeEl) {
        badgeEl.textContent = usuario.perfil;
        badgeEl.className = `badge-perfil ${usuario.perfil}`;
    }

    // ── LINK ADMIN (apenas para administradores) ──
    const linkAdminEl = document.getElementById('linkAdmin');
        if (linkAdminEl) {
            if (this.isAdmin()) {
                linkAdminEl.style.display = '';
            } else {
                linkAdminEl.style.display = 'none';
            }
        }

        // ── BOTÃO LOGOUT ──
        const btnLogout = document.getElementById('btnLogout') || document.getElementById('btnLogoutArena');
        if (btnLogout) {
            btnLogout.addEventListener('click', () => this.logout());
        }
    }

}

// ✅ Expõe globalmente — compatível com carregar() do dashboard.html
window.AuthService = AuthService;