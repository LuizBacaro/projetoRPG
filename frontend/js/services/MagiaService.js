/**
 * MagiaService.js
 * SRP: Comunicação HTTP exclusivamente com /magias
 * SOLID: DIP — injetável via constructor
 * ✅ FIX: Normaliza classe para uppercase para evitar mismatch
 */

import { getApiUrl } from '../config/api.config.js';

export class MagiaService {
    constructor(token) {
        this.token = token || localStorage.getItem('token');
        this._cache = new Map(); // Cache por classe normalizada
        console.log('✅ MagiaService inicializado');
    }

    /**
     * Headers padrão para requisições
     * @private
     * @returns {Object}
     */
    _headers() {
        const h = { 'Content-Type': 'application/json' };
        if (this.token) h['Authorization'] = `Bearer ${this.token}`;
        return h;
    }

    /**
     * Normaliza classe para MAIÚSCULA para evitar mismatch com banco
     * @private
     * @param {string} classe
     * @returns {string}
     */
    _normalizarClasse(classe) {
        return classe.toUpperCase();
    }

    /**
     * Busca magias filtradas por classe
     * Suporta fallback: se a API não filtrar, busca todas e filtra no frontend
     * @param {string} classe - Ex: 'Mago', 'Clérigo', 'MAGO'
     * @returns {Promise<Array>}
     */
    async listarPorClasse(classe) {
        const classeNormalizada = this._normalizarClasse(classe);

        // Verifica cache
        if (this._cache.has(classeNormalizada)) {
            console.log(`🔄 Magias de ${classeNormalizada} recuperadas do cache`);
            return this._cache.get(classeNormalizada);
        }

        try {
            // Tenta com filtro na API
            const url = getApiUrl(`/magias/?classe=${encodeURIComponent(classeNormalizada)}&limit=500`);
            console.log(`📡 Buscando magias de ${classeNormalizada}...`);
            
            const res = await fetch(url, { headers: this._headers() });
            
            if (!res.ok) {
                // Se falhar, tenta fallback: busca todas e filtra no frontend
                console.warn(`⚠️ Filtro por classe falhou (HTTP ${res.status}), usando fallback...`);
                return await this._listarTodasEFiltrar(classeNormalizada);
            }

            const magias = await res.json();
            
            // Se retornar vazio, tenta fallback
            if (!magias || magias.length === 0) {
                console.warn(`⚠️ API retornou 0 magias, usando fallback...`);
                return await this._listarTodasEFiltrar(classeNormalizada);
            }

            this._cache.set(classeNormalizada, magias);
            console.log(`✅ ${magias.length} magias de ${classeNormalizada} carregadas`);
            return magias;
        } catch (err) {
            console.error(`❌ Erro ao buscar magias de ${classeNormalizada}:`, err);
            // Fallback: tenta buscar todas
            try {
                return await this._listarTodasEFiltrar(classeNormalizada);
            } catch (fallbackErr) {
                console.error(`❌ Fallback também falhou:`, fallbackErr);
                throw fallbackErr;
            }
        }
    }

    /**
     * Fallback: busca todas as magias e filtra por classe no frontend
     * @private
     * @param {string} classeNormalizada - Já em MAIÚSCULA
     * @returns {Promise<Array>}
     */
    async _listarTodasEFiltrar(classeNormalizada) {
        try {
            const url = getApiUrl('/magias/');
            console.log(`📡 Buscando TODAS as magias para fallback...`);
            const res = await fetch(url, { headers: this._headers() });
            
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            
            const todasMagias = await res.json();
            console.log(`📖 Total de magias no banco: ${todasMagias.length}`);
            
            // Filtra por classe normalizada
            const magiasFiltradas = todasMagias.filter(m => {
                if (!m.classe) return false;
                return m.classe.toUpperCase() === classeNormalizada;
            });
            
            this._cache.set(classeNormalizada, magiasFiltradas);
            console.log(`✅ ${magiasFiltradas.length} magias de ${classeNormalizada} filtradas no frontend`);
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
            console.log(`✅ Magia ID ${magiaId} carregada`);
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
        console.log('🗑️ Cache de MagiaService limpo');
    }
}