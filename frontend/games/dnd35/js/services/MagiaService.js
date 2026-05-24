/**
 * MagiaService.js
 * SRP: Comunicação HTTP exclusivamente com /magias
 * SOLID: DIP — injetável via constructor
 * ✅ FIX: Busca por classe em MAIÚSCULA + fallback com filtro correto
 */

import { getApiUrl } from '../config/api.config.js';
import { classeTabelaMagias } from '../utils/combat-rules.js?v=20260524a';

/** Aliases de classe → token usado na API /magias (MAIÚSCULAS, sem acento). */
const CLASSE_API_ALIASES = {
    FEITICEIRO: 'MAGO',
    SORCERER: 'MAGO',
    WIZARD: 'MAGO',
    PATRULHEIRO: 'RANGER',
    CLERIC: 'CLERIGO',
    DRUID: 'DRUIDA',
    BARD: 'BARDO',
    PALADIN: 'PALADINO',
};

export class MagiaService {
    constructor(token) {
        this.token = token || localStorage.getItem('token');
        this._cache = new Map();
    }

    _headers() {
        const h = { 'Content-Type': 'application/json' };
        if (this.token) h['Authorization'] = `Bearer ${this.token}`;
        return h;
    }

    /**
     * Normaliza classe para MAIÚSCULA (como está no banco)
     * Mapeia Feiticeiro → Mago (mesmas magias)
     * @private
     * @param {string} classe
     * @returns {string}
     */
    _normalizarClasse(classe) {
        const tabela = classeTabelaMagias(classe) || String(classe || '').trim();
        const valorBase = String(tabela || classe || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '');
        let classNorm = valorBase.toUpperCase().trim();

        classNorm = CLASSE_API_ALIASES[classNorm] || classNorm;

        return classNorm;
    }

    _normalizarFiltroToken(valor, padrao) {
        const token = String(valor ?? padrao).trim().toLowerCase();
        return token || padrao;
    }

    /**
     * Busca magias filtradas por classe
     * @param {string} classe - Ex: 'Mago', 'Clérigo' (será convertido para MAIÚSCULA)
     * @returns {Promise<Array>}
     */
    async listarPorClasse(classe, { forceRefresh = false } = {}) {
        const classeNormalizada = this._normalizarClasse(classe);

        if (!classeNormalizada) {
            return [];
        }

        if (!forceRefresh && this._cache.has(classeNormalizada)) {
            const cached = this._cache.get(classeNormalizada);
            if (Array.isArray(cached) && cached.length > 0) {
                return cached;
            }
        }

        try {
            const magias = await this.listarTodasPorClasse(classeNormalizada, { forceRefresh });

            if (!magias || magias.length === 0) {
                console.info(
                    '[MagiaService] Catálogo vazio ou sem magias para a classe; ' +
                    'importe magias (admin) ou verifique a classe do personagem.'
                );
                return [];
            }

            this._cache.set(classeNormalizada, magias);
            return magias;
        } catch (err) {
            console.error(`❌ Erro ao buscar magias de ${classeNormalizada}:`, err);
            try {
                return await this._listarTodasEFiltrar(classeNormalizada);
            } catch (fallbackErr) {
                console.error('❌ Fallback também falhou:', fallbackErr);
                throw fallbackErr;
            }
        }
    }

    /**
     * Carrega todas as magias de uma classe (paginação server-side com ?classe=).
     * @param {string} classe
     * @param {{ forceRefresh?: boolean }} [opts]
     */
    async listarTodasPorClasse(classe, { forceRefresh = false } = {}) {
        const classeNormalizada = this._normalizarClasse(classe);
        if (!classeNormalizada) return [];

        if (!forceRefresh && this._cache.has(classeNormalizada)) {
            const cached = this._cache.get(classeNormalizada);
            if (Array.isArray(cached) && cached.length > 0) {
                return cached;
            }
        }

        const pageSize = 500;
        let skip = 0;
        let totalEsperado = Infinity;
        const acumulado = [];

        while (skip < totalEsperado) {
            const pagina = await this.listarPorClassePaginado(classeNormalizada, {
                skip,
                limit: pageSize,
            });

            const lote = Array.isArray(pagina?.items) ? pagina.items : [];
            const total = Math.max(0, Number(pagina?.total || 0));
            if (Number.isFinite(total) && total > 0) {
                totalEsperado = total;
            }

            if (!lote.length) {
                break;
            }

            acumulado.push(...lote);
            skip += lote.length;

            if (lote.length < pageSize) {
                break;
            }
        }

        if (acumulado.length > 0) {
            this._cache.set(classeNormalizada, acumulado);
        }

        return acumulado;
    }

    async ListaMagiaPorClasse(classe) {
        return this.listarPorClasse(classe);
    }

    async listarMagiaPorClasse(classe) {
        return this.listarPorClasse(classe);
    }

    async listarMagiasPorClasse(classe) {
        return this.listarPorClasse(classe);
    }

