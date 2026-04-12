(function () {
    var RACES = [
        'Humano',
        'Anao',
        'Elfo',
        'Gnomo',
        'Meio-elfo',
        'Meio-orc',
        'Halfling',
    ];

    function listar() {
        return RACES.slice();
    }

    function valorOutro() {
        return '__OUTRO__';
    }

    function preencherSelect(select, options) {
        if (!select) return;

        var opts = options || {};
        var incluirVazio = opts.incluirVazio !== false;
        var textoVazio = opts.textoVazio || '-- Selecione uma raca --';
        var incluirOutro = opts.incluirOutro === true;
        var textoOutro = opts.textoOutro || 'Outro (personalizada)';
        var valorOutroCustom = opts.valorOutro || valorOutro();

        select.innerHTML = '';

        if (incluirVazio) {
            var optionVazia = document.createElement('option');
            optionVazia.value = '';
            optionVazia.textContent = textoVazio;
            select.appendChild(optionVazia);
        }

        listar().forEach(function (race) {
            var opt = document.createElement('option');
            opt.value = race;
            opt.textContent = race;
            select.appendChild(opt);
        });

        if (incluirOutro) {
            var optionOutro = document.createElement('option');
            optionOutro.value = valorOutroCustom;
            optionOutro.textContent = textoOutro;
            select.appendChild(optionOutro);
        }
    }

    window.RacasPHB = window.RacasPHB || {
        listar: listar,
        preencherSelect: preencherSelect,
        valorOutro: valorOutro,
    };
})();