/**
 * Progressão no pré-cadastro — marcos ASI/talento e expertise de classe.
 */
const PREC_EXPERTISE_CLASSE = {
    ladino: [
        [1, 2],
        [6, 2],
    ],
    bardo: [
        [3, 2],
        [10, 2],
    ],
};

const PREC_ATTR_OPTS = [
    { key: 'strength', label: 'Força' },
    { key: 'dexterity', label: 'Destreza' },
    { key: 'constitution', label: 'Constituição' },
    { key: 'intelligence', label: 'Inteligência' },
    { key: 'wisdom', label: 'Sabedoria' },
    { key: 'charisma', label: 'Carisma' },
];

class Dnd5ePreCadastroProgressao {
    constructor(options) {
        this.el = options.el || ((id) => document.getElementById(id));
        this.rs = options.regrasService;
        this.niveisFeat = [4, 8, 12, 16, 19];
        this.catalogoFeats = [];
        this.catalogoPericias = [];
        this._proficientes = [];
        this._expertiseSlots = 0;
    }

    async init() {
        try {
            const [classes, feats, per] = await Promise.all([
                this.rs.classes(),
                this.rs.talentos(),
                this.rs.pericias(),
            ]);
            this.niveisFeat = classes.niveis_ganho_feat || this.niveisFeat;
            this.catalogoFeats = (feats.talentos || []).filter(
                (f) => f.slug !== 'ability-score-improvement'
            );
            this.catalogoPericias = per.pericias || [];
        } catch (_e) {
            /* offline */
        }
    }

    slotsExpertise(classeSlug, nivel) {
        const key = (classeSlug || '').toLowerCase();
        const marcos = PREC_EXPERTISE_CLASSE[key] || [];
        let total = 0;
        marcos.forEach(([min, qtd]) => {
            if (nivel >= min) total += qtd;
        });
        return total;
    }

    niveisMarcoObrigatorios(nivel, racaSlug) {
        const out = [];
        const raca = (racaSlug || '').toLowerCase();
        if (raca === 'humano' && nivel >= 1) out.push(1);
        this.niveisFeat.forEach((n) => {
            if (n <= nivel) out.push(n);
        });
        return [...new Set(out)].sort((a, b) => a - b);
    }

    _featOptsHtml() {
        return this.catalogoFeats
            .map((f) => `<option value="${f.slug}">${f.nome}</option>`)
            .join('');
    }

    _periciaOptsHtml(filtroProf = false) {
        let lista = this.catalogoPericias;
        if (filtroProf && this._proficientes.length) {
            const prof = new Set(this._proficientes);
            lista = lista.filter((p) => prof.has(p.slug));
        }
        const opts = lista.map((p) => `<option value="${p.slug}">${p.nome}</option>`).join('');
        return `<option value="">— escolha —</option>${opts}`;
    }

    _attrOptsHtml() {
        return PREC_ATTR_OPTS.map((a) => `<option value="${a.key}">${a.label}</option>`).join('');
    }

    render(ctx) {
        const wrap = this.el('prec_progressao_wrap');
        const host = this.el('prec_progressao_host');
        if (!wrap || !host) return;

        const nivel = Math.max(1, parseInt(ctx.nivel, 10) || 1);
        const raca = (ctx.racaSlug || '').toLowerCase();
        this._expertiseSlots =
            ctx.expertiseSlotsClasse != null
                ? ctx.expertiseSlotsClasse
                : this.slotsExpertise(ctx.classeSlug, nivel);
        const mostrar = nivel > 1 || raca === 'humano' || this._expertiseSlots > 0;

        if (!mostrar) {
            wrap.hidden = true;
            host.innerHTML = '';
            return;
        }

        wrap.hidden = false;
        this._proficientes = Array.isArray(ctx.periciasProficientes)
            ? ctx.periciasProficientes
            : [];

        const niveis = this.niveisMarcoObrigatorios(nivel, ctx.racaSlug);
        const cards = niveis.map((n) => this._htmlMarcoCard(n)).join('');

        const expertise =
            this._expertiseSlots > 0
                ? `
            <div class="dnd5e-prec-progressao-expertise">
                <p class="ficha-label">Expertise de classe (${this._expertiseSlots} perícia(s))</p>
                <div class="dnd5e-prec-expertise-grid" id="prec_expertise_grid">
                    ${Array.from({ length: this._expertiseSlots }, (_, i) => {
                        const idx = i + 1;
                        return `<select id="prec_expertise_${idx}" aria-label="Expertise ${idx}">${this._periciaOptsHtml(true)}</select>`;
                    }).join('')}
                </div>
            </div>`
                : '';

        const tituloSec =
            nivel > 1
                ? `Nível ${nivel}: informe marcos de talento/incremento e expertise exigidos pela classe.`
                : 'Informe talento humano e/ou expertise de classe, conforme aplicável.';

        host.innerHTML = `
            <p class="ficha-dnd5e-status dnd5e-prec-progressao-hint">${tituloSec}</p>
            <div class="dnd5e-prec-marcos-list">${cards}</div>
            ${expertise}`;

        niveis.forEach((n) => this._bindMarcoCard(n));
    }

