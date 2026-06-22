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

    temVarianteEscolha(raca) {
        if (!raca) return false;
        if (raca.escolhe_variante === true) return true;
        return Array.isArray(raca.variantes) && raca.variantes.length > 0;
    },

    listarVariantes(raca) {
        if (!raca || !Array.isArray(raca.variantes)) return [];
        return raca.variantes;
    },

    labelVariante(raca) {
        if (!raca) return 'Linhagem';
        return raca.slug === 'tiefling' ? 'Herança infernal' : 'Ancestralidade dracônica';
    },

    temPericiaExtra(raca) {
        if (!raca) return false;
        if (
            Array.isArray(raca.caracteristicas) &&
            raca.caracteristicas.includes('proficiencia_pericia_extra')
        ) {
            return true;
        }
        return this.racaExigePericiaExtraPorSlug(raca.slug);
    },

    racaExigePericiaExtraPorSlug(slug) {
        const s = (slug || '').trim().toLowerCase();
        return s === 'humano' || s === 'meio_elfo';
    },

    precisaSecaoRacaExtra(raca) {
        return (
            this.temBonusHabilidadeExtraEscolha(raca) || this.temVarianteEscolha(raca)
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

    preencherSelectVariante(raca, selectEl, valorAtual) {
        if (!selectEl) return;
        const variantes = this.listarVariantes(raca);
        if (!variantes.length) {
            selectEl.innerHTML = '';
            return;
        }
        selectEl.innerHTML =
            '<option value="">— escolha —</option>' +
            variantes
                .map(
                    (v) =>
                        `<option value="${v.slug}">${v.nome} (resist. ${v.tipo_dano_pt || v.tipo_dano || ''})</option>`
                )
                .join('');
        if (valorAtual) selectEl.value = valorAtual;
    },
};
