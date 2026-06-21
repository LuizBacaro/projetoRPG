/**
 * Modal de pré-cadastro D&D 5e (dashboard) — identidade, atributos e combos raça/classe.
 */
class Dnd5ePreCadastroModal {
    constructor() {
        this.ABILITIES = [
            { key: 'strength', label: 'FOR', name: 'Força' },
            { key: 'dexterity', label: 'DES', name: 'Destreza' },
            { key: 'constitution', label: 'CON', name: 'Constituição' },
            { key: 'intelligence', label: 'INT', name: 'Inteligência' },
            { key: 'wisdom', label: 'SAB', name: 'Sabedoria' },
            { key: 'charisma', label: 'CAR', name: 'Carisma' },
        ];
        this.MATRIZ_PADRAO = [15, 14, 13, 12, 10, 8];
        this.ps = new Dnd5ePersonagemService();
        this.rs = new Dnd5eRegrasService();
        this.tipoAtual = 'jogador';
        this.catalogoRacas = [];
        this.catalogoClasses = [];
        this.catalogoAntecedentes = [];
        this.catalogoPericias = [];
        this.catalogoIdiomas = [];
        this.armaduras = [];
        this.escudos = [];
        this.debounceTimer = null;
        this._inicializado = false;
        this._syncXpEmAndamento = false;
        this.hpRollsCache = {};
        this.lastConMod = 0;
        this.classeOuroMeta = {
            slug: null,
            ouro_aplicado: 0,
            rolagem: [],
            formula: '',
        };
        this.idiomasAntecedente = [];
        this.tracosAntecedente = null;
    }

    el(id) {
        return document.getElementById(id);
    }

    fmtMod(n) {
        const v = Number(n);
        if (!Number.isFinite(v)) return '—';
        return v >= 0 ? `+${v}` : String(v);
    }

    formatHpDetalhe(resumo) {
        if (!resumo?.niveis?.length) return '';
        const linhas = resumo.niveis.map((n) => {
            const modStr = this.fmtMod(n.con_mod);
            const partes = [`${resumo.dado_vida}(${n.roll})`, `CON(${modStr})`];
            if (resumo.bonus_racial_por_nivel) {
                partes.push(`raça(+${resumo.bonus_racial_por_nivel})`);
            }
            return `Nív. ${n.nivel}: ${partes.join(' + ')} = ${n.subtotal} PV`;
        });
        const total = resumo.total != null ? ` · Total: ${resumo.total} PV` : '';
        return `${linhas.join(' · ')}${total}`;
    }

    nivelAtual() {
        return Math.max(1, Math.min(20, parseInt(this.el('prec_nivel')?.value, 10) || 1));
    }

    salvarHpRollsNoCache() {
        const host = this.el('prec_hp_rolls_host');
        if (!host) return;
        host.querySelectorAll('[data-hp-nivel]').forEach((inp) => {
            const nivel = parseInt(inp.dataset.hpNivel, 10);
            const val = parseInt(inp.value, 10);
            if (Number.isFinite(nivel) && Number.isFinite(val) && val > 0) {
                this.hpRollsCache[nivel] = val;
            }
        });
    }

    renderHpRolls() {
        const host = this.el('prec_hp_rolls_host');
        const titulo = this.el('prec_hp_sec_titulo');
        const hint = this.el('prec_hp_hint');
        if (!host) return;

        this.salvarHpRollsNoCache();
        const nivel = this.nivelAtual();

        if (titulo) {
            titulo.textContent =
                nivel === 1
                    ? '❤️ Pontos de Vida (nível 1)'
                    : `❤️ Pontos de Vida (níveis 1–${nivel})`;
        }
        if (hint) {
            hint.textContent =
                'Informe os PV ganhos em cada nível (valor livre — normalmente dado de vida + CON).';
        }

        const linhas = [];
        for (let n = 1; n <= nivel; n += 1) {
            const id = `prec_hp_roll_${n}`;
            const cached = this.hpRollsCache[n];
            const valor = Number.isFinite(cached) && cached > 0 ? String(cached) : '';
            linhas.push(`
                <div class="dnd5e-prec-hp-roll-row">
                    <label class="ficha-label" for="${id}">PV nível ${n}</label>
                    <input type="number" min="1" id="${id}" data-hp-nivel="${n}"
                        value="${valor}" placeholder="ex.: ${n === 1 ? 12 : 7}"
                        title="Pontos de vida ganhos no nível ${n}" />
                </div>`);
        }
        host.innerHTML = linhas.join('');
        host.querySelectorAll('input[data-hp-nivel]').forEach((inp) => {
            inp.addEventListener('input', () => this.agendarPreview());
        });
    }

