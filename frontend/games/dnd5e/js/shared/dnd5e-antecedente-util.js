/**
 * Utilitário D&D 5e — sincronizar inventário com antecedente (espelha backend).
 */
const Dnd5eAntecedenteUtil = (() => {
    const NOMES_ITEM = {
        simbolo_sagrado: 'Símbolo sagrado',
        livro_preces: 'Livro de preces',
        roupa_religiosa: 'Roupas de aventureiro',
        ferramentas_profissionais: 'Ferramentas de artesão',
        carta_guilda: 'Carta de membro da guilda',
        roupa_escura: 'Roupas escuras com capuz',
        kit_disfarce: 'Kit de disfarce',
        cajado: 'Cajado',
        armadilhas: 'Armadilhas de caçador',
        pele: 'Pele de animal',
        ferramentas_artesao: 'Ferramentas de artesão',
        pa: 'Pá',
        insignia: 'Insígnia de patente',
        trofeu: 'Troféu de inimigo',
        kit_jogos: 'Kit de jogos',
        roupa_fina: 'Roupas finas',
        instrumento: 'Instrumento musical',
        admirecao: 'Admiradores',
        porta_pergaminho: 'Porta-pergaminho',
        kit_herbalismo: 'Kit de herbalismo',
        anel_sinete: 'Anel com sinete',
        vidro_tinta: 'Frasco de tinta',
        facas: 'Facas',
        livro: 'Livro de conhecimento',
        roupa_comum: 'Roupas comuns',
        adaga: 'Adaga',
        corda: 'Corda (15 m)',
        faca: 'Faca pequena',
        mapa_cidade: 'Mapa da cidade',
        rato: 'Rato de estimação',
    };

    function nomeItem(slug) {
        const chave = String(slug || '').trim().toLowerCase();
        if (NOMES_ITEM[chave]) return NOMES_ITEM[chave];
        return chave.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()) || chave;
    }

    function gerarTracosPlaceholder(ant) {
        const n = ant?.nome || 'Antecedente';
        return {
            personalidade: [`Traço de personalidade (${n}) 1`, `Traço de personalidade (${n}) 2`],
            ideais: [`Ideal (${n}) 1`, `Ideal (${n}) 2`],
            lacos: [`Laço (${n}) 1`, `Laço (${n}) 2`],
            fraquezas: [`Fraqueza (${n}) 1`, `Fraqueza (${n}) 2`],
        };
    }

    function criarItemInventario(slug, antecedenteSlug, uidFn) {
        const itemSlug = String(slug || '').trim().toLowerCase();
        const uid =
            typeof uidFn === 'function'
                ? uidFn()
                : `ant_${itemSlug}_${Date.now().toString(36)}`;
        return {
            id: uid,
            slug: itemSlug,
            nome: nomeItem(itemSlug),
            quantidade: 1,
            fonte: 'antecedente',
            antecedente_slug: antecedenteSlug,
        };
    }

    function removerItensAntecedente(equipamentos, antecedenteSlug) {
        const alvo = String(antecedenteSlug || '').trim().toLowerCase();
        if (!alvo) return [...(equipamentos || [])];
        return (equipamentos || []).filter(
            (item) =>
                !(
                    item &&
                    item.fonte === 'antecedente' &&
                    String(item.antecedente_slug || '').trim().toLowerCase() === alvo
                )
        );
    }

    /**
     * @param {object} params
     * @param {object} params.inventarioState — estado do painel (equipamentos, ouro_po)
     * @param {string|null} params.slugAtual — antecedente selecionado
     * @param {string|null} params.slugAplicado — último antecedente sincronizado
     * @param {number} params.ouroAplicado — ouro do antecedente já somado
     * @param {object|null} params.antecedente — item do catálogo API
     * @param {string[]} [params.idiomasEscolhidos]
     * @param {object|null} [params.tracosEscolhidos]
     * @param {function} [params.uidFn]
     * @returns {{ changed: boolean, inventarioState: object, meta: object }}
     */
    function sincronizarInventario({
        inventarioState,
        slugAtual,
        slugAplicado,
        ouroAplicado,
        antecedente,
        idiomasEscolhidos,
        tracosEscolhidos,
        uidFn,
    }) {
        const atual = slugAtual ? String(slugAtual).trim().toLowerCase() : null;
        const aplicado = slugAplicado ? String(slugAplicado).trim().toLowerCase() : null;

        if (atual === aplicado) {
            const idiomas =
                typeof Dnd5eIdiomasUtil !== 'undefined'
                    ? Dnd5eIdiomasUtil.normalizarEscolhidos(
                          idiomasEscolhidos,
                          window.__dnd5eCatalogoIdiomas || []
                      )
                    : [...(idiomasEscolhidos || [])];
            const tracos =
                typeof Dnd5eTracosUtil !== 'undefined' && antecedente?.tracos_opcoes
                    ? Dnd5eTracosUtil.normalizarEscolhidos(
                          tracosEscolhidos,
                          antecedente.tracos_opcoes
                      )
                    : tracosEscolhidos || null;
            return {
                changed: false,
                inventarioState,
                meta: {
                    antecedente_inventario_slug: aplicado,
                    antecedente_ouro_aplicado: ouroAplicado || 0,
                    antecedente_idiomas: idiomas,
                    antecedente_tracos: tracos,
                },
            };
        }

        const state = {
            ...(inventarioState || {}),
            equipamentos: [...((inventarioState && inventarioState.equipamentos) || [])],
            ouro_po: Number(inventarioState?.ouro_po) || 0,
        };

        if (aplicado) {
            state.equipamentos = removerItensAntecedente(state.equipamentos, aplicado);
            state.ouro_po = Math.max(0, state.ouro_po - (Number(ouroAplicado) || 0));
        }

        const meta = {
            antecedente_inventario_slug: atual,
            antecedente_ouro_aplicado: 0,
            antecedente_tracos: null,
            antecedente_idiomas: [],
        };

        if (!atual || !antecedente) {
            return { changed: true, inventarioState: state, meta };
        }

        (antecedente.equipamento || []).forEach((slug) => {
            state.equipamentos.push(criarItemInventario(slug, atual, uidFn));
        });

        const ouroExtra = Number(antecedente.ouro_po ?? antecedente.ouro_extra) || 0;
        state.ouro_po += ouroExtra;
        meta.antecedente_ouro_aplicado = ouroExtra;
        meta.antecedente_idiomas = [];

        return { changed: true, inventarioState: state, meta };
    }

    return {
        nomeItem,
        sincronizarInventario,
        gerarTracosPlaceholder,
    };
})();
