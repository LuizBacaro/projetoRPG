/**
 * Ficha Tormenta — consumíveis MB (modal no padrão equipamentos) e companheiro animal (localStorage por ficha).
 */
(function () {
    const LS_COMP = 't20FichaCompanheiros_v1';
    let catalogoConsum = null;
    let _consModalCtx = null;
    let _consBuscaT = null;

    function esc(s) {
        return String(s ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    async function carregarCatalogoConsum() {
        if (catalogoConsum) return catalogoConsum;
        const r = await fetch('/games/tormenta/data/arena-consumiveis-mb.json?v=20260512', { cache: 'no-cache' });
        if (!r.ok) throw new Error('Catálogo de consumíveis indisponível');
        catalogoConsum = await r.json();
        return catalogoConsum;
    }

    function flatCatalogoConsumItems() {
        if (!catalogoConsum) return [];
        const out = [];
        (catalogoConsum.pocoes || []).forEach((p) => {
            out.push({ tipo: 'pocao', nome: p.nome || '', nota: p.nota, circulo: null });
        });
        (catalogoConsum.pergaminhos || []).forEach((p) => {
            out.push({ tipo: 'pergaminho', nome: p.nome || '', nota: null, circulo: p.circulo });
        });
        return out.filter((x) => x.nome);
    }

    function _consSpecPar(lbl, val) {
        if (val == null || String(val).trim() === '') return '';
        return `<div class="equipamento-spec-par" role="listitem"><span class="equipamento-spec-lbl">${esc(
            lbl
        )}</span><span class="equipamento-spec-val">${esc(String(val))}</span></div>`;
    }

    function montarHtmlConsumCatalogoItem(it) {
        const nome = it.nome || '';
        const secao = it.tipo === 'pocao' ? 'Poção (MB)' : 'Pergaminho (MB)';
        let gridClass = 'equipamento-spec-grid--unica';
        let gridBody = '';
        if (it.tipo === 'pocao') {
            gridBody = `<div role="list">${_consSpecPar('Nota / efeito (mesa)', it.nota || '—')}</div>`;
        } else {
            const circ = it.circulo != null && it.circulo !== '' ? `${it.circulo}º círculo` : '—';
            gridBody = `<div role="list">${_consSpecPar('Círculo', circ)}</div>`;
        }
        const nomeEnc = encodeURIComponent(nome);
        return `<article class="talento-linha equipamento-catalogo-linha">
            <div class="talento-linha-conteudo">
                <div class="talento-linha-cabecalho">
                    <span class="talento-linha-nome">${esc(nome)}</span>
                    <span class="talento-linha-secao">${esc(secao)}</span>
                </div>
                <div class="equipamento-spec-grid ${gridClass}">${gridBody}</div>
            </div>
            <div class="equipamento-catalogo-acoes">
                <button type="button" class="talento-linha-acao item-btn-primary" data-cons-add="${nomeEnc}">➕ Adicionar</button>
            </div>
        </article>`;
    }

    function fecharModalConsumiveisTormenta() {
        const ov = document.getElementById('modalConsumiveisTormenta');
        if (!ov) return;
        const ae = document.activeElement;
        if (ae && typeof ov.contains === 'function' && ov.contains(ae)) {
            ae.blur();
        }
        ov.classList.remove('is-open');
        ov.setAttribute('aria-hidden', 'true');
    }

    function abaConsumModalTormenta(modo) {
        const aL = document.getElementById('abaListarConsumMb');
        const aC = document.getElementById('abaCriarConsumMb');
        const cL = document.getElementById('conteudoListarConsumMb');
        const cC = document.getElementById('conteudoCriarConsumMb');
        if (modo === 'criar') {
            if (aL) aL.classList.remove('ativa');
            if (aC) aC.classList.add('ativa');
            if (cL) cL.classList.remove('ativo');
            if (cC) cC.classList.add('ativo');
        } else {
            if (aL) aL.classList.add('ativa');
            if (aC) aC.classList.remove('ativa');
            if (cL) cL.classList.add('ativo');
            if (cC) cC.classList.remove('ativo');
        }
    }

    function renderConsumCatalogoTormenta() {
        const lista = document.getElementById('consumiveisListaCatalogoMb');
        if (!lista) return;
        const busInp = document.getElementById('consumiveisTormentaBusca');
        const qNorm = (busInp && String(busInp.value || '').trim().toLowerCase()) || '';
        const all = flatCatalogoConsumItems();
        const fil = qNorm
            ? all.filter((x) => String(x.nome || '').toLowerCase().includes(qNorm))
            : all;
        fil.sort((a, b) => String(a.nome).localeCompare(String(b.nome), 'pt-BR'));
        lista.innerHTML = fil.length ? fil.map((x) => montarHtmlConsumCatalogoItem(x)).join('') : '<p class="t20-ficha-vazio">Nenhum item corresponde à busca.</p>';
    }

    async function persistirConsumivelNaFicha(nome, qtdRaw) {
        const ctx = _consModalCtx;
        if (!ctx || !ctx.svc || !ctx.q) return;
        const { svc, q, preencherConsumiveisFromApi } = ctx;
        const nomeTrim = String(nome || '').trim();
        if (!nomeTrim) return;
        let qtdNum = 1;
        try {
            const raw = qtdRaw != null && String(qtdRaw).trim() !== '' ? qtdRaw : '1';
            qtdNum = Math.max(1, Math.min(999, parseInt(String(raw), 10) || 1));
        } catch (_e) {
            qtdNum = 1;
        }
        const fid = q('fichaId') && q('fichaId').value;
        if (!fid) {
            if (typeof Toast !== 'undefined') Toast.error('Salve a ficha antes.');
            return;
        }
        try {
            await svc.adicionarConsumivel(fid, { nome: nomeTrim, quantidade: qtdNum });
            if (typeof Toast !== 'undefined') Toast.success('Consumível adicionado.');
            const p = await svc.obter(fid);
            if (typeof preencherConsumiveisFromApi === 'function') {
                preencherConsumiveisFromApi(p.consumiveis || []);
            }
            fecharModalConsumiveisTormenta();
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro ao adicionar consumível');
        }
    }

    function wireModalConsumiveisTormenta(ctx) {
        const ov = document.getElementById('modalConsumiveisTormenta');
        if (!ctx || !ov || ov.dataset.wiredCons) return;
        ov.dataset.wiredCons = '1';

        document.getElementById('btnFecharModalConsumiveisTormenta')?.addEventListener('click', () => fecharModalConsumiveisTormenta());
        if (ov) {
            ov.addEventListener('click', (e) => {
                if (e.target === ov) fecharModalConsumiveisTormenta();
            });
        }
        document.getElementById('abaListarConsumMb')?.addEventListener('click', () => abaConsumModalTormenta('listar'));
        document.getElementById('abaCriarConsumMb')?.addEventListener('click', () => abaConsumModalTormenta('criar'));

        const lista = document.getElementById('consumiveisListaCatalogoMb');
        if (lista && !lista.dataset.consDeleg) {
            lista.dataset.consDeleg = '1';
            lista.addEventListener('click', (ev) => {
                const btn = ev.target.closest('[data-cons-add]');
                if (!btn) return;
                const enc = btn.getAttribute('data-cons-add') || '';
                let nome = '';
                try {
                    nome = decodeURIComponent(enc);
                } catch (_e) {
                    nome = enc;
                }
                const qInp = document.getElementById('consumiveisTormentaQuantidade');
                const qtd = qInp ? qInp.value : '1';
                persistirConsumivelNaFicha(nome, qtd);
            });
        }

        const busInp = document.getElementById('consumiveisTormentaBusca');
        if (busInp && !busInp.dataset.boundConsBusca) {
            busInp.dataset.boundConsBusca = '1';
            busInp.addEventListener('input', () => {
                clearTimeout(_consBuscaT);
                _consBuscaT = setTimeout(() => renderConsumCatalogoTormenta(), 280);
            });
        }

        document.getElementById('btnSalvarConsumivelCustomizado')?.addEventListener('click', async () => {
            const nome = (document.getElementById('criarNomeConsumivel') && document.getElementById('criarNomeConsumivel').value.trim()) || '';
            if (!nome) {
                if (typeof Toast !== 'undefined') Toast.error('Informe o nome do consumível.');
                return;
            }
            const desc = (document.getElementById('criarDescricaoConsumivel') && document.getElementById('criarDescricaoConsumivel').value.trim()) || '';
            const pag = (document.getElementById('criarPaginaRefConsumivel') && document.getElementById('criarPaginaRefConsumivel').value.trim()) || '';
            const qtd = (document.getElementById('criarQuantidadeConsumivel') && document.getElementById('criarQuantidadeConsumivel').value) || '1';
            let linha = nome;
            if (desc) linha += ` — ${desc}`;
            if (pag) linha += ` (${pag})`;
            await persistirConsumivelNaFicha(linha, qtd);
            ['criarNomeConsumivel', 'criarDescricaoConsumivel', 'criarPaginaRefConsumivel'].forEach((id) => {
                const n = document.getElementById(id);
                if (n) n.value = '';
            });
            const qEl = document.getElementById('criarQuantidadeConsumivel');
            if (qEl) qEl.value = '1';
        });
    }

    async function openConsumiveisModal() {
        const loadEl = document.getElementById('consumiveisTormentaLoading');
        const ov = document.getElementById('modalConsumiveisTormenta');
        const qtd = document.getElementById('consumiveisTormentaQuantidade');
        const busca = document.getElementById('consumiveisTormentaBusca');
        if (qtd) qtd.value = '1';
        if (busca) busca.value = '';
        abaConsumModalTormenta('listar');
        if (ov) {
            ov.classList.add('is-open');
            ov.setAttribute('aria-hidden', 'false');
        }
        if (loadEl) loadEl.style.display = '';
        try {
            await carregarCatalogoConsum();
            renderConsumCatalogoTormenta();
        } catch (_e) {
            const lista = document.getElementById('consumiveisListaCatalogoMb');
            if (lista) lista.innerHTML = '<p class="t20-ficha-vazio">Catálogo indisponível. Tente «Criar novo».</p>';
        }
        if (loadEl) loadEl.style.display = 'none';
    }

    function formCompanheiroVazio() {
        return {
            nome: '',
            especie: '',
            tendencia: '',
            nivel: '',
            niveis_criatura: '',
            tamanho: '',
            deslocamento: '',
            sentidos: '',
            for_v: '',
            for_m: '',
            des_v: '',
            des_m: '',
            con_v: '',
            con_m: '',
            int_v: '',
            int_m: '',
            sab_v: '',
            sab_m: '',
            car_v: '',
            car_m: '',
            ca_nv: '',
            ca_des: '',
            ca_tam: '',
            ca_nat: '',
            ca_out: '',
            fort_nv: '',
            fort_hab: '',
            fort_out: '',
            ref_nv: '',
            ref_hab: '',
            ref_out: '',
            von_nv: '',
            von_hab: '',
            von_out: '',
            pv_max: '',
            pv_atual: '',
            atk1: '',
            atk1b: '',
            atk1d: '',
            atk1c: '',
            atk1t: '',
            atk2: '',
            atk2b: '',
            atk2d: '',
            atk2c: '',
            atk2t: '',
            atk3: '',
            atk3b: '',
            atk3d: '',
            atk3c: '',
            atk3t: '',
            pericias: '',
            talentos: '',
            hab1: '',
            hab2: '',
            hab3: '',
            equipamento: '',
            anotacoes: '',
        };
    }

    const MAP_IDS = {
        t20CompNome: 'nome',
        t20CompEspecie: 'especie',
        t20CompTend: 'tendencia',
        t20CompNivel: 'nivel',
        t20CompNvCri: 'niveis_criatura',
        t20CompTam: 'tamanho',
        t20CompDesl: 'deslocamento',
        t20CompSent: 'sentidos',
        t20CompForV: 'for_v',
        t20CompForM: 'for_m',
        t20CompDesV: 'des_v',
        t20CompDesM: 'des_m',
        t20CompConV: 'con_v',
        t20CompConM: 'con_m',
        t20CompIntV: 'int_v',
        t20CompIntM: 'int_m',
        t20CompSabV: 'sab_v',
        t20CompSabM: 'sab_m',
        t20CompCarV: 'car_v',
        t20CompCarM: 'car_m',
        t20CompCaNv: 'ca_nv',
        t20CompCaDes: 'ca_des',
        t20CompCaTam: 'ca_tam',
        t20CompCaNat: 'ca_nat',
        t20CompCaOut: 'ca_out',
        t20CompFortNv: 'fort_nv',
        t20CompFortHab: 'fort_hab',
        t20CompFortOut: 'fort_out',
        t20CompRefNv: 'ref_nv',
        t20CompRefHab: 'ref_hab',
        t20CompRefOut: 'ref_out',
        t20CompVonNv: 'von_nv',
        t20CompVonHab: 'von_hab',
        t20CompVonOut: 'von_out',
        t20CompPvMax: 'pv_max',
        t20CompPvAtu: 'pv_atual',
        t20CompAtk1: 'atk1',
        t20CompAtk1b: 'atk1b',
        t20CompAtk1d: 'atk1d',
        t20CompAtk1c: 'atk1c',
        t20CompAtk1t: 'atk1t',
        t20CompAtk2: 'atk2',
        t20CompAtk2b: 'atk2b',
        t20CompAtk2d: 'atk2d',
        t20CompAtk2c: 'atk2c',
        t20CompAtk2t: 'atk2t',
        t20CompAtk3: 'atk3',
        t20CompAtk3b: 'atk3b',
        t20CompAtk3d: 'atk3d',
        t20CompAtk3c: 'atk3c',
        t20CompAtk3t: 'atk3t',
        t20CompPer: 'pericias',
        t20CompTal: 'talentos',
        t20CompHab1: 'hab1',
        t20CompHab2: 'hab2',
        t20CompHab3: 'hab3',
        t20CompEq: 'equipamento',
        t20CompAnot: 'anotacoes',
    };

    function preencherModalComp(c) {
        const d = { ...formCompanheiroVazio(), ...c };
        Object.keys(MAP_IDS).forEach((id) => {
            const el = document.getElementById(id);
            if (el) el.value = d[MAP_IDS[id]] != null ? String(d[MAP_IDS[id]]) : '';
        });
    }

    function lerModalComp() {
        const o = formCompanheiroVazio();
        Object.keys(MAP_IDS).forEach((id) => {
            const el = document.getElementById(id);
            o[MAP_IDS[id]] = el ? String(el.value || '').trim() : '';
        });
        return o;
    }

    function lerCompanheiros(fid) {
        try {
            const raw = localStorage.getItem(LS_COMP);
            const all = raw ? JSON.parse(raw) : {};
            return Array.isArray(all[String(fid)]) ? all[String(fid)] : [];
        } catch (_e) {
            return [];
        }
    }

    function salvarCompanheiros(fid, arr) {
        try {
            const raw = localStorage.getItem(LS_COMP);
            const all = raw ? JSON.parse(raw) : {};
            all[String(fid)] = arr;
            localStorage.setItem(LS_COMP, JSON.stringify(all));
        } catch (_e) {}
    }

    window.T20FichaMbExtras = {
        openConsumiveisModal: openConsumiveisModal,
        fecharModalConsumiveisTormenta: fecharModalConsumiveisTormenta,

        async init(ctx) {
            const { svc, q, preencherConsumiveisFromApi } = ctx;
            if (!svc || !q) return;

            _consModalCtx = { svc, q, preencherConsumiveisFromApi };
            wireModalConsumiveisTormenta(_consModalCtx);

            const host = document.getElementById('t20FichaCompLista');
            const dlg = document.getElementById('t20FichaModalCompanheiro');

            function renderListaComp() {
                const fid = q('fichaId') && q('fichaId').value;
                if (!host) return;
                if (!fid) {
                    host.innerHTML = '<p class="t20-ficha-comp-vazio">Salve a ficha para cadastrar companheiros.</p>';
                    return;
                }
                const arr = lerCompanheiros(fid);
                if (!arr.length) {
                    host.innerHTML = '<p class="t20-ficha-comp-vazio">Nenhum companheiro. Use «Adicionar».</p>';
                    return;
                }
                host.innerHTML = arr
                    .map((c, i) => {
                        const tit = esc(c.nome || `Companheiro ${i + 1}`);
                        const sub = esc(c.especie || '—');
                        return `<div class="t20-ficha-comp-card" data-idx="${i}">
                            <div><strong>${tit}</strong><br><span class="t20-ficha-comp-sub">${sub}</span></div>
                            <div class="t20-ficha-comp-acoes">
                                <button type="button" class="tormenta-btn t20-ficha-comp-edit" data-idx="${i}">Editar</button>
                                <button type="button" class="tormenta-btn t20-ficha-comp-del" data-idx="${i}">Excluir</button>
                            </div>
                        </div>`;
                    })
                    .join('');
            }

            function fecharComp() {
                if (dlg && typeof dlg.close === 'function') dlg.close();
            }

            function abrirComp(idx) {
                const fid = q('fichaId') && q('fichaId').value;
                if (!dlg) return;
                dlg.dataset.editIdx = idx != null && idx >= 0 ? String(idx) : '';
                if (fid && idx != null && idx >= 0) {
                    const arr = lerCompanheiros(fid);
                    preencherModalComp(arr[idx] || {});
                } else {
                    preencherModalComp({});
                }
                if (typeof dlg.showModal === 'function') dlg.showModal();
            }

            if (host && !host.dataset.boundComp) {
                host.dataset.boundComp = '1';
                host.addEventListener('click', (ev) => {
                    const ed = ev.target.closest('.t20-ficha-comp-edit');
                    const del = ev.target.closest('.t20-ficha-comp-del');
                    if (ed) {
                        abrirComp(Number(ed.getAttribute('data-idx')));
                        return;
                    }
                    if (del) {
                        const i = Number(del.getAttribute('data-idx'));
                        const fid2 = q('fichaId') && q('fichaId').value;
                        if (!fid2 || !confirm('Excluir este companheiro?')) return;
                        const arr = lerCompanheiros(fid2).filter((_, j) => j !== i);
                        salvarCompanheiros(fid2, arr);
                        renderListaComp();
                    }
                });
            }

            const btnAddComp = document.getElementById('btnT20FichaAddComp');
            if (btnAddComp && !btnAddComp.dataset.bound) {
                btnAddComp.dataset.bound = '1';
                btnAddComp.addEventListener('click', () => abrirComp(null));
            }
            const btnFechar = document.getElementById('t20FichaModalCompFechar');
            const btnCancel = document.getElementById('t20FichaModalCompCancelar');
            const btnSalvar = document.getElementById('t20FichaModalCompSalvar');
            if (btnFechar && !btnFechar.dataset.bound) {
                btnFechar.dataset.bound = '1';
                btnFechar.addEventListener('click', fecharComp);
            }
            if (btnCancel && !btnCancel.dataset.bound) {
                btnCancel.dataset.bound = '1';
                btnCancel.addEventListener('click', fecharComp);
            }
            if (btnSalvar && !btnSalvar.dataset.bound) {
                btnSalvar.dataset.bound = '1';
                btnSalvar.addEventListener('click', () => {
                    const fid3 = q('fichaId') && q('fichaId').value;
                    if (!fid3) return;
                    const nome =
                        (document.getElementById('t20CompNome') && document.getElementById('t20CompNome').value.trim()) || '';
                    if (nome.length < 2) {
                        if (typeof Toast !== 'undefined') Toast.error('Informe o nome do companheiro.');
                        return;
                    }
                    const data = lerModalComp();
                    data.nome = nome;
                    const arr = lerCompanheiros(fid3);
                    const idxStr = dlg && dlg.dataset ? dlg.dataset.editIdx : '';
                    const idx = idxStr !== '' && idxStr != null ? Number(idxStr) : -1;
                    if (idx >= 0 && idx < arr.length) arr[idx] = data;
                    else arr.push(data);
                    salvarCompanheiros(fid3, arr);
                    fecharComp();
                    renderListaComp();
                    if (typeof Toast !== 'undefined') Toast.success('Companheiro guardado (neste navegador).');
                });
            }

            window.__t20FichaMbExtrasRefreshComp = renderListaComp;
            renderListaComp();
        },
    };
})();
