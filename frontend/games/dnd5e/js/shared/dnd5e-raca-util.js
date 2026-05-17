/**
 * Utilitários compartilhados — UI de traços raciais (ficha + pré-cadastro).
 */
const Dnd5eRacaUtil = {
    temBonusHabilidadeExtraEscolha(raca) {
        if (!raca) return false;
        if (raca.escolhe_duas_mais1 === true) return true;
        return (
            Array.isArray(raca.caracteristicas) &&
            raca.caracteristicas.includes('dois_bonus_habilidade_extra')
        );
    },

    labelBonusHabilidadeExtra(raca) {
        return raca ? `+1 (${raca.nome})` : '+1 (bônus racial)';
    },

    atualizarLabelsBonusExtra(raca, labelIds, getEl) {
        const texto = this.labelBonusHabilidadeExtra(raca);
        labelIds.forEach((id) => {
            const lbl = getEl(id);
            if (lbl) lbl.textContent = texto;
        });
    },
};