    getHpRollsFromInputs() {
        const host = this.el('prec_hp_rolls_host');
        if (!host) return [];
        const out = [];
        host.querySelectorAll('[data-hp-nivel]').forEach((inp) => {
            const nivel = parseInt(inp.dataset.hpNivel, 10);
            const roll = parseInt(inp.value, 10);
            if (Number.isFinite(nivel) && Number.isFinite(roll) && roll > 0) {
                out.push({ nivel, roll });
            }
        });
        return out.sort((a, b) => a.nivel - b.nivel);
    }

    buildProgressaoHp(conMod = 0) {
        const mod = Number.isFinite(conMod) ? conMod : 0;
        const rolls = this.getHpRollsFromInputs();
        if (!rolls.length) return null;
        return {
            hp_rolls: rolls.map(({ nivel, roll: ganhoPv }) => {
                const ganho = Math.max(1, ganhoPv);
                return {
                    nivel,
                    roll: Math.max(1, ganho - mod),
                    con_mod: mod,
                    ganho,
                    usar_media: false,
                };
            }),
            marcos: [],
        };
    }

    nomeJogadorLogado() {
        if (typeof AuthService.getNome === 'function') return AuthService.getNome();
        return '';
    }

    async init() {
        if (this._inicializado) return;
        this._inicializado = true;
        this.renderAbilities();
        this.el('prec_jogador').value = this.nomeJogadorLogado();
        this.el('btnPrecMatriz').addEventListener('click', () => this.aplicarMatrizPadrao());
        this.el('prec_btn_rolar_ouro')?.addEventListener('click', () => this.rolarOuroClasse(true));
        this.el('formPrecadastro').addEventListener('submit', (e) => {
            e.preventDefault();
            this.cadastrar();
        });
        [
            'prec_raca',
            'prec_classe',
            'prec_nivel',
            'prec_antecedente',
            'prec_subclasse',
            'prec_armadura',
            'prec_escudo',
            'prec_extra1',
            'prec_extra2',
            'prec_pericia_racial',
        ].forEach((id) => {
            this.el(id)?.addEventListener('change', () => {
                if (id === 'prec_raca') this.atualizarUiRaca();
                if (id === 'prec_classe') {
                    this.renderPericiasEscolha();
                    this.atualizarSubclasses();
                    this.atualizarOuroFormula();
                    this.rolarOuroClasse(true);
                }
                if (id === 'prec_antecedente') {
                    this.renderOuroResumo();
                    this.renderIdiomasAntecedente(true);
                    this.renderTracosAntecedente(true);
                }
                if (id === 'prec_nivel') {
                    this.sincronizarXpComNivel();
                    this.renderHpRolls();
                    this.atualizarSubclasses();
                }
                this.agendarPreview();
            });
        });
        this.el('prec_xp')?.addEventListener('input', () => this.sincronizarNivelComXp());
        this.el('prec_xp')?.addEventListener('change', () => this.sincronizarNivelComXp());
        this.el('prec_nivel')?.addEventListener('input', () => {
            this.sincronizarXpComNivel();
            this.renderHpRolls();
            this.atualizarSubclasses();
            this.agendarPreview();
        });
        this.el('btnFecharPrecadastro')?.addEventListener('click', () => this.fechar());
        this.el('btnCancelarPrecadastro')?.addEventListener('click', () => this.fechar());
        this.el('modalPrecadastro')?.addEventListener('click', (e) => {
            if (e.target.id === 'modalPrecadastro') this.fechar();
        });
        document.getElementById('btnNovoJogador')?.addEventListener('click', () => this.abrir('jogador'));
        document.getElementById('btnNovoMonstro')?.addEventListener('click', () => this.abrir('monstro'));
        document.getElementById('btnNovoNpc')?.addEventListener('click', () => this.abrir('npc'));

        try {
            const carregarIdiomas =
                typeof this.rs.idiomas === 'function'
                    ? this.rs.idiomas()
                    : Promise.resolve({ idiomas: window.__dnd5eCatalogoIdiomas || [] });
            const [racas, classes, ant, per, equip, idiomas] = await Promise.all([
                this.rs.racas(),
                this.rs.classes(),
                this.rs.antecedentes(),
                this.rs.pericias(),
                this.rs.equipamento(),
                carregarIdiomas,
            ]);
            this.catalogoRacas = racas.racas || [];
            this.catalogoClasses = classes.classes || [];
            this.catalogoAntecedentes = ant.antecedentes || [];
            this.catalogoPericias = per.pericias || [];
            this.catalogoIdiomas = idiomas.idiomas || [];
            window.__dnd5eCatalogoIdiomas = this.catalogoIdiomas;
            this.armaduras = equip.armaduras || [];
            this.escudos = equip.escudos || [];
            if (typeof Dnd5eXpUtil !== 'undefined' && classes.xp_por_nivel) {
                Dnd5eXpUtil.setTabela(classes.xp_por_nivel);
            }
            this.preencherSelects();
            this.preencherSelectExtra();
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro ao carregar catálogos');
        }
    }

