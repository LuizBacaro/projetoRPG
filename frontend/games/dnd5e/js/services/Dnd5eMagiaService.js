/**
 * Catálogo de magias D&D 5e — `/api/v1/dnd5e/magias`.
 * Compatível com MagiaService (dnd35) para reutilizar o grimório compartilhado (base dnd35).
 */
import { getApiUrl } from '/games/dnd35/js/config/api.config.js';

/** Limite máximo aceito por GET /dnd5e/magias (FastAPI le=500). */
const API_LIMIT_MAX = 500;

const ALIASES = {
    feiticeiro: 'mago',
    sorcerer: 'mago',
    wizard: 'mago',
    cleric: 'clerigo',
    druid: 'druida',
    bard: 'bardo',
    warlock: 'bruxo',
    paladin: 'paladino',
    ranger: 'patrulheiro',
};

export class Dnd5eMagiaService {
    constructor(token) {
        this.token = token || localStorage.getItem('token');
        this._cache = new Map();
    }

    _headers() {
        const h = { 'Content-Type': 'application/json' };
        if (this.token) h.Authorization = `Bearer ${this.token}`;
        return h;
    }

    _normalizarClasse(classe) {
        const base = String(classe || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .trim();
        return ALIASES[base] || base;
    }

    async listarPorClasse(classe) {
        const slug = this._normalizarClasse(classe);
        if (this._cache.has(slug)) return this._cache.get(slug);

        const magias = [];
        let skip = 0;
        let total = Number.POSITIVE_INFINITY;

        while (skip < total) {
            const pagina = await this.listarPorClassePaginado(slug, {
                skip,
                limit: API_LIMIT_MAX,
            });
            const lote = pagina.items || [];
            magias.push(...lote);
            total = Number.isFinite(pagina.total) ? pagina.total : magias.length;
            if (!lote.length || lote.length < API_LIMIT_MAX) break;
            skip += lote.length;
        }

        this._cache.set(slug, magias);
        return magias;
    }

    async listarPorClassePaginado(
        classe,
        { nome, nivel, maxNivel, escola, componentes, skip = 0, limit = 20 } = {}
    ) {
        const slug = this._normalizarClasse(classe);
        const query = new URLSearchParams();
        query.set('classe', slug);
        if (nome) query.set('nome', String(nome).trim());
        if (nivel !== undefined && nivel !== null && String(nivel) !== 'todos') {
            query.set('nivel', String(nivel));
        } else if (maxNivel !== undefined && maxNivel !== null && String(maxNivel) !== '') {
            query.set('max_nivel', String(maxNivel));
        }
        if (escola && escola !== 'todas') query.set('escola', String(escola).trim());
        if (componentes && componentes !== 'todos') {
            query.set('componentes', String(componentes).trim());
        }
        const limitClamped = Math.min(
            API_LIMIT_MAX,
            Math.max(1, Number(limit) || 20)
        );
        query.set('skip', String(Math.max(0, Number(skip) || 0)));
        query.set('limit', String(limitClamped));

        const url = getApiUrl(`/dnd5e/magias?${query.toString()}`);
        const res = await fetch(url, { headers: this._headers() });
        if (!res.ok) {
            throw new Error(`Falha ao carregar magias (HTTP ${res.status})`);
        }
        const body = await res.json();
        const raw = Array.isArray(body) ? body : body.magias || body.items || [];
        const items = raw.map((m) => this._mapMagia(m));
        const totalHeader = Number(res.headers.get('X-Total-Count'));
        return {
            items,
            total: Number.isFinite(totalHeader) ? totalHeader : items.length,
            skip: Math.max(0, Number(skip) || 0),
            limit: limitClamped,
        };
    }

    _mapMagia(m) {
        return {
            id: m.id,
            nome: m.nome,
            nivel: m.nivel,
            escola: m.escola,
            componentes: m.componentes,
            descricao: m.descricao,
            tempo_conjuracao: m.tempo_conjuracao,
            alcance: m.alcance_texto,
            duracao: m.duracao,
            dano: m.dano,
            teste_resistencia: m.teste_resistencia,
        };
    }

    async obter(magiaId) {
        const url = getApiUrl(`/dnd5e/magias/${magiaId}`);
        const res = await fetch(url, { headers: this._headers() });
        if (!res.ok) throw new Error(`Magia não encontrada (${res.status})`);
        return this._mapMagia(await res.json());
    }
}
