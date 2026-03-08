/*
   AtaqueService.js
   SRP: comunicação HTTP para ataques e slots de magia
   ✅ Padrão global (window) — sem export/import
*/

class AtaqueService {

    _url(path) {
        return window.getApiUrl(path || '');
    }

    _headers() {
        var h = { 'Content-Type': 'application/json' };
        if (typeof AuthService !== 'undefined') {
            var t = AuthService.getToken();
            if (t) h['Authorization'] = 'Bearer ' + t;
        }
        return h;
    }

    // ── Ataques ──────────────────────────────────────────────────

    async listarAtaques(combatenteId) {
        var res = await fetch(
            this._url('/ataques/?combatente_id=' + combatenteId),
            { headers: this._headers() }
        );
        if (!res.ok) throw new Error('Erro ao buscar ataques');
        return res.json();
    }

    async salvarAtaques(combatenteId, ataques) {
        var res = await fetch(
            this._url('/ataques/combatente/' + combatenteId),
            {
                method:  'PUT',
                headers: this._headers(),
                body:    JSON.stringify(ataques)
            }
        );
        if (!res.ok) throw new Error('Erro ao salvar ataques');
        return res.json();
    }

    // ── Slots de Magia ───────────────────────────────────────────

    async listarMagias(combatenteId) {
        var res = await fetch(
            this._url('/magias_slots/?combatente_id=' + combatenteId),
            { headers: this._headers() }
        );
        if (!res.ok) throw new Error('Erro ao buscar slots de magia');
        return res.json();
    }

    async salvarMagias(combatenteId, slots) {
        var res = await fetch(
            this._url('/magias_slots/combatente/' + combatenteId),
            {
                method:  'PUT',
                headers: this._headers(),
                body:    JSON.stringify(slots)
            }
        );
        if (!res.ok) throw new Error('Erro ao salvar slots de magia');
        return res.json();
    }

    async atualizarSlotUsados(slotId, usados) {
        var res = await fetch(
            this._url('/magias_slots/' + slotId + '/usados'),
            {
                method:  'PATCH',
                headers: this._headers(),
                body:    JSON.stringify({ usados: usados })
            }
        );
        if (!res.ok) throw new Error('Erro ao atualizar slot');
        return res.json();
    }
}

// ✅ Expõe globalmente — sem export
window.AtaqueService = AtaqueService;