    renderAbilities() {
        const host = this.el('prec_abilities_circles');
        if (!host) return;
        const linhas = this.ABILITIES.map(
            (a) => `
            <tr data-ability="${a.key}">
                <td class="dnd5e-prec-attr-id">
                    <span class="dnd5e-prec-attr-abbr">${a.label}</span>
                    <span class="dnd5e-prec-attr-nome">${a.name}</span>
                </td>
                <td class="col-num">
                    <input type="number" min="8" max="15" id="prec_base_${a.key}" value="10"
                        class="dnd5e-prec-input-num" aria-label="${a.name} base" />
                </td>
                <td class="col-num dnd5e-prec-attr-total" id="prec_eff_${a.key}">10</td>
                <td class="col-num dnd5e-prec-attr-mod" id="prec_mod_${a.key}">+0</td>
            </tr>`
        ).join('');
        host.innerHTML = `
            <div class="dnd5e-prec-tabela-wrap">
                <table class="dnd5e-prec-tabela dnd5e-prec-atributos-tabela">
                    <thead>
                        <tr>
                            <th scope="col">Atributo</th>
                            <th scope="col" class="col-num">Base</th>
                            <th scope="col" class="col-num">Total</th>
                            <th scope="col" class="col-num">Mod.</th>
                        </tr>
                    </thead>
                    <tbody>${linhas}</tbody>
                </table>
            </div>`;
        this.ABILITIES.forEach((a) => {
            this.el(`prec_base_${a.key}`).addEventListener('input', () => this.agendarPreview());
        });
    }

    aplicarAtributosNeutros() {
        this.ABILITIES.forEach((a) => {
            this.el(`prec_base_${a.key}`).value = '10';
        });
        this.agendarPreview();
    }

    aplicarMatrizPadrao() {
        this.ABILITIES.forEach((a, i) => {
            this.el(`prec_base_${a.key}`).value = String(this.MATRIZ_PADRAO[i]);
        });
        this.agendarPreview();
    }

    getScoresBase() {
        const out = {};
        this.ABILITIES.forEach((a) => {
            out[a.key] = parseInt(this.el(`prec_base_${a.key}`).value, 10) || 10;
        });
        return out;
    }

    antecedenteSelecionado() {
        const slug = this.el('prec_antecedente').value || null;
        if (!slug) return null;
        return this.catalogoAntecedentes.find((a) => a.slug === slug) || null;
    }

    getIdiomasAntecedenteEscolhidos() {
        if (typeof Dnd5eIdiomasUtil === 'undefined') return this.idiomasAntecedente;
        const fromDom = Dnd5eIdiomasUtil.getEscolhidosDoHost(
            this.el('prec_antecedente_idiomas_host'),
            'prec-idioma'
        );
        return fromDom.length ? fromDom : this.idiomasAntecedente;
    }

    renderIdiomasAntecedente(reset = false) {
        const wrap = this.el('prec_antecedente_idiomas_wrap');
        const host = this.el('prec_antecedente_idiomas_host');
        const hint = this.el('prec_antecedente_idiomas_hint');
        const ant = this.antecedenteSelecionado();
        if (!wrap || !host || typeof Dnd5eIdiomasUtil === 'undefined') return;
        if (!ant || !(ant.idiomas_qtd > 0)) {
            wrap.hidden = true;
            host.innerHTML = '';
            this.idiomasAntecedente = [];
            return;
        }
        wrap.hidden = false;
        if (reset) this.idiomasAntecedente = [];
        Dnd5eIdiomasUtil.renderEscolha({
            host,
            hint,
            catalogo: this.catalogoIdiomas,
            qtd: ant.idiomas_qtd,
            selecionados: this.idiomasAntecedente,
            idPrefix: 'prec-idioma',
            onChange: (idiomas) => {
                this.idiomasAntecedente = idiomas;
            },
        });
    }

    getTracosAntecedenteEscolhidos() {
        if (typeof Dnd5eTracosUtil === 'undefined') return this.tracosAntecedente;
        const ant = this.antecedenteSelecionado();
        const fromDom = Dnd5eTracosUtil.getEscolhidosDoHost(
            this.el('prec_antecedente_tracos_host')
        );
        if (fromDom && Dnd5eTracosUtil.tracosEstaoCompletos(fromDom)) return fromDom;
        if (this.tracosAntecedente && ant?.tracos_opcoes) {
            return Dnd5eTracosUtil.normalizarEscolhidos(
                this.tracosAntecedente,
                ant.tracos_opcoes
            );
        }
        return fromDom;
    }

