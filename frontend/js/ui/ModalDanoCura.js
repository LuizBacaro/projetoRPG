/**
 * ModalDanoCura
 * SRP: gerencia apenas a UI do modal de aplicação de dano/cura
 * DIP: depende de DanoCuraService e ArenaController via injeção
 *
 * CORRIGIDO: carregarCombatentes() agora renderiza HP para
 * jogadores, monstros e NPCs igualmente
 */

// ── Helper de Toast (fora da classe — SRP) ────────────────────────────────
function mostrarToast(mensagem, tipo = 'success') {
    if (typeof Toast !== 'undefined') {
        tipo === 'success' ? Toast.success(mensagem) : Toast.error(mensagem);
        return;
    }
    const toast = document.createElement('div');
    toast.className  = 'toast show';
    toast.style.cssText = `
        position: fixed; bottom: 2rem; right: 2rem;
        padding: 1rem 2rem;
        background: ${tipo === 'success' ? '#32CD32' : '#DC143C'};
        color: white; border-radius: 8px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,.3);
        z-index: 10000;
    `;
    toast.textContent = mensagem;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ── Classe principal ──────────────────────────────────────────────────────
class ModalDanoCura {

    constructor(danoCuraService, arenaController) {
        this.danoCuraService         = danoCuraService;
        this.arenaController         = arenaController;
        this.modalElement            = null;
        this.combatentesSelecionados = new Set();
        this.inicializar();
    }

    // ── Init ──────────────────────────────────────────────────────────────

    inicializar() {
        this.modalElement = document.getElementById('modalDanoCura');
        this.vincularEventos();
    }

    vincularEventos() {
        // Inputs numéricos — aceita apenas valores positivos
        const inputDano = document.getElementById('inputDanoModal');
        const inputCura = document.getElementById('inputCuraModal');

        if (inputDano) inputDano.addEventListener('input', () => {
            if (parseInt(inputDano.value) > 0) inputCura.value = '0';
        });

        if (inputCura) inputCura.addEventListener('input', () => {
            if (parseInt(inputCura.value) > 0) inputDano.value = '0';
        });
    }

    // ── Abrir / Fechar ────────────────────────────────────────────────────

    abrir() {
        this.combatentesSelecionados.clear();
        this.limparInputs();
        this.carregarCombatentes();
        this.modalElement.classList.add('show');
    }

    fechar() {
        this.modalElement.classList.remove('show');
    }

    limparInputs() {
        const inputDano = document.getElementById('inputDanoModal');
        const inputCura = document.getElementById('inputCuraModal');
        if (inputDano) inputDano.value = '0';
        if (inputCura) inputCura.value = '0';
    }

    // ── Renderiza lista de combatentes ────────────────────────────────────
    //
    // CORREÇÃO: combatentes.tipo pode ser 'jogador', 'monstro' ou 'npc'
    // O HP é exibido para TODOS os tipos — a condição anterior
    // limitava ao tipo 'jogador' implicitamente por usar c.hp_atual
    // que monstros/NPCs não tinham no objeto local (vinham sem hp_atual
    // atualizado). Agora usa hp_atual ?? hp_maximo como fallback.

    carregarCombatentes() {
        const combatentes = this.arenaController?.combatentes;
        const container   = document.getElementById('listaCombatentesDanoCura');

        if (!container) return;

        if (!combatentes || !combatentes.length) {
            container.innerHTML = '<p style="color:#64748b;text-align:center">Nenhum combatente na arena</p>';
            return;
        }

        container.innerHTML = '';

        combatentes.forEach(c => {
            // Garante hp_atual para monstros e NPCs que podem não ter
            // o campo atualizado no objeto local — usa hp_maximo como fallback
            const hpAtual  = c.hp_atual  ?? c.hp_maximo ?? '—';
            const hpMaximo = c.hp_maximo ?? '—';

            // Badge por tipo
            const badgeClass = {
                jogador: 'badge-jogador',
                monstro: 'badge-monstro',
                npc:     'badge-npc'
            }[c.tipo] ?? 'badge-jogador';

            // Cor do HP baseada no percentual
            let hpClass = 'hp-normal';
            if (hpMaximo > 0) {
                const pct = (hpAtual / hpMaximo) * 100;
                if (pct <= 25)      hpClass = 'hp-critico';
                else if (pct <= 50) hpClass = 'hp-baixo';
            }

            const item = document.createElement('div');
            item.className   = 'combatente-dano-item';
            item.dataset.id  = c.id;

            item.innerHTML = `
                <label class="combatente-dano-label">
                    <input
                        type="checkbox"
                        class="combatente-checkbox"
                        data-id="${c.id}"
                    />
                    <div class="combatente-dano-info">
                        <span class="combatente-dano-nome">${c.nome}</span>
                        <div class="combatente-dano-meta">
                            <span class="badge ${badgeClass}">${c.tipo}</span>
                            <span class="combatente-hp ${hpClass}">${hpAtual}/${hpMaximo} PV</span>
                        </div>
                    </div>
                </label>
            `;

            // Toggle seleção ao clicar no checkbox
            const checkbox = item.querySelector('.combatente-checkbox');
            checkbox.addEventListener('change', () => {
                this.toggleCombatente(c.id);
                // Feedback visual no item
                item.classList.toggle('selecionado', checkbox.checked);
            });

            container.appendChild(item);
        });
    }

    // ── Toggle seleção ────────────────────────────────────────────────────

    toggleCombatente(combatenteId) {
        if (this.combatentesSelecionados.has(combatenteId)) {
            this.combatentesSelecionados.delete(combatenteId);
        } else {
            this.combatentesSelecionados.add(combatenteId);
        }
    }

    // ── Aplicar dano / cura ───────────────────────────────────────────────

    async aplicar() {
        try {
            const dano = parseInt(document.getElementById('inputDanoModal')?.value) || 0;
            const cura = parseInt(document.getElementById('inputCuraModal')?.value) || 0;

            // Valida entrada
            const validacao = this.danoCuraService.validarEntrada(dano, cura);
            if (!validacao.valido) {
                mostrarToast(validacao.erro, 'error');
                return;
            }

            // Valida seleção
            if (this.combatentesSelecionados.size === 0) {
                mostrarToast('Selecione pelo menos um combatente', 'error');
                return;
            }

            const ids = Array.from(this.combatentesSelecionados);

            let resultados;
            if (validacao.tipo === 'dano') {
                resultados = await this.danoCuraService.aplicarDanoEmMassa(ids, validacao.valor);
                mostrarToast(`💥 ${validacao.valor} de dano aplicado a ${ids.length} combatente(s)!`);
            } else {
                resultados = await this.danoCuraService.aplicarCuraEmMassa(ids, validacao.valor);
                mostrarToast(`💚 ${validacao.valor} de cura aplicada a ${ids.length} combatente(s)!`);
            }

            // Atualiza os combatentes na arena
            resultados.forEach(resultado => {
                if (resultado?.combatente) {
                    this.arenaController.atualizarCombatente(resultado.combatente);
                }
            });

            this.fechar();

        } catch (err) {
            mostrarToast(err.message || 'Erro ao aplicar dano/cura', 'error');
            console.error('❌ Erro ao aplicar dano/cura:', err);
        }
    }
}