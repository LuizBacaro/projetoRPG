/**
 * AtaqueService
 * SRP: comunicação HTTP com os endpoints de ataques e magias
 * Global — sem import/export (carregado via script dinâmico no dashboard)
 */
class AtaqueService {

    _url(path) { return window.getApiUrl(path); }

    _headers() {
        const h = { 'Content-Type': 'application/json' };
        if (typeof AuthService !== 'undefined') {
            const token = AuthService.getToken();
            if (token) h['Authorization'] = `Bearer ${token}`;
        }
        return h;
    }

    // ── Ataques 

    async listarAtaques(combatenteId) {
        const res = await fetch(this._url(`/combatentes/${combatenteId}/ataques`),
                                { headers: this._headers() });
        if (!res.ok) throw new Error('Erro ao carregar ataques');
        return res.json();
    }

    async salvarAtaques(combatenteId, ataques) {
        const res = await fetch(this._url(`/combatentes/${combatenteId}/ataques`), {
            method:  'PUT',
            headers: this._headers(),
            body:    JSON.stringify({ ataques })
        });
        if (!res.ok) throw new Error('Erro ao salvar ataques');
        return res.json();
    }

    // ── Magias 

    async listarMagias(combatenteId) {
        const res = await fetch(this._url(`/combatentes/${combatenteId}/magias`),
                                { headers: this._headers() });
        if (!res.ok) throw new Error('Erro ao carregar magias');
        return res.json();
    }

    async salvarMagias(combatenteId, slots) {
        const res = await fetch(this._url(`/combatentes/${combatenteId}/magias`), {
            method:  'PUT',
            headers: this._headers(),
            body:    JSON.stringify({ slots })
        });
        if (!res.ok) throw new Error('Erro ao salvar magias');
        return res.json();
    }

    async atualizarUsados(slotId, usados) {
        const res = await fetch(this._url(`/magias_slots/${slotId}/usados`), {
            method:  'PATCH',
            headers: this._headers(),
            body:    JSON.stringify({ usados })
        });
        if (!res.ok) throw new Error('Erro ao atualizar slot');
        return res.json();
    }
}

window.AtaqueService = AtaqueService;