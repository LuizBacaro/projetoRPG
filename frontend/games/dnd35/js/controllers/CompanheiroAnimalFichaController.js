import { CompanheiroAnimalService } from '../services/CompanheiroAnimalService.js';
import { FamiliarService } from '../services/FamiliarService.js';
import { escapeHtml } from '../utils/formatters.js';

const ATRIBUTOS = [
    { key: 'forca', label: 'FOR' },
    { key: 'destreza', label: 'DES' },
    { key: 'constituicao', label: 'CON' },
    { key: 'inteligencia', label: 'INT' },
    { key: 'sabedoria', label: 'SAB' },
    { key: 'carisma', label: 'CAR' },
];

class CompanheiroAnimalFichaController {
    constructor() {
        this.companheiroService = new CompanheiroAnimalService();
        this.familiarService = new FamiliarService();
        this.combatenteId = null;
        this.especiesCompanheiro = [];
        this.especiesFamiliar = [];
        this.companheiro = null;
        this.familiar = null;
        this.elegCompanheiro = null;
        this.elegFamiliar = null;
        this.modo = null;
        this.vinculo = null;
        this.preview = null;
        this.bonusAtributos = {};
    }

    get service() {
        return this.modo === 'familiar' ? this.familiarService : this.companheiroService;
    }

    get elegibilidade() {
        return this.modo === 'familiar' ? this.elegFamiliar : this.elegCompanheiro;
    }

    get especies() {
        return this.modo === 'familiar' ? this.especiesFamiliar : this.especiesCompanheiro;
    }

    _classeCadastro() {
        return (
            this.elegCompanheiro?.classe ||
            this.elegFamiliar?.classe ||
            ''
        ).toLowerCase();
    }

    _inferirModoPadrao() {
        const cls = this._classeCadastro();
        const comp = this.elegCompanheiro?.elegivel;
        const fam = this.elegFamiliar?.elegivel;
        if (comp && !fam) return 'companheiro';
        if (fam && !comp) return 'familiar';
        if (/\b(druida|ranger|patrulheiro)\b/.test(cls)) return 'companheiro';
        if (/\b(mago|feiticeiro|wizard|sorcerer)\b/.test(cls)) return 'familiar';
        return comp ? 'companheiro' : 'familiar';
    }

    _definirModo(forcar = null) {
        if (forcar === 'companheiro' || forcar === 'familiar') {
            this.modo = forcar;
        } else if (this.companheiro) {
            this.modo = 'companheiro';
        } else if (this.familiar) {
            this.modo = 'familiar';
        } else {
            this.modo = this._inferirModoPadrao();
        }
        this.vinculo = this.modo === 'familiar' ? this.familiar : this.companheiro;
    }

    _elegivelAlgum() {
        return Boolean(this.elegCompanheiro?.elegivel || this.elegFamiliar?.elegivel);
    }

    _ambosElegiveisSemVinculo() {
        return (
            !this.companheiro &&
            !this.familiar &&
            this.elegCompanheiro?.elegivel &&
            this.elegFamiliar?.elegivel
        );
    }

    async inicializar() {
        const params = new URLSearchParams(window.location.search);
        this.combatenteId = Number(params.get('id'));
        if (!Number.isFinite(this.combatenteId) || this.combatenteId <= 0) return;

        try {
            const [especiesC, eligC, comp, especiesF, eligF, fam] = await Promise.all([
                this.companheiroService.listarEspecies(),
                this.companheiroService.elegibilidade(this.combatenteId),
                this.companheiroService.obter(this.combatenteId),
                this.familiarService.listarEspecies(),
                this.familiarService.elegibilidade(this.combatenteId),
                this.familiarService.obter(this.combatenteId),
            ]);
            this.especiesCompanheiro = especiesC;
            this.elegCompanheiro = eligC;
            this.companheiro = comp;
            this.especiesFamiliar = especiesF;
            this.elegFamiliar = eligF;
            this.familiar = fam;
            this._definirModo();
            await this._renderLista();
            this._bind();
        } catch (e) {
            const lista = document.getElementById('fichaCompanheiroAnimal');
            if (lista) {
                lista.innerHTML = `<span class="ficha-vazio">❌ ${escapeHtml(e.message || 'Erro ao carregar')}</span>`;
            }
        }
    }

