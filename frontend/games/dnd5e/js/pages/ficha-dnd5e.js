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
    let catalogoIdiomas = [];
    let catalogoCondicoes = [];
    let inventarioPanel = null;
    let previewAtual = null;
    let fichaProgressaoLocal = {
        metodo_atributos: 'padrao',
        progressao: { hp_rolls: [], marcos: [] },
        feats: [],
        feat_escolhas: {},
        bonus_atributo_feat: {},
        pericias_override: {},
        expertise_pericias: [],
    };
    let periciasEditModo = false;
    let periciasDesejadasLocal = {};
    let periciasOverrideSalvo = {};
    let expertiseLocal = [];
    let progressaoPanel = null;
    let debounceTimer = null;
    let debounceHpCondTimer = null;
    let arenaCondicoesAtual = [];
    let syncXpEmAndamento = false;
    let xpSalvoNoServidor = 0;
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

    function subclasseValidaParaPreview() {
        const sub = el('f5e_subclasse')?.value;
        if (!sub) return null;
        const nivel = parseInt(el('f5e_nivel').value, 10) || 1;
        const opt = el('f5e_subclasse')?.selectedOptions?.[0];
        const match = opt?.textContent?.match(/nív\.\s*(\d+)/i);
        const minNivel = match ? parseInt(match[1], 10) : 3;
        return nivel >= minNivel ? sub : null;
    }

    function sincronizarXpComNivel() {
        if (typeof Dnd5eXpUtil === 'undefined' || syncXpEmAndamento) return;
        syncXpEmAndamento = true;
        Dnd5eXpUtil.aplicarNivelParaXp(el('f5e_nivel'), el('f5e_xp'));
        syncXpEmAndamento = false;
        atualizarHeaderIdentidade();
    }

    function sincronizarNivelComXp() {
        if (typeof Dnd5eXpUtil === 'undefined' || syncXpEmAndamento) return;
        syncXpEmAndamento = true;
        const novoNivel = Dnd5eXpUtil.aplicarXpParaNivel(el('f5e_xp'), el('f5e_nivel'));
        syncXpEmAndamento = false;
        if (novoNivel == null) {
            atualizarHeaderIdentidade();
            atualizarPendenciasLocais();
            return;
        }
        atualizarHeaderIdentidade();
        atualizarSubclasses();
        if (typeof window.__dnd5eAtualizarSecaoMagias === 'function') {
            window.__dnd5eAtualizarSecaoMagias();
        }
        agendarPreview();
        progressaoPanel?.renderPendenciasLocais(previewAtual?.pendencias || []);
    }

    function atualizarPendenciasLocais() {
        progressaoPanel?.renderPendenciasLocais(previewAtual?.pendencias || []);
    }

    function aoAlterarNivel() {
        sincronizarXpComNivel();
        atualizarHeaderIdentidade();
        if (typeof window.__dnd5eAtualizarSecaoMagias === 'function') {
            window.__dnd5eAtualizarSecaoMagias();
        }
        atualizarSubclasses();
        agendarPreview();
        if (personagemId) {
            progressaoPanel?.refreshPendencias();
        } else {
            atualizarPendenciasLocais();
        }
    }

    function payloadCalcular() {
        const armEsc = inventarioPanel
            ? inventarioPanel.getArmaduraEscudoParaCalcular()
            : {
                  armadura_slug: el('f5e_armadura')?.value || null,
                  escudo_slug: el('f5e_escudo')?.value || null,
              };
        return {
            raca_slug: el('f5e_raca').value,
            raca_variante_slug: el('f5e_raca_variante')?.value || null,
            classe_slug: el('f5e_classe').value,
            antecedente_slug: el('f5e_antecedente').value || null,
            scores_base: getScoresBase(),
            bonus_habilidade_extra: getBonusExtra(),
            bonus_atributo_feat: fichaProgressaoLocal.bonus_atributo_feat || {},
            nivel: parseInt(el('f5e_nivel').value, 10) || 1,
            pericias_classe_escolhidas: getPericiasClasseEscolhidas(),
            pericia_racial_extra: el('f5e_pericia_racial').value || null,
            subclasse_slug: subclasseValidaParaPreview(),
            armadura_slug: armEsc.armadura_slug,
            escudo_slug: armEsc.escudo_slug,
            feats: fichaProgressaoLocal.feats || [],
            feat_escolhas: fichaProgressaoLocal.feat_escolhas || {},
            pericias_override: fichaProgressaoLocal.pericias_override || {},
            expertise_pericias: fichaProgressaoLocal.expertise_pericias || [],
            progressao: fichaProgressaoLocal.progressao || { hp_rolls: [], marcos: [] },
        };
    }

    function calcularPericiasOverride(desejadas, automaticas) {
        const auto = new Set(automaticas || []);
        const override = {};
        Object.keys(desejadas || {}).forEach((slug) => {
            const desejada = !!desejadas[slug];
            const autoProf = auto.has(slug);
            if (desejada !== autoProf) {
                override[slug] = desejada;
            }
        });
        return override;
    }

    function sincronizarPericiasOverrideLocal() {
        if (!periciasEditModo || !previewAtual) return;
        fichaProgressaoLocal.pericias_override = calcularPericiasOverride(
            periciasDesejadasLocal,
            previewAtual.pericias_automaticas || []
        );
    }

    function setModoEdicaoPericias(ativo) {
        periciasEditModo = !!ativo;
        const sec = document.querySelector('.ficha-dnd5e-secao-pericias-todas');
        sec?.classList.toggle('is-editing', periciasEditModo);
        el('f5e_btn_editar_pericias').hidden = periciasEditModo;
        el('f5e_btn_salvar_pericias').hidden = !periciasEditModo;
        el('f5e_btn_cancelar_pericias').hidden = !periciasEditModo;
        const leg = el('f5e_pericias_grade_legenda');
        if (leg) {
            leg.textContent = periciasEditModo
                ? 'Marque as perícias em que o personagem é proficiente (multiclasse, talentos, mesa).'
                : 'Bônus totais · destaque = proficiente';
        }
    }

    function abrirEditorPericias() {
        if (!previewAtual?.pericias?.length) {
            Toast.error('Aguarde o cálculo da ficha antes de editar perícias.');
            return;
        }
        periciasOverrideSalvo = { ...(fichaProgressaoLocal.pericias_override || {}) };
        periciasDesejadasLocal = {};
        previewAtual.pericias.forEach((p) => {
            periciasDesejadasLocal[p.slug] = !!p.proficiente;
        });
        setModoEdicaoPericias(true);
        renderPericiasGrade(previewAtual.pericias);
    }

    function cancelarEditorPericias() {
        fichaProgressaoLocal.pericias_override = { ...periciasOverrideSalvo };
        periciasDesejadasLocal = {};
        setModoEdicaoPericias(false);
        agendarPreview();
    }

    async function salvarPericiasOverride() {
        sincronizarPericiasOverrideLocal();
        const override = { ...(fichaProgressaoLocal.pericias_override || {}) };
        try {
            if (personagemId) {
                const res = await ps.progressaoPericiasOverride(personagemId, {
                    pericias_override: override,
                });
                if (res.pericias_override) {
                    fichaProgressaoLocal.pericias_override = res.pericias_override;
                }
                if (res.ficha?.pericias_override) {
                    fichaProgressaoLocal.pericias_override = res.ficha.pericias_override;
                }
                progressaoPanel?.renderPendenciasLocais(res.pendencias || []);
            } else {
                fichaProgressaoLocal.pericias_override = override;
            }
            periciasOverrideSalvo = { ...fichaProgressaoLocal.pericias_override };
            setModoEdicaoPericias(false);
            periciasDesejadasLocal = {};
            await rodarPreview();
            Toast.success('Proficiências de perícias salvas.');
        } catch (e) {
            Toast.error(e.message || 'Erro ao salvar proficiências');
        }
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
        const temVariante = Dnd5eRacaUtil.temVarianteEscolha(raca);
        el('f5e_raca_variante_wrap').hidden = !temVariante;
        if (temVariante) {
            const lbl = el('f5e_raca_variante_label');
            if (lbl) lbl.textContent = Dnd5eRacaUtil.labelVariante(raca);
            Dnd5eRacaUtil.preencherSelectVariante(
                raca,
                el('f5e_raca_variante'),
                el('f5e_raca_variante')?.value
            );
        }
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
        const nivel = parseInt(el('f5e_nivel').value, 10) || 1;
        const profBonus = previewAtual?.bonus_proficiencia ?? bonusProficiencia(nivel);
        if (periciasEditModo) {
            host.innerHTML = pericias
                .map((p) => {
                    const prof = !!periciasDesejadasLocal[p.slug];
                    const modBase = Number(p.bonus) - (p.proficiente ? profBonus : 0);
                    const bonus = modBase + (prof ? profBonus : 0);
                    const checked = prof ? 'checked' : '';
                    return `<div class="ficha-dnd5e-pericia-row is-edit${prof ? ' is-prof' : ''}">
                <label>
                    <input type="checkbox" data-pericia-slug="${p.slug}" ${checked} />
                    <span>${p.nome}</span>
                </label>
                <strong>${fmtMod(bonus)}</strong>
            </div>`;
                })
                .join('');
            host.querySelectorAll('input[data-pericia-slug]').forEach((inp) => {
                inp.addEventListener('change', () => {
                    const slug = inp.getAttribute('data-pericia-slug');
                    periciasDesejadasLocal[slug] = inp.checked;
                    sincronizarPericiasOverrideLocal();
                    renderPericiasGrade(pericias);
                    agendarPreview();
                });
            });
            return;
        }
        host.innerHTML = pericias
            .map(
                (p) => `
            <div class="ficha-dnd5e-pericia-row${p.proficiente ? ' is-prof' : ''}${p.expertise ? ' is-expert' : ''}">
                <span>${p.nome}${p.expertise ? ' <em class="ficha-dnd5e-expertise-tag">2× prof</em>' : ''}</span>
                <strong>${fmtMod(p.bonus)}</strong>
            </div>`
            )
            .join('');
    }

    function renderExpertiseSection(preview) {
        const wrap = el('f5e_expertise_wrap');
        const hint = el('f5e_expertise_hint');
        const host = el('f5e_expertise_escolha');
        const slots = Number(preview?.expertise_slots_classe || 0);
        if (!wrap || !host) return;
        if (!slots) {
            wrap.hidden = true;
            host.innerHTML = '';
            return;
        }
        wrap.hidden = false;
        const classe = preview?.classe?.nome || 'classe';
        if (hint) {
            hint.textContent = `${classe}: escolha ${slots} perícia(s) proficiente(s) para dobrar o bônus de proficiência (Expertise).`;
        }
        const profs = (preview?.pericias || []).filter((x) => x.proficiente);
        const escolhidas = new Set(expertiseLocal || []);
        host.innerHTML = profs
            .map((p) => {
                const checked = escolhidas.has(p.slug) ? 'checked' : '';
                return `<label class="ficha-dnd5e-expertise-item">
                    <input type="checkbox" data-expertise-slug="${p.slug}" ${checked} />
                    <span>${p.nome}</span>
                </label>`;
            })
            .join('');
        host.querySelectorAll('input[data-expertise-slug]').forEach((inp) => {
            inp.addEventListener('change', () => {
                const slug = inp.getAttribute('data-expertise-slug');
                let next = (expertiseLocal || []).filter((s) => s !== slug);
                if (inp.checked) {
                    if (next.length >= slots) {
                        inp.checked = false;
                        Toast.error(`Escolha no máximo ${slots} perícia(s) com Expertise.`);
                        return;
                    }
                    next.push(slug);
                }
                expertiseLocal = next;
                fichaProgressaoLocal.expertise_pericias = [...next];
                agendarPreview();
            });
        });
    }

    async function salvarExpertisePericias() {
        if (!personagemId) {
            Toast.error('Salve a ficha antes de registrar Expertise.');
            return;
        }
        const slots = Number(previewAtual?.expertise_slots_classe || 0);
        const lista = [...(expertiseLocal || [])];
        if (slots && lista.length < slots) {
            Toast.error(`Escolha ${slots} perícia(s) com Expertise.`);
            return;
        }
        try {
            const res = await ps.progressaoExpertisePericias(personagemId, {
                expertise_pericias: lista,
            });
            if (res.expertise_pericias) {
                fichaProgressaoLocal.expertise_pericias = res.expertise_pericias;
                expertiseLocal = [...res.expertise_pericias];
            }
            if (res.ficha?.expertise_pericias) {
                fichaProgressaoLocal.expertise_pericias = res.ficha.expertise_pericias;
                expertiseLocal = [...res.ficha.expertise_pericias];
            }
            progressaoPanel?.renderPendenciasLocais(res.pendencias || []);
            await rodarPreview();
            Toast.success('Expertise salva.');
        } catch (e) {
            Toast.error(e.message || 'Erro ao salvar expertise');
        }
    }

    function antecedenteSelecionado() {
        const slug = el('f5e_antecedente').value || null;
        if (!slug) return null;
        return (
            catalogoAntecedentes.find((a) => a.slug === slug) || previewAtual?.antecedente || null
        );
    }

    function getIdiomasAntecedenteEscolhidos() {
        if (typeof Dnd5eIdiomasUtil === 'undefined') {
            return inventarioPanel ? inventarioPanel.getIdiomasAntecedente() : [];
        }
        const fromDom = Dnd5eIdiomasUtil.getEscolhidosDoHost(
            el('f5e_antecedente_idiomas_host'),
            'f5e-idioma'
        );
        if (fromDom.length) return fromDom;
        return inventarioPanel ? inventarioPanel.getIdiomasAntecedente() : [];
    }

    function getTracosAntecedenteEscolhidos() {
        if (typeof Dnd5eTracosUtil === 'undefined') {
            return inventarioPanel ? inventarioPanel.getTracosAntecedente() : null;
        }
        const host = el('f5e_antecedente_tracos_host');
        const ant = antecedenteSelecionado();
        const fromDom = Dnd5eTracosUtil.getEscolhidosDoHost(host);
        if (fromDom && Dnd5eTracosUtil.tracosEstaoCompletos(fromDom)) return fromDom;
        const salvos =
            inventarioPanel?.getTracosAntecedente() ||
            previewAtual?.antecedente_tracos ||
            null;
        if (salvos && ant?.tracos_opcoes) {
            return Dnd5eTracosUtil.normalizarEscolhidos(salvos, ant.tracos_opcoes);
        }
        return fromDom;
    }

    function renderTracosAntecedente(reset = false) {
        const ant = antecedenteSelecionado();
        const host = el('f5e_antecedente_tracos_host');
        const hint = el('f5e_antecedente_tracos_hint');
        const btn = el('f5e_antecedente_tracos_sortear');
        const wrap = el('f5e_antecedente_tracos_wrap');
        if (!host || typeof Dnd5eTracosUtil === 'undefined') return;
        if (!ant) {
            host.innerHTML = '';
            host.hidden = true;
            if (hint) hint.textContent = '';
            if (btn) btn.hidden = true;
            if (wrap) wrap.hidden = true;
            return;
        }
        if (wrap) wrap.hidden = false;
        if (reset) inventarioPanel?.setTracosAntecedente(null);
        const selecionados = reset
            ? null
            : inventarioPanel?.getTracosAntecedente() ||
              previewAtual?.antecedente_tracos ||
              null;
        Dnd5eTracosUtil.renderEscolha({
            host,
            hint,
            btnSortear: btn,
            opcoes: ant.tracos_opcoes || {},
            selecionados,
            idPrefix: 'f5e-traco',
            onChange: (tracos) => {
                inventarioPanel?.setTracosAntecedente(tracos);
                atualizarAntecedentePainel(ant, tracos);
            },
        });
    }

    function renderIdiomasAntecedente() {
        const ant = antecedenteSelecionado();
        const host = el('f5e_antecedente_idiomas_host');
        const hint = el('f5e_antecedente_idiomas_hint');
        if (!host || typeof Dnd5eIdiomasUtil === 'undefined') return;
        if (!ant) {
            host.innerHTML = '';
            host.hidden = true;
            if (hint) hint.textContent = '';
            return;
        }
        const selecionados =
            inventarioPanel?.getIdiomasAntecedente() ||
            Dnd5eIdiomasUtil.normalizarEscolhidos(
                previewAtual?.antecedente_idiomas,
                catalogoIdiomas
            );
        Dnd5eIdiomasUtil.renderEscolha({
            host,
            hint,
            catalogo: catalogoIdiomas,
            qtd: ant.idiomas_qtd || 0,
            selecionados,
            idPrefix: 'f5e-idioma',
            onChange: (idiomas) => {
                inventarioPanel?.setIdiomasAntecedente(idiomas);
                atualizarAntecedentePainel(ant, getTracosAntecedenteEscolhidos());
            },
        });
    }

    function atualizarAntecedentePainel(ant, tracosExtras) {
        const painel = el('f5e_antecedente_painel');
        const resumo = el('f5e_antecedente_resumo');
        if (!ant) {
            painel.hidden = true;
            return;
        }
        painel.hidden = false;
        const per = (ant.pericias || []).join(', ');
        const tracos = tracosExtras || getTracosAntecedenteEscolhidos();
        const idiomasTxt =
            ant.idiomas_qtd > 0
                ? `Idiomas: ${Dnd5eIdiomasUtil.formatLista(getIdiomasAntecedenteEscolhidos(), catalogoIdiomas) || `escolha ${ant.idiomas_qtd}`}`
                : '';
        const tracoTxt =
            tracos && typeof Dnd5eTracosUtil !== 'undefined'
                ? Dnd5eTracosUtil.formatResumo(tracos)
                : tracos && tracos.personalidade && tracos.personalidade.length
                  ? `Personalidade: ${tracos.personalidade.join(' · ')}`
                  : '';
        resumo.innerHTML = [
            `<strong>${ant.nome}</strong>`,
            per ? `Perícias: ${per}` : '',
            ant.ferramentas && ant.ferramentas.length
                ? `Ferramentas: ${ant.ferramentas.join(', ')}`
                : '',
            idiomasTxt,
            ant.equipamento && ant.equipamento.length
                ? `Equipamento: ${ant.equipamento.join(', ')}`
                : '',
            ant.ouro_po ? `Ouro do antecedente: ${ant.ouro_po} PO` : '',
            tracoTxt,
        ]
            .filter(Boolean)
            .join(' · ');
    }

    function sincronizarAntecedenteInventario() {
        if (!inventarioPanel) return;
        const slug = el('f5e_antecedente').value || null;
        const ant = slug
            ? catalogoAntecedentes.find((a) => a.slug === slug) ||
              previewAtual?.antecedente
            : null;
        const changed = inventarioPanel.sincronizarAntecedente(slug, ant);
        if (changed) {
            renderIdiomasAntecedente();
            renderTracosAntecedente(true);
        }
        if (ant) {
            renderTracosAntecedente(false);
            atualizarAntecedentePainel(ant, getTracosAntecedenteEscolhidos());
        } else {
            renderIdiomasAntecedente();
            renderTracosAntecedente(false);
        }
    }

    function sincronizarXpAoCarregar() {
        if (typeof Dnd5eXpUtil === 'undefined') return;
        const xpAntes = parseInt(el('f5e_xp').value, 10) || 0;
        const nivel = parseInt(el('f5e_nivel').value, 10) || 1;
        const ajustou = Dnd5eXpUtil.aplicarNivelParaXp(el('f5e_nivel'), el('f5e_xp'));
        const xpDepois = parseInt(el('f5e_xp').value, 10) || 0;
        if (ajustou && xpDepois !== xpAntes) {
            Toast.warning(
                `XP ajustado para ${xpDepois.toLocaleString('pt-BR')} (mínimo do nível ${nivel}). Salve a ficha para sincronizar.`
            );
            atualizarPendenciasLocais();
        }
    }

    async function aplicarEquipamentoClasse(forcar = false) {
        if (!inventarioPanel) return;
        const slug = el('f5e_classe').value;
        if (!slug) return;
        const jaAplicado =
            !forcar &&
            inventarioPanel.classeEquipMeta.slug === slug &&
            inventarioPanel.classeEquipMeta.aplicado;
        if (jaAplicado) return;
        try {
            const inv = inventarioPanel.getInventarioParaFicha();
            const res = await rs.aplicarEquipamentoClasse({
                classe_slug: slug,
                inventario: inv,
                armadura_slug: inv.armadura_slug,
                escudo_slug: inv.escudo_slug,
                arma_principal_slug: inv.arma_principal_slug,
                classe_equip_slug: inventarioPanel.classeEquipMeta.slug,
                forcar,
            });
            inventarioPanel.aplicarEquipamentoClasse(res);
            agendarPreview();
            Toast.success(res.nome_pacote || 'Equipamento inicial aplicado.');
        } catch (e) {
            Toast.error(e.message || 'Erro ao aplicar equipamento da classe');
        }
    }

    async function rolarESincronizarOuroClasse(forcar = false) {
        if (!inventarioPanel) return;
        const slug = el('f5e_classe').value;
        if (!slug) return;
        const jaAplicado =
            !forcar &&
            inventarioPanel.classeOuroMeta.slug === slug &&
            inventarioPanel.classeOuroMeta.ouro_aplicado > 0;
        if (jaAplicado) return;
        try {
            const roll = await rs.rolarOuroClasse({ classe_slug: slug });
            inventarioPanel.aplicarOuroClasse(slug, roll, forcar);
        } catch (e) {
            Toast?.error?.(e.message || 'Erro ao rolar ouro da classe');
        }
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
            } else {
                select.value = '';
            }
            atualizarHeaderIdentidade();
        } catch {
            wrap.hidden = true;
            if (el('fichaHdrSubclasseWrap')) el('fichaHdrSubclasseWrap').hidden = true;
        }
    }

    function formatHpDetalhe(resumo) {
        if (!resumo?.niveis?.length) return '';
        const n1 = resumo.niveis[0];
        const modStr = fmtMod(n1.con_mod);
        const partes = [`${resumo.dado_vida}(${n1.roll})`, `CON(${modStr})`];
        if (resumo.bonus_racial_por_nivel) {
            partes.push(`raça(+${resumo.bonus_racial_por_nivel}/nív.)`);
        }
        if (resumo.bonus_feat_por_nivel) {
            partes.push(`Tough(+${resumo.bonus_feat_por_nivel}/nív.)`);
        }
        let linha = `${partes.join(' + ')} = ${n1.subtotal} PV (nív. 1)`;
        if (resumo.niveis.length > 1) {
            const extras = resumo.niveis
                .slice(1)
                .map(
                    (n) =>
                        `nív. ${n.nivel}: ${resumo.dado_vida}(${n.roll})+CON(${fmtMod(n.con_mod)})+${n.bonus_extra} = +${n.subtotal}`
                )
                .join(' · ');
            linha += ` · ${extras} · total ${resumo.total}`;
        }
        return linha;
    }

    function renderHpDetalhe(resumo) {
        const host = el('f5e_hp_detalhe');
        if (!host) return;
        host.textContent = resumo ? formatHpDetalhe(resumo) : '';
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
        if (el('fichaHdrRaca')) el('fichaHdrRaca').textContent = raca ? raca.nome : '—';
        if (el('fichaHdrClasse')) el('fichaHdrClasse').textContent = classe ? classe.nome : '—';
        const fichaClasse = el('fichaClasse');
        if (fichaClasse) fichaClasse.textContent = classe ? classe.nome : '—';
        if (el('fichaHdrAntecedente')) {
            el('fichaHdrAntecedente').textContent = ant ? ant.nome : '—';
        }
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

    async function aplicarRepousoLongo() {
        if (!personagemId) {
            Toast.error('Salve a ficha antes do repouso longo.');
            return;
        }
        const confirmar =
            typeof Dnd5eConfirmModal !== 'undefined'
                ? () =>
                      Dnd5eConfirmModal.confirmar({
                          variante: 'repouso',
                          icone: '🌙',
                          titulo: 'Repouso longo',
                          texto: 'Seu personagem descansa 8 horas e recupera recursos.',
                          detalhe:
                              '<li><strong>PV:</strong> 1d8 + CON por nível acima de 1 (mín. 1 por nível)</li>' +
                              '<li><strong>Magia:</strong> restaura todos os espaços de magia</li>',
                          textoConfirmar: 'Aplicar repouso',
                          textoCancelar: 'Cancelar',
                      })
                : () =>
                      Promise.resolve(
                          window.confirm(
                              'Repouso longo recupera PV e espaços de magia. Continuar?'
                          )
                      );
        const ok = await confirmar();
        if (!ok) return;
        const btn = el('f5e_btn_repouso_longo');
        if (btn) btn.disabled = true;
        try {
            const res = await ps.repousoLongo(personagemId);
            if (res.hp_atual != null) {
                el('f5e_hp_atual').value = String(res.hp_atual);
                el('f5e_hp_atual').dataset.userTouched = '1';
                const hpMax =
                    parseInt(el('f5e_hp_max').textContent, 10) || res.hp_max || 1;
                atualizarBarraPv(res.hp_atual, hpMax);
            }
            if (typeof window.__dnd5eRecarregarConjuracao === 'function') {
                await window.__dnd5eRecarregarConjuracao(personagemId);
            }
            if (window._grimorioController?._recarregarDados) {
                await window._grimorioController._recarregarDados();
            }
            Toast.success(res.mensagem || 'Repouso longo aplicado.');
        } catch (e) {
            Toast.error(e.message || 'Erro no repouso longo');
        } finally {
            if (btn) btn.disabled = false;
        }
    }

    window.__dnd5eAplicarRepousoLongo = aplicarRepousoLongo;

    function aplicarPreview(p) {
        previewAtual = p;
        const tracosEl = el('f5e_tracos');
        if (tracosEl && p.tracos_resumo) {
            tracosEl.textContent = p.tracos_resumo;
            tracosEl.hidden = false;
        }
        ABILITIES.forEach((a) => {
            const mod = p.modificadores[a.key];
            const eff = p.scores_efetivos[a.key];
            el(`mod_${a.key}`).textContent = fmtMod(mod);
            el(`eff_${a.key}`).textContent = String(eff);
        });
        const nivelPreview = parseInt(el('f5e_nivel').value, 10) || 1;
        const hpMax =
            nivelPreview > 1 && p.hp_max_total
                ? p.hp_max_total
                : p.hp_max_nivel_1;
        el('f5e_hp_max').textContent = String(hpMax);
        const hpInput = el('f5e_hp_atual');
        if (!hpInput.dataset.userTouched) {
            hpInput.value = String(hpMax);
        }
        atualizarBarraPv(parseInt(hpInput.value, 10), hpMax);
        renderHpDetalhe(p.hp_resumo);
        if (el('f5e_ca')) el('f5e_ca').textContent = String(p.ca_total ?? p.ca_base);
        el('f5e_iniciativa').textContent = fmtMod(p.iniciativa);
        if (el('f5e_percepcao_passiva')) {
            el('f5e_percepcao_passiva').textContent = String(p.percepcao_passiva ?? 10);
        }
        const mi = p.magic_initiate || p.efeitos_feats?.magic_initiate;
        const miHost = el('f5e_magic_initiate_resumo');
        if (miHost) {
            miHost.textContent = mi?.resumo || '';
            miHost.hidden = !mi?.resumo;
        }
        const nivel = parseInt(el('f5e_nivel').value, 10) || 1;
        el('f5e_prof').textContent = fmtMod(p.bonus_proficiencia ?? bonusProficiencia(nivel));
        renderSalvamentos(p.salvamentos);
        renderPericiasGrade(p.pericias);
        expertiseLocal = [...(fichaProgressaoLocal.expertise_pericias || p.expertise_pericias || [])];
        renderExpertiseSection(p);
        atualizarAntecedentePainel(p.antecedente, inventarioPanel?.antecedenteMeta?.tracos);
        atualizarHeaderIdentidade();
        if (typeof window.__dnd5eAtualizarSecaoMagias === 'function') {
            window.__dnd5eAtualizarSecaoMagias();
        }
        progressaoPanel?.renderPendenciasLocais(p.pendencias || []);
    }

    async function rodarPreview() {
        const raca = el('f5e_raca').value;
        const classe = el('f5e_classe').value;
        if (!raca || !classe) return;
        try {
            const p = await rs.calcularAtributos(payloadCalcular());
            aplicarPreview(p);
            if (inventarioPanel) {
                inventarioPanel.renderTudo(fichaProgressaoLocal.feats);
                await inventarioPanel.atualizarResumoEquipamento(p);
            }
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
        fichaProgressaoLocal.metodo_atributos = 'padrao';
        ABILITIES.forEach((a, i) => {
            el(`base_${a.key}`).value = String(MATRIZ_PADRAO[i]);
        });
        agendarPreview();
    }

    async function aplicarGeracaoAtributos(metodo) {
        try {
            const data = await rs.gerarAtributos({ metodo });
            fichaProgressaoLocal.metodo_atributos = data.metodo || metodo;
            const scores = data.scores_base || {};
            const maxBase = metodo === '4d6' ? 18 : 15;
            const minBase = metodo === '4d6' ? 3 : 8;
            ABILITIES.forEach((a) => {
                const inp = el(`base_${a.key}`);
                if (!inp) return;
                inp.min = String(minBase);
                inp.max = String(maxBase);
                inp.value = String(scores[a.key] ?? 10);
            });
            agendarPreview();
            if (metodo === 'pontos') {
                Toast.success('Compra de pontos: ajuste os valores (máx. 27 pts).');
            }
        } catch (e) {
            Toast.error(e.message || 'Erro ao gerar atributos');
        }
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
            v: 2,
            raca_slug: el('f5e_raca').value,
            raca_variante_slug: el('f5e_raca_variante')?.value || null,
            classe_slug: el('f5e_classe').value,
            antecedente_slug: el('f5e_antecedente').value || null,
            subclasse_slug: el('f5e_subclasse').value || null,
            metodo_atributos: fichaProgressaoLocal.metodo_atributos || 'padrao',
            scores_base: base,
            bonus_habilidade_extra: getBonusExtra(),
            bonus_atributo_feat: fichaProgressaoLocal.bonus_atributo_feat || {},
            progressao: fichaProgressaoLocal.progressao || { hp_rolls: [], marcos: [] },
            feats: fichaProgressaoLocal.feats || [],
            feat_escolhas: fichaProgressaoLocal.feat_escolhas || {},
            pericias_override: fichaProgressaoLocal.pericias_override || {},
            pericias_classe_escolhidas: getPericiasClasseEscolhidas(),
            pericia_racial_extra: el('f5e_pericia_racial').value || null,
            raca_variante_slug: el('f5e_raca_variante')?.value || null,
            ...(inventarioPanel
                ? inventarioPanel.getArmaduraEscudoParaCalcular()
                : {
                      armadura_slug: el('f5e_armadura')?.value || null,
                      escudo_slug: el('f5e_escudo')?.value || null,
                  }),
            inventario: inventarioPanel
                ? inventarioPanel.getInventarioParaFicha()
                : {},
            ...(inventarioPanel ? inventarioPanel.getAntecedenteMeta() : {}),
            ...(inventarioPanel ? inventarioPanel.getClasseOuroMeta() : {}),
            ...(inventarioPanel ? inventarioPanel.getClasseEquipMeta() : {}),
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
        if (Dnd5eRacaUtil.temVarianteEscolha(raca) && !el('f5e_raca_variante')?.value) {
            Toast.error(`Escolha ${Dnd5eRacaUtil.labelVariante(raca).toLowerCase()}.`);
            return false;
        }
        const ant = antecedenteSelecionado();
        if (
            ant &&
            ant.idiomas_qtd > 0 &&
            typeof Dnd5eIdiomasUtil !== 'undefined' &&
            !Dnd5eIdiomasUtil.validarEscolha(
                getIdiomasAntecedenteEscolhidos(),
                ant.idiomas_qtd,
                catalogoIdiomas
            )
        ) {
            Toast.error(`Escolha exatamente ${ant.idiomas_qtd} idioma(s) do antecedente.`);
            return false;
        }
        if (inventarioPanel && ant) {
            inventarioPanel.setIdiomasAntecedente(getIdiomasAntecedenteEscolhidos());
            inventarioPanel.setTracosAntecedente(getTracosAntecedenteEscolhidos());
        }
        if (
            ant &&
            typeof Dnd5eTracosUtil !== 'undefined' &&
            !Dnd5eTracosUtil.validarEscolha(getTracosAntecedenteEscolhidos(), ant.tracos_opcoes || {})
        ) {
            Toast.error('Escolha traço de personalidade, ideal, laço e fraqueza do antecedente.');
            return false;
        }
        if (el('f5e_raca').value === 'humano') {
            const marcos = fichaProgressaoLocal?.progressao?.marcos || [];
            const temFeatHumano = marcos.some(
                (m) => m.nivel === 1 && (m.tipo || '').toLowerCase() === 'feat' && m.slug
            );
            if (!temFeatHumano) {
                Toast.error(
                    'Humano exige talento no nível 1 — registre na seção Progressão.'
                );
                return false;
            }
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
            sincronizarXpComNivel();
            const preview = await rs.calcularAtributos(payloadCalcular());
            const eff = preview.scores_efetivos;
            const nivel = parseInt(el('f5e_nivel').value, 10) || 1;
            const hpMax =
                preview.hp_max_total && preview.hp_max_total > preview.hp_max_nivel_1
                    ? preview.hp_max_total
                    : preview.hp_max_nivel_1;
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
                xpSalvoNoServidor = parseInt(el('f5e_xp').value, 10) || 0;
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
    }

    async function carregarPersonagem(p) {
        if (p.tipo) tipoCriacao = p.tipo;
        el('f5e_nome').value = p.nome || '';
        el('f5e_jogador').value = p.jogador_nome || nomeJogadorLogado();
        el('f5e_nivel').value = p.nivel;
        el('f5e_xp').value = p.experiencia;
        xpSalvoNoServidor = parseInt(p.experiencia, 10) || 0;
        sincronizarXpComNivel();
        sincronizarXpAoCarregar();
        el('f5e_hp_atual').value = p.hp_atual;
        el('f5e_hp_atual').dataset.userTouched = '1';

        const f = p.ficha || {};
        fichaProgressaoLocal = {
            metodo_atributos: f.metodo_atributos || 'padrao',
            progressao: f.progressao || { hp_rolls: [], marcos: [] },
            feats: f.feats || [],
            feat_escolhas: f.feat_escolhas || {},
            bonus_atributo_feat: f.bonus_atributo_feat || {},
            pericias_override: f.pericias_override || {},
            expertise_pericias: f.expertise_pericias || [],
        };
        if (progressaoPanel) {
            progressaoPanel.loadFromFicha(f);
            progressaoPanel.refreshPendencias();
        }
        arenaCondicoesAtual = CU.normalizarLista(f.arena_condicoes || []);
        sincronizarCondicoesPorHp();
        if (f.raca_slug) el('f5e_raca').value = f.raca_slug;
        atualizarUiRaca();
        if (f.raca_variante_slug) el('f5e_raca_variante').value = f.raca_variante_slug;
        if (f.classe_slug) el('f5e_classe').value = f.classe_slug;
        if (f.antecedente_slug) el('f5e_antecedente').value = f.antecedente_slug;
        if (inventarioPanel) {
            inventarioPanel.loadFromFicha(f, fichaProgressaoLocal.feats);
            const antSlug = f.antecedente_slug || el('f5e_antecedente').value || null;
            if (
                antSlug &&
                String(f.antecedente_inventario_slug || '') !== String(antSlug)
            ) {
                const ant =
                    catalogoAntecedentes.find((a) => a.slug === antSlug) || null;
                inventarioPanel.sincronizarAntecedente(antSlug, ant);
            }
            renderIdiomasAntecedente();
            renderTracosAntecedente(false);
            const antAtual = antecedenteSelecionado();
            if (antAtual) atualizarAntecedentePainel(antAtual, getTracosAntecedenteEscolhidos());
            if (
                f.classe_slug &&
                (!f.ouro_classe_aplicado ||
                    String(f.classe_ouro_slug || '') !== String(f.classe_slug))
            ) {
                await rolarESincronizarOuroClasse(true);
            }
            if (
                f.classe_slug &&
                (!f.classe_equip_aplicado ||
                    String(f.classe_equip_slug || '') !== String(f.classe_slug))
            ) {
                await aplicarEquipamentoClasse(true);
            }
        }
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
        const xpNode = el('f5e_xp');
        if (xpNode) {
            xpNode.disabled = false;
            xpNode.readOnly = false;
            xpNode.removeAttribute('data-pre-cadastro-lock');
        }
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
        el('btnGerar4d6')?.addEventListener('click', () => aplicarGeracaoAtributos('4d6'));
        el('btnCompraPontos')?.addEventListener('click', () => aplicarGeracaoAtributos('pontos'));
        el('btnSalvar').addEventListener('click', salvar);

        el('f5e_btn_editar_pericias')?.addEventListener('click', abrirEditorPericias);
        el('f5e_btn_salvar_pericias')?.addEventListener('click', salvarPericiasOverride);
        el('f5e_btn_cancelar_pericias')?.addEventListener('click', cancelarEditorPericias);
        el('f5e_btn_salvar_expertise')?.addEventListener('click', salvarExpertisePericias);

        progressaoPanel = new Dnd5eProgressaoPanel({
            personagemService: ps,
            regrasService: rs,
            el,
            getPersonagemId: () => personagemId,
            getNivel: () => parseInt(el('f5e_nivel').value, 10) || 1,
            getRacaSlug: () => el('f5e_raca').value || '',
            getXp: () => parseInt(el('f5e_xp').value, 10) || 0,
            xpPrecisaSalvar: () => {
                const xp = parseInt(el('f5e_xp').value, 10) || 0;
                return xp !== xpSalvoNoServidor;
            },
            onFichaAtualizada: (res) => {
                const ficha = res.ficha || res;
                if (res.hp_max != null) {
                    el('f5e_hp_max').textContent = String(res.hp_max);
                }
                if (res.hp_atual != null) {
                    el('f5e_hp_atual').value = String(res.hp_atual);
                    const hpMax =
                        parseInt(el('f5e_hp_max').textContent, 10) || res.hp_max || 1;
                    atualizarBarraPv(res.hp_atual, hpMax);
                }
                if (ficha.progressao) {
                    fichaProgressaoLocal.progressao = ficha.progressao;
                }
                if (ficha.feats) {
                    fichaProgressaoLocal.feats = ficha.feats;
                    inventarioPanel?.renderTalentos(ficha.feats);
                }
                if (ficha.bonus_atributo_feat) {
                    fichaProgressaoLocal.bonus_atributo_feat = ficha.bonus_atributo_feat;
                }
                if (ficha.feat_escolhas) {
                    fichaProgressaoLocal.feat_escolhas = ficha.feat_escolhas;
                }
                if (ficha.pericias_override) {
                    fichaProgressaoLocal.pericias_override = ficha.pericias_override;
                }
                if (ficha.expertise_pericias) {
                    fichaProgressaoLocal.expertise_pericias = ficha.expertise_pericias;
                    expertiseLocal = [...ficha.expertise_pericias];
                }
                agendarPreview();
            },
        });
        await progressaoPanel.init();

        inventarioPanel = new Dnd5eFichaInventarioPanel({
            el,
            regrasService: rs,
            onChange: agendarPreview,
            getPreview: () => previewAtual,
            onRolarOuroClasse: (forcar) => rolarESincronizarOuroClasse(forcar),
            onAplicarEquipClasse: (forcar) => aplicarEquipamentoClasse(forcar),
        });
        await inventarioPanel.init();
        el('f5e_raca').addEventListener('change', () => {
            atualizarUiRaca();
            atualizarHeaderIdentidade();
            agendarPreview();
        });
        el('f5e_classe').addEventListener('change', () => {
            renderPericiasEscolha();
            atualizarSubclasses();
            atualizarHeaderIdentidade();
            rolarESincronizarOuroClasse(true);
            aplicarEquipamentoClasse(true);
            if (typeof window.__dnd5eAtualizarSecaoMagias === 'function') {
                window.__dnd5eAtualizarSecaoMagias();
            }
            agendarPreview();
        });
        el('f5e_nivel').addEventListener('change', aoAlterarNivel);
        el('f5e_nivel').addEventListener('input', aoAlterarNivel);
        el('f5e_xp').addEventListener('input', () => {
            sincronizarNivelComXp();
            atualizarPendenciasLocais();
        });
        el('f5e_xp').addEventListener('change', () => {
            sincronizarNivelComXp();
            atualizarPendenciasLocais();
        });
        el('f5e_antecedente').addEventListener('change', () => {
            sincronizarAntecedenteInventario();
            agendarPreview();
        });
        el('f5e_extra1').addEventListener('change', agendarPreview);
        el('f5e_extra2').addEventListener('change', agendarPreview);
        el('f5e_pericia_racial').addEventListener('change', agendarPreview);
        el('f5e_raca_variante')?.addEventListener('change', agendarPreview);
        el('f5e_subclasse').addEventListener('change', agendarPreview);
        el('f5e_hp_atual').addEventListener('input', () => {
            el('f5e_hp_atual').dataset.userTouched = '1';
            const hpMax = parseInt(el('f5e_hp_max').textContent, 10) || 1;
            atualizarBarraPv(parseInt(el('f5e_hp_atual').value, 10), hpMax);
            agendarSyncHpCondicoes();
        });
        el('f5e_nome').addEventListener('input', atualizarHeaderIdentidade);
        configurarUploadFoto();
        el('f5e_btn_repouso_longo')?.addEventListener('click', aplicarRepousoLongo);

        try {
            const carregarIdiomas =
                typeof rs.idiomas === 'function'
                    ? rs.idiomas()
                    : Promise.resolve({ idiomas: window.__dnd5eCatalogoIdiomas || [] });
            const [racas, classes, ant, per, idiomas, combateMeta] = await Promise.all([
                rs.racas(),
                rs.classes(),
                rs.antecedentes(),
                rs.pericias(),
                carregarIdiomas,
                rs.combate().catch(() => ({ condicoes: [] })),
            ]);
            catalogoCondicoes = combateMeta.condicoes || [];
            catalogoRacas = racas.racas || [];
            catalogoClasses = classes.classes || [];
            catalogoAntecedentes = ant.antecedentes || [];
            catalogoPericias = per.pericias || [];
            catalogoIdiomas = idiomas.idiomas || [];
            window.__dnd5eCatalogoIdiomas = catalogoIdiomas;
            if (typeof Dnd5eXpUtil !== 'undefined' && classes.xp_por_nivel) {
                Dnd5eXpUtil.setTabela(classes.xp_por_nivel);
            }
            preencherSelects();
            preencherSelectExtra();
            atualizarUiRaca();
            renderPericiasEscolha();

            if (personagemId) {
                const p = await ps.obter(personagemId);
                await carregarPersonagem(p);
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
