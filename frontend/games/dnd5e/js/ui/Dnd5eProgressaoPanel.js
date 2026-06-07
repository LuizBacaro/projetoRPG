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

const PENDENCIAS_LABELS = {
    hp_nivel_2: 'Rolar PV do nível 2',
    hp_nivel_3: 'Rolar PV do nível 3',
    hp_nivel_4: 'Rolar PV do nível 4',
    hp_nivel_5: 'Rolar PV do nível 5',
    hp_nivel_6: 'Rolar PV do nível 6',
    hp_nivel_7: 'Rolar PV do nível 7',
    hp_nivel_8: 'Rolar PV do nível 8',
    hp_nivel_9: 'Rolar PV do nível 9',
    hp_nivel_10: 'Rolar PV do nível 10',
    hp_nivel_11: 'Rolar PV do nível 11',
    hp_nivel_12: 'Rolar PV do nível 12',
    hp_nivel_13: 'Rolar PV do nível 13',
    hp_nivel_14: 'Rolar PV do nível 14',
    hp_nivel_15: 'Rolar PV do nível 15',
    hp_nivel_16: 'Rolar PV do nível 16',
    hp_nivel_17: 'Rolar PV do nível 17',
    hp_nivel_18: 'Rolar PV do nível 18',
    hp_nivel_19: 'Rolar PV do nível 19',
    hp_nivel_20: 'Rolar PV do nível 20',
    marco_nivel_4: 'Escolher incremento ou talento (nível 4)',
    marco_nivel_8: 'Escolher incremento ou talento (nível 8)',
    marco_nivel_12: 'Escolher incremento ou talento (nível 12)',
    marco_nivel_16: 'Escolher incremento ou talento (nível 16)',
    marco_nivel_19: 'Escolher incremento ou talento (nível 19)',
    revisar_feats: 'Revisar talentos registrados',
    hp_max_invalido: 'PV máximo inválido — confira as rolagens',
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
        this.onFichaAtualizada = options.onFichaAtualizada || (() => {});
        this.catalogoFeats = [];
        this.niveisFeat = [4, 8, 12, 16, 19];
    }

    async init() {
        try {
            const data = await this.rs.classes();
            this.niveisFeat = data.niveis_ganho_feat || this.niveisFeat;
            const feats = await this.rs.talentos();
            this.catalogoFeats = (feats.talentos || []).filter(
                (f) => f.slug !== 'ability-score-improvement'
            );
        } catch (_e) {
            /* offline */
        }
        this._bind();
    }

    loadFromFicha(ficha) {
        const f = ficha || {};
        const prog = f.progressao || { hp_rolls: [], marcos: [] };
        this._renderPendencias(f.pendencias || []);
        this._renderHpRolls(prog.hp_rolls || []);
        this._renderMarcos(prog.marcos || [], f.feats || []);
    }

    _bind() {
        const btnHp = this.el('f5e_btn_hp_roll');
        const btnMarco = this.el('f5e_btn_marco');
        const tipoMarco = this.el('f5e_marco_tipo');
        const asiModo = this.el('f5e_marco_asi_modo');
        if (btnHp) {
            btnHp.addEventListener('click', () => this._registrarHpRoll());
        }
        if (btnMarco) {
            btnMarco.addEventListener('click', () => this._registrarMarco());
        }
        if (tipoMarco) {
            tipoMarco.addEventListener('change', () => this._toggleMarcoCampos());
            this._toggleMarcoCampos();
        }
        if (asiModo) {
            asiModo.addEventListener('change', () => this._toggleAsiModo());
            this._toggleAsiModo();
        }
    }

    _toggleMarcoCampos() {
        const tipo = (this.el('f5e_marco_tipo')?.value || 'asi').toLowerCase();
        const featWrap = this.el('f5e_marco_feat_wrap');
        const asiWrap = this.el('f5e_marco_asi_wrap');
        if (featWrap) featWrap.hidden = tipo !== 'feat';
        if (asiWrap) asiWrap.hidden = tipo !== 'asi';
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
            this._renderPendencias(data.pendencias || []);
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

    _renderPendencias(pendencias) {
        const host = this.el('f5e_pendencias_lista');
        if (!host) return;
        if (!pendencias.length) {
            host.innerHTML = '<span class="ficha-vazio">Nenhuma pendência</span>';
            return;
        }
        host.innerHTML = pendencias
            .map((p) => `<li>${PENDENCIAS_LABELS[p] || p}</li>`)
            .join('');
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
            return `<div class="ficha-dnd5e-progressao-item">Nív. ${m.nivel}: Talento — ${feat ? feat.nome : m.slug}</div>`;
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
            const usados = new Set((marcos || []).map((m) => m.nivel));
            const opcoes = this.niveisFeat.filter((n) => n <= nivel && !usados.has(n));
            selectNivel.innerHTML = opcoes.length
                ? opcoes.map((n) => `<option value="${n}">${n}º nível</option>`).join('')
                : '<option value="">—</option>';
        }
        if (selectFeat && this.catalogoFeats.length) {
            selectFeat.innerHTML = this.catalogoFeats
                .map((f) => `<option value="${f.slug}">${f.nome}</option>`)
                .join('');
        }
    }

    _setStatus(msg) {
        const st = this.el('f5e_progressao_status');
        if (st) st.textContent = msg || '';
    }

    async _registrarHpRoll() {
        const id = this.getPersonagemId();
        if (!id) {
            Toast.error('Salve a ficha antes de registrar PV por nível.');
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
        const tipo = (this.el('f5e_marco_tipo')?.value || 'asi').toLowerCase();
        const body = { nivel, tipo };
        if (tipo === 'feat') {
            const slug = this.el('f5e_marco_feat')?.value;
            if (!slug) {
                Toast.error('Selecione um talento.');
                return;
            }
            body.slug = slug;
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
            this.onFichaAtualizada(res);
            await this.refreshPendencias();
            Toast.success('Escolha de progressão registrada.');
            this._setStatus('');
        } catch (e) {
            this._setStatus('');
            Toast.error(e.message || 'Erro ao registrar escolha');
        }
    }
}
