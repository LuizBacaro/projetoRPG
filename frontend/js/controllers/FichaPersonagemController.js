/**
 * FichaPersonagemController.js
 * SRP: Controlar renderização da ficha do personagem
 * SOLID: DIP via constructor injection de services
 */

import { CombatenteService } from '../services/CombatenteService.js';
import { getApiUrl         } from '../config/api.config.js';

export class FichaPersonagemController {

    constructor() {
        this.combatenteService = new CombatenteService();
        this.token             = localStorage.getItem('token');
        this.combatente        = null;
        console.log('✅ FichaPersonagemController inicializado');
    }

    async inicializar() {
        try {
            const params       = new URLSearchParams(window.location.search);
            const combatenteId = params.get('id');

            if (!combatenteId) throw new Error('ID do combatente não fornecido');

            console.log('🎯 Carregando ficha do combatente:', combatenteId);

            this.combatente = await this.combatenteService.obterCombatente(parseInt(combatenteId));

            // ✅ Expor globalmente para debug no console
            window._fichaController = this;

            console.log('✅ Combatente carregado:', this.combatente.nome);
            console.log('📦 magias_slots recebidos:', this.combatente.magias_slots);
            console.log('⚔️ ataques recebidos:', this.combatente.ataques);

            // ── Renderizar tudo ──
            this.renderizarIdentidade();
            this.renderizarAtributos();
            this.renderizarDefesa();
            this.renderizarResistencias();
            this.renderizarAtaques();
            this.renderizarSlotsDeMapia();    // ✅ slots de magia
            await this.carregarRenderizarPericias(parseInt(combatenteId));

            console.log('✅ Ficha carregada com sucesso');

        } catch (error) {
            console.error('❌ Erro ao inicializar ficha:', error);
            this.mostrarErro('Erro ao carregar ficha: ' + error.message);
        }
    }

    // ─────────────────────────────────────────────────────────
    // IDENTIDADE
    // ─────────────────────────────────────────────────────────

    renderizarIdentidade() {
        const nome        = document.getElementById('fichaNome');
        const raca        = document.getElementById('fichaRaca');
        const classe      = document.getElementById('fichaClasse');
        const tipo        = document.getElementById('fichaTipo');
        const nivel       = document.getElementById('fichaNivel');
        const placeholder = document.getElementById('fichaFotoPlaceholder');
        const foto        = document.getElementById('fichaFoto');

        if (nome)   nome.textContent   = this.combatente.nome;
        if (raca)   raca.textContent   = this.combatente.raca   || '—';
        if (classe) classe.textContent = this.combatente.classe || '—';
        if (tipo)   tipo.textContent   = this.combatente.tipo   || 'jogador';
        if (nivel)  nivel.textContent  = this.combatente.nivel  || 1;

        if (this.combatente.foto_url) {
            if (foto) {
                foto.src = this.combatente.foto_url;
                foto.classList.add('carregada');
            }
            if (placeholder) placeholder.style.display = 'none';
        } else {
            const emojiMap = { jogador: '🧙', npc: '🤝', monstro: '👹' };
            if (placeholder) placeholder.textContent = emojiMap[this.combatente.tipo] || '⚔️';
        }

        console.log('✅ Identidade renderizada');
    }

    // ─────────────────────────────────────────────────────────
    // ATRIBUTOS
    // ─────────────────────────────────────────────────────────

    renderizarAtributos() {
        const map = {
            forca:         'For',
            destreza:      'Des',
            constituicao:  'Con',
            inteligencia:  'Int',
            sabedoria:     'Sab',
            carisma:       'Car',
        };

        Object.entries(map).forEach(([attr, abrev]) => {
            const valor   = this.combatente[attr] || 10;
            const mod     = Math.floor((valor - 10) / 2);
            const elValor = document.getElementById(`ficha${abrev}`);
            const elMod   = document.getElementById(`ficha${abrev}Mod`);
            if (elValor) elValor.textContent = valor;
            if (elMod)   elMod.textContent   = mod >= 0 ? `+${mod}` : `${mod}`;
        });

        console.log('✅ Atributos renderizados');
    }

    // ─────────────────────────────────────────────────────────
    // DEFESA
    // ─────────────────────────────────────────────────────────

