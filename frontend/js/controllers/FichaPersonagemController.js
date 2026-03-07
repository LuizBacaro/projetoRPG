/*
   FichaPersonagemController.js
   SRP: carregar e exibir a ficha completa do personagem
   Recebe o ID via query string: /ficha-personagem.html?id=123
*/

import { CombatenteService } from '../services/CombatenteService.js';
import { MagiaSlotService   } from '../services/MagiaSlotService.js';
import { getApiUrl          } from '../config/api.config.js';

class FichaPersonagemController {

    constructor() {
        this.combatenteService = new CombatenteService();
        this.magiaSlotService  = new MagiaSlotService();
        this._init();
    }

    // ── Inicialização ─────────────────────────────────────────
    async _init() {
        const id = this._obterIdDaUrl();
        if (!id) {
            this._mostrarErro('ID do personagem não encontrado na URL.');
            return;
        }
        try {
            // ✅ CORRIGIDO: obterPorId() — nome correto do CombatenteService
            const personagem = await this.combatenteService.obterPorId(id);
            if (!personagem) {
                this._mostrarErro('Personagem não encontrado.');
                return;
            }
            this._renderizar(personagem);
        } catch (err) {
            console.error('[FichaPersonagemController] Erro ao carregar:', err);
            this._mostrarErro('Erro ao carregar personagem. Verifique o console.');
        }
    }

    // ── Utilitários ───────────────────────────────────────────
    _obterIdDaUrl() {
        const params = new URLSearchParams(window.location.search);
        return params.get('id');
    }

    _mod(valor) {
        const m = Math.floor(((valor || 10) - 10) / 2);
        return m >= 0 ? ('+' + m) : ('' + m);
    }

    _sinal(valor) {
        if (valor === null || valor === undefined) return '+0';
        return valor >= 0 ? ('+' + valor) : ('' + valor);
    }

    _texto(id, valor) {
        const el = document.getElementById(id);
        if (el) el.textContent = valor;
    }

    // ── Renderização principal ────────────────────────────────
    _renderizar(p) {
        document.title = (p.nome || 'Personagem') + ' — Ficha';

        this._renderizarIdentidade(p);
        this._renderizarFoto(p);
        this._renderizarAtributos(p);
        this._renderizarDefesa(p);
        this._renderizarResistencias(p);
        this._renderizarPericias(p.pericias || []);
        this._renderizarEquipamentos(p.equipamentos || []);
        this._renderizarAtaques(p.ataques || []);
        this._renderizarMagias(p.magias_slots || []);
    }

    // ── Identidade ────────────────────────────────────────────
    _renderizarIdentidade(p) {
        this._texto('fichaNome',   p.nome    || '—');
        this._texto('fichaRaca',   p.raca    || '—');
        this._texto('fichaClasse', p.classe  || '—');
        this._texto('fichaTipo',   p.tipo    || '—');
        this._texto('fichaNivel',  (p.nivel  || 1) + 'º nível');

        // ✅ Aplica cor do badge de tipo
        const tagTipo = document.getElementById('fichaTipo');
        if (tagTipo && p.tipo) {
            tagTipo.className = 'ficha-tag ficha-tag-tipo ficha-tag-' + p.tipo.toLowerCase();
        }
    }

    // ── Foto ──────────────────────────────────────────────────
    _renderizarFoto(p) {
        const img         = document.getElementById('fichaFoto');
        const placeholder = document.getElementById('fichaFotoPlaceholder');
        if (!img) return;

        if (p.foto_url) {
            img.src = p.foto_url;
            img.onload  = () => {
                img.classList.add('carregada');
                if (placeholder) placeholder.style.display = 'none';
            };
            img.onerror = () => {
                // Foto com erro → mantém placeholder
                img.style.display = 'none';
            };
        }
    }

    // ── Atributos ─────────────────────────────────────────────
    _renderizarAtributos(p) {
        const atribs = [
            ['For', p.forca        || 10],
            ['Des', p.destreza     || 10],
            ['Con', p.constituicao || 10],
            ['Int', p.inteligencia || 10],
            ['Sab', p.sabedoria    || 10],
            ['Car', p.carisma      || 10],
        ];

        atribs.forEach(([chave, valor]) => {
            this._texto('ficha' + chave,        valor);
            this._texto('ficha' + chave + 'Mod', this._mod(valor));
        });
    }

