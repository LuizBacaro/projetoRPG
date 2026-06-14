/**
 * Rolagens de combate Tormenta na arena (iniciativa, ataque, dano).
 */
(function () {
    const combate = () => new TormentaCombateService();

    function esc(s) {
        return String(s ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;');
    }

    function arenaRef() {
        return window.__t20ArenaRef;
    }

    async function rolarIniciativaTodos() {
        const ar = arenaRef();
        if (!ar || !ar.ativo || !ar.ordemIds.length) {
            if (typeof Toast !== 'undefined') Toast.error('Inicie o combate antes.');
            return;
        }
        try {
            const res = await combate().rolarIniciativa(ar.ordemIds);
            if (typeof Toast !== 'undefined') {
                const linhas = (res.resultados || [])
                    .map((r) => `${esc(r.nome)}: ${r.d20}+${r.modificador}=${r.total}`)
                    .join(' · ');
                Toast.info(`Iniciativa: ${linhas}`);
            }
            if (typeof ar.refresh === 'function') await ar.refresh();
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro');
        }
    }

    async function rolarAtaquePrompt() {
        const ar = arenaRef();
        if (!ar || !ar.ativo) return;
        const ativoId = ar.ordemIds[ar.turnoIdx];
        const alvoId = window.prompt('ID do alvo (personagem):', String(ar.ordemIds.find((id) => id !== ativoId) || ''));
        if (!alvoId) return;
        const bab = Number(window.prompt('BAB:', '0')) || 0;
        const mod = Number(window.prompt('Mod. atributo (FOR/DES):', '0')) || 0;
        try {
            const r = await combate().rolarAtaque({
                atacante_id: ativoId,
                alvo_id: Number(alvoId),
                bab,
                mod_atributo: mod,
            });
            const msg = `${r.atacante_nome} → ${r.alvo_nome}: ${r.d20}+${r.bonus}=${r.total} vs CA ${r.ca_alvo} → ${r.acertou ? 'ACERTO' : 'ERRO'}`;
            if (typeof Toast !== 'undefined') Toast.info(msg);
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro');
        }
    }

    async function rolarDanoPrompt() {
        const ar = arenaRef();
        if (!ar || !ar.ativo) return;
        const formula = window.prompt('Fórmula de dano (ex. 1d8):', '1d8');
        if (!formula) return;
        const mod = Number(window.prompt('Mod. FOR (CAC):', '0')) || 0;
        const aplicar = window.confirm('Aplicar dano ao alvo ativo?');
        const alvoId = aplicar ? ar.ordemIds[ar.turnoIdx] : null;
        try {
            const r = await combate().rolarDano({
                formula_dano: formula,
                mod_atributo: mod,
                aplicar_ao_alvo_id: alvoId,
            });
            let msg = `Dano: ${r.dano} (${formula}${mod ? `+${mod}` : ''})`;
            if (r.pv_antes != null) msg += ` · PV ${r.pv_antes}→${r.pv_depois}`;
            if (r.concentracao && r.concentracao.tinha_concentracao) {
                const t = r.concentracao.teste || {};
                const concMsg = r.concentracao.perdida
                    ? `Concentração perdida (${r.concentracao.magia_anterior || '—'}): ${t.d20}+${t.bonus}=${t.total} vs CD ${t.dc}`
                    : `Manteve concentração (${r.concentracao.magia_anterior || '—'}): ${t.d20}+${t.bonus}=${t.total} vs CD ${t.dc}`;
                msg += ` · ${concMsg}`;
            }
            if (typeof Toast !== 'undefined') Toast.info(msg);
            if (typeof ar.refresh === 'function') await ar.refresh();
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro');
        }
    }

    async function testarResistenciaMagiaPrompt() {
        const ar = arenaRef();
        if (!ar || !ar.ativo) return;
        const alvoId = window.prompt('ID do alvo:', String(ar.ordemIds[ar.turnoIdx] || ''));
        if (!alvoId) return;
        const tipo = window.prompt('Tipo (fortitude/reflexos/vontade):', 'vontade');
        if (!tipo) return;
        const usarCd = window.confirm('Informar CD manualmente? (Cancelar = calcular por círculo + conjurador)');
        let payload = { alvo_id: Number(alvoId), tipo };
        if (usarCd) {
            const cd = Number(window.prompt('CD do teste:', '15'));
            if (!Number.isFinite(cd)) return;
            payload.cd = cd;
        } else {
            const circ = Number(window.prompt('Círculo da magia:', '3'));
            const conjId = window.prompt('ID do conjurador:', String(ar.ordemIds[0] || ''));
            if (!conjId || !Number.isFinite(circ)) return;
            payload.circulo_magia = circ;
            payload.conjurador_id = Number(conjId);
        }
        try {
            const r = await combate().testarResistenciaMagia(payload);
            const rm = r.bonus_resistencia_magia ? ` (+${r.bonus_resistencia_magia} RM)` : '';
            const msg = r.falha_voluntaria
                ? `${r.alvo_nome}: falha voluntária vs CD ${r.cd}`
                : `${r.alvo_nome}: ${r.d20}+${r.bonus_total}${rm}=${r.total} vs CD ${r.cd} → ${r.passou ? 'PASSOU' : 'FALHOU'}`;
            if (typeof Toast !== 'undefined') Toast.info(msg);
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro');
        }
    }

    function bindArenaRollButtons() {
        const bar = document.querySelector('.t20-arena-quick-btns');
        if (!bar || bar.dataset.rollBound) return;
        bar.dataset.rollBound = '1';
        const mk = (label, fn) => {
            const b = document.createElement('button');
            b.type = 'button';
            b.className = 'tormenta-btn';
            b.textContent = label;
            b.addEventListener('click', fn);
            return b;
        };
        bar.appendChild(mk('Rolar iniciativa', rolarIniciativaTodos));
        bar.appendChild(mk('Rolar ataque', rolarAtaquePrompt));
        bar.appendChild(mk('Rolar dano', rolarDanoPrompt));
        bar.appendChild(mk('Teste resist. magia', testarResistenciaMagiaPrompt));
    }

    document.addEventListener('DOMContentLoaded', () => {
        bindArenaRollButtons();
        const obs = new MutationObserver(bindArenaRollButtons);
        const root = document.getElementById('t20ArenaActive');
        if (root) obs.observe(root, { attributes: true, attributeFilter: ['hidden'] });
    });
})();
