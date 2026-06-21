/**
 * Painel de progressão D&D 5e — PV por nível e marcos (incremento / talento).
 */
const ATTR_LABELS_PT = {
    strength: 'Força',
    dexterity: 'Destreza',
    constitution: 'Constituição',
    intelligence: 'Inteligência',
    wisdom: 'Sabedoria',
    charisma: 'Carisma',
};

const PENDENCIAS_UTIL = typeof Dnd5ePendenciasUtil !== 'undefined' ? Dnd5ePendenciasUtil : null;

const EXPERTISE_SLOTS_CLASSE = {
    ladino: [
        [1, 2],
        [6, 2],
    ],
    bardo: [
        [3, 2],
        [10, 2],
    ],
};

function formatDistribuicaoAsi(distribuicao) {
    const partes = Object.entries(distribuicao || {}).map(
        ([k, v]) => `${ATTR_LABELS_PT[k] || k} +${v}`
    );
    return partes.join(', ');
}

class Dnd5eProgressaoPanel {
    constructor(options) {
        this.ps = options.personagemService;
        this.rs = options.regrasService;
        this.el = options.el || ((id) => document.getElementById(id));
        this.getPersonagemId = options.getPersonagemId || (() => null);
        this.getNivel = options.getNivel || (() => 1);
        this.getXp = options.getXp || (() => 0);
        this.getRacaSlug = options.getRacaSlug || (() => '');
        this.getClasseSlug = options.getClasseSlug || (() => '');
        this.getExpertisePericias = options.getExpertisePericias || (() => []);
        this.getExpertiseSlotsClasse = options.getExpertiseSlotsClasse || null;
        this.getProgressao = options.getProgressao || (() => this._progCache || {});
        this.getNivelSalvo = options.getNivelSalvo || (() => this.getNivel());
        this.xpPrecisaSalvar = options.xpPrecisaSalvar || (() => false);
        this.onFichaAtualizada = options.onFichaAtualizada || (() => {});
        this.catalogoFeats = [];
        this.catalogoPericias = [];
        this.niveisFeat = [4, 8, 12, 16, 19];
        this._featEscolhasLocal = {};
        this._progCache = { hp_rolls: [], marcos: [] };
        this._featsCache = [];
    }

    async init() {
        try {
            const data = await this.rs.classes();
            this.niveisFeat = data.niveis_ganho_feat || this.niveisFeat;
            const [feats, per] = await Promise.all([
                this.rs.talentos(),
                this.rs.pericias(),
            ]);
            this.catalogoFeats = (feats.talentos || []).filter(
                (f) => f.slug !== 'ability-score-improvement'
            );
            this.catalogoPericias = per.pericias || [];
            this._preencherSkilledSelectOptions();
            this._preencherSkillExpertSelectOptions();
        } catch (_e) {
            /* offline */
        }
        this._bind();
    }

    _periciaNome(slug) {
        const p = this.catalogoPericias.find((x) => x.slug === slug);
        return p ? p.nome : slug;
    }

    _htmlOptsPericias() {
        const opts = (this.catalogoPericias || [])
            .map((p) => `<option value="${p.slug}">${p.nome}</option>`)
            .join('');
        return `<option value="">— escolha —</option>${opts}`;
    }

    _preencherSkilledSelectOptions() {
        const html = this._htmlOptsPericias();
        [1, 2, 3].forEach((i) => {
            const marco = this.el(`f5e_marco_feat_skilled_${i}`);
            const feat = this.el(`f5e_feat_escolha_skilled_${i}`);
            if (marco) marco.innerHTML = html;
            if (feat) feat.innerHTML = html;
        });
    }

    _preencherSkillExpertSelectOptions() {
        const html = this._htmlOptsPericias();
        ['f5e_marco_feat_skill_expert_nova', 'f5e_marco_feat_skill_expert_exp'].forEach((id) => {
            const sel = this.el(id);
            if (sel) sel.innerHTML = html;
        });
        ['f5e_feat_escolha_skill_expert_nova', 'f5e_feat_escolha_skill_expert_exp'].forEach((id) => {
            const sel = this.el(id);
            if (sel) sel.innerHTML = html;
        });
    }

    _preencherSkillExpertSelects(prefix, escolhas) {
        const nova = escolhas?.skill_expert_nova || escolhas?.skill_expert_pericia || '';
        const exp =
            escolhas?.skill_expert_expertise || escolhas?.skill_expert_especializacao || '';
        const selNova = this.el(`${prefix}_nova`);
        const selExp = this.el(`${prefix}_exp`);
        if (selNova) selNova.value = nova || '';
        if (selExp) selExp.value = exp || '';
    }

    _coletarSkillExpert(prefix) {
        const nova = this.el(`${prefix}_nova`)?.value || '';
        const exp = this.el(`${prefix}_exp`)?.value || '';
        const out = {};
        if (nova) out.skill_expert_nova = nova;
        if (exp) out.skill_expert_expertise = exp;
        return out;
    }

    _validarSkillExpert(escolhas) {
        if (!escolhas?.skill_expert_nova || !escolhas?.skill_expert_expertise) {
            return 'Especialista (Skill Expert) exige nova proficiência e perícia para expertise.';
        }
        return null;
    }

    _labelSkillExpertExtra(escolhas) {
        const nova = escolhas?.skill_expert_nova || escolhas?.skill_expert_pericia;
        const exp =
            escolhas?.skill_expert_expertise || escolhas?.skill_expert_especializacao;
        if (!nova || !exp) return '';
        return ` (${this._periciaNome(nova)} + exp. ${this._periciaNome(exp)})`;
    }

