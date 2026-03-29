/**
 * Helper para exibir toasts
 * Função auxiliar fora da classe (SRP)
 */
function mostrarToast(mensagem, tipo = 'success') {
    if (typeof Toast !== 'undefined') {
        tipo === 'success' ? Toast.success(mensagem) : Toast.error(mensagem);
    } else {
        const toast = document.createElement('div');
        toast.className    = 'toast show';
        toast.style.cssText = `
            position: fixed; bottom: 2rem; right: 2rem;
            padding: 1rem 2rem;
            background: ${tipo === 'success' ? '#32CD32' : '#DC143C'};
            color: white; border-radius: 8px;
            font-family: var(--fonte-texto); font-weight: bold;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            z-index: 10000;
        `;
        toast.textContent = mensagem;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
}

/**
 * Componente UI do modal de aplicação de dano/cura
 * SRP: apenas gerencia a UI do modal
 * DIP: depende de DanoCuraService e ArenaController via injeção
 */
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

    // ── Eventos ───────────────────────────────────────────────────────────

    vincularEventos() {
        const inputDano = document.getElementById('inputDanoModal');
        const inputCura = document.getElementById('inputCuraModal');

        if (!inputDano || !inputCura) return;

        // Quando preencher dano, zera cura e vice-versa
        inputDano.addEventListener('input', () => {
            if (parseInt(inputDano.value) > 0) inputCura.value = '0';
        });
        inputCura.addEventListener('input', () => {
            if (parseInt(inputCura.value) > 0) inputDano.value = '0';
        });
    }

    // ── Abrir / Fechar ────────────────────────────────────────────────────

    abrir() {
        this.carregarCombatentes();
        this.combatentesSelecionados.clear();
        this.limparInputs();
        this.modalElement.classList.add('show');
    }

    fechar() {
        this.modalElement.classList.remove('show');
    }

    // ── Helpers ───────────────────────────────────────────────────────────

    limparInputs() {
        const inputDano = document.getElementById('inputDanoModal');
        const inputCura = document.getElementById('inputCuraModal');
        if (inputDano) inputDano.value = '0';
        if (inputCura) inputCura.value = '0';
    }

    // ── Render: Lista de combatentes ──────────────────────────────────────
    //
    // REGRA DE NEGÓCIO:
    //   jogador  → exibe HP (ex: "45/45 PV")
    //   monstro  → NÃO exibe HP
    //   npc      → NÃO exibe HP

    carregarCombatentes() {
        const combatentes = this.arenaController.combatentes;
        const container   = document.getElementById('listaCombatentesDanoCura');

        if (!combatentes || combatentes.length === 0) {
            container.innerHTML = '<p style="color:#888;font-style:italic;padding:1rem;">⚠️ Nenhum combatente disponível</p>';
            return;
        }

        container.innerHTML = combatentes.map(c => {

            // Só jogadores têm o HP exibido publicamente
            const mostrarHP  = c.tipo.toLowerCase() === 'jogador';
            const spanHP     = mostrarHP
                ? `<span class="combatente-hp">${c.hp_atual}/${c.hp_maximo} PV</span>`
                : '';

            return `
                <div class="checkbox-combatente-item">
                    <input
                        type="checkbox"
                        id="dano-check-${c.id}"
                        value="${c.id}"
                        onchange="modalDanoCuraInstance.toggleCombatente(${c.id})"
                    >
                    <label for="dano-check-${c.id}">
                        <span class="combatente-nome">${escapeHtml(c.nome)}</span>
                        ${spanHP}
                        <span class="badge badge-${c.tipo.toLowerCase()}">${c.tipo}</span>
                    </label>
                </div>
            `;
        }).join('');
    }

    // ── Toggle combatente selecionado ─────────────────────────────────────

    toggleCombatente(combatenteId) {
        if (this.combatentesSelecionados.has(combatenteId)) {
            this.combatentesSelecionados.delete(combatenteId);
        } else {
            this.combatentesSelecionados.add(combatenteId);
        }
        console.log('✅ Combatentes selecionados:', Array.from(this.combatentesSelecionados));
    }

    // ── Aplicar dano ou cura ──────────────────────────────────────────────

    async aplicar() {
        try {
            console.log('🎯 Iniciando aplicação de dano/cura...');

            const dano = parseInt(document.getElementById('inputDanoModal').value) || 0;
            const cura = parseInt(document.getElementById('inputCuraModal').value) || 0;

            const validacao = this.danoCuraService.validarEntrada(dano, cura);

            if (this.combatentesSelecionados.size === 0) {
                mostrarToast('⚠️ Selecione ao menos um combatente!', 'error');
                return;
            }

            if (!validacao.valido) {
                mostrarToast(`⚠️ ${validacao.erro}`, 'error');
                return;
            }

            const ids   = Array.from(this.combatentesSelecionados);
            const tipo  = validacao.tipo;   // 'dano' | 'cura'
            const valor = validacao.valor;

            if (tipo === 'dano') {
                await this.danoCuraService.aplicarDanoEmMassa(ids, valor);
            } else {
                await this.danoCuraService.aplicarCuraEmMassa(ids, valor);
            }

            // Sincroniza HP nos combatentes locais do ArenaController
            ids.forEach(id => {
                const c = this.arenaController.combatentes.find(x => x.id === id);
                if (!c) return;

                if (tipo === 'dano') {
                    c.hp_atual = Math.max(0, c.hp_atual - valor);
                } else {
                    c.hp_atual = Math.min(c.hp_maximo, c.hp_atual + valor);
                }
            });

            // Atualiza a interface da arena
            this.arenaController.atualizarInterface();

            const emoji = tipo === 'dano' ? '⚔️' : '💚';
            mostrarToast(`${emoji} ${tipo === 'dano' ? 'Dano' : 'Cura'} de ${valor} aplicado!`, 'success');

            this.fechar();

        } catch (erro) {
            console.error('❌ Erro ao aplicar dano/cura:', erro);
            mostrarToast(`❌ Erro: ${erro.message}`, 'error');
        }
    }
}