/*
 * MembershipsAdminService.js
 * SRP: cliente HTTP para os endpoints `/api/v1/games/{slug}/memberships`
 * (painel admin multi-jogo). Não conhece DOM — apenas fala com o backend.
 *
 * Os endpoints consumidos exigem perfil `administrador` global; o backend
 * responde 403 em caso contrário.
 */
(function (global) {
    function authHeader() {
        const token = localStorage.getItem('token');
        return token ? { Authorization: `Bearer ${token}` } : {};
    }

    async function listarCatalogo() {
        const res = await fetch(global.getApiUrl('/games'), {
            headers: authHeader(),
        });
        if (!res.ok) {
            throw new Error(`Falha ao listar catálogo de jogos (${res.status})`);
        }
        return res.json();
    }

    async function listarMemberships(slug) {
        const res = await fetch(
            global.getApiUrl(`/games/${encodeURIComponent(slug)}/memberships`),
            { headers: authHeader() }
        );
        if (!res.ok) {
            const detalhe = await res.json().catch(() => ({}));
            throw new Error(
                detalhe.detail || `Falha ao listar acessos (${res.status})`
            );
        }
        return res.json();
    }

    async function conceder(slug, payload) {
        const res = await fetch(
            global.getApiUrl(`/games/${encodeURIComponent(slug)}/memberships`),
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', ...authHeader() },
                body: JSON.stringify(payload),
            }
        );
        const body = await res.json().catch(() => ({}));
        if (!res.ok) {
            throw new Error(body.detail || `Falha ao conceder acesso (${res.status})`);
        }
        return body;
    }

    async function atualizar(slug, membershipId, payload) {
        const res = await fetch(
            global.getApiUrl(
                `/games/${encodeURIComponent(slug)}/memberships/${membershipId}`
            ),
            {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json', ...authHeader() },
                body: JSON.stringify(payload),
            }
        );
        const body = await res.json().catch(() => ({}));
        if (!res.ok) {
            throw new Error(body.detail || `Falha ao atualizar (${res.status})`);
        }
        return body;
    }

    async function revogar(slug, membershipId) {
        const res = await fetch(
            global.getApiUrl(
                `/games/${encodeURIComponent(slug)}/memberships/${membershipId}`
            ),
            {
                method: 'DELETE',
                headers: authHeader(),
            }
        );
        if (!res.ok && res.status !== 204) {
            const body = await res.json().catch(() => ({}));
            throw new Error(body.detail || `Falha ao revogar (${res.status})`);
        }
    }

    global.MembershipsAdminService = {
        listarCatalogo,
        listarMemberships,
        conceder,
        atualizar,
        revogar,
    };
})(window);
