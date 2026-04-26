/**
 * MagiaService.js
 * SRP: Comunicação HTTP exclusivamente com /magias
 * SOLID: DIP — injetável via constructor
 * ✅ FIX: Busca por classe em MAIÚSCULA + fallback com filtro correto
 */

import { getApiUrl } from '../config/api.config.js';

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
        const valorBase = String(classe || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '');
        let classNorm = valorBase.toUpperCase().trim();
        
        // Mapear Feiticeiro para Mago (mesmas magias)
        if (classNorm === 'FEITICEIRO') {
            classNorm = 'MAGO';
        }
        
        return classNorm;
    }

    /**
     * Busca magias filtradas por classe
     * @param {string} classe - Ex: 'Mago', 'Clérigo' (será convertido para MAIÚSCULA)
     * @returns {Promise<Array>}
     */
    async listarPorClasse(classe) {
        // ✅ NORMALIZA PARA MAIÚSCULA
        const classeNormalizada = this._normalizarClasse(classe);

        if (this._cache.has(classeNormalizada)) {
            return this._cache.get(classeNormalizada);
        }

        try {
            const pagina = await this.listarPorClassePaginado(classeNormalizada, { skip: 0, limit: 500 });

            if (!pagina || !Array.isArray(pagina.items)) {
                console.warn('⚠️ Filtro na API paginada falhou, usando fallback...');
                return await this._listarTodasEFiltrar(classeNormalizada);
            }

            const magias = pagina.items;

            // Catálogo vazio na API (sem dados importados) ou filtro sem match → tenta fallback
            if (!magias || magias.length === 0) {
                const fallback = await this._listarTodasEFiltrar(classeNormalizada);
                if (!fallback.length) {
                    console.info(
                        '[MagiaService] Catálogo vazio ou sem magias para a classe; ' +
                        'importe magias (admin) ou verifique a classe do personagem.'
                    );
                }
                return fallback;
            }

            this._cache.set(classeNormalizada, magias);
            return magias;
        } catch (err) {
            console.error(`❌ Erro ao buscar magias de ${classeNormalizada}:`, err);
            try {
                return await this._listarTodasEFiltrar(classeNormalizada);
            } catch (fallbackErr) {
                console.error(`❌ Fallback também falhou:`, fallbackErr);
                throw fallbackErr;
            }
        }
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
        if (nivel !== undefined && nivel !== null && String(nivel).trim() !== '' && String(nivel) !== 'todos') {
            query.set('nivel', String(nivel));
        }
        if (escola !== undefined && escola !== null && String(escola).trim() !== '' && String(escola) !== 'todas') {
            query.set('escola', String(escola).trim());
        }
        if (componentes !== undefined && componentes !== null && String(componentes).trim() !== '' && String(componentes) !== 'todos') {
            query.set('componentes', String(componentes).trim());
        }

        query.set('skip', String(Math.max(0, Number(skip || 0))));
        query.set('limit', String(Math.max(1, Number(limit || 20))));

        const url = getApiUrl(`/magias/?${query.toString()}`);
        const res = await fetch(url, { headers: this._headers() });

        if (!res.ok) {
            throw new Error(`Falha ao carregar magias paginadas (HTTP ${res.status})`);
        }

        const body = await res.json();
        const items = Array.isArray(body)
            ? body
            : (Array.isArray(body?.items) ? body.items : []);
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
     * Fallback: busca todas as magias e filtra por classe no frontend
     * @private
     * @param {string} classeNormalizada - Já em MAIÚSCULA
     * @returns {Promise<Array>}
     */
    async _listarTodasEFiltrar(classeNormalizada) {
        try {
            const url = getApiUrl('/magias/?limit=500');
            const res = await fetch(url, { headers: this._headers() });
            
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            
            const raw = await res.json();
            const todasMagias = Array.isArray(raw) ? raw : (Array.isArray(raw?.items) ? raw.items : []);

            // ✅ FILTRA COMPARANDO EM MAIÚSCULA
            const magiasFiltradas = todasMagias.filter(m => {
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
            });
            
            this._cache.set(classeNormalizada, magiasFiltradas);
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
}