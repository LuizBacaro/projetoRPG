/**
 * Ofício v1.3 — especialidades múltiplas (RF-T04g / RF-T04-v13b).
 *
 * UX simples: cada linha é um Ofício completo (Tr / Atrib. / Out / Σ).
 * «+» duplica a linha; campo inline define a especialidade (alquimia, armeiro…).
 * Sem acordeão, chevron ou painel extra.
 *
 * Contratos:
 * - `data-per-idx` da linha-pai nas filhas → meta INT / somente treinada.
 * - `data-per-nome-canon="Ofício"` → bônus racial e lookup do backend.
 * - Sem `data-per-slug` nas filhas → origem/classe não marcam todas de uma vez.
 * - Nome salvo: «Ofício» ou «Ofício (especialidade)» via `.p-oficio-esp`.
 */
(function (global) {
    'use strict';

    const CANON = 'Ofício';
    const SUGESTOES = [
        'alquimia',
        'armeiro',
        'artesão',
        'cozinheiro',
        'alfaiate',
        'carpinteiro',
        'pedreiro',
        'ourives',
        'fazendeiro',
        'pescador',
        'estalajadeiro',
        'escriba',
        'escultor',
        'pintor',
    ];

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

    function todasLinhasOficio() {
        const pai = rowOficio();
        const out = [];
        if (pai) out.push(pai);
        rowsEsp().forEach((tr) => out.push(tr));
        return out;
    }

    function ultimaLinhaOficio() {
        const esp = rowsEsp();
        if (esp.length) return esp[esp.length - 1];
        return rowOficio();
    }

    function escAttr(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function lerEspDaLinha(tr) {
        if (!tr) return '';
        const inp = tr.querySelector('.p-oficio-esp');
        if (inp) return String(inp.value || '').trim();
        return String(tr.getAttribute('data-oficio-esp') || '').trim();
    }

    function nomeSalvoDaLinha(tr) {
        const esp = lerEspDaLinha(tr);
        return esp ? `${CANON} (${esp})` : CANON;
    }

    function lerValoresLinha(tr) {
        if (!tr) return null;
        return {
            treinado: Boolean(tr.querySelector('.p-treinado')?.checked),
            total: tr.querySelector('.p-total')?.value || '0',
            mod: tr.querySelector('.p-mod')?.value || '0',
            outros: tr.querySelector('.p-out')?.value || '0',
            so_treina: Boolean(tr.querySelector('.p-so-treina')?.checked),
            esp: lerEspDaLinha(tr),
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
        if (vals.esp != null) setEspNaLinha(tr, vals.esp);
    }

    function setEspNaLinha(tr, esp) {
        const nome = String(esp || '').trim();
        const inp = tr.querySelector('.p-oficio-esp');
        if (inp && inp.value !== nome) inp.value = nome;
        if (tr.hasAttribute('data-oficio-esp') || tr.classList.contains('t20-pericia-oficio-esp')) {
            tr.setAttribute('data-oficio-esp', nome || '_');
        }
        const span = tr.querySelector('.t20-p-nome');
        if (span) {
            span.textContent = CANON;
            span.title = nome
                ? `Clique para rolar Ofício (${nome})`
                : 'Clique para rolar Ofício';
        }
    }

    function ensureDatalist() {
        if (q('t20OficioEspSugestoes')) return;
        const dl = document.createElement('datalist');
        dl.id = 't20OficioEspSugestoes';
        dl.innerHTML = SUGESTOES.map((s) => '<option value="' + escAttr(s) + '"></option>').join('');
        document.body.appendChild(dl);
    }

    function montarNomeCell(opts) {
        const { comAdd, comRemover } = opts;
        const addHtml = comAdd
            ? '<button type="button" class="t20-oficio-esp-add-btn" title="Duplicar linha de Ofício">' +
              '<span aria-hidden="true">+</span>' +
              '<span class="t20-sr-only">Duplicar Ofício</span>' +
              '</button>'
            : '';
        const remHtml = comRemover
            ? '<button type="button" class="t20-oficio-esp-remover" title="Remover este Ofício">×</button>'
            : '';
        return (
            '<span class="t20-p-nome-wrap t20-oficio-esp-linha-nome">' +
            addHtml +
            '<span class="t20-p-nome t20-p-nome--rolavel" title="Clique para rolar 1d20 + bônus">' +
            CANON +
            '</span>' +
            '<span class="t20-oficio-esp-paren" aria-hidden="true">(</span>' +
            '<input type="text" class="t20-input p-oficio-esp" maxlength="60" list="t20OficioEspSugestoes" ' +
            'placeholder="ex.: alquimia" autocomplete="off" />' +
            '<span class="t20-oficio-esp-paren" aria-hidden="true">)</span>' +
            remHtml +
            '</span>'
        );
    }

    function bindLinhaOficio(tr, { comAdd, comRemover }) {
        const addBtn = tr.querySelector('.t20-oficio-esp-add-btn');
        if (addBtn && comAdd) {
            addBtn.onclick = (ev) => {
                ev.preventDefault();
                ev.stopPropagation();
                duplicarLinha();
            };
        }
        const remBtn = tr.querySelector('.t20-oficio-esp-remover');
        if (remBtn && comRemover) {
            remBtn.onclick = (ev) => {
                ev.preventDefault();
                ev.stopPropagation();
                removerLinha(tr);
            };
        }
        const inp = tr.querySelector('.p-oficio-esp');
        if (inp) {
            const sync = () => {
                setEspNaLinha(tr, inp.value);
                atualizarAcessorios();
            };
            inp.addEventListener('input', sync);
            inp.addEventListener('change', sync);
            inp.addEventListener('click', (ev) => ev.stopPropagation());
            inp.addEventListener('keydown', (ev) => ev.stopPropagation());
        }
    }

    function criarLinhaEsp(esp, pai) {
        const idx = pai.getAttribute('data-per-idx') || '';
        const tr = document.createElement('tr');
        tr.className = 't20-pericia-oficio-esp';
        if (idx !== '') tr.setAttribute('data-per-idx', idx);
        tr.setAttribute('data-per-attr', pai.getAttribute('data-per-attr') || 'int');
        tr.setAttribute('data-per-nome-canon', CANON);
        tr.setAttribute('data-oficio-esp', String(esp || '').trim() || '_');

        const armInput = pai.querySelector('.p-pen-arm');
        const armHtml = armInput
            ? '<input type="checkbox" class="p-pen-arm t20-sr-only" tabindex="-1" aria-hidden="true"' +
              (armInput.checked ? ' checked' : '') +
              ' />'
            : '';

        tr.innerHTML =
            '<td><input type="checkbox" class="p-treinado" /></td>' +
            '<td class="t20-p-nome-cell">' +
            armHtml +
            montarNomeCell({ comAdd: false, comRemover: true }) +
            '</td>' +
            '<td><input type="number" class="p-total t20-input" value="0" /></td>' +
            '<td><span class="t20-p-half">0</span></td>' +
            '<td><input type="number" class="p-mod t20-input" value="0" /></td>' +
            '<td><input type="number" class="p-out t20-input" value="0" /></td>' +
            '<td class="t20-p-bonus-cell" title="Bônus total — passe o mouse para fórmula; clique para rolar">' +
            '<span class="t20-p-bonus-val">—</span>' +
            '<span class="t20-p-breakdown t20-sr-only" aria-hidden="true"></span></td>' +
            '<td><input type="checkbox" class="p-so-treina" title="Somente treinado (Ofício exige treino)" checked /></td>';

        if (isV13()) {
            const tdTotal = tr.querySelector('.p-total')?.closest('td');
            if (tdTotal) tdTotal.style.display = 'none';
        }
        setEspNaLinha(tr, esp);
        bindLinhaOficio(tr, { comAdd: false, comRemover: true });
        return tr;
    }

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

    function limparUiLegada(tr) {
        if (!tr) return;
        ['t20OficioEspHead', 't20OficioEspWrap', 't20OficioEspToggle', 't20OficioEspBadge'].forEach(
            (id) => q(id)?.remove()
        );
        tr.querySelectorAll('.t20-oficio-esp-head, .t20-oficio-esp-wrap, .t20-oficio-esp-toggle, .t20-oficio-esp-badge').forEach(
            (el) => el.remove()
        );
        tr.classList.remove('t20-pericia-oficio-pai');
        ['.p-treinado', '.p-total', '.p-mod', '.p-out'].forEach((sel) => {
            const el = tr.querySelector(sel);
            if (el) el.disabled = false;
        });
    }

    function ensureUiPai() {
        const tr = rowOficio();
        if (!tr) return;
        limparUiLegada(tr);
        ensureDatalist();

        const td = tr.querySelector('.t20-p-nome-cell') || tr.querySelector('td:nth-child(2)');
        if (!td) return;

        if (!tr.querySelector('.p-oficio-esp')) {
            const armInput = td.querySelector('.p-pen-arm');
            const armBadge = td.querySelector('.t20-pen-arm-badge');
            const armHtml = armInput ? armInput.outerHTML : '';
            const badgeHtml = armBadge ? armBadge.outerHTML : '';
            td.innerHTML = armHtml + badgeHtml + montarNomeCell({ comAdd: true, comRemover: false });
            bindLinhaOficio(tr, { comAdd: true, comRemover: false });
        } else {
            bindLinhaOficio(tr, { comAdd: true, comRemover: false });
        }

        const addBtn = tr.querySelector('.t20-oficio-esp-add-btn');
        if (addBtn) addBtn.hidden = !isV13();
        const paren = tr.querySelectorAll('.t20-oficio-esp-paren, .p-oficio-esp');
        paren.forEach((el) => {
            el.hidden = !isV13();
        });
        if (!isV13()) {
            const inp = tr.querySelector('.p-oficio-esp');
            if (inp) inp.value = '';
            const span = tr.querySelector('.t20-p-nome');
            if (span) {
                span.textContent = CANON;
                span.classList.add('t20-p-nome--rolavel');
                span.title = 'Clique para rolar 1d20 + bônus';
            }
        }
    }

    function duplicarLinha() {
        if (!isV13()) return;
        const pai = rowOficio();
        if (!pai) return;
        const tr = criarLinhaEsp('', pai);
        const ancora = ultimaLinhaOficio();
        ancora.insertAdjacentElement('afterend', tr);
        atualizarAcessorios();
        const inp = tr.querySelector('.p-oficio-esp');
        if (inp) {
            inp.focus();
            inp.select();
        }
    }

    function removerLinha(tr) {
        if (!tr || !tr.classList.contains('t20-pericia-oficio-esp')) return;
        const key = lerEspDaLinha(tr).toLowerCase();
        if (key) valoresCache.delete(key);
        tr.remove();
        atualizarAcessorios();
    }

    function sincronizarLinhasExtras(listaEsp) {
        const pai = rowOficio();
        if (!pai) return;

        const snapshot = new Map();
        rowsEsp().forEach((tr) => {
            const vals = lerValoresLinha(tr);
            const k = (vals && vals.esp ? vals.esp : tr.getAttribute('data-oficio-esp') || '').toLowerCase();
            if (vals) {
                snapshot.set(k, vals);
                if (vals.esp) valoresCache.set(vals.esp.toLowerCase(), vals);
            }
            tr.remove();
        });

        if (!isV13()) {
            atualizarAcessorios();
            return;
        }

        const extras = Array.isArray(listaEsp) ? listaEsp.slice(1) : [];
        let anchor = pai;
        extras.forEach((esp) => {
            const nome = String(esp || '').trim();
            const tr = criarLinhaEsp(nome, pai);
            anchor.insertAdjacentElement('afterend', tr);
            anchor = tr;
            const k = nome.toLowerCase();
            const vals = snapshot.get(k) || valoresCache.get(k);
            if (vals) aplicarValoresLinha(tr, { ...vals, esp: nome });
            else setEspNaLinha(tr, nome);
        });
        atualizarAcessorios();
    }

    function lerLista() {
        return todasLinhasOficio()
            .map((tr) => lerEspDaLinha(tr))
            .filter(Boolean);
    }

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
        ensureUiPai();
        const lista = Array.isArray(arr)
            ? arr.map((x) => String(x || '').trim()).filter(Boolean)
            : [];
        valoresCache.clear();
        const pai = rowOficio();
        if (pai && isV13()) {
            setEspNaLinha(pai, lista[0] || '');
        }
        sincronizarLinhasExtras(lista);
    }

    function syncVisibilidade() {
        ensureUiPai();
        if (!isV13()) {
            valoresCache.clear();
            rowsEsp().forEach((tr) => tr.remove());
            atualizarAcessorios();
            return;
        }
        // Mantém especialidades já na DOM; só garante UI do pai.
        rowsEsp().forEach((tr) => {
            if (!tr.querySelector('.p-oficio-esp')) {
                const esp = tr.getAttribute('data-oficio-esp') || '';
                const nomeCell = tr.querySelector('.t20-p-nome-cell') || tr.querySelector('td:nth-child(2)');
                if (nomeCell) {
                    const armInput = nomeCell.querySelector('.p-pen-arm');
                    const armHtml = armInput ? armInput.outerHTML : '';
                    nomeCell.innerHTML = armHtml + montarNomeCell({ comAdd: false, comRemover: true });
                    setEspNaLinha(tr, esp === '_' ? '' : esp);
                    bindLinhaOficio(tr, { comAdd: false, comRemover: true });
                }
            } else {
                bindLinhaOficio(tr, { comAdd: false, comRemover: true });
            }
        });
        atualizarAcessorios();
    }

    function initAposTabelaPericias() {
        syncVisibilidade();
    }

    /** Usado por coletarPericias / mapa de nomes na ficha. */
    function nomeExibidoLinha(tr) {
        if (!tr) return '';
        if (tr.getAttribute('data-per-slug') === 'oficio' || tr.hasAttribute('data-oficio-esp')) {
            return nomeSalvoDaLinha(tr);
        }
        return '';
    }

    global.T20OficioEspecialidadesV13 = {
        initAposTabelaPericias,
        syncVisibilidade,
        lerLista,
        aplicarLista,
        derivarDePericias,
        nomeExibidoLinha,
        duplicarLinha,
    };
    global.T20OficioEspecialidades = global.T20OficioEspecialidadesV13;
})(typeof window !== 'undefined' ? window : globalThis);