    _htmlMarcoCard(nivelMarco) {
        const soFeat = nivelMarco === 1;
        const tipoOpts = soFeat
            ? '<option value="feat">Talento</option>'
            : `<option value="asi">Incremento no Valor de Habilidade</option>
               <option value="feat">Talento (regra opcional)</option>`;
        const titulo =
            nivelMarco === 1
                ? '1º nível — talento humano'
                : `${nivelMarco}º nível — incremento ou talento`;

        return `
            <div class="dnd5e-prec-marco-card" data-marco-nivel="${nivelMarco}">
                <p class="ficha-label dnd5e-prec-marco-titulo">${titulo}</p>
                <div class="dnd5e-prec-grid">
                    <div>
                        <label class="ficha-label" for="prec_marco_tipo_${nivelMarco}">Escolha</label>
                        <select id="prec_marco_tipo_${nivelMarco}">${tipoOpts}</select>
                    </div>
                </div>
                <div id="prec_marco_feat_wrap_${nivelMarco}" class="dnd5e-prec-marco-feat" ${soFeat ? '' : 'hidden'}>
                    <label class="ficha-label" for="prec_marco_feat_${nivelMarco}">Talento</label>
                    <select id="prec_marco_feat_${nivelMarco}">${this._featOptsHtml()}</select>
                    <div id="prec_marco_res_wrap_${nivelMarco}" class="dnd5e-prec-feat-extra" hidden>
                        <label class="ficha-label" for="prec_marco_res_${nivelMarco}">Resiliente — salvaguarda</label>
                        <select id="prec_marco_res_${nivelMarco}">
                            <option value="">— escolha —</option>
                            ${this._attrOptsHtml()}
                        </select>
                    </div>
                    <div id="prec_marco_mag_wrap_${nivelMarco}" class="dnd5e-prec-feat-extra" hidden>
                        <label class="ficha-label" for="prec_marco_mag_${nivelMarco}">Iniciado em Magia — classe</label>
                        <select id="prec_marco_mag_${nivelMarco}">
                            <option value="">— escolha —</option>
                            <option value="clerigo">Clérigo</option>
                            <option value="mago">Mago</option>
                            <option value="druida">Druida</option>
                            <option value="bruxo">Bruxo</option>
                        </select>
                    </div>
                    <div id="prec_marco_skilled_wrap_${nivelMarco}" class="dnd5e-prec-feat-extra" hidden>
                        <p class="ficha-label">Habilidoso — 3 perícias</p>
                        <div class="dnd5e-prec-skilled-grid">
                            <select id="prec_marco_skilled_${nivelMarco}_1">${this._periciaOptsHtml()}</select>
                            <select id="prec_marco_skilled_${nivelMarco}_2">${this._periciaOptsHtml()}</select>
                            <select id="prec_marco_skilled_${nivelMarco}_3">${this._periciaOptsHtml()}</select>
                        </div>
                    </div>
                </div>
                <div id="prec_marco_asi_wrap_${nivelMarco}" class="dnd5e-prec-marco-asi" hidden>
                    <label class="ficha-label" for="prec_marco_asi_modo_${nivelMarco}">Distribuição</label>
                    <select id="prec_marco_asi_modo_${nivelMarco}">
                        <option value="2">+2 em um atributo</option>
                        <option value="1+1">+1 em dois atributos</option>
                    </select>
                    <div class="dnd5e-prec-grid dnd5e-prec-asi-grid">
                        <div>
                            <label class="ficha-label" for="prec_marco_asi_1_${nivelMarco}">Atributo</label>
                            <select id="prec_marco_asi_1_${nivelMarco}">${this._attrOptsHtml()}</select>
                        </div>
                        <div id="prec_marco_asi_2_box_${nivelMarco}" hidden>
                            <label class="ficha-label" for="prec_marco_asi_2_${nivelMarco}">Segundo atributo</label>
                            <select id="prec_marco_asi_2_${nivelMarco}">${this._attrOptsHtml()}</select>
                        </div>
                    </div>
                </div>
            </div>`;
    }

