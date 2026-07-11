/**
 * Escolhas raciais v1.3 — Lefou, Qareen, Dahllan, Golem, Kliren, Osteon, Sereia, Sílfide.
 */
(function (global) {
    'use strict';

    const CACHE = {};
    let bound = false;
    let periciasCatalogo = null;
    let periciasCatalogoPromise = null;

    const PERICIAS_FALLBACK_NOMES = [
        'Acrobacia',
        'Adestramento',
        'Atletismo',
        'Enganação',
        'Furtividade',
        'Iniciativa',
        'Intimidação',
        'Ladinagem',
        'Misticismo',
        'Percepção',
        'Sobrevivência',
    ];

    function q(id) {
        return document.getElementById(id);
    }

    function isV13() {
        if (typeof global.getRegraVersaoAtiva === 'function') {
            return global.T20RegraVersao && global.T20RegraVersao.isV13(global.getRegraVersaoAtiva());
        }
        return global.T20RegraVersao && global.T20RegraVersao.isV13('v13');
    }

    function isCadastro(prefix) {
        return prefix === 'cad';
    }

    function ids(prefix) {
        const p = prefix || 'f';
        return {
            wrapLefou: q(`${p === 'cad' ? 'cad' : 'wrap'}${p === 'cad' ? 'Wrap' : ''}LefouDeformidade`.replace('wrapWrap', 'wrap')),
            lefouModo: q(`${p === 'cad' ? 'cad' : 'f'}_lefou_deformidade_modo`),
            lefouPer1: q(`${p === 'cad' ? 'cad' : 'f'}_lefou_pericia_1`),
            lefouPer2: q(`${p === 'cad' ? 'cad' : 'f'}_lefou_pericia_2`),
            lefouPodWrap: q(`${p === 'cad' ? 'cad' : 'wrap'}${p === 'cad' ? 'Wrap' : ''}LefouPoderTormenta`.replace('wrapWrap', 'wrap')),
            lefouPodNome: q(`${p === 'cad' ? 'cad' : 'f'}_lefou_poder_tormenta_nome`),
            wrapQareen: q(`${p === 'cad' ? 'cad' : 'wrap'}${p === 'cad' ? 'Wrap' : ''}QareenEscolhas`.replace('wrapWrap', 'wrap')),
            qareenAsc: q(`${p === 'cad' ? 'cad' : 'f'}_qareen_ascendencia`),
            qareenMagia: q(`${p === 'cad' ? 'cad' : 'f'}_qareen_magia_nome`),
            wrapDahllan: q(`${p === 'cad' ? 'cad' : 'wrap'}${p === 'cad' ? 'Wrap' : ''}DahllanMagias`.replace('wrapWrap', 'wrap')),
            dahllanHint: q(`${p === 'cad' ? 'cad' : ''}DahllanMagiasHint`.replace('cadDahllan', 'cadDahllan')),
            racaSelect: q(p === 'cad' ? 'cadRacaSelect' : 'f_raca_select'),
        };
    }

    function fichaIds() {
        return {
            wrapLefou: q('wrapLefouDeformidade'),
            lefouModo: q('f_lefou_deformidade_modo'),
            lefouPer1: q('f_lefou_pericia_1'),
            lefouPer2: q('f_lefou_pericia_2'),
            lefouPodWrap: q('wrapLefouPoderTormenta'),
            lefouPodNome: q('f_lefou_poder_tormenta_nome'),
            wrapQareen: q('wrapQareenEscolhas'),
            qareenAsc: q('f_qareen_ascendencia'),
            qareenMagia: q('f_qareen_magia_nome'),
            wrapDahllan: q('wrapDahllanMagias'),
            dahllanHint: q('dahllanMagiasHint'),
            wrapOsteon: q('wrapOsteonMemoria'),
            osteonModo: q('f_osteon_memoria_modo'),
            osteonPer: q('f_osteon_memoria_pericia'),
            osteonPodWrap: q('wrapOsteonPoderGeral'),
            osteonPodNome: q('f_osteon_memoria_poder_nome'),
            wrapSereia: q('wrapSereiaMagias'),
            sereiaMag1: q('f_sereia_magia_1'),
            sereiaMag2: q('f_sereia_magia_2'),
            wrapGolem: q('wrapGolemEscolhas'),
            golemFonte: q('f_golem_fonte_elemental'),
            golemPodNome: q('f_golem_poder_geral_nome'),
            wrapKliren: q('wrapKlirenEscolhas'),
            klirenPer: q('f_kliren_pericia'),
            klirenOficio: q('f_kliren_oficio'),
            wrapSilfide: q('wrapSilfideMagias'),
            silfideMag1: q('f_silfide_magia_1'),
            silfideMag2: q('f_silfide_magia_2'),
            racaSelect: q('f_raca_select'),
        };
    }

    function cadIds() {
        return {
            wrapLefou: q('cadWrapLefouDeformidade'),
            lefouModo: q('cadLefouDeformidadeModo'),
            lefouPer1: q('cadLefouPericia1'),
            lefouPer2: q('cadLefouPericia2'),
            lefouPodWrap: q('cadWrapLefouPoderTormenta'),
            lefouPodNome: q('cadLefouPoderTormentaNome'),
            wrapQareen: q('cadWrapQareenEscolhas'),
            qareenAsc: q('cadQareenAscendencia'),
            qareenMagia: q('cadQareenMagiaNome'),
            wrapDahllan: q('cadWrapDahllanMagias'),
            dahllanHint: q('cadDahllanMagiasHint'),
            wrapOsteon: q('cadWrapOsteonMemoria'),
            osteonModo: q('cadOsteonMemoriaModo'),
            osteonPer: q('cadOsteonMemoriaPericia'),
            osteonPodWrap: q('cadWrapOsteonPoderGeral'),
            osteonPodNome: q('cadOsteonMemoriaPoderNome'),
            wrapSereia: q('cadWrapSereiaMagias'),
            sereiaMag1: q('cadSereiaMagia1'),
            sereiaMag2: q('cadSereiaMagia2'),
            wrapGolem: q('cadWrapGolemEscolhas'),
            golemFonte: q('cadGolemFonteElemental'),
            golemPodNome: q('cadGolemPoderGeralNome'),
            wrapKliren: q('cadWrapKlirenEscolhas'),
            klirenPer: q('cadKlirenPericia'),
            klirenOficio: q('cadKlirenOficio'),
            wrapSilfide: q('cadWrapSilfideMagias'),
            silfideMag1: q('cadSilfideMagia1'),
            silfideMag2: q('cadSilfideMagia2'),
            racaSelect: q('cadRacaSelect'),
        };
    }

    function popularMagiasEscolha(sel1, sel2, data) {
        const cur1 = sel1 && sel1.value;
        const cur2 = sel2 && sel2.value;
        const opts = (data && data.raca && data.raca.magias_opcoes) || [];
        [sel1, sel2].forEach((sel) => {
            if (!sel) return;
            sel.innerHTML = '<option value="">—</option>';
            opts.forEach((row) => {
                const o = document.createElement('option');
                o.value = row.slug;
                o.textContent = row.nome;
                sel.appendChild(o);
            });
        });
        if (sel1 && cur1) sel1.value = cur1;
        if (sel2 && cur2) sel2.value = cur2;
    }

    function popularMagiasSereia(sel1, sel2, data) {
        popularMagiasEscolha(sel1, sel2, data);
    }

    function popularFontesGolem(sel, data) {
        if (!sel || !data || !data.raca) return;
        const cur = sel.value;
        sel.innerHTML = '<option value="">— Escolha —</option>';
        (data.raca.fontes || []).forEach((row) => {
            const o = document.createElement('option');
            o.value = row.slug;
            o.textContent = `${row.rotulo} (imune ${row.imunidade_tipo})`;
            sel.appendChild(o);
        });
        if (cur) sel.value = cur;
    }

    function lerMagiasDuplas(sel1, sel2) {
        const out = [];
        [sel1, sel2].forEach((sel) => {
            const v = sel && sel.value ? String(sel.value).trim().toLowerCase() : '';
            if (v && !out.includes(v)) out.push(v);
        });
        return out;
    }

    function atualizarUiOsteonModo(prefix) {
        const idset = prefix === 'cad' ? cadIds() : fichaIds();
        const modo = (idset.osteonModo && idset.osteonModo.value) || '';
        const per = modo === 'pericia';
        const pod = modo === 'poder_geral';
        if (idset.osteonPer) idset.osteonPer.style.display = per ? '' : 'none';
        if (idset.osteonPodWrap) idset.osteonPodWrap.style.display = pod ? '' : 'none';
        if (!pod && idset.osteonPodNome) idset.osteonPodNome.value = '';
    }

    function lerSereiaMagias(idset) {
        return lerMagiasDuplas(idset.sereiaMag1, idset.sereiaMag2);
    }

    function lerSilfideMagias(idset) {
        return lerMagiasDuplas(idset.silfideMag1, idset.silfideMag2);
    }

    function aplicarPericiasTreinadas(nomes) {
        if (!Array.isArray(nomes) || !nomes.length) return;
        const alvo = new Set(nomes.map((n) => String(n).trim()).filter(Boolean));
        document.querySelectorAll('#tblPericias tbody tr').forEach((tr) => {
            const span = tr.querySelector('.t20-p-nome');
            const nome = span ? span.textContent.trim() : '';
            if (!alvo.has(nome)) return;
            const cb = tr.querySelector('.p-treinado');
            if (cb) cb.checked = true;
        });
        if (typeof global.t20ValidarPericiasOrcamentoMb === 'function') {
            global.t20ValidarPericiasOrcamentoMb();
        }
    }

    function slugifyPoder(texto) {
        return String(texto || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '_')
            .replace(/^_|_$/g, '');
    }

    async function carregarEscolhas(slug) {
        const s = String(slug || '').trim().toLowerCase();
        if (!s || CACHE[s]) return CACHE[s];
        try {
            const data = await new TormentaRegrasService().obterEscolhasRaciais(s, {
                regraVersao: 'v13',
            });
            CACHE[s] = data;
            return data;
        } catch (_e) {
            return null;
        }
    }

    function normalizarCatalogoPericias(rows) {
        return (Array.isArray(rows) ? rows : [])
            .map((r) => {
                const nome = String((r && r.nome) || '').trim();
                if (!nome) return null;
                const slug = String((r && r.slug) || '').trim().toLowerCase();
                return r && typeof r === 'object' ? { ...r, nome, slug } : { nome, slug };
            })
            .filter(Boolean)
            .sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
    }

    function aplicarCatalogoPericias(rows) {
        const catalogo = normalizarCatalogoPericias(rows);
        if (!catalogo.length) return null;
        periciasCatalogo = catalogo;
        if (!Array.isArray(global.PERICIAS_META) || !global.PERICIAS_META.length) {
            global.PERICIAS_META = catalogo;
        }
        return catalogo;
    }

    async function carregarCatalogoPericias() {
        if (periciasCatalogo && periciasCatalogo.length) return periciasCatalogo;
        const meta = global.PERICIAS_META;
        if (Array.isArray(meta) && meta.length) {
            const cached = aplicarCatalogoPericias(meta);
            if (cached) return cached;
        }
        if (periciasCatalogoPromise) return periciasCatalogoPromise;
        periciasCatalogoPromise = (async () => {
            try {
                const data = await new TormentaRegrasService().obterAtributos({
                    regraVersao: isV13() ? 'v13' : 'mb',
                });
                const cached = aplicarCatalogoPericias(data && data.pericias);
                if (cached) return cached;
            } catch (_e) {
                /* fallback abaixo */
            }
            periciasCatalogo = PERICIAS_FALLBACK_NOMES.map((nome) => ({ nome, slug: '' }));
            return periciasCatalogo;
        })();
        try {
            return await periciasCatalogoPromise;
        } finally {
            periciasCatalogoPromise = null;
        }
    }

    function nomesPericiasDisponiveis() {
        const meta = periciasCatalogo || global.PERICIAS_META;
        if (Array.isArray(meta) && meta.length) {
            return meta.map((r) => r.nome).filter(Boolean);
        }
        return PERICIAS_FALLBACK_NOMES.slice();
    }

    function popularSelectPericias(sel, cur) {
        if (!sel) return;
        const prev = cur || sel.value;
        sel.innerHTML = '<option value="">—</option>';
        nomesPericiasDisponiveis().forEach((nome) => {
            const o = document.createElement('option');
            o.value = nome;
            o.textContent = nome;
            sel.appendChild(o);
        });
        if (prev) sel.value = prev;
    }

    function popularAscendencias(sel, data) {
        if (!sel || !data || !data.raca) return;
        const cur = sel.value;
        sel.innerHTML = '<option value="">— Escolha —</option>';
        (data.raca.ascendencias || []).forEach((row) => {
            const o = document.createElement('option');
            o.value = row.slug;
            o.textContent = `${row.rotulo} (RD ${row.rd_valor} ${row.rd_tipo})`;
            sel.appendChild(o);
        });
        if (cur) sel.value = cur;
    }

    function atualizarUiLefouModo(el, prefix) {
        const idset = prefix === 'cad' ? cadIds() : fichaIds();
        const modo = (idset.lefouModo && idset.lefouModo.value) || 'duas_pericias';
        const duas = modo === 'duas_pericias';
        if (idset.lefouPer2) idset.lefouPer2.style.display = duas ? '' : 'none';
        if (idset.lefouPodWrap) idset.lefouPodWrap.style.display = duas ? 'none' : '';
        if (duas && idset.lefouPodNome) idset.lefouPodNome.value = '';
    }

    async function atualizarUi(prefix) {
        if (!isV13()) {
            [fichaIds(), cadIds()].forEach((idset) => {
                Object.keys(idset).forEach((k) => {
                    if (k.startsWith('wrap') && idset[k]) idset[k].style.display = 'none';
                });
            });
            return;
        }
        const idset = prefix === 'cad' ? cadIds() : fichaIds();
        const slug = (idset.racaSelect && idset.racaSelect.value) || '';
        const showLefou = slug === 'lefou';
        const showQareen = slug === 'qareen';
        const showDahllan = slug === 'dahllan';
        const showOsteon = slug === 'osteon';
        const showSereia = slug === 'sereia_tritao';
        const showGolem = slug === 'golem';
        const showKliren = slug === 'kliren';
        const showSilfide = slug === 'silfide';
        if (idset.wrapLefou) idset.wrapLefou.style.display = showLefou ? '' : 'none';
        if (idset.wrapQareen) idset.wrapQareen.style.display = showQareen ? '' : 'none';
        if (idset.wrapDahllan) idset.wrapDahllan.style.display = showDahllan ? '' : 'none';
        if (idset.wrapOsteon) idset.wrapOsteon.style.display = showOsteon ? '' : 'none';
        if (idset.wrapSereia) idset.wrapSereia.style.display = showSereia ? '' : 'none';
        if (idset.wrapGolem) idset.wrapGolem.style.display = showGolem ? '' : 'none';
        if (idset.wrapKliren) idset.wrapKliren.style.display = showKliren ? '' : 'none';
        if (idset.wrapSilfide) idset.wrapSilfide.style.display = showSilfide ? '' : 'none';
        if (
            !showLefou &&
            !showQareen &&
            !showDahllan &&
            !showOsteon &&
            !showSereia &&
            !showGolem &&
            !showKliren &&
            !showSilfide
        ) {
            return;
        }

        if (showLefou || showOsteon || showKliren) {
            await carregarCatalogoPericias();
        }
        if (showLefou) {
            popularSelectPericias(idset.lefouPer1);
            popularSelectPericias(idset.lefouPer2);
            atualizarUiLefouModo(null, prefix);
        }
        if (showQareen) {
            const data = await carregarEscolhas('qareen');
            popularAscendencias(idset.qareenAsc, data);
        }
        if (showDahllan) {
            const data = await carregarEscolhas('dahllan');
            const magias = (data && data.raca && data.raca.magias_inatas) || [];
            if (idset.dahllanHint) {
                idset.dahllanHint.textContent = magias.length
                    ? magias.map((m) => `${m.nome} (${String(m.atributo_chave || 'sab').toUpperCase()})`).join(' · ')
                    : 'Controlar Plantas (SAB)';
            }
        }
        if (showOsteon) {
            popularSelectPericias(idset.osteonPer);
            atualizarUiOsteonModo(prefix);
        }
        if (showSereia) {
            const data = await carregarEscolhas('sereia_tritao');
            popularMagiasSereia(idset.sereiaMag1, idset.sereiaMag2, data);
        }
        if (showGolem) {
            const data = await carregarEscolhas('golem');
            popularFontesGolem(idset.golemFonte, data);
        }
        if (showKliren) {
            popularSelectPericias(idset.klirenPer);
        }
        if (showSilfide) {
            const data = await carregarEscolhas('silfide');
            popularMagiasEscolha(idset.silfideMag1, idset.silfideMag2, data);
        }
    }

    function lerPericiasLefou(idset) {
        const modo = (idset.lefouModo && idset.lefouModo.value) || 'duas_pericias';
        const out = [];
        const p1 = idset.lefouPer1 && idset.lefouPer1.value ? idset.lefouPer1.value.trim() : '';
        if (p1) out.push(p1);
        if (modo === 'duas_pericias') {
            const p2 = idset.lefouPer2 && idset.lefouPer2.value ? idset.lefouPer2.value.trim() : '';
            if (p2) out.push(p2);
        }
        return out;
    }

    function lerPayloadFicha() {
        if (!isV13()) return {};
        const idset = fichaIds();
        const slug = (idset.racaSelect && idset.racaSelect.value) || '';
        const out = {};
        if (slug === 'lefou') {
            out.lefou_deformidade_modo = (idset.lefouModo && idset.lefouModo.value) || 'duas_pericias';
            out.lefou_deformidade_pericias = lerPericiasLefou(idset);
            const modo = out.lefou_deformidade_modo;
            out.lefou_deformidade_poder_slug =
                modo === 'pericia_poder_tormenta'
                    ? global.__t20LefouPoderSlug ||
                      (idset.lefouPodNome && idset.lefouPodNome.value.trim()
                          ? slugifyPoder(idset.lefouPodNome.value)
                          : null)
                    : null;
        }
        if (slug === 'qareen') {
            out.qareen_ascendencia =
                idset.qareenAsc && idset.qareenAsc.value
                    ? String(idset.qareenAsc.value).trim().toLowerCase()
                    : null;
            out.qareen_magia_slug =
                idset.qareenMagia && idset.qareenMagia.value.trim()
                    ? slugifyPoder(idset.qareenMagia.value)
                    : null;
        }
        if (slug === 'dahllan') {
            out.dahllan_magias_inatas = ['controlar_plantas'];
        }
        if (slug === 'osteon') {
            out.osteon_memoria_modo =
                idset.osteonModo && idset.osteonModo.value
                    ? String(idset.osteonModo.value).trim().toLowerCase()
                    : null;
            out.osteon_memoria_pericia =
                out.osteon_memoria_modo === 'pericia' && idset.osteonPer && idset.osteonPer.value
                    ? idset.osteonPer.value.trim()
                    : null;
            out.osteon_memoria_poder_slug =
                out.osteon_memoria_modo === 'poder_geral'
                    ? global.__t20OsteonPoderSlug ||
                      (idset.osteonPodNome && idset.osteonPodNome.value.trim()
                          ? slugifyPoder(idset.osteonPodNome.value)
                          : null)
                    : null;
        }
        if (slug === 'sereia_tritao') {
            out.sereia_magias = lerSereiaMagias(idset);
        }
        if (slug === 'golem') {
            out.golem_fonte_elemental =
                idset.golemFonte && idset.golemFonte.value
                    ? String(idset.golemFonte.value).trim().toLowerCase()
                    : null;
            out.golem_poder_geral_slug =
                global.__t20GolemPoderSlug ||
                (idset.golemPodNome && idset.golemPodNome.value.trim()
                    ? slugifyPoder(idset.golemPodNome.value)
                    : null);
        }
        if (slug === 'kliren') {
            out.kliren_pericia =
                idset.klirenPer && idset.klirenPer.value ? idset.klirenPer.value.trim() : null;
            out.kliren_oficio =
                idset.klirenOficio && idset.klirenOficio.value
                    ? idset.klirenOficio.value.trim()
                    : null;
        }
        if (slug === 'silfide') {
            out.silfide_magias = lerSilfideMagias(idset);
        }
        return out;
    }

    function lerPayloadCadastro() {
        if (!isV13()) return {};
        const idset = cadIds();
        const slug = (idset.racaSelect && idset.racaSelect.value) || '';
        const out = {};
        if (slug === 'lefou') {
            out.lefou_deformidade_modo = (idset.lefouModo && idset.lefouModo.value) || 'duas_pericias';
            out.lefou_deformidade_pericias = lerPericiasLefou(idset);
            const modo = out.lefou_deformidade_modo;
            out.lefou_deformidade_poder_slug =
                modo === 'pericia_poder_tormenta' && idset.lefouPodNome && idset.lefouPodNome.value.trim()
                    ? slugifyPoder(idset.lefouPodNome.value)
                    : null;
        }
        if (slug === 'qareen') {
            out.qareen_ascendencia =
                idset.qareenAsc && idset.qareenAsc.value
                    ? String(idset.qareenAsc.value).trim().toLowerCase()
                    : null;
            out.qareen_magia_slug =
                idset.qareenMagia && idset.qareenMagia.value.trim()
                    ? slugifyPoder(idset.qareenMagia.value)
                    : null;
        }
        if (slug === 'dahllan') {
            out.dahllan_magias_inatas = ['controlar_plantas'];
        }
        if (slug === 'osteon') {
            out.osteon_memoria_modo =
                idset.osteonModo && idset.osteonModo.value
                    ? String(idset.osteonModo.value).trim().toLowerCase()
                    : null;
            out.osteon_memoria_pericia =
                out.osteon_memoria_modo === 'pericia' && idset.osteonPer && idset.osteonPer.value
                    ? idset.osteonPer.value.trim()
                    : null;
            out.osteon_memoria_poder_slug =
                out.osteon_memoria_modo === 'poder_geral' && idset.osteonPodNome && idset.osteonPodNome.value.trim()
                    ? slugifyPoder(idset.osteonPodNome.value)
                    : null;
        }
        if (slug === 'sereia_tritao') {
            out.sereia_magias = lerSereiaMagias(idset);
        }
        if (slug === 'golem') {
            out.golem_fonte_elemental =
                idset.golemFonte && idset.golemFonte.value
                    ? String(idset.golemFonte.value).trim().toLowerCase()
                    : null;
            out.golem_poder_geral_slug =
                idset.golemPodNome && idset.golemPodNome.value.trim()
                    ? slugifyPoder(idset.golemPodNome.value)
                    : null;
        }
        if (slug === 'kliren') {
            out.kliren_pericia =
                idset.klirenPer && idset.klirenPer.value ? idset.klirenPer.value.trim() : null;
            out.kliren_oficio =
                idset.klirenOficio && idset.klirenOficio.value
                    ? idset.klirenOficio.value.trim()
                    : null;
        }
        if (slug === 'silfide') {
            out.silfide_magias = lerSilfideMagias(idset);
        }
        return out;
    }

    function aplicarDoJsonFicha(j) {
        if (!j || typeof j !== 'object') return;
        const idset = fichaIds();
        if (idset.lefouModo) {
            idset.lefouModo.value = j.lefou_deformidade_modo || 'duas_pericias';
        }
        const per = Array.isArray(j.lefou_deformidade_pericias) ? j.lefou_deformidade_pericias : [];
        if (idset.lefouPer1 && per[0]) idset.lefouPer1.value = per[0];
        if (idset.lefouPer2 && per[1]) idset.lefouPer2.value = per[1];
        global.__t20LefouPoderSlug = j.lefou_deformidade_poder_slug
            ? String(j.lefou_deformidade_poder_slug).trim()
            : null;
        if (idset.lefouPodNome) {
            if (global.__t20LefouPoderSlug) {
                idset.lefouPodNome.value = global.__t20LefouPoderSlug
                    .replace(/_/g, ' ')
                    .replace(/\b\w/g, (c) => c.toUpperCase());
            } else {
                idset.lefouPodNome.value = '';
            }
        }
        if (idset.qareenAsc) idset.qareenAsc.value = j.qareen_ascendencia || '';
        if (idset.qareenMagia) {
            idset.qareenMagia.value = j.qareen_magia_slug
                ? String(j.qareen_magia_slug).replace(/_/g, ' ')
                : '';
        }
        if (idset.osteonModo) idset.osteonModo.value = j.osteon_memoria_modo || '';
        if (idset.osteonPer && j.osteon_memoria_pericia) {
            idset.osteonPer.value = j.osteon_memoria_pericia;
        }
        global.__t20OsteonPoderSlug = j.osteon_memoria_poder_slug
            ? String(j.osteon_memoria_poder_slug).trim()
            : null;
        if (idset.osteonPodNome) {
            idset.osteonPodNome.value = global.__t20OsteonPoderSlug
                ? global.__t20OsteonPoderSlug.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
                : '';
        }
        const sereia = Array.isArray(j.sereia_magias) ? j.sereia_magias : [];
        if (idset.sereiaMag1 && sereia[0]) idset.sereiaMag1.value = sereia[0];
        if (idset.sereiaMag2 && sereia[1]) idset.sereiaMag2.value = sereia[1];
        if (idset.golemFonte) idset.golemFonte.value = j.golem_fonte_elemental || '';
        global.__t20GolemPoderSlug = j.golem_poder_geral_slug
            ? String(j.golem_poder_geral_slug).trim()
            : null;
        if (idset.golemPodNome) {
            idset.golemPodNome.value = global.__t20GolemPoderSlug
                ? global.__t20GolemPoderSlug.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
                : '';
        }
        if (idset.klirenPer && j.kliren_pericia) idset.klirenPer.value = j.kliren_pericia;
        if (idset.klirenOficio && j.kliren_oficio) idset.klirenOficio.value = j.kliren_oficio;
        const silfide = Array.isArray(j.silfide_magias) ? j.silfide_magias : [];
        if (idset.silfideMag1 && silfide[0]) idset.silfideMag1.value = silfide[0];
        if (idset.silfideMag2 && silfide[1]) idset.silfideMag2.value = silfide[1];
        void atualizarUi('ficha');
        atualizarUiLefouModo(null, 'ficha');
        atualizarUiOsteonModo('ficha');
        if (j.osteon_memoria_modo === 'pericia' && j.osteon_memoria_pericia) {
            aplicarPericiasTreinadas([j.osteon_memoria_pericia]);
        }
        const treinadas = [];
        if (j.kliren_pericia) treinadas.push(j.kliren_pericia);
        if (treinadas.length) aplicarPericiasTreinadas(treinadas);
        if (j.kliren_oficio && window.T20OficioEspecialidades && typeof window.T20OficioEspecialidades.aplicarLista === 'function') {
            const esp = Array.isArray(j.oficio_especialidades) ? j.oficio_especialidades.slice() : [];
            if (!esp.includes(j.kliren_oficio)) esp.unshift(j.kliren_oficio);
            window.T20OficioEspecialidades.aplicarLista(esp);
        }
    }

    function optsPreviewTracos(slug) {
        if (!isV13()) return {};
        const s = String(slug || '').trim().toLowerCase();
        const payload = lerPayloadFicha();
        const opts = {};
        if (s === 'lefou') {
            opts.lefouDeformidadeModo = payload.lefou_deformidade_modo;
            if (payload.lefou_deformidade_pericias && payload.lefou_deformidade_pericias.length) {
                opts.lefouDeformidadePericias = payload.lefou_deformidade_pericias.join(',');
            }
        }
        if (s === 'qareen' && payload.qareen_ascendencia) {
            opts.qareenAscendencia = payload.qareen_ascendencia;
        }
        if (s === 'osteon') {
            if (payload.osteon_memoria_modo) opts.osteonMemoriaModo = payload.osteon_memoria_modo;
            if (payload.osteon_memoria_pericia) opts.osteonMemoriaPericia = payload.osteon_memoria_pericia;
        }
        if (s === 'sereia_tritao' && payload.sereia_magias && payload.sereia_magias.length) {
            opts.sereiaMagias = payload.sereia_magias.join(',');
        }
        if (s === 'golem') {
            if (payload.golem_fonte_elemental) opts.golemFonteElemental = payload.golem_fonte_elemental;
        }
        if (s === 'kliren') {
            if (payload.kliren_pericia) opts.klirenPericia = payload.kliren_pericia;
            if (payload.kliren_oficio) opts.klirenOficio = payload.kliren_oficio;
        }
        if (s === 'silfide' && payload.silfide_magias && payload.silfide_magias.length) {
            opts.silfideMagias = payload.silfide_magias.join(',');
        }
        return opts;
    }

    function validarCadastro() {
        if (!isV13()) return { ok: true };
        const idset = cadIds();
        const slug = (idset.racaSelect && idset.racaSelect.value) || '';
        if (slug === 'lefou') {
            const per = lerPericiasLefou(idset);
            const modo = (idset.lefouModo && idset.lefouModo.value) || 'duas_pericias';
            const need = modo === 'duas_pericias' ? 2 : 1;
            if (per.length < need) {
                return { ok: false, msg: `Lefou: escolha ${need} perícia(s) para deformidade.` };
            }
            if (modo === 'pericia_poder_tormenta') {
                const pod = idset.lefouPodNome && idset.lefouPodNome.value.trim();
                if (!pod) {
                    return { ok: false, msg: 'Lefou: informe o poder da Tormenta.' };
                }
            }
        }
        if (slug === 'qareen') {
            if (!idset.qareenAsc || !idset.qareenAsc.value) {
                return { ok: false, msg: 'Qareen: escolha a ascendência elementar.' };
            }
            if (!idset.qareenMagia || !idset.qareenMagia.value.trim()) {
                return { ok: false, msg: 'Qareen: informe a magia de 1º círculo (Tatuagem Mística).' };
            }
        }
        if (slug === 'osteon') {
            const modo = (idset.osteonModo && idset.osteonModo.value) || '';
            if (!modo) return { ok: false, msg: 'Osteon: escolha Memória Póstuma (perícia ou poder geral).' };
            if (modo === 'pericia' && !(idset.osteonPer && idset.osteonPer.value)) {
                return { ok: false, msg: 'Osteon: informe a perícia da Memória Póstuma.' };
            }
            if (modo === 'poder_geral' && !(idset.osteonPodNome && idset.osteonPodNome.value.trim())) {
                return { ok: false, msg: 'Osteon: informe o poder geral da Memória Póstuma.' };
            }
        }
        if (slug === 'sereia_tritao') {
            const mag = lerSereiaMagias(idset);
            if (mag.length < 2) {
                return { ok: false, msg: 'Sereia/Tritão: escolha 2 magias (Canção dos Mares).' };
            }
        }
        if (slug === 'golem') {
            if (!(idset.golemFonte && idset.golemFonte.value)) {
                return { ok: false, msg: 'Golem: escolha a Fonte Elemental.' };
            }
            const pod =
                (idset.golemPodNome && idset.golemPodNome.value.trim()) ||
                (global.__t20GolemPoderSlug ? 'x' : '');
            if (!pod) {
                return { ok: false, msg: 'Golem: informe o poder geral (Propósito de Criação).' };
            }
        }
        if (slug === 'kliren') {
            if (!(idset.klirenPer && idset.klirenPer.value)) {
                return { ok: false, msg: 'Kliren: informe a perícia do Híbrido.' };
            }
            if (!(idset.klirenOficio && idset.klirenOficio.value.trim())) {
                return { ok: false, msg: 'Kliren: informe a especialidade de Ofício (Vanguardista).' };
            }
        }
        if (slug === 'silfide') {
            const mag = lerSilfideMagias(idset);
            if (mag.length < 2) {
                return { ok: false, msg: 'Sílfide: escolha 2 magias (Magia das Fadas).' };
            }
        }
        return { ok: true };
    }

    function resumoCadastro() {
        const idset = cadIds();
        const slug = (idset.racaSelect && idset.racaSelect.value) || '';
        const parts = [];
        if (slug === 'lefou') {
            const per = lerPericiasLefou(idset);
            if (per.length) parts.push(`Lefou: ${per.join(', ')}`);
        }
        if (slug === 'qareen') {
            const op = idset.qareenAsc && idset.qareenAsc.selectedOptions[0];
            if (op) parts.push(`Qareen: ${op.textContent}`);
        }
        if (slug === 'dahllan') parts.push('Dahllan: Controlar Plantas');
        if (slug === 'osteon') {
            const modo = idset.osteonModo && idset.osteonModo.value;
            if (modo === 'pericia' && idset.osteonPer && idset.osteonPer.value) {
                parts.push(`Osteon: ${idset.osteonPer.value}`);
            } else if (modo === 'poder_geral') parts.push('Osteon: poder geral');
        }
        if (slug === 'sereia_tritao') {
            const mag = lerSereiaMagias(idset);
            if (mag.length) parts.push(`Sereia: ${mag.join(', ')}`);
        }
        if (slug === 'golem') {
            const op = idset.golemFonte && idset.golemFonte.selectedOptions[0];
            if (op) parts.push(`Golem: ${op.textContent}`);
        }
        if (slug === 'kliren') {
            if (idset.klirenPer && idset.klirenPer.value) {
                parts.push(`Kliren: ${idset.klirenPer.value}`);
            }
            if (idset.klirenOficio && idset.klirenOficio.value.trim()) {
                parts.push(`Ofício ${idset.klirenOficio.value.trim()}`);
            }
        }
        if (slug === 'silfide') {
            const mag = lerSilfideMagias(idset);
            if (mag.length) parts.push(`Sílfide: ${mag.join(', ')}`);
        }
        return parts.join(' · ');
    }

    function bindOnce() {
        if (bound) return;
        bound = true;
        ['f', 'cad'].forEach((prefix) => {
            const idset = prefix === 'cad' ? cadIds() : fichaIds();
            if (idset.lefouModo) {
                idset.lefouModo.addEventListener('change', () => {
                    atualizarUiLefouModo(null, prefix === 'cad' ? 'cad' : 'ficha');
                    refreshTracos(prefix);
                });
            }
            if (idset.osteonModo) {
                idset.osteonModo.addEventListener('change', () => {
                    atualizarUiOsteonModo(prefix === 'cad' ? 'cad' : 'ficha');
                    refreshTracos(prefix);
                });
            }
            [idset.lefouPer1, idset.lefouPer2, idset.qareenAsc, idset.osteonPer, idset.sereiaMag1, idset.sereiaMag2, idset.golemFonte, idset.klirenPer, idset.silfideMag1, idset.silfideMag2].forEach(
                (el) => {
                    if (el) el.addEventListener('change', () => refreshTracos(prefix));
                }
            );
            if (idset.klirenOficio) {
                idset.klirenOficio.addEventListener('input', () => refreshTracos(prefix));
            }
            if (idset.qareenMagia) {
                idset.qareenMagia.addEventListener('input', () => refreshTracos(prefix));
            }
        });
        const btnLefou = q('btnLefouPoderTormenta');
        if (btnLefou) {
            btnLefou.addEventListener('click', () => {
                const inp = q('f_lefou_poder_tormenta_nome');
                if (inp && typeof global.abrirModalTalentosTormenta === 'function') {
                    global.abrirModalTalentosTormenta(inp, 'tormenta');
                }
            });
        }
        const btnOsteon = q('btnOsteonPoderGeral');
        if (btnOsteon) {
            btnOsteon.addEventListener('click', () => {
                const inp = q('f_osteon_memoria_poder_nome');
                if (inp && typeof global.abrirModalTalentosTormenta === 'function') {
                    global.abrirModalTalentosTormenta(inp, null);
                }
            });
        }
        const btnGolem = q('btnGolemPoderGeral');
        if (btnGolem) {
            btnGolem.addEventListener('click', () => {
                const inp = q('f_golem_poder_geral_nome');
                if (inp && typeof global.abrirModalTalentosTormenta === 'function') {
                    global.abrirModalTalentosTormenta(inp, null);
                }
            });
        }
    }

    function refreshTracos(prefix) {
        const sel = prefix === 'cad' ? q('cadRacaSelect') : q('f_raca_select');
        const slug = (sel && sel.value) || '';
        if (typeof global.__t20AplicarTracosRaciaisMecanicos === 'function') {
            global.__t20AplicarTracosRaciaisMecanicos(slug);
        }
    }

    function onRacaChange(prefix) {
        void atualizarUi(prefix === 'cad' ? 'cad' : 'ficha');
        refreshTracos(prefix === 'cad' ? 'cad' : 'ficha');
    }

    function resetCadastro() {
        const idset = cadIds();
        if (idset.lefouModo) idset.lefouModo.value = 'duas_pericias';
        [
            idset.lefouPer1,
            idset.lefouPer2,
            idset.lefouPodNome,
            idset.qareenAsc,
            idset.qareenMagia,
            idset.osteonModo,
            idset.osteonPer,
            idset.osteonPodNome,
            idset.sereiaMag1,
            idset.sereiaMag2,
            idset.golemFonte,
            idset.golemPodNome,
            idset.klirenPer,
            idset.klirenOficio,
            idset.silfideMag1,
            idset.silfideMag2,
        ].forEach((el) => {
            if (el) el.value = '';
        });
    }

    global.T20EscolhasRaciaisV13 = {
        bindOnce,
        carregarCatalogoPericias,
        atualizarUiFicha: () => atualizarUi('ficha'),
        atualizarUiCadastro: () => atualizarUi('cad'),
        onRacaChangeFicha: () => onRacaChange('ficha'),
        onRacaChangeCadastro: () => onRacaChange('cad'),
        aplicarDoJsonFicha,
        aplicarPericiasTreinadas,
        lerPayloadFicha,
        lerPayloadCadastro,
        optsPreviewTracos,
        validarCadastro,
        resumoCadastro,
        resetCadastro,
        slugifyPoder,
    };

    document.addEventListener('DOMContentLoaded', () => {
        bindOnce();
        if (isV13()) void carregarCatalogoPericias();
    });
})(typeof window !== 'undefined' ? window : globalThis);
