/**
 * Ficha GURPS — planilha oficial + extras locais (localStorage).
 */
(function () {
    const svc = new GurpsPersonagemService();
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');
    const el = (sel) => document.querySelector(sel);

    const localKey = () => `gurps_ficha_local_${id || 'novo'}`;

    /** Retrato pendente (ficha ainda sem id) ou pré-visualização após escolher arquivo. */
    let pendingPortrait = null;

    function resolvePortraitUrl(url) {
        if (!url) return '';
        const s = String(url);
        if (s.startsWith('http://') || s.startsWith('https://') || s.startsWith('data:')) return s;
        if (s.startsWith('/')) return s;
        return `/${s}`;
    }

    function revokePendingPortrait() {
        if (pendingPortrait?.previewUrl) {
            URL.revokeObjectURL(pendingPortrait.previewUrl);
        }
        pendingPortrait = null;
    }

    function applyPortraitDisplay(src) {
        const img = el('#fg_portrait_img');
        const ph = el('#fg_portrait_ph');
        if (!img) return;
        if (src) {
            img.src = src;
            img.hidden = false;
            if (ph) ph.hidden = true;
        } else {
            img.removeAttribute('src');
            img.hidden = true;
            if (ph) ph.hidden = false;
        }
    }

    function updatePortraitHint() {
        const hint = el('#fg_portrait_hint_noid');
        if (!hint) return;
        hint.hidden = !!id;
    }

    async function onPortraitFileSelected(file) {
        if (!file || !String(file.type || '').startsWith('image/')) {
            Toast.error('Escolha um arquivo de imagem');
            return;
        }
        revokePendingPortrait();
        const previewUrl = URL.createObjectURL(file);
        pendingPortrait = { file, previewUrl };
        applyPortraitDisplay(previewUrl);

        const hint = el('#fg_portrait_hint_noid');
        if (!id) {
            if (hint) hint.hidden = false;
            return;
        }
        if (hint) hint.hidden = true;
        try {
            const updated = await svc.enviarFoto(Number(id), file);
            URL.revokeObjectURL(previewUrl);
            pendingPortrait = null;
            applyPortraitDisplay(updated.foto_url ? resolvePortraitUrl(updated.foto_url) : '');
            Toast.success('Retrato atualizado');
        } catch (e) {
            Toast.error(e.message || 'Falha no envio do retrato');
        }
    }

    function num(id, d = 0) {
        const v = el(id);
        if (!v || v.value === '') return d;
        const n = Number(v.value);
        return Number.isFinite(n) ? n : d;
    }

    function str(id) {
        const v = el(id);
        return v ? String(v.value || '').trim() : '';
    }

    function dec(id, d = '5.00') {
        const v = str(id);
        return v || d;
    }

    function optInt(sel) {
        const raw = str(sel);
        if (!raw) return null;
        const n = Number(raw);
        return Number.isFinite(n) ? n : null;
    }

    /**
     * Tabela ST → (thr, sw) — espelho de `backend/app/games/gurps/core/dano_st.py` (`dano_thr_sw_por_st`).
     */
    const GURPS_ST_DANO_THR_SW = {
        1: ['1d-6', '1d-5'],
        2: ['1d-6', '1d-5'],
        3: ['1d-5', '1d-4'],
        4: ['1d-5', '1d-4'],
        5: ['1d-4', '1d-3'],
        6: ['1d-4', '1d-3'],
        7: ['1d-3', '1d-2'],
        8: ['1d-3', '1d-2'],
        9: ['1d-2', '1d-1'],
        10: ['1d-2', '1d'],
        11: ['1d-1', '1d+1'],
        12: ['1d-1', '1d+2'],
        13: ['1d', '2d-1'],
        14: ['1d', '2d'],
        15: ['1d+1', '2d+1'],
        16: ['1d+1', '2d+2'],
        17: ['1d+2', '3d-1'],
        18: ['1d+2', '3d'],
        19: ['2d-1', '3d+1'],
        20: ['2d-1', '3d+2'],
        21: ['2d', '4d-1'],
        22: ['2d', '4d'],
        23: ['2d+1', '4d+1'],
        24: ['2d+1', '4d+2'],
        25: ['2d+2', '5d-1'],
        26: ['2d+2', '5d'],
        27: ['3d-1', '5d+1'],
        28: ['3d-1', '5d+1'],
        29: ['3d', '5d+2'],
        30: ['3d', '6d-1'],
    };

    function danoThrSwPorSt(st) {
        let s = Math.trunc(Number(st));
        if (!Number.isFinite(s) || s < 1) s = 1;
        else if (s > 30) s = 30;
        return GURPS_ST_DANO_THR_SW[s];
    }

    function aplicarDanoThrSwPorSt() {
        const st = num('#fg_st_valor', 10);
        const pair = danoThrSwPorSt(st);
        if (!pair) return;
        const [thr, sw] = pair;
        const imp = el('#fg_dano_imp');
        const bal = el('#fg_dano_bal');
        if (imp) imp.value = thr;
        if (bal) bal.value = sw;
    }

    /** Lite: PV máx = ST; PV atual = min(atual, novo máx) se preenchido (como `personagem_service.atualizar`). */
    function aplicarPvMaxPorSt() {
        if (num('#fg_hp_custo', 0) > 0) return;
        const st = Math.trunc(num('#fg_st_valor', 10));
        if (!Number.isFinite(st)) return;
        const hpVal = el('#fg_hp_valor');
        if (hpVal) hpVal.value = String(st);
        const hpAt = el('#fg_hp_atual');
        if (hpAt && hpAt.value !== '') {
            const cur = Number(hpAt.value);
            if (Number.isFinite(cur)) hpAt.value = String(Math.min(cur, st));
        }
    }

    /** Lite: FAD máx = HT; FAD atual = min(atual, novo máx) se preenchido. */
    function aplicarFadMaxPorHt() {
        if (num('#fg_fp_custo', 0) > 0) return;
        const ht = Math.trunc(num('#fg_ht_valor', 10));
        if (!Number.isFinite(ht)) return;
        const fpVal = el('#fg_fp_valor');
        if (fpVal) fpVal.value = String(ht);
        const fpAt = el('#fg_fp_atual');
        if (fpAt && fpAt.value !== '') {
            const cur = Number(fpAt.value);
            if (Number.isFinite(cur)) fpAt.value = String(Math.min(cur, ht));
        }
    }

    /** Lite: Vontade = IQ; Percepção = IQ (só se custo XP da linha = 0). */
    function aplicarVonPerPorIq() {
        const iq = Math.trunc(num('#fg_iq_valor', 10));
        if (!Number.isFinite(iq)) return;
        if (num('#fg_will_custo', 0) === 0) {
            const w = el('#fg_will_valor');
            if (w) w.value = String(iq);
        }
        if (num('#fg_per_custo', 0) === 0) {
            const p = el('#fg_per_valor');
            if (p) p.value = String(iq);
        }
    }

    function onStValorInput() {
        aplicarDanoThrSwPorSt();
        aplicarPvMaxPorSt();
    }

    function onHtValorInput() {
        aplicarVelocidadeBasicaDerivada();
        aplicarFadMaxPorHt();
    }

    /**
     * GURPS Lite (igual ao backend):
     * VB = (HT + DX) / 4; deslocamento = floor(VB); esquiva = floor(VB) + 3.
     * Não sobrescreve se `velocidade_custo` > 0 (VB comprado com pontos).
     */
    function aplicarVelocidadeBasicaDerivada() {
        if (num('#fg_vel_custo', 0) > 0) return;
        const ht = num('#fg_ht_valor', 10);
        const dx = num('#fg_dx_valor', 10);
        const vb = (ht + dx) / 4;
        if (!Number.isFinite(vb)) return;
        const velInp = el('#fg_vel_valor');
        if (velInp) velInp.value = vb.toFixed(2);
        const mov = Math.floor(vb + 1e-9);
        const movInp = el('#fg_mov_valor');
        if (movInp) movInp.value = String(mov);
        const esqInp = el('#fg_esquiva');
        if (esqInp) esqInp.value = String(mov + 3);
    }

    /** Recalcula na ficha o que o backend deriva (Lite). */
    function aplicarDerivadosGurpsLiteFicha() {
        aplicarVelocidadeBasicaDerivada();
        aplicarDanoThrSwPorSt();
        aplicarPvMaxPorSt();
        aplicarFadMaxPorHt();
        aplicarVonPerPorIq();
    }

    function syncXpMirror() {
        const v = el('#fg_pt_total')?.value ?? '0';
        const m = el('#fg_xp_top_mirror');
        if (m) m.textContent = v;
    }

    function buildExtrasPayload() {
        const enc = {};
        document.querySelectorAll('.ficha-local-enc').forEach((inp) => {
            const k = inp.getAttribute('data-enc');
            if (!enc[k]) enc[k] = {};
            enc[k].fp = inp.value;
        });
        document.querySelectorAll('.ficha-local-enc-d').forEach((inp) => {
            const k = inp.getAttribute('data-enc');
            if (!enc[k]) enc[k] = {};
            enc[k].d = inp.value;
        });
        const hit = {};
        document.querySelectorAll('.ficha-local-hit').forEach((inp) => {
            const p = inp.getAttribute('data-part');
            if (p) hit[p] = inp.value;
        });
        return {
            criacao: str('#fg_criacao'),
            aparencia_long: el('#fg_aparencia_long')?.value || '',
            equipamento: el('#fg_equipamento')?.value || '',
            escudo: str('#fg_escudo'),
            enc,
            hit,
            arma: {
                golp: str('#fg_arma_golp'),
                bal: str('#fg_arma_bal'),
                nh: str('#fg_arma_nh'),
            },
        };
    }

    function salvarLocal() {
        try {
            localStorage.setItem(localKey(), JSON.stringify(buildExtrasPayload()));
        } catch (e) {
            console.warn('localStorage ficha', e);
        }
    }

    function applyExtrasPayload(o) {
        if (!o || typeof o !== 'object') return;
        if (o.criacao != null) setVal('#fg_criacao', o.criacao);
        if (o.aparencia_long != null && el('#fg_aparencia_long')) {
            el('#fg_aparencia_long').value = o.aparencia_long;
        }
        if (o.equipamento != null && el('#fg_equipamento')) {
            el('#fg_equipamento').value = o.equipamento;
        }
        if (o.escudo != null) setVal('#fg_escudo', o.escudo);
        if (o.arma) {
            setVal('#fg_arma_golp', o.arma.golp);
            setVal('#fg_arma_bal', o.arma.bal);
            setVal('#fg_arma_nh', o.arma.nh);
        }
        if (o.enc) {
            Object.keys(o.enc).forEach((k) => {
                const row = o.enc[k];
                const a = document.querySelector(`.ficha-local-enc[data-enc="${k}"]`);
                const b = document.querySelector(`.ficha-local-enc-d[data-enc="${k}"]`);
                if (a && row.fp != null) a.value = row.fp;
                if (b && row.d != null) b.value = row.d;
            });
        }
        if (o.hit) {
            const hit = { ...o.hit };
            const mig = [
                ['cabeca', 'cranio'],
                ['tronco', 'torso'],
                ['bracos', 'braco'],
                ['pernas', 'perna'],
                ['extrem', 'mao'],
            ];
            mig.forEach(([antigo, novo]) => {
                if (hit[antigo] != null && hit[antigo] !== '' && (hit[novo] == null || hit[novo] === '')) {
                    hit[novo] = hit[antigo];
                }
            });
            Object.keys(hit).forEach((p) => {
                const inp = document.querySelector(`.ficha-local-hit[data-part="${p}"]`);
                if (inp && hit[p] != null) inp.value = hit[p];
            });
        }
    }

    /** True se nada foi salvo ainda no servidor (migração localStorage → API). */
    function extrasServidorVazio(ex) {
        if (!ex || typeof ex !== 'object') return true;
        /* Já persistido no servidor (versão de formato); não sobrescrever com localStorage. */
        if (Object.prototype.hasOwnProperty.call(ex, 'v')) return false;
        const t = (v) => (v == null ? '' : String(v)).trim();
        if (t(ex.criacao)) return false;
        if (t(ex.aparencia_long)) return false;
        if (t(ex.equipamento)) return false;
        if (t(ex.escudo)) return false;
        if (ex.arma && (t(ex.arma.golp) || t(ex.arma.bal) || t(ex.arma.nh))) return false;
        if (ex.enc && typeof ex.enc === 'object') {
            const encTem = Object.keys(ex.enc).some((k) => {
                const row = ex.enc[k];
                return row && (t(row.fp) || t(row.d));
            });
            if (encTem) return false;
        }
        if (ex.hit && typeof ex.hit === 'object') {
            const hitTem = Object.keys(ex.hit).some((k) => t(ex.hit[k]));
            if (hitTem) return false;
        }
        return true;
    }

    function carregarLocal() {
        try {
            const raw = localStorage.getItem(localKey());
            if (!raw) return;
            applyExtrasPayload(JSON.parse(raw));
        } catch (e) {
            console.warn('carregarLocal', e);
        }
    }

    function setVal(sel, v) {
        const n = el(sel);
        if (n && v != null && v !== '') n.value = v;
    }

    function coletarLinhas(selector, mapFn) {
        return Array.from(document.querySelectorAll(selector)).map(mapFn).filter(Boolean);
    }

    function montarPayload() {
        const hpA = el('#fg_hp_atual');
        const fpA = el('#fg_fp_atual');
        return {
            tipo: str('#fg_tipo') || 'jogador',
            nome: str('#fg_nome'),
            conceito: str('#fg_conceito') || null,
            reacao: str('#fg_reacao') || null,
            idade: str('#fg_idade') || null,
            campanha_id: optInt('#fg_campanha_id'),
            iniciativa: num('#fg_iniciativa', 0),
            st_custo: num('#fg_st_custo'),
            st_valor: num('#fg_st_valor', 10),
            dx_custo: num('#fg_dx_custo'),
            dx_valor: num('#fg_dx_valor', 10),
            iq_custo: num('#fg_iq_custo'),
            iq_valor: num('#fg_iq_valor', 10),
            ht_custo: num('#fg_ht_custo'),
            ht_valor: num('#fg_ht_valor', 10),
            vontade_custo: num('#fg_will_custo'),
            vontade_valor: num('#fg_will_valor', 10),
            percepcao_custo: num('#fg_per_custo'),
            percepcao_valor: num('#fg_per_valor', 10),
            pvs_custo: num('#fg_hp_custo'),
            pvs_valor: num('#fg_hp_valor', 10),
            pvs_atual: hpA && hpA.value !== '' ? num('#fg_hp_atual', num('#fg_hp_valor', 10)) : null,
            fadiga_custo: num('#fg_fp_custo'),
            fadiga_valor: num('#fg_fp_valor', 10),
            fadiga_atual: fpA && fpA.value !== '' ? num('#fg_fp_atual', num('#fg_fp_valor', 10)) : null,
            velocidade_custo: num('#fg_vel_custo'),
            velocidade_valor: dec('#fg_vel_valor', '5.00'),
            deslocamento_custo: num('#fg_mov_custo'),
            deslocamento_valor: num('#fg_mov_valor', 5),
            esquiva: num('#fg_esquiva'),
            aparar: num('#fg_aparar'),
            bloqueio: str('#fg_bloqueio') || null,
            dano_impacto: str('#fg_dano_imp') || null,
            dano_balanco: str('#fg_dano_bal') || null,
            pontos_atributos: num('#fg_pt_attr'),
            pontos_vantagens: num('#fg_pt_vant'),
            pontos_desvantagens: num('#fg_pt_desv'),
            pontos_pericias: num('#fg_pt_per'),
            pontos_total: num('#fg_pt_total'),
            vantagens: coletasVantagens(),
            desvantagens: coletasDesvantagens(),
            pericias: coletasPericias(),
            extras: buildExtrasPayload(),
        };
    }

    function coletasVantagens() {
        return coletarLinhas('.fg-row-vant', (row) => {
            const nome = row.querySelector('.fg-vant-nome')?.value?.trim();
            if (!nome) return null;
            const custo = Number(row.querySelector('.fg-vant-custo')?.value || 0);
            return { nome, custo: Number.isFinite(custo) ? custo : 0 };
        });
    }

    function coletasDesvantagens() {
        return coletarLinhas('.fg-row-desv', (row) => {
            const nome = row.querySelector('.fg-desv-nome')?.value?.trim();
            if (!nome) return null;
            const custo = Number(row.querySelector('.fg-desv-custo')?.value || 0);
            return { nome, custo: Number.isFinite(custo) ? custo : 0 };
        });
    }

    function coletasPericias() {
        return coletarLinhas('.fg-row-per', (row) => {
            const nome = row.querySelector('.fg-per-nome')?.value?.trim();
            if (!nome) return null;
            const tipo = row.querySelector('.fg-per-tipo')?.value?.trim() || 'DX/M';
            const nh = Number(row.querySelector('.fg-per-nh')?.value || 0);
            const custo = Number(row.querySelector('.fg-per-custo')?.value || 0);
            return {
                nome,
                tipo,
                nh: Number.isFinite(nh) ? nh : 0,
                custo: Number.isFinite(custo) ? custo : 0,
            };
        });
    }

    function addRowVant() {
        const w = el('#fg_vant_wrap');
        if (!w) return;
        const d = document.createElement('div');
        d.className = 'ficha-linha fg-row-vant';
        d.innerHTML =
            '<input class="fg-vant-nome" type="text" placeholder="Vantagem" />' +
            '<input class="fg-vant-custo" type="number" value="0" />' +
            '<button type="button" class="ficha-btn ficha-btn--icon ficha-btn--ghost" aria-label="Remover">✕</button>';
        d.querySelector('button').addEventListener('click', () => d.remove());
        w.appendChild(d);
    }

    function addRowDesv() {
        const w = el('#fg_desv_wrap');
        if (!w) return;
        const d = document.createElement('div');
        d.className = 'ficha-linha fg-row-desv';
        d.innerHTML =
            '<input class="fg-desv-nome" type="text" placeholder="Desvantagem" />' +
            '<input class="fg-desv-custo" type="number" value="0" />' +
            '<button type="button" class="ficha-btn ficha-btn--icon ficha-btn--ghost" aria-label="Remover">✕</button>';
        d.querySelector('button').addEventListener('click', () => d.remove());
        w.appendChild(d);
    }

    function addRowPer() {
        const tb = el('#fg_per_wrap');
        if (!tb) return;
        const tr = document.createElement('tr');
        tr.className = 'fg-row-per';
        tr.innerHTML =
            '<td><input class="fg-per-nome" type="text" placeholder="Perícia" /></td>' +
            '<td><input class="fg-per-tipo" type="text" placeholder="DX/M" /></td>' +
            '<td><input class="fg-per-nh" type="number" value="10" /></td>' +
            '<td><input class="fg-per-custo" type="number" value="0" /></td>' +
            '<td><button type="button" class="ficha-btn ficha-btn--icon ficha-btn--ghost" aria-label="Remover">✕</button></td>';
        tr.querySelector('button').addEventListener('click', () => tr.remove());
        tb.appendChild(tr);
    }

    window.fgAddVant = addRowVant;
    window.fgAddDesv = addRowDesv;
    window.fgAddPer = addRowPer;

    function preencher(p) {
        const set = (sel, v) => {
            const n = el(sel);
            if (n && v != null) n.value = v;
        };
        set('#fg_tipo', p.tipo);
        set('#fg_nome', p.nome);
        set('#fg_conceito', p.conceito);
        set('#fg_reacao', p.reacao);
        set('#fg_idade', p.idade);
        set('#fg_campanha_id', p.campanha_id || '');
        set('#fg_iniciativa', p.iniciativa);
        set('#fg_st_custo', p.st_custo);
        set('#fg_st_valor', p.st_valor);
        set('#fg_dx_custo', p.dx_custo);
        set('#fg_dx_valor', p.dx_valor);
        set('#fg_iq_custo', p.iq_custo);
        set('#fg_iq_valor', p.iq_valor);
        set('#fg_ht_custo', p.ht_custo);
        set('#fg_ht_valor', p.ht_valor);
        set('#fg_will_custo', p.vontade_custo);
        set('#fg_will_valor', p.vontade_valor);
        set('#fg_per_custo', p.percepcao_custo);
        set('#fg_per_valor', p.percepcao_valor);
        set('#fg_hp_custo', p.pvs_custo);
        set('#fg_hp_valor', p.pvs_valor);
        set('#fg_hp_atual', p.pvs_atual);
        set('#fg_fp_custo', p.fadiga_custo);
        set('#fg_fp_valor', p.fadiga_valor);
        set('#fg_fp_atual', p.fadiga_atual);
        set('#fg_vel_custo', p.velocidade_custo);
        set('#fg_vel_valor', p.velocidade_valor);
        set('#fg_mov_custo', p.deslocamento_custo);
        set('#fg_mov_valor', p.deslocamento_valor);
        set('#fg_esquiva', p.esquiva);
        set('#fg_aparar', p.aparar);
        set('#fg_bloqueio', p.bloqueio || '');
        set('#fg_dano_imp', p.dano_impacto || '');
        set('#fg_dano_bal', p.dano_balanco || '');
        set('#fg_pt_attr', p.pontos_atributos);
        set('#fg_pt_vant', p.pontos_vantagens);
        set('#fg_pt_desv', p.pontos_desvantagens);
        set('#fg_pt_per', p.pontos_pericias);
        set('#fg_pt_total', p.pontos_total);
        syncXpMirror();

        revokePendingPortrait();
        applyPortraitDisplay(p.foto_url ? resolvePortraitUrl(p.foto_url) : '');

        el('#fg_vant_wrap').innerHTML = '';
        el('#fg_desv_wrap').innerHTML = '';
        el('#fg_per_wrap').innerHTML = '';
        (p.vantagens || []).forEach((v) => {
            addRowVant();
            const rows = document.querySelectorAll('.fg-row-vant');
            const r = rows[rows.length - 1];
            if (r && v) {
                r.querySelector('.fg-vant-nome').value = v.nome;
                r.querySelector('.fg-vant-custo').value = v.custo;
            }
        });
        (p.desvantagens || []).forEach((v) => {
            addRowDesv();
            const rows = document.querySelectorAll('.fg-row-desv');
            const r = rows[rows.length - 1];
            if (r && v) {
                r.querySelector('.fg-desv-nome').value = v.nome;
                r.querySelector('.fg-desv-custo').value = v.custo;
            }
        });
        (p.pericias || []).forEach((v) => {
            addRowPer();
            const rows = document.querySelectorAll('.fg-row-per');
            const r = rows[rows.length - 1];
            if (r && v) {
                r.querySelector('.fg-per-nome').value = v.nome;
                r.querySelector('.fg-per-tipo').value = v.tipo;
                r.querySelector('.fg-per-nh').value = v.nh;
                r.querySelector('.fg-per-custo').value = v.custo;
            }
        });
    }

    function preencherJogador() {
        const u = typeof AuthService !== 'undefined' ? AuthService.getUsuario() : null;
        const inp = el('#fg_jogador_leitura');
        if (inp) inp.value = u?.nome || u?.email || '—';
    }

    async function carregar() {
        updatePortraitHint();
        preencherJogador();
        if (!id) {
            addRowVant();
            addRowDesv();
            addRowPer();
            carregarLocal();
            aplicarDerivadosGurpsLiteFicha();
            syncXpMirror();
            return;
        }
        try {
            const p = await svc.obter(Number(id));
            preencher(p);
            el('#fg_titulo_sub').textContent = p.nome ? ` — ${p.nome}` : '';
            const ex = p.extras && typeof p.extras === 'object' ? p.extras : {};
            applyExtrasPayload(ex);
            if (extrasServidorVazio(ex)) {
                carregarLocal();
            } else {
                salvarLocal();
            }
        } catch (e) {
            Toast.error(e.message || 'Erro ao carregar');
        }
    }

    async function salvar() {
        const payload = montarPayload();
        if (!payload.nome) {
            Toast.error('Nome do personagem é obrigatório');
            return;
        }
        try {
            if (id) {
                await svc.atualizar(Number(id), payload);
                salvarLocal();
                Toast.success('Ficha atualizada');
            } else {
                const criado = await svc.criar(payload);
                salvarLocal();
                try {
                    const novo = localStorage.getItem(localKey());
                    if (novo) {
                        localStorage.setItem(`gurps_ficha_local_${criado.id}`, novo);
                        localStorage.removeItem('gurps_ficha_local_novo');
                    }
                } catch (e) { /* ignore */ }
                if (pendingPortrait?.file) {
                    try {
                        await svc.enviarFoto(criado.id, pendingPortrait.file);
                    } catch (e) {
                        Toast.error(e.message || 'Personagem criado; envie o retrato novamente pela ficha.');
                    }
                }
                if (pendingPortrait?.previewUrl) {
                    URL.revokeObjectURL(pendingPortrait.previewUrl);
                }
                pendingPortrait = null;
                Toast.success('Personagem criado');
                window.location.href = `ficha-personagem.html?id=${criado.id}`;
                return;
            }
        } catch (e) {
            Toast.error(e.message || 'Erro ao salvar');
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        AuthService.configurarHeaderUsuario();
        carregar();
        el('#btnSalvarFicha')?.addEventListener('click', salvar);
        el('#fg_pt_total')?.addEventListener('input', syncXpMirror);
        el('#fg_ht_valor')?.addEventListener('input', onHtValorInput);
        el('#fg_dx_valor')?.addEventListener('input', aplicarVelocidadeBasicaDerivada);
        el('#fg_st_valor')?.addEventListener('input', onStValorInput);
        el('#fg_iq_valor')?.addEventListener('input', aplicarVonPerPorIq);
        /* btnTrocarJogo / btnLogout: configurarHeaderUsuario() já associa quando há usuário */

        el('#fg_portrait_file')?.addEventListener('change', (ev) => {
            const f = ev.target?.files?.[0];
            ev.target.value = '';
            if (f) onPortraitFileSelected(f);
        });
        el('#fg_portrait_clear')?.addEventListener('click', async () => {
            revokePendingPortrait();
            if (id) {
                try {
                    await svc.atualizar(Number(id), { foto_url: null });
                    applyPortraitDisplay('');
                    Toast.success('Retrato removido');
                } catch (e) {
                    Toast.error(e.message || 'Erro ao remover retrato');
                }
            } else {
                applyPortraitDisplay('');
            }
            updatePortraitHint();
        });

        document.querySelectorAll('.ficha-local-enc, .ficha-local-enc-d, .ficha-local-hit, .ficha-local-arma, #fg_aparencia_long, #fg_equipamento, #fg_escudo, #fg_criacao').forEach((elem) => {
            elem.addEventListener('change', salvarLocal);
        });
    });
})();