    renderizarDefesa() {
        const ca         = document.getElementById('fichaCa');
        const toque      = document.getElementById('fichaToque');
        const surpresa   = document.getElementById('fichaSurpresa');
        const pv         = document.getElementById('fichaPv');
        const pvFill     = document.getElementById('fichaPvFill');
        const iniciativa = document.getElementById('fichaIniciativa');

        if (ca)       ca.textContent      = this.combatente.ca       ?? 10;
        if (toque)    toque.textContent    = this.combatente.toque    ?? 10;
        if (surpresa) surpresa.textContent = this.combatente.surpresa ?? 10;

        if (pv) pv.textContent = `${this.combatente.hp_atual ?? 0}/${this.combatente.hp_maximo ?? 0}`;

        if (pvFill) {
            const pct = (this.combatente.hp_maximo || 0) > 0
                ? ((this.combatente.hp_atual || 0) / this.combatente.hp_maximo) * 100
                : 0;
            pvFill.style.width = `${Math.max(0, Math.min(100, pct))}%`;
        }

        if (iniciativa) {
            const ini = this.combatente.iniciativa || 0;
            iniciativa.textContent = ini >= 0 ? `+${ini}` : `${ini}`;
        }

        console.log('✅ Defesa renderizada');
    }

    // ─────────────────────────────────────────────────────────
    // RESISTÊNCIAS
    // ─────────────────────────────────────────────────────────

    renderizarResistencias() {
        const fort   = document.getElementById('fichaFort');
        const reflex = document.getElementById('fichaReflex');
        const vont   = document.getElementById('fichaVont');

        const fmt = v => v >= 0 ? `+${v}` : `${v}`;
        if (fort)   fort.textContent   = fmt(this.combatente.fortitude || 0);
        if (reflex) reflex.textContent = fmt(this.combatente.reflexos  || 0);
        if (vont)   vont.textContent   = fmt(this.combatente.vontade   || 0);

        console.log('✅ Resistências renderizadas');
    }

    // ─────────────────────────────────────────────────────────
    // ATAQUES
    // ─────────────────────────────────────────────────────────

    renderizarAtaques() {
        const lista = document.getElementById('fichaAtaquesLista');
        if (!lista) return;

        const ataques = this.combatente.ataques || [];

        if (ataques.length === 0) {
            lista.innerHTML = '<div class="ficha-ataque-vazio">Nenhum ataque cadastrado</div>';
            return;
        }

        lista.innerHTML = ataques.map(a => `
            <div class="ficha-ataque-linha">
                <span class="ficha-ataque-nome">${a.nome || '—'}</span>
                <span class="ficha-ataque-bonus">${a.bonus_ataque || '+0'}</span>
                <span class="ficha-ataque-dano">${a.dano || '—'}</span>
            </div>
        `).join('');

        console.log('✅ Ataques renderizados:', ataques.length);
    }

    // ─────────────────────────────────────────────────────────
    // SLOTS DE MAGIA
    // ─────────────────────────────────────────────────────────