    _preencherSkilledSelects(prefix, slugs) {
        const lista = Array.isArray(slugs) ? slugs : [];
        [1, 2, 3].forEach((i) => {
            const sel = this.el(`${prefix}_${i}`);
            if (sel) sel.value = lista[i - 1] || '';
        });
    }

    _coletarSkilledSlugs(prefix) {
        return [1, 2, 3]
            .map((i) => this.el(`${prefix}_${i}`)?.value || '')
            .filter(Boolean);
    }

    _validarSkilledSlugs(slugs) {
        const list = slugs || [];
        if (list.length !== 3) {
            return 'Habilidoso (Skilled) exige exatamente 3 perícias.';
        }
        if (new Set(list).size !== 3) {
            return 'As 3 perícias do Habilidoso devem ser distintas.';
        }
        return null;
    }

    _labelSkilledExtra(escolhas) {
        const slugs = escolhas?.skilled_pericias || escolhas?.skilled;
        if (!Array.isArray(slugs) || !slugs.length) return '';
        const nomes = slugs.map((s) => this._periciaNome(s)).join(', ');
        return ` (${nomes})`;
    }

    loadFromFicha(ficha) {
        const f = ficha || {};
        const prog = f.progressao || { hp_rolls: [], marcos: [] };
        this._progCache = prog;
        this._featsCache = f.feats || [];
        this.renderPendenciasLocais(f.pendencias || []);
        this._renderHpRolls(prog.hp_rolls || []);
        this._renderMarcos(prog.marcos || [], f.feats || []);
        this._featEscolhasLocal = { ...(f.feat_escolhas || {}) };
        this._renderFeatEscolhasSection(f.feats || [], this._featEscolhasLocal);
    }

    _nivelEfetivo() {
        let n = Math.max(1, Math.min(20, parseInt(this.getNivel(), 10) || 1));
        if (typeof Dnd5eXpUtil !== 'undefined') {
            n = Math.max(n, Dnd5eXpUtil.nivelPorXp(this.getXp()));
        }
        return n;
    }

    _nivelSubiuPendente() {
        const atual = this._nivelEfetivo();
        const salvo = Math.max(1, parseInt(this.getNivelSalvo(), 10) || 1);
        return atual > salvo;
    }

    _dadosProgressaoLocal() {
        const prog = this.getProgressao?.() || this._progCache || {};
        return {
            hp_rolls: prog.hp_rolls || [],
            marcos: prog.marcos || [],
        };
    }

    _slotsExpertiseClasse(classeSlug, nivel) {
        if (typeof this.getExpertiseSlotsClasse === 'function') {
            const slots = this.getExpertiseSlotsClasse();
            if (Number.isFinite(slots)) return Math.max(0, slots);
        }
        const key = (classeSlug || '').toLowerCase();
        let total = 0;
        (EXPERTISE_SLOTS_CLASSE[key] || []).forEach(([min, qtd]) => {
            if (nivel >= min) total += qtd;
        });
        return total;
    }

    _pendenciasProgressaoLocal() {
        const nivel = this._nivelEfetivo();
        const raca = (this.getRacaSlug() || '').toLowerCase();
        const classe = (this.getClasseSlug() || '').toLowerCase();
        const { hp_rolls: hpRolls, marcos } = this._dadosProgressaoLocal();
        const hpNiveis = new Set(
            hpRolls.map((r) => parseInt(r.nivel, 10)).filter((n) => Number.isFinite(n))
        );
        const marcoNiveis = new Set(
            marcos.map((m) => parseInt(m.nivel, 10)).filter((n) => Number.isFinite(n))
        );
        const out = [];

        for (let n = 1; n <= nivel; n += 1) {
            if (!hpNiveis.has(n)) out.push(`hp_nivel_${n}`);
        }

        if (raca === 'humano' && nivel >= 1 && !marcoNiveis.has(1)) {
            out.push('feat_nivel_1');
        }

        this.niveisFeat.forEach((n) => {
            if (n <= nivel && !marcoNiveis.has(n)) {
                out.push(`marco_nivel_${n}`);
            }
        });

        out.push(...this._pendenciasFeatEscolhasLocal());

        const slotsExp = this._slotsExpertiseClasse(classe, nivel);
        const expertise = (this.getExpertisePericias() || []).filter(Boolean);
        if (slotsExp > 0 && expertise.length < slotsExp) {
            out.push('expertise_classe');
        }

        return out;
    }

    _pendenciasFeatEscolhasLocal() {
        const feats = (this._featsCache || []).map((f) => String(f).toLowerCase());
        const esc = this._featEscolhasLocal || {};
        const out = [];
        if (feats.includes('resilient') && !esc.resilient) {
            out.push('feat_escolha_resilient');
        }
        if (feats.includes('magic-initiate') && !esc.magic_initiate) {
            out.push('feat_escolha_magic_initiate');
        }
        if (feats.includes('skilled')) {
            const sl = esc.skilled_pericias || [];
            if (sl.length !== 3 || new Set(sl).size !== 3) {
                out.push('feat_escolha_skilled');
            }
        }
        if (feats.includes('skill-expert')) {
            if (!esc.skill_expert_nova || !esc.skill_expert_expertise) {
                out.push('feat_escolha_skill_expert');
            }
        }
        return out;
    }

