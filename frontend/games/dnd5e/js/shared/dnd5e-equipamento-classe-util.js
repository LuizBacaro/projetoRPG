/**
 * Utilitário D&D 5e — equipamento inicial da classe (espelha backend).
 */
const Dnd5eEquipamentoClasseUtil = (() => {
    function formatHint(res) {
        if (!res?.classe_equip_aplicado) return '';
        const nome = res.nome_pacote || res.classe_equip_nome || 'Pacote aplicado';
        return `${nome} aplicado à ficha.`;
    }

    /**
     * Mescla resposta da API no estado local do inventário.
     */
    function aplicarResposta(state, res) {
        if (!res || !state) return { changed: false, state, meta: {} };
        const inv = { ...(state || {}) };
        inv.equipamentos = Array.isArray(res.inventario?.equipamentos)
            ? res.inventario.equipamentos.map((x) => ({ ...x }))
            : inv.equipamentos || [];
        if (res.armadura_slug != null) inv.armadura_slug = res.armadura_slug || null;
        if (res.escudo_slug != null) inv.escudo_slug = res.escudo_slug || null;
        if (res.arma_principal_slug != null) {
            inv.arma_principal_slug = res.arma_principal_slug || null;
        }
        return {
            changed: true,
            state: inv,
            meta: {
                classe_equip_slug: res.classe_equip_slug || null,
                classe_equip_aplicado: !!res.classe_equip_aplicado,
                classe_equip_nome: res.classe_equip_nome || res.nome_pacote || '',
            },
        };
    }

    return { formatHint, aplicarResposta };
})();
