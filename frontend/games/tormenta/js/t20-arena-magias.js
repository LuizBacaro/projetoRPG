/**
 * Arena Tormenta 20 — lançar magias MB (debita PM; concentração MVP).
 */
(function () {
    const personagemSvc = () => new TormentaPersonagemService();

    function arenaRef() {
        return window.__t20ArenaRef;
    }

    function escHtml(s) {
        if (typeof window.escapeHtml === 'function') return window.escapeHtml(s);
        const d = document.createElement('div');
        d.textContent = s == null ? '' : String(s);
        return d.innerHTML;
    }

    function personagemAtivo() {
        const ar = arenaRef();
        if (!ar || !ar.ativo) return null;
        const ids = ar.ordemIds || [];
        const id = ids.length ? ids[ar.turnoIdx] : null;
        if (id == null) return null;
        return ar.byId[id] || null;
    }

    function lerConcentracao(fichaJson) {
        const fj = fichaJson && typeof fichaJson === 'object' ? fichaJson : {};
        const sess = fj.tormenta_grimorio_sessao_mb;
        if (!sess || typeof sess !== 'object') return null;
        const slug = String(sess.concentracao_magia_slug || '').trim();
        if (!slug) return null;
        return {
            slug,
            nome: String(sess.concentracao_magia_nome || slug).trim(),
        };
    }

    function magiasLancaveisNaLista(magias) {
        const arr = Array.isArray(magias) ? magias : [];
        const out = [];
        const seen = new Set();
        arr.forEach((m) => {
            const slug = String(m.magia_slug || '').trim().toLowerCase();
            const pap = String(m.papel || '').trim().toLowerCase();
            const circ = Number(m.circulo);
            if (!slug || seen.has(slug)) return;
            if (pap === 'conhecida' || pap === 'preparada') {
                seen.add(slug);
                out.push(m);
                return;
            }
            if (pap === 'grimorio' && (circ === 0 || !Number.isFinite(circ))) {
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

    function montarCabecalhoCombate(conc, srBonus) {
        const partes = [];
        if (conc) {
            partes.push(
                `<p class="t20-dash-hint"><strong>Concentração:</strong> ${escHtml(conc.nome)} · <button type="button" class="tormenta-btn tormenta-btn--secondary t20-arena-encerrar-conc" style="padding:.2rem .5rem;font-size:.75rem">Encerrar</button></p>`
            );
        }
        if (srBonus) {
            partes.push(
                `<p class="t20-dash-hint"><strong>Resistência à magia (MB):</strong> +${srBonus} em testes contra magia${conc ? '' : ' (ativa na sessão ou lembrete do grimório)'}.</p>`
            );
        }
        return partes.join('');
    }

    function montarListaHtml(magias, pmAtual, extraHtml) {
        const lista = magiasLancaveisNaLista(magias);
        const head = extraHtml || '';
        if (!lista.length) {
            return `${head}<p class="t20-dash-hint">Nenhuma magia vinculada para lançar. Abra o <strong>Grimório</strong> na ficha (repertório, preparadas ou livro do mago). Clérigo: a <strong>prece de devoção</strong> da divindade pode ser lançada sem PM.</p>`;
        }
        const pm = Number.isFinite(Number(pmAtual)) ? Number(pmAtual) : null;
        return `${head}<ul class="t20-arena-magias-lista">${lista
            .map((m) => {
                const slug = escHtml(m.magia_slug || '');
                const nome = escHtml(m.nome || m.magia_slug || '');
                const circ = m.circulo != null ? `C${m.circulo}` : '';
                const circN = Number(m.circulo);
                // Tormenta 20 v1.3 Tabela 4-1: 1/3/6/10/15 (arena usa ficha v1.3 por padrão)
                const mapaPmV13 = { 1: 1, 2: 3, 3: 6, 4: 10, 5: 15 };
                const custoPm =
                    Number.isFinite(circN) && circN >= 1
                        ? mapaPmV13[circN] != null
                            ? mapaPmV13[circN]
                            : circN
                        : 0;
                const custo = `${custoPm} PM`;
                const pap = escHtml(m.papel || '');
                const dur = m.duracao ? String(m.duracao) : '';
                const concHint =
                    dur.toLowerCase().includes('concentr') ? ' · concentração' : '';
                const disabled =
                    pm != null && custoPm > pm ? ' disabled title="PM insuficientes"' : '';
                return `<li class="t20-arena-magia-item">
                    <div class="t20-arena-magia-meta">
                        <strong>${nome}</strong>
                        <span class="t20-hint">${circ} · ${custo} · ${pap}${concHint}</span>
                    </div>
                    <button type="button" class="tormenta-btn tormenta-btn--primary t20-arena-magia-lancar" data-magia-slug="${slug}"${disabled}>Lançar</button>
                </li>`;
            })
            .join('')}</ul>`;
    }

    function lerResistenciaMagia(fichaJson) {
        const fj = fichaJson && typeof fichaJson === 'object' ? fichaJson : {};
        const sess = fj.tormenta_grimorio_sessao_mb;
        if (!sess || typeof sess !== 'object') return null;
        const b = Number(sess.resistencia_magia_bonus);
        return Number.isFinite(b) && b > 0 ? b : null;
    }

    function srBonusDeVinculos(magias, fichaJson) {
        const ativo = lerResistenciaMagia(fichaJson);
        if (ativo) return ativo;
        const map = {
            resistencia_a_magia: 4,
            resistencia_a_magia_div: 4,
            resistencia_a_magia_maior: 8,
            resistencia_a_magia_maior_div: 8,
        };
        let best = 0;
        (magias || []).forEach((m) => {
            const pap = String(m.papel || '').toLowerCase();
            if (pap !== 'preparada' && pap !== 'conhecida') return;
            const b = map[String(m.magia_slug || '').toLowerCase()];
            if (b && b > best) best = b;
        });
        return best || null;
    }

    async function abrirModal() {
        const dlg = document.getElementById('t20ArenaModalMagias');
        const corpo = document.getElementById('t20ArenaMagiasCorpo');
        const tit = document.getElementById('t20ArenaMagiasTitulo');
        const p = personagemAtivo();
        if (!dlg || !corpo) return;
        if (!p || !p.id) {
            if (typeof Toast !== 'undefined') Toast.error('Nenhum combatente ativo no turno.');
            return;
        }
        if (tit) tit.textContent = `Magias — ${p.nome || 'Combatente'}`;
        corpo.innerHTML = '<p class="t20-dash-hint">Carregando magias…</p>';
        if (typeof dlg.showModal === 'function') dlg.showModal();
        try {
            const full = await personagemSvc().obter(p.id);
            const pm = full.pa_atual != null ? full.pa_atual : p.pa_atual;
            const conc = lerConcentracao(full.ficha_json);
            const sr = srBonusDeVinculos(full.magias, full.ficha_json);
            const head = montarCabecalhoCombate(conc, sr);
            corpo.innerHTML = montarListaHtml(full.magias, pm, head);
            const btnConc = corpo.querySelector('.t20-arena-encerrar-conc');
            if (btnConc) {
                btnConc.addEventListener('click', () => encerrarConcentracao(p.id, dlg));
            }
            corpo.querySelectorAll('.t20-arena-magia-lancar').forEach((btn) => {
                btn.addEventListener('click', () => lancarMagia(p.id, btn.getAttribute('data-magia-slug'), dlg));
            });
        } catch (e) {
            corpo.innerHTML = `<p class="t20-dash-hint">${escHtml(e.message || 'Erro ao carregar magias')}</p>`;
        }
    }

    async function encerrarConcentracao(personagemId, dlg) {
        try {
            const res = await personagemSvc().encerrarConcentracao(personagemId);
            if (typeof Toast !== 'undefined') {
                Toast.success(
                    res && res.encerrada
                        ? `Concentração encerrada (${res.concentracao_anterior || ''}).`
                        : 'Nenhuma concentração ativa.'
                );
            }
            if (dlg) await abrirModal();
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro ao encerrar concentração');
        }
    }

    async function lancarMagia(personagemId, slug, dlg) {
        const s = String(slug || '').trim().toLowerCase();
        if (!s) return;
        try {
            const res = await personagemSvc().lancarMagia(personagemId, s);
            if (typeof Toast !== 'undefined') {
                let msg = `Magia lançada (−${res.custo_pm || 0} PM). PM: ${res.pa_atual_depois}/${res.pa_max != null ? res.pa_max : '—'}`;
                if (res.concentracao_ativa) msg += ` · Concentração: ${res.concentracao_ativa}`;
                if (res.resistencia_magia_bonus) msg += ` · RM +${res.resistencia_magia_bonus}`;
                Toast.success(msg);
            }
            const ar = arenaRef();
            if (ar && ar.byId[personagemId]) {
                ar.byId[personagemId].pa_atual = res.pa_atual_depois;
                if (res.pa_max != null) ar.byId[personagemId].pa_max = res.pa_max;
            }
            if (typeof window.__t20ArenaRenderActive === 'function') {
                window.__t20ArenaRenderActive();
            } else if (typeof t20ArenaRenderActive === 'function') {
                t20ArenaRenderActive();
            }
            if (window.T20SyncFichaArena && typeof window.T20SyncFichaArena.publicarVitais === 'function') {
                window.T20SyncFichaArena.publicarVitais({
                    origem: 'arena',
                    personagem_id: personagemId,
                    pa_atual: res.pa_atual_depois,
                    pa_max: res.pa_max != null ? res.pa_max : ar && ar.byId[personagemId] ? ar.byId[personagemId].pa_max : null,
                    pv_atual: ar && ar.byId[personagemId] ? ar.byId[personagemId].pv_atual : null,
                    pv_max: ar && ar.byId[personagemId] ? ar.byId[personagemId].pv_max : null,
                });
            }
            if (dlg && typeof dlg.close === 'function') dlg.close();
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro ao lançar magia');
        }
    }

    function init() {
        const btn = document.getElementById('t20ArenaBtnMagias');
        if (btn) btn.addEventListener('click', () => abrirModal());
        ['t20ArenaModalMagiasFechar', 't20ArenaModalMagiasCancelar'].forEach((id) => {
            const b = document.getElementById(id);
            const dlg = document.getElementById('t20ArenaModalMagias');
            if (b && dlg) b.addEventListener('click', () => dlg.close());
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window.__t20ArenaAbrirMagias = abrirModal;
})();