    _bindMarcoCard(nivelMarco) {
        const tipo = this.el(`prec_marco_tipo_${nivelMarco}`);
        const feat = this.el(`prec_marco_feat_${nivelMarco}`);
        const asiModo = this.el(`prec_marco_asi_modo_${nivelMarco}`);
        const toggle = () => this._toggleMarcoCard(nivelMarco);
        tipo?.addEventListener('change', toggle);
        feat?.addEventListener('change', () => this._toggleFeatExtra(nivelMarco));
        asiModo?.addEventListener('change', () => this._toggleAsiModo(nivelMarco));
        toggle();
    }

    _toggleMarcoCard(nivelMarco) {
        const tipo = (this.el(`prec_marco_tipo_${nivelMarco}`)?.value || 'feat').toLowerCase();
        const featWrap = this.el(`prec_marco_feat_wrap_${nivelMarco}`);
        const asiWrap = this.el(`prec_marco_asi_wrap_${nivelMarco}`);
        if (nivelMarco === 1) {
            if (featWrap) featWrap.hidden = false;
            if (asiWrap) asiWrap.hidden = true;
            this._toggleFeatExtra(nivelMarco);
            return;
        }
        if (featWrap) featWrap.hidden = tipo !== 'feat';
        if (asiWrap) asiWrap.hidden = tipo !== 'asi';
        if (tipo === 'feat') this._toggleFeatExtra(nivelMarco);
        if (tipo === 'asi') this._toggleAsiModo(nivelMarco);
    }

    _toggleFeatExtra(nivelMarco) {
        const slug = (this.el(`prec_marco_feat_${nivelMarco}`)?.value || '').toLowerCase();
        const res = this.el(`prec_marco_res_wrap_${nivelMarco}`);
        const mag = this.el(`prec_marco_mag_wrap_${nivelMarco}`);
        const skilled = this.el(`prec_marco_skilled_wrap_${nivelMarco}`);
        if (res) res.hidden = slug !== 'resilient';
        if (mag) mag.hidden = slug !== 'magic-initiate';
        if (skilled) skilled.hidden = slug !== 'skilled';
    }

    _toggleAsiModo(nivelMarco) {
        const modo = this.el(`prec_marco_asi_modo_${nivelMarco}`)?.value || '2';
        const box2 = this.el(`prec_marco_asi_2_box_${nivelMarco}`);
        if (box2) box2.hidden = modo !== '1+1';
    }

    _coletarDistribuicaoAsi(nivelMarco) {
        const modo = this.el(`prec_marco_asi_modo_${nivelMarco}`)?.value || '2';
        const a1 = this.el(`prec_marco_asi_1_${nivelMarco}`)?.value;
        if (!a1) return null;
        if (modo === '2') return { [a1]: 2 };
        const a2 = this.el(`prec_marco_asi_2_${nivelMarco}`)?.value;
        if (!a2 || a2 === a1) return null;
        return { [a1]: 1, [a2]: 1 };
    }

    _coletarFeatEscolhas(nivelMarco, slug) {
        const s = (slug || '').toLowerCase();
        const out = {};
        if (s === 'resilient') {
            const v = this.el(`prec_marco_res_${nivelMarco}`)?.value;
            if (v) out.resilient = v;
        }
        if (s === 'magic-initiate') {
            const v = this.el(`prec_marco_mag_${nivelMarco}`)?.value;
            if (v) out.magic_initiate = v;
        }
        if (s === 'skilled') {
            const slugs = [1, 2, 3]
                .map((i) => this.el(`prec_marco_skilled_${nivelMarco}_${i}`)?.value || '')
                .filter(Boolean);
            if (slugs.length) out.skilled_pericias = slugs;
        }
        return Object.keys(out).length ? out : null;
    }

