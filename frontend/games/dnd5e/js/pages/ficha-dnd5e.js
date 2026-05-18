/**
 * Ficha D&D 5e — criação/edição com raça, classe, perícias, antecedente e CA.
 */
(function () {
    const ABILITIES = [
        { key: 'strength', label: 'FOR', name: 'Força' },
        { key: 'dexterity', label: 'DES', name: 'Destreza' },
        { key: 'constitution', label: 'CON', name: 'Constituição' },
        { key: 'intelligence', label: 'INT', name: 'Inteligência' },
        { key: 'wisdom', label: 'SAB', name: 'Sabedoria' },
        { key: 'charisma', label: 'CAR', name: 'Carisma' },
    ];

    const MATRIZ_PADRAO = [15, 14, 13, 12, 10, 8];
    const PROF_POR_NIVEL = [
        [1, 4, 2],
        [5, 8, 3],
        [9, 12, 4],
        [13, 16, 5],
        [17, 20, 6],
    ];

    const ps = new Dnd5ePersonagemService();
    const rs = new Dnd5eRegrasService();
    const cs = new Dnd5eCombateService();
    const CU = Dnd5eCondicoesUtil;

    const params = new URLSearchParams(window.location.search);
    const personagemId = params.get('id') ? parseInt(params.get('id'), 10) : null;
    const tipoNovoParam = (params.get('tipo') || 'jogador').toLowerCase();
    const tiposValidos = ['jogador', 'monstro', 'npc'];
    let tipoCriacao = tiposValidos.includes(tipoNovoParam) ? tipoNovoParam : 'jogador';

    let catalogoRacas = [];
    let catalogoClasses = [];
    let catalogoAntecedentes = [];
    let catalogoPericias = [];
    let catalogoCondicoes = [];
    let armaduras = [];
    let escudos = [];
    let previewAtual = null;
    let debounceTimer = null;
    let debounceHpCondTimer = null;
    let arenaCondicoesAtual = [];
    const el = (id) => document.getElementById(id);

    function fmtMod(n) {
        const v = Number(n);
        if (!Number.isFinite(v)) return '—';
        return v >= 0 ? `+${v}` : String(v);
    }

    function nomeJogadorLogado() {
        if (typeof AuthService.getNome === 'function') return AuthService.getNome();
        return '';
    }

    function bonusProficiencia(nivel) {
        const n = Math.max(1, Math.min(20, Number(nivel) || 1));
        for (const [min, max, bonus] of PROF_POR_NIVEL) {
            if (n >= min && n <= max) return bonus;
        }
        return 2;
    }

    function periciaNome(slug) {
        const p = catalogoPericias.find((x) => x.slug === slug);
        return p ? p.nome : slug;
    }

    function renderAbilities() {
        const host = el('f5e_abilities_circles');
        if (!host) return;
        host.innerHTML = ABILITIES.map(
            (a) => `
            <div class="ficha-atributo-circulo" data-ability="${a.key}">
                <div class="circulo-externo">
                    <span class="circulo-valor" id="eff_${a.key}">10</span>
                    <span class="circulo-mod" id="mod_${a.key}">+0</span>
                </div>
                <span class="circulo-label">${a.label}</span>
                <input type="number" min="8" max="15" id="base_${a.key}" value="10"
                    aria-label="${a.name} base" title="Valor base" />
            </div>`
        ).join('');
        ABILITIES.forEach((a) => {
            el(`base_${a.key}`).addEventListener('input', agendarPreview);
        });
    }

    function getScoresBase() {
        const out = {};
        ABILITIES.forEach((a) => {
            out[a.key] = parseInt(el(`base_${a.key}`).value, 10) || 10;
        });
        return out;
    }

    function racaSelecionada() {
        return catalogoRacas.find((r) => r.slug === el('f5e_raca').value);
    }

    function getBonusExtra() {
        if (!Dnd5eRacaUtil.temBonusHabilidadeExtraEscolha(racaSelecionada())) return {};
        const k1 = el('f5e_extra1').value;
        const k2 = el('f5e_extra2').value;
        const out = {};
        if (k1) out[k1] = (out[k1] || 0) + 1;
        if (k2 && k2 !== k1) out[k2] = (out[k2] || 0) + 1;
        return out;
    }

    function getPericiasClasseEscolhidas() {
        return Array.from(
            document.querySelectorAll('#f5e_pericias_escolha input[type=checkbox]:checked')
        ).map((cb) => cb.value);
    }

    function payloadCalcular() {
        return {
            raca_slug: el('f5e_raca').value,
            classe_slug: el('f5e_classe').value,
            antecedente_slug: el('f5e_antecedente').value || null,
            scores_base: getScoresBase(),
            bonus_habilidade_extra: getBonusExtra(),
            nivel: parseInt(el('f5e_nivel').value, 10) || 1,
            pericias_classe_escolhidas: getPericiasClasseEscolhidas(),
            pericia_racial_extra: el('f5e_pericia_racial').value || null,
            subclasse_slug: el('f5e_subclasse').value || null,
            armadura_slug: el('f5e_armadura').value || null,
            escudo_slug: el('f5e_escudo').value || null,
        };
    }

    function atualizarUiRaca() {
        const raca = racaSelecionada();
        const tracos = el('f5e_tracos');
        const extra = el('f5e_raca_extra');
        if (raca && raca.tracos_resumo) {
            tracos.textContent = raca.tracos_resumo;
            tracos.hidden = false;
        } else {
            tracos.hidden = true;
        }
        extra.classList.toggle(
            'is-visible',
            Dnd5eRacaUtil.temBonusHabilidadeExtraEscolha(raca)
        );
        Dnd5eRacaUtil.atualizarLabelsBonusExtra(
            raca,
            ['f5e_extra1_label', 'f5e_extra2_label'],
            el
        );
        const temPericiaExtra =
            raca &&
            Array.isArray(raca.caracteristicas) &&
            raca.caracteristicas.includes('proficiencia_pericia_extra');
        el('f5e_pericia_racial_wrap').hidden = !temPericiaExtra;
    }

    function preencherSelectExtra() {
        const opts = ABILITIES.map(
            (a) => `<option value="${a.key}">${a.name}</option>`
        ).join('');
        el('f5e_extra1').innerHTML = opts;
        el('f5e_extra2').innerHTML = opts;
        el('f5e_extra2').value = 'wisdom';
        const perOpts =
            '<option value="">—</option>' +
            catalogoPericias.map((p) => `<option value="${p.slug}">${p.nome}</option>`).join('');
        el('f5e_pericia_racial').innerHTML = perOpts;
    }

    function renderPericiasEscolha() {
        const classeSlug = el('f5e_classe').value;
        const classe = catalogoClasses.find((c) => c.slug === classeSlug);
        const host = el('f5e_pericias_escolha');
        const hint = el('f5e_pericias_classe_hint');
        if (!classe) {
            host.innerHTML = '';
            hint.textContent = '';
            return;
        }
        const qtd = classe.pericias_escolha_qtd || 0;
        let pool = classe.pericias_escolha_de || [];
        if (!pool.length && qtd > 0) {
            pool = catalogoPericias.map((p) => p.slug);
        }
        hint.textContent =
            qtd > 0
                ? `Escolha até ${qtd} perícia(s) de classe.`
                : 'Esta classe não exige escolha de perícias no nível 1.';
        const escolhidas = new Set(getPericiasClasseEscolhidas());
        const selAtual = getPericiasClasseEscolhidas();
        const noLimite = qtd > 0 && selAtual.length >= qtd;
        host.innerHTML = pool
            .map((slug) => {
                const checked = escolhidas.has(slug) ? 'checked' : '';
                const disabled =
                    qtd > 0 && noLimite && !escolhidas.has(slug) ? 'disabled' : '';
                return `<label class="ficha-dnd5e-pericia-opt">
                    <input type="checkbox" value="${slug}" ${checked} ${disabled} />
                    <span>${periciaNome(slug)}</span>
                </label>`;
            })
            .join('');
        host.querySelectorAll('input').forEach((inp) => {
            inp.addEventListener('change', () => {
                const sel = getPericiasClasseEscolhidas();
                if (sel.length > qtd) {
                    inp.checked = false;
                    Toast.error(`Máximo ${qtd} perícia(s) de classe.`);
                    return;
                }
                renderPericiasEscolha();
                agendarPreview();
            });
        });
    }

    function renderSalvamentos(salvamentos) {
        const host = el('f5e_salvamentos');
        if (!host) return;
        if (!salvamentos || !salvamentos.length) {
            host.innerHTML = '<span class="ficha-vazio">—</span>';
            return;
        }
        const labels = { strength: 'Fort', dexterity: 'Ref', constitution: 'Con', intelligence: 'Int', wisdom: 'Sab', charisma: 'Car' };
        host.innerHTML = salvamentos
            .map((s) => {
                const nome = s.nome || labels[s.habilidade] || s.habilidade;
                return `<div class="ficha-resistencia-box">
                    <span class="ficha-res-label">${nome}</span>
                    <span class="ficha-res-valor">${fmtMod(s.bonus)}</span>
                </div>`;
            })
            .join('');
    }

    function renderPericiasGrade(pericias) {
        const host = el('f5e_pericias_grade');
        if (!pericias || !pericias.length) {
            host.innerHTML = '';
            return;
        }
        host.innerHTML = pericias
            .map(
                (p) => `
            <div class="ficha-dnd5e-pericia-row${p.proficiente ? ' is-prof' : ''}">
                <span>${p.nome}</span>
                <strong>${fmtMod(p.bonus)}</strong>
            </div>`
            )
            .join('');
    }

    function atualizarAntecedentePainel(ant) {
        const painel = el('f5e_antecedente_painel');
        const resumo = el('f5e_antecedente_resumo');
        if (!ant) {
            painel.hidden = true;
            return;
        }
        painel.hidden = false;
        const per = (ant.pericias || []).join(', ');
        resumo.innerHTML = [
            `<strong>${ant.nome}</strong>`,
            per ? `Perícias: ${per}` : '',
            ant.idiomas_qtd ? `Idiomas extras: ${ant.idiomas_qtd}` : '',
            ant.equipamento && ant.equipamento.length
                ? `Equipamento: ${ant.equipamento.join(', ')}`
                : '',
            ant.ouro_po ? `Ouro inicial: ${ant.ouro_po} PO` : '',
        ]
            .filter(Boolean)
            .join(' · ');
    }

    async function atualizarSubclasses() {
        const classeSlug = el('f5e_classe').value;
        const nivel = parseInt(el('f5e_nivel').value, 10) || 1;
        const wrap = el('f5e_subclasse_wrap');
        const select = el('f5e_subclasse');
        const atual = select.value;
        if (!classeSlug) {
            wrap.hidden = true;
            return;
        }
        try {
            const data = await rs.subclasses(classeSlug);
            const subs = data.subclasses || [];
            const disponiveis = subs.filter((s) => nivel >= s.nivel_escolha);
            const hdrWrap = el('fichaHdrSubclasseWrap');
            if (!disponiveis.length) {
                wrap.hidden = true;
                if (hdrWrap) hdrWrap.hidden = true;
                select.innerHTML = '<option value="">—</option>';
                return;
            }
            wrap.hidden = false;
            select.innerHTML =
                '<option value="">—</option>' +
                disponiveis
                    .map(
                        (s) =>
                            `<option value="${s.slug}">${s.nome} (nív. ${s.nivel_escolha}+)</option>`
                    )
                    .join('');
            if (atual && disponiveis.some((s) => s.slug === atual)) {
                select.value = atual;
            }
            atualizarHeaderIdentidade();
        } catch {
            wrap.hidden = true;
            if (el('fichaHdrSubclasseWrap')) el('fichaHdrSubclasseWrap').hidden = true;
        }
    }

    function atualizarBarraPv(hpAtual, hpMax) {
        const fill = el('fichaPvFill');
        const label = el('f5e_hp_atual_label');
        const maxEl = el('f5e_hp_max');
        const max = Math.max(1, hpMax || 1);
        const cur = Math.max(0, Math.min(max, hpAtual ?? max));
        if (maxEl) maxEl.textContent = String(max);
        if (label) label.textContent = String(cur);
        if (fill) fill.style.width = `${Math.round((cur / max) * 100)}%`;
    }

    function atualizarHeaderIdentidade() {
        const racaSlug = el('f5e_raca').value;
        const classeSlug = el('f5e_classe').value;
        const antSlug = el('f5e_antecedente').value;
        const subSlug = el('f5e_subclasse').value;
        const raca = catalogoRacas.find((r) => r.slug === racaSlug);
        const classe = catalogoClasses.find((c) => c.slug === classeSlug);
        const ant = catalogoAntecedentes.find((a) => a.slug === antSlug);
        const nome = el('f5e_nome').value.trim();
        if (el('fichaHeaderNome')) el('fichaHeaderNome').textContent = nome || 'Ficha D&D 5e';
        if (el('fichaHdrJogador')) {
            el('fichaHdrJogador').textContent =
                el('f5e_jogador').value.trim() || nomeJogadorLogado() || '—';
        }
        if (el('fichaHdrNivel')) el('fichaHdrNivel').textContent = el('f5e_nivel').value || '1';
        if (el('fichaHdrRaca')) el('fichaHdrRaca').textContent = raca ? raca.nome : '—';
        if (el('fichaHdrClasse')) el('fichaHdrClasse').textContent = classe ? classe.nome : '—';
        const fichaClasse = el('fichaClasse');
        if (fichaClasse) fichaClasse.textContent = classe ? classe.nome : '—';
        if (el('fichaHdrAntecedente')) {
            el('fichaHdrAntecedente').textContent = ant ? ant.nome : '—';
        }
        if (el('fichaHdrXp')) el('fichaHdrXp').textContent = el('f5e_xp').value || '0';
        const tipoEl = el('fichaHdrTipo');
        if (tipoEl) {
            tipoEl.textContent = tipoCriacao;
            const chip = tipoEl.closest('.ficha-hdr-chip-tipo');
            if (chip) {
                chip.className = `ficha-hdr-chip ficha-hdr-chip-tipo ficha-hdr-chip-tipo--${tipoCriacao}`;
            }
        }
        const subWrap = el('fichaHdrSubclasseWrap');
        const subVal = el('fichaHdrSubclasse');
        if (subWrap && subVal) {
            if (subSlug) {
                const opt = el('f5e_subclasse')?.selectedOptions?.[0];
                const nomeSub =
                    (previewAtual?.subclasse?.slug === subSlug
                        ? previewAtual.subclasse.nome
                        : null) ||
                    (opt?.value ? opt.textContent.replace(/\s*\(nív\..*$/, '').trim() : null) ||
                    subSlug.replace(/_/g, ' ');
                subVal.textContent = nomeSub;
                subWrap.hidden = false;
            } else {
                subWrap.hidden = true;
            }
        }
    }

    function renderFoto(url) {
        const foto = el('fichaFoto');
        const placeholder = el('fichaFotoPlaceholder');
        if (url && foto) {
            foto.src = url;
            foto.classList.add('carregada');
            if (placeholder) placeholder.style.display = 'none';
        } else {
            if (foto) {
                foto.removeAttribute('src');
                foto.classList.remove('carregada');
            }
            if (placeholder) placeholder.style.display = 'flex';
        }
    }

    async function enviarFotoArquivo(file) {
        if (!personagemId) {
            Toast.error('Salve a ficha antes de enviar a foto.');
            return;
        }
        const area = el('fichaFotoArea');
        area?.classList.add('is-uploading');
        try {
            const atualizado = await ps.enviarFoto(personagemId, file);
            renderFoto(atualizado.foto_url);
            Toast.success('Retrato atualizado.');
        } catch (e) {
            Toast.error(e.message || 'Erro ao enviar foto');
        } finally {
            area?.classList.remove('is-uploading');
        }
    }

    function configurarUploadFoto() {
        const input = el('f5e_foto_file');
        const btn = el('btnF5eFotoUpload');
        const area = el('fichaFotoArea');
        const abrir = () => input?.click();
        btn?.addEventListener('click', abrir);
        area?.addEventListener('click', () => {
            if (personagemId) abrir();
            else Toast.error('Salve a ficha antes de enviar a foto.');
        });
        input?.addEventListener('change', () => {
            const file = input.files?.[0];
            if (file) enviarFotoArquivo(file);
            input.value = '';
        });
    }

    function aplicarPreview(p) {
        previewAtual = p;
        ABILITIES.forEach((a) => {
            const mod = p.modificadores[a.key];
            const eff = p.scores_efetivos[a.key];
            el(`mod_${a.key}`).textContent = fmtMod(mod);
            el(`eff_${a.key}`).textContent = String(eff);
        });
        const hpMax = p.hp_max_nivel_1;
        el('f5e_hp_max').textContent = String(hpMax);
        const hpInput = el('f5e_hp_atual');
        if (!hpInput.dataset.userTouched) {
            hpInput.value = String(hpMax);
        }
        atualizarBarraPv(parseInt(hpInput.value, 10), hpMax);
        if (el('f5e_ca')) el('f5e_ca').textContent = String(p.ca_total ?? p.ca_base);
        el('f5e_iniciativa').textContent = fmtMod(p.iniciativa);
        const nivel = parseInt(el('f5e_nivel').value, 10) || 1;
        el('f5e_prof').textContent = fmtMod(p.bonus_proficiencia ?? bonusProficiencia(nivel));
        renderSalvamentos(p.salvamentos);
        renderPericiasGrade(p.pericias);
        atualizarAntecedentePainel(p.antecedente);
        atualizarHeaderIdentidade();
        if (typeof window.__dnd5eAtualizarSecaoMagias === 'function') {
            window.__dnd5eAtualizarSecaoMagias();
        }
    }

    async function rodarPreview() {
        const raca = el('f5e_raca').value;
        const classe = el('f5e_classe').value;
        if (!raca || !classe) return;
        try {
            const p = await rs.calcularAtributos(payloadCalcular());
            aplicarPreview(p);
            el('f5e_status').textContent = '';
        } catch (e) {
            el('f5e_status').textContent = e.message || 'Erro no cálculo';
        }
    }

    function agendarPreview() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(rodarPreview, 280);
    }

    function aplicarAtributosNeutros() {
        ABILITIES.forEach((a) => {
            el(`base_${a.key}`).value = '10';
        });
        agendarPreview();
    }

    function aplicarMatrizPadrao() {
        ABILITIES.forEach((a, i) => {
            el(`base_${a.key}`).value = String(MATRIZ_PADRAO[i]);
        });
        agendarPreview();
    }

    function renderCondicoesFicha() {
        const host = el('f5e_condicoes_lista');
        const lista = arenaCondicoesAtual || [];
        if (!lista.length) {
            host.innerHTML =
                '<span class="ficha-dnd5e-condicoes-vazio">Nenhuma condição ativa</span>';
            return;
        }
        host.innerHTML = lista
            .map((c) => {
                const auto = c.origem === 'hp' ? ' is-auto' : '';
                return `<span class="ficha-dnd5e-cond-badge${auto}" title="${c.origem === 'hp' ? 'Automático (0 PV)' : 'Condição de arena'}">${CU.label(c, catalogoCondicoes)}</span>`;
            })
            .join('');
    }

    async function sincronizarCondicoesPorHp() {
        const hp = parseInt(el('f5e_hp_atual').value, 10);
        const hpAtual = Number.isFinite(hp) ? Math.max(0, hp) : 0;
        try {
            const res = await cs.sincronizarCondicoesHp(hpAtual, arenaCondicoesAtual);
            arenaCondicoesAtual = CU.normalizarLista(res.condicoes || []);
            renderCondicoesFicha();
        } catch (_e) {
            /* preview offline */
        }
    }

    function agendarSyncHpCondicoes() {
        clearTimeout(debounceHpCondTimer);
        debounceHpCondTimer = setTimeout(sincronizarCondicoesPorHp, 300);
    }

    function montarFichaJson(preview) {
        const base = getScoresBase();
        const f = {
            v: 1,
            raca_slug: el('f5e_raca').value,
            classe_slug: el('f5e_classe').value,
            antecedente_slug: el('f5e_antecedente').value || null,
            subclasse_slug: el('f5e_subclasse').value || null,
            scores_base: base,
            bonus_habilidade_extra: getBonusExtra(),
            pericias_classe_escolhidas: getPericiasClasseEscolhidas(),
            pericia_racial_extra: el('f5e_pericia_racial').value || null,
            armadura_slug: el('f5e_armadura').value || null,
            escudo_slug: el('f5e_escudo').value || null,
            notas: el('f5e_notas').value.trim(),
        };
        if (preview) {
            f.ca_base = preview.ca_base;
            f.ca_total = preview.ca_total;
            f.pericias_proficientes = preview.pericias_proficientes;
            f.hp_max_nivel_1_ref = preview.hp_max_nivel_1;
            if (preview.subclasse) f.subclasse_nome = preview.subclasse.nome;
        }
        f.arena_condicoes = arenaCondicoesAtual;
        return f;
    }

    function validarAntesSalvar() {
        const classe = catalogoClasses.find((c) => c.slug === el('f5e_classe').value);
        const qtd = (classe && classe.pericias_escolha_qtd) || 0;
        const sel = getPericiasClasseEscolhidas();
        if (qtd > 0 && sel.length !== qtd) {
            Toast.error(`Escolha exatamente ${qtd} perícia(s) de classe.`);
            return false;
        }
        const raca = catalogoRacas.find((r) => r.slug === el('f5e_raca').value);
        const precisaPericiaRacial =
            raca &&
            Array.isArray(raca.caracteristicas) &&
            raca.caracteristicas.includes('proficiencia_pericia_extra');
        if (precisaPericiaRacial && !el('f5e_pericia_racial').value) {
            Toast.error('Escolha a perícia extra concedida pela raça.');
            return false;
        }
        return true;
    }

    async function salvar() {
        const nome = el('f5e_nome').value.trim();
        if (!nome) {
            Toast.error('Informe o nome do personagem.');
            return;
        }
        if (!el('f5e_raca').value || !el('f5e_classe').value) {
            Toast.error('Selecione raça e classe.');
            return;
        }
        if (!validarAntesSalvar()) return;

        el('f5e_status').textContent = 'Salvando…';
        try {
            const preview = await rs.calcularAtributos(payloadCalcular());
            const eff = preview.scores_efetivos;
            const nivel = parseInt(el('f5e_nivel').value, 10) || 1;
            const hpMax =
                nivel === 1 ? preview.hp_max_nivel_1 : parseInt(el('f5e_hp_max').textContent, 10);
            const hpAtual = parseInt(el('f5e_hp_atual').value, 10);
            const payload = {
                nome,
                jogador_nome: el('f5e_jogador').value.trim() || null,
                nivel,
                experiencia: parseInt(el('f5e_xp').value, 10) || 0,
                strength: eff.strength,
                dexterity: eff.dexterity,
                constitution: eff.constitution,
                intelligence: eff.intelligence,
                wisdom: eff.wisdom,
                charisma: eff.charisma,
                hp_max: hpMax,
                hp_atual: Number.isFinite(hpAtual) ? hpAtual : hpMax,
                ficha: montarFichaJson(preview),
            };

            if (personagemId) {
                await ps.atualizar(personagemId, payload);
                Toast.success('Ficha salva.');
            } else {
                payload.tipo = tipoCriacao;
                const criado = await ps.criar(payload);
                Toast.success('Personagem criado.');
                window.location.replace(`ficha-personagem.html?id=${criado.id}`);
                return;
            }
            el('f5e_status').textContent = 'Salvo';
        } catch (e) {
            el('f5e_status').textContent = '';
            Toast.error(e.message || 'Erro ao salvar');
        }
    }

    function preencherSelects() {
        el('f5e_raca').innerHTML = catalogoRacas
            .map((r) => `<option value="${r.slug}">${r.nome}</option>`)
            .join('');
        el('f5e_classe').innerHTML = catalogoClasses
            .map((c) => `<option value="${c.slug}">${c.nome} (${c.dado_vida})</option>`)
            .join('');
        el('f5e_antecedente').innerHTML =
            '<option value="">—</option>' +
            catalogoAntecedentes
                .map((a) => `<option value="${a.slug}">${a.nome}</option>`)
                .join('');
        el('f5e_armadura').innerHTML =
            '<option value="">Sem armadura</option>' +
            armaduras
                .map((a) => `<option value="${a.slug}">${a.nome} (CA ${a.ca})</option>`)
                .join('');
        el('f5e_escudo').innerHTML =
            '<option value="">Nenhum</option>' +
            escudos.map((s) => `<option value="${s.slug}">${s.nome} (+${s.bonus_ac})</option>`).join('');
    }

    function carregarPersonagem(p) {
        if (p.tipo) tipoCriacao = p.tipo;
        el('f5e_nome').value = p.nome || '';
        el('f5e_jogador').value = p.jogador_nome || nomeJogadorLogado();
        el('f5e_nivel').value = p.nivel;
        el('f5e_xp').value = p.experiencia;
        el('f5e_hp_atual').value = p.hp_atual;
        el('f5e_hp_atual').dataset.userTouched = '1';

        const f = p.ficha || {};
        arenaCondicoesAtual = CU.normalizarLista(f.arena_condicoes || []);
        sincronizarCondicoesPorHp();
        if (f.raca_slug) el('f5e_raca').value = f.raca_slug;
        if (f.classe_slug) el('f5e_classe').value = f.classe_slug;
        if (f.antecedente_slug) el('f5e_antecedente').value = f.antecedente_slug;
        if (f.armadura_slug) el('f5e_armadura').value = f.armadura_slug;
        if (f.escudo_slug) el('f5e_escudo').value = f.escudo_slug;
        if (f.notas) el('f5e_notas').value = f.notas;
        const base = f.scores_base || {};
        ABILITIES.forEach((a) => {
            if (base[a.key] != null) el(`base_${a.key}`).value = base[a.key];
        });
        if (f.bonus_habilidade_extra) {
            const keys = Object.keys(f.bonus_habilidade_extra);
            if (keys[0]) el('f5e_extra1').value = keys[0];
            if (keys[1]) el('f5e_extra2').value = keys[1];
        }
        if (f.pericia_racial_extra) el('f5e_pericia_racial').value = f.pericia_racial_extra;

        renderFoto(p.foto_url);
        atualizarHeaderIdentidade();
        el('f5e_hp_max').textContent = String(p.hp_max);
        atualizarBarraPv(p.hp_atual, p.hp_max);
        atualizarUiRaca();
        renderPericiasEscolha();
        if (f.pericias_classe_escolhidas) {
            f.pericias_classe_escolhidas.forEach((slug) => {
                const cb = document.querySelector(
                    `#f5e_pericias_escolha input[value="${slug}"]`
                );
                if (cb) cb.checked = true;
            });
        }
        atualizarSubclasses().then(() => {
            if (f.subclasse_slug) el('f5e_subclasse').value = f.subclasse_slug;
        });
        rodarPreview();
    }

    function configurarTipoCriacao() {
        if (personagemId) return;
        if (
            (tipoCriacao === 'monstro' || tipoCriacao === 'npc') &&
            typeof AuthService.isMestre === 'function' &&
            !AuthService.isMestre()
        ) {
            tipoCriacao = 'jogador';
            Toast.error('Apenas mestre pode criar monstro ou NPC.');
            window.location.replace('ficha-personagem.html');
            return;
        }
        const labels = { jogador: 'Novo jogador', monstro: 'Novo monstro', npc: 'Novo NPC' };
        if (el('fichaHeaderNome')) {
            el('fichaHeaderNome').textContent = labels[tipoCriacao] || 'Ficha D&D 5e';
        }
        atualizarHeaderIdentidade();
    }

    function aplicarModoPreCadastroFixo() {
        if (!personagemId) return;
        document.body.classList.add('ficha-dnd5e-pre-cadastro-fixo');
        [
            'f5e_nome',
            'f5e_nivel',
            'f5e_raca',
            'f5e_classe',
            'f5e_antecedente',
            'f5e_subclasse',
            'f5e_xp',
            'f5e_extra1',
            'f5e_extra2',
            'f5e_pericia_racial',
        ].forEach((id) => {
            const node = el(id);
            if (!node) return;
            node.disabled = true;
            if (node.tagName === 'INPUT') node.readOnly = true;
            node.setAttribute('data-pre-cadastro-lock', '');
        });
        ABILITIES.forEach((a) => {
            const inp = el(`base_${a.key}`);
            if (inp) inp.disabled = true;
        });
        el('btnMatrizPadrao')?.setAttribute('hidden', '');
        document
            .querySelectorAll('#f5e_pericias_escolha input[type=checkbox]')
            .forEach((cb) => {
                cb.disabled = true;
            });
    }

    window.__dnd5eFichaGrimorioApi = {
        getSnapshot() {
            const nivel = parseInt(el('f5e_nivel').value, 10) || 1;
            return {
                id: personagemId,
                nome: el('f5e_nome').value.trim(),
                nivel,
                ficha: {
                    classe_slug: el('f5e_classe').value,
                    raca_slug: el('f5e_raca').value,
                },
            };
        },
        getClasseNome() {
            const slug = el('f5e_classe').value;
            const c = catalogoClasses.find((x) => x.slug === slug);
            return c ? c.nome : slug;
        },
    };

    async function init() {
        configurarTipoCriacao();
        AuthService.configurarHeaderUsuario();

        el('f5e_jogador').value = nomeJogadorLogado();
        renderAbilities();

        el('btnMatrizPadrao').addEventListener('click', aplicarMatrizPadrao);
        el('btnSalvar').addEventListener('click', salvar);
        el('f5e_raca').addEventListener('change', () => {
            atualizarUiRaca();
            atualizarHeaderIdentidade();
            agendarPreview();
        });
        el('f5e_classe').addEventListener('change', () => {
            renderPericiasEscolha();
            atualizarSubclasses();
            atualizarHeaderIdentidade();
            if (typeof window.__dnd5eAtualizarSecaoMagias === 'function') {
                window.__dnd5eAtualizarSecaoMagias();
            }
            agendarPreview();
        });
        el('f5e_nivel').addEventListener('change', () => {
            atualizarHeaderIdentidade();
            if (typeof window.__dnd5eAtualizarSecaoMagias === 'function') {
                window.__dnd5eAtualizarSecaoMagias();
            }
        });
        el('f5e_antecedente').addEventListener('change', agendarPreview);
        el('f5e_extra1').addEventListener('change', agendarPreview);
        el('f5e_extra2').addEventListener('change', agendarPreview);
        el('f5e_pericia_racial').addEventListener('change', agendarPreview);
        el('f5e_armadura').addEventListener('change', agendarPreview);
        el('f5e_escudo').addEventListener('change', agendarPreview);
        el('f5e_subclasse').addEventListener('change', agendarPreview);
        el('f5e_nivel').addEventListener('change', () => {
            atualizarSubclasses();
            agendarPreview();
        });
        el('f5e_hp_atual').addEventListener('input', () => {
            el('f5e_hp_atual').dataset.userTouched = '1';
            const hpMax = parseInt(el('f5e_hp_max').textContent, 10) || 1;
            atualizarBarraPv(parseInt(el('f5e_hp_atual').value, 10), hpMax);
            agendarSyncHpCondicoes();
        });
        el('f5e_nome').addEventListener('input', atualizarHeaderIdentidade);
        configurarUploadFoto();

        try {
            const [racas, classes, ant, per, equip, combateMeta] = await Promise.all([
                rs.racas(),
                rs.classes(),
                rs.antecedentes(),
                rs.pericias(),
                rs.equipamento(),
                rs.combate().catch(() => ({ condicoes: [] })),
            ]);
            catalogoCondicoes = combateMeta.condicoes || [];
            catalogoRacas = racas.racas || [];
            catalogoClasses = classes.classes || [];
            catalogoAntecedentes = ant.antecedentes || [];
            catalogoPericias = per.pericias || [];
            armaduras = equip.armaduras || [];
            escudos = equip.escudos || [];
            preencherSelects();
            preencherSelectExtra();
            atualizarUiRaca();
            renderPericiasEscolha();

            if (personagemId) {
                const p = await ps.obter(personagemId);
                carregarPersonagem(p);
                aplicarModoPreCadastroFixo();
            } else {
                aplicarAtributosNeutros();
                renderCondicoesFicha();
                Toast.error('Use o dashboard (+ Jogador) para o pré-cadastro.');
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 2200);
            }
        } catch (e) {
            Toast.error(e.message || 'Erro ao carregar catálogos');
        }
    }

    init();
})();