    _pendenciasAcao(pendencias) {
        const merged = this._pendenciasMescladas(pendencias);
        return merged.filter((p) => {
            const cat = PENDENCIAS_UTIL ? PENDENCIAS_UTIL.categoria(p) : '';
            return cat === 'hp' || cat === 'marco' || cat === 'pericia';
        });
    }

    _deveExibirProgressao(pendenciasServidor) {
        if (this._pendenciasAcao(pendenciasServidor).length > 0) return true;
        return this._nivelSubiuPendente();
    }

    _htmlHpRolls(rolls) {
        if (!rolls.length) return '';
        return rolls
            .map((r) => {
                const mod = Number(r.con_mod);
                const modStr = mod >= 0 ? `+${mod}` : String(mod);
                return `<div class="ficha-dnd5e-progressao-item is-readonly">Nív. ${r.nivel}: dado(${r.roll}) CON(${modStr}) = +${r.ganho} PV</div>`;
            })
            .join('');
    }

    _htmlMarcos(marcos, feats) {
        const linhas = (marcos || []).map((m) => {
            if (m.tipo === 'asi') {
                const dist = formatDistribuicaoAsi(m.distribuicao);
                return `<div class="ficha-dnd5e-progressao-item is-readonly">Nív. ${m.nivel}: Incremento (${dist})</div>`;
            }
            const feat = this.catalogoFeats.find((f) => f.slug === m.slug);
            let extra = '';
            if (m.slug === 'resilient' && this._featEscolhasLocal?.resilient) {
                extra = ` (${ATTR_LABELS_PT[this._featEscolhasLocal.resilient] || this._featEscolhasLocal.resilient})`;
            }
            if (m.slug === 'magic-initiate' && this._featEscolhasLocal?.magic_initiate) {
                extra = ` (${this._featEscolhasLocal.magic_initiate})`;
            }
            if (m.slug === 'skilled') {
                extra = this._labelSkilledExtra(this._featEscolhasLocal);
            }
            if (m.slug === 'skill-expert') {
                extra = this._labelSkillExpertExtra(this._featEscolhasLocal);
            }
            return `<div class="ficha-dnd5e-progressao-item is-readonly">Nív. ${m.nivel}: Talento — ${feat ? feat.nome : m.slug}${extra}</div>`;
        });
        if (!linhas.length && feats && feats.length) {
            feats
                .filter((slug) => slug !== 'ability-score-improvement')
                .forEach((slug) => {
                    const feat = this.catalogoFeats.find((f) => f.slug === slug);
                    linhas.push(
                        `<div class="ficha-dnd5e-progressao-item is-readonly">Talento — ${feat ? feat.nome : slug}</div>`
                    );
                });
        }
        return linhas.join('');
    }

    _textoProximaProgressao() {
        const nivel = this.getNivel();
        const raca = (this.getRacaSlug() || '').toLowerCase();
        const hpRolls = this._progCache?.hp_rolls || [];
        const marcos = this._progCache?.marcos || [];
        const hpNiveis = new Set(hpRolls.map((r) => r.nivel));
        const marcoNiveis = new Set(marcos.map((m) => m.nivel));
        const partes = [];

        if (nivel < 20) {
            partes.push(`Ao atingir o nível ${nivel + 1}, registre os PV do dado de vida.`);
        }
        const marcosFuturos = this.niveisFeat.filter((n) => n > nivel);
        const proxMarco = marcosFuturos[0];
        if (proxMarco) {
            partes.push(`Próximo marco de classe: nível ${proxMarco}.`);
        } else if (nivel >= 20) {
            partes.push('Nível máximo — sem marcos futuros.');
        }

        if (nivel >= 2 && !hpNiveis.has(2)) {
            return `Registre os PV do nível 2 para concluir a progressão atual.`;
        }
        for (let n = 2; n <= nivel; n += 1) {
            if (!hpNiveis.has(n)) {
                return `Registre os PV do nível ${n} para concluir a progressão atual.`;
            }
        }
        const marcosDevidos = this.niveisFeat.filter((n) => n <= nivel && !marcoNiveis.has(n));
        if (raca === 'humano' && nivel >= 1 && !marcoNiveis.has(1)) {
            marcosDevidos.unshift(1);
        }
        if (marcosDevidos.length) {
            return `Escolha incremento ou talento do nível ${marcosDevidos[0]}.`;
        }

        return partes.join(' ');
    }

    _renderProgressaoInfo() {
        const host = this.el('f5e_progressao_info');
        if (!host) return;
        const nivel = this.getNivel();
        const hpRolls = this._progCache?.hp_rolls || [];
        const marcos = this._progCache?.marcos || [];
        const hpHtml = this._htmlHpRolls(hpRolls);
        const marcoHtml = this._htmlMarcos(marcos, this._featsCache);
        const proximo = this._textoProximaProgressao();
        host.innerHTML = `
            <p class="ficha-dnd5e-status ficha-dnd5e-progressao-info-status">
                <strong>Progressão em dia</strong> — nível ${nivel}.
            </p>
            <p class="ficha-dnd5e-status ficha-dnd5e-progressao-info-proximo">${proximo}</p>
            ${
                hpHtml
                    ? `<p class="ficha-label">PV registrados</p><div class="ficha-dnd5e-progressao-lista">${hpHtml}</div>`
                    : ''
            }
            ${
                marcoHtml
                    ? `<p class="ficha-label">Marcos registrados</p><div class="ficha-dnd5e-progressao-lista">${marcoHtml}</div>`
                    : ''
            }`;
    }