    // ── Defesa ────────────────────────────────────────────────
    _renderizarDefesa(p) {
        // CA
        this._texto('fichaCa',       p.ca       !== undefined ? p.ca       : 10);
        this._texto('fichaToque',    p.toque     !== undefined ? p.toque    : 10);
        this._texto('fichaSurpresa', p.surpresa  !== undefined ? p.surpresa : 10);

        // Iniciativa
        this._texto('fichaIniciativa', this._sinal(p.iniciativa || 0));

        // PV com barra de cor dinâmica
        const hpAtual = p.hp_atual  || 0;
        const hpMax   = p.hp_maximo || 0;
        this._texto('fichaPv', hpAtual + ' / ' + hpMax);

        const pct  = hpMax > 0 ? Math.min(100, (hpAtual / hpMax) * 100) : 0;
        const cor  = pct > 50 ? '#4CAF50' : pct > 25 ? '#FF9800' : '#F44336';
        const fill = document.getElementById('fichaPvFill');
        if (fill) {
            fill.style.width      = pct + '%';
            fill.style.background = cor;
        }
    }

    // ── Resistências ──────────────────────────────────────────
    _renderizarResistencias(p) {
        this._texto('fichaFort',   this._sinal(p.fortitude || 0));
        this._texto('fichaReflex', this._sinal(p.reflexos  || 0));
        this._texto('fichaVont',   this._sinal(p.vontade   || 0));
    }

    // ── Perícias ──────────────────────────────────────────────
    _renderizarPericias(pericias) {
        const container = document.getElementById('fichaPericiasLista');
        if (!container) return;

        if (!pericias.length) {
            container.innerHTML = '<span class="ficha-vazio">Nenhuma perícia cadastrada</span>';
            return;
        }

        // ✅ Ordena por valor decrescente
        const ordenadas = [...pericias].sort((a, b) => (b.valor || 0) - (a.valor || 0));

        container.innerHTML = ordenadas.map(p => `
            <div class="ficha-pericia-item">
                <span class="ficha-pericia-nome">${p.nome || '—'}</span>
                <span class="ficha-pericia-valor">${this._sinal(p.valor || 0)}</span>
            </div>
        `).join('');
    }

    // ── Equipamentos ──────────────────────────────────────────
    _renderizarEquipamentos(equipamentos) {
        const container = document.getElementById('fichaEquipamentos');
        if (!container) return;

        if (!equipamentos.length) {
            container.innerHTML = '<span class="ficha-vazio">Nenhum equipamento cadastrado</span>';
            return;
        }

        container.innerHTML = equipamentos.map(e => `
            <div class="ficha-equip-item">
                🗡️ <span>${e.nome || '—'}${e.descricao ? ' — ' + e.descricao : ''}</span>
            </div>
        `).join('');
    }

    // ── Ataques ───────────────────────────────────────────────
    _renderizarAtaques(ataques) {
        const container = document.getElementById('fichaAtaquesLista');
        if (!container) return;

        if (!ataques.length) {
            container.innerHTML = '<div class="ficha-ataque-vazio">Nenhum ataque cadastrado</div>';
            return;
        }

        container.innerHTML = ataques.map(a => {
            const tipo = a.tipo_dano ? ` <span class="ataque-tipo">(${a.tipo_dano})</span>` : '';
            return `
                <div class="ficha-ataque-row">
                    <span class="ataque-nome">${a.nome || '—'}</span>
                    <span>${a.bonus_ataque !== undefined ? this._sinal(a.bonus_ataque) : '—'}</span>
                    <span>${a.dano || '—'}${tipo}</span>
                </div>
            `;
        }).join('');
    }

    // ── Magias ────────────────────────────────────────────────
    _renderizarMagias(slots) {
        const container = document.getElementById('fichaMagiasGrid');
        if (!container) return;

        // ✅ Filtra slots com total > 0 e ordena por nível
        const comSlot = slots
            .filter(s => s.total > 0)
            .sort((a, b) => a.nivel - b.nivel);

        if (!comSlot.length) {
            container.innerHTML = '<div class="ficha-magia-vazio">Nenhum slot cadastrado</div>';
            return;
        }

        container.innerHTML = comSlot.map(s => {
            const restantes = s.total - (s.usados || 0);
            const corSlot   = restantes === 0 ? 'ficha-magia-esgotado' : '';
            return `
                <div class="ficha-magia-row ${corSlot}">
                    <span class="ficha-magia-nivel">Nív ${s.nivel}</span>
                    <span class="ficha-magia-slots">${restantes}/${s.total}</span>
                </div>
            `;
        }).join('');
    }

    // ── Erro ──────────────────────────────────────────────────
    _mostrarErro(msg) {
        document.body.innerHTML = `
            <div style="
                display:flex; align-items:center; justify-content:center;
                height:100vh; flex-direction:column; gap:1rem;
                background:#1a0e06; color:#f4e9d0; font-family:serif;
            ">
                <span style="font-size:3rem;">⚠️</span>
                <p style="font-size:1.1rem; text-align:center; max-width:400px;">${msg}</p>
                <button onclick="window.close()"
                    style="padding:0.5rem 1.5rem; background:#c9a84c; border:none;
                           border-radius:8px; cursor:pointer; font-weight:bold;">
                    Fechar
                </button>
            </div>`;
    }
}

new FichaPersonagemController();