/**
 * Modal de Ataques Tormenta 20 — catálogo v1.3, inventário e itens superiores.
 * Expõe window.T20AtaquesModal.
 */
(function (global) {
    'use strict';

    const MAX_MELHORIAS = 4;
    let _draft = [];
    let _editIdx = -1;
    let _armasCatalogo = [];
    let _superiores = null;
    let _escBound = false;
    let _buscaTimer = null;

    function $(id) {
        return document.getElementById(id);
    }

    function esc(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function norm(s) {
        return String(s || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .trim();
    }

    function isArmaCatalogo(it) {
        const cat = norm(it.categoria || '');
        const sec = norm(it.secao || '');
        if (sec.indexOf('armas') >= 0) return true;
        if (cat.indexOf('arma') >= 0) return true;
        if (it.dano_m || it.dano_p || it.tipo_dano) return true;
        return false;
    }

    function parseBonusNum(txt) {
        const s = String(txt || '').trim().replace(/^\+/, '');
        if (s === '' || s === '—') return 0;
        const n = parseInt(s, 10);
        return Number.isFinite(n) ? n : 0;
    }

    function formatBonus(n) {
        const v = Number(n) || 0;
        return (v >= 0 ? '+' : '') + String(v);
    }

    function parseCustoTs(texto) {
        const s = String(texto || '').trim();
        if (!s || s === '—' || s === '-') return 0;
        const m = s.replace(/\./g, '').match(/(\d+)/);
        return m ? parseInt(m[1], 10) : 0;
    }

    function aplicarDanoBonus(danoBase, bonus) {
        const b = Number(bonus) || 0;
        const base = String(danoBase || '').trim();
        if (!b) return base;
        if (!base) return formatBonus(b).replace('+', '');
        // Já tem +N no final?
        const m = base.match(/^(.*?)([+-]\d+)\s*$/);
        if (m) {
            const cur = parseInt(m[2], 10) || 0;
            const novo = cur + b;
            return m[1] + (novo >= 0 ? '+' : '') + novo;
        }
        return base + (b >= 0 ? '+' : '') + b;
    }

    function inventarioNomes() {
        const out = [];
        const seen = new Set();
        document
            .querySelectorAll('#fichaEquipamentos .ficha-equipamentos-lista-items input[type="text"]')
            .forEach((inp) => {
                const nome = (inp.value || '').trim();
                if (!nome) return;
                const k = norm(nome);
                if (seen.has(k)) return;
                seen.add(k);
                out.push(nome);
            });
        return out;
    }

    function bonusSugeridoParaArma(arma) {
        const sec = norm((arma && arma.secao) || '');
        const dist =
            sec.indexOf('distancia') >= 0 ||
            sec.indexOf('à distancia') >= 0 ||
            sec.indexOf('fogo') >= 0 ||
            Boolean(arma && arma.alcance);
        const id = dist ? 't20AtqDistTotal' : 't20AtqCacTotal';
        const el = $(id);
        if (el && String(el.value).trim() !== '') {
            return formatBonus(parseBonusNum(el.value));
        }
        return '+0';
    }

    function cloneAtaque(a) {
        return {
            nome: String(a.nome || ''),
            bonus_ataque: String(a.bonus_ataque != null ? a.bonus_ataque : a.teste || ''),
            dano: String(a.dano || ''),
            tipo_dano: String(a.tipo_dano != null ? a.tipo_dano : a.tipo || ''),
            critico: String(a.critico || ''),
            alcance: String(a.alcance || ''),
            empunhado: a.empunhado === true,
            arma_base: a.arma_base ? String(a.arma_base) : '',
            melhorias: Array.isArray(a.melhorias) ? a.melhorias.slice() : [],
            material: a.material ? String(a.material) : '',
            custo_ts_estimado:
                a.custo_ts_estimado != null && a.custo_ts_estimado !== ''
                    ? Number(a.custo_ts_estimado)
                    : null,
            notas: a.notas ? String(a.notas) : '',
            origem: a.origem,
            arma_natural: a.arma_natural === true,
            proficiencia_arma: a.proficiencia_arma,
            teste: String(a.teste || a.bonus_ataque || ''),
            tipo: String(a.tipo || a.tipo_dano || ''),
        };
    }

    function overlay() {
        return $('modalAtaquesTormenta');
    }

    function abrir() {
        const ov = overlay();
        if (!ov) return;
        const src =
            typeof global.t20AtaquesLista !== 'undefined' && Array.isArray(global.t20AtaquesLista)
                ? global.t20AtaquesLista
                : [];
        _draft = src.map(cloneAtaque);
        _editIdx = -1;
        ov.classList.add('is-open');
        ov.setAttribute('aria-hidden', 'false');
        ov.style.display = 'flex';
        setAba('livro');
        limparFormulario();
        renderDraftLista();
        renderInventario();
        carregarCatalogoArmas('');
        carregarSuperiores();
        // Foco no diálogo (não deixar foco preso sob aria-hidden ao fechar)
        const focoInicial =
            $('t20AtqBusca') || $('t20BtnFecharModalAtaques') || ov.querySelector('button, input, select');
        if (focoInicial && typeof focoInicial.focus === 'function') {
            try {
                focoInicial.focus({ preventScroll: true });
            } catch (_e) {
                focoInicial.focus();
            }
        }
        if (!_escBound) {
            _escBound = true;
            document.addEventListener('keydown', onKeydown);
        }
    }

    function fechar() {
        const ov = overlay();
        if (!ov) return;
        // Tirar o foco de dentro do modal ANTES de aria-hidden (aviso do Chrome/a11y)
        const ativo = document.activeElement;
        if (ativo && ov.contains(ativo) && typeof ativo.blur === 'function') {
            ativo.blur();
        }
        const restaurar = $('t20BtnAdicionarAtaques');
        if (restaurar && typeof restaurar.focus === 'function') {
            try {
                restaurar.focus({ preventScroll: true });
            } catch (_e) {
                restaurar.focus();
            }
        }
        ov.classList.remove('is-open');
        ov.setAttribute('aria-hidden', 'true');
        ov.style.display = 'none';
    }

    function onKeydown(e) {
        if (e.key !== 'Escape') return;
        const ov = overlay();
        if (ov && ov.classList.contains('is-open')) {
            e.preventDefault();
            fechar();
        }
    }

    function setAba(nome) {
        ['livro', 'inventario', 'lista'].forEach((k) => {
            const btn = $('t20AtqAba' + k.charAt(0).toUpperCase() + k.slice(1));
            const painel = $('t20AtqPainel' + k.charAt(0).toUpperCase() + k.slice(1));
            if (btn) btn.classList.toggle('ativa', k === nome);
            if (painel) {
                painel.classList.toggle('ativo', k === nome);
                painel.hidden = k !== nome;
            }
        });
    }

    async function carregarCatalogoArmas(q) {
        const lista = $('t20AtqCatalogoLista');
        if (!lista) return;
        lista.innerHTML = '<p class="t20-hint">Carregando armas…</p>';
        try {
            const svc = new TormentaRegrasService();
            const data = await svc.listarEquipamentosCatalogo({
                q: q || '',
                skip: 0,
                limit: 200,
            });
            _armasCatalogo = (data.itens || []).filter(isArmaCatalogo);
            renderCatalogoLista(_armasCatalogo);
        } catch (err) {
            lista.innerHTML =
                '<p class="t20-hint">' + esc(err.message || 'Erro ao carregar catálogo') + '</p>';
        }
    }

    function renderCatalogoLista(itens) {
        const lista = $('t20AtqCatalogoLista');
        if (!lista) return;
        if (!itens.length) {
            lista.innerHTML = '<p class="t20-hint">Nenhuma arma encontrada.</p>';
            return;
        }
        lista.innerHTML = itens
            .map((it) => {
                const meta = [
                    it.dano_m || it.dano_p || '',
                    it.tipo_dano || '',
                    it.critico || '',
                    it.proficiencia || '',
                ]
                    .filter(Boolean)
                    .join(' · ');
                return (
                    '<button type="button" class="t20-atq-cat-item" data-nome="' +
                    esc(it.nome) +
                    '">' +
                    '<strong>' +
                    esc(it.nome) +
                    '</strong>' +
                    '<span class="t20-atq-cat-meta">' +
                    esc(meta || it.secao || it.categoria || '') +
                    '</span></button>'
                );
            })
            .join('');
        lista.querySelectorAll('.t20-atq-cat-item').forEach((btn) => {
            btn.addEventListener('click', () => {
                const nome = btn.getAttribute('data-nome');
                const arma = _armasCatalogo.find((x) => x.nome === nome);
                if (arma) preencherDeCatalogo(arma);
            });
        });
    }

    function renderInventario() {
        const lista = $('t20AtqInventarioLista');
        if (!lista) return;
        const nomes = inventarioNomes();
        if (!nomes.length) {
            lista.innerHTML =
                '<p class="t20-hint">Nenhum equipamento na ficha. Adicione itens no inventário ou use a aba Livro.</p>';
            return;
        }
        lista.innerHTML = nomes
            .map(
                (n) =>
                    '<button type="button" class="t20-atq-cat-item" data-inv="' +
                    esc(n) +
                    '"><strong>' +
                    esc(n) +
                    '</strong></button>'
            )
            .join('');
        lista.querySelectorAll('.t20-atq-cat-item').forEach((btn) => {
            btn.addEventListener('click', () => {
                const nome = btn.getAttribute('data-inv');
                const arma =
                    _armasCatalogo.find((x) => norm(x.nome) === norm(nome)) ||
                    { nome: nome };
                preencherDeCatalogo(arma);
            });
        });
    }

    async function carregarSuperiores() {
        const boxMel = $('t20AtqMelhoriasChecks');
        const selMat = $('t20AtqMaterial');
        if (!boxMel || !selMat) return;
        try {
            if (!_superiores) {
                const svc = new TormentaRegrasService();
                _superiores = await svc.listarItensSuperiores({ aplicaEm: 'arma' });
            }
            const melhorias = (_superiores.melhorias || []).filter((m) => {
                const ap = m.aplica_em || [];
                return ap.indexOf('arma') >= 0 && m.slug !== 'material_especial';
            });
            boxMel.innerHTML = melhorias
                .map(
                    (m) =>
                        '<label class="t20-atq-check" title="' +
                        esc(m.efeito_resumo || '') +
                        '">' +
                        '<input type="checkbox" data-melhoria="' +
                        esc(m.slug) +
                        '" /> ' +
                        esc(m.nome) +
                        '</label>'
                )
                .join('');
            boxMel.querySelectorAll('input[data-melhoria]').forEach((cb) => {
                cb.addEventListener('change', onMelhoriaChange);
            });
            const mats = _superiores.materiais || [];
            selMat.innerHTML =
                '<option value="">— nenhum —</option>' +
                mats
                    .map(
                        (m) =>
                            '<option value="' +
                            esc(m.slug) +
                            '" title="' +
                            esc(m.efeito_resumo || '') +
                            '">' +
                            esc(m.nome) +
                            '</option>'
                    )
                    .join('');
            selMat.addEventListener('change', atualizarPreviewSuperior);
        } catch (err) {
            boxMel.innerHTML =
                '<p class="t20-hint">' + esc(err.message || 'Não foi possível carregar melhorias') + '</p>';
        }
    }

    function onMelhoriaChange(e) {
        const checked = Array.from(
            document.querySelectorAll('#t20AtqMelhoriasChecks input[data-melhoria]:checked')
        );
        if (checked.length > MAX_MELHORIAS) {
            e.target.checked = false;
            return;
        }
        // incompatíveis
        const slug = e.target.getAttribute('data-melhoria');
        const row = (_superiores.melhorias || []).find((m) => m.slug === slug);
        if (e.target.checked && row && Array.isArray(row.incompativel_com)) {
            row.incompativel_com.forEach((inc) => {
                const other = document.querySelector(
                    '#t20AtqMelhoriasChecks input[data-melhoria="' + inc + '"]'
                );
                if (other) other.checked = false;
            });
        }
        atualizarPreviewSuperior();
    }

    function preencherDeCatalogo(arma) {
        _editIdx = -1;
        $('t20AtqFormNome').value = arma.nome || '';
        $('t20AtqFormArmaBase').value = arma.nome || '';
        $('t20AtqFormBonus').value = bonusSugeridoParaArma(arma);
        $('t20AtqFormDano').value = arma.dano_m || arma.dano_p || '';
        $('t20AtqFormTipo').value = arma.tipo_dano || '';
        $('t20AtqFormCritico').value = arma.critico || '';
        $('t20AtqFormAlcance').value = arma.alcance || '';
        $('t20AtqFormEmp').checked = false;
        $('t20AtqFormCustoBase').value = String(parseCustoTs(arma.custo));
        document.querySelectorAll('#t20AtqMelhoriasChecks input').forEach((cb) => {
            cb.checked = false;
        });
        if ($('t20AtqMaterial')) $('t20AtqMaterial').value = '';
        atualizarPreviewSuperior();
        setAba('lista');
        const btn = $('t20AtqBtnAplicarForm');
        if (btn) btn.textContent = '➕ Incluir na lista';
    }

    function limparFormulario() {
        _editIdx = -1;
        ['t20AtqFormNome', 't20AtqFormArmaBase', 't20AtqFormBonus', 't20AtqFormDano', 't20AtqFormTipo', 't20AtqFormCritico', 't20AtqFormAlcance', 't20AtqFormNotas', 't20AtqFormCustoBase'].forEach(
            (id) => {
                const el = $(id);
                if (el) el.value = id === 't20AtqFormBonus' ? '+0' : '';
            }
        );
        if ($('t20AtqFormEmp')) $('t20AtqFormEmp').checked = false;
        document.querySelectorAll('#t20AtqMelhoriasChecks input').forEach((cb) => {
            cb.checked = false;
        });
        if ($('t20AtqMaterial')) $('t20AtqMaterial').value = '';
        atualizarPreviewSuperior();
        const btn = $('t20AtqBtnAplicarForm');
        if (btn) btn.textContent = '➕ Incluir na lista';
    }

    function melhoriasSelecionadas() {
        return Array.from(
            document.querySelectorAll('#t20AtqMelhoriasChecks input[data-melhoria]:checked')
        ).map((cb) => cb.getAttribute('data-melhoria'));
    }

    function modsDasMelhorias(slugs) {
        const mods = { ataque: 0, dano: 0, critico_margem: 0 };
        const rows = (_superiores && _superiores.melhorias) || [];
        slugs.forEach((slug) => {
            const m = rows.find((r) => r.slug === slug);
            if (!m || !m.mods) return;
            if (m.mods.ataque) mods.ataque += Number(m.mods.ataque) || 0;
            if (m.mods.dano) mods.dano += Number(m.mods.dano) || 0;
            if (m.mods.critico_margem) mods.critico_margem += Number(m.mods.critico_margem) || 0;
        });
        const matSlug = ($('t20AtqMaterial') && $('t20AtqMaterial').value) || '';
        if (matSlug && _superiores) {
            const mat = (_superiores.materiais || []).find((x) => x.slug === matSlug);
            if (mat && mat.mods) {
                if (mat.mods.dano_frio_arma) mods.dano += Number(mat.mods.dano_frio_arma) || 0;
                if (mat.mods.critico_margem_arma)
                    mods.critico_margem += Number(mat.mods.critico_margem_arma) || 0;
            }
        }
        return mods;
    }

    function custoEstimado(nMelhorias, materialSlug) {
        const precos = (_superiores && _superiores.precos_melhoria) || [300, 3000, 9000, 18000];
        const n = Math.max(0, Math.min(4, nMelhorias));
        let total = parseCustoTs($('t20AtqFormCustoBase') && $('t20AtqFormCustoBase').value);
        for (let i = 0; i < n; i++) total += Number(precos[i]) || 0;
        // Material especial conta como melhoria na regra, mas preço extra na T3-9
        if (materialSlug && nMelhorias === 0) {
            // se só material, ainda precisa da melhoria "material especial" — UI trata material separado;
            // preço: 1ª melhoria + material
            total += Number(precos[0]) || 300;
        }
        if (materialSlug && _superiores) {
            const mat = (_superiores.materiais || []).find((x) => x.slug === materialSlug);
            const extra = mat && mat.custo_ts && mat.custo_ts.arma;
            if (extra) total += Number(extra) || 0;
        }
        return total;
    }

    function nomeComposto(base, slugs, materialSlug) {
        const rows = (_superiores && _superiores.melhorias) || [];
        const nomesMel = slugs
            .map((s) => {
                const r = rows.find((x) => x.slug === s);
                return r ? String(r.nome).toLowerCase() : s;
            })
            .filter(Boolean);
        let matNome = '';
        if (materialSlug && _superiores) {
            const mat = (_superiores.materiais || []).find((x) => x.slug === materialSlug);
            matNome = mat ? String(mat.nome) : materialSlug;
        }
        let nome = String(base || '').trim() || 'Arma';
        if (nomesMel.length) nome += ' ' + nomesMel.join(', ');
        if (matNome) nome += ' de ' + matNome;
        return nome;
    }

    function atualizarPreviewSuperior() {
        const base = ($('t20AtqFormArmaBase') && $('t20AtqFormArmaBase').value) ||
            ($('t20AtqFormNome') && $('t20AtqFormNome').value) ||
            '';
        const slugs = melhoriasSelecionadas();
        const mat = ($('t20AtqMaterial') && $('t20AtqMaterial').value) || '';
        const nMel = slugs.length + (mat ? 1 : 0);
        const prev = $('t20AtqPreviewSuperior');
        if (prev) {
            const nome = nomeComposto(base, slugs, mat);
            const custo = custoEstimado(slugs.length + (mat ? 1 : 0), mat);
            prev.textContent =
                (nome || '—') +
                (custo ? ' · ≈ T$ ' + custo.toLocaleString('pt-BR') : '') +
                (nMel ? ' · ' + Math.min(nMel, 4) + '/4 melhorias' : '');
        }
    }

    function coletarFormComoAtaque() {
        const slugs = melhoriasSelecionadas();
        const mat = ($('t20AtqMaterial') && $('t20AtqMaterial').value) || '';
        const mods = modsDasMelhorias(slugs);
        let bonus = parseBonusNum($('t20AtqFormBonus') && $('t20AtqFormBonus').value);
        bonus += mods.ataque;
        let dano = ($('t20AtqFormDano') && $('t20AtqFormDano').value.trim()) || '';
        dano = aplicarDanoBonus(dano, mods.dano);
        let critico = ($('t20AtqFormCritico') && $('t20AtqFormCritico').value.trim()) || '';
        if (mods.critico_margem && critico) {
            // só anota em notas se não parseável simples
            const notasExtra = 'margem +' + mods.critico_margem;
            const notasBase = ($('t20AtqFormNotas') && $('t20AtqFormNotas').value.trim()) || '';
            if ($('t20AtqFormNotas') && !notasBase.includes('margem')) {
                $('t20AtqFormNotas').value = (notasBase ? notasBase + '; ' : '') + notasExtra;
            }
        }
        const armaBase =
            ($('t20AtqFormArmaBase') && $('t20AtqFormArmaBase').value.trim()) ||
            ($('t20AtqFormNome') && $('t20AtqFormNome').value.trim()) ||
            '';
        let nome = ($('t20AtqFormNome') && $('t20AtqFormNome').value.trim()) || '';
        if (slugs.length || mat) {
            nome = nomeComposto(armaBase || nome, slugs, mat);
            if ($('t20AtqFormNome')) $('t20AtqFormNome').value = nome;
        }
        const custo = custoEstimado(slugs.length + (mat ? 1 : 0), mat);
        return {
            nome: nome,
            bonus_ataque: formatBonus(bonus),
            teste: formatBonus(bonus),
            dano: dano,
            tipo_dano: ($('t20AtqFormTipo') && $('t20AtqFormTipo').value.trim()) || '',
            tipo: ($('t20AtqFormTipo') && $('t20AtqFormTipo').value.trim()) || '',
            critico: critico,
            alcance: ($('t20AtqFormAlcance') && $('t20AtqFormAlcance').value.trim()) || '',
            empunhado: Boolean($('t20AtqFormEmp') && $('t20AtqFormEmp').checked),
            arma_base: armaBase,
            melhorias: slugs,
            material: mat || '',
            custo_ts_estimado: custo || null,
            notas: ($('t20AtqFormNotas') && $('t20AtqFormNotas').value.trim()) || '',
        };
    }

    function aplicarFormNaLista() {
        const atq = coletarFormComoAtaque();
        if (!atq.nome && !atq.dano) return;
        if (_editIdx >= 0 && _editIdx < _draft.length) {
            const prev = _draft[_editIdx];
            atq.origem = prev.origem;
            atq.arma_natural = prev.arma_natural;
            _draft[_editIdx] = atq;
        } else {
            _draft.push(atq);
        }
        _editIdx = -1;
        renderDraftLista();
        limparFormulario();
        setAba('lista');
    }

    function renderDraftLista() {
        const lista = $('t20AtqDraftLista');
        if (!lista) return;
        if (!_draft.length) {
            lista.innerHTML = '<p class="t20-hint">Nenhum ataque na lista ainda.</p>';
            return;
        }
        lista.innerHTML = _draft
            .map((a, i) => {
                const chips = [];
                (a.melhorias || []).forEach((s) => chips.push(s));
                if (a.material) chips.push(a.material);
                const chipHtml = chips.length
                    ? '<span class="t20-atq-chips">' +
                      chips.map((c) => '<span class="t20-atq-chip">' + esc(c) + '</span>').join('') +
                      '</span>'
                    : '';
                return (
                    '<div class="t20-atq-draft-row" data-idx="' +
                    i +
                    '">' +
                    '<div class="t20-atq-draft-main">' +
                    '<strong>' +
                    esc(a.nome || '—') +
                    '</strong> ' +
                    '<span>' +
                    esc(a.bonus_ataque || a.teste || '—') +
                    '</span> · ' +
                    '<span>' +
                    esc(a.dano || '—') +
                    '</span>' +
                    (a.empunhado ? ' 🖐' : '') +
                    chipHtml +
                    '</div>' +
                    '<div class="t20-atq-draft-actions">' +
                    '<button type="button" class="tormenta-btn t20-atq-edit" data-idx="' +
                    i +
                    '">Editar</button>' +
                    '<button type="button" class="tormenta-btn t20-atq-del" data-idx="' +
                    i +
                    '" style="background:#b91c1c;color:#fff">✕</button>' +
                    '</div></div>'
                );
            })
            .join('');
        lista.querySelectorAll('.t20-atq-edit').forEach((btn) => {
            btn.addEventListener('click', () => editarDraft(Number(btn.getAttribute('data-idx'))));
        });
        lista.querySelectorAll('.t20-atq-del').forEach((btn) => {
            btn.addEventListener('click', () => {
                const i = Number(btn.getAttribute('data-idx'));
                _draft.splice(i, 1);
                renderDraftLista();
            });
        });
    }

    function editarDraft(idx) {
        const a = _draft[idx];
        if (!a) return;
        _editIdx = idx;
        $('t20AtqFormNome').value = a.nome || '';
        $('t20AtqFormArmaBase').value = a.arma_base || a.nome || '';
        // Reverter mods de ataque para o campo base (evita somar 2× ao salvar de novo)
        let bonus = parseBonusNum(a.bonus_ataque || a.teste || 0);
        $('t20AtqFormDano').value = a.dano || '';
        $('t20AtqFormTipo').value = a.tipo_dano || a.tipo || '';
        $('t20AtqFormCritico').value = a.critico || '';
        $('t20AtqFormAlcance').value = a.alcance || '';
        $('t20AtqFormEmp').checked = a.empunhado === true;
        $('t20AtqFormNotas').value = a.notas || '';
        document.querySelectorAll('#t20AtqMelhoriasChecks input').forEach((cb) => {
            cb.checked = (a.melhorias || []).indexOf(cb.getAttribute('data-melhoria')) >= 0;
        });
        if ($('t20AtqMaterial')) $('t20AtqMaterial').value = a.material || '';
        const modsNow = modsDasMelhorias(a.melhorias || []);
        bonus -= modsNow.ataque;
        $('t20AtqFormBonus').value = formatBonus(bonus);
        // Dano: tentar remover +mods.dano do final
        if (modsNow.dano) {
            const d = String(a.dano || '');
            const m = d.match(/^(.*?)([+-]\d+)\s*$/);
            if (m) {
                const cur = parseInt(m[2], 10) || 0;
                const novo = cur - modsNow.dano;
                $('t20AtqFormDano').value = m[1] + (novo >= 0 ? '+' : '') + novo;
                if (novo === 0 && m[1].endsWith('+')) {
                    $('t20AtqFormDano').value = m[1].replace(/\+$/, '');
                }
            }
        }
        atualizarPreviewSuperior();
        const btn = $('t20AtqBtnAplicarForm');
        if (btn) btn.textContent = '💾 Atualizar linha';
    }

    function salvarTudo() {
        const out = _draft
            .map(cloneAtaque)
            .filter((x) => x.nome || x.dano || x.bonus_ataque);
        if (typeof global.t20AplicarAtaquesDoModal === 'function') {
            global.t20AplicarAtaquesDoModal(out);
        } else {
            global.t20AtaquesLista = out;
            if (typeof global.renderT20AtaquesLista === 'function') global.renderT20AtaquesLista();
        }
        fechar();
    }

    function bind() {
        const ov = overlay();
        if (!ov || ov.dataset.t20AtqBound === '1') return;
        ov.dataset.t20AtqBound = '1';
        $('t20BtnFecharModalAtaques')?.addEventListener('click', fechar);
        $('t20AtqBtnCancelar')?.addEventListener('click', fechar);
        $('t20AtqBtnSalvarTudo')?.addEventListener('click', salvarTudo);
        $('t20AtqBtnAplicarForm')?.addEventListener('click', aplicarFormNaLista);
        $('t20AtqBtnLimparForm')?.addEventListener('click', limparFormulario);
        ov.addEventListener('click', (e) => {
            if (e.target === ov) fechar();
        });
        $('t20AtqAbaLivro')?.addEventListener('click', () => setAba('livro'));
        $('t20AtqAbaInventario')?.addEventListener('click', () => {
            setAba('inventario');
            renderInventario();
        });
        $('t20AtqAbaLista')?.addEventListener('click', () => {
            setAba('lista');
            renderDraftLista();
        });
        $('t20AtqBusca')?.addEventListener('input', () => {
            clearTimeout(_buscaTimer);
            _buscaTimer = setTimeout(() => {
                carregarCatalogoArmas(($('t20AtqBusca') && $('t20AtqBusca').value) || '');
            }, 280);
        });
        ['t20AtqFormNome', 't20AtqFormArmaBase'].forEach((id) => {
            $(id)?.addEventListener('input', atualizarPreviewSuperior);
        });
    }

    function init() {
        bind();
    }

    global.T20AtaquesModal = {
        abrir,
        fechar,
        init,
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})(typeof window !== 'undefined' ? window : globalThis);