    _atualizarModoProgressao(pendenciasServidor) {
        const acao = this._pendenciasAcao(pendenciasServidor);
        const nivelSubiu = this._nivelSubiuPendente();
        const exibir = acao.length > 0 || nivelSubiu;
        const edit = this.el('f5e_progressao_edit');
        const info = this.el('f5e_progressao_info');
        const secao = this.el('f5e_progressao_sec');
        const tituloPendencias = edit?.querySelector('.ficha-dnd5e-pendencias-titulo');

        if (edit) edit.hidden = !exibir;
        if (info) info.hidden = true;
        if (tituloPendencias) tituloPendencias.hidden = !acao.length;
        if (secao) {
            secao.hidden = !exibir;
            secao.classList.toggle('has-pendencias', exibir);
        }
        if (nivelSubiu && this.xpPrecisaSalvar()) {
            this._setStatus(
                `Nível ${this._nivelEfetivo()} — salve a ficha e registre PV/marcos do novo nível.`
            );
        } else if (!exibir) {
            this._setStatus('');
        }
    }

    renderPendenciasLocais(pendenciasServidor) {
        this._renderPendencias(pendenciasServidor || []);
    }

    _ctxPendencias() {
        return {
            nivel: this.getNivel(),
            xp: this.getXp(),
            xpPrecisaSalvar: this.xpPrecisaSalvar(),
            temPersonagem: !!this.getPersonagemId(),
        };
    }

    _pendenciasMescladas(pendenciasServidor) {
        const localProg = this._pendenciasProgressaoLocal();
        let base = pendenciasServidor || [];
        if (PENDENCIAS_UTIL) {
            base = PENDENCIAS_UTIL.mergePendencias(pendenciasServidor, this._ctxPendencias());
        }
        const seen = new Set(base);
        localProg.forEach((p) => {
            if (!seen.has(p)) {
                base.push(p);
                seen.add(p);
            }
        });
        if (PENDENCIAS_UTIL) {
            const ordem = { xp: 0, hp: 1, marco: 2, pericia: 3, outro: 4 };
            base = base.sort((a, b) => {
                const ca = ordem[PENDENCIAS_UTIL.categoria(a)] ?? 9;
                const cb = ordem[PENDENCIAS_UTIL.categoria(b)] ?? 9;
                if (ca !== cb) return ca - cb;
                return PENDENCIAS_UTIL.traduzir(a).localeCompare(
                    PENDENCIAS_UTIL.traduzir(b),
                    'pt-BR'
                );
            });
        }
        return base;
    }

    _bind() {
        const btnHp = this.el('f5e_btn_hp_roll');
        const btnMarco = this.el('f5e_btn_marco');
        const btnFeatEscolhas = this.el('f5e_btn_feat_escolhas');
        const tipoMarco = this.el('f5e_marco_tipo');
        const selFeatMarco = this.el('f5e_marco_feat');
        const asiModo = this.el('f5e_marco_asi_modo');
        if (btnHp) {
            btnHp.addEventListener('click', () => this._registrarHpRoll());
        }
        if (btnMarco) {
            btnMarco.addEventListener('click', () => this._registrarMarco());
        }
        if (btnFeatEscolhas) {
            btnFeatEscolhas.addEventListener('click', () => this._salvarFeatEscolhas());
        }
        if (selFeatMarco) {
            selFeatMarco.addEventListener('change', () => this._toggleFeatEscolhaMarco());
        }
        if (tipoMarco) {
            tipoMarco.addEventListener('change', () => this._toggleMarcoCampos());
            this._toggleMarcoCampos();
        }
        const selNivel = this.el('f5e_marco_nivel');
        if (selNivel) {
            selNivel.addEventListener('change', () => this._toggleMarcoCampos());
        }
        if (asiModo) {
            asiModo.addEventListener('change', () => this._toggleAsiModo());
            this._toggleAsiModo();
        }
    }

    _toggleMarcoCampos() {
        const nivelMarco = parseInt(this.el('f5e_marco_nivel')?.value, 10);
        const tipo = (this.el('f5e_marco_tipo')?.value || 'asi').toLowerCase();
        const featWrap = this.el('f5e_marco_feat_wrap');
        const asiWrap = this.el('f5e_marco_asi_wrap');
        const tipoSel = this.el('f5e_marco_tipo');
        const soFeatHumano = nivelMarco === 1;
        if (soFeatHumano && tipoSel) {
            tipoSel.value = 'feat';
        }
        if (tipoSel) {
            tipoSel.querySelectorAll('option').forEach((opt) => {
                if (opt.value === 'asi') {
                    opt.hidden = soFeatHumano;
                    opt.disabled = soFeatHumano;
                }
            });
        }
        const tipoEf = soFeatHumano ? 'feat' : tipo;
        if (featWrap) featWrap.hidden = tipoEf !== 'feat';
        if (asiWrap) asiWrap.hidden = tipoEf !== 'asi';
        this._toggleFeatEscolhaMarco();
    }

    _toggleFeatEscolhaMarco() {
        const slug = (this.el('f5e_marco_feat')?.value || '').toLowerCase();
        const resilient = this.el('f5e_marco_feat_resilient_wrap');
        const magic = this.el('f5e_marco_feat_magic_wrap');
        const skilled = this.el('f5e_marco_feat_skilled_wrap');
        const skillExpert = this.el('f5e_marco_feat_skill_expert_wrap');
        if (resilient) resilient.hidden = slug !== 'resilient';
        if (magic) magic.hidden = slug !== 'magic-initiate';
        if (skilled) skilled.hidden = slug !== 'skilled';
        if (skillExpert) skillExpert.hidden = slug !== 'skill-expert';
    }

