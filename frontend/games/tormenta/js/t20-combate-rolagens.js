/**
 * Rolagens de combate Tormenta na arena — modais (paridade UX D&D 3.5, CSS Tormenta).
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

    function statsMascarados(ar) {
        return !!(ar && ar.ativo && !ar.statsVisiveis);
    }

    function arenaRefresh() {
        const ar = arenaRef();
        if (ar && typeof ar.refresh === 'function') return ar.refresh();
        if (typeof window.__t20ArenaRefreshFromApi === 'function') {
            return window.__t20ArenaRefreshFromApi();
        }
        return Promise.resolve();
    }

    function defaultAlvoInimigo(ar, excluirId) {
        const ids = ar.ordemIds || [];
        const inimigo = ids.find((id) => {
            if (excluirId != null && Number(id) === Number(excluirId)) return false;
            const p = ar.byId[id];
            const t = p ? String(p.tipo || '').toLowerCase() : '';
            return t === 'monstro' || t === 'npc';
        });
        if (inimigo != null) return inimigo;
        return ids.find((id) => excluirId == null || Number(id) !== Number(excluirId)) || null;
    }

    function parseFormulaDano(txt) {
        const s = String(txt || '')
            .trim()
            .replace(/\s+/g, '');
        const m = s.match(/^(\d+d\d+)([+-]\d+)?$/i);
        if (m) {
            return {
                formula: m[1].toLowerCase(),
                mod: m[2] ? Number(m[2]) : 0,
            };
        }
        return { formula: s || '1d8', mod: 0 };
    }

    function parseBonusNumero(txt) {
        const m = String(txt || '').match(/[-+]?\d+/);
        return m ? Number(m[0]) : 0;
    }

    function ataquesDaFicha(personagem) {
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
                return { nome: nome || `Ataque ${i + 1}`, bonus, dano: dano || '1d6' };
            })
            .filter(Boolean);
    }

    function popularListaAlvos(hostId, opts) {
        const host = document.getElementById(hostId);
        const ar = arenaRef();
        if (!host || !ar) return;
        const ids = ar.ordemIds || [];
        const ativoId = ids.length ? ids[ar.turnoIdx] : null;
        const mode = opts && opts.mode === 'radio' ? 'radio' : 'checkbox';
        const name = opts && opts.inputName ? opts.inputName : `t20alvo-${hostId}`;
        const excludeId = opts && opts.excludeId != null ? Number(opts.excludeId) : null;
        const defaultId = opts && opts.defaultId != null ? Number(opts.defaultId) : null;
        const permitirNenhum = !!(opts && opts.permitirNenhum);

        if (!ids.length) {
            host.innerHTML = '<p class="t20-arena-cb-vazio">Nenhum combatente no combate.</p>';
            return;
        }

        const linhas = [];
        if (permitirNenhum && mode === 'radio') {
            const ck = defaultId == null ? ' checked' : '';
            linhas.push(
                `<div class="t20-arena-cb-item"><input type="radio" class="t20-arena-cb-inp" name="${esc(name)}" id="${esc(hostId)}-none" value=""${ck} /><label class="t20-arena-cb-lbl" for="${esc(hostId)}-none"><span class="t20-arena-cb-nome">Nenhum (só rolar)</span></label></div>`
            );
        }

        ids.forEach((id) => {
            if (excludeId != null && Number(id) === excludeId) return;
            const p = ar.byId[id];
            const nome = p ? esc(p.nome) : `#${id}`;
            const tipo = p ? String(p.tipo || '').toLowerCase() : '';
            const mask = statsMascarados(ar);
            let pvSpan = '';
            if (tipo === 'jogador' && p && Number(p.pv_max) >= 0) {
                pvSpan = mask
                    ? '<span class="t20-arena-cb-hp t20-hp-oculto">???/??? PV</span>'
                    : `<span class="t20-arena-cb-hp">${esc(String(p.pv_atual))}/${esc(String(p.pv_max))} PV</span>`;
            }
            const caSpan =
                p && p.ca != null && !mask
                    ? `<span class="t20-arena-cb-hp">CA ${esc(String(p.ca))}</span>`
                    : '';
            const badge = tipo
                ? `<span class="t20-arena-cb-tipo t20-arena-cb-tipo--${esc(tipo)}">${esc(tipo)}</span>`
                : '';
            const sel =
                defaultId != null && Number(id) === defaultId ? ' checked' : '';
            const inpType = mode === 'radio' ? 'radio' : 'checkbox';
            linhas.push(
                `<div class="t20-arena-cb-item"><input type="${inpType}" class="t20-arena-cb-inp" name="${esc(name)}" id="${esc(hostId)}-${id}" value="${id}"${sel} /><label class="t20-arena-cb-lbl" for="${esc(hostId)}-${id}"><span class="t20-arena-cb-nome">${nome}</span>${pvSpan}${caSpan}${badge}</label></div>`
            );
        });

        host.innerHTML = linhas.length
            ? linhas.join('')
            : '<p class="t20-arena-cb-vazio">Nenhum alvo disponível.</p>';
    }

    function preencherSelectAtaques(selectId, personagem) {
        const sel = document.getElementById(selectId);
        if (!sel) return;
        const lista = ataquesDaFicha(personagem);
        sel.innerHTML =
            '<option value="">— Manual —</option>' +
            lista
                .map(
                    (a, i) =>
                        `<option value="${i}">${esc(a.nome)} · ${esc(a.bonus || '+0')} · ${esc(a.dano)}</option>`
                )
                .join('');
        sel.dataset.t20AtaquesJson = JSON.stringify(lista);
    }

    function ataquePresetSelecionado(selectId) {
        const sel = document.getElementById(selectId);
        if (!sel || sel.value === '') return null;
        let lista = [];
        try {
            lista = JSON.parse(sel.dataset.t20AtaquesJson || '[]');
        } catch (_e) {
            return null;
        }
        const idx = Number(sel.value);
        return Number.isFinite(idx) && lista[idx] ? lista[idx] : null;
    }

    function alvoIdSelecionado(hostId, inputName) {
        const el = document.querySelector(
            `#${hostId} input[name="${inputName}"]:checked`
        );
        if (!el || !String(el.value || '').trim()) return null;
        const id = Number(el.value);
        return Number.isFinite(id) && id > 0 ? id : null;
    }

    function renderResultadoAtaque(box, r) {
        if (!box) return;
        const crit =
            r.ameaca_critica && r.acertou
                ? ' · <strong>Ameaça de crítico</strong>'
                : r.falha_critica
                  ? ' · <strong>Falha crítica (1)</strong>'
                  : '';
        const hit = r.acertou
            ? '<span class="t20-arena-roll-ok">ACERTO</span>'
            : '<span class="t20-arena-roll-fail">ERRO</span>';
        box.innerHTML = `<p class="t20-arena-roll-result__tit">${esc(r.atacante_nome)} → ${esc(r.alvo_nome)}</p>
            <p class="t20-arena-roll-result__linha"><strong>${r.d20}</strong> + ${r.bonus} = <strong>${r.total}</strong> vs CA <strong>${r.ca_alvo}</strong> → ${hit}${crit}</p>`;
        box.hidden = false;
    }

    function renderResultadoDano(box, r, formula, mod) {
        if (!box) return;
        const rolls = (r.rolagens || []).join(' + ') || '—';
        let html = `<p class="t20-arena-roll-result__tit">Dano: <strong>${r.dano}</strong>${r.critico ? ' (crítico)' : ''}</p>
            <p class="t20-arena-roll-result__linha">${esc(formula)}${mod ? ` + ${mod}` : ''} · dados: ${esc(rolls)}</p>`;
        if (r.alvo_nome != null && r.pv_antes != null) {
            html += `<p class="t20-arena-roll-result__linha">${esc(r.alvo_nome)}: PV ${r.pv_antes} → <strong>${r.pv_depois}</strong></p>`;
        }
        if (r.concentracao && r.concentracao.tinha_concentracao) {
            const t = r.concentracao.teste || {};
            const conc = r.concentracao.perdida
                ? `Concentração perdida (${esc(r.concentracao.magia_anterior || '')})`
                : `Manteve concentração (${esc(r.concentracao.magia_anterior || '')})`;
            html += `<p class="t20-arena-roll-result__linha t20-arena-roll-result__hint">${conc}: ${t.d20}+${t.bonus}=${t.total} vs CD ${t.dc}</p>`;
        }
        box.innerHTML = html;
        box.hidden = false;
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
            await arenaRefresh();
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro');
        }
    }

    function abrirModalAtaque() {
        const ar = arenaRef();
        if (!ar || !ar.ativo || !ar.ordemIds.length) {
            if (typeof Toast !== 'undefined') Toast.error('Inicie o combate antes.');
            return;
        }
        const dlg = document.getElementById('t20ArenaModalAtaque');
        if (!dlg) return;
        const ativoId = ar.ordemIds[ar.turnoIdx];
        const alvoDefault = defaultAlvoInimigo(ar, ativoId);
        popularListaAlvos('t20ArenaAtaqueListaAlvos', {
            mode: 'radio',
            inputName: 't20ataque-alvo',
            excludeId: ativoId,
            defaultId: alvoDefault,
        });
        const atacante = ar.byId[ativoId];
        preencherSelectAtaques('t20ArenaAtaquePreset', atacante);
        const resBox = document.getElementById('t20ArenaAtaqueResultado');
        if (resBox) {
            resBox.hidden = true;
            resBox.innerHTML = '';
        }
        const set = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.value = String(val);
        };
        set('t20ArenaAtaqueBab', 0);
        set('t20ArenaAtaqueMod', 0);
        set('t20ArenaAtaqueBonusArma', 0);
        set('t20ArenaAtaquePenal', 0);
        const ca = document.getElementById('t20ArenaAtaqueCa');
        if (ca) ca.value = '';
        sincronizarCaAlvoAtaque();
        if (typeof dlg.showModal === 'function') dlg.showModal();
    }

    function fecharModalAtaque() {
        const dlg = document.getElementById('t20ArenaModalAtaque');
        if (dlg && typeof dlg.close === 'function') dlg.close();
    }

    async function confirmarRolarAtaque() {
        const ar = arenaRef();
        if (!ar || !ar.ativo) return;
        const ativoId = ar.ordemIds[ar.turnoIdx];
        const alvoId = alvoIdSelecionado('t20ArenaAtaqueListaAlvos', 't20ataque-alvo');
        if (!alvoId) {
            if (typeof Toast !== 'undefined') Toast.error('Escolha um alvo.');
            return;
        }
        const bab = Number(document.getElementById('t20ArenaAtaqueBab')?.value) || 0;
        const mod = Number(document.getElementById('t20ArenaAtaqueMod')?.value) || 0;
        const bonusArma = Number(document.getElementById('t20ArenaAtaqueBonusArma')?.value) || 0;
        const penal = Number(document.getElementById('t20ArenaAtaquePenal')?.value) || 0;
        const caRaw = document.getElementById('t20ArenaAtaqueCa')?.value;
        const caAlvo =
            caRaw != null && String(caRaw).trim() !== ''
                ? Number(caRaw)
                : undefined;
        try {
            const payload = {
                atacante_id: ativoId,
                alvo_id: alvoId,
                bab,
                mod_atributo: mod,
                bonus_arma: bonusArma,
                penalidades: penal,
            };
            if (caAlvo != null && Number.isFinite(caAlvo)) payload.ca_alvo = caAlvo;
            const r = await combate().rolarAtaque(payload);
            renderResultadoAtaque(document.getElementById('t20ArenaAtaqueResultado'), r);
            const msg = `${r.atacante_nome} → ${r.alvo_nome}: ${r.d20}+${r.bonus}=${r.total} vs CA ${r.ca_alvo} → ${r.acertou ? 'ACERTO' : 'ERRO'}`;
            if (typeof Toast !== 'undefined') Toast.info(msg);
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro ao rolar ataque');
        }
    }

    function abrirModalDano() {
        const ar = arenaRef();
        if (!ar || !ar.ativo || !ar.ordemIds.length) {
            if (typeof Toast !== 'undefined') Toast.error('Inicie o combate antes.');
            return;
        }
        const dlg = document.getElementById('t20ArenaModalDano');
        if (!dlg) return;
        const ativoId = ar.ordemIds[ar.turnoIdx];
        const alvoDefault = defaultAlvoInimigo(ar, null);
        const aplicarPv = document.getElementById('t20ArenaDanoAplicarPv');
        const aplicarChecked = aplicarPv ? aplicarPv.checked : true;
        popularListaAlvos('t20ArenaDanoListaAlvos', {
            mode: 'radio',
            inputName: 't20dano-alvo',
            defaultId: aplicarChecked ? alvoDefault : null,
            permitirNenhum: true,
        });
        const atacante = ar.byId[ativoId];
        preencherSelectAtaques('t20ArenaDanoPreset', atacante);
        const resBox = document.getElementById('t20ArenaDanoResultado');
        if (resBox) {
            resBox.hidden = true;
            resBox.innerHTML = '';
        }
        const form = document.getElementById('t20ArenaDanoFormula');
        if (form) form.value = '1d8';
        const mod = document.getElementById('t20ArenaDanoMod');
        if (mod) mod.value = '0';
        const crit = document.getElementById('t20ArenaDanoCritico');
        if (crit) crit.checked = false;
        const apl = document.getElementById('t20ArenaDanoAplicarPv');
        if (apl) apl.checked = true;
        if (typeof dlg.showModal === 'function') dlg.showModal();
    }

    function fecharModalDano() {
        const dlg = document.getElementById('t20ArenaModalDano');
        if (dlg && typeof dlg.close === 'function') dlg.close();
    }

    async function confirmarRolarDano() {
        const ar = arenaRef();
        if (!ar || !ar.ativo) return;
        const formula = String(document.getElementById('t20ArenaDanoFormula')?.value || '').trim();
        if (!formula) {
            if (typeof Toast !== 'undefined') Toast.error('Informe a fórmula de dano.');
            return;
        }
        const mod = Number(document.getElementById('t20ArenaDanoMod')?.value) || 0;
        const critico = !!document.getElementById('t20ArenaDanoCritico')?.checked;
        const aplicarPv = !!document.getElementById('t20ArenaDanoAplicarPv')?.checked;
        const alvoId = alvoIdSelecionado('t20ArenaDanoListaAlvos', 't20dano-alvo');
        if (aplicarPv && !alvoId) {
            if (typeof Toast !== 'undefined') Toast.error('Marque um alvo ou desative «Aplicar dano».');
            return;
        }
        try {
            const r = await combate().rolarDano({
                formula_dano: formula,
                mod_atributo: mod,
                confirmar_critico: critico,
                aplicar_ao_alvo_id: aplicarPv && alvoId ? alvoId : null,
            });
            renderResultadoDano(
                document.getElementById('t20ArenaDanoResultado'),
                r,
                formula,
                mod
            );
            let msg = `Dano: ${r.dano}`;
            if (r.pv_antes != null) msg += ` · PV ${r.pv_antes}→${r.pv_depois}`;
            if (typeof Toast !== 'undefined') Toast.info(msg);
            await arenaRefresh();
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro ao rolar dano');
        }
    }

    function aplicarPresetAtaque(selectId, bonusArmaId, danoFormulaId, danoModId) {
        const preset = ataquePresetSelecionado(selectId);
        if (!preset) return;
        const bonus = parseBonusNumero(preset.bonus);
        const bonusEl = document.getElementById(bonusArmaId);
        if (bonusEl) bonusEl.value = String(bonus);
        if (danoFormulaId && preset.dano) {
            const parsed = parseFormulaDano(preset.dano);
            const f = document.getElementById(danoFormulaId);
            if (f) f.value = parsed.formula;
            if (danoModId) {
                const modEl = document.getElementById(danoModId);
                if (modEl) modEl.value = String(parsed.mod);
            }
        }
    }

    function sincronizarCaAlvoAtaque() {
        const ar = arenaRef();
        if (!ar) return;
        const alvoId = alvoIdSelecionado('t20ArenaAtaqueListaAlvos', 't20ataque-alvo');
        const ca = document.getElementById('t20ArenaAtaqueCa');
        if (!ca || !alvoId) return;
        const p = ar.byId[alvoId];
        if (p && p.ca != null && !statsMascarados(ar)) {
            ca.value = String(p.ca);
        }
    }

    function aoToggleAplicarPvDano() {
        const aplicar = !!document.getElementById('t20ArenaDanoAplicarPv')?.checked;
        const none = document.getElementById('t20ArenaDanoListaAlvos-none');
        if (!aplicar && none) {
            none.checked = true;
            return;
        }
        if (aplicar && none?.checked) {
            const ar = arenaRef();
            if (!ar) return;
            const alvo = defaultAlvoInimigo(ar, null);
            if (alvo != null) {
                const el = document.getElementById(`t20ArenaDanoListaAlvos-${alvo}`);
                if (el) el.checked = true;
            }
        }
    }

    function personagemSvc() {
        return new TormentaPersonagemService();
    }

    function regrasSvc() {
        return new TormentaRegrasService();
    }

    function inferirTipoResistencia(txt) {
        const t = String(txt || '').toLowerCase();
        if (!t.trim() || t.includes('nenhum')) return '';
        if (t.includes('fortitude') || /\bfort\b/.test(t)) return 'fortitude';
        if (t.includes('reflex') || /\bref\b/.test(t)) return 'reflexos';
        if (t.includes('vontade') || /\bvon\b/.test(t)) return 'vontade';
        return '';
    }

    function popularSelectCombatentes(selectId, defaultId) {
        const sel = document.getElementById(selectId);
        const ar = arenaRef();
        if (!sel || !ar) return;
        const ids = ar.ordemIds || [];
        if (!ids.length) {
            sel.innerHTML = '<option value="">—</option>';
            return;
        }
        sel.innerHTML = ids
            .map((id) => {
                const p = ar.byId[id];
                const nome = p ? esc(p.nome) : `#${id}`;
                const selAttr = defaultId != null && Number(id) === Number(defaultId) ? ' selected' : '';
                return `<option value="${id}"${selAttr}>${nome}</option>`;
            })
            .join('');
    }

    function magiasLancaveisSr(magias) {
        const arr = Array.isArray(magias) ? magias : [];
        const out = [];
        const seen = new Set();
        arr.forEach((m) => {
            const slug = String(m.magia_slug || '').trim().toLowerCase();
            const pap = String(m.papel || '').trim().toLowerCase();
            if (!slug || seen.has(slug)) return;
            if (pap === 'conhecida' || pap === 'preparada') {
                seen.add(slug);
                out.push(m);
                return;
            }
            if (pap === 'grimorio' && (Number(m.circulo) === 0 || !Number.isFinite(Number(m.circulo)))) {
                seen.add(slug);
                out.push(m);
            }
        });
        return out.sort((a, b) => {
            const ca = Number(a.circulo) || 0;
            const cb = Number(b.circulo) || 0;
            if (ca !== cb) return ca - cb;
            return String(a.nome || a.magia_slug).localeCompare(String(b.nome || b.magia_slug), 'pt');
        });
    }

    async function carregarMagiasConjuradorSr(conjId) {
        const sel = document.getElementById('t20ArenaSrMagia');
        if (!sel) return;
        sel.innerHTML = '<option value="">— Manual —</option>';
        sel.dataset.magiasJson = '[]';
        if (!conjId) return;
        try {
            const lista = magiasLancaveisSr(await personagemSvc().listarMagias(conjId));
            sel.dataset.magiasJson = JSON.stringify(lista);
            sel.innerHTML =
                '<option value="">— Manual —</option>' +
                lista
                    .map((m) => {
                        const slug = esc(String(m.magia_slug || '').toLowerCase());
                        const nome = esc(m.nome || m.magia_slug || slug);
                        const circ = m.circulo != null ? `C${m.circulo}` : '';
                        return `<option value="${slug}">${nome} · ${circ}</option>`;
                    })
                    .join('');
        } catch (_e) {
            /* mantém manual */
        }
    }

    async function aplicarMetaMagiaSr(slug) {
        const s = String(slug || '').trim().toLowerCase();
        if (!s) return;
        let circ = null;
        try {
            const lista = JSON.parse(
                document.getElementById('t20ArenaSrMagia')?.dataset.magiasJson || '[]'
            );
            const local = (lista || []).find(
                (m) => String(m.magia_slug || '').toLowerCase() === s
            );
            if (local && local.circulo != null) circ = Number(local.circulo);
        } catch (_e) {
            /* ignore */
        }
        try {
            const res = await regrasSvc().listarMagiasCatalogo({ q: s, limit: 30 });
            const item = (res.itens || []).find(
                (m) => String(m.slug || '').toLowerCase() === s
            );
            if (item) {
                if (item.circulo != null) circ = Number(item.circulo);
                const tipo = inferirTipoResistencia(item.resistencia);
                const tipoEl = document.getElementById('t20ArenaSrTipo');
                if (tipo && tipoEl) tipoEl.value = tipo;
            }
        } catch (_e) {
            /* ignore */
        }
        if (circ != null && Number.isFinite(circ)) {
            const cEl = document.getElementById('t20ArenaSrCirculo');
            if (cEl) cEl.value = String(circ);
        }
    }

    function sincronizarCdManualSr() {
        const manual = !!document.getElementById('t20ArenaSrCdManual')?.checked;
        const wrap = document.getElementById('t20ArenaSrCdWrap');
        if (wrap) wrap.hidden = !manual;
    }

    function atualizarBonusAlvoSr() {
        const hint = document.getElementById('t20ArenaSrBonusAlvo');
        const ar = arenaRef();
        if (!hint || !ar) return;
        const alvoId = alvoIdSelecionado('t20ArenaSrListaAlvos', 't20sr-alvo');
        if (!alvoId) {
            hint.hidden = true;
            hint.textContent = '';
            return;
        }
        const p = ar.byId[alvoId];
        if (!p) {
            hint.hidden = true;
            return;
        }
        const mask = statsMascarados(ar);
        if (mask) {
            hint.hidden = false;
            hint.textContent = 'Bônus de resistência ocultos (revele stats na mesa).';
            return;
        }
        hint.hidden = false;
        hint.innerHTML = `Fort <strong>${esc(String(p.fort_total ?? '—'))}</strong> · Ref <strong>${esc(String(p.ref_total ?? '—'))}</strong> · Von <strong>${esc(String(p.von_total ?? '—'))}</strong>`;
    }

    function renderResultadoSr(box, r) {
        if (!box) return;
        if (r.falha_voluntaria) {
            box.innerHTML = `<p class="t20-arena-roll-result__tit">${esc(r.alvo_nome)} — falha voluntária</p>
                <p class="t20-arena-roll-result__linha">O alvo não resistiu à magia${r.conjurador_nome ? ` de ${esc(r.conjurador_nome)}` : ''}.</p>`;
            box.hidden = false;
            return;
        }
        const pass = !!(r.passou || r.sucesso);
        const hit = pass
            ? '<span class="t20-arena-roll-ok">PASSOU</span>'
            : '<span class="t20-arena-roll-fail">FALHOU</span>';
        const rm =
            r.bonus_resistencia_magia > 0
                ? ` (+${r.bonus_resistencia_magia} RM)`
                : '';
        const tipoLbl = esc(String(r.tipo || '').replace(/^./, (c) => c.toUpperCase()));
        box.innerHTML = `<p class="t20-arena-roll-result__tit">${esc(r.alvo_nome)} · ${tipoLbl}</p>
            <p class="t20-arena-roll-result__linha"><strong>${r.d20}</strong> + ${r.bonus_total} (${r.bonus_base}${rm}) = <strong>${r.total}</strong> vs CD <strong>${r.cd}</strong> → ${hit}</p>
            ${r.conjurador_nome ? `<p class="t20-arena-roll-result__hint">Conjurador: ${esc(r.conjurador_nome)}${r.magia_slug ? ` · ${esc(r.magia_slug)}` : ''}</p>` : ''}`;
        box.hidden = false;
    }

    async function abrirModalResistenciaMagia() {
        const ar = arenaRef();
        if (!ar || !ar.ativo || !ar.ordemIds.length) {
            if (typeof Toast !== 'undefined') Toast.error('Inicie o combate antes.');
            return;
        }
        const dlg = document.getElementById('t20ArenaModalResistenciaMagia');
        if (!dlg) return;
        const ativoId = ar.ordemIds[ar.turnoIdx];
        const alvoDefault = defaultAlvoInimigo(ar, ativoId);
        popularListaAlvos('t20ArenaSrListaAlvos', {
            mode: 'radio',
            inputName: 't20sr-alvo',
            defaultId: alvoDefault,
        });
        popularSelectCombatentes('t20ArenaSrConjurador', ativoId);
        const resBox = document.getElementById('t20ArenaSrResultado');
        if (resBox) {
            resBox.hidden = true;
            resBox.innerHTML = '';
        }
        const tipo = document.getElementById('t20ArenaSrTipo');
        if (tipo) tipo.value = '';
        const circ = document.getElementById('t20ArenaSrCirculo');
        if (circ) circ.value = '1';
        const cdManual = document.getElementById('t20ArenaSrCdManual');
        if (cdManual) cdManual.checked = false;
        const cd = document.getElementById('t20ArenaSrCd');
        if (cd) cd.value = '';
        const falha = document.getElementById('t20ArenaSrFalhaVol');
        if (falha) falha.checked = false;
        sincronizarCdManualSr();
        atualizarBonusAlvoSr();
        await carregarMagiasConjuradorSr(ativoId);
        if (typeof dlg.showModal === 'function') dlg.showModal();
    }

    function fecharModalResistenciaMagia() {
        const dlg = document.getElementById('t20ArenaModalResistenciaMagia');
        if (dlg && typeof dlg.close === 'function') dlg.close();
    }

    async function confirmarRolarResistenciaMagia() {
        const ar = arenaRef();
        if (!ar || !ar.ativo) return;
        const alvoId = alvoIdSelecionado('t20ArenaSrListaAlvos', 't20sr-alvo');
        if (!alvoId) {
            if (typeof Toast !== 'undefined') Toast.error('Escolha quem faz o teste.');
            return;
        }
        const conjId = Number(document.getElementById('t20ArenaSrConjurador')?.value);
        const tipo = String(document.getElementById('t20ArenaSrTipo')?.value || '').trim();
        const magiaSlug = String(document.getElementById('t20ArenaSrMagia')?.value || '').trim();
        const falhaVol = !!document.getElementById('t20ArenaSrFalhaVol')?.checked;
        const cdManual = !!document.getElementById('t20ArenaSrCdManual')?.checked;
        if (!tipo && !magiaSlug) {
            if (typeof Toast !== 'undefined') {
                Toast.error('Informe o tipo de teste ou escolha uma magia.');
            }
            return;
        }
        const payload = {
            alvo_id: alvoId,
            falha_voluntaria: falhaVol,
        };
        if (tipo) payload.tipo = tipo;
        if (magiaSlug) payload.magia_slug = magiaSlug;
        if (!falhaVol) {
            if (cdManual) {
                const cdVal = Number(document.getElementById('t20ArenaSrCd')?.value);
                if (!Number.isFinite(cdVal) || cdVal < 1) {
                    if (typeof Toast !== 'undefined') Toast.error('Informe a CD do teste.');
                    return;
                }
                payload.cd = cdVal;
            } else {
                if (!Number.isFinite(conjId) || conjId <= 0) {
                    if (typeof Toast !== 'undefined') Toast.error('Escolha o conjurador.');
                    return;
                }
                payload.conjurador_id = conjId;
                const circVal = document.getElementById('t20ArenaSrCirculo')?.value;
                if (circVal != null && String(circVal).trim() !== '') {
                    payload.circulo_magia = Number(circVal);
                }
            }
        }
        try {
            const r = await combate().testarResistenciaMagia(payload);
            renderResultadoSr(document.getElementById('t20ArenaSrResultado'), r);
            let msg;
            if (r.falha_voluntaria) {
                msg = `${r.alvo_nome}: falha voluntária`;
            } else {
                const pass = r.passou || r.sucesso;
                msg = `${r.alvo_nome}: ${r.d20}+${r.bonus_total}=${r.total} vs CD ${r.cd} → ${pass ? 'PASSOU' : 'FALHOU'}`;
            }
            if (typeof Toast !== 'undefined') Toast.info(msg);
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro no teste de resistência');
        }
    }

    function init() {
        document.getElementById('t20ArenaBtnRolarIniciativa')?.addEventListener('click', rolarIniciativaTodos);
        document.getElementById('t20ArenaBtnRolarAtaque')?.addEventListener('click', abrirModalAtaque);
        document.getElementById('t20ArenaBtnRolarDano')?.addEventListener('click', abrirModalDano);
        document.getElementById('t20ArenaBtnResistenciaMagia')?.addEventListener('click', abrirModalResistenciaMagia);

        document.getElementById('t20ArenaModalAtaqueFechar')?.addEventListener('click', fecharModalAtaque);
        document.getElementById('t20ArenaModalAtaqueCancelar')?.addEventListener('click', fecharModalAtaque);
        document.getElementById('t20ArenaModalAtaqueRolar')?.addEventListener('click', confirmarRolarAtaque);

        document.getElementById('t20ArenaModalDanoFechar')?.addEventListener('click', fecharModalDano);
        document.getElementById('t20ArenaModalDanoCancelar')?.addEventListener('click', fecharModalDano);
        document.getElementById('t20ArenaModalDanoRolar')?.addEventListener('click', confirmarRolarDano);

        document.getElementById('t20ArenaModalResistenciaMagiaFechar')?.addEventListener('click', fecharModalResistenciaMagia);
        document.getElementById('t20ArenaModalResistenciaMagiaCancelar')?.addEventListener('click', fecharModalResistenciaMagia);
        document.getElementById('t20ArenaModalResistenciaMagiaRolar')?.addEventListener('click', confirmarRolarResistenciaMagia);

        document.getElementById('t20ArenaAtaquePreset')?.addEventListener('change', () => {
            aplicarPresetAtaque('t20ArenaAtaquePreset', 't20ArenaAtaqueBonusArma', null, null);
        });
        document.getElementById('t20ArenaDanoPreset')?.addEventListener('change', () => {
            aplicarPresetAtaque(
                't20ArenaDanoPreset',
                't20ArenaDanoMod',
                't20ArenaDanoFormula',
                't20ArenaDanoMod'
            );
        });

        document.getElementById('t20ArenaAtaqueListaAlvos')?.addEventListener('change', (e) => {
            if (e.target && e.target.matches('input[type="radio"]')) sincronizarCaAlvoAtaque();
        });
        document.getElementById('t20ArenaDanoAplicarPv')?.addEventListener('change', aoToggleAplicarPvDano);

        document.getElementById('t20ArenaSrConjurador')?.addEventListener('change', (e) => {
            carregarMagiasConjuradorSr(Number(e.target.value));
        });
        document.getElementById('t20ArenaSrMagia')?.addEventListener('change', (e) => {
            aplicarMetaMagiaSr(e.target.value);
        });
        document.getElementById('t20ArenaSrCdManual')?.addEventListener('change', sincronizarCdManualSr);
        document.getElementById('t20ArenaSrListaAlvos')?.addEventListener('change', (e) => {
            if (e.target && e.target.matches('input[type="radio"]')) atualizarBonusAlvoSr();
        });

        ['t20ArenaModalAtaque', 't20ArenaModalDano', 't20ArenaModalResistenciaMagia'].forEach((id) => {
            const dlg = document.getElementById(id);
            if (!dlg) return;
            dlg.addEventListener('click', (e) => {
                if (e.target === dlg) dlg.close();
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window.__t20ArenaAbrirModalAtaque = abrirModalAtaque;
    window.__t20ArenaAbrirModalDano = abrirModalDano;
    window.__t20ArenaAbrirModalResistenciaMagia = abrirModalResistenciaMagia;
})();
