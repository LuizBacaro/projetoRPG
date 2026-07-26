/**
 * RF-T12h — sincronização leve ficha ↔ arena (PV, PM, condições) via BroadcastChannel.
 * Mesma aba/navegador: ficha aberta em outra aba recebe alterações da mesa e vice-versa.
 */
(function () {
    const CANAL = 'tormenta-t20-sync';

    let _bc = null;

    function canal() {
        if (_bc) return _bc;
        try {
            _bc = new BroadcastChannel(CANAL);
        } catch (_e) {
            _bc = null;
        }
        return _bc;
    }

    function publicar(msg) {
        const ch = canal();
        if (!ch) return;
        try {
            ch.postMessage({ ...msg, timestamp: Date.now() });
        } catch (e) {
            console.warn('T20 sync: BroadcastChannel indisponível', e);
        }
    }

    function numOrNull(v) {
        const n = Number(v);
        return Number.isFinite(n) ? n : null;
    }

    function escHtml(s) {
        return String(s ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function publicarVitais(payload) {
        const pid = Number(payload && payload.personagem_id);
        if (!Number.isFinite(pid) || pid <= 0) return;
        publicar({
            tipo: 'vitais',
            origem: payload.origem === 'ficha' ? 'ficha' : 'arena',
            personagem_id: pid,
            pv_atual: numOrNull(payload.pv_atual),
            pv_max: numOrNull(payload.pv_max),
            pa_atual: numOrNull(payload.pa_atual),
            pa_max: numOrNull(payload.pa_max),
        });
    }

    function publicarCondicoes(payload) {
        const pid = Number(payload && payload.personagem_id);
        if (!Number.isFinite(pid) || pid <= 0) return;
        const rotulos = Array.isArray(payload.rotulos) ? payload.rotulos.filter(Boolean) : [];
        const tips = Array.isArray(payload.tips) ? payload.tips.filter(Boolean) : [];
        publicar({
            tipo: 'condicoes',
            origem: payload.origem === 'ficha' ? 'ficha' : 'arena',
            personagem_id: pid,
            rotulos,
            tips,
            mods: payload.mods && typeof payload.mods === 'object' ? payload.mods : null,
        });
    }

    function readPairSlash(id) {
        const el = document.getElementById(id);
        if (!el) return { a: 0, b: 0 };
        const raw = (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' ? el.value : el.textContent) || '';
        const parts = String(raw).split('/').map((x) => x.trim());
        const a = parseInt(parts[0], 10);
        const b = parseInt(parts[1], 10);
        return {
            a: Number.isFinite(a) ? a : 0,
            b: Number.isFinite(b) ? b : 0,
        };
    }

    function writePairSlash(id, a, b) {
        const el = document.getElementById(id);
        if (!el) return;
        const av = Number.isFinite(Number(a)) ? Math.trunc(Number(a)) : 0;
        const bv = Number.isFinite(Number(b)) ? Math.trunc(Number(b)) : 0;
        const s = `${av} / ${bv}`;
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') el.value = s;
        else el.textContent = s;
    }

    function aplicarVitaisFicha(data) {
        const fid = document.getElementById('fichaId');
        const meuId = fid && fid.value ? Number(fid.value) : NaN;
        if (!Number.isFinite(meuId) || meuId !== data.personagem_id) return;

        if (data.pv_atual != null || data.pv_max != null) {
            let a = data.pv_atual;
            let b = data.pv_max;
            const par = readPairSlash('fichaPv');
            if (a == null) a = par.a;
            if (b == null) b = par.b;
            writePairSlash('fichaPv', a, b);
        }
        if (data.pa_atual != null || data.pa_max != null) {
            let a = data.pa_atual;
            let b = data.pa_max;
            const par = readPairSlash('fichaPm');
            if (a == null) a = par.a;
            if (b == null) b = par.b;
            writePairSlash('fichaPm', a, b);
        }
        if (typeof window.t20AtualizarVitaisBreakdownTormenta === 'function') {
            window.t20AtualizarVitaisBreakdownTormenta();
        }
        const pvEl = document.getElementById('fichaPv');
        const pmEl = document.getElementById('fichaPm');
        [pvEl, pmEl].forEach((el) => {
            if (!el) return;
            el.classList.add('t20-sync-pulse');
            setTimeout(() => el.classList.remove('t20-sync-pulse'), 900);
        });
        if (window.__t20LastPersonagemPayload && window.__t20LastPersonagemPayload.id === data.personagem_id) {
            if (data.pv_atual != null) window.__t20LastPersonagemPayload.pv_atual = data.pv_atual;
            if (data.pv_max != null) window.__t20LastPersonagemPayload.pv_max = data.pv_max;
            if (data.pa_atual != null) window.__t20LastPersonagemPayload.pa_atual = data.pa_atual;
            if (data.pa_max != null) window.__t20LastPersonagemPayload.pa_max = data.pa_max;
        }
    }

    function renderCondicoesFicha(data) {
        const wrap = document.getElementById('t20FichaCondMesaWrap');
        const body = document.getElementById('t20FichaCondMesaBody');
        if (!wrap || !body) return;
        const rotulos = Array.isArray(data.rotulos) ? data.rotulos.filter(Boolean) : [];
        if (!rotulos.length) {
            wrap.hidden = true;
            body.innerHTML = '';
            wrap.removeAttribute('title');
            return;
        }
        wrap.hidden = false;
        const tips = Array.isArray(data.tips) ? data.tips : [];
        const tipTxt = tips.join(' · ');
        if (tipTxt) wrap.setAttribute('title', tipTxt.length > 400 ? `${tipTxt.slice(0, 397)}…` : tipTxt);
        else wrap.removeAttribute('title');
        body.innerHTML = rotulos.map((l) => `<span class="t20-ficha-cond-pill">${escHtml(l)}</span>`).join('');
        const mods = data.mods && typeof data.mods === 'object' ? data.mods : null;
        if (mods) {
            const parts = [];
            if (mods.ataque) parts.push(`Atq ${mods.ataque > 0 ? '+' : ''}${mods.ataque}`);
            if (mods.ca) parts.push(`Defesa ${mods.ca > 0 ? '+' : ''}${mods.ca}`);
            if (mods.pericia_geral) parts.push(`Perícias ${mods.pericia_geral > 0 ? '+' : ''}${mods.pericia_geral}`);
            if (parts.length) {
                body.innerHTML += `<p class="t20-ficha-cond-mods">${parts.map((x) => escHtml(x)).join(' · ')}</p>`;
            }
        }
    }

    function aplicarCondicoesFicha(data) {
        const fid = document.getElementById('fichaId');
        const meuId = fid && fid.value ? Number(fid.value) : NaN;
        if (!Number.isFinite(meuId) || meuId !== data.personagem_id) return;
        renderCondicoesFicha(data);
    }

    function aplicarVitaisArena(data) {
        const ar = window.__t20ArenaRef;
        if (!ar || !ar.byId) return;
        const p = ar.byId[data.personagem_id];
        if (!p) return;
        if (data.pv_atual != null) p.pv_atual = data.pv_atual;
        if (data.pv_max != null) p.pv_max = data.pv_max;
        if (data.pa_atual != null) p.pa_atual = data.pa_atual;
        if (data.pa_max != null) p.pa_max = data.pa_max;
        if (typeof window.__t20ArenaOnVitaisSync === 'function') {
            const patch = {};
            if (data.pv_atual != null) patch.pv_atual = data.pv_atual;
            if (data.pv_max != null) patch.pv_max = data.pv_max;
            if (data.pa_atual != null) patch.pa_atual = data.pa_atual;
            if (data.pa_max != null) patch.pa_max = data.pa_max;
            if (Object.keys(patch).length) window.__t20ArenaOnVitaisSync(data.personagem_id, patch);
        }
        if (typeof window.__t20ArenaRenderActive === 'function') window.__t20ArenaRenderActive();
        if (typeof window.__t20ArenaRenderPick === 'function') window.__t20ArenaRenderPick();
    }

    function aplicarCondicoesArena(data) {
        const ar = window.__t20ArenaRef;
        if (!ar) return;
        if (!ar.condPorId) ar.condPorId = Object.create(null);
        const rotulos = Array.isArray(data.rotulos) ? data.rotulos : [];
        const tips = Array.isArray(data.tips) ? data.tips : [];
        if (!rotulos.length && !tips.length) {
            delete ar.condPorId[data.personagem_id];
        } else {
            ar.condPorId[data.personagem_id] = {
                rotulos: rotulos.slice(),
                tips: tips.slice(),
                mods: data.mods || null,
            };
        }
        if (typeof window.__t20ArenaRenderCondStatus === 'function') {
            window.__t20ArenaRenderCondStatus();
        } else if (typeof t20ArenaRenderCondicaoStatus === 'function') {
            t20ArenaRenderCondicaoStatus();
        }
    }

    let _listenerOrigem = null;

    function initListener(origem) {
        const ch = canal();
        if (!ch) return;
        _listenerOrigem = origem;
        ch.onmessage = (ev) => {
            const d = ev.data;
            if (!d || !d.tipo || d.origem === origem) return;
            if (d.tipo === 'vitais') {
                if (origem === 'ficha') aplicarVitaisFicha(d);
                else if (origem === 'arena') aplicarVitaisArena(d);
            }
            if (d.tipo === 'condicoes') {
                if (origem === 'ficha') aplicarCondicoesFicha(d);
                else if (origem === 'arena') aplicarCondicoesArena(d);
            }
        };
    }

    function initFicha() {
        initListener('ficha');
    }

    function initArena() {
        initListener('arena');
    }

    function notificarSalvarFicha(body, personagemId) {
        if (!body || !personagemId) return;
        publicarVitais({
            origem: 'ficha',
            personagem_id: personagemId,
            pv_atual: body.pv_atual,
            pv_max: body.pv_max,
            pa_atual: body.pa_atual,
            pa_max: body.pa_max,
        });
    }

    window.T20SyncFichaArena = {
        CANAL,
        publicarVitais,
        publicarCondicoes,
        initFicha,
        initArena,
        notificarSalvarFicha,
        renderCondicoesFicha,
    };
})();
