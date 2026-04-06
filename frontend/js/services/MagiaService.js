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
        let classNorm = classe.toUpperCase().trim();
        
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
            // Tenta buscar com filtro na API (classe em MAIÚSCULA)
            const url = getApiUrl(`/magias/?classe=${encodeURIComponent(classeNormalizada)}&limit=500`);
            
            const res = await fetch(url, { headers: this._headers() });
            
            if (!res.ok) {
                console.warn(`⚠️ Filtro na API falhou (HTTP ${res.status}), usando fallback...`);
                return await this._listarTodasEFiltrar(classeNormalizada);
            }

            const magias = await res.json();
            
            // Se a API retornar vazio, usa fallback
            if (!magias || magias.length === 0) {
                console.warn(`⚠️ API retornou 0 magias, usando fallback...`);
                return await this._listarTodasEFiltrar(classeNormalizada);
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
            
            const todasMagias = await res.json();
            
            // ✅ FILTRA COMPARANDO EM MAIÚSCULA
            const magiasFiltradas = todasMagias.filter(m => {
                const alvo = classeNormalizada.trim();

                if (Array.isArray(m.classes_niveis) && m.classes_niveis.length > 0) {
                    return m.classes_niveis.some(cn =>
                        String(cn.classe || '').toUpperCase().trim() === alvo
                    );
                }

                if (!m.classe) return false;
                const classesLegacy = String(m.classe)
                    .toUpperCase()
                    .split(/[,/;|]/)
                    .map(v => v.trim())
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