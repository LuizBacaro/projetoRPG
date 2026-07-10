/**
 * RF-T12d — rolagem de perícia na arena com modificadores de condição.
 */
(function () {
    const regras = () => new TormentaRegrasService();

    function esc(s) {
        return String(s ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;');
    }

    function arenaRef() {
        return window.__t20ArenaRef;
    }

    function registrarLog(texto) {
        if (window.T20ArenaLogMesa && typeof window.T20ArenaLogMesa.append === 'function') {
            window.T20ArenaLogMesa.append('pericia', texto);
            return;
        }
        if (!texto) return;
        const arr = window.__t20LogMesa || [];
        arr.unshift({ ts: Date.now(), texto: String(texto) });
        if (arr.length > 12) arr.length = 12;
        window.__t20LogMesa = arr;
    }

    function rotulosCondicoes(personagemId) {
        const ar = arenaRef();
        if (!ar || personagemId == null) return [];
        const rec = ar.condPorId && ar.condPorId[personagemId];
        if (!rec || !Array.isArray(rec.rotulos)) return [];
        return rec.rotulos.filter(Boolean);
    }

    function regraVersaoDe(p) {
        const fj = p && p.ficha_json;
        if (fj && fj.regra_versao) return String(fj.regra_versao);
        if (window.T20RegraVersao) return window.T20RegraVersao.DEFAULT_NOVA_FICHA || 'v13';
        return 'v13';
    }

    function periciasDoPersonagem(p) {
        const fj = p && p.ficha_json;
        const raw = fj && Array.isArray(fj.pericias) ? fj.pericias : [];
        const lista = raw
            .map((row, i) => {
                if (!row || typeof row !== 'object') return null;
                const nome = String(row.nome || '').trim();
                if (!nome) return null;
                const slug = nome
                    .normalize('NFD')
                    .replace(/[\u0300-\u036f]/g, '')
                    .toLowerCase()
                    .replace(/[^a-z0-9]+/g, '_')
                    .replace(/^_|_$/g, '');
                return {
                    nome,
                    slug: slug || `pericia_${i}`,
                    treinado: Boolean(row.treinado),
                    mod_atributo: Number(row.mod_atributo) || 0,
                    outros: Number(row.outros) || 0,
                    graduacao: Number(row.graduacao != null ? row.graduacao : row.total) || 0,
                    somente_treinado: Boolean(row.somente_treinado),
                };
            })
            .filter(Boolean);
        const saves = [
            { nome: 'Fortitude', slug: 'fortitude', treinado: true, bonus_fixo: Number(p.fort_total) || 0 },
            { nome: 'Reflexos', slug: 'reflexos', treinado: true, bonus_fixo: Number(p.ref_total) || 0 },
            { nome: 'Vontade', slug: 'vontade', treinado: true, bonus_fixo: Number(p.von_total) || 0 },
        ];
        return { pericias: lista, saves };
    }

    function popularSelectPericias(p) {
        const sel = document.getElementById('t20ArenaPericiaSelect');
        if (!sel) return;
        const { pericias, saves } = periciasDoPersonagem(p);
        const opts = [];
        if (saves.length) {
            opts.push('<optgroup label="Resistências">');
            saves.forEach((s) => {
                opts.push(
                    `<option value="save:${s.slug}" data-slug="${esc(s.slug)}">${esc(s.nome)} (${s.bonus_fixo >= 0 ? '+' : ''}${s.bonus_fixo})</option>`
                );
            });
            opts.push('</optgroup>');
        }
        if (pericias.length) {
            opts.push('<optgroup label="Perícias da ficha">');
            pericias.forEach((row, i) => {
                const tre = row.treinado ? 'tr' : 'n-tr';
                opts.push(
                    `<option value="per:${i}" data-slug="${esc(row.slug)}">${esc(row.nome)} (${tre})</option>`
                );
            });
            opts.push('</optgroup>');
        }
        sel.innerHTML =
            opts.length > 0
                ? '<option value="">— Escolha —</option>' + opts.join('')
                : '<option value="">Sem perícias na ficha</option>';
        sel.dataset.t20PericiasJson = JSON.stringify({ pericias, saves });
    }

    async function modCondicaoPericia(slug, rotulos, rv) {
        if (!rotulos.length) return 0;
        try {
            const r = await regras().condicoesModificadores({
                rotulos,
                pericia_slug: slug,
                regra_versao: rv,
            });
            return Number(r.pericia) || 0;
        } catch (_e) {
            return 0;
        }
    }

    async function bonusPericiaSelecionada(p, valorSel) {
        const sel = document.getElementById('t20ArenaPericiaSelect');
        let data = { pericias: [], saves: [] };
        try {
            data = JSON.parse(sel?.dataset.t20PericiasJson || '{}');
        } catch (_e) {
            /* ignore */
        }
        const rv = regraVersaoDe(p);
        const isV13 = window.T20RegraVersao && window.T20RegraVersao.isV13(rv);

        if (String(valorSel).startsWith('save:')) {
            const slug = valorSel.slice(5);
            const save = (data.saves || []).find((s) => s.slug === slug);
            return {
                nome: save ? save.nome : slug,
                slug,
                bonus: save ? Number(save.bonus_fixo) || 0 : 0,
                pode_usar: true,
                origem: 'resistencia',
            };
        }

        const idx = Number(String(valorSel).replace('per:', ''));
        const row = Number.isFinite(idx) ? (data.pericias || [])[idx] : null;
        if (!row) throw new Error('Perícia inválida.');

        if (row.somente_treinado && !row.treinado) {
            return {
                nome: row.nome,
                slug: row.slug,
                bonus: 0,
                pode_usar: false,
                motivo_bloqueio: `${row.nome}: somente treinada.`,
            };
        }

        const fj = p.ficha_json || {};
        const body = {
            nivel: Number(p.nivel) || 1,
            mod_atributo: row.mod_atributo,
            treinado: row.treinado,
            graduacao: isV13 ? 0 : row.graduacao,
            outros: isV13 ? row.outros + row.graduacao : row.outros,
            racial_bonus: 0,
            slug_raca: fj.raca_tormenta_slug || '',
            nome_pericia: row.nome,
            pericia_de_classe: false,
            regra_versao: rv,
        };
        if (isV13 && fj.tormenta_classe_mb_slug) {
            body.tormenta_classe_mb_slug = String(fj.tormenta_classe_mb_slug);
        }
        const calc = await regras().calcularBonusPericia(body);
        return {
            nome: row.nome,
            slug: row.slug,
            bonus: Number(calc.bonus_total) || 0,
            pode_usar: calc.pode_usar !== false,
            motivo_bloqueio: calc.motivo_bloqueio || '',
            calc,
        };
    }

    function abrirModalPericia() {
        const ar = arenaRef();
        if (!ar || !ar.ativo || !ar.ordemIds.length) {
            if (typeof Toast !== 'undefined') Toast.error('Inicie o combate antes.');
            return;
        }
        const dlg = document.getElementById('t20ArenaModalPericia');
        if (!dlg) return;
        const ativoId = ar.ordemIds[ar.turnoIdx];
        const displayId =
            ar.viewId != null && ar.byId[ar.viewId] ? ar.viewId : ativoId;
        const p = ar.byId[displayId];
        const tit = document.getElementById('t20ArenaPericiaTitulo');
        if (tit) tit.textContent = p ? `Perícia — ${p.nome}` : 'Rolar perícia';
        popularSelectPericias(p || {});
        const hint = document.getElementById('t20ArenaPericiaCondHint');
        const rotulos = rotulosCondicoes(displayId);
        if (hint) {
            hint.textContent = rotulos.length
                ? `Condições ativas: ${rotulos.join(', ')} (modificadores entram no bônus).`
                : 'Sem condições gravadas — marque em «Condições» se necessário.';
        }
        const res = document.getElementById('t20ArenaPericiaResultado');
        if (res) {
            res.hidden = true;
            res.innerHTML = '';
        }
        const dc = document.getElementById('t20ArenaPericiaDc');
        if (dc) dc.value = '15';
        if (typeof dlg.showModal === 'function') dlg.showModal();
    }

    function fecharModalPericia() {
        const dlg = document.getElementById('t20ArenaModalPericia');
        if (dlg && typeof dlg.close === 'function') dlg.close();
    }

    async function confirmarRolarPericia() {
        const ar = arenaRef();
        if (!ar || !ar.ativo) return;
        const ativoId = ar.ordemIds[ar.turnoIdx];
        const displayId =
            ar.viewId != null && ar.byId[ar.viewId] ? ar.viewId : ativoId;
        const p = ar.byId[displayId];
        if (!p) return;
        const selVal = document.getElementById('t20ArenaPericiaSelect')?.value;
        if (!selVal) {
            if (typeof Toast !== 'undefined') Toast.error('Escolha uma perícia.');
            return;
        }
        const dcRaw = document.getElementById('t20ArenaPericiaDc')?.value;
        const dc = Number(dcRaw);
        if (!Number.isFinite(dc) || dc < 1) {
            if (typeof Toast !== 'undefined') Toast.error('Informe uma CD válida (1–99).');
            return;
        }
        const btn = document.getElementById('t20ArenaModalPericiaRolar');
        try {
            if (btn) btn.disabled = true;
            const info = await bonusPericiaSelecionada(p, selVal);
            if (!info.pode_usar) {
                if (typeof Toast !== 'undefined') Toast.error(info.motivo_bloqueio || 'Não pode rolar.');
                return;
            }
            const rotulos = rotulosCondicoes(displayId);
            const modCond = await modCondicaoPericia(info.slug, rotulos, regraVersaoDe(p));
            const bonusFinal = info.bonus + modCond;
            const roll = await regras().rolarPericia({ bonus: bonusFinal, dc });
            const box = document.getElementById('t20ArenaPericiaResultado');
            const hit = roll.sucesso
                ? '<span class="t20-arena-roll-ok">SUCESSO</span>'
                : '<span class="t20-arena-roll-fail">FALHA</span>';
            const modTxt =
                modCond !== 0
                    ? ` <span class="t20-arena-roll-result__hint">(cond. ${modCond >= 0 ? '+' : ''}${modCond})</span>`
                    : '';
            if (box) {
                box.innerHTML = `<p class="t20-arena-roll-result__tit">${esc(p.nome)} · ${esc(info.nome)}</p>
                    <p class="t20-arena-roll-result__linha"><strong>${roll.d20}</strong> + ${bonusFinal} (base ${info.bonus})${modTxt} = <strong>${roll.total}</strong> vs CD <strong>${dc}</strong> → ${hit}</p>`;
                box.hidden = false;
            }
            let msg = `${p.nome} · ${info.nome}: ${roll.d20}+${bonusFinal}=${roll.total} vs CD ${dc} → ${roll.sucesso ? 'SUCESSO' : 'FALHA'}`;
            if (modCond) msg += ` (cond. ${modCond >= 0 ? '+' : ''}${modCond})`;
            registrarLog(msg);
            if (typeof Toast !== 'undefined') Toast.info(msg);
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro ao rolar perícia');
        } finally {
            if (btn) btn.disabled = false;
        }
    }

    function bindOnce() {
        const btn = document.getElementById('t20ArenaBtnRolarPericia');
        if (btn && !btn.dataset.bound) {
            btn.dataset.bound = '1';
            btn.addEventListener('click', abrirModalPericia);
        }
        ['t20ArenaModalPericiaFechar', 't20ArenaModalPericiaCancelar'].forEach((id) => {
            const el = document.getElementById(id);
            if (!el || el.dataset.bound) return;
            el.dataset.bound = '1';
            el.addEventListener('click', fecharModalPericia);
        });
        const btnRolar = document.getElementById('t20ArenaModalPericiaRolar');
        if (btnRolar && !btnRolar.dataset.bound) {
            btnRolar.dataset.bound = '1';
            btnRolar.addEventListener('click', confirmarRolarPericia);
        }
    }

    window.__t20ArenaPericiasInit = bindOnce;
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bindOnce);
    } else {
        bindOnce();
    }
})();
