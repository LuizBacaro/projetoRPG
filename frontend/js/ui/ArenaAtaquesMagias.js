export class ArenaAtaquesMagias {

    static renderAtaques(ataques, containerId) {
        if (!containerId) containerId = 'arenaAtaquesContainer';
        var container = document.getElementById(containerId);
        if (!container) return;

        if (!ataques || ataques.length === 0) {
            var html = '';
            html += '<div class="arena-secao">';
            html += '<h3 class="arena-secao-titulo">Ataques</h3>';
            html += '<div class="arena-ataques-lista">';
            html += '<div class="arena-ataque-header"><span>Nome</span><span>Ataque</span><span>Dano</span></div>';
            html += '<div class="arena-ataque-item arena-ataque-placeholder"><span>Nenhum ataque cadastrado</span></div>';
            html += '</div></div>';
            container.innerHTML = html;
            return;
        }

        var linhas = '';
        for (var i = 0; i &lt; ataques.length; i++) {
            var a      = ataques[i];
            var tipo   = a.tipo_dano ? ' (' + a.tipo_dano + ')' : '';
            linhas += '<div class="arena-ataque-item">';
            linhas += '<span>' + a.nome + '</span>';
            linhas += '<span>' + a.bonus_ataque + '</span>';
            linhas += '<span>' + a.dano + tipo + '</span>';
            linhas += '</div>';
        }

        var html2 = '';
        html2 += '<div class="arena-secao">';
        html2 += '<h3 class="arena-secao-titulo">Ataques</h3>';
        html2 += '<div class="arena-ataques-lista">';
        html2 += '<div class="arena-ataque-header"><span>Nome</span><span>Ataque</span><span>Dano</span></div>';
        html2 += linhas;
        html2 += '</div></div>';
        container.innerHTML = html2;
    }

    static renderMagias(slots, containerId, onUsadosChange) {
        if (!containerId)    containerId    = 'arenaMagiasContainer';
        if (!onUsadosChange) onUsadosChange = null;

        var container = document.getElementById(containerId);
        if (!container) return;

        var grid = [];
        for (var i = 0; i &lt;= 9; i++) {
            var slot = null;
            if (slots) {
                for (var k = 0; k &lt; slots.length; k++) {
                    if (slots[k].nivel === i) { slot = slots[k]; break; }
                }
            }
            grid.push({
                nivel:  i,
                id:     slot ? slot.id     : null,
                total:  slot ? slot.total  : 0,
                usados: slot ? slot.usados : 0
            });
        }

        var linhas = '';
        for (var j = 0; j &lt; grid.length; j++) {
            var s        = grid[j];
            var disabled = (s.total === 0) ? 'disabled' : '';
            linhas += '<div class="arena-magia-linha" data-nivel="' + s.nivel + '">';
            linhas += '<span class="arena-magia-nivel">NIV ' + s.nivel + '</span>';
            linhas += '<div class="arena-magia-controle">';
            linhas += '<button class="arena-magia-btn" data-slot-id="' + s.id + '" data-acao="diminuir" data-nivel="' + s.nivel + '" ' + disabled + '>-</button>';
            linhas += '<span class="arena-magia-valor" data-nivel="' + s.nivel + '">' + s.usados + '</span>';
            linhas += '<button class="arena-magia-btn" data-slot-id="' + s.id + '" data-acao="aumentar" data-nivel="' + s.nivel + '" ' + disabled + '>+</button>';
            linhas += '</div>';
            linhas += '<span class="arena-magia-usados" data-nivel-total="' + s.nivel + '">' + s.total + '</span>';
            linhas += '</div>';
        }

        var html = '';
        html += '<div class="arena-secao">';
        html += '<h3 class="arena-secao-titulo">Controle de Magias</h3>';
        html += '<div class="arena-magias-grid">' + linhas + '</div>';
        html += '</div>';
        container.innerHTML = html;

        if (onUsadosChange) {
            var btns = container.querySelectorAll('.arena-magia-btn');
            for (var b = 0; b &lt; btns.length; b++) {
                (function(btn) {
                    btn.addEventListener('click', function() {
                        var nivel   = parseInt(btn.dataset.nivel);
                        var slotId  = (btn.dataset.slotId !== 'null') ? parseInt(btn.dataset.slotId) : null;
                        var acao    = btn.dataset.acao;
                        var spanVal = container.querySelector('[data-nivel="'       + nivel + '"]');
                        var spanTot = container.querySelector('[data-nivel-total="' + nivel + '"]');
                        var total   = parseInt(spanTot ? spanTot.textContent : 0);
                        var usados  = parseInt(spanVal ? spanVal.textContent : 0);

                        if      (acao === 'aumentar' && usados &lt; total) usados++;
                        else if (acao === 'diminuir' && usados > 0)     usados--;
                        else return;

                        if (spanVal) spanVal.textContent = usados;
                        onUsadosChange(slotId, nivel, usados);
                    });
                })(btns[b]);
            }
        }
    }
}