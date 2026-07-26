/**
 * RF-T04i — catálogo de usos na rolagem (mesma perícia; não linha separada).
 * P0: Atletismo · P1: Enganação, Acrobacia, Ladinagem, Sobrevivência, Cura ·
 * P2: Diplomacia, Investigação, Adestramento, Percepção · P3: Cavalgar.
 * Atuação: fora até confirmar no livro se é especialidade (Ofício) ou só rótulo.
 * Extensível: basta acrescentar entradas em USOS_POR_SLUG.
 */
(function (global) {
    'use strict';

    /** @type {Record<string, { id: string, rotulo: string, hint?: string }[]>} */
    const USOS_POR_SLUG = {
        atletismo: [
            { id: 'escalar', rotulo: 'Escalar' },
            { id: 'nadar', rotulo: 'Nadar', hint: 'Aplica penalidade de armadura' },
            { id: 'saltar', rotulo: 'Saltar' },
        ],
        enganacao: [
            { id: 'blefar', rotulo: 'Blefar' },
            { id: 'disfarce', rotulo: 'Disfarce' },
            { id: 'fingir', rotulo: 'Fingir' },
        ],
        acrobacia: [
            { id: 'equilibrio', rotulo: 'Equilíbrio' },
            { id: 'escapar', rotulo: 'Escapar' },
            { id: 'queda', rotulo: 'Queda' },
        ],
        ladinagem: [
            { id: 'fechaduras', rotulo: 'Fechaduras' },
            { id: 'armadilhas', rotulo: 'Armadilhas' },
            { id: 'pungar', rotulo: 'Pungar' },
        ],
        sobrevivencia: [
            { id: 'orientar', rotulo: 'Orientar' },
            { id: 'rastrear', rotulo: 'Rastrear' },
            { id: 'forragear', rotulo: 'Forragear' },
        ],
        cura: [
            { id: 'primeiros_socorros', rotulo: 'Primeiros Socorros' },
            { id: 'tratamento', rotulo: 'Tratamento' },
        ],
        diplomacia: [
            { id: 'persuadir', rotulo: 'Persuadir' },
            { id: 'barganhar', rotulo: 'Barganhar' },
            {
                id: 'obter_informacao',
                rotulo: 'Obter Informação',
                hint: 'Uso legado MB (perícia removida do catálogo v1.3)',
            },
        ],
        investigacao: [
            { id: 'buscar', rotulo: 'Buscar' },
            { id: 'analisar', rotulo: 'Analisar' },
            {
                id: 'obter_informacao',
                rotulo: 'Obter Informação',
                hint: 'Uso legado MB (perícia removida do catálogo v1.3)',
            },
        ],
        adestramento: [
            { id: 'comandar', rotulo: 'Comandar' },
            { id: 'treinar', rotulo: 'Treinar' },
        ],
        percepcao: [
            { id: 'observar', rotulo: 'Observar' },
            { id: 'ouvir', rotulo: 'Ouvir' },
        ],
        cavalgar: [
            { id: 'montar', rotulo: 'Montar' },
            { id: 'combater_montado', rotulo: 'Combater Montado' },
        ],
    };

    const DEFAULT_USO = {
        atletismo: 'escalar',
        diplomacia: 'persuadir',
        investigacao: 'buscar',
        adestramento: 'comandar',
        percepcao: 'observar',
        cavalgar: 'montar',
    };

    /** Último uso escolhido na sessão (memória em runtime). */
    const ultimoUsoPorSlug = Object.create(null);

    const ALIAS_NOME = {
        atletismo: 'atletismo',
        enganacao: 'enganacao',
        enganação: 'enganacao',
        acrobacia: 'acrobacia',
        ladinagem: 'ladinagem',
        sobrevivencia: 'sobrevivencia',
        sobrevivência: 'sobrevivencia',
        cura: 'cura',
        diplomacia: 'diplomacia',
        investigacao: 'investigacao',
        investigação: 'investigacao',
        adestramento: 'adestramento',
        percepcao: 'percepcao',
        percepção: 'percepcao',
        cavalgar: 'cavalgar',
    };

    function normalizarSlug(slugOuNome) {
        let s = String(slugOuNome || '')
            .trim()
            .toLowerCase();
        if (!s) return '';
        if (USOS_POR_SLUG[s]) return s;
        if (ALIAS_NOME[s]) return ALIAS_NOME[s];
        s = s
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/[^a-z0-9]+/g, '_')
            .replace(/^_+|_+$/g, '');
        if (USOS_POR_SLUG[s]) return s;
        if (ALIAS_NOME[s]) return ALIAS_NOME[s];
        return s;
    }

    function usosDaPericia(slugOuNome) {
        const slug = normalizarSlug(slugOuNome);
        const lista = USOS_POR_SLUG[slug];
        if (!lista || !lista.length) return [];
        return lista.map((u) => ({
            id: u.id,
            rotulo: u.rotulo,
            hint: u.hint || undefined,
        }));
    }

    function temUsos(slugOuNome) {
        return usosDaPericia(slugOuNome).length > 0;
    }

    function usoPorId(slugOuNome, usoId) {
        const id = String(usoId || '').trim();
        if (!id) return null;
        return usosDaPericia(slugOuNome).find((u) => u.id === id) || null;
    }

    function usoDefault(slugOuNome) {
        const slug = normalizarSlug(slugOuNome);
        const lista = usosDaPericia(slug);
        if (!lista.length) return null;
        const mem = ultimoUsoPorSlug[slug];
        if (mem && lista.some((u) => u.id === mem)) return mem;
        if (DEFAULT_USO[slug] && lista.some((u) => u.id === DEFAULT_USO[slug])) {
            return DEFAULT_USO[slug];
        }
        return lista[0].id;
    }

    function lembrarUso(slugOuNome, usoId) {
        const slug = normalizarSlug(slugOuNome);
        const u = usoPorId(slug, usoId);
        if (!slug || !u) return;
        ultimoUsoPorSlug[slug] = u.id;
    }

    function formatarNomeComUso(nomePericia, slugOuNome, usoId) {
        const base = String(nomePericia || '').trim() || 'Perícia';
        const u = usoPorId(slugOuNome || nomePericia, usoId);
        if (!u) return base;
        return `${base} (${u.rotulo})`;
    }

    /** Atletismo + nadar → flag de API; demais usos / perícias → false. */
    function usoAtletismoNatacao(slugOuNome, usoId) {
        return normalizarSlug(slugOuNome) === 'atletismo' && String(usoId || '') === 'nadar';
    }

    global.T20PericiasUsos = {
        USOS_POR_SLUG,
        normalizarSlug,
        usosDaPericia,
        temUsos,
        usoPorId,
        usoDefault,
        lembrarUso,
        formatarNomeComUso,
        usoAtletismoNatacao,
    };
})(typeof window !== 'undefined' ? window : globalThis);