    renderTracosAntecedente(reset = false) {
        const wrap = this.el('prec_antecedente_tracos_wrap');
        const host = this.el('prec_antecedente_tracos_host');
        const hint = this.el('prec_antecedente_tracos_hint');
        const btn = this.el('prec_antecedente_tracos_sortear');
        const ant = this.antecedenteSelecionado();
        if (!wrap || !host || typeof Dnd5eTracosUtil === 'undefined') return;
        if (!ant) {
            wrap.hidden = true;
            host.innerHTML = '';
            this.tracosAntecedente = null;
            return;
        }
        wrap.hidden = false;
        if (reset) this.tracosAntecedente = null;
        Dnd5eTracosUtil.renderEscolha({
            host,
            hint,
            btnSortear: btn,
            opcoes: ant.tracos_opcoes || {},
            selecionados: reset ? null : this.tracosAntecedente,
            idPrefix: 'prec-traco',
            onChange: (tracos) => {
                this.tracosAntecedente = tracos;
            },
        });
    }

    classeSelecionada() {
        return this.catalogoClasses.find((c) => c.slug === this.el('prec_classe').value);
    }

    atualizarOuroFormula() {
        const elFormula = this.el('prec_ouro_formula');
        if (!elFormula) return;
        const classe = this.classeSelecionada();
        if (!classe) {
            elFormula.textContent = 'Selecione uma classe.';
            return;
        }
        const formula = classe.ouro_inicial_formula || '—';
        elFormula.textContent = `Fórmula PHB: ${formula}`;
    }

    renderOuroResumo(roll) {
        const host = this.el('prec_ouro_resultado');
        if (!host) return;
        const antSlug = this.el('prec_antecedente').value || null;
        const ant = antSlug
            ? this.catalogoAntecedentes.find((a) => a.slug === antSlug)
            : null;
        const antOuro = Number(ant?.ouro_po ?? ant?.ouro_extra) || 0;
        const classeOuro = this.classeOuroMeta.ouro_aplicado || 0;
        const partes = [];
        if (roll && typeof Dnd5eOuroClasseUtil !== 'undefined') {
            partes.push(`Classe: ${Dnd5eOuroClasseUtil.formatRollHint(roll)}`);
        } else if (classeOuro > 0) {
            partes.push(`Classe: ${classeOuro} gp`);
        }
        if (antOuro > 0) partes.push(`Antecedente: +${antOuro} gp`);
        if (classeOuro > 0 || antOuro > 0) {
            partes.push(`Total inicial: ${classeOuro + antOuro} gp`);
        }
        host.textContent = partes.join(' · ');
    }

    async rolarOuroClasse(forcar = false) {
        const slug = this.el('prec_classe').value;
        if (!slug) return;
        if (
            !forcar &&
            this.classeOuroMeta.slug === slug &&
            this.classeOuroMeta.ouro_aplicado > 0
        ) {
            this.renderOuroResumo({
                total: this.classeOuroMeta.ouro_aplicado,
                dados: this.classeOuroMeta.rolagem,
                formula: this.classeOuroMeta.formula,
                multiplicador: 1,
            });
            return;
        }
        const btn = this.el('prec_btn_rolar_ouro');
        if (btn) btn.disabled = true;
        try {
            const roll = await this.rs.rolarOuroClasse({ classe_slug: slug });
            this.classeOuroMeta = {
                slug,
                ouro_aplicado: Number(roll.total) || 0,
                rolagem: roll.dados || [],
                formula: roll.formula || '',
            };
            this.renderOuroResumo(roll);
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro ao rolar ouro');
        } finally {
            if (btn) btn.disabled = false;
        }
    }

    racaSelecionada() {
        return this.catalogoRacas.find((r) => r.slug === this.el('prec_raca').value);
    }

    getBonusExtra() {
        if (!Dnd5eRacaUtil.temBonusHabilidadeExtraEscolha(this.racaSelecionada())) return {};
        const k1 = this.el('prec_extra1').value;
        const k2 = this.el('prec_extra2').value;
        const out = {};
        if (k1) out[k1] = (out[k1] || 0) + 1;
        if (k2 && k2 !== k1) out[k2] = (out[k2] || 0) + 1;
        return out;
    }

    getPericiasClasseEscolhidas() {
        return Array.from(
            document.querySelectorAll('#prec_pericias_escolha input[type=checkbox]:checked')
        ).map((cb) => cb.value);
    }

    sincronizarXpComNivel() {
        if (typeof Dnd5eXpUtil === 'undefined' || this._syncXpEmAndamento) return;
        this._syncXpEmAndamento = true;
        Dnd5eXpUtil.aplicarNivelParaXp(this.el('prec_nivel'), this.el('prec_xp'));
        this._syncXpEmAndamento = false;
    }

