/**
 * RF-T04i — catálogo de usos na rolagem (mesma perícia; não linha separada).
 * Fonte: Tormenta20 Edição Jogo do Ano v1.3 — Cap. 2 Perícias (p.114–123).
 * Ofício = especialidades em linhas próprias (não este catálogo).
 *
 * Bônus por uso (persistido em `ficha_json.pericias_usos_bonus`):
 * `{ enganacao: { mentir: 2 }, … }` — soma no teste via `bonus_uso`, não na CD.
 */
(function (global) {
    'use strict';

    /**
     * @typedef {{ id: string, rotulo: string, hint?: string, apenas_treinado?: boolean }} UsoPericia
     * @type {Record<string, UsoPericia[]>}
     */
    const USOS_POR_SLUG = {
        acrobacia: [
            {
                id: 'amortecer_queda',
                rotulo: 'Amortecer Queda',
                apenas_treinado: true,
                hint: 'Apenas Treinado',
            },
            { id: 'equilibrio', rotulo: 'Equilíbrio' },
            { id: 'escapar', rotulo: 'Escapar' },
            {
                id: 'levantar_se',
                rotulo: 'Levantar-se Rapidamente',
                apenas_treinado: true,
                hint: 'Apenas Treinado',
            },
            {
                id: 'espaco_apertado',
                rotulo: 'Passar por Espaço Apertado',
                apenas_treinado: true,
                hint: 'Apenas Treinado',
            },
            { id: 'passar_inimigo', rotulo: 'Passar por Inimigo' },
        ],
        adestramento: [
            { id: 'acalmar_animal', rotulo: 'Acalmar Animal' },
            { id: 'manejar_animal', rotulo: 'Manejar Animal' },
        ],
        atletismo: [
            { id: 'corrida', rotulo: 'Corrida' },
            { id: 'escalar', rotulo: 'Escalar' },
            {
                id: 'natacao',
                rotulo: 'Natação',
                hint: 'Aplica penalidade de armadura',
            },
            { id: 'saltar', rotulo: 'Saltar' },
        ],
        atuacao: [
            { id: 'apresentacao', rotulo: 'Apresentação' },
            { id: 'impressionar', rotulo: 'Impressionar' },
        ],
        cavalgar: [
            { id: 'conduzir', rotulo: 'Conduzir' },
            { id: 'galopar', rotulo: 'Galopar' },
            { id: 'montar_rapidamente', rotulo: 'Montar Rapidamente' },
        ],
        conhecimento: [
            { id: 'idiomas', rotulo: 'Idiomas' },
            { id: 'informacao', rotulo: 'Informação' },
        ],
        cura: [
            {
                id: 'cuidados_prolongados',
                rotulo: 'Cuidados Prolongados',
                apenas_treinado: true,
                hint: 'Apenas Treinado',
            },
            {
                id: 'necropsia',
                rotulo: 'Necropsia',
                apenas_treinado: true,
                hint: 'Apenas Treinado',
            },
            { id: 'primeiros_socorros', rotulo: 'Primeiros Socorros' },
            {
                id: 'tratamento',
                rotulo: 'Tratamento',
                apenas_treinado: true,
                hint: 'Apenas Treinado',
            },
        ],
        diplomacia: [
            { id: 'barganha', rotulo: 'Barganha' },
            { id: 'mudar_atitude', rotulo: 'Mudar Atitude' },
            { id: 'persuasao', rotulo: 'Persuasão' },
        ],
        enganacao: [
            { id: 'disfarce', rotulo: 'Disfarce' },
            { id: 'falsificacao', rotulo: 'Falsificação' },
            { id: 'fintar', rotulo: 'Fintar' },
            { id: 'insinuacao', rotulo: 'Insinuação' },
            { id: 'intriga', rotulo: 'Intriga' },
            { id: 'mentir', rotulo: 'Mentir' },
        ],
        furtividade: [
            { id: 'esconder_se', rotulo: 'Esconder-se' },
            { id: 'seguir', rotulo: 'Seguir' },
        ],
        guerra: [
            { id: 'analisar_terreno', rotulo: 'Analisar Terreno' },
            { id: 'plano_de_acao', rotulo: 'Plano de Ação' },
        ],
        intimidacao: [
            { id: 'assustar', rotulo: 'Assustar' },
            { id: 'coagir', rotulo: 'Coagir' },
        ],
        intuicao: [
            { id: 'perceber_mentira', rotulo: 'Perceber Mentira' },
            {
                id: 'pressentimento',
                rotulo: 'Pressentimento',
                apenas_treinado: true,
                hint: 'Apenas Treinado',
            },
        ],
        investigacao: [
            { id: 'interrogar', rotulo: 'Interrogar' },
            { id: 'procurar', rotulo: 'Procurar' },
        ],
        jogatina: [{ id: 'apostar', rotulo: 'Apostar' }],
        ladinagem: [
            { id: 'abrir_fechadura', rotulo: 'Abrir Fechadura' },
            { id: 'ocultar', rotulo: 'Ocultar' },
            { id: 'punga', rotulo: 'Punga' },
            { id: 'sabotar', rotulo: 'Sabotar' },
        ],
        misticismo: [
            { id: 'detectar_magia', rotulo: 'Detectar Magia' },
            { id: 'identificar_criatura', rotulo: 'Identificar Criatura' },
            { id: 'identificar_item', rotulo: 'Identificar Item Mágico' },
            { id: 'identificar_magia', rotulo: 'Identificar Magia' },
            { id: 'informacao', rotulo: 'Informação' },
            {
                id: 'lancar_magia_armadura',
                rotulo: 'Lançar Magia de Armadura',
                hint: 'Penalidade de armadura no teste',
            },
        ],
        nobreza: [
            { id: 'etiqueta', rotulo: 'Etiqueta' },
            { id: 'informacao', rotulo: 'Informação' },
        ],
        percepcao: [
            { id: 'observar', rotulo: 'Observar' },
            { id: 'ouvir', rotulo: 'Ouvir' },
        ],
        religiao: [
            { id: 'identificar_criatura', rotulo: 'Identificar Criatura' },
            { id: 'identificar_item', rotulo: 'Identificar Item Mágico' },
            { id: 'informacao', rotulo: 'Informação' },
            { id: 'rito', rotulo: 'Rito' },
        ],
        sobrevivencia: [
            { id: 'acampamento', rotulo: 'Acampamento' },
            { id: 'identificar_criatura', rotulo: 'Identificar Criatura' },
            { id: 'orientar_se', rotulo: 'Orientar-se' },
            {
                id: 'rastrear',
                rotulo: 'Rastrear',
                apenas_treinado: true,
                hint: 'Apenas Treinado',
            },
        ],
    };

    const DEFAULT_USO = {
        acrobacia: 'equilibrio',
        adestramento: 'manejar_animal',
        atletismo: 'escalar',
        atuacao: 'apresentacao',
        cavalgar: 'conduzir',
        conhecimento: 'informacao',
        cura: 'primeiros_socorros',
        diplomacia: 'persuasao',
        enganacao: 'mentir',
        furtividade: 'esconder_se',
        guerra: 'analisar_terreno',
        intimidacao: 'assustar',
        intuicao: 'perceber_mentira',
        investigacao: 'procurar',
        jogatina: 'apostar',
        ladinagem: 'abrir_fechadura',
        misticismo: 'identificar_magia',
        nobreza: 'etiqueta',
        percepcao: 'observar',
        religiao: 'informacao',
        sobrevivencia: 'orientar_se',
    };

    /**
     * Ids antigos → canônicos (v1.3 Cap. 2), por perícia.
     * Entradas sem mapeamento válido são descartadas em `aplicarBonusMap`.
     * @type {Record<string, Record<string, string>>}
     */
    const MIGRACAO_USO_IDS = {
        atletismo: { nadar: 'natacao' },
        enganacao: { blefar: 'mentir', fingir: 'fintar' },
        acrobacia: { queda: 'amortecer_queda' },
        ladinagem: {
            fechaduras: 'abrir_fechadura',
            armadilhas: 'sabotar',
            pungar: 'punga',
        },
        sobrevivencia: { orientar: 'orientar_se' },
        diplomacia: {
            persuadir: 'persuasao',
            barganhar: 'barganha',
            obter_informacao: 'persuasao',
        },
        investigacao: {
            buscar: 'procurar',
            analisar: 'interrogar',
            obter_informacao: 'interrogar',
        },
        adestramento: { comandar: 'manejar_animal', treinar: 'acalmar_animal' },
        cavalgar: { montar: 'montar_rapidamente', combater_montado: 'galopar' },
    };

    /** Último uso escolhido na sessão (memória em runtime). */
    const ultimoUsoPorSlug = Object.create(null);

    /**
     * Bônus persistidos por perícia → uso.
     * @type {Record<string, Record<string, number>>}
     */
    let bonusPorSlugUso = Object.create(null);

    const ALIAS_NOME = {
        atletismo: 'atletismo',
        atuacao: 'atuacao',
        atuação: 'atuacao',
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
        conhecimento: 'conhecimento',
        furtividade: 'furtividade',
        guerra: 'guerra',
        intimidacao: 'intimidacao',
        intimidação: 'intimidacao',
        intuicao: 'intuicao',
        intuição: 'intuicao',
        jogatina: 'jogatina',
        misticismo: 'misticismo',
        nobreza: 'nobreza',
        religiao: 'religiao',
        religião: 'religiao',
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

    function migrarUsoId(slug, usoId) {
        const id = String(usoId || '').trim();
        if (!id) return '';
        const map = MIGRACAO_USO_IDS[slug];
        if (map && map[id]) return map[id];
        return id;
    }

    function usosDaPericia(slugOuNome) {
        const slug = normalizarSlug(slugOuNome);
        const lista = USOS_POR_SLUG[slug];
        if (!lista || !lista.length) return [];
        return lista.map((u) => ({
            id: u.id,
            rotulo: u.rotulo,
            hint: u.hint || undefined,
            apenas_treinado: Boolean(u.apenas_treinado),
        }));
    }

    function temUsos(slugOuNome) {
        return usosDaPericia(slugOuNome).length > 0;
    }

    function usoPorId(slugOuNome, usoId) {
        const slug = normalizarSlug(slugOuNome);
        const id = migrarUsoId(slug, usoId);
        if (!id) return null;
        return usosDaPericia(slug).find((u) => u.id === id) || null;
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

    /** Atletismo + natação → flag de API; aceita id legado `nadar`. */
    function usoAtletismoNatacao(slugOuNome, usoId) {
        if (normalizarSlug(slugOuNome) !== 'atletismo') return false;
        const id = migrarUsoId('atletismo', usoId);
        return id === 'natacao';
    }

    function _clampBonus(n) {
        if (!Number.isFinite(n)) return 0;
        return Math.max(-99, Math.min(99, Math.trunc(n)));
    }

    function bonusDoUso(slugOuNome, usoId) {
        const slug = normalizarSlug(slugOuNome);
        const id = migrarUsoId(slug, usoId);
        if (!slug || !id) return 0;
        const n = Number(bonusPorSlugUso[slug] && bonusPorSlugUso[slug][id]);
        return _clampBonus(Number.isFinite(n) ? n : 0);
    }

    function setBonusUso(slugOuNome, usoId, valor) {
        const slug = normalizarSlug(slugOuNome);
        const id = migrarUsoId(slug, usoId);
        if (!slug || !id) return;
        if (!usoPorId(slug, id)) return;
        const n = _clampBonus(Number(valor));
        if (!bonusPorSlugUso[slug]) bonusPorSlugUso[slug] = Object.create(null);
        if (n === 0) {
            delete bonusPorSlugUso[slug][id];
            if (!Object.keys(bonusPorSlugUso[slug]).length) delete bonusPorSlugUso[slug];
        } else {
            bonusPorSlugUso[slug][id] = n;
        }
    }

    /** Snapshot limpo para `ficha_json.pericias_usos_bonus`. */
    function lerBonusMap() {
        const out = {};
        Object.keys(bonusPorSlugUso).forEach((slug) => {
            const usos = bonusPorSlugUso[slug];
            if (!usos || typeof usos !== 'object') return;
            const inner = {};
            Object.keys(usos).forEach((id) => {
                const n = _clampBonus(Number(usos[id]));
                if (n !== 0) inner[id] = n;
            });
            if (Object.keys(inner).length) out[slug] = inner;
        });
        return out;
    }

    function aplicarBonusMap(map) {
        bonusPorSlugUso = Object.create(null);
        if (!map || typeof map !== 'object' || Array.isArray(map)) {
            if (typeof global.T20PericiasUsosBadgeAll === 'function') {
                try {
                    global.T20PericiasUsosBadgeAll();
                } catch (_e) {
                    /* ignore */
                }
            }
            return;
        }
        Object.keys(map).forEach((rawSlug) => {
            const slug = normalizarSlug(rawSlug);
            if (!slug || !temUsos(slug)) return;
            const usos = map[rawSlug];
            if (!usos || typeof usos !== 'object' || Array.isArray(usos)) return;
            Object.keys(usos).forEach((rawId) => {
                const id = migrarUsoId(slug, rawId);
                if (!usoPorId(slug, id)) return;
                const n = _clampBonus(Number(usos[rawId]));
                if (n !== 0) setBonusUso(slug, id, n);
            });
        });
        if (typeof global.T20PericiasUsosBadgeAll === 'function') {
            try {
                global.T20PericiasUsosBadgeAll();
            } catch (_e) {
                /* ignore */
            }
        }
    }

    function contarUsosComBonus(slugOuNome) {
        const slug = normalizarSlug(slugOuNome);
        const usos = bonusPorSlugUso[slug];
        if (!usos || typeof usos !== 'object') return 0;
        return Object.keys(usos).filter((id) => _clampBonus(Number(usos[id])) !== 0).length;
    }

    /** Lista legível dos usos com bônus (para title do badge). */
    function listarUsosComBonus(slugOuNome) {
        const slug = normalizarSlug(slugOuNome);
        const usos = bonusPorSlugUso[slug];
        if (!usos || typeof usos !== 'object') return [];
        const out = [];
        Object.keys(usos).forEach((id) => {
            const n = _clampBonus(Number(usos[id]));
            if (n === 0) return;
            const u = usoPorId(slug, id);
            const rotulo = u ? u.rotulo : id;
            out.push(`${rotulo} ${n > 0 ? '+' : ''}${n}`);
        });
        return out;
    }

    global.T20PericiasUsos = {
        USOS_POR_SLUG,
        MIGRACAO_USO_IDS,
        normalizarSlug,
        usosDaPericia,
        temUsos,
        usoPorId,
        usoDefault,
        lembrarUso,
        formatarNomeComUso,
        usoAtletismoNatacao,
        bonusDoUso,
        setBonusUso,
        lerBonusMap,
        aplicarBonusMap,
        contarUsosComBonus,
        listarUsosComBonus,
        migrarUsoId,
    };
})(typeof window !== 'undefined' ? window : globalThis);
