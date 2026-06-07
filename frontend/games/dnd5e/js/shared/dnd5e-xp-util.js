/**
 * Utilitário D&D 5e — tabela de XP por nível (PHB) e sincronização nível ↔ experiência.
 */
const Dnd5eXpUtil = (() => {
    const TABELA_PADRAO = [
        { nivel: 1, xp_total: 0 },
        { nivel: 2, xp_total: 300 },
        { nivel: 3, xp_total: 900 },
        { nivel: 4, xp_total: 2700 },
        { nivel: 5, xp_total: 6500 },
        { nivel: 6, xp_total: 14000 },
        { nivel: 7, xp_total: 23000 },
        { nivel: 8, xp_total: 34000 },
        { nivel: 9, xp_total: 48000 },
        { nivel: 10, xp_total: 64000 },
        { nivel: 11, xp_total: 85000 },
        { nivel: 12, xp_total: 100000 },
        { nivel: 13, xp_total: 120000 },
        { nivel: 14, xp_total: 140000 },
        { nivel: 15, xp_total: 165000 },
        { nivel: 16, xp_total: 195000 },
        { nivel: 17, xp_total: 225000 },
        { nivel: 18, xp_total: 265000 },
        { nivel: 19, xp_total: 305000 },
        { nivel: 20, xp_total: 355000 },
    ];

    let tabela = null;

    function setTabela(xpPorNivel) {
        if (!Array.isArray(xpPorNivel) || !xpPorNivel.length) {
            tabela = null;
            return;
        }
        tabela = xpPorNivel
            .map((row) => ({
                nivel: parseInt(row.nivel, 10),
                xp_total: parseInt(row.xp_total, 10),
            }))
            .filter((row) => Number.isFinite(row.nivel) && Number.isFinite(row.xp_total))
            .sort((a, b) => a.nivel - b.nivel);
    }

    function getTabela() {
        return tabela && tabela.length ? tabela : TABELA_PADRAO;
    }

    function xpMinimaPorNivel(nivel) {
        const n = Math.max(1, Math.min(20, parseInt(nivel, 10) || 1));
        const row = getTabela().find((r) => r.nivel === n);
        return row ? row.xp_total : 0;
    }

    function nivelPorXp(xp) {
        const x = Math.max(0, parseInt(xp, 10) || 0);
        let nivel = 1;
        for (const row of getTabela()) {
            if (x >= row.xp_total) nivel = row.nivel;
        }
        return nivel;
    }

    function aplicarNivelParaXp(nivelInput, xpInput) {
        if (!nivelInput || !xpInput) return false;
        const xp = xpMinimaPorNivel(nivelInput.value);
        const atual = parseInt(xpInput.value, 10) || 0;
        if (atual === xp) return false;
        xpInput.value = String(xp);
        return true;
    }

    function aplicarXpParaNivel(xpInput, nivelInput) {
        if (!xpInput || !nivelInput) return null;
        const novoNivel = nivelPorXp(xpInput.value);
        const atual = parseInt(nivelInput.value, 10) || 1;
        if (novoNivel === atual) return null;
        nivelInput.value = String(novoNivel);
        return novoNivel;
    }

    return {
        setTabela,
        getTabela,
        xpMinimaPorNivel,
        nivelPorXp,
        aplicarNivelParaXp,
        aplicarXpParaNivel,
    };
})();