    sincronizarNivelComXp() {
        if (typeof Dnd5eXpUtil === 'undefined' || this._syncXpEmAndamento) return;
        this._syncXpEmAndamento = true;
        const novoNivel = Dnd5eXpUtil.aplicarXpParaNivel(this.el('prec_xp'), this.el('prec_nivel'));
        this._syncXpEmAndamento = false;
        if (novoNivel != null) {
            this.atualizarSubclasses();
            this.agendarPreview();
        }
    }

    subclasseValidaParaPreview() {
        const sub = this.el('prec_subclasse')?.value;
        if (!sub) return null;
        const nivel = parseInt(this.el('prec_nivel').value, 10) || 1;
        const opt = this.el('prec_subclasse')?.selectedOptions?.[0];
        const match = opt?.textContent?.match(/nív\.\s*(\d+)/i);
        const minNivel = match ? parseInt(match[1], 10) : 3;
        return nivel >= minNivel ? sub : null;
    }

    payloadCalcular() {
        const body = {
            raca_slug: this.el('prec_raca').value,
            classe_slug: this.el('prec_classe').value,
            antecedente_slug: this.el('prec_antecedente').value || null,
            scores_base: this.getScoresBase(),
            bonus_habilidade_extra: this.getBonusExtra(),
            nivel: parseInt(this.el('prec_nivel').value, 10) || 1,
            pericias_classe_escolhidas: this.getPericiasClasseEscolhidas(),
            pericia_racial_extra: this.el('prec_pericia_racial').value || null,
            subclasse_slug: this.subclasseValidaParaPreview(),
            armadura_slug: this.el('prec_armadura').value || null,
            escudo_slug: this.el('prec_escudo').value || null,
        };
        const progressao = this.buildProgressaoHp(this.lastConMod);
        if (progressao) body.progressao = progressao;
        return body;
    }

    periciaNome(slug) {
        const p = this.catalogoPericias.find((x) => x.slug === slug);
        return p ? p.nome : slug;
    }

    preencherSelects() {
        this.el('prec_raca').innerHTML = this.catalogoRacas
            .map((r) => `<option value="${r.slug}">${r.nome}</option>`)
            .join('');
        this.el('prec_classe').innerHTML = this.catalogoClasses
            .map((c) => `<option value="${c.slug}">${c.nome} (${c.dado_vida})</option>`)
            .join('');
        this.el('prec_antecedente').innerHTML =
            '<option value="">—</option>' +
            this.catalogoAntecedentes
                .map((a) => `<option value="${a.slug}">${a.nome}</option>`)
                .join('');
        this.el('prec_armadura').innerHTML =
            '<option value="">Sem armadura</option>' +
            this.armaduras
                .map((a) => `<option value="${a.slug}">${a.nome} (CA ${a.ca})</option>`)
                .join('');
        this.el('prec_escudo').innerHTML =
            '<option value="">Nenhum</option>' +
            this.escudos
                .map((s) => `<option value="${s.slug}">${s.nome} (+${s.bonus_ac})</option>`)
                .join('');
    }

    preencherSelectExtra() {
        const opts = this.ABILITIES.map(
            (a) => `<option value="${a.key}">${a.name}</option>`
        ).join('');
        this.el('prec_extra1').innerHTML = opts;
        this.el('prec_extra2').innerHTML = opts;
        this.el('prec_extra2').value = 'wisdom';
        const perOpts =
            '<option value="">—</option>' +
            this.catalogoPericias
                .map((p) => `<option value="${p.slug}">${p.nome}</option>`)
                .join('');
        this.el('prec_pericia_racial').innerHTML = perOpts;
    }

    atualizarUiRaca() {
        const raca = this.racaSelecionada();
        const tracos = this.el('prec_tracos');
        const extra = this.el('prec_raca_extra');
        if (raca && raca.tracos_resumo) {
            tracos.textContent = raca.tracos_resumo;
            tracos.hidden = false;
        } else {
            tracos.hidden = true;
        }
        extra?.classList.toggle(
            'is-visible',
            Dnd5eRacaUtil.temBonusHabilidadeExtraEscolha(raca)
        );
        Dnd5eRacaUtil.atualizarLabelsBonusExtra(
            raca,
            ['prec_extra1_label', 'prec_extra2_label'],
            (id) => this.el(id)
        );
        const temPericiaExtra =
            raca &&
            Array.isArray(raca.caracteristicas) &&
            raca.caracteristicas.includes('proficiencia_pericia_extra');
        this.el('prec_pericia_racial_wrap').hidden = !temPericiaExtra;
    }

