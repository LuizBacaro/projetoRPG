/**
 * Modal de conjuração na arena — alvo, upcast, ritual e material.
 */
import {
    magiaPrecisaAlvo,
    normalizarSave,
} from '../arena/Dnd5eArenaConjuracaoHelper.js';

const esc = (str) => {
    if (typeof window !== 'undefined' && typeof window.escapeHtml === 'function') {
        return window.escapeHtml(String(str ?? ''));
    }
    return String(str ?? '');
};

export class Dnd5eArenaConjuracaoModal {
    constructor(arena) {
        this.arena = arena;
        this._ctx = null;
        this._criarDom();
        this._vincular();
    }

    _criarDom() {
        if (document.getElementById('modal-conjuracao-dnd5e')) return;
        document.body.insertAdjacentHTML(
            'beforeend',
            `
            <div id="modal-conjuracao-dnd5e" class="modal-condicao-overlay dnd5e-modal-conj" style="display:none">
                <div class="modal-condicao-container dnd5e-modal-conj-container">
                    <div class="modal-condicao-header">
                        <h2 id="dnd5e_conj_titulo">🔮 Conjurar magia</h2>
                        <button type="button" id="btn-fechar-conj-dnd5e" class="modal-condicao-fechar">✕</button>
                    </div>
                    <div class="modal-condicao-body">
                        <p id="dnd5e_conj_resumo" class="dnd5e-conj-modal-resumo"></p>
                        <div class="dnd5e-conj-modal-campos">
                            <div class="campo-grupo" id="dnd5e_conj_alvo_wrap">
                                <label for="dnd5e_conj_alvo" class="modal-label">Alvo</label>
                                <select id="dnd5e_conj_alvo" class="modal-select-condicao"></select>
                            </div>
                            <div class="campo-grupo" id="dnd5e_conj_slot_wrap" hidden>
                                <label for="dnd5e_conj_slot" class="modal-label">Espaço gasto (upcast)</label>
                                <select id="dnd5e_conj_slot" class="modal-select-condicao"></select>
                            </div>
                            <label class="arena-check" id="dnd5e_conj_ritual_wrap" hidden>
                                <input type="checkbox" id="dnd5e_conj_ritual" /> Conjurar como ritual (sem gastar espaço)
                            </label>
                            <label class="arena-check" id="dnd5e_conj_material_wrap" hidden>
                                <input type="checkbox" id="dnd5e_conj_material" /> Confirmar consumo de material
                            </label>
                        </div>
                    </div>
                    <div class="modal-condicao-footer">
                        <button type="button" id="btn-cancelar-conj-dnd5e" class="btn-cancelar-condicao">Cancelar</button>
                        <button type="button" id="btn-aplicar-conj-dnd5e" class="btn-aplicar-condicao">Conjurar</button>
                    </div>
                </div>
            </div>`
        );
        this.el = document.getElementById('modal-conjuracao-dnd5e');
    }

    _vincular() {
        document.getElementById('btn-fechar-conj-dnd5e')?.addEventListener('click', () => this.fechar());
        document.getElementById('btn-cancelar-conj-dnd5e')?.addEventListener('click', () => this.fechar());
        document.getElementById('btn-aplicar-conj-dnd5e')?.addEventListener('click', () => this._confirmar());
        this.el?.addEventListener('click', (e) => {
            if (e.target === this.el) this.fechar();
        });
    }

