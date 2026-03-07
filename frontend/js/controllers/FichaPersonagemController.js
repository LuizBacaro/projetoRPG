/* 
   FichaPersonagemPage.js
   Responsabilidade única: carregar e exibir a ficha do personagem
   Recebe o ID via query string: /ficha-personagem.html?id=123
    */

import { CombatenteService } from '../services/CombatenteService.js';
import { MagiaSlotService   } from '../services/MagiaSlotService.js';

class FichaPersonagemPage {

    constructor() {
        this.combatenteService = new CombatenteService();
        this.magiaSlotService  = new MagiaSlotService();
        this._init();
    }

    async _init() {
        var id = this._obterIdDaUrl();
        if (!id) { this._mostrarErro('ID do personagem não encontrado na URL.'); return; }
        try {
            var personagem = await this.combatenteService.buscarPorId(id);
            if (!personagem) { this._mostrarErro('Personagem não encontrado.'); return; }
            this._renderizar(personagem);
        } catch (err) {
            console.error(err);
            this._mostrarErro('Erro ao carregar personagem.');
        }
    }

    _obterIdDaUrl() {
        var params = new URLSearchParams(window.location.search);
        return params.get('id');
    }

    _mod(valor) {
        var m = Math.floor(((valor || 10) - 10) / 2);
        return m >= 0 ? ('+' + m) : ('' + m);
    }

    _sinal(valor) {
        if (valor === null || valor === undefined) return '+0';
        return valor >= 0 ? ('+' + valor) : ('' + valor);
    }

    _renderizar(p) {
        document.title = p.nome + ' — Ficha';

        // Identidade
        this._texto('fichaNome',    p.nome || '—');
        this._texto('fichaRaca',    p.raca || '—');
        this._texto('fichaClasse',  p.classe || '—');
        this._texto('fichaTipo',    p.tipo || '—');
        this._texto('fichaNivel',   (p.nivel || 1) + 'º nível');

        // Foto
        if (p.foto_url) {
            var img = document.getElementById('fichaFoto');
            img.src = p.foto_url;
            img.classList.add('carregada');
            document.getElementById('fichaFotoPlaceholder').style.display = 'none';
        }

        // Atributos
        var atribs = [
            ['For', p.forca        || 10],
            ['Des', p.destreza     || 10],
            ['Con', p.constituicao || 10],
            ['Int', p.inteligencia || 10],
            ['Sab', p.sabedoria    || 10],
            ['Car', p.carisma      || 10],
        ];
        var self = this;
        atribs.forEach(function(a) {
            self._texto('ficha' + a[0],        a[1]);
            self._texto('ficha' + a[0] + 'Mod', self._mod(a[1]));
        });

        // Defesa
        this._texto('fichaCa',       p.ca        !== undefined ? p.ca       : 10);
        this._texto('fichaToque',    p.toque     !== undefined ? p.toque    : 10);
        this._texto('fichaSurpresa', p.surpresa  !== undefined ? p.surpresa : 10);
        this._texto('fichaIniciativa', this._sinal(p.iniciativa || 0));

        // PV
        var hpAtual = p.hp_atual  || 0;
        var hpMax   = p.hp_maximo || 0;
        this._texto('fichaPv', hpAtual + ' / ' + hpMax);
        var pct = hpMax > 0 ? Math.min(100, (hpAtual / hpMax) * 100) : 0;
        var cor = pct > 50 ? '#4CAF50' : pct > 25 ? '#FF9800' : '#F44336';
        var fill = document.getElementById('fichaPvFill');
        if (fill) { fill.style.width = pct + '%'; fill.style.background = cor; }

        // Resistências
        this._texto('fichaFort',   this._sinal(p.fortitude || 0));
        this._texto('fichaReflex', this._sinal(p.reflexos  || 0));
        this._texto('fichaVont',   this._sinal(p.vontade   || 0));

        // Perícias
        this._renderizarPericias(p.pericias || []);

        // Equipamentos
        this._renderizarEquipamentos(p.equipamentos || []);

        // Ataques
        this._renderizarAtaques(p.ataques || []);

        // Magias
        this._renderizarMagias(p.magias_slots || []);
    }

    _renderizarPericias(pericias) {
        var container = document.getElementById('fichaPericiasLista');
        if (!container) return;
        if (!pericias || pericias.length === 0) {
            container.innerHTML = '<span class="ficha-vazio">Nenhuma perícia cadastrada</span>';
            return;
        }
        var html = '';
        for (var i = 0; i < pericias.length; i++) {
            var p = pericias[i];
            html += '<div class="ficha-pericia-item">';
            html += '<span class="ficha-pericia-nome">' + p.nome + '</span>';
            html += '<span class="ficha-pericia-valor">' + this._sinal(p.valor || 0) + '</span>';
            html += '</div>';
        }
        container.innerHTML = html;
    }

    _renderizarEquipamentos(equipamentos) {
        var container = document.getElementById('fichaEquipamentos');
        if (!container) return;
        if (!equipamentos || equipamentos.length === 0) {
            container.innerHTML = '<span class="ficha-vazio">Nenhum equipamento cadastrado</span>';
            return;
        }
        var html = '';
        for (var i = 0; i < equipamentos.length; i++) {
            var e = equipamentos[i];
            html += '<div class="ficha-equip-item">';
            html += '🗡️ <span>' + e.nome + (e.descricao ? ' — ' + e.descricao : '') + '</span>';
            html += '</div>';
        }
        container.innerHTML = html;
    }

    _renderizarAtaques(ataques) {
        var container = document.getElementById('fichaAtaquesLista');
        if (!container) return;
        if (!ataques || ataques.length === 0) {
            container.innerHTML = '<div class="ficha-ataque-vazio">Nenhum ataque cadastrado</div>';
            return;
        }
        var html = '';
        for (var i = 0; i < ataques.length; i++) {
            var a    = ataques[i];
            var tipo = a.tipo_dano ? ' (' + a.tipo_dano + ')' : '';
            html += '<div class="ficha-ataque-row">';
            html += '<span class="ataque-nome">' + a.nome + '</span>';
            html += '<span>' + (a.bonus_ataque || '—') + '</span>';
            html += '<span>' + (a.dano || '—') + tipo + '</span>';
            html += '</div>';
        }
        container.innerHTML = html;
    }

    _renderizarMagias(slots) {
        var container = document.getElementById('fichaMagiasGrid');
        if (!container) return;
        var comSlot = slots.filter(function(s) { return s.total > 0; });
        if (comSlot.length === 0) {
            container.innerHTML = '<div class="ficha-magia-vazio">Nenhum slot cadastrado</div>';
            return;
        }
        var html = '';
        for (var i = 0; i < comSlot.length; i++) {
            var s = comSlot[i];
            html += '<div class="ficha-magia-row">';
            html += '<span class="ficha-magia-nivel">NIV ' + s.nivel + '</span>';
            html += '<span class="ficha-magia-slots">' + (s.total - s.usados) + '/' + s.total + '</span>';
            html += '</div>';
        }
        container.innerHTML = html;
    }

    _texto(id, valor) {
        var el = document.getElementById(id);
        if (el) el.textContent = valor;
    }

    _mostrarErro(msg) {
        document.body.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100vh;color:#f4e9d0;font-family:serif;font-size:1.2rem;">' + msg + '</div>';
    }
}

new FichaPersonagemController();