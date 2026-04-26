/*
   AuthService.js
   SRP: gerencia token JWT e sessão do usuário no frontend
   ✅ Padrão global (window) — compatível com carregamento dinâmico do dashboard.html
*/

class AuthService {

    static TOKEN_KEY      = 'token';
    static USUARIO_KEY    = 'usuario';
    static REFRESH_KEY    = 'refresh_token';
    static GAME_SLUG_KEY  = 'game_slug_ativo';
    static GAME_NOME_KEY  = 'game_nome_ativo';
    static GAME_SLUG_DND35 = 'dnd35';

    // Catálogo conhecido pelo frontend para fallback de exibição quando
    // `localStorage.game_nome_ativo` ainda não foi populado (ex.: token antigo).
    static GAME_LABELS = {
        dnd35: 'D&D 3.5',
        dnd5e: 'D&D 5e',
        gurps: 'GURPS',
    };

    static GAME_ICONS = {
        dnd35: '🐉',
        dnd5e: '🐲',
        gurps: '⚔️',
    };

    // ── Token 
    static getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    }

    // ── Multi-jogo 
    static getGameSlugAtivo() {
        return localStorage.getItem(this.GAME_SLUG_KEY) || null;
    }

    static getGameNomeAtivo() {
        const explicito = localStorage.getItem(this.GAME_NOME_KEY);
        if (explicito) return explicito;
        const slug = this.getGameSlugAtivo();
        return slug ? (this.GAME_LABELS[slug] || slug.toUpperCase()) : null;
    }

    static getGameIconeAtivo() {
        const slug = this.getGameSlugAtivo();
        return slug ? (this.GAME_ICONS[slug] || '🎲') : '🎲';
    }

    /**
     * Garante que o usuário esteja logado E tenha selecionado um jogo
     * compatível com a página atual. Caso contrário, redireciona:
     *   - sem token: /pages/login.html
     *   - sem game_slug ativo: /pages/selecionar-jogo.html
     *   - game_slug diferente do esperado: /pages/selecionar-jogo.html
     */
    static exigirJogo(slugEsperado = AuthService.GAME_SLUG_DND35) {
        if (!this.estaLogado()) {
            window.location.href = '/pages/login.html';
            return false;
        }
        const ativo = this.getGameSlugAtivo();
        if (!ativo || ativo !== slugEsperado) {
            window.location.href = '/pages/selecionar-jogo.html';
            return false;
        }
        return true;
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
        localStorage.removeItem(this.REFRESH_KEY);
        localStorage.removeItem(this.GAME_SLUG_KEY);
        localStorage.removeItem(this.GAME_NOME_KEY);
        window.location.href = '/pages/login.html';
    }

    /**
     * Sai do jogo atual mas mantém a sessão global, voltando ao seletor.
     */
    static trocarJogo() {
        localStorage.removeItem(this.GAME_SLUG_KEY);
        localStorage.removeItem(this.GAME_NOME_KEY);
        window.location.href = '/pages/selecionar-jogo.html';
    }

    /**
     * Trata respostas 409 do backend que sinalizam ausência ou divergência
     * de `game_slug` no token (header `X-Game-Slug-Required`). Quando detecta,
     * limpa o slug local e redireciona para o seletor.
     * @returns {boolean} true se redirecionou (chamador deve abortar fluxo).
     */
    static lidarComJogoAusenteOuTrocado(response) {
        if (!response) return false;
        const headerSlug = (
            response.headers?.get?.('X-Game-Slug-Required') ||
            response.headers?.get?.('x-game-slug-required')
        );
        if (!headerSlug) return false;
        if (response.status !== 409 && response.status !== 403) return false;
        localStorage.removeItem(this.GAME_SLUG_KEY);
        localStorage.removeItem(this.GAME_NOME_KEY);
        window.location.href = '/pages/selecionar-jogo.html';
        return true;
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

        // ── BOTÃO TROCAR JOGO (volta ao seletor mantendo a sessão) ──
        const btnTrocarJogo = document.getElementById('btnTrocarJogo') || document.getElementById('btnTrocarJogoArena');
        if (btnTrocarJogo) {
            btnTrocarJogo.addEventListener('click', () => this.trocarJogo());
        }

        // ── BADGE DO JOGO ATIVO ──
        const badgeJogoEl = document.getElementById('badgeJogoAtivo') || document.getElementById('badgeJogoAtivoArena');
        if (badgeJogoEl) {
            const nome = this.getGameNomeAtivo();
            if (nome) {
                const icone = this.getGameIconeAtivo();
                badgeJogoEl.innerHTML = `<span class="badge-jogo__icone">${icone}</span> <span class="badge-jogo__nome">${nome}</span>`;
                badgeJogoEl.title = `Jogo ativo: ${nome}. Clique em "Trocar jogo" para mudar.`;
                badgeJogoEl.style.display = '';
            } else {
                badgeJogoEl.style.display = 'none';
            }
        }
    }

}

// ✅ Expõe globalmente — compatível com carregar() do dashboard.html
window.AuthService = AuthService;

/**
 * Interceptador global de respostas 409/403 com header
 * `X-Game-Slug-Required`. Quando o backend rejeita uma chamada por falta ou
 * divergência de `game_slug`, o usuário é redirecionado para o seletor sem
 * perder a sessão global. Executa apenas uma vez por carga de página.
 *
 * Idempotência: se o fetch global já foi envolto, não faz nada.
 */
(function instalarMultiJogoInterceptor() {
    if (typeof window === 'undefined' || !window.fetch) return;
    if (window.__multiJogoInterceptorInstalado) return;
    const fetchOriginal = window.fetch.bind(window);

    window.fetch = async function (...args) {
        const resposta = await fetchOriginal(...args);
        try {
            if (
                resposta &&
                (resposta.status === 409 || resposta.status === 403) &&
                resposta.headers &&
                typeof resposta.headers.get === 'function'
            ) {
                const slug = resposta.headers.get('X-Game-Slug-Required');
                if (slug) {
                    AuthService.lidarComJogoAusenteOuTrocado(resposta);
                }
            }
        } catch (_err) {
            // não derruba a requisição original em caso de erro do interceptor
        }
        return resposta;
    };

    window.__multiJogoInterceptorInstalado = true;
})();