    abrir(ctx) {
        this._ctx = ctx;
        const { combatente, magia, estado } = ctx;
        const nivel = Number(magia?.magia_nivel ?? ctx.nivel ?? 0) || 0;
        const precisaAlvo = magiaPrecisaAlvo(magia);

        document.getElementById('dnd5e_conj_titulo').textContent =
            `🔮 ${magia?.magia_nome || 'Magia'}`;

        const partes = [];
        if (nivel === 0) partes.push('Truque');
        else partes.push(`${nivel}º nível`);
        if (magia?.magia_dano) partes.push(`dano ${magia.magia_dano}`);
        const save = normalizarSave(magia?.teste_resistencia);
        if (save !== 'nenhum') partes.push(`resistência ${save}`);
        if (magia?.magia_ataque_magico) partes.push('ataque mágico');
        if (magia?.requer_concentracao) partes.push('concentração');
        if (estado?.habilidade_primaria) {
            partes.push(`CD: mod. ${String(estado.habilidade_primaria).toUpperCase()}`);
        }
        document.getElementById('dnd5e_conj_resumo').textContent = partes.join(' · ');

        const alvoWrap = document.getElementById('dnd5e_conj_alvo_wrap');
        const selAlvo = document.getElementById('dnd5e_conj_alvo');
        alvoWrap.hidden = !precisaAlvo;
        if (precisaAlvo) {
            const lista = (this.arena.combatentes || []).filter((c) => c.id !== combatente.id);
            const fallback = this.arena.combatentes || [];
            const opts = (lista.length ? lista : fallback)
                .map(
                    (c) =>
                        `<option value="${c.id}">${esc(c.nome)} (CA ${c.ca})</option>`
                )
                .join('');
            selAlvo.innerHTML = opts;
            const toolAlvo = this.arena.el('toolAlvoDano')?.value;
            if (toolAlvo && [...selAlvo.options].some((o) => o.value === toolAlvo)) {
                selAlvo.value = toolAlvo;
            }
        }

        const slotWrap = document.getElementById('dnd5e_conj_slot_wrap');
        const selSlot = document.getElementById('dnd5e_conj_slot');
        if (nivel >= 1 && estado?.slots) {
            const disponiveis = (estado.slots || []).filter(
                (s) => Number(s.nivel) >= nivel && Number(s.disponiveis) > 0
            );
            if (disponiveis.length) {
                slotWrap.hidden = false;
                selSlot.innerHTML = disponiveis
                    .map(
                        (s) =>
                            `<option value="${s.nivel}">${s.nivel}º (${s.disponiveis} disp.)</option>`
                    )
                    .join('');
            } else {
                slotWrap.hidden = true;
            }
        } else {
            slotWrap.hidden = true;
        }

        const ritualWrap = document.getElementById('dnd5e_conj_ritual_wrap');
        const ritualCb = document.getElementById('dnd5e_conj_ritual');
        ritualWrap.hidden = !(magia?.ritual && nivel >= 1);
        if (ritualCb) ritualCb.checked = false;

        const matWrap = document.getElementById('dnd5e_conj_material_wrap');
        const matCb = document.getElementById('dnd5e_conj_material');
        matWrap.hidden = !magia?.material_consumido;
        if (matCb) matCb.checked = false;

        this.el.style.display = 'flex';
    }

    fechar() {
        if (this.el) this.el.style.display = 'none';
        this._ctx = null;
    }

    _confirmar() {
        const ctx = this._ctx;
        if (!ctx) return;
        const precisaAlvo = magiaPrecisaAlvo(ctx.magia);
        const alvoId = document.getElementById('dnd5e_conj_alvo')?.value;
        const alvo = alvoId ? this.arena.combatentePorId(alvoId) : null;
        if (precisaAlvo && !alvo) {
            Toast.error('Selecione um alvo.');
            return;
        }
        if (ctx.magia?.material_consumido && !document.getElementById('dnd5e_conj_material')?.checked) {
            Toast.error('Confirme o consumo do material.');
            return;
        }
        const opts = {
            alvo,
            condicoes_atacante: this.arena.slugsCondicoes(ctx.combatente),
            condicoes_alvo: alvo ? this.arena.slugsCondicoes(alvo) : [],
            como_ritual: !!document.getElementById('dnd5e_conj_ritual')?.checked,
            confirmar_material: !!document.getElementById('dnd5e_conj_material')?.checked,
        };
        const slotSel = document.getElementById('dnd5e_conj_slot');
        if (slotSel && !document.getElementById('dnd5e_conj_slot_wrap')?.hidden) {
            opts.nivel_slot = parseInt(slotSel.value, 10);
        }
        this.fechar();
        ctx.onConfirm(opts);
    }
}