    _bind() {
        document.getElementById('btnAdicionarCompanheiroAnimal')?.addEventListener('click', () =>
            this.abrirModal()
        );
        document.getElementById('btnFecharModalCompanheiroAnimal')?.addEventListener('click', () =>
            this.fecharModal()
        );
        document.getElementById('btnSalvarCompanheiroAnimal')?.addEventListener('click', () =>
            this.salvar()
        );
        document.getElementById('btnRemoverCompanheiroAnimal')?.addEventListener('click', () =>
            this.remover()
        );
        document.getElementById('btnPreviewCompanheiroAnimal')?.addEventListener('click', () =>
            this.atualizarPreview()
        );
        document.getElementById('caEspecieCompanheiro')?.addEventListener('change', () =>
            this.atualizarPreview()
        );
        document.getElementById('caTipoVinculo')?.addEventListener('change', () => {
            this._definirModo(document.getElementById('caTipoVinculo')?.value);
            this._preencherFormulario();
            this.atualizarPreview();
        });
        document.getElementById('modalCompanheiroAnimal')?.addEventListener('click', (e) => {
            if (e.target?.id === 'modalCompanheiroAnimal') this.fecharModal();
        });
        document.querySelectorAll('[data-bonus-attr]').forEach((inp) => {
            inp.addEventListener('change', () => this.atualizarPreview());
        });
    }

    _fmtMod(n) {
        const v = Number(n);
        if (!Number.isFinite(v)) return '—';
        return v >= 0 ? `+${v}` : String(v);
    }

    _rotuloModo() {
        return this.modo === 'familiar' ? 'Familiar' : 'Companheiro animal';
    }

    async _renderLista() {
        const lista = document.getElementById('fichaCompanheiroAnimal');
        const btn = document.getElementById('btnAdicionarCompanheiroAnimal');
        if (!lista) return;

        if (!this._elegivelAlgum()) {
            const motivo =
                this.elegCompanheiro?.motivo ||
                this.elegFamiliar?.motivo ||
                'Classe sem companheiro animal ou familiar';
            lista.innerHTML = `<span class="ficha-vazio">${escapeHtml(motivo)}</span>`;
            if (btn) btn.hidden = true;
            return;
        }
        if (btn) btn.hidden = false;

        if (!this.vinculo) {
            lista.innerHTML =
                '<span class="ficha-vazio">Nenhum companheiro animal ou familiar cadastrado</span>';
            if (btn) btn.textContent = '➕ Adicionar';
            return;
        }

        if (this.modo === 'familiar') {
            const d = this.familiar.derivadas || {};
            lista.innerHTML = `
            <div class="ficha-equipamentos-tabela">
                <div class="ficha-equipamento-linha ficha-companheiro-resumo">
                    <span class="ficha-equipamento-nome">${escapeHtml(this.familiar.nome)}</span>
                    <span class="ficha-equipamento-desc">${escapeHtml(this.familiar.especie_nome || this.familiar.especie_slug)} · Familiar</span>
                    <span class="ficha-equipamento-pag">PV ${this.familiar.hp_atual}/${this.familiar.hp_maximo}</span>
                    <span class="ficha-equipamento-qtd">CA ${this.familiar.ca}</span>
                </div>
                <p class="ficha-companheiro-stats">
                    INT ${this.familiar.inteligencia} · Nível mestre ${d.nivel_mestre ?? this.familiar.nivel_mestre ?? '—'}
                    · ${escapeHtml(this.familiar.bonus_mestre || d.bonus_mestre_especie || '')}
                </p>
            </div>`;
        } else {
            const d = this.companheiro.derivadas || {};
            lista.innerHTML = `
            <div class="ficha-equipamentos-tabela">
                <div class="ficha-equipamento-linha ficha-companheiro-resumo">
                    <span class="ficha-equipamento-nome">${escapeHtml(this.companheiro.nome)}</span>
                    <span class="ficha-equipamento-desc">${escapeHtml(this.companheiro.especie_nome || this.companheiro.especie_slug)}</span>
                    <span class="ficha-equipamento-pag">PV ${this.companheiro.hp_atual}/${this.companheiro.hp_maximo}</span>
                    <span class="ficha-equipamento-qtd">CA ${this.companheiro.ca}</span>
                </div>
                <p class="ficha-companheiro-stats">
                    HD ${d.hd_total ?? '—'} · BAB ${this._fmtMod(d.bab)} · Fort ${this._fmtMod(d.fortitude)}
                    · Ref ${this._fmtMod(d.reflexos)} · Von ${this._fmtMod(d.vontade)}
                </p>
            </div>`;
        }
        if (btn) btn.textContent = '✏️ Editar';
    }

