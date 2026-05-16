/**
 * Cliente API — combate D&D 5e (`/api/v1/dnd5e/combate/*`).
 */
class Dnd5eCombateService {
    _url(path) {
        return window.getApiUrl('/dnd5e/combate' + path);
    }

    _headers() {
        const headers = { 'Content-Type': 'application/json' };
        const token = AuthService.getToken();
        if (token) headers.Authorization = `Bearer ${token}`;
        return headers;
    }

    async _post(path, body) {
        const res = await fetch(this._url(path), {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify(body),
        });
        if (res.status === 401) {
            if (typeof AuthService.logout === 'function') AuthService.logout();
            throw new Error('Sessão expirada.');
        }
        if (!res.ok) {
            const e = await res.json().catch(() => ({}));
            throw new Error(e.detail || 'Erro no combate');
        }
        return res.json();
    }

    iniciativa(combatentes) {
        return this._post('/iniciativa', { combatentes });
    }

    ataque(payload) {
        return this._post('/ataque', payload);
    }

    dano(payload) {
        return this._post('/dano', payload);
    }

    decrementarCondicoesTurno(condicoes) {
        return this._post('/condicoes/decrementar-turno', { condicoes });
    }

    normalizarCondicoes(condicoes) {
        return this._post('/condicoes/normalizar', { condicoes });
    }

    sincronizarCondicoesHp(hpAtual, condicoes) {
        return this._post('/condicoes/sincronizar-hp', {
            hp_atual: hpAtual,
            condicoes,
        });
    }
}
