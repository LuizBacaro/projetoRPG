/**
 * Modal de condições — arena D&D 5e (estilo dnd35).
 */
export class Dnd5eCondicaoModal {
    constructor(arena) {
        this.arena = arena;
        this.selecionados = new Set();
        this._criarDom();
        this._vincular();
    }

    _criarDom() {
        if (document.getElementById('modal-condicao-dnd5e')) return;
        document.body.insertAdjacentHTML(
            'beforeend',
            `
            <div id="modal-condicao-dnd5e" class="modal-condicao-overlay" style="display:none">
                <div class="modal-condicao-container">
                    <div class="modal-condicao-header">
                        <h2>🔮 Aplicar condição</h2>
                        <button type="button" id="btn-fechar-cond-dnd5e" class="modal-condicao-fechar">✕</button>
                    </div>
                    <div class="modal-condicao-body">
                        <div class="condicao-layout">
                            <div class="condicao-combatentes-selecao">
                                <h3>🎯 Combatentes:</h3>
                                <div id="lista-combatentes-cond-dnd5e" class="lista-checkbox-combatentes"></div>
                            </div>
                            <div class="condicao-valores-aplicacao">
                                <div class="campo-grupo">
                                <label for="select-cond-dnd5e" class="modal-label">Condição</label>
                                <select id="select-cond-dnd5e" class="modal-select-condicao">
                                    <option value="">Selecione…</option>
                                </select>
                                </div>
                                <div class="campo-grupo">
                                    <label for="input-duracao-dnd5e" class="modal-label">⏰ Turnos (-1 = permanente)</label>
                                    <input type="number" id="input-duracao-dnd5e" class="modal-input-duracao" value="-1" min="-1" max="99" />
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-condicao-footer">
                        <button type="button" id="btn-cancelar-cond-dnd5e" class="btn-cancelar-condicao">Cancelar</button>
                        <button type="button" id="btn-aplicar-cond-dnd5e" class="btn-aplicar-condicao">Aplicar</button>
                    </div>
                </div>
            </div>`
        );
        this.el = document.getElementById('modal-condicao-dnd5e');
        this._preencherSelect();
    }

    _preencherSelect() {
        const sel = document.getElementById('select-cond-dnd5e');
        if (!sel) return;
        const opts = (this.arena.catalogoCondicoes || [])
            .map((c) => `<option value="${c.slug}">${c.nome}</option>`)
            .join('');
        sel.innerHTML = `<option value="">Selecione…</option>${opts}`;
    }

    _vincular() {
        document.getElementById('btn-fechar-cond-dnd5e')?.addEventListener('click', () => this.fechar());
        document.getElementById('btn-cancelar-cond-dnd5e')?.addEventListener('click', () => this.fechar());
        document.getElementById('btn-aplicar-cond-dnd5e')?.addEventListener('click', () => this.aplicar());
        this.el?.addEventListener('click', (e) => {
            if (e.target === this.el) this.fechar();
        });
    }

    abrir(combatenteIdPre) {
        this.selecionados.clear();
        if (combatenteIdPre) this.selecionados.add(combatenteIdPre);
        this._preencherSelect();
        this._renderLista();
        this.el.style.display = 'flex';
    }

    fechar() {
        if (this.el) this.el.style.display = 'none';
    }

    _renderLista() {
        const box = document.getElementById('lista-combatentes-cond-dnd5e');
        if (!box) return;
        const lista = this.arena.combatentes || [];
        if (!lista.length) {
            box.innerHTML = '<p style="color:#888;font-style:italic">Nenhum combatente</p>';
            return;
        }
        box.innerHTML = lista
            .map((c) => {
                const checked = this.selecionados.has(c.id) ? 'checked' : '';
                return `
                <div class="checkbox-combatente-item">
                    <input type="checkbox" id="cond-check-${c.id}" value="${c.id}" ${checked} />
                    <label for="cond-check-${c.id}">
                        <span class="combatente-nome">${window.escapeHtml(c.nome)}</span>
                        <span class="combatente-hp">${c.hp_atual}/${c.hp_maximo} PV</span>
                    </label>
                </div>`;
            })
            .join('');
        box.querySelectorAll('input[type=checkbox]').forEach((cb) => {
            cb.addEventListener('change', () => {
                const id = cb.value;
                if (cb.checked) this.selecionados.add(id);
                else this.selecionados.delete(id);
            });
        });
    }

    async aplicar() {
        const slug = document.getElementById('select-cond-dnd5e')?.value;
        const dur = parseInt(document.getElementById('input-duracao-dnd5e')?.value, 10);
        if (!slug) {
            Toast.error('Selecione uma condição.');
            return;
        }
        if (!this.selecionados.size) {
            Toast.error('Selecione ao menos um combatente.');
            return;
        }
        for (const id of this.selecionados) {
            await this.arena.adicionarCondicao(id, slug, dur);
        }
        this.fechar();
        Toast.success('Condição aplicada.');
    }
}