    _preencherFormulario() {
        const sel = document.getElementById('caEspecieCompanheiro');
        const nome = document.getElementById('caNomeCompanheiro');
        const hint = document.getElementById('caElegibilidadeHint');
        const tipoWrap = document.getElementById('caTipoVinculoWrap');
        const tipoSel = document.getElementById('caTipoVinculo');
        const bonusFs = document.getElementById('caBonusAtributosFieldset');
        if (!sel) return;

        if (tipoWrap) tipoWrap.hidden = !this._ambosElegiveisSemVinculo();
        if (tipoSel) tipoSel.value = this.modo || 'companheiro';
        if (bonusFs) bonusFs.hidden = this.modo === 'familiar';

        const titulo = document.querySelector('#modalCompanheiroAnimal .equipamentos-titulo');
        if (titulo) {
            titulo.textContent =
                this.modo === 'familiar' ? 'Familiar' : 'Companheiro Animal / Familiar';
        }

        if (this.modo === 'familiar') {
            sel.innerHTML = this.especiesFamiliar
                .map(
                    (e) =>
                        `<option value="${escapeHtml(e.slug)}">${escapeHtml(e.nome)} (${escapeHtml(e.bonus_mestre || '')})</option>`
                )
                .join('');
            if (this.familiar) {
                sel.value = this.familiar.especie_slug;
                if (nome) nome.value = this.familiar.nome;
            } else if (nome) nome.value = '';
        } else {
            sel.innerHTML = this.especiesCompanheiro
                .map(
                    (e) =>
                        `<option value="${escapeHtml(e.slug)}">${escapeHtml(e.nome)} (${e.categoria}, ${e.hd_base} HD)</option>`
                )
                .join('');
            if (this.companheiro) {
                sel.value = this.companheiro.especie_slug;
                if (nome) nome.value = this.companheiro.nome;
                this.bonusAtributos = { ...(this.companheiro.bonus_atributos || {}) };
            } else {
                if (nome) nome.value = '';
                this.bonusAtributos = {};
            }
            ATRIBUTOS.forEach((a) => {
                const inp = document.querySelector(`[data-bonus-attr="${a.key}"]`);
                if (inp) inp.value = String(this.bonusAtributos[a.key] || 0);
            });
        }

        const eleg = this.elegibilidade;
        if (hint && eleg) {
            if (this.modo === 'familiar') {
                hint.textContent = eleg.elegivel
                    ? `Familiar · nível mestre ${eleg.nivel_mestre} (${eleg.classe} ${eleg.nivel_personagem})`
                    : eleg.motivo;
            } else {
                hint.textContent = eleg.elegivel
                    ? `Companheiro · nível efetivo ${eleg.nivel_efetivo} (${eleg.classe} ${eleg.nivel_personagem})`
                    : eleg.motivo;
            }
        }

        const anot = document.getElementById('caAnotacoesCompanheiro');
        if (anot) anot.value = this.vinculo?.anotacoes || '';

        document.getElementById('btnRemoverCompanheiroAnimal').hidden = !this.vinculo;
    }

    _lerBonusAtributos() {
        const out = {};
        ATRIBUTOS.forEach((a) => {
            const inp = document.querySelector(`[data-bonus-attr="${a.key}"]`);
            const v = parseInt(inp?.value, 10);
            if (Number.isFinite(v) && v !== 0) out[a.key] = v;
        });
        return out;
    }

