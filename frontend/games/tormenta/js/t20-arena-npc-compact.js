/**
 * RF-T12e — vista compacta NPC/monstro na arena (PV, CA, ini, ataques).
 */
(function () {
    'use strict';

    function esc(s) {
        return String(s ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;');
    }

    function arenaRef() {
        return window.__t20ArenaRef;
    }

    function isNpcOuMonstro(p) {
        const t = p ? String(p.tipo || '').toLowerCase() : '';
        return t === 'npc' || t === 'monstro';
    }

    function ataquesDeFicha(personagem) {
        const fj = personagem && personagem.ficha_json;
        if (!fj || typeof fj !== 'object') return [];
        const raw = Array.isArray(fj.ataques) ? fj.ataques : [];
        return raw
            .map((a, i) => {
                if (!a || typeof a !== 'object') return null;
                const nome = String(a.nome || a.arma || `Ataque ${i + 1}`).trim();
                const bonus = String(a.bonus_ataque != null ? a.bonus_ataque : a.teste || '').trim();
                const dano = String(a.dano || '').trim();
                if (!nome && !bonus && !dano) return null;
                return { nome: nome || `Ataque ${i + 1}`, bonus: bonus || '+0', dano: dano || '—' };
            })
            .filter(Boolean);
    }

    function renderAtaques(p, mask) {
        const wrap = document.getElementById('t20ArenaNpcCompact');
        const host = document.getElementById('t20ArenaNpcAtaques');
        const hint = document.getElementById('t20ArenaNpcCompactHint');
        if (!wrap || !host) return;

        const npc = isNpcOuMonstro(p);
        wrap.hidden = !npc || !p;
        if (!npc || !p) {
            host.innerHTML = '';
            if (hint) hint.textContent = '';
            return;
        }

        const lista = ataquesDeFicha(p);
        if (!lista.length) {
            host.innerHTML =
                '<p class="t20-arena-npc-sem-ataques">Nenhum ataque na ficha. Edite o combatente ou use «Rolar ataque» manual.</p>';
        } else {
            host.innerHTML = `<table class="t20-arena-npc-atq-table"><thead><tr><th>Ataque</th><th>Bônus</th><th>Dano</th><th></th></tr></thead><tbody>${lista
                .map(
                    (a, i) =>
                        `<tr><td>${esc(a.nome)}</td><td>${esc(a.bonus)}</td><td>${esc(a.dano)}</td><td><button type="button" class="tormenta-btn tormenta-btn--secondary t20-arena-npc-atq-btn" data-atq-idx="${i}" title="Abrir rolagem de ataque com este preset">🎲</button></td></tr>`
                )
                .join('')}</tbody></table>`;
            host.querySelectorAll('.t20-arena-npc-atq-btn').forEach((btn) => {
                if (btn.dataset.bound) return;
                btn.dataset.bound = '1';
                btn.addEventListener('click', () => {
                    const idx = Number(btn.getAttribute('data-atq-idx'));
                    if (typeof window.__t20ArenaAbrirModalAtaquePreset === 'function') {
                        window.__t20ArenaAbrirModalAtaquePreset(idx);
                    } else if (typeof window.__t20ArenaAbrirModalAtaque === 'function') {
                        window.__t20ArenaAbrirModalAtaque();
                    }
                });
            });
        }

        if (hint) {
            const ar = arenaRef();
            const viewId = ar && ar.viewId != null ? ar.viewId : null;
            const turnId = ar && ar.ordemIds.length ? ar.ordemIds[ar.turnoIdx] : null;
            if (viewId != null && turnId != null && Number(viewId) !== Number(turnId)) {
                hint.textContent = 'Visualizando outro combatente (turno ativo destacado na iniciativa).';
            } else {
                hint.textContent = 'Clique 🎲 para rolar com o preset do ataque.';
            }
        }
    }

    function ajustarUiPorTipo(p) {
        const npc = isNpcOuMonstro(p);
        const pmMax = Math.max(0, Number(p && p.pa_max) || 0);
        const pmCard = document.querySelector('.t20-arena-res-card--pm');
        if (pmCard) pmCard.hidden = pmMax <= 0;
        const btnMag = document.getElementById('t20ArenaBtnMagias');
        if (btnMag) btnMag.hidden = npc && pmMax <= 0;
        const main = document.querySelector('.t20-arena-main');
        if (main) main.classList.toggle('t20-arena-main--npc', npc);
    }

    function bindIniLista() {
        const ul = document.getElementById('t20ArenaIniList');
        if (!ul || ul.dataset.t20NpcIniBound) return;
        ul.dataset.t20NpcIniBound = '1';
        ul.addEventListener('click', (e) => {
            const li = e.target.closest('li[data-combatente-id]');
            if (!li) return;
            const ar = arenaRef();
            if (!ar) return;
            const id = Number(li.getAttribute('data-combatente-id'));
            if (!Number.isFinite(id)) return;
            ar.viewId = id;
            if (typeof window.__t20ArenaRenderActive === 'function') {
                window.__t20ArenaRenderActive();
            }
        });
    }

    function bindSeguirTurno() {
        const btn = document.getElementById('t20ArenaBtnSeguirTurno');
        if (!btn || btn.dataset.bound) return;
        btn.dataset.bound = '1';
        btn.addEventListener('click', () => {
            const ar = arenaRef();
            if (!ar) return;
            ar.viewId = null;
            if (typeof window.__t20ArenaRenderActive === 'function') {
                window.__t20ArenaRenderActive();
            }
        });
    }

    window.__t20ArenaNpcCompactRender = function (p, mask) {
        renderAtaques(p, mask);
        ajustarUiPorTipo(p);
        const ar = arenaRef();
        const btnSeguir = document.getElementById('t20ArenaBtnSeguirTurno');
        if (btnSeguir && ar) {
            const turnId = ar.ordemIds.length ? ar.ordemIds[ar.turnoIdx] : null;
            const viewing = ar.viewId != null && turnId != null && Number(ar.viewId) !== Number(turnId);
            btnSeguir.hidden = !viewing;
        }
    };

    window.__t20ArenaNpcCompactInit = function () {
        bindIniLista();
        bindSeguirTurno();
    };
})();