    renderizarSlotsDeMapia() {
        const grid      = document.getElementById('fichaMagiasGrid');
        const secao     = document.getElementById('secaoMagias');
        if (!grid) {
            console.warn('⚠️ #fichaMagiasGrid não encontrado no DOM');
            return;
        }

        const slots      = this.combatente.magias_slots || [];
        const slotsAtivos = slots.filter(s => (s.total || 0) > 0);

        console.log('🔮 Todos os slots:', slots);
        console.log('🔮 Slots ativos (total > 0):', slotsAtivos);

        // ✅ Mostrar seção sempre que o personagem for jogador
        // (independente de ser conjurador — GrimorioController cuida do botão)
        if (secao && this.combatente.tipo === 'jogador') {
            secao.style.display = 'flex';
        }

        if (slotsAtivos.length === 0) {
            grid.innerHTML = '<div class="ficha-magia-vazio">Nenhum slot cadastrado</div>';
            console.log('ℹ️ Nenhum slot de magia ativo');
            return;
        }

        // Ordenar por nível
        slotsAtivos.sort((a, b) => a.nivel - b.nivel);

        grid.innerHTML = slotsAtivos.map(slot => {
            const usados      = slot.usados || 0;
            const total       = slot.total  || 0;
            const disponiveis = total - usados;
            const pct         = total > 0 ? (disponiveis / total) * 100 : 0;
            const labelNivel  = slot.nivel === 0 ? 'Truques' : `${slot.nivel}° Nível`;

            // Verde > 50%, Amarelo > 25%, Vermelho <= 25%
            const corBarra = pct > 50 ? '#4ade80' : pct > 25 ? '#facc15' : '#f87171';

            return `
                <div class="ficha-slot-linha">
                    <div class="ficha-slot-topo">
                        <span class="ficha-slot-nivel">${labelNivel}</span>
                        <span class="ficha-slot-contagem">${disponiveis}/${total}</span>
                    </div>
                    <div class="ficha-slot-barra-wrap">
                        <div class="ficha-slot-barra-fill"
                             style="width:${pct}%; background:${corBarra}">
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        console.log('✅ Slots de magia renderizados:', slotsAtivos.length);
    }

    // ─────────────────────────────────────────────────────────
    // PERÍCIAS
    // ─────────────────────────────────────────────────────────

    async carregarRenderizarPericias(combatenteId) {
        try {
            const url = getApiUrl(`/pericias/${combatenteId}/listar`);
            const res = await fetch(url, {
                headers: {
                    'Content-Type':  'application/json',
                    'Authorization': `Bearer ${this.token}`,
                }
            });

            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data    = await res.json();
            const pericias = data.pericias || [];
            console.log('✅ Perícias carregadas:', pericias.length);
            this.renderizarPericiasNaFicha(pericias);

        } catch (error) {
            console.warn('⚠️ Erro ao carregar perícias:', error);
            this.renderizarPericiasVazias();
        }
    }

    renderizarPericiasNaFicha(pericias) {
        const container = document.getElementById('fichaPericiasLista');
        if (!container) return;

        if (pericias.length === 0) {
            container.innerHTML = '<span class="ficha-vazio">Nenhuma perícia selecionada</span>';
            return;
        }

        container.innerHTML = '';
        pericias.forEach(pj => {
            const total = pj.graduacao + pj.modificador_atributo + (pj.bonus_outros || 0);
            const item  = document.createElement('div');
            item.className = 'ficha-pericia-item';
            item.title     = pj.pericia?.descricao || '';
            item.innerHTML = `
                <span class="ficha-pericia-nome">${pj.pericia?.nome || '—'}</span>
                <span class="ficha-pericia-atributo">${pj.pericia?.atributo || '—'}</span>
                <div class="ficha-pericia-mods">
                    <div class="ficha-pericia-mod">
                        <span class="ficha-pericia-mod-label">Gra</span>
                        <span class="ficha-pericia-mod-valor">${pj.graduacao}</span>
                    </div>
                    <div class="ficha-pericia-mod">
                        <span class="ficha-pericia-mod-label">Atr</span>
                        <span class="ficha-pericia-mod-valor">${pj.modificador_atributo >= 0 ? '+' : ''}${pj.modificador_atributo}</span>
                    </div>
                    <div class="ficha-pericia-mod">
                        <span class="ficha-pericia-mod-label">Bôn</span>
                        <span class="ficha-pericia-mod-valor">${(pj.bonus_outros || 0) >= 0 ? '+' : ''}${pj.bonus_outros || 0}</span>
                    </div>
                </div>
                <span class="ficha-pericia-total ${total >= 0 ? 'positivo' : 'negativo'}">
                    ${total >= 0 ? '+' : ''}${total}
                </span>
            `;
            container.appendChild(item);
        });

        console.log('✅ Perícias renderizadas:', pericias.length);
    }

    renderizarPericiasVazias() {
        const container = document.getElementById('fichaPericiasLista');
        if (container) container.innerHTML = '<span class="ficha-vazio">Nenhuma perícia selecionada</span>';
    }

    // ─────────────────────────────────────────────────────────
    // ERRO
    // ─────────────────────────────────────────────────────────

    mostrarErro(mensagem) {
        console.error('❌', mensagem);
        const container = document.getElementById('fichaPericiasLista');
        if (container) container.innerHTML = `<span class="ficha-vazio">❌ ${mensagem}</span>`;
    }
}

// ── Inicializar quando DOM estiver pronto ──
document.addEventListener('DOMContentLoaded', async () => {
    const controller = new FichaPersonagemController();
    await controller.inicializar();
});