    _renderFeatEscolhasSection(feats, escolhas) {
        const lista = (feats || []).map((f) => String(f).toLowerCase());
        const temRes = lista.includes('resilient');
        const temMag = lista.includes('magic-initiate');
        const temSkilled = lista.includes('skilled');
        const temSkillExpert = lista.includes('skill-expert');
        const sec = this.el('f5e_feat_escolhas_sec');
        const wrapRes = this.el('f5e_feat_escolhas_resilient_wrap');
        const wrapMag = this.el('f5e_feat_escolhas_magic_wrap');
        const wrapSkilled = this.el('f5e_feat_escolhas_skilled_wrap');
        const wrapSkillExpert = this.el('f5e_feat_escolhas_skill_expert_wrap');
        if (sec) sec.hidden = !temRes && !temMag && !temSkilled && !temSkillExpert;
        if (wrapRes) wrapRes.hidden = !temRes;
        if (wrapMag) wrapMag.hidden = !temMag;
        if (wrapSkilled) wrapSkilled.hidden = !temSkilled;
        if (wrapSkillExpert) wrapSkillExpert.hidden = !temSkillExpert;
        const selRes = this.el('f5e_feat_escolha_resilient');
        const selMag = this.el('f5e_feat_escolha_magic');
        if (selRes) {
            selRes.value =
                escolhas?.resilient || escolhas?.resilient_atributo || '';
        }
        if (selMag) {
            selMag.value =
                escolhas?.magic_initiate || escolhas?.magic_initiate_classe || '';
        }
        if (temSkilled) {
            this._preencherSkilledSelects(
                'f5e_feat_escolha_skilled',
                escolhas?.skilled_pericias || escolhas?.skilled
            );
        }
        if (temSkillExpert) {
            this._preencherSkillExpertSelects('f5e_feat_escolha_skill_expert', escolhas);
        }
    }

    _coletarFeatEscolhasMarco(slug) {
        const s = (slug || '').toLowerCase();
        const out = {};
        if (s === 'resilient') {
            const v = this.el('f5e_marco_feat_resilient')?.value || '';
            if (v) out.resilient = v;
        }
        if (s === 'magic-initiate') {
            const v = this.el('f5e_marco_feat_magic')?.value || '';
            if (v) out.magic_initiate = v;
        }
        if (s === 'skilled') {
            const slugs = this._coletarSkilledSlugs('f5e_marco_feat_skilled');
            if (slugs.length) out.skilled_pericias = slugs;
        }
        if (s === 'skill-expert') {
            Object.assign(out, this._coletarSkillExpert('f5e_marco_feat_skill_expert'));
        }
        return Object.keys(out).length ? out : null;
    }

    _coletarFeatEscolhasAtuais() {
        const out = { ...(this._featEscolhasLocal || {}) };
        if (!this.el('f5e_feat_escolhas_resilient_wrap')?.hidden) {
            const v = this.el('f5e_feat_escolha_resilient')?.value || '';
            if (v) out.resilient = v;
            else delete out.resilient;
        }
        if (!this.el('f5e_feat_escolhas_magic_wrap')?.hidden) {
            const v = this.el('f5e_feat_escolha_magic')?.value || '';
            if (v) out.magic_initiate = v;
            else delete out.magic_initiate;
        }
        if (!this.el('f5e_feat_escolhas_skilled_wrap')?.hidden) {
            const slugs = this._coletarSkilledSlugs('f5e_feat_escolha_skilled');
            if (slugs.length) out.skilled_pericias = slugs;
            else delete out.skilled_pericias;
        }
        if (!this.el('f5e_feat_escolhas_skill_expert_wrap')?.hidden) {
            const se = this._coletarSkillExpert('f5e_feat_escolha_skill_expert');
            if (se.skill_expert_nova) out.skill_expert_nova = se.skill_expert_nova;
            else delete out.skill_expert_nova;
            if (se.skill_expert_expertise) out.skill_expert_expertise = se.skill_expert_expertise;
            else delete out.skill_expert_expertise;
        }
        return out;
    }

    async _salvarFeatEscolhas() {
        const id = this.getPersonagemId();
        if (!id) {
            Toast.error('Salve a ficha antes de registrar escolhas de talentos.');
            return;
        }
        const escolhas = this._coletarFeatEscolhasAtuais();
        if (this.el('f5e_feat_escolhas_skilled_wrap')?.hidden === false) {
            const err = this._validarSkilledSlugs(escolhas.skilled_pericias);
            if (err) {
                Toast.error(err);
                return;
            }
        }
        if (this.el('f5e_feat_escolhas_skill_expert_wrap')?.hidden === false) {
            const err = this._validarSkillExpert(escolhas);
            if (err) {
                Toast.error(err);
                return;
            }
        }
        this._setStatus('Salvando escolhas…');
        try {
            const res = await this.ps.progressaoFeatEscolhas(id, {
                feat_escolhas: escolhas,
            });
            this._featEscolhasLocal = { ...(res.feat_escolhas || escolhas) };
            this.loadFromFicha(res.ficha);
            this.onFichaAtualizada(res);
            await this.refreshPendencias();
            Toast.success('Escolhas de talentos salvas.');
            this._setStatus('');
        } catch (e) {
            this._setStatus('');
            Toast.error(e.message || 'Erro ao salvar escolhas');
        }
    }