    async atualizarPreview() {
        const painel = document.getElementById('caPreviewDerivadas');
        if (!painel || !this.elegibilidade?.elegivel) return;
        const especie_slug = document.getElementById('caEspecieCompanheiro')?.value;
        if (!especie_slug) return;
        const nome =
            document.getElementById('caNomeCompanheiro')?.value?.trim() ||
            (this.modo === 'familiar' ? 'Familiar' : 'Companheiro');
        try {
            if (this.modo === 'familiar') {
                this.preview = await this.familiarService.calcular(this.combatenteId, {
                    especie_slug,
                    nome,
                });
                const d = this.preview.derivadas;
                painel.innerHTML = `
                <p><strong>Derivadas familiar (PHB)</strong></p>
                <ul class="ca-preview-lista">
                    <li>INT ${d.inteligencia} · AN +${d.armadura_natural_bonus} (total ${d.armadura_natural_total})</li>
                    <li>CA sugerida: ${d.ca} · PV sugeridos: ${d.hp_max_sugerido}</li>
                    <li>Bônus ao mestre: ${escapeHtml(d.bonus_mestre_especie || this.preview.especie?.bonus_mestre || '')}</li>
                    <li>Habilidades: ${(d.habilidades_especiais || []).map(escapeHtml).join(', ') || '—'}</li>
                    ${d.resistencia_magia != null ? `<li>Resistência à magia: ${d.resistencia_magia}</li>` : ''}
                </ul>`;
            } else {
                this.preview = await this.companheiroService.calcular(this.combatenteId, {
                    especie_slug,
                    bonus_atributos: this._lerBonusAtributos(),
                    nome,
                });
                const d = this.preview.derivadas;
                const dist = d.distribuicao_atributos || '';
                painel.innerHTML = `
                <p><strong>Derivadas companheiro (PHB)</strong> — ${escapeHtml(dist)}</p>
                <ul class="ca-preview-lista">
                    <li>HD total: ${d.hd_total} (bônus +${d.hd_bonus})</li>
                    <li>BAB ${this._fmtMod(d.bab)} · Fort ${this._fmtMod(d.fortitude)} · Ref ${this._fmtMod(d.reflexos)} · Von ${this._fmtMod(d.vontade)}</li>
                    <li>CA sugerida: ${d.ca} · PV sugeridos: ${d.hp_max_sugerido}</li>
                    <li>Talentos: ${d.talentos_total} · Truques bônus: ${d.truques_bonus}</li>
                    <li>Habilidades: ${(d.habilidades_especiais || []).map(escapeHtml).join(', ') || '—'}</li>
                </ul>`;
            }
        } catch (e) {
            painel.innerHTML = `<p class="ficha-vazio">${escapeHtml(e.message)}</p>`;
        }
    }

    async abrirModal() {
        if (!this._elegivelAlgum()) {
            const motivo =
                this.elegCompanheiro?.motivo ||
                this.elegFamiliar?.motivo ||
                'Não elegível';
            if (typeof Toast !== 'undefined') Toast.error(motivo);
            return;
        }
        const modal = document.getElementById('modalCompanheiroAnimal');
        if (!modal) return;
        this._definirModo();
        this._preencherFormulario();
        await this.atualizarPreview();
        modal.style.display = 'flex';
    }

    fecharModal() {
        const modal = document.getElementById('modalCompanheiroAnimal');
        if (modal) modal.style.display = 'none';
    }

    async salvar() {
        const nome = document.getElementById('caNomeCompanheiro')?.value?.trim();
        const especie_slug = document.getElementById('caEspecieCompanheiro')?.value;
        if (!nome || !especie_slug) {
            if (typeof Toast !== 'undefined') Toast.error('Informe nome e espécie.');
            return;
        }
        if (!this.elegibilidade?.elegivel) {
            if (typeof Toast !== 'undefined') {
                Toast.error(this.elegibilidade?.motivo || 'Personagem não elegível.');
            }
            return;
        }

        if (this.modo === 'familiar') {
            await this._salvarFamiliar(nome, especie_slug);
            return;
        }
        await this._salvarCompanheiro(nome, especie_slug);
    }

