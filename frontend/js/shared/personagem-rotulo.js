/**
 * Rótulo de personagem com nome da conta (dono_nome) para listas e campanhas.
 */
(function (global) {
    function tipoExibicao(personagem) {
        const tipoLabel = String(personagem?.tipo || '').toLowerCase();
        if (!tipoLabel) return 'Personagem';
        return tipoLabel.charAt(0).toUpperCase() + tipoLabel.slice(1);
    }

    function donoRotulo(personagem) {
        const dono = String(personagem?.dono_nome || '').trim();
        if (!dono) return '';
        if (String(personagem?.tipo || '').toLowerCase() !== 'jogador') return '';
        return dono;
    }

    /**
     * @param {object} personagem
     * @param {string} [detalhe] Ex.: "Nv 3", "150 pts"
     * @returns {string} texto sem escape HTML
     */
    function rotuloPersonagemComDono(personagem, detalhe) {
        const nome = String(personagem?.nome || '').trim() || '—';
        const dono = donoRotulo(personagem);
        const tipo = tipoExibicao(personagem);
        const sufixo = detalhe ? `${tipo} • ${detalhe}` : tipo;
        if (dono) return `${nome} — ${dono} (${sufixo})`;
        return `${nome} (${sufixo})`;
    }

    function textoBuscaPersonagem(personagem) {
        const partes = [
            personagem?.nome,
            personagem?.dono_nome,
            personagem?.tipo,
            personagem?.jogador_nome,
        ];
        return partes
            .map((p) => String(p || '').toLowerCase())
            .join(' ');
    }

    global.PersonagemRotulo = {
        rotuloPersonagemComDono,
        textoBuscaPersonagem,
        tipoExibicao,
        donoRotulo,
    };
})(typeof window !== 'undefined' ? window : globalThis);
