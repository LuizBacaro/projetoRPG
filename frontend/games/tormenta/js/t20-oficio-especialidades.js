/**
 * Ofício v1.3 — especialidades múltiplas (RF-T04g / RF-T04-v13b).
 *
 * Cada especialidade é uma LINHA própria na tabela de perícias, com seus
 * próprios Tr / Atrib. / Out / Σ e rolagem — em T20 cada Ofício é treinado
 * separadamente. A linha-pai «Ofício» segue existindo como cabeçalho do grupo
 * e traz a setinha que mostra/esconde as especialidades.
 *
 * Contratos preservados:
 * - `data-per-idx` da linha-pai é repetido nas filhas → meta (INT, somente
 *   treinada, penalidade de armadura) resolve igual.
 * - `data-per-nome-canon="Ofício"` → bônus racial e lookup do backend.
 * - Sem `data-per-slug` nas filhas → origem/classe não marcam todas de uma vez.
 */
(function (global) {
    'use strict';

    const CANON = 'Ofício';

    let lista = [];
    let expandido = false;
    /** Valores por especialidade, para não perder em reconstruções. */
    const valoresCache = new Map();

    function q(id) {
        return document.getElementById(id);
    }

    function isV13() {
        if (typeof global.getRegraVersaoAtiva === 'function') {
            return global.T20RegraVersao && global.T20RegraVersao.isV13(global.getRegraVersaoAtiva());
        }
        return false;
    }

    function rowOficio() {
        return document.querySelector('#tblPericias tbody tr[data-per-slug="oficio"]');
    }

    function rowsEsp() {
        return Array.from(document.querySelectorAll('#tblPericias tbody tr[data-oficio-esp]'));
    }

    function rowEsp(nome) {
        const alvo = String(nome || '').toLowerCase();
        return rowsEsp().find(
            (tr) => (tr.getAttribute('data-oficio-esp') || '').toLowerCase() === alvo
        );
    }

    function nomeExibido(esp) {
        return `${CANON} (${esp})`;
    }

    function escAttr(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    /** Snapshot dos valores digitados, para não perder ao reconstruir linhas. */
    function lerValoresLinha(tr) {
        if (!tr) return null;
        return {
            treinado: Boolean(tr.querySelector('.p-treinado')?.checked),
            total: tr.querySelector('.p-total')?.value || '0',
            mod: tr.querySelector('.p-mod')?.value || '0',
            outros: tr.querySelector('.p-out')?.value || '0',
            so_treina: Boolean(tr.querySelector('.p-so-treina')?.checked),
        };
    }

    function aplicarValoresLinha(tr, vals) {
        if (!tr || !vals) return;
        const tre = tr.querySelector('.p-treinado');
        if (tre) tre.checked = Boolean(vals.treinado);
        const tot = tr.querySelector('.p-total');
        if (tot) tot.value = String(vals.total ?? '0');
        const mod = tr.querySelector('.p-mod');
        if (mod) mod.value = String(vals.mod ?? '0');
        const out = tr.querySelector('.p-out');
        if (out) out.value = String(vals.outros ?? '0');
        const st = tr.querySelector('.p-so-treina');
        if (st && vals.so_treina != null) st.checked = Boolean(vals.so_treina);
    }

    function criarLinhaEsp(esp, pai) {
        const idx = pai.getAttribute('data-per-idx') || '';
        const tr = document.createElement('tr');
        tr.className = 't20-pericia-oficio-esp';
        if (idx !== '') tr.setAttribute('data-per-idx', idx);
        tr.setAttribute('data-per-attr', pai.getAttribute('data-per-attr') || 'int');
        tr.setAttribute('data-per-nome-canon', CANON);
        tr.setAttribute('data-oficio-esp', esp);
        tr.innerHTML =
            '<td><input type="checkbox" class="p-treinado" /></td>' +
            '<td class="t20-p-nome-cell">' +
            '<span class="t20-p-nome-wrap t20-oficio-esp-linha-nome">' +
            '<span class="t20-oficio-esp-ramo" aria-hidden="true">↳</span>' +
            '<span class="t20-p-nome t20-p-nome--rolavel" title="Clique para rolar 1d20 + bônus">' +
            escAttr(nomeExibido(esp)) +
            '</span>' +
            '<button type="button" class="t20-oficio-esp-remover" data-oficio-esp-del="' +
            escAttr(esp) +
            '" title="Remover especialidade">×</button>' +
            '</span></td>' +
            '<td><input type="number" class="p-total t20-input" value="0" /></td>' +
            '<td><span class="t20-p-half">0</span></td>' +
            '<td><input type="number" class="p-mod t20-input" value="0" /></td>' +
            '<td><input type="number" class="p-out t20-input" value="0" /></td>' +
            '<td class="t20-p-bonus-cell" title="Bônus total — passe o mouse para fórmula; clique para rolar">' +
            '<span class="t20-p-bonus-val">—</span>' +
            '<span class="t20-p-breakdown t20-sr-only" aria-hidden="true"></span></td>' +
            '<td><input type="checkbox" class="p-so-treina" title="Somente treinado (Ofício exige treino)" checked /></td>';
        // Em v1.3 a coluna «Total» (graduações MB) está oculta no cabeçalho;
        // a linha nasce depois de t20AtualizarUiPericiasVersao, então alinha aqui.
        if (isV13()) {
            const tdTotal = tr.querySelector('.p-total')?.closest('td');
            if (tdTotal) tdTotal.style.display = 'none';
        }
        const btn = tr.querySelector('[data-oficio-esp-del]');
        if (btn) {
            btn.addEventListener('click', (ev) => {
                ev.preventDefault();
                ev.stopPropagation();
                remover(btn.getAttribute('data-oficio-esp-del'));
            });
        }
        return tr;
    }

    /**
     * Reconstrói as linhas filhas preservando valores por especialidade.
     * As linhas existem sempre que houver especialidade (mesmo recolhidas), para
     * que `coletarPericias` grave os valores ao salvar a ficha; recolher só oculta.
     */
    function sincronizarLinhas() {
        const pai = rowOficio();
        if (!pai) return;
        const snapshot = new Map();
        rowsEsp().forEach((tr) => {
            const k = (tr.getAttribute('data-oficio-esp') || '').toLowerCase();
            const vals = lerValoresLinha(tr);
            if (vals) {
                snapshot.set(k, vals);
                valoresCache.set(k, vals);
            }
            tr.remove();
        });
        if (!isV13() || !lista.length) {
            atualizarAcessorios();
            return;
        }
        let anchor = pai;
        lista.forEach((esp) => {
            const tr = criarLinhaEsp(esp, pai);
            tr.hidden = !expandido;
            anchor.insertAdjacentElement('afterend', tr);
            anchor = tr;
            const k = esp.toLowerCase();
            const vals = snapshot.get(k) || valoresCache.get(k);
            if (vals) aplicarValoresLinha(tr, vals);
        });
        atualizarAcessorios();
    }

    function atualizarVisibilidadeLinhas() {
        const mostrar = isV13() && expandido;
        rowsEsp().forEach((tr) => {
            tr.hidden = !mostrar;
        });
    }

    /** Meio nível, mod. de atributo, Σ e penalidades para as linhas novas. */
    function atualizarAcessorios() {
        if (typeof global.atualizarMeioNivelColuna === 'function') {
            global.atualizarMeioNivelColuna();
        }
        if (typeof global.atualizarModsPericiasDasHabilidades === 'function') {
            global.atualizarModsPericiasDasHabilidades();
        }
        if (typeof global.t20AtualizarPenalidadesPericias === 'function') {
            global.t20AtualizarPenalidadesPericias();
        }
        if (global.T20BreakdownFicha && global.T20BreakdownFicha.agendarPericias) {
            global.T20BreakdownFicha.agendarPericias();
        }
        if (typeof global.t20ValidarPericiasOrcamentoMb === 'function') {
            global.t20ValidarPericiasOrcamentoMb();
        }
    }

    function renderTags() {
        const host = q('t20OficioEspTags');
        if (!host) return;
        host.innerHTML = '';
        if (!lista.length) {
            const vazio = document.createElement('p');
            vazio.className = 't20-hint';
            vazio.style.margin = '0 0 0.25rem';
            vazio.textContent = 'Nenhuma especialidade. Cada Ofício vira uma linha própria.';
            host.appendChild(vazio);
            return;
        }
        lista.forEach((nome) => {
            const tag = document.createElement('span');
            tag.className = 't20-oficio-esp-tag';
            tag.textContent = nome;
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 't20-oficio-esp-del';
            btn.textContent = '×';
            btn.title = 'Remover';
            btn.addEventListener('click', (ev) => {
                ev.preventDefault();
                ev.stopPropagation();
                remover(nome);
            });
            tag.appendChild(btn);
            host.appendChild(tag);
        });
    }

    /** A linha-pai mantém o nome canônico «Ofício» (lookup racial/backend). */
    function atualizarRotuloOficio() {
        const tr = rowOficio();
        if (!tr) return;
        const span = tr.querySelector('.t20-p-nome');
        if (span) span.textContent = CANON;
        ajustarLinhaPai();
        atualizarAccordionUi();
    }

    /**
     * Com especialidades, «Ofício» vira só cabeçalho do grupo: sem treino nem
     * valores próprios, para não haver dúvida de onde o bônus está e para não
     * consumir uma vaga de perícia treinada a mais.
     */
    function ajustarLinhaPai() {
        const tr = rowOficio();
        if (!tr) return;
        const virouCabecalho = isV13() && lista.length > 0;
        const tre = tr.querySelector('.p-treinado');
        if (tre) {
            if (virouCabecalho && tre.checked) tre.checked = false;
            tre.disabled = virouCabecalho;
        }
        ['.p-total', '.p-mod', '.p-out'].forEach((sel) => {
            const inp = tr.querySelector(sel);
            if (!inp) return;
            if (virouCabecalho) inp.value = '0';
            inp.disabled = virouCabecalho;
        });
        const nomeSpan = tr.querySelector('.t20-p-nome');
        if (nomeSpan) {
            nomeSpan.classList.toggle('t20-p-nome--rolavel', !virouCabecalho);
            nomeSpan.title = virouCabecalho
                ? 'Grupo de especialidades — role a especialidade desejada'
                : 'Clique para rolar 1d20 + bônus';
        }
    }

    /** Ao criar a 1ª especialidade, herda o que já estava na linha «Ofício». */
    function migrarValoresDoPai() {
        const tr = rowOficio();
        if (!tr) return null;
        const vals = lerValoresLinha(tr);
        if (!vals) return null;
        const vazio =
            !vals.treinado &&
            Number(vals.total || 0) === 0 &&
            Number(vals.outros || 0) === 0;
        return vazio ? null : vals;
    }

    function atualizarAccordionUi() {
        const btn = q('t20OficioEspToggle');
        const badge = q('t20OficioEspBadge');
        const wrap = q('t20OficioEspWrap');
        const v13 = isV13();
        if (btn) {
            btn.hidden = !v13;
            btn.setAttribute('aria-expanded', expandido ? 'true' : 'false');
            btn.title = expandido ? 'Ocultar especialidades de Ofício' : 'Mostrar especialidades de Ofício';
            btn.classList.toggle('is-open', expandido);
        }
        if (badge) {
            if (v13 && lista.length) {
                badge.hidden = false;
                badge.textContent = String(lista.length);
                badge.title = lista.join(', ');
            } else {
                badge.hidden = true;
                badge.textContent = '';
                badge.title = '';
            }
        }
        if (wrap) {
            wrap.hidden = !v13 || !expandido;
            wrap.style.display = !v13 || !expandido ? 'none' : '';
        }
        const pai = rowOficio();
        if (pai) pai.classList.toggle('t20-pericia-oficio-pai', v13 && lista.length > 0);
    }

    function toggleAccordion(ev) {
        if (ev) {
            ev.preventDefault();
            ev.stopPropagation();
        }
        if (!isV13()) return;
        expandido = !expandido;
        atualizarVisibilidadeLinhas();
        atualizarAccordionUi();
        if (expandido) {
            const inp = q('t20OficioEspInput');
            if (inp) {
                try {
                    inp.focus({ preventScroll: true });
                } catch (_e) {
                    inp.focus();
                }
            }
        }
    }

    function ensureUi() {
        const tr = rowOficio();
        if (!tr) return;
        const td = tr.querySelector('td:nth-child(2)');
        if (!td) return;

        if (!q('t20OficioEspHead')) {
            const nomeWrap = td.querySelector('.t20-p-nome-wrap') || td;
            const head = document.createElement('span');
            head.id = 't20OficioEspHead';
            head.className = 't20-oficio-esp-head';
            head.innerHTML =
                '<button type="button" class="t20-oficio-esp-toggle" id="t20OficioEspToggle" aria-expanded="false" aria-controls="t20OficioEspWrap" title="Mostrar especialidades de Ofício">' +
                '<span class="t20-oficio-esp-chevron" aria-hidden="true">▾</span>' +
                '</button>' +
                '<span class="t20-oficio-esp-badge" id="t20OficioEspBadge" hidden></span>';
            const nomeSpan = nomeWrap.querySelector('.t20-p-nome');
            if (nomeSpan) nomeSpan.insertAdjacentElement('afterend', head);
            else nomeWrap.appendChild(head);
            q('t20OficioEspToggle')?.addEventListener('click', toggleAccordion);
        }

        if (!q('t20OficioEspWrap')) {
            const div = document.createElement('div');
            div.id = 't20OficioEspWrap';
            div.className = 't20-oficio-esp-wrap';
            div.hidden = true;
            div.style.display = 'none';
            div.innerHTML =
                '<div id="t20OficioEspTags" class="t20-oficio-esp-tags"></div>' +
                '<div class="t20-oficio-esp-add">' +
                '<input id="t20OficioEspInput" class="t20-input" maxlength="60" placeholder="Especialidade (ex.: alquimia)" />' +
                '<button type="button" class="tormenta-btn" id="t20OficioEspBtn">+</button>' +
                '</div>' +
                '<p class="t20-hint t20-oficio-esp-nota">Cada especialidade é treinada à parte e consome uma vaga de perícia treinada.</p>';
            td.appendChild(div);
            q('t20OficioEspBtn')?.addEventListener('click', (ev) => {
                ev.preventDefault();
                ev.stopPropagation();
                adicionar();
            });
            q('t20OficioEspInput')?.addEventListener('keydown', (ev) => {
                if (ev.key === 'Enter') {
                    ev.preventDefault();
                    ev.stopPropagation();
                    adicionar();
                }
            });
            div.addEventListener('click', (ev) => ev.stopPropagation());
        }
    }

    function adicionar() {
        const inp = q('t20OficioEspInput');
        if (!inp) return;
        const v = inp.value.trim();
        if (!v) return;
        const key = v.toLowerCase();
        if (lista.some((x) => x.toLowerCase() === key)) {
            inp.value = '';
            return;
        }
        const herdado = lista.length === 0 ? migrarValoresDoPai() : null;
        lista.push(v);
        if (herdado) valoresCache.set(key, herdado);
        inp.value = '';
        expandido = true;
        renderTags();
        sincronizarLinhas();
        atualizarRotuloOficio();
    }

    function remover(esp) {
        const key = String(esp || '').toLowerCase();
        const antes = lista.length;
        lista = lista.filter((x) => x.toLowerCase() !== key);
        if (lista.length === antes) return;
        valoresCache.delete(key);
        const tr = rowEsp(esp);
        if (tr) tr.remove();
        renderTags();
        sincronizarLinhas();
        atualizarRotuloOficio();
    }

    function syncVisibilidade() {
        ensureUi();
        if (!isV13()) {
            lista = [];
            expandido = false;
            valoresCache.clear();
            rowsEsp().forEach((tr) => tr.remove());
        }
        renderTags();
        sincronizarLinhas();
        atualizarRotuloOficio();
    }

    function lerLista() {
        return lista.slice();
    }

    /** Extrai especialidades de uma lista `pericias[]` salva (fallback de restore). */
    function derivarDePericias(pericias) {
        const out = [];
        const seen = new Set();
        (Array.isArray(pericias) ? pericias : []).forEach((p) => {
            const nome = String((p && p.nome) || '').trim();
            const m = nome.match(/^Of[íi]cio\s*\((.+)\)\s*$/i);
            if (!m) return;
            const esp = m[1].trim();
            const k = esp.toLowerCase();
            if (!esp || seen.has(k)) return;
            seen.add(k);
            out.push(esp);
        });
        return out;
    }

    function aplicarLista(arr) {
        lista = Array.isArray(arr) ? arr.map((x) => String(x || '').trim()).filter(Boolean) : [];
        // Com especialidades salvas, abre o grupo para os valores ficarem visíveis
        expandido = lista.length > 0;
        valoresCache.clear();
        ensureUi();
        renderTags();
        sincronizarLinhas();
        atualizarRotuloOficio();
    }

    function initAposTabelaPericias() {
        syncVisibilidade();
    }

    global.T20OficioEspecialidadesV13 = {
        initAposTabelaPericias,
        syncVisibilidade,
        lerLista,
        aplicarLista,
        derivarDePericias,
    };
})(typeof window !== 'undefined' ? window : globalThis);
