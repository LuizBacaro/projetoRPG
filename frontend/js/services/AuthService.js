/**
 * AuthService
 * SRP: gerencia token JWT e sessão do usuário no frontend
 */
class AuthService {

    static TOKEN_KEY   = 'rpg_token';
    static USUARIO_KEY = 'rpg_usuario';

    static getToken()  { return sessionStorage.getItem(this.TOKEN_KEY); }

    static getAuthHeader() {
        const token = this.getToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    static estaLogado() { return !!this.getToken(); }

    static getUsuario() {
        try { return JSON.parse(sessionStorage.getItem(this.USUARIO_KEY)) || null; }
        catch { return null; }
    }

    static getPerfil() { return this.getUsuario()?.perfil || null; }
    static getNome()   { return this.getUsuario()?.nome   || 'Usuário'; }

    static isAdmin()  { return this.getPerfil() === 'administrador'; }
    static isMestre() { return ['mestre', 'administrador'].includes(this.getPerfil()); }

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
}