    _toggleAsiModo() {
        const modo = this.el('f5e_marco_asi_modo')?.value || '2';
        const wrap2 = this.el('f5e_marco_asi_attr2_wrap');
        if (wrap2) wrap2.hidden = modo !== '1+1';
    }

    async refreshPendencias() {
        const id = this.getPersonagemId();
        if (!id) return;
        try {
            const data = await this.ps.progressaoPendencias(id);
            this.renderPendenciasLocais(data.pendencias || []);
            this._preencherNivelHpPendente(data.niveis_hp_pendentes);
            if (this.el('f5e_hp_max') && data.hp_max) {
                this.el('f5e_hp_max').textContent = String(data.hp_max);
            }
            const hpInput = this.el('f5e_hp_atual');
            if (hpInput && data.hp_max) {
                const cur = parseInt(hpInput.value, 10);
                if (!Number.isFinite(cur) || cur > data.hp_max) {
                    hpInput.value = String(data.hp_max);
                }
            }
            this._renderHpDetalhe(data.hp_resumo);
            this.onFichaAtualizada(data);
        } catch (e) {
            this._setStatus(e.message || 'Erro ao carregar pendências');
        }
    }

    _renderPendencias(pendenciasServidor) {
        const host = this.el('f5e_pendencias_lista');
        const alerta = this.el('f5e_pendencias_alerta');
        const badge = this.el('f5e_pendencias_badge');
        const acao = this._pendenciasAcao(pendenciasServidor);
        const nivelSubiu = this._nivelSubiuPendente();

        this._atualizarModoProgressao(pendenciasServidor);

        const hpPendentes = acao
            .filter((p) => String(p).startsWith('hp_nivel_'))
            .map((p) => (PENDENCIAS_UTIL ? PENDENCIAS_UTIL.nivelDePendencia(p) : null))
            .filter((n) => Number.isFinite(n))
            .sort((a, b) => a - b);
        this._preencherNivelHpPendente(hpPendentes);

        const badgeQtd = acao.length + (nivelSubiu && !acao.length ? 1 : 0);
        if (badge) {
            badge.textContent = badgeQtd ? String(badgeQtd) : '';
            badge.hidden = !badgeQtd;
        }
        if (alerta) {
            if (!acao.length && !nivelSubiu) {
                alerta.hidden = true;
                alerta.innerHTML = '';
            } else {
                alerta.hidden = false;
                const partes = [];
                if (nivelSubiu) {
                    partes.push(
                        `nível ${this._nivelEfetivo()} (salve a ficha${acao.length ? ' e complete' : ''})`
                    );
                }
                if (acao.length) {
                    const resumo = PENDENCIAS_UTIL
                        ? PENDENCIAS_UTIL.resumoAlerta(acao)
                        : `${acao.length} item(ns)`;
                    partes.push(resumo);
                }
                alerta.innerHTML = `<strong>Progressão incompleta</strong> — ${partes.join(' · ')}. Clique em um item para ir ao campo.`;
            }
        }
        if (!host) return;
        if (!acao.length) {
            host.innerHTML = '';
            return;
        }
        host.innerHTML = acao
            .map((p) => {
                const cat = PENDENCIAS_UTIL ? PENDENCIAS_UTIL.categoria(p) : 'outro';
                const label = PENDENCIAS_UTIL ? PENDENCIAS_UTIL.traduzir(p) : p;
                return `<li><button type="button" class="ficha-dnd5e-pendencia-item is-${cat}" data-pendencia="${p}">${label}</button></li>`;
            })
            .join('');
        host.querySelectorAll('[data-pendencia]').forEach((btn) => {
            btn.addEventListener('click', () => this._navegarPendencia(btn.dataset.pendencia));
        });
    }

