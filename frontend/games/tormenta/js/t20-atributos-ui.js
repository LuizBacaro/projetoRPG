/**
 * UI de atributos v1.3 vs MB — hints, labels e limites de input compartilhados.
 */
(function (global) {
    'use strict';

    const ATTR_KEYS = ['for', 'des', 'con', 'int', 'sab', 'car'];

    function q(id) {
        return document.getElementById(id);
    }

    function regraVersaoAtiva() {
        if (typeof global.getRegraVersaoAtiva === 'function') {
            return global.getRegraVersaoAtiva();
        }
        return 'mb';
    }

    function isV13(rv) {
        return global.T20RegraVersao && global.T20RegraVersao.isV13(rv != null ? rv : regraVersaoAtiva());
    }

    function fallbackAttrDefault(rv) {
        return isV13(rv) ? 0 : 10;
    }

    function hintAtributosResumoHtml(rv, pontosCompra) {
        const pts = pontosCompra != null ? pontosCompra : isV13(rv) ? 10 : 20;
        if (isV13(rv)) {
            return (
                'v1.3: use a coluna <strong>Rolagem</strong> da Tabela 1-1 nos campos (10 = atributo 0). ' +
                'O valor nativo e o modificador entram nas fórmulas; a ficha exibe ambos no resumo. ' +
                'Jogador: <strong>compra ' +
                pts +
                ' pts</strong> (bases −2 a +4) ou <strong>4d6</strong> (soma dos seis ≥ 6). ' +
                'Edite em <strong>Editar ficha</strong>.'
            );
        }
        return (
            'Modificadores conforme <strong>tabela do MB</strong> (faixas de valor). ' +
            'O valor e o modificador são exibidos juntos no resumo da ficha para maior clareza. ' +
            'Jogador: <strong>compra ' +
            pts +
            ' pts</strong> (bases 8–18) ou <strong>4d6</strong> (reroll MB). ' +
            'Edite em <strong>Editar ficha</strong>.'
        );
    }

    function hintEdicaoAtributosHtml(rv) {
        if (isV13(rv)) {
            return (
                'Edite os valores finais (base + racial). Jogadores v1.3: rolagem padrão <strong>10</strong> (atributo 0); compra reinicia em 10 nos campos (+ racial nos finais).'
            );
        }
        return (
            'Edite os valores finais (base + racial). Jogadores MB: escolha o método abaixo; ao trocar a raça, a base reinicia em <strong>10</strong> (+ ajustes raciais nos finais).'
        );
    }

    function formatContribuicaoAttr(val, rv) {
        const n = global.T20RegraVersao
            ? global.T20RegraVersao.contribuicaoAtributo(val, rv != null ? rv : regraVersaoAtiva())
            : Number(val) || 0;
        if (!Number.isFinite(n)) return '+0';
        return (n >= 0 ? '+' : '') + n;
    }

    function labelContribuicaoAbrev(slug, val, rv) {
        const ab = { for: 'FOR', des: 'DES', con: 'CON', int: 'INT', sab: 'SAB', car: 'CAR' }[slug] || slug;
        const n = global.T20RegraVersao
            ? global.T20RegraVersao.contribuicaoAtributo(val, rv != null ? rv : regraVersaoAtiva())
            : Number(val) || 0;
        if (isV13(rv)) return `${ab} ${n}`;
        return `${ab} ${formatContribuicaoAttr(val, rv)}`;
    }

    /**
     * Atualiza hints/labels/limites na ficha (ids fixos da página).
     * @param {{ pontosCompra?: number }} opts
     */
    function atualizarUiFicha(opts) {
        const rv = regraVersaoAtiva();
        const v13 = isV13(rv);
        const pts =
            opts && opts.pontosCompra != null
                ? opts.pontosCompra
                : typeof global.PONTOS_INICIAIS_COMPRA_FICHA === 'number'
                  ? global.PONTOS_INICIAIS_COMPRA_FICHA
                  : v13
                    ? 10
                    : 20;

        const hint = q('hintAtributos');
        if (hint) hint.innerHTML = hintAtributosResumoHtml(rv, pts);

        const hintEd = q('hintEdicaoAtributos');
        if (hintEd) hintEd.innerHTML = hintEdicaoAtributosHtml(rv);

        const lblMet = document.querySelector('label[for="f_metodo_geracao"]');
        if (lblMet) lblMet.textContent = v13 ? 'Geração de atributos (v1.3)' : 'Geração de atributos (MB)';

        const optCompra = q('f_metodo_geracao') && q('f_metodo_geracao').querySelector('option[value="compra_pontos"]');
        if (optCompra) optCompra.textContent = `Compra por pontos (${pts} pts)`;

        const br = q('btnFichaResetCompra');
        if (br) br.textContent = v13 ? 'Base 0' : 'Base 10';

        const minInp = v13 ? -99 : 0;
        const dlgIds = [
            'f_dlg_attr_for',
            'f_dlg_attr_des',
            'f_dlg_attr_con',
            'f_dlg_attr_int',
            'f_dlg_attr_sab',
            'f_dlg_attr_car',
        ];
        dlgIds.forEach((id) => {
            const el = q(id);
            if (el) el.min = String(minInp);
        });
        const resIds = ['fichaForResumo', 'fichaDesResumo', 'fichaConResumo', 'fichaIntResumo', 'fichaSabResumo', 'fichaCarResumo'];
        resIds.forEach((id) => {
            const el = q(id);
            if (el) el.min = String(minInp);
        });

        const modIds = [
            'fichaForModResumo',
            'fichaDesModResumo',
            'fichaConModResumo',
            'fichaIntModResumo',
            'fichaSabModResumo',
            'fichaCarModResumo',
        ];
        modIds.forEach((id) => {
            const el = q(id);
            if (el) {
                // Sempre mostrar contribuição na ficha de atributos;
                // em v1.3 ela coincide com o valor bruto e dá clareza ao jogador.
                el.style.display = '';
            }
        });
    }

    global.T20AtributosUi = {
        ATTR_KEYS,
        fallbackAttrDefault,
        hintAtributosResumoHtml,
        hintEdicaoAtributosHtml,
        formatContribuicaoAttr,
        labelContribuicaoAbrev,
        atualizarUiFicha,
        isV13,
    };
})(typeof window !== 'undefined' ? window : globalThis);