    async _salvarFamiliar(nome, especie_slug) {
        try {
            await this.atualizarPreview();
            const d = this.preview?.derivadas;
            if (!d) {
                if (typeof Toast !== 'undefined') Toast.error('Não foi possível calcular as derivadas.');
                return;
            }
            this.familiar = await this.familiarService.salvar(this.combatenteId, {
                especie_slug,
                nome,
                nivel_mestre: d.nivel_mestre,
                inteligencia: d.inteligencia,
                armadura_natural_bonus: d.armadura_natural_bonus,
                hp_atual: d.hp_max_sugerido,
                hp_maximo: d.hp_max_sugerido,
                ca: d.ca,
                bonus_mestre: d.bonus_mestre_especie || this.preview?.especie?.bonus_mestre || '',
                habilidades_especiais: [...(d.habilidades_especiais || [])],
                anotacoes: document.getElementById('caAnotacoesCompanheiro')?.value?.trim() || null,
            });
            this.companheiro = null;
            this._definirModo();
            if (typeof Toast !== 'undefined') Toast.success('Familiar salvo.');
            this.fecharModal();
            await this._renderLista();
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro ao salvar');
        }
    }

    async _salvarCompanheiro(nome, especie_slug) {
        const bonus = this._lerBonusAtributos();
        try {
            await this.atualizarPreview();
            const d = this.preview?.derivadas;
            if (!d) {
                if (typeof Toast !== 'undefined') Toast.error('Não foi possível calcular as derivadas.');
                return;
            }
            const a = d.atributos_efetivos || {};
            const existente = this.companheiro || (await this.companheiroService.obter(this.combatenteId));
            this.companheiro = await this.companheiroService.salvar(this.combatenteId, {
                especie_slug,
                nome,
                bonus_atributos: bonus,
                forca: a.forca ?? existente?.forca ?? 10,
                destreza: a.destreza ?? existente?.destreza ?? 10,
                constituicao: a.constituicao ?? existente?.constituicao ?? 10,
                inteligencia: a.inteligencia ?? existente?.inteligencia ?? 2,
                sabedoria: a.sabedoria ?? existente?.sabedoria ?? 10,
                carisma: a.carisma ?? existente?.carisma ?? 6,
                hp_atual: d.hp_max_sugerido ?? existente?.hp_atual ?? 1,
                hp_maximo: d.hp_max_sugerido ?? existente?.hp_maximo ?? 1,
                ca: d.ca ?? existente?.ca ?? 10,
                deslocamento: this.preview?.especie?.deslocamento ?? existente?.deslocamento ?? null,
                truques: existente?.truques || [],
                talentos: existente?.talentos || [],
                pericias: existente?.pericias || [],
                ataques: existente?.ataques?.length
                    ? existente.ataques
                    : [{ nome: 'Padrão', descricao: this.preview?.especie?.ataque_padrao || '' }],
                anotacoes: document.getElementById('caAnotacoesCompanheiro')?.value?.trim() || null,
            });
            this.familiar = null;
            this._definirModo();
            if (typeof Toast !== 'undefined') Toast.success('Companheiro salvo.');
            this.fecharModal();
            await this._renderLista();
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro ao salvar');
        }
    }

    async remover() {
        if (!this.vinculo) return;
        const rotulo = this._rotuloModo();
        const executar = async () => {
            try {
                if (this.modo === 'familiar') {
                    await this.familiarService.remover(this.combatenteId);
                    this.familiar = null;
                } else {
                    await this.companheiroService.remover(this.combatenteId);
                    this.companheiro = null;
                }
                this._definirModo();
                if (typeof Toast !== 'undefined') Toast.success(`${rotulo} removido.`);
                this.fecharModal();
                await this._renderLista();
            } catch (e) {
                if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro ao remover');
            }
        };
        if (window.ModalConfirm?.mostrar) {
            window.ModalConfirm.mostrar({
                icone: '🐾',
                titulo: `Remover ${rotulo.toLowerCase()}`,
                texto: `Remover <strong>${escapeHtml(this.vinculo.nome)}</strong>?`,
                textoConfirmar: 'Remover',
                classeConfirmar: 'modal-confirm-btn-perigo',
                onConfirmar: executar,
            });
            return;
        }
        await executar();
    }
}

const companheiroAnimalFicha = new CompanheiroAnimalFichaController();
companheiroAnimalFicha.inicializar();
