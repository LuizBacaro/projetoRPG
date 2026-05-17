import { CompanheiroAnimalService } from '../services/CompanheiroAnimalService.js';
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
        this.service = new CompanheiroAnimalService();
        this.combatenteId = null;
        this.especies = [];
        this.companheiro = null;
        this.elegibilidade = null;
        this.preview = null;
        this.bonusAtributos = {};
    }

    async inicializar() {
        const params = new URLSearchParams(window.location.search);
        this.combatenteId = Number(params.get('id'));
        if (!Number.isFinite(this.combatenteId) || this.combatenteId <= 0) return;

        try {
            this.especies = await this.service.listarEspecies();
            this.elegibilidade = await this.service.elegibilidade(this.combatenteId);
            this.companheiro = await this.service.obter(this.combatenteId);
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

    async _renderLista() {
        const lista = document.getElementById('fichaCompanheiroAnimal');
        const btn = document.getElementById('btnAdicionarCompanheiroAnimal');
        if (!lista) return;

        if (!this.elegibilidade?.elegivel) {
            lista.innerHTML = `<span class="ficha-vazio">${escapeHtml(
                this.elegibilidade?.motivo || 'Classe sem companheiro animal'
            )}</span>`;
            if (btn) btn.hidden = true;
            return;
        }
        if (btn) btn.hidden = false;

        if (!this.companheiro) {
            lista.innerHTML = '<span class="ficha-vazio">Nenhum companheiro animal cadastrado</span>';
            if (btn) btn.textContent = '➕ Adicionar';
            return;
        }

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
        if (btn) btn.textContent = '✏️ Editar';
    }

    _preencherFormulario() {
        const sel = document.getElementById('caEspecieCompanheiro');
        const nome = document.getElementById('caNomeCompanheiro');
        const hint = document.getElementById('caElegibilidadeHint');
        if (!sel) return;

        sel.innerHTML = this.especies
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

        if (hint && this.elegibilidade) {
            hint.textContent = this.elegibilidade.elegivel
                ? `Nível efetivo: ${this.elegibilidade.nivel_efetivo} (${this.elegibilidade.classe} ${this.elegibilidade.nivel_personagem})`
                : this.elegibilidade.motivo;
        }

        const anot = document.getElementById('caAnotacoesCompanheiro');
        if (anot) anot.value = this.companheiro?.anotacoes || '';

        document.getElementById('btnRemoverCompanheiroAnimal').hidden = !this.companheiro;
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
        try {
            this.preview = await this.service.calcular(this.combatenteId, {
                especie_slug,
                bonus_atributos: this._lerBonusAtributos(),
                nome: document.getElementById('caNomeCompanheiro')?.value?.trim() || 'Companheiro',
            });
            const d = this.preview.derivadas;
            const dist = d.distribuicao_atributos || '';
            painel.innerHTML = `
                <p><strong>Derivadas (PHB)</strong> — ${escapeHtml(dist)}</p>
                <ul class="ca-preview-lista">
                    <li>HD total: ${d.hd_total} (bônus +${d.hd_bonus})</li>
                    <li>BAB ${this._fmtMod(d.bab)} · Fort ${this._fmtMod(d.fortitude)} · Ref ${this._fmtMod(d.reflexos)} · Von ${this._fmtMod(d.vontade)}</li>
                    <li>CA sugerida: ${d.ca} · PV sugeridos: ${d.hp_max_sugerido}</li>
                    <li>Talentos: ${d.talentos_total} · Truques bônus: ${d.truques_bonus}</li>
                    <li>Habilidades: ${(d.habilidades_especiais || []).map(escapeHtml).join(', ') || '—'}</li>
                </ul>`;
        } catch (e) {
            painel.innerHTML = `<p class="ficha-vazio">${escapeHtml(e.message)}</p>`;
        }
    }

    async abrirModal() {
        if (!this.elegibilidade?.elegivel) {
            if (typeof Toast !== 'undefined') Toast.error(this.elegibilidade?.motivo || 'Não elegível');
            return;
        }
        const modal = document.getElementById('modalCompanheiroAnimal');
        if (!modal) return;
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
        const bonus = this._lerBonusAtributos();
        try {
            await this.atualizarPreview();
            const d = this.preview?.derivadas;
            if (!d) {
                if (typeof Toast !== 'undefined') Toast.error('Não foi possível calcular as derivadas.');
                return;
            }
            const a = d.atributos_efetivos || {};
            const existente = this.companheiro || (await this.service.obter(this.combatenteId));
            this.companheiro = await this.service.salvar(this.combatenteId, {
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
            if (typeof Toast !== 'undefined') Toast.success('Companheiro salvo.');
            this.fecharModal();
            await this._renderLista();
        } catch (e) {
            if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro ao salvar');
        }
    }

    async remover() {
        if (!this.companheiro) return;
        const executar = async () => {
            try {
                await this.service.remover(this.combatenteId);
                this.companheiro = null;
                if (typeof Toast !== 'undefined') Toast.success('Companheiro removido.');
                this.fecharModal();
                await this._renderLista();
            } catch (e) {
                if (typeof Toast !== 'undefined') Toast.error(e.message || 'Erro ao remover');
            }
        };
        if (window.ModalConfirm?.mostrar) {
            window.ModalConfirm.mostrar({
                icone: '🐾',
                titulo: 'Remover companheiro',
                texto: `Remover <strong>${escapeHtml(this.companheiro.nome)}</strong>?`,
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
