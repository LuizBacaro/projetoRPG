/**
 * Utilitário D&D 5e — pendências de progressão (tradução, categorias, XP local).
 */
const Dnd5ePendenciasUtil = (() => {
    const LABELS = {
        hp_nivel_2: 'Rolar PV do nível 2',
        hp_nivel_3: 'Rolar PV do nível 3',
        hp_nivel_4: 'Rolar PV do nível 4',
        hp_nivel_5: 'Rolar PV do nível 5',
        hp_nivel_6: 'Rolar PV do nível 6',
        hp_nivel_7: 'Rolar PV do nível 7',
        hp_nivel_8: 'Rolar PV do nível 8',
        hp_nivel_9: 'Rolar PV do nível 9',
        hp_nivel_10: 'Rolar PV do nível 10',
        hp_nivel_11: 'Rolar PV do nível 11',
        hp_nivel_12: 'Rolar PV do nível 12',
        hp_nivel_13: 'Rolar PV do nível 13',
        hp_nivel_14: 'Rolar PV do nível 14',
        hp_nivel_15: 'Rolar PV do nível 15',
        hp_nivel_16: 'Rolar PV do nível 16',
        hp_nivel_17: 'Rolar PV do nível 17',
        hp_nivel_18: 'Rolar PV do nível 18',
        hp_nivel_19: 'Rolar PV do nível 19',
        hp_nivel_20: 'Rolar PV do nível 20',
        marco_nivel_4: 'Escolher incremento ou talento (nível 4)',
        marco_nivel_8: 'Escolher incremento ou talento (nível 8)',
        marco_nivel_12: 'Escolher incremento ou talento (nível 12)',
        marco_nivel_16: 'Escolher incremento ou talento (nível 16)',
        marco_nivel_19: 'Escolher incremento ou talento (nível 19)',
        feat_nivel_1: 'Escolher talento humano (nível 1)',
        feat_escolha_resilient: 'Escolher salvaguarda do talento Resiliente',
        feat_escolha_magic_initiate: 'Escolher classe do Iniciado em Magia',
        feat_escolha_skilled: 'Escolher 3 perícias do talento Habilidoso (Skilled)',
        feat_escolha_skill_expert: 'Escolher proficiência e expertise do talento Especialista',
        expertise_classe: 'Escolher perícias com Expertise (Ladino/Bardo)',
        revisar_feats: 'Revisar talentos registrados',
        hp_max_invalido: 'PV máximo inválido — confira as rolagens',
        xp_nao_salvo: 'Salvar a ficha para sincronizar XP e nível',
        xp_insuficiente: 'XP abaixo do mínimo exigido para o nível',
        xp_nivel_excedido: 'Nível exige mais XP do que o informado',
    };

    function traduzir(slug) {
        return LABELS[slug] || String(slug || '').replace(/_/g, ' ');
    }

    function categoria(slug) {
        const s = String(slug || '');
        if (s.startsWith('xp_')) return 'xp';
        if (s.startsWith('hp_nivel_') || s === 'hp_max_invalido') return 'hp';
        if (s.startsWith('marco_nivel_') || s === 'revisar_feats' || s === 'feat_nivel_1') return 'marco';
        if (s.startsWith('feat_escolha_')) return 'marco';
        if (s === 'expertise_classe') return 'pericia';
        return 'outro';
    }

    function pendenciasCliente({ nivel, xp, xpPrecisaSalvar, temPersonagem }) {
        const out = [];
        const n = Math.max(1, Math.min(20, parseInt(nivel, 10) || 1));
        const x = Math.max(0, parseInt(xp, 10) || 0);
        if (typeof Dnd5eXpUtil === 'undefined') return out;
        const xpMin = Dnd5eXpUtil.xpMinimaPorNivel(n);
        const maxNivel = Dnd5eXpUtil.nivelPorXp(x);
        if (x < xpMin) out.push('xp_insuficiente');
        if (n > maxNivel) out.push('xp_nivel_excedido');
        if (temPersonagem && xpPrecisaSalvar) out.push('xp_nao_salvo');
        return out;
    }

    function mergePendencias(servidor, ctx) {
        const base = Array.isArray(servidor) ? [...servidor] : [];
        const extras = pendenciasCliente(ctx || {});
        const seen = new Set(base);
        extras.forEach((p) => {
            if (!seen.has(p)) {
                base.push(p);
                seen.add(p);
            }
        });
        const ordem = { xp: 0, hp: 1, marco: 2, pericia: 3, outro: 4 };
        return base.sort((a, b) => {
            const ca = ordem[categoria(a)] ?? 9;
            const cb = ordem[categoria(b)] ?? 9;
            if (ca !== cb) return ca - cb;
            return traduzir(a).localeCompare(traduzir(b), 'pt-BR');
        });
    }

    function resumoAlerta(pendencias) {
        const lista = Array.isArray(pendencias) ? pendencias : [];
        if (!lista.length) return '';
        const cats = { xp: 0, hp: 0, marco: 0, outro: 0 };
        lista.forEach((p) => {
            cats[categoria(p)] = (cats[categoria(p)] || 0) + 1;
        });
        const partes = [];
        if (cats.xp) partes.push(`${cats.xp} XP/nível`);
        if (cats.hp) partes.push(`${cats.hp} PV`);
        if (cats.marco) partes.push(`${cats.marco} marco(s)`);
        if (cats.outro) partes.push(`${cats.outro} outra(s)`);
        return partes.join(' · ');
    }

    function nivelDePendencia(slug) {
        const m = String(slug || '').match(/_(\d+)$/);
        return m ? parseInt(m[1], 10) : null;
    }

    return {
        LABELS,
        traduzir,
        categoria,
        pendenciasCliente,
        mergePendencias,
        resumoAlerta,
        nivelDePendencia,
    };
})();