    renderPericiasEscolha() {
        const classeSlug = this.el('prec_classe').value;
        const classe = this.catalogoClasses.find((c) => c.slug === classeSlug);
        const host = this.el('prec_pericias_escolha');
        const hint = this.el('prec_pericias_classe_hint');
        if (!classe) {
            host.innerHTML = '';
            hint.textContent = '';
            return;
        }
        const qtd = classe.pericias_escolha_qtd || 0;
        let pool = classe.pericias_escolha_de || [];
        if (!pool.length && qtd > 0) {
            pool = this.catalogoPericias.map((p) => p.slug);
        }
        if (!pool.length || qtd <= 0) {
            hint.textContent =
                qtd > 0
                    ? 'Nenhuma perícia disponível para esta classe.'
                    : 'Esta classe não exige escolha de perícias no nível 1.';
            host.innerHTML = '<p class="dnd5e-prec-vazio">—</p>';
            return;
        }
        this._periciasEscolhaQtd = qtd;
        this.atualizarHintPericias(0, qtd);
        const linhas = pool
            .map((slug) => {
                const nome = this.periciaNome(slug);
                const id = `prec_per_${slug}`;
                return `
            <tr class="dnd5e-prec-pericia-row" data-slug="${slug}">
                <td class="col-check">
                    <input type="checkbox" id="${id}" value="${slug}" aria-label="${nome}" />
                </td>
                <td>
                    <label for="${id}" class="dnd5e-prec-pericia-label">${nome}</label>
                </td>
            </tr>`;
            })
            .join('');
        host.innerHTML = `
            <div class="dnd5e-prec-tabela-wrap">
                <table class="dnd5e-prec-tabela dnd5e-prec-pericias-tabela">
                    <thead>
                        <tr>
                            <th scope="col" class="col-check" aria-label="Selecionar"></th>
                            <th scope="col">Perícia</th>
                        </tr>
                    </thead>
                    <tbody>${linhas}</tbody>
                </table>
            </div>`;
        host.querySelectorAll('tbody tr').forEach((row) => {
            const inp = row.querySelector('input[type=checkbox]');
            if (!inp) return;
            const syncRow = () => {
                row.classList.toggle('is-selected', inp.checked);
            };
            inp.addEventListener('change', () => {
                const sel = this.getPericiasClasseEscolhidas();
                if (sel.length > qtd) {
                    inp.checked = false;
                    Toast.error(`Máximo ${qtd} perícia(s) de classe.`);
                    syncRow();
                    return;
                }
                this.atualizarHintPericias(sel.length, qtd);
                syncRow();
                this.agendarPreview();
            });
            syncRow();
        });
    }

    atualizarHintPericias(selecionadas, total) {
        const hint = this.el('prec_pericias_classe_hint');
        if (!hint) return;
        if (!total) {
            hint.textContent = 'Esta classe não exige escolha de perícias no nível 1.';
            return;
        }
        hint.textContent = `Escolha ${total} perícia(s) de classe · ${selecionadas}/${total} selecionada(s)`;
        hint.classList.toggle('is-completo', selecionadas === total);
    }

