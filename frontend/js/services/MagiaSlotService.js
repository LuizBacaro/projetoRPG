/**
 * MagiaSlotService
 * SRP: responsável EXCLUSIVAMENTE pela comunicação HTTP
 *      dos slots de magia na arena (incrementar/decrementar usados)
 */
export class MagiaSlotService {

    _url(path) { return window.getApiUrl(path); }

    _headers() {
        var h = { 'Content-Type': 'application/json' };
        if (typeof AuthService !== 'undefined') {
            var t = AuthService.getToken();
            if (t) h['Authorization'] = 'Bearer ' + t;
        }
        return h;
    }

    async atualizarUsados(slotId, usados) {
        var res = await fetch(this._url('/magias_slots/' + slotId + '/usados'), {
            method:  'PATCH',
            headers: this._headers(),
            body:    JSON.stringify({ usados: usados })
        });
        if (!res.ok) throw new Error('Erro ao atualizar slot de magia');
        return res.json();
    }
}