    async listarPorClassePaginado(classe, {
        nome,
        nivel,
        escola,
        componentes,
        skip = 0,
        limit = 20,
    } = {}) {
        const classeNormalizada = this._normalizarClasse(classe);
        const query = new URLSearchParams();
        query.set('classe', classeNormalizada);

        if (nome !== undefined && nome !== null && String(nome).trim() !== '') {
            query.set('nome', String(nome).trim());
        }
        const nivelToken = this._normalizarFiltroToken(nivel, 'todos');
        if (nivelToken !== 'todos') {
            query.set('nivel', nivelToken);
        }
        const escolaToken = this._normalizarFiltroToken(escola, 'todas');
        if (escolaToken !== 'todas') {
            query.set('escola', String(escola).trim());
        }
        const componenteToken = this._normalizarFiltroToken(componentes, 'todos').toUpperCase();
        if (componenteToken !== 'TODOS') {
            query.set('componentes', componenteToken);
        }

        query.set('skip', String(Math.max(0, Number(skip || 0))));
        query.set('limit', String(Math.max(1, Number(limit || 20))));

        const url = getApiUrl(`/magias/?${query.toString()}`);
        const res = await fetch(url, { headers: this._headers() });

        if (!res.ok) {
            throw new Error(`Falha ao carregar magias paginadas (HTTP ${res.status})`);
        }

        const body = await res.json();
        const rawItems = Array.isArray(body)
            ? body
            : (Array.isArray(body?.items) ? body.items : []);
        const items = this._normalizarNiveisPorClasse(rawItems, classeNormalizada);
        const totalHeader = Number(res.headers.get('X-Total-Count'));
        const skipHeader = Number(res.headers.get('X-Skip'));
        const limitHeader = Number(res.headers.get('X-Limit'));

        return {
            items,
            total: Number.isFinite(totalHeader)
                ? totalHeader
                : (Array.isArray(items) ? items.length : 0),
            skip: Number.isFinite(skipHeader) ? skipHeader : Math.max(0, Number(skip || 0)),
            limit: Number.isFinite(limitHeader) ? limitHeader : Math.max(1, Number(limit || 20)),
        };
    }

    async ListaMagiaPorClassePaginado(classe, filtros = {}) {
        return this.listarPorClassePaginado(classe, filtros);
    }

    async listarMagiaPorClassePaginado(classe, filtros = {}) {
        return this.listarPorClassePaginado(classe, filtros);
    }

    async listarMagiasPorClassePaginado(classe, filtros = {}) {
        return this.listarPorClassePaginado(classe, filtros);
    }

    /**
     * Garante que `nivel` reflita a classe consultada (MagiaClasse), não o nível legado.
     * @private
     */
    _normalizarNiveisPorClasse(magias, classeNormalizada) {
        if (!Array.isArray(magias) || !classeNormalizada) return magias || [];
        const alvo = this._normalizarClasse(classeNormalizada);
        return magias.map((magia) => {
            const classes = Array.isArray(magia?.classes_niveis) ? magia.classes_niveis : [];
            const match = classes.find((cn) => this._normalizarClasse(cn?.classe || '') === alvo);
            if (!match) return magia;
            return { ...magia, nivel: Number(match.nivel ?? magia.nivel) };
        });
    }

    /**
     * Fallback: busca todas as magias e filtra por classe no frontend
     * @private
     * @param {string} classeNormalizada - Já em MAIÚSCULA
     * @returns {Promise<Array>}
     */
    async _listarTodasEFiltrar(classeNormalizada) {
        try {
            // Antes buscávamos /magias/?limit=500 (sem filtro) e cortávamos client-side.
            // Com >500 magias na base de produção, isso podia perder magias de Mago/Clérigo
            // se elas caíssem fora da primeira janela de IDs. Aplicamos o filtro de classe
            // diretamente no backend, garantindo todas as magias da classe.
            const params = new URLSearchParams({ classe: classeNormalizada, limit: '500' });
            const url = getApiUrl(`/magias/?${params.toString()}`);
            const res = await fetch(url, { headers: this._headers() });

            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const raw = await res.json();
            const todasMagias = Array.isArray(raw) ? raw : (Array.isArray(raw?.items) ? raw.items : []);

            // Mesmo com ?classe=, mantemos o filtro client-side defensivo: cobre legado
            // (classes em string única) e qualquer divergência entre normalizações.
            const magiasFiltradas = this._normalizarNiveisPorClasse(todasMagias.filter(m => {
                const alvo = this._normalizarClasse(classeNormalizada);

                if (Array.isArray(m.classes_niveis) && m.classes_niveis.length > 0) {
                    return m.classes_niveis.some(cn =>
                        this._normalizarClasse(cn.classe || '') === alvo
                    );
                }

                if (!m.classe) return false;
                const classesLegacy = String(m.classe)
                    .split(/[,/;|]/)
                    .map(v => this._normalizarClasse(v))
                    .filter(Boolean);
                return classesLegacy.includes(alvo);
            }), classeNormalizada);

            // Não persiste cache vazio: evita travar a UI em "0 magias" se o /magias?limit=500
            // (sem filtro de classe) trouxer apenas magias de outras classes na primeira janela
            // de IDs (com a base atual em produção há 1061 magias e o limite máximo é 500).
            if (magiasFiltradas.length > 0) {
                this._cache.set(classeNormalizada, magiasFiltradas);
            }
            return magiasFiltradas;
        } catch (err) {
            console.error(`❌ Erro ao filtrar magias:`, err);
            throw err;
        }
    }

    /**
     * Busca uma magia específica por ID
     * @param {number} magiaId
     * @returns {Promise<Object|null>}
     */
    async obterPorId(magiaId) {
        try {
            const url = getApiUrl(`/magias/${magiaId}`);
            const res = await fetch(url, { headers: this._headers() });
            
            if (res.status === 404) {
                console.warn(`⚠️ Magia ID ${magiaId} não encontrada`);
                return null;
            }
            
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            
            const magia = await res.json();
            return magia;
        } catch (err) {
            console.error(`❌ Erro ao buscar magia ID ${magiaId}:`, err);
            throw err;
        }
    }

    /**
     * Limpa o cache
     */
    limparCache() {
        this._cache.clear();
    }

    limparCacheClasse(classe) {
        const classeNormalizada = this._normalizarClasse(classe);
        if (classeNormalizada) {
            this._cache.delete(classeNormalizada);
        }
    }
}