    coletarMarco(nivelMarco) {
        const tipo = (this.el(`prec_marco_tipo_${nivelMarco}`)?.value || '').toLowerCase();
        if (tipo === 'asi') {
            const distribuicao = this._coletarDistribuicaoAsi(nivelMarco);
            if (!distribuicao) return null;
            return { nivel: nivelMarco, tipo: 'asi', distribuicao };
        }
        const slug = this.el(`prec_marco_feat_${nivelMarco}`)?.value;
        if (!slug) return null;
        const marco = { nivel: nivelMarco, tipo: 'feat', slug };
        const esc = this._coletarFeatEscolhas(nivelMarco, slug);
        if (esc) marco.feat_escolhas = esc;
        return marco;
    }

    getExpertisePericias() {
        const out = [];
        for (let i = 1; i <= this._expertiseSlots; i += 1) {
            const v = this.el(`prec_expertise_${i}`)?.value;
            if (v) out.push(v);
        }
        return out;
    }

    getMarcos(nivel, racaSlug) {
        return this.niveisMarcoObrigatorios(nivel, racaSlug)
            .map((n) => this.coletarMarco(n))
            .filter(Boolean);
    }

    montarExtrasFicha(nivel, racaSlug) {
        const marcos = this.getMarcos(nivel, racaSlug);
        const expertise = this.getExpertisePericias();
        const feats = [];
        const featEscolhas = {};
        const bonusAsi = {};
        marcos.forEach((m) => {
            if (m.tipo === 'feat') {
                feats.push(m.slug);
                if (m.feat_escolhas) Object.assign(featEscolhas, m.feat_escolhas);
            } else if (m.tipo === 'asi' && m.distribuicao) {
                Object.entries(m.distribuicao).forEach(([k, v]) => {
                    bonusAsi[k] = (bonusAsi[k] || 0) + Number(v);
                });
            }
        });
        const out = { marcos };
        if (feats.length) out.feats = feats;
        if (Object.keys(featEscolhas).length) out.feat_escolhas = featEscolhas;
        if (Object.keys(bonusAsi).length) out.bonus_atributo_feat = bonusAsi;
        if (expertise.length) out.expertise_pericias = expertise;
        return out;
    }

    validar(nivel, racaSlug, classeSlug) {
        const raca = (racaSlug || '').toLowerCase();
        const slots = this._expertiseSlots || this.slotsExpertise(classeSlug, nivel);
        const precisaMarcos = nivel > 1 || raca === 'humano';
        if (!precisaMarcos && slots <= 0) return null;

        if (precisaMarcos) {
            const obrigatorios = this.niveisMarcoObrigatorios(nivel, racaSlug);
            for (const n of obrigatorios) {
                const m = this.coletarMarco(n);
                if (!m) {
                    return n === 1
                        ? 'Escolha o talento humano do 1º nível.'
                        : `Escolha incremento ou talento do nível ${n}.`;
                }
                if (m.tipo === 'feat') {
                    const slug = (m.slug || '').toLowerCase();
                    if (slug === 'resilient' && !m.feat_escolhas?.resilient) {
                        return `Resiliente (nível ${n}): escolha a salvaguarda.`;
                    }
                    if (slug === 'magic-initiate' && !m.feat_escolhas?.magic_initiate) {
                        return `Iniciado em Magia (nível ${n}): escolha a classe.`;
                    }
                    if (slug === 'skilled') {
                        const sl = m.feat_escolhas?.skilled_pericias || [];
                        if (sl.length !== 3 || new Set(sl).size !== 3) {
                            return `Habilidoso (nível ${n}): escolha 3 perícias distintas.`;
                        }
                    }
                }
            }
        }

        const exp = this.getExpertisePericias();
        if (slots > 0) {
            if (exp.length < slots) {
                return `Escolha ${slots} perícia(s) com Expertise de classe.`;
            }
            if (new Set(exp).size !== exp.length) {
                return 'As perícias de Expertise devem ser distintas.';
            }
        }
        return null;
    }
}