    async atualizarSubclasses() {
        const classeSlug = this.el('prec_classe').value;
        const nivel = parseInt(this.el('prec_nivel').value, 10) || 1;
        const wrap = this.el('prec_subclasse_wrap');
        const select = this.el('prec_subclasse');
        const atual = select.value;
        if (!classeSlug) {
            wrap.hidden = true;
            return;
        }
        try {
            const data = await this.rs.subclasses(classeSlug);
            const subs = data.subclasses || [];
            const disponiveis = subs.filter((s) => nivel >= s.nivel_escolha);
            if (!disponiveis.length) {
                wrap.hidden = true;
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
        } catch {
            wrap.hidden = true;
        }
    }

    aplicarPreview(p) {
        if (p?.modificadores?.constitution != null) {
            this.lastConMod = p.modificadores.constitution;
        }
        this.ABILITIES.forEach((a) => {
            this.el(`prec_mod_${a.key}`).textContent = this.fmtMod(p.modificadores[a.key]);
            this.el(`prec_eff_${a.key}`).textContent = String(p.scores_efetivos[a.key]);
        });
        const dadoEl = this.el('prec_hp_dado');
        if (dadoEl && p.classe?.dado_vida) {
            dadoEl.textContent = p.classe.dado_vida;
        }
        const hpDet = this.el('prec_hp_detalhe');
        if (hpDet) {
            hpDet.textContent = p.hp_resumo ? this.formatHpDetalhe(p.hp_resumo) : '';
        }
        const resumo = this.el('prec_preview_resumo');
        if (resumo) {
            const pv =
                p.hp_max_total && p.hp_max_total > 0 ? p.hp_max_total : p.hp_max_nivel_1;
            resumo.textContent = `CA ${p.ca_total ?? p.ca_base} · PV ${pv} · Inic. ${this.fmtMod(p.iniciativa)}`;
        }
    }

    agendarPreview() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => this.rodarPreview(), 280);
    }

    async rodarPreview() {
        const raca = this.el('prec_raca').value;
        const classe = this.el('prec_classe').value;
        if (!raca || !classe) return;
        try {
            const p = await this.rs.calcularAtributos(this.payloadCalcular());
            this.aplicarPreview(p);
            this.el('prec_status').textContent = '';
        } catch (e) {
            this.el('prec_status').textContent = e.message || 'Erro no cálculo';
        }
    }

    validar() {
        const nome = this.el('prec_nome').value.trim();
        if (!nome) {
            Toast.error('Informe o nome do personagem.');
            return false;
        }
        if (!this.el('prec_raca').value || !this.el('prec_classe').value) {
            Toast.error('Selecione raça e classe.');
            return false;
        }
        const classe = this.catalogoClasses.find((c) => c.slug === this.el('prec_classe').value);
        const qtd = (classe && classe.pericias_escolha_qtd) || 0;
        const sel = this.getPericiasClasseEscolhidas();
        if (qtd > 0 && sel.length !== qtd) {
            Toast.error(`Escolha exatamente ${qtd} perícia(s) de classe.`);
            return false;
        }
        const raca = this.catalogoRacas.find((r) => r.slug === this.el('prec_raca').value);
        const precisaPericiaRacial =
            raca &&
            Array.isArray(raca.caracteristicas) &&
            raca.caracteristicas.includes('proficiencia_pericia_extra');
        if (precisaPericiaRacial && !this.el('prec_pericia_racial').value) {
            Toast.error('Escolha a perícia extra concedida pela raça.');
            return false;
        }
        const nivel = this.nivelAtual();
        const rolls = this.getHpRollsFromInputs();
        const faltando = [];
        for (let n = 1; n <= nivel; n += 1) {
            if (!rolls.some((r) => r.nivel === n)) faltando.push(n);
        }
        if (faltando.length) {
            Toast.error(
                faltando.length === 1
                    ? `Informe os PV do nível ${faltando[0]}.`
                    : `Informe os PV dos níveis: ${faltando.join(', ')}.`
            );
            return false;
        }
        const ant = this.antecedenteSelecionado();
        if (
            ant &&
            ant.idiomas_qtd > 0 &&
            typeof Dnd5eIdiomasUtil !== 'undefined' &&
            !Dnd5eIdiomasUtil.validarEscolha(
                this.getIdiomasAntecedenteEscolhidos(),
                ant.idiomas_qtd,
                this.catalogoIdiomas
            )
        ) {
            Toast.error(`Escolha exatamente ${ant.idiomas_qtd} idioma(s) do antecedente.`);
            return false;
        }
        if (
            ant &&
            typeof Dnd5eTracosUtil !== 'undefined' &&
            !Dnd5eTracosUtil.validarEscolha(
                this.getTracosAntecedenteEscolhidos(),
                ant.tracos_opcoes || {}
            )
        ) {
            Toast.error('Escolha traço de personalidade, ideal, laço e fraqueza do antecedente.');
            return false;
        }
        return true;
    }

    montarFichaJson(preview) {
        const base = this.getScoresBase();
        const f = {
            v: 1,
            raca_slug: this.el('prec_raca').value,
            classe_slug: this.el('prec_classe').value,
            antecedente_slug: this.el('prec_antecedente').value || null,
            subclasse_slug: this.el('prec_subclasse').value || null,
            scores_base: base,
            bonus_habilidade_extra: this.getBonusExtra(),
            pericias_classe_escolhidas: this.getPericiasClasseEscolhidas(),
            pericia_racial_extra: this.el('prec_pericia_racial').value || null,
            armadura_slug: this.el('prec_armadura').value || null,
            escudo_slug: this.el('prec_escudo').value || null,
            pre_cadastro_concluido: true,
        };
        if (preview) {
            f.ca_base = preview.ca_base;
            f.ca_total = preview.ca_total;
            f.pericias_proficientes = preview.pericias_proficientes;
            f.hp_max_nivel_1_ref = preview.hp_max_nivel_1;
            if (preview.subclasse) f.subclasse_nome = preview.subclasse.nome;
            const conMod = preview.modificadores?.constitution ?? 0;
            const progressao = this.buildProgressaoHp(conMod);
            if (progressao) f.progressao = progressao;
        }
        if (this.classeOuroMeta.ouro_aplicado > 0) {
            f.classe_ouro_slug = this.classeOuroMeta.slug;
            f.ouro_classe_aplicado = this.classeOuroMeta.ouro_aplicado;
            f.ouro_classe_rolagem = this.classeOuroMeta.rolagem;
            f.ouro_classe_formula = this.classeOuroMeta.formula;
            f.inventario = {
                ouro_po: this.classeOuroMeta.ouro_aplicado,
                equipamentos: [],
                consumiveis: [],
            };
        }
        const idiomas = this.getIdiomasAntecedenteEscolhidos();
        if (idiomas.length) {
            f.antecedente_idiomas = idiomas;
        }
        const tracos = this.getTracosAntecedenteEscolhidos();
        if (tracos && typeof Dnd5eTracosUtil !== 'undefined' && Dnd5eTracosUtil.tracosEstaoCompletos(tracos)) {
            f.antecedente_tracos = tracos;
        }
        f.arena_condicoes = [];
        return f;
    }

    async cadastrar() {
        if (!this.validar()) return;
        const btn = this.el('btnPrecadastroSalvar');
        btn.disabled = true;
        this.el('prec_status').textContent = 'Cadastrando…';
        try {
            const preview = await this.rs.calcularAtributos(this.payloadCalcular());
            const eff = preview.scores_efetivos;
            this.sincronizarXpComNivel();
            const nivel = parseInt(this.el('prec_nivel').value, 10) || 1;
            const hpMax =
                preview.hp_max_total && preview.hp_max_total > preview.hp_max_nivel_1
                    ? preview.hp_max_total
                    : preview.hp_max_nivel_1;
            const payload = {
                nome: this.el('prec_nome').value.trim(),
                jogador_nome: this.el('prec_jogador').value.trim() || null,
                nivel,
                experiencia: parseInt(this.el('prec_xp').value, 10) || 0,
                tipo: this.tipoAtual,
                strength: eff.strength,
                dexterity: eff.dexterity,
                constitution: eff.constitution,
                intelligence: eff.intelligence,
                wisdom: eff.wisdom,
                charisma: eff.charisma,
                hp_max: hpMax,
                hp_atual: hpMax,
                ficha: this.montarFichaJson(preview),
            };
            const criado = await this.ps.criar(payload);
            Toast.success(`${criado.nome} cadastrado.`);
            this.fechar();
            window.location.href = `ficha-personagem.html?id=${criado.id}`;
        } catch (e) {
            this.el('prec_status').textContent = '';
            Toast.error(e.message || 'Erro ao cadastrar');
        } finally {
            btn.disabled = false;
        }
    }

    resetForm() {
        this.el('formPrecadastro').reset();
        this.el('prec_jogador').value = this.nomeJogadorLogado();
        this.el('prec_nivel').value = '1';
        this.sincronizarXpComNivel();
        this.hpRollsCache = {};
        this.lastConMod = 0;
        this.classeOuroMeta = {
            slug: null,
            ouro_aplicado: 0,
            rolagem: [],
            formula: '',
        };
        this.idiomasAntecedente = [];
        this.tracosAntecedente = null;
        this.renderIdiomasAntecedente(true);
        this.renderTracosAntecedente(true);
        this.renderHpRolls();
        if (this.el('prec_ouro_resultado')) this.el('prec_ouro_resultado').textContent = '';
        this.atualizarOuroFormula();
        if (this.el('prec_hp_detalhe')) this.el('prec_hp_detalhe').textContent = '';
        this.aplicarAtributosNeutros();
        this.atualizarUiRaca();
        this.renderPericiasEscolha();
        this.el('prec_status').textContent = '';
    }

    abrir(tipo) {
        if (
            (tipo === 'monstro' || tipo === 'npc') &&
            typeof AuthService.isMestre === 'function' &&
            !AuthService.isMestre()
        ) {
            Toast.error('Apenas mestre pode criar monstro ou NPC.');
            return;
        }
        if (!this.catalogoRacas.length || !this.catalogoClasses.length) {
            Toast.error('Aguarde o carregamento dos catálogos.');
            return;
        }
        this.tipoAtual = tipo || 'jogador';
        const titulos = {
            jogador: '🧙 Novo jogador',
            monstro: '👹 Novo monstro',
            npc: '🤝 Novo NPC',
        };
        this.el('precadastroTitulo').textContent = titulos[this.tipoAtual] || titulos.jogador;
        this.resetForm();
        this.el('modalPrecadastro').classList.add('show');
        this.renderHpRolls();
        this.atualizarSubclasses();
        this.atualizarOuroFormula();
        this.rolarOuroClasse(true);
        this.renderIdiomasAntecedente(true);
        this.renderTracosAntecedente(true);
        this.rodarPreview();
    }

    fechar() {
        this.el('modalPrecadastro').classList.remove('show');
    }
}
