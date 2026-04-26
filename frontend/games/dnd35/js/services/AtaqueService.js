/*
   AtaqueService.js
   SRP: comunicação HTTP para ataques e slots de magia
   ✅ URLs alinhadas com o backend: /combatentes/{id}/ataques
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

    async _buildHttpError(res, contexto) {
        var detalhe = '';

        try {
            var data = await res.clone().json();
            if (data && typeof data.detail === 'string' && data.detail.trim()) {
                detalhe = data.detail.trim();
            }
        } catch (_) {}

        if (!detalhe) {
            try {
                var txt = (await res.text()).trim();
                if (txt) detalhe = txt;
            } catch (_) {}
        }

        return new Error(
            detalhe
                ? contexto + ' (HTTP ' + res.status + '): ' + detalhe
                : contexto + ' (HTTP ' + res.status + ')'
        );
    }

    // ── Ataques ──────────────────────────────────────────────────

    async listarAtaques(combatenteId) {
        var res = await fetch(
            // ✅ GET /combatentes/{id}/ataques
            this._url('/combatentes/' + combatenteId + '/ataques'),
            { headers: this._headers() }
        );
        if (!res.ok) {
            throw await this._buildHttpError(res, 'Erro ao buscar ataques do combatente #' + combatenteId);
        }
        return res.json();
    }

    async salvarAtaques(combatenteId, ataques) {
        var res = await fetch(
            // ✅ PUT /combatentes/{id}/ataques
            this._url('/combatentes/' + combatenteId + '/ataques'),
            {
                method:  'PUT',
                headers: this._headers(),
                body:    JSON.stringify({ ataques: ataques })
            }
        );
        if (!res.ok) {
            throw await this._buildHttpError(res, 'Erro ao salvar ataques do combatente #' + combatenteId);
        }
        return res.json();
    }

    // ── Magias ───────────────────────────────────────────────────

    async listarMagias(combatenteId) {
        var res = await fetch(
            // ✅ GET /combatentes/{id}/magias
            this._url('/combatentes/' + combatenteId + '/magias'),
            { headers: this._headers() }
        );
        if (!res.ok) {
            throw await this._buildHttpError(res, 'Erro ao buscar slots de magia do combatente #' + combatenteId);
        }
        return res.json();
    }

    async salvarMagias(combatenteId, slots) {
        var res = await fetch(
            // ✅ PUT /combatentes/{id}/magias
            this._url('/combatentes/' + combatenteId + '/magias'),
            {
                method:  'PUT',
                headers: this._headers(),
                body:    JSON.stringify({ slots: slots })
            }
        );
        if (!res.ok) {
            throw await this._buildHttpError(
                res,
                'Erro ao salvar slots de magia do combatente #' + combatenteId
            );
        }
        return res.json();
    }

    async atualizarSlotUsados(slotId, usados) {
        var res = await fetch(
            // ✅ PATCH /magias_slots/{slot_id}/usados (rota separada — está correta)
            this._url('/magias_slots/' + slotId + '/usados'),
            {
                method:  'PATCH',
                headers: this._headers(),
                body:    JSON.stringify({ usados: usados })
            }
        );
        if (!res.ok) {
            throw await this._buildHttpError(res, 'Erro ao atualizar slot #' + slotId + ' para ' + usados + ' usados');
        }
        return res.json();
    }
}

// ✅ Global — sem export
window.AtaqueService = AtaqueService;