    _navegarPendencia(slug) {
        const util = PENDENCIAS_UTIL;
        const cat = util ? util.categoria(slug) : '';
        const secao = this.el('f5e_progressao_sec');
        secao?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        if (slug === 'xp_nao_salvo') {
            this.el('btnSalvar')?.focus();
            return;
        }
        if (slug === 'xp_insuficiente' || slug === 'xp_nivel_excedido') {
            const xp = this.el('f5e_xp');
            xp?.focus();
            xp?.select?.();
            return;
        }
        if (cat === 'hp' || slug.startsWith('hp_nivel_')) {
            const n = util ? util.nivelDePendencia(slug) : null;
            const input = this.el('f5e_hp_roll_nivel');
            if (input && n) input.value = String(n);
            input?.focus();
            return;
        }
        if (cat === 'marco' || slug.startsWith('marco_nivel_') || slug === 'feat_nivel_1') {
            const n =
                slug === 'feat_nivel_1'
                    ? 1
                    : util
                      ? util.nivelDePendencia(slug)
                      : null;
            const sel = this.el('f5e_marco_nivel');
            if (sel && n) sel.value = String(n);
            this._toggleMarcoCampos();
            sel?.focus();
            return;
        }
        if (slug === 'feat_escolha_resilient' || slug === 'feat_escolha_magic_initiate' || slug === 'feat_escolha_skilled' || slug === 'feat_escolha_skill_expert') {
            this.el('f5e_feat_escolhas_sec')?.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest',
            });
            if (slug === 'feat_escolha_resilient') {
                this.el('f5e_feat_escolha_resilient')?.focus();
            } else if (slug === 'feat_escolha_magic_initiate') {
                this.el('f5e_feat_escolha_magic')?.focus();
            } else if (slug === 'feat_escolha_skilled') {
                this.el('f5e_feat_escolha_skilled_1')?.focus();
            } else {
                this.el('f5e_feat_escolha_skill_expert_nova')?.focus();
            }
            return;
        }
        if (slug === 'expertise_classe') {
            this.el('f5e_expertise_wrap')?.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest',
            });
            this.el('f5e_expertise_escolha')?.querySelector('input')?.focus();
            return;
        }
        this.el('f5e_btn_hp_roll')?.focus();
    }

    _preencherNivelHpPendente(pendentes) {
        const input = this.el('f5e_hp_roll_nivel');
        if (!input) return;
        const lista = Array.isArray(pendentes) ? pendentes : [];
        if (lista.length) {
            input.value = String(lista[0]);
        }
    }

    _renderHpRolls(rolls) {
        const host = this.el('f5e_hp_rolls_lista');
        if (!host) return;
        if (!rolls.length) {
            host.innerHTML = '<span class="ficha-vazio">Nenhuma rolagem registrada</span>';
            return;
        }
        host.innerHTML = rolls
            .map((r) => {
                const mod = Number(r.con_mod);
                const modStr = mod >= 0 ? `+${mod}` : String(mod);
                return `<div class="ficha-dnd5e-progressao-item">Nív. ${r.nivel}: dado(${r.roll}) CON(${modStr}) = +${r.ganho} PV (classe)</div>`;
            })
            .join('');
    }

    _renderHpDetalhe(resumo) {
        const host = this.el('f5e_hp_detalhe');
        if (!host || !resumo?.niveis?.length) return;
        const n1 = resumo.niveis[0];
        const modStr = n1.con_mod >= 0 ? `+${n1.con_mod}` : String(n1.con_mod);
        const partes = [`${resumo.dado_vida}(${n1.roll})`, `CON(${modStr})`];
        if (resumo.bonus_racial_por_nivel) {
            partes.push(`raça(+${resumo.bonus_racial_por_nivel}/nív.)`);
        }
        if (resumo.bonus_feat_por_nivel) {
            partes.push(`Robusto(+${resumo.bonus_feat_por_nivel}/nív.)`);
        }
        let texto = `${partes.join(' + ')} = ${n1.subtotal} PV (nív. 1)`;
        if (resumo.niveis.length > 1) {
            texto += ` · total ${resumo.total}`;
        }
        host.textContent = texto;
    }

    _renderMarcos(marcos, feats) {
        const host = this.el('f5e_marcos_lista');
        if (!host) return;
        const linhas = (marcos || []).map((m) => {
            if (m.tipo === 'asi') {
                const dist = formatDistribuicaoAsi(m.distribuicao);
                return `<div class="ficha-dnd5e-progressao-item">Nív. ${m.nivel}: Incremento (${dist})</div>`;
            }
            const feat = this.catalogoFeats.find((f) => f.slug === m.slug);
            let extra = '';
            if (m.slug === 'resilient' && this._featEscolhasLocal?.resilient) {
                extra = ` (${ATTR_LABELS_PT[this._featEscolhasLocal.resilient] || this._featEscolhasLocal.resilient})`;
            }
            if (m.slug === 'magic-initiate' && this._featEscolhasLocal?.magic_initiate) {
                extra = ` (${this._featEscolhasLocal.magic_initiate})`;
            }
            if (m.slug === 'skilled') {
                extra = this._labelSkilledExtra(this._featEscolhasLocal);
            }
            if (m.slug === 'skill-expert') {
                extra = this._labelSkillExpertExtra(this._featEscolhasLocal);
            }
            return `<div class="ficha-dnd5e-progressao-item">Nív. ${m.nivel}: Talento — ${feat ? feat.nome : m.slug}${extra}</div>`;
        });
        if (!linhas.length && feats && feats.length) {
            feats
                .filter((slug) => slug !== 'ability-score-improvement')
                .forEach((slug) => {
                    const feat = this.catalogoFeats.find((f) => f.slug === slug);
                    linhas.push(
                        `<div class="ficha-dnd5e-progressao-item">Talento — ${feat ? feat.nome : slug}</div>`
                    );
                });
        }
        host.innerHTML =
            linhas.join('') || '<span class="ficha-vazio">Nenhuma escolha registrada</span>';

        const selectNivel = this.el('f5e_marco_nivel');
        const selectFeat = this.el('f5e_marco_feat');
        if (selectNivel) {
            const nivel = this.getNivel();
            const raca = (this.getRacaSlug() || '').toLowerCase();
            const usados = new Set((marcos || []).map((m) => m.nivel));
            let opcoes = this.niveisFeat.filter((n) => n <= nivel && !usados.has(n));
            if (raca === 'humano' && nivel >= 1 && !usados.has(1)) {
                opcoes = [1, ...opcoes];
            }
            selectNivel.innerHTML = opcoes.length
                ? opcoes.map((n) => `<option value="${n}">${n}º nível</option>`).join('')
                : '<option value="">—</option>';
            this._toggleMarcoCampos();
        }
        if (selectFeat && this.catalogoFeats.length) {
            selectFeat.innerHTML = this.catalogoFeats
                .map((f) => `<option value="${f.slug}">${f.nome}</option>`)
                .join('');
            this._toggleFeatEscolhaMarco();
        }
    }

    _setStatus(msg) {
        const st = this.el('f5e_progressao_status');
        if (st) st.textContent = msg || '';
    }

    _validarAntesHpRoll() {
        const nivel = parseInt(this.el('f5e_nivel')?.value, 10) || 1;
        const xp = parseInt(this.el('f5e_xp')?.value, 10) || 0;
        if (typeof Dnd5eXpUtil !== 'undefined') {
            const xpMin = Dnd5eXpUtil.xpMinimaPorNivel(nivel);
            if (xp < xpMin) {
                Dnd5eXpUtil.aplicarNivelParaXp(this.el('f5e_nivel'), this.el('f5e_xp'));
                return `Nível ${nivel} exige pelo menos ${xpMin} XP. Ajuste aplicado — salve a ficha e tente novamente.`;
            }
            const maxNivel = Dnd5eXpUtil.nivelPorXp(xp);
            if (nivel > maxNivel) {
                return `Nível ${nivel} exige mais XP (máximo permitido com ${xp} XP: ${maxNivel}).`;
            }
        }
        if (this.xpPrecisaSalvar()) {
            return 'Salve a ficha para sincronizar o XP antes de registrar PV por nível.';
        }
        return null;
    }

    async _registrarHpRoll() {
        const id = this.getPersonagemId();
        if (!id) {
            Toast.error('Salve a ficha antes de registrar PV por nível.');
            return;
        }
        const erroValidacao = this._validarAntesHpRoll();
        if (erroValidacao) {
            Toast.error(erroValidacao);
            return;
        }
        const nivel = parseInt(this.el('f5e_hp_roll_nivel')?.value, 10);
        const usarMedia = !!this.el('f5e_hp_roll_media')?.checked;
        const rollRaw = this.el('f5e_hp_roll_valor')?.value;
        const roll = rollRaw ? parseInt(rollRaw, 10) : null;
        this._setStatus('Registrando PV…');
        try {
            const res = await this.ps.progressaoHpRoll(id, {
                nivel,
                roll: Number.isFinite(roll) ? roll : null,
                usar_media: usarMedia,
            });
            this.loadFromFicha(res.ficha);
            if (this.el('f5e_hp_max')) {
                this.el('f5e_hp_max').textContent = String(res.hp_max);
            }
            this.onFichaAtualizada(res);
            await this.refreshPendencias();
            Toast.success(`PV do nível ${nivel} registrado (+${res.entrada.ganho}).`);
            this._setStatus('');
        } catch (e) {
            this._setStatus('');
            Toast.error(e.message || 'Erro ao registrar PV');
        }
    }

    async _registrarMarco() {
        const id = this.getPersonagemId();
        if (!id) {
            Toast.error('Salve a ficha antes de registrar incremento ou talento.');
            return;
        }
        const nivel = parseInt(this.el('f5e_marco_nivel')?.value, 10);
        if (!Number.isFinite(nivel)) {
            Toast.error('Não há marco pendente para registrar neste nível.');
            return;
        }
        let tipo = (this.el('f5e_marco_tipo')?.value || 'asi').toLowerCase();
        if (nivel === 1) {
            tipo = 'feat';
        }
        const body = { nivel, tipo };
        if (tipo === 'feat') {
            const slug = this.el('f5e_marco_feat')?.value;
            if (!slug) {
                Toast.error('Selecione um talento.');
                return;
            }
            body.slug = slug;
            const escolhas = this._coletarFeatEscolhasMarco(slug);
            if (slug === 'resilient' && !escolhas?.resilient) {
                Toast.error('Resiliente exige escolha de salvaguarda.');
                return;
            }
            if (slug === 'magic-initiate' && !escolhas?.magic_initiate) {
                Toast.error('Iniciado em Magia exige escolha de classe.');
                return;
            }
            if (slug === 'skilled') {
                const err = this._validarSkilledSlugs(escolhas?.skilled_pericias);
                if (err) {
                    Toast.error(err);
                    return;
                }
            }
            if (slug === 'skill-expert') {
                const err = this._validarSkillExpert(escolhas);
                if (err) {
                    Toast.error(err);
                    return;
                }
            }
            if (escolhas) body.feat_escolhas = escolhas;
        } else {
            const modo = this.el('f5e_marco_asi_modo')?.value || '2';
            const attr1 = this.el('f5e_marco_asi_attr')?.value;
            if (modo === '1+1') {
                const attr2 = this.el('f5e_marco_asi_attr2')?.value;
                if (!attr1 || !attr2) {
                    Toast.error('Selecione os dois atributos para +1/+1.');
                    return;
                }
                if (attr1 === attr2) {
                    Toast.error('Os dois atributos devem ser diferentes.');
                    return;
                }
                body.distribuicao = { [attr1]: 1, [attr2]: 1 };
            } else {
                body.distribuicao = { [attr1]: 2 };
            }
        }
        this._setStatus('Registrando escolha…');
        try {
            const res = await this.ps.progressaoMarco(id, body);
            this.loadFromFicha(res.ficha);
            if (this.el('f5e_hp_max') && res.hp_max) {
                this.el('f5e_hp_max').textContent = String(res.hp_max);
            }
            const hpInput = this.el('f5e_hp_atual');
            if (hpInput && res.hp_atual != null) {
                hpInput.value = String(res.hp_atual);
            }
            this.onFichaAtualizada(res);
            await this.refreshPendencias();
            if (res.hp_retroativo_con > 0) {
                Toast.success(
                    `CON aumentou: +${res.hp_retroativo_con} PV máx. (retroativo por nível).`
                );
            } else {
                Toast.success('Escolha de progressão registrada.');
            }
            this._setStatus('');
        } catch (e) {
            this._setStatus('');
            Toast.error(e.message || 'Erro ao registrar escolha');
        }
    }
}
