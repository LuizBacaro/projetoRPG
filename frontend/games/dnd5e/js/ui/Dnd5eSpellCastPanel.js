/**
 * Painel de conjuração na arena D&D 5e — slots, upcast, CD, resistência e concentração.
 */
import { Dnd5eGrimorioService } from '../services/Dnd5eGrimorioService.js';
import { Dnd5eConjuracaoFichaService } from '../services/Dnd5eConjuracaoFichaService.js';

const PREPARED_SLUGS = new Set(['mago', 'wizard', 'clerigo', 'cleric', 'druida', 'druid']);

export class Dnd5eSpellCastPanel {
    constructor(arena) {
        this.arena = arena;
        this.grimorioService = new Dnd5eGrimorioService();
        this.conjuracaoService = new Dnd5eConjuracaoFichaService();
        this._magias = [];
        this._estadoConj = null;
    }

    static _mod(attr) {
        const v = Number(attr);
        if (!Number.isFinite(v)) return 0;
        return Math.floor((v - 10) / 2);
    }

    static _esc(text) {
        if (typeof escapeHtml === 'function') return escapeHtml(String(text ?? ''));
        return String(text ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    static _prof(nivel) {
        return 2 + Math.floor((Math.max(1, nivel) - 1) / 4);
    }

    async carregarMagias(combatente) {
        this._magias = [];
        this._estadoConj = null;
        if (!combatente?.personagemId || !combatente.classe) return;

        try {
            const [res, estado] = await Promise.all([
                this.grimorioService.listar(combatente.personagemId, {
                    classe: combatente.classe,
                    limit: 200,
                }),
                this.conjuracaoService.obter(combatente.personagemId).catch(() => null),
            ]);
            this._magias = res.items || [];
            this._estadoConj = estado;
            if (estado) {
                combatente.arena_conjuracao = {
                    espacos_usados: (estado.slots || []).map((s) => s.usados || 0),
                    espacos_por_nivel: (estado.slots || []).map((s) => s.total || 0),
                    magias_preparadas_ids: estado.magias_preparadas_ids || [],
                    magia_concentracao_id: estado.magia_concentracao_id ?? null,
                    prepara_magias: estado.prepara_magias,
                };
            }
        } catch {
            this._magias = [];
        }
    }

    _magiaPorId(id) {
        return this._magias.find((m) => Number(m.magia_id) === Number(id));
    }

    _slotsHtml(estado) {
        const slots = estado?.slots || [];
        if (!slots.length) return '<p class="dnd5e-spell-panel-vazio">Sem espaços de magia.</p>';
        return slots
            .map(
                (s) =>
                    `<span class="dnd5e-slot-chip">${s.nivel}º: ${s.disponiveis}/${s.total}</span>`
            )
            .join('');
    }

    _atualizarOpcoesSlot(magiaId) {
        const selSlot = document.getElementById('selectSlotArena');
        const magia = this._magiaPorId(magiaId);
        const chkRitual = document.getElementById('chkConjurarRitual');
        if (!selSlot || !magia) return;
        if (chkRitual?.checked) {
            selSlot.innerHTML = '<option value="">Ritual (sem espaço)</option>';
            selSlot.disabled = true;
            return;
        }
        const nivel = Number(magia.magia_nivel || 0);
        const slots = this._estadoConj?.slots || [];
        if (nivel <= 0) {
            selSlot.innerHTML = '<option value="0">Truque (sem espaço)</option>';
            selSlot.disabled = true;
            return;
        }
        selSlot.disabled = false;
        const niveis = new Set();
        slots.forEach((s) => {
            if (s.nivel >= nivel && s.disponiveis > 0) niveis.add(s.nivel);
        });
        const sorted = [...niveis].sort((a, b) => a - b);
        selSlot.innerHTML = sorted.length
            ? sorted
                  .map((n) => {
                      const s = slots.find((x) => x.nivel === n);
                      return `<option value="${n}">${n}º nível (${s?.disponiveis ?? 0} disp.)</option>`;
                  })
                  .join('')
            : `<option value="${nivel}">${nivel}º (sem espaço livre)</option>`;
    }

    _detalheMagia(magia) {
        const el = document.getElementById('detalheMagiaArena');
        if (!el) return;
        if (!magia) {
            el.textContent = '';
            return;
        }
        const parts = [
            magia.magia_escola ? `Escola: ${magia.magia_escola}` : null,
            magia.magia_tempo_conjuracao ? `Tempo: ${magia.magia_tempo_conjuracao}` : null,
            magia.magia_alcance ? `Alcance: ${magia.magia_alcance}` : null,
            magia.magia_componentes ? `Comp.: ${magia.magia_componentes}` : null,
            magia.magia_ataque_magico
                ? `Ataque mágico (${magia.magia_ataque_magico})`
                : null,
        ].filter(Boolean);
        el.textContent = parts.join(' · ');

        const blocoAtaque = document.getElementById('blocoAtaqueMagicoArena');
        if (blocoAtaque) {
            const precisa = Boolean(magia.magia_ataque_magico);
            blocoAtaque.style.display = precisa ? '' : 'none';
        }

        const blocoRitual = document.getElementById('blocoRitualArena');
        const chkRitual = document.getElementById('chkConjurarRitual');
        if (blocoRitual && chkRitual) {
            const podeRitual = Boolean(magia.ritual) && Number(magia.magia_nivel || 0) > 0;
            blocoRitual.style.display = podeRitual ? '' : 'none';
            if (!podeRitual) chkRitual.checked = false;
        }

        const blocoMaterial = document.getElementById('blocoMaterialConsumivelArena');
        const chkMaterial = document.getElementById('chkMaterialConsumido');
        const labelMat = document.getElementById('labelMaterialConsumivel');
        if (blocoMaterial && chkMaterial) {
            const consome = Boolean(magia.material_consumido);
            blocoMaterial.style.display = consome ? '' : 'none';
            if (!consome) chkMaterial.checked = false;
            if (labelMat && consome) {
                const mat = magia.componentes_material || 'componente material';
                labelMat.textContent = `Confirmar consumo: ${mat}`;
            }
        }
    }

    render(container, combatente) {
        if (!container) return;
        if (!combatente?.classe || !combatente.personagemId) {
            container.innerHTML =
                '<p class="dnd5e-spell-panel-vazio">Sem grimório (personagem manual ou sem classe conjuradora).</p>';
            return;
        }

        const estado = combatente.arena_conjuracao || {};
        const conc =
            estado.magia_concentracao_id != null
                ? `Concentração ativa (#${estado.magia_concentracao_id})`
                : 'Sem concentração ativa';

        const opts =
            this._magias.length > 0
                ? this._magias
                      .map((m) => {
                          const prep =
                              estado.prepara_magias &&
                              (estado.magias_preparadas_ids || []).includes(
                                  Number(m.magia_id)
                              )
                                  ? ' ★'
                                  : '';
                          return `<option value="${m.magia_id}">${Dnd5eSpellCastPanel._esc(m.magia_nome)} (nív. ${m.magia_nivel ?? '?'})${prep}</option>`;
                      })
                      .join('')
                : '<option value="">Nenhuma magia no grimório</option>';

        const classeSlug = (combatente.classe || '').toLowerCase();
        const validarPrep = PREPARED_SLUGS.has(classeSlug);

        container.innerHTML = `
            <div class="dnd5e-spell-panel">
                <h3 class="arena-secao-titulo">Conjuração</h3>
                <div class="dnd5e-spell-slots-resumo">${this._slotsHtml(this._estadoConj)}</div>
                <label class="dnd5e-spell-label" for="selectMagiaArena">Magia</label>
                <select id="selectMagiaArena" class="dnd5e-spell-select">${opts}</select>
                <p class="dnd5e-spell-detalhe" id="detalheMagiaArena"></p>
                <label class="dnd5e-spell-label" for="selectSlotArena">Espaço gasto</label>
                <select id="selectSlotArena" class="dnd5e-spell-select"></select>
                <div id="blocoRitualArena" class="dnd5e-spell-ritual-bloco" style="display:none">
                    <label class="dnd5e-spell-check">
                        <input type="checkbox" id="chkConjurarRitual"> Conjurar como ritual (+10 min, sem gastar espaço)
                    </label>
                </div>
                <div id="blocoMaterialConsumivelArena" class="dnd5e-spell-material-bloco" style="display:none">
                    <label class="dnd5e-spell-check">
                        <input type="checkbox" id="chkMaterialConsumido">
                        <span id="labelMaterialConsumivel">Confirmar consumo do material</span>
                    </label>
                </div>
                ${
                    validarPrep
                        ? '<label class="dnd5e-spell-check"><input type="checkbox" id="chkValidarPreparada" checked> Exigir magia preparada</label>'
                        : ''
                }
                <div id="blocoAtaqueMagicoArena" class="dnd5e-spell-ataque-bloco" style="display:none">
                    <label class="dnd5e-spell-label" for="inputAcAlvo">Ataque mágico — CA do alvo</label>
                    <div class="dnd5e-spell-save-row">
                        <input type="number" id="inputAcAlvo" class="dnd5e-spell-input" placeholder="CA" min="0" max="40">
                        <input type="number" id="inputRollAtaque" class="dnd5e-spell-input" placeholder="d20 ataque" min="1" max="20">
                    </div>
                </div>
                <label class="dnd5e-spell-label" for="inputSaveAlvo">Resistência do alvo (opcional)</label>
                <div class="dnd5e-spell-save-row">
                    <input type="number" id="inputModSaveAlvo" class="dnd5e-spell-input" placeholder="Mod." min="-5" max="20">
                    <input type="number" id="inputRollSaveAlvo" class="dnd5e-spell-input" placeholder="d20" min="1" max="20">
                </div>
                <button type="button" class="arena-btn-dano-cura dnd5e-btn-conjurar" id="btnConjurarArena">✨ Conjurar</button>
                <hr class="dnd5e-spell-sep">
                <p class="dnd5e-spell-conc" id="labelConcentracaoArena">${Dnd5eSpellCastPanel._esc(conc)}</p>
                <label class="dnd5e-spell-label" for="inputDanoConc">Dano recebido (teste de concentração)</label>
                <div class="dnd5e-spell-save-row">
                    <input type="number" id="inputDanoConc" class="dnd5e-spell-input" min="0" value="10">
                    <button type="button" class="arena-btn-dano-cura" id="btnTesteConc">🛡 Testar concentração</button>
                </div>
                <p class="dnd5e-spell-resultado" id="resultadoConjuracaoArena"></p>
            </div>
        `;

        const selMagia = document.getElementById('selectMagiaArena');
        const onMagia = () => {
            const id = parseInt(selMagia?.value, 10);
            this._atualizarOpcoesSlot(id);
            this._detalheMagia(this._magiaPorId(id));
        };
        selMagia?.addEventListener('change', onMagia);
        onMagia();
        document.getElementById('chkConjurarRitual')?.addEventListener('change', () => {
            const id = parseInt(selMagia?.value, 10);
            this._atualizarOpcoesSlot(id);
        });

        document.getElementById('btnConjurarArena')?.addEventListener('click', () =>
            this._conjurar(combatente)
        );
        document.getElementById('btnTesteConc')?.addEventListener('click', () =>
            this._testeConcentracao(combatente)
        );
    }

    async _conjurar(combatente) {
        const sel = document.getElementById('selectMagiaArena');
        const selSlot = document.getElementById('selectSlotArena');
        const out = document.getElementById('resultadoConjuracaoArena');
        const magiaId = parseInt(sel?.value, 10);
        if (!magiaId) {
            if (out) out.textContent = 'Selecione uma magia.';
            return;
        }

        const estado = combatente.arena_conjuracao || {
            espacos_usados: [],
            espacos_por_nivel: [],
            magias_preparadas_ids: [],
            magia_concentracao_id: null,
        };
        const magia = this._magiaPorId(magiaId);
        const nivelMagia = Number(magia?.magia_nivel || 0);
        const comoRitual = Boolean(document.getElementById('chkConjurarRitual')?.checked);
        const confirmarMaterial = Boolean(
            document.getElementById('chkMaterialConsumido')?.checked
        );
        if (magia?.material_consumido && !confirmarMaterial) {
            if (out) {
                out.textContent = 'Marque a confirmação de consumo do material.';
            }
            return;
        }
        let nivelSlot = parseInt(selSlot?.value, 10);
        if (nivelMagia <= 0 || comoRitual) nivelSlot = null;
        else if (!Number.isFinite(nivelSlot)) nivelSlot = nivelMagia;

        const modSave = document.getElementById('inputModSaveAlvo')?.value;
        const rollSave = document.getElementById('inputRollSaveAlvo')?.value;
        const chkPrep = document.getElementById('chkValidarPreparada');

        const payload = {
            conjurador_id: combatente.id,
            nome: combatente.nome,
            classe: combatente.classe,
            nivel_personagem: combatente.nivel || 1,
            magia_id: magiaId,
            personagem_id: combatente.personagemId,
            bonus_proficiencia: Dnd5eSpellCastPanel._prof(combatente.nivel || 1),
            mod_inteligencia: Dnd5eSpellCastPanel._mod(combatente.inteligencia),
            mod_sabedoria: Dnd5eSpellCastPanel._mod(combatente.sabedoria),
            mod_carisma: Dnd5eSpellCastPanel._mod(combatente.carisma),
            mod_destreza: Dnd5eSpellCastPanel._mod(combatente.destreza),
            mod_constituicao: Dnd5eSpellCastPanel._mod(combatente.constituicao),
            espacos_por_nivel: estado.espacos_por_nivel || [],
            espacos_usados_por_nivel: estado.espacos_usados || [],
            magia_concentracao_id: estado.magia_concentracao_id,
            nivel_slot_usado: nivelSlot,
            magias_preparadas_ids: estado.magias_preparadas_ids || [],
            validar_preparacao: Boolean(chkPrep?.checked),
            como_ritual: comoRitual,
            confirmar_material_consumido: confirmarMaterial,
        };
        if (modSave !== '' && rollSave !== '') {
            payload.teste_resistencia_mod_alvo = parseInt(modSave, 10);
            payload.rolagem_salvaguarda_alvo = parseInt(rollSave, 10);
        }
        const magiaAtk = this._magiaPorId(magiaId);
        if (magiaAtk?.magia_ataque_magico) {
            const ac = document.getElementById('inputAcAlvo')?.value;
            if (ac === '' || ac === undefined) {
                if (out) out.textContent = 'Informe a CA do alvo para ataque mágico.';
                return;
            }
            payload.ac_alvo = parseInt(ac, 10);
            const rollAtk = document.getElementById('inputRollAtaque')?.value;
            if (rollAtk !== '') {
                payload.rolagem_ataque_d20 = parseInt(rollAtk, 10);
            }
        }

        try {
            const res = await this.arena.cs.conjurarMagia(payload);
            combatente.arena_conjuracao = {
                ...estado,
                espacos_usados: res.espacos_usados_por_nivel || [],
                magia_concentracao_id: res.magia_concentracao_id ?? null,
            };
            if (combatente.personagemId && res.sucesso && res.nivel_slot_gasto && !res.conjurada_como_ritual) {
                try {
                    await this.conjuracaoService.gastarSlot(
                        combatente.personagemId,
                        res.nivel_slot_gasto,
                        1
                    );
                    this._estadoConj = await this.conjuracaoService.obter(
                        combatente.personagemId
                    );
                } catch {
                    /* estado local da arena já foi atualizado */
                }
            }
            let msg = res.mensagem || (res.sucesso ? 'Conjurada.' : 'Falhou.');
            if (res.dc) msg += ` · CD ${res.dc}`;
            if (res.componentes) msg += ` · ${res.componentes}`;
            if (res.ataque_total != null) {
                msg += res.ataque_acertou
                    ? ` · Ataque ${res.ataque_total} (acerto)`
                    : ` · Ataque ${res.ataque_total} (erro)`;
            }
            if (res.dano_total) msg += ` · Dano ${res.dano_total}`;
            if (res.conjurada_como_ritual) msg += ' · Ritual';
            if (res.material_consumido_confirmado) msg += ' · Material consumido';
            if (out) out.textContent = msg;
            const concEl = document.getElementById('labelConcentracaoArena');
            if (concEl) {
                concEl.textContent =
                    res.magia_concentracao_id != null
                        ? `Concentração: ${res.magia_nome || magiaId}`
                        : 'Sem concentração ativa';
            }
            const grid = document.querySelector('.dnd5e-spell-slots-resumo');
            if (grid && this._estadoConj) grid.innerHTML = this._slotsHtml(this._estadoConj);
            if (res.sucesso && typeof Toast !== 'undefined') Toast.success(msg);
        } catch (e) {
            if (out) out.textContent = e.message || 'Erro ao conjurar';
            if (typeof Toast !== 'undefined') Toast.error(e.message);
        }
    }

    async _testeConcentracao(combatente) {
        const out = document.getElementById('resultadoConjuracaoArena');
        const dano = parseInt(document.getElementById('inputDanoConc')?.value, 10) || 0;
        const estado = combatente.arena_conjuracao || {};
        if (!estado.magia_concentracao_id) {
            if (out) out.textContent = 'Nenhuma magia em concentração.';
            return;
        }
        try {
            const res = await this.arena.cs.testeConcentracao({
                conjurador_id: combatente.id,
                dano_recebido: dano,
                mod_constituicao: Dnd5eSpellCastPanel._mod(combatente.constituicao),
                bonus_proficiencia: Dnd5eSpellCastPanel._prof(combatente.nivel || 1),
                magia_concentracao_id: estado.magia_concentracao_id,
            });
            combatente.arena_conjuracao.magia_concentracao_id =
                res.magia_concentracao_id ?? null;
            const msg = `${res.mensagem} (d20=${res.rolagem} → ${res.total} vs CD ${res.dc})`;
            if (out) out.textContent = msg;
            const concEl = document.getElementById('labelConcentracaoArena');
            if (concEl) {
                concEl.textContent = res.magia_concentracao_id
                    ? `Concentração: magia #${res.magia_concentracao_id}`
                    : 'Sem concentração ativa';
            }
        } catch (e) {
            if (out) out.textContent = e.message || 'Erro no teste';
        }
    }
}
