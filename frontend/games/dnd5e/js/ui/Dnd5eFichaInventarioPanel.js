/**
 * Painel de inventário D&D 5e — blocos alinhados à ficha 3.5:
 * Talentos, Equipamentos, Consumíveis, Armadura/Proteção, Ataques.
 */
const F5E_ESC = (s) => {
    if (typeof window !== 'undefined' && typeof window.escapeHtml === 'function') {
        return window.escapeHtml(String(s ?? ''));
    }
    return String(s ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
};

function f5eUid() {
    return `i${Date.now().toString(36)}${Math.random().toString(36).slice(2, 7)}`;
}

function normalizarInventarioFicha(ficha) {
    const inv = { ...(ficha?.inventario || {}) };
    const topArm = ficha?.armadura_slug ?? inv.armadura_slug ?? null;
    const topEsc = ficha?.escudo_slug ?? inv.escudo_slug ?? null;

    let equipamentos = Array.isArray(inv.equipamentos) ? inv.equipamentos.map((x) => ({ ...x })) : [];
    let consumiveis = Array.isArray(inv.consumiveis) ? inv.consumiveis.map((x) => ({ ...x })) : [];

    if ((!equipamentos.length && !consumiveis.length) && Array.isArray(inv.itens)) {
        inv.itens.forEach((row) => {
            const copia = { ...row, id: row.id || f5eUid() };
            if ((row.categoria || '') === 'medicinal') consumiveis.push(copia);
            else equipamentos.push(copia);
        });
    }

    equipamentos = equipamentos.map((x) => ({ ...x, id: x.id || f5eUid() }));
    consumiveis = consumiveis.map((x) => ({ ...x, id: x.id || f5eUid() }));

    return {
        armadura_slug: topArm || null,
        escudo_slug: topEsc || null,
        arma_principal_slug: inv.arma_principal_slug || null,
        ouro_po: Number(inv.ouro_po) || 0,
        equipamentos,
        consumiveis,
        ataques: Array.isArray(inv.ataques) ? inv.ataques.map((a) => ({ ...a })) : [],
    };
}

class Dnd5eFichaInventarioPanel {
    constructor(options) {
        this.el = options.el || ((id) => document.getElementById(id));
        this.rs = options.regrasService;
        this.onChange = options.onChange || (() => {});
        this.onRolarOuroClasse = options.onRolarOuroClasse || (() => {});
        this.onAplicarEquipClasse = options.onAplicarEquipClasse || (() => {});
        this.getPreview = options.getPreview || (() => null);
        this.catalogoModal = options.catalogoModal || new Dnd5eFichaCatalogoModal();

        this.catalogo = {
            armaduras: [],
            escudos: [],
            armas: [],
            itens: [],
            consumiveis: [],
            talentos: [],
        };
        this.state = normalizarInventarioFicha({});
        this.antecedenteMeta = {
            inventario_slug: null,
            ouro_aplicado: 0,
            tracos: null,
            idiomas: [],
        };
        this.classeOuroMeta = {
            slug: null,
            ouro_aplicado: 0,
            rolagem: [],
            formula: '',
        };
        this.classeEquipMeta = {
            slug: null,
            aplicado: false,
            nome: '',
        };
    }

    async init() {
        try {
            const [equip, talentos] = await Promise.all([
                this.rs.equipamento(),
                this.rs.talentos(),
            ]);
            this.catalogo.armaduras = equip.armaduras || [];
            this.catalogo.escudos = equip.escudos || [];
            this.catalogo.armas = [
                ...(equip.armas_simples || []),
                ...(equip.armas_marciais || []),
            ];
            const todosItens = equip.itens_variados || [];
            this.catalogo.consumiveis = todosItens.filter((i) => i.categoria === 'medicinal');
            this.catalogo.itens = todosItens.filter((i) => i.categoria !== 'medicinal');
            this.catalogo.talentos = talentos.talentos || [];
        } catch (_e) {
            /* offline */
        }
        this._preencherSelectsCatalogo();
        this._bind();
    }

    loadFromFicha(ficha, featsExtras) {
        this.state = normalizarInventarioFicha(ficha || {});
        this.antecedenteMeta = {
            inventario_slug: ficha?.antecedente_inventario_slug || null,
            ouro_aplicado: Number(ficha?.antecedente_ouro_aplicado) || 0,
            tracos: ficha?.antecedente_tracos || null,
            idiomas: ficha?.antecedente_idiomas || [],
        };
        this.classeOuroMeta = {
            slug: ficha?.classe_ouro_slug || null,
            ouro_aplicado: Number(ficha?.ouro_classe_aplicado) || 0,
            rolagem: ficha?.ouro_classe_rolagem || [],
            formula: ficha?.ouro_classe_formula || '',
        };
        this.classeEquipMeta = {
            slug: ficha?.classe_equip_slug || null,
            aplicado: !!ficha?.classe_equip_aplicado,
            nome: ficha?.classe_equip_nome || '',
        };
        this._featsFicha = Array.isArray(featsExtras)
            ? featsExtras
            : Array.isArray(ficha?.feats)
              ? ficha.feats
              : [];
        this._syncCamposDom();
        if (this.classeOuroMeta.ouro_aplicado > 0) {
            this._atualizarHintOuroClasse({
                total: this.classeOuroMeta.ouro_aplicado,
                dados: this.classeOuroMeta.rolagem,
                formula: this.classeOuroMeta.formula,
                multiplicador: 1,
            });
        }
        if (this.classeEquipMeta.aplicado) {
            this._atualizarHintEquipClasse(this.classeEquipMeta);
        }
        this.renderTudo();
    }

    getClasseEquipMeta() {
        return {
            classe_equip_slug: this.classeEquipMeta.slug,
            classe_equip_aplicado: !!this.classeEquipMeta.aplicado,
            classe_equip_nome: this.classeEquipMeta.nome || '',
        };
    }

    _atualizarHintEquipClasse(meta) {
        const hint = this.el('f5e_equip_classe_hint');
        if (!hint) return;
        if (!meta?.aplicado) {
            hint.textContent = '';
            return;
        }
        hint.textContent = meta.nome
            ? `${meta.nome} aplicado.`
            : 'Equipamento inicial da classe aplicado.';
    }

    aplicarEquipamentoClasse(res) {
        if (typeof Dnd5eEquipamentoClasseUtil === 'undefined') return false;
        const out = Dnd5eEquipamentoClasseUtil.aplicarResposta(this.state, res);
        if (!out.changed) return false;
        this.state = out.state;
        this.classeEquipMeta = {
            slug: out.meta.classe_equip_slug,
            aplicado: out.meta.classe_equip_aplicado,
            nome: out.meta.classe_equip_nome,
        };
        this._syncCamposDom();
        this._atualizarHintEquipClasse(this.classeEquipMeta);
        this.renderTudo();
        this._emitChange();
        return true;
    }

    getAntecedenteMeta() {
        return {
            antecedente_inventario_slug: this.antecedenteMeta.inventario_slug,
            antecedente_ouro_aplicado: this.antecedenteMeta.ouro_aplicado || 0,
            antecedente_tracos: this.antecedenteMeta.tracos || null,
            antecedente_idiomas: this.antecedenteMeta.idiomas || [],
        };
    }

    getClasseOuroMeta() {
        return {
            classe_ouro_slug: this.classeOuroMeta.slug,
            ouro_classe_aplicado: this.classeOuroMeta.ouro_aplicado || 0,
            ouro_classe_rolagem: this.classeOuroMeta.rolagem || [],
            ouro_classe_formula: this.classeOuroMeta.formula || '',
        };
    }

    _atualizarHintOuroClasse(roll) {
        const hint = this.el('f5e_ouro_classe_hint');
        if (!hint || typeof Dnd5eOuroClasseUtil === 'undefined') return;
        hint.textContent = roll ? Dnd5eOuroClasseUtil.formatRollHint(roll) : '';
    }

    aplicarOuroClasse(classeSlug, roll, forcar = false) {
        if (typeof Dnd5eOuroClasseUtil === 'undefined') return false;
        const slugAtual = classeSlug ? String(classeSlug).trim() : null;
        const res = Dnd5eOuroClasseUtil.sincronizarOuro({
            inventarioState: this.state,
            slugAtual,
            slugAplicado: this.classeOuroMeta.slug,
            ouroAplicado: this.classeOuroMeta.ouro_aplicado,
            roll,
            forcar,
        });
        if (!res.changed) {
            this._atualizarHintOuroClasse(
                roll || {
                    total: this.classeOuroMeta.ouro_aplicado,
                    dados: this.classeOuroMeta.rolagem,
                    formula: this.classeOuroMeta.formula,
                    multiplicador: 1,
                }
            );
            return false;
        }
        this.state.ouro_po = res.inventarioState.ouro_po;
        this.classeOuroMeta = {
            slug: res.meta.classe_ouro_slug,
            ouro_aplicado: res.meta.ouro_classe_aplicado || 0,
            rolagem: res.meta.ouro_classe_rolagem || [],
            formula: res.meta.ouro_classe_formula || '',
        };
        this._syncCamposDom();
        this._atualizarHintOuroClasse(roll);
        this._emitChange();
        return true;
    }

    sincronizarAntecedente(antecedenteSlug, antecedente, idiomasEscolhidos, tracosEscolhidos) {
        if (typeof Dnd5eAntecedenteUtil === 'undefined') return false;
        const slugAtual = antecedenteSlug ? String(antecedenteSlug).trim() : null;
        const idiomas =
            idiomasEscolhidos !== undefined
                ? idiomasEscolhidos
                : this.antecedenteMeta.idiomas;
        const tracos =
            tracosEscolhidos !== undefined ? tracosEscolhidos : this.antecedenteMeta.tracos;
        const res = Dnd5eAntecedenteUtil.sincronizarInventario({
            inventarioState: this.state,
            slugAtual,
            slugAplicado: this.antecedenteMeta.inventario_slug,
            ouroAplicado: this.antecedenteMeta.ouro_aplicado,
            antecedente,
            idiomasEscolhidos: idiomas,
            tracosEscolhidos: tracos,
            uidFn: f5eUid,
        });
        if (!res.changed) return false;
        this.state.equipamentos = res.inventarioState.equipamentos;
        this.state.ouro_po = res.inventarioState.ouro_po;
        this.antecedenteMeta = {
            inventario_slug: res.meta.antecedente_inventario_slug,
            ouro_aplicado: res.meta.antecedente_ouro_aplicado || 0,
            tracos: res.meta.antecedente_tracos,
            idiomas: res.meta.antecedente_idiomas || [],
        };
        this._syncCamposDom();
        this.renderEquipamentos();
        this._emitChange();
        return true;
    }

    setIdiomasAntecedente(idiomas) {
        this.antecedenteMeta.idiomas = Array.isArray(idiomas) ? [...idiomas] : [];
    }

    getIdiomasAntecedente() {
        return [...(this.antecedenteMeta.idiomas || [])];
    }

    setTracosAntecedente(tracos) {
        this.antecedenteMeta.tracos = tracos && typeof tracos === 'object' ? tracos : null;
    }

    getTracosAntecedente() {
        return this.antecedenteMeta.tracos || null;
    }

    getInventarioParaFicha() {
        const arm = this.el('f5e_armadura')?.value || null;
        const esc = this.el('f5e_escudo')?.value || null;
        const arma = this.el('f5e_arma_principal')?.value || null;
        const ouro = parseFloat(this.el('f5e_ouro')?.value) || 0;
        return {
            ...this.state,
            armadura_slug: arm || null,
            escudo_slug: esc || null,
            arma_principal_slug: arma || null,
            ouro_po: ouro,
            ataques: [...(this.state.ataques || [])],
            equipamentos: [...(this.state.equipamentos || [])],
            consumiveis: [...(this.state.consumiveis || [])],
        };
    }

    getArmaduraEscudoParaCalcular() {
        return {
            armadura_slug: this.el('f5e_armadura')?.value || null,
            escudo_slug: this.el('f5e_escudo')?.value || null,
            arma_principal_slug: this.el('f5e_arma_principal')?.value || null,
        };
    }

    payloadCalcularEquipamento(preview) {
        const mods = preview?.modificadores || {};
        const inv = this.getInventarioParaFicha();
        const itens = [
            ...(inv.equipamentos || []).map((x) => ({
                slug: x.slug,
                quantidade: x.quantidade || 1,
            })),
            ...(inv.consumiveis || []).map((x) => ({
                slug: x.slug,
                quantidade: x.quantidade || 1,
            })),
        ];
        return {
            armadura_slug: inv.armadura_slug,
            escudo_slug: inv.escudo_slug,
            arma_principal_slug: inv.arma_principal_slug,
            itens,
            forca: preview?.scores_efetivos?.strength ?? 10,
            dex_mod: mods.dexterity ?? 0,
            ouro_po: inv.ouro_po,
        };
    }

    _preencherSelectsCatalogo() {
        const armSel = this.el('f5e_armadura');
        const escSel = this.el('f5e_escudo');
        const armaSel = this.el('f5e_arma_principal');
        if (armSel) {
            const cur = armSel.value;
            armSel.innerHTML =
                '<option value="">Sem armadura</option>' +
                this.catalogo.armaduras
                    .map((a) => `<option value="${a.slug}">${F5E_ESC(a.nome)} (CA ${a.ca})</option>`)
                    .join('');
            if (cur) armSel.value = cur;
        }
        if (escSel) {
            const cur = escSel.value;
            escSel.innerHTML =
                '<option value="">Nenhum</option>' +
                this.catalogo.escudos
                    .map((s) => `<option value="${s.slug}">${F5E_ESC(s.nome)} (+${s.bonus_ac})</option>`)
                    .join('');
            if (cur) escSel.value = cur;
        }
        if (armaSel) {
            const cur = armaSel.value;
            armaSel.innerHTML =
                '<option value="">Nenhuma</option>' +
                this.catalogo.armas
                    .map((a) => `<option value="${a.slug}">${F5E_ESC(a.nome)} (${a.dano})</option>`)
                    .join('');
            if (cur) armaSel.value = cur;
        }
    }

    _syncCamposDom() {
        const s = this.state;
        if (this.el('f5e_armadura') && s.armadura_slug) {
            this.el('f5e_armadura').value = s.armadura_slug;
        }
        if (this.el('f5e_escudo') && s.escudo_slug) {
            this.el('f5e_escudo').value = s.escudo_slug;
        }
        if (this.el('f5e_arma_principal') && s.arma_principal_slug) {
            this.el('f5e_arma_principal').value = s.arma_principal_slug;
        }
        if (this.el('f5e_ouro')) {
            this.el('f5e_ouro').value = String(s.ouro_po ?? 0);
        }
    }

    _bind() {
        ['f5e_armadura', 'f5e_escudo', 'f5e_arma_principal', 'f5e_ouro'].forEach((id) => {
            this.el(id)?.addEventListener('change', () => this._emitChange());
            this.el(id)?.addEventListener('input', () => this._emitChange());
        });

        this.el('f5e_btn_ir_progressao')?.addEventListener('click', () => {
            this.el('f5e_progressao_sec')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });

        this.el('f5e_btn_add_equip')?.addEventListener('click', () => this._abrirModalEquipamentos());
        this.el('f5e_btn_add_consumivel')?.addEventListener('click', () => this._abrirModalConsumiveis());

        this.el('f5e_btn_editar_ataques')?.addEventListener('click', () => this._abrirEditorAtaques());
        this.el('f5e_btn_add_linha_ataque')?.addEventListener('click', () => this._adicionarLinhaAtaqueEditor());
        this.el('f5e_btn_salvar_ataques')?.addEventListener('click', () => this._salvarAtaquesEditor());
        this.el('f5e_btn_cancelar_ataques')?.addEventListener('click', () => {
            const ed = this.el('f5e_ataques_editor');
            if (ed) ed.hidden = true;
        });
        this.el('f5e_btn_sync_arma_ataque')?.addEventListener('click', () => this._sincronizarArmaPrincipalAtaque());
        this.el('f5e_btn_rolar_ouro')?.addEventListener('click', () => {
            if (typeof this.onRolarOuroClasse === 'function') {
                this.onRolarOuroClasse(true);
            }
        });
        this.el('f5e_btn_equip_classe')?.addEventListener('click', () => {
            if (typeof this.onAplicarEquipClasse === 'function') {
                this.onAplicarEquipClasse(true);
            }
        });
    }

    _emitChange() {
        this.onChange();
    }

    _nomeCatalogo(slug, lista) {
        const row = (lista || []).find((x) => x.slug === slug);
        return row ? row.nome : slug;
    }

    renderTudo(feats) {
        if (feats) this._featsFicha = feats;
        this.renderTalentos();
        this.renderEquipamentos();
        this.renderConsumiveis();
        this.renderProtecaoResumo();
        this.renderAtaques();
    }

    renderTalentos() {
        const host = this.el('f5e_talentos_lista');
        if (!host) return;
        const slugs = [...new Set(this._featsFicha || [])].filter(
            (s) => s && s !== 'ability-score-improvement'
        );
        if (!slugs.length) {
            host.innerHTML = '<span class="ficha-vazio">Nenhum talento registrado</span>';
            return;
        }
        host.innerHTML = `
            <div class="ficha-talentos-grid">
                ${slugs
                    .map((slug) => {
                        const t = this.catalogo.talentos.find((x) => x.slug === slug);
                        const nome = t ? t.nome : slug;
                        const tipo = t?.tipo_bonus ? `<span class="ficha-dnd5e-talento-tipo">${F5E_ESC(t.tipo_bonus)}</span>` : '';
                        return `<div class="ficha-talento-card ficha-dnd5e-talento-card-compact">
                            <h4 class="ficha-talento-card-title">${F5E_ESC(nome)}</h4>
                            ${tipo}
                        </div>`;
                    })
                    .join('')}
            </div>`;
    }

    renderEquipamentos() {
        const host = this.el('f5e_equipamentos_lista');
        if (!host) return;
        const lista = this.state.equipamentos || [];
        if (!lista.length) {
            host.innerHTML = '<span class="ficha-vazio">Nenhum equipamento cadastrado</span>';
            return;
        }
        host.innerHTML = `
            <div class="ficha-equipamentos-tabela">
                <div class="ficha-equipamento-header">
                    <span>Item</span><span>Qtd</span><span></span>
                </div>
                <div class="ficha-equipamentos-lista-items">
                    ${lista
                        .map((row) => {
                            const nome = row.nome || this._nomeCatalogo(row.slug, this.catalogo.itens);
                            return `<div class="ficha-equipamento-linha">
                                <span class="ficha-equipamento-nome">${F5E_ESC(nome)}</span>
                                <span class="ficha-equipamento-qtd">${row.quantidade || 1}</span>
                                <button type="button" class="btn-deletar-eq" data-id="${F5E_ESC(row.id)}" title="Remover">🗑️</button>
                            </div>`;
                        })
                        .join('')}
                </div>
            </div>`;
        host.querySelectorAll('.btn-deletar-eq').forEach((btn) => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                this.state.equipamentos = (this.state.equipamentos || []).filter((x) => x.id !== id);
                this.renderEquipamentos();
                this._emitChange();
            });
        });
    }

    renderConsumiveis() {
        const host = this.el('f5e_consumiveis_lista');
        if (!host) return;
        const lista = this.state.consumiveis || [];
        if (!lista.length) {
            host.innerHTML = '<span class="ficha-vazio">Nenhum consumível cadastrado</span>';
            return;
        }
        host.innerHTML = `
            <div class="ficha-equipamentos-tabela">
                <div class="ficha-equipamento-header">
                    <span>Item</span><span>Qtd</span><span></span>
                </div>
                <div class="ficha-equipamentos-lista-items">
                    ${lista
                        .map((row) => {
                            const nome =
                                row.nome || this._nomeCatalogo(row.slug, this.catalogo.consumiveis);
                            return `<div class="ficha-equipamento-linha">
                                <span class="ficha-equipamento-nome">${F5E_ESC(nome)}</span>
                                <span class="ficha-equipamento-qtd">${row.quantidade || 1}</span>
                                <button type="button" class="btn-deletar-eq" data-id="${F5E_ESC(row.id)}" title="Remover">🗑️</button>
                            </div>`;
                        })
                        .join('')}
                </div>
            </div>`;
        host.querySelectorAll('.btn-deletar-eq').forEach((btn) => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                this.state.consumiveis = (this.state.consumiveis || []).filter((x) => x.id !== id);
                this.renderConsumiveis();
                this._emitChange();
            });
        });
    }

    renderProtecaoResumo() {
        const host = this.el('f5e_protecao_resumo');
        if (!host) return;
        const arm = this.catalogo.armaduras.find((a) => a.slug === this.el('f5e_armadura')?.value);
        const esc = this.catalogo.escudos.find((s) => s.slug === this.el('f5e_escudo')?.value);
        const partes = [];
        if (arm) partes.push(`${arm.nome} (base CA ${arm.ca})`);
        else partes.push('Sem armadura (CA 10 + DES)');
        if (esc) partes.push(`${esc.nome} (+${esc.bonus_ac})`);
        host.textContent = partes.join(' · ');
    }

    renderAtaques() {
        const lista = this.el('f5e_ataques_lista');
        if (!lista) return;
        const ataques = this.state.ataques || [];
        if (!ataques.length) {
            lista.innerHTML = '<div class="ficha-ataque-vazio">Nenhum ataque cadastrado</div>';
            return;
        }
        lista.innerHTML = ataques
            .map(
                (a) => `<div class="ficha-ataque-linha">
                <span class="ficha-ataque-nome">${F5E_ESC(a.nome) || '—'}</span>
                <span class="ficha-ataque-bonus">${F5E_ESC(a.bonus_ataque) || '+0'}</span>
                <span class="ficha-ataque-dano">${F5E_ESC(a.dano) || '—'}</span>
            </div>`
            )
            .join('');
    }

    _abrirModalEquipamentos() {
        this.catalogoModal.abrir({
            titulo: 'Gerenciar Equipamentos',
            subtitulo: 'Adicione itens ao inventário da ficha',
            icone: '🎒',
            itens: this.catalogo.itens,
            onConfirm: (slug, qtd) => this._adicionarEquipamento(slug, qtd),
        });
    }

    _abrirModalConsumiveis() {
        const filtros = [
            { id: 'todos', label: 'Todos', fn: () => true },
            {
                id: 'pocao',
                label: 'Poções',
                fn: (i) => String(i.categoria || '').toLowerCase().includes('poç'),
            },
            {
                id: 'oleo',
                label: 'Óleos',
                fn: (i) => String(i.categoria || '').toLowerCase().includes('óleo'),
            },
            {
                id: 'pergaminho',
                label: 'Pergaminhos',
                fn: (i) => String(i.categoria || '').toLowerCase().includes('pergaminho'),
            },
        ];
        this.catalogoModal.abrir({
            titulo: 'Gerenciar Consumíveis',
            subtitulo: 'Poções, óleos, pergaminhos e itens de uso único',
            icone: '🧪',
            itens: this.catalogo.consumiveis,
            filtros,
            onConfirm: (slug, qtd) => this._adicionarConsumivel(slug, qtd),
        });
    }

    _adicionarEquipamento(slug, qtd) {
        if (!slug) return;
        const existente = (this.state.equipamentos || []).find((x) => x.slug === slug);
        if (existente) existente.quantidade = (existente.quantidade || 1) + qtd;
        else {
            this.state.equipamentos.push({
                id: f5eUid(),
                slug,
                nome: this._nomeCatalogo(slug, this.catalogo.itens),
                quantidade: qtd,
            });
        }
        this.renderEquipamentos();
        this._emitChange();
    }

    _adicionarConsumivel(slug, qtd) {
        if (!slug) return;
        const existente = (this.state.consumiveis || []).find((x) => x.slug === slug);
        if (existente) existente.quantidade = (existente.quantidade || 1) + qtd;
        else {
            this.state.consumiveis.push({
                id: f5eUid(),
                slug,
                nome: this._nomeCatalogo(slug, this.catalogo.consumiveis),
                quantidade: qtd,
            });
        }
        this.renderConsumiveis();
        this._emitChange();
    }

    _abrirEditorAtaques() {
        const editor = this.el('f5e_ataques_editor');
        const listaEl = this.el('f5e_ataques_editor_lista');
        if (!editor || !listaEl) return;
        listaEl.innerHTML = '';
        const ataques = this.state.ataques || [];
        if (!ataques.length) this._adicionarLinhaAtaqueEditor();
        else ataques.forEach((a) => this._adicionarLinhaAtaqueEditor(a));
        editor.hidden = false;
    }

    _adicionarLinhaAtaqueEditor(ataque = {}) {
        const lista = this.el('f5e_ataques_editor_lista');
        if (!lista) return;
        const div = document.createElement('div');
        div.className = 'ataque-linha ficha-dnd5e-ataque-linha-edit';
        div.innerHTML = `
            <input type="text" class="ataque-nome" placeholder="Nome" value="${F5E_ESC(ataque.nome || '')}" />
            <input type="text" class="ataque-bonus" placeholder="+0" value="${F5E_ESC(ataque.bonus_ataque || '+0')}" />
            <input type="text" class="ataque-dano" placeholder="1d8+3" value="${F5E_ESC(ataque.dano || '')}" />
            <input type="text" class="ataque-tipo" placeholder="tipo" value="${F5E_ESC(ataque.tipo_dano || '')}" />
            <button type="button" class="ficha-dnd5e-ataque-rem" title="Remover">✕</button>`;
        div.querySelector('.ficha-dnd5e-ataque-rem')?.addEventListener('click', () => div.remove());
        lista.appendChild(div);
    }

    _coletarAtaquesEditor() {
        return Array.from(
            this.el('f5e_ataques_editor_lista')?.querySelectorAll('.ataque-linha') || []
        )
            .map((l) => ({
                nome: l.querySelector('.ataque-nome')?.value?.trim() || '',
                bonus_ataque: l.querySelector('.ataque-bonus')?.value?.trim() || '+0',
                dano: l.querySelector('.ataque-dano')?.value?.trim() || '',
                tipo_dano: l.querySelector('.ataque-tipo')?.value?.trim() || '',
            }))
            .filter((a) => a.nome);
    }

    _salvarAtaquesEditor() {
        this.state.ataques = this._coletarAtaquesEditor();
        this.el('f5e_ataques_editor').hidden = true;
        this.renderAtaques();
        this._emitChange();
    }

    _sincronizarArmaPrincipalAtaque() {
        const slug = this.el('f5e_arma_principal')?.value;
        if (!slug) {
            Toast?.warning?.('Selecione a arma principal.');
            return;
        }
        const arma = this.catalogo.armas.find((a) => a.slug === slug);
        if (!arma) return;
        const preview = this.getPreview();
        const prof = preview?.bonus_proficiencia ?? 2;
        const mods = preview?.modificadores || {};
        const usaDex = (arma.propriedades || []).some((p) =>
            String(p).toLowerCase().includes('finesse')
        );
        const mod = usaDex
            ? Math.max(mods.strength ?? 0, mods.dexterity ?? 0)
            : mods.strength ?? 0;
        const bonus = mod + prof;
        const bonusStr = bonus >= 0 ? `+${bonus}` : String(bonus);
        const modStr = mod >= 0 ? `+${mod}` : String(mod);
        const linha = {
            nome: arma.nome,
            bonus_ataque: bonusStr,
            dano: `${arma.dano}${modStr}`,
            tipo_dano: arma.tipo_dano || '',
        };
        const ataques = [...(this.state.ataques || [])];
        const idx = ataques.findIndex((a) => a.nome === arma.nome);
        if (idx >= 0) ataques[idx] = linha;
        else ataques.unshift(linha);
        this.state.ataques = ataques;
        this.renderAtaques();
        Toast?.success?.('Ataque atualizado a partir da arma principal.');
        this._emitChange();
    }

    async atualizarResumoEquipamento(preview) {
        const resumoEl = this.el('f5e_equip_resumo');
        if (!resumoEl || !preview) return;
        try {
            const eq = await this.rs.calcularEquipamento(this.payloadCalcularEquipamento(preview));
            const partes = [
                `Peso ${eq.peso_total_lb} / ${eq.capacidade_lb} lb`,
                `CA ${eq.ca_total}`,
            ];
            if (eq.penalidade_velocidade_m > 0) {
                partes.push(`velocidade −${eq.penalidade_velocidade_m} m`);
            }
            if (eq.sobrecarregado) partes.push('sobrecarregado');
            if (eq.ouro_po > 0) partes.push(`${eq.ouro_po} gp`);
            resumoEl.textContent = partes.join(' · ');
            resumoEl.classList.toggle('is-sobrecarregado', !!eq.sobrecarregado);
            resumoEl.classList.toggle(
                'is-penalidade',
                !eq.sobrecarregado && eq.penalidade_velocidade_m > 0
            );
            this.renderProtecaoResumo();
        } catch (_e) {
            resumoEl.textContent = '';
        }
    }
}
