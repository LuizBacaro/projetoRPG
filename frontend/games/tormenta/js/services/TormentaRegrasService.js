/**
 * Regras estáticas da ficha Tormenta (`/api/v1/tormenta/regras/*`).
 */
class TormentaRegrasService {
    _appendRegraVersao(url, regraVersao) {
        if (!regraVersao) return url;
        const rv = String(regraVersao).trim();
        if (!rv) return url;
        const sep = url.includes('?') ? '&' : '?';
        return `${url}${sep}regra_versao=${encodeURIComponent(rv)}`;
    }

    _appendQuery(url, key, value) {
        if (value == null || String(value).trim() === '') return url;
        const sep = url.includes('?') ? '&' : '?';
        return `${url}${sep}${encodeURIComponent(key)}=${encodeURIComponent(String(value).trim())}`;
    }

    _urlAtributos(regraVersao) {
        return this._appendRegraVersao(
            window.getApiUrl('/tormenta/regras/atributos'),
            regraVersao
        );
    }

    _urlRacas(regraVersao, suplemento) {
        let url = this._appendRegraVersao(
            window.getApiUrl('/tormenta/regras/racas'),
            regraVersao
        );
        return this._appendQuery(url, 'suplemento', suplemento);
    }

    _headers() {
        const headers = {};
        const token = AuthService.getToken();
        if (token) headers.Authorization = `Bearer ${token}`;
        return headers;
    }

    async _handleJson(res, fallbackMessage) {
        if (res.status === 401) {
            if (typeof AuthService.logout === 'function') AuthService.logout();
            throw new Error('Sessão expirada. Faça login novamente.');
        }
        if (res.status === 503 || res.status === 502 || res.status === 504) {
            throw new Error(
                'API indisponível ou a acordar (Render). Aguarde alguns segundos e tente de novo.'
            );
        }
        if (!res.ok) {
            const e = await res.json().catch(() => ({}));
            const d = e.detail;
            const msg = typeof d === 'string' && d ? d : fallbackMessage;
            throw new Error(msg);
        }
        return res.json();
    }

    async obterAtributos(opts = {}) {
        const res = await fetch(this._urlAtributos(opts.regraVersao), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar regras Tormenta');
    }

    async gerarAtributos(payload = {}) {
        const body = { ...payload };
        if (payload.regraVersao && body.regra_versao == null) {
            body.regra_versao = payload.regraVersao;
        }
        const res = await fetch(window.getApiUrl('/tormenta/regras/gerar-atributos'), {
            method: 'POST',
            headers: { ...this._headers(), 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        return this._handleJson(res, 'Erro ao gerar atributos T20');
    }

    async obterRacas(opts = {}) {
        const res = await fetch(this._urlRacas(opts.regraVersao, opts.suplemento), {
            headers: this._headers(),
        });
        return this._handleJson(res, 'Erro ao carregar raças Tormenta');
    }

    _urlClasses(regraVersao, suplemento) {
        let url = this._appendRegraVersao(
            window.getApiUrl('/tormenta/regras/classes'),
            regraVersao
        );
        return this._appendQuery(url, 'suplemento', suplemento);
    }

    async obterClasses(opts = {}) {
        const res = await fetch(this._urlClasses(opts.regraVersao, opts.suplemento), {
            headers: this._headers(),
        });
        return this._handleJson(res, 'Erro ao carregar classes Tormenta');
    }

    _urlIdentidadeMb() {
        return window.getApiUrl('/tormenta/regras/identidade-mb');
    }

    /** PM por classe, chave de conjuração e custo em PM por círculo. */
    _urlConjuracaoMb(regraVersao) {
        return this._appendRegraVersao(
            window.getApiUrl('/tormenta/regras/conjuracao-mb'),
            regraVersao
        );
    }

    _urlOrigens(regraVersao, suplemento) {
        let url = this._appendRegraVersao(
            window.getApiUrl('/tormenta/regras/origens'),
            regraVersao || 'v13'
        );
        return this._appendQuery(url, 'suplemento', suplemento);
    }

    /** Tendências (alinhamento) e divindades (Os Vinte) do MB para combos na ficha. */
    async obterIdentidadeMb() {
        const res = await fetch(this._urlIdentidadeMb(), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar tendências/divindades MB');
    }

    /** Origens v1.3 (Tabela 1-19) — benefícios de perícia e poder. */
    async obterOrigens(opts = {}) {
        const res = await fetch(this._urlOrigens(opts.regraVersao, opts.suplemento), {
            headers: this._headers(),
        });
        return this._handleJson(res, 'Erro ao carregar origens v1.3');
    }

    /** Kit inicial v1.3 (p.140) — opções por classe. */
    async obterKitInicial(opts = {}) {
        const q = new URLSearchParams();
        q.set('regra_versao', opts.regraVersao || 'v13');
        if (opts.tormentaClasseMbSlug) q.set('tormenta_classe_mb_slug', String(opts.tormentaClasseMbSlug));
        const res = await fetch(`${window.getApiUrl('/tormenta/regras/kit-inicial')}?${q}`, {
            headers: this._headers(),
        });
        return this._handleJson(res, 'Erro ao carregar kit inicial v1.3');
    }

    async obterConjuracaoMb(opts = {}) {
        const res = await fetch(this._urlConjuracaoMb(opts.regraVersao), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar regras de conjuração');
    }

    _urlEquipamentos() {
        return window.getApiUrl('/tormenta/regras/equipamentos');
    }

    _urlBestiario() {
        return window.getApiUrl('/tormenta/regras/bestiario');
    }

    _urlTalentos() {
        return window.getApiUrl('/tormenta/regras/talentos');
    }

    /**
     * Catálogo stub MB de criaturas (RF-T12g).
     * @param {{ q?: string, skip?: number, limit?: number }} params
     */
    async listarBestiarioCatalogo(params = {}) {
        const q = new URLSearchParams();
        if (params.q) q.set('q', params.q);
        if (params.skip != null) q.set('skip', String(params.skip));
        if (params.limit != null) q.set('limit', String(params.limit));
        const qs = q.toString();
        const res = await fetch(this._urlBestiario() + (qs ? `?${qs}` : ''), {
            headers: this._headers(),
            cache: 'no-store',
        });
        return this._handleJson(res, 'Erro ao carregar bestiário');
    }

    async obterBestiarioDetalhe(slug) {
        const s = encodeURIComponent(String(slug || '').trim());
        const res = await fetch(`${this._urlBestiario()}/${s}`, {
            headers: this._headers(),
            cache: 'no-store',
        });
        return this._handleJson(res, 'Criatura não encontrada no bestiário');
    }

    /**
     * Catálogo MB de equipamento (paginação + busca).
     * @param {{ q?: string, skip?: number, limit?: number }} params
     */
    async listarEquipamentosCatalogo(params = {}) {
        const q = new URLSearchParams();
        if (params.q) q.set('q', params.q);
        if (params.skip != null) q.set('skip', String(params.skip));
        if (params.limit != null) q.set('limit', String(params.limit));
        const qs = q.toString();
        const res = await fetch(this._urlEquipamentos() + (qs ? `?${qs}` : ''), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar equipamentos MB');
    }

    async listarTalentosCatalogo(params = {}) {
        const q = new URLSearchParams();
        if (params.q) q.set('q', params.q);
        if (params.categoria_v13) q.set('categoria_v13', params.categoria_v13);
        if (params.suplemento) q.set('suplemento', String(params.suplemento).trim());
        if (params.raca) q.set('raca', String(params.raca).trim());
        if (params.classe_exigida) q.set('classe_exigida', String(params.classe_exigida).trim());
        if (params.skip != null) q.set('skip', String(params.skip));
        if (params.limit != null) q.set('limit', String(params.limit));
        const qs = q.toString();
        const res = await fetch(this._urlTalentos() + (qs ? `?${qs}` : ''), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar talentos MB');
    }

    /** Alias v1.3 — mesmo endpoint `/tormenta/regras/poderes`. */
    listarPoderesCatalogo(params = {}) {
        return this.listarTalentosCatalogo(params);
    }

    _urlMagias() {
        return window.getApiUrl('/tormenta/regras/magias');
    }

    /**
     * Catálogo MB de magias — metadados (grimório / listagens).
     * @param {{ q?: string, circulo?: number, tipo?: 'arcana'|'divina', escola?: string, skip?: number, limit?: number, catalogo_por_classe_mb?: boolean, classe_mb_slug?: string, nivel_mb?: number, conjuracao_manual_mb?: boolean }} params
     */
    async listarMagiasCatalogo(params = {}) {
        const sp = new URLSearchParams();
        if (params.q) sp.set('q', params.q);
        if (params.circulo != null && params.circulo !== '') sp.set('circulo', String(params.circulo));
        if (params.tipo) sp.set('tipo', params.tipo);
        if (params.escola) sp.set('escola', params.escola);
        if (params.skip != null) sp.set('skip', String(params.skip));
        if (params.limit != null) sp.set('limit', String(params.limit));
        if (params.catalogo_por_classe_mb) sp.set('catalogo_por_classe_mb', 'true');
        if (params.classe_mb_slug) sp.set('classe_mb_slug', String(params.classe_mb_slug).trim());
        if (params.nivel_mb != null && params.nivel_mb !== '') sp.set('nivel_mb', String(params.nivel_mb));
        if (params.conjuracao_manual_mb) sp.set('conjuracao_manual_mb', 'true');
        const qs = sp.toString();
        const res = await fetch(this._urlMagias() + (qs ? `?${qs}` : ''), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar magias MB');
    }

    _urlConjuracaoPreview() {
        return window.getApiUrl('/tormenta/regras/conjuracao-preview');
    }

    /**
     * CD base (10+mod), modificador da chave e PM máx. de conjuração MB.
     * @param {{ classe_slug: string, nivel?: number, nivel_conjurador?: number|null, for_valor?: number, des_valor?: number, con_valor?: number, int_valor?: number, sab_valor?: number, car_valor?: number }} p
     */
    async obterConjuracaoPreview(p) {
        const sp = new URLSearchParams();
        sp.set('classe_slug', String(p.classe_slug || '').trim());
        sp.set('nivel', String(p.nivel != null ? p.nivel : 1));
        if (p.nivel_conjurador != null && p.nivel_conjurador !== '') {
            sp.set('nivel_conjurador', String(p.nivel_conjurador));
        }
        if (p.regraVersao) sp.set('regra_versao', String(p.regraVersao).trim());
        if (p.arcanista_caminho) sp.set('arcanista_caminho', String(p.arcanista_caminho).trim());
        if (p.raca_tormenta_slug) {
            sp.set('raca_tormenta_slug', String(p.raca_tormenta_slug).trim());
        }
        ['for', 'des', 'con', 'int', 'sab', 'car'].forEach((k) => {
            const key = `${k}_valor`;
            if (p[key] != null) sp.set(key, String(p[key]));
        });
        const qs = sp.toString();
        const res = await fetch(`${this._urlConjuracaoPreview()}?${qs}`, { headers: this._headers() });
        return this._handleJson(res, 'Erro ao calcular pré-visualização de conjuração');
    }

    _urlArmadurasProtecao() {
        return window.getApiUrl('/tormenta/regras/armaduras-protecao');
    }

    /**
     * Catálogo de armaduras / proteção (paginação + busca).
     * @param {{ q?: string, skip?: number, limit?: number }} params
     */
    async listarArmadurasProtecaoCatalogo(params = {}) {
        const sp = new URLSearchParams();
        if (params.q) sp.set('q', params.q);
        if (params.skip != null) sp.set('skip', String(params.skip));
        if (params.limit != null) sp.set('limit', String(params.limit));
        const qs = sp.toString();
        const res = await fetch(this._urlArmadurasProtecao() + (qs ? `?${qs}` : ''), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar catálogo de armaduras');
    }

    _urlTracosRaciaisPreview() {
        return window.getApiUrl('/tormenta/regras/tracos-raciais-preview');
    }

    async obterTracosRaciaisPreview(slug, opts = {}) {
        const sp = new URLSearchParams();
        sp.set('slug', String(slug || '').trim());
        if (opts.regraVersao) sp.set('regra_versao', String(opts.regraVersao).trim());
        if (opts.humanoVersatil) sp.set('humano_versatil', String(opts.humanoVersatil).trim());
        if (opts.lefouDeformidadeModo) {
            sp.set('lefou_deformidade_modo', String(opts.lefouDeformidadeModo).trim());
        }
        if (opts.lefouDeformidadePericias) {
            sp.set('lefou_deformidade_pericias', String(opts.lefouDeformidadePericias).trim());
        }
        if (opts.qareenAscendencia) {
            sp.set('qareen_ascendencia', String(opts.qareenAscendencia).trim());
        }
        if (opts.osteonMemoriaModo) {
            sp.set('osteon_memoria_modo', String(opts.osteonMemoriaModo).trim());
        }
        if (opts.osteonMemoriaPericia) {
            sp.set('osteon_memoria_pericia', String(opts.osteonMemoriaPericia).trim());
        }
        if (opts.sereiaMagias) {
            sp.set('sereia_magias', String(opts.sereiaMagias).trim());
        }
        if (opts.golemFonteElemental) {
            sp.set('golem_fonte_elemental', String(opts.golemFonteElemental).trim());
        }
        if (opts.klirenPericia) {
            sp.set('kliren_pericia', String(opts.klirenPericia).trim());
        }
        if (opts.klirenOficio) {
            sp.set('kliren_oficio', String(opts.klirenOficio).trim());
        }
        if (opts.silfideMagias) {
            sp.set('silfide_magias', String(opts.silfideMagias).trim());
        }
        if (opts.duendeTamanho) {
            sp.set('duende_tamanho', String(opts.duendeTamanho).trim());
        }
        if (opts.duendePresentes) {
            sp.set('duende_presentes', String(opts.duendePresentes).trim());
        }
        if (opts.duendeNatureza) {
            sp.set('duende_natureza', String(opts.duendeNatureza).trim());
        }
        if (opts.duendeTabuPenalidade) {
            sp.set('duende_tabu_penalidade', String(opts.duendeTabuPenalidade).trim());
        }
        if (opts.duendeTabuTexto) {
            sp.set('duende_tabu_texto', String(opts.duendeTabuTexto).trim());
        }
        const res = await fetch(`${this._urlTracosRaciaisPreview()}?${sp}`, { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar traços raciais');
    }

    _urlEscolhasRaciais() {
        return window.getApiUrl('/tormenta/regras/escolhas-raciais');
    }

    async obterEscolhasRaciais(slug, opts = {}) {
        const sp = new URLSearchParams();
        sp.set('slug', String(slug || '').trim());
        if (opts.regraVersao) sp.set('regra_versao', String(opts.regraVersao).trim());
        const res = await fetch(`${this._urlEscolhasRaciais()}?${sp}`, { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar escolhas raciais');
    }

    _urlPericiasRegras(regraVersao) {
        return this._appendRegraVersao(
            window.getApiUrl('/tormenta/regras/pericias'),
            regraVersao
        );
    }

    async obterRegrasPericias(opts = {}) {
        const res = await fetch(this._urlPericiasRegras(opts.regraVersao), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar regras de perícias');
    }

    async obterPericiasClassePreview(classeSlug) {
        const sp = new URLSearchParams();
        sp.set('classe_slug', String(classeSlug || '').trim());
        const res = await fetch(
            `${window.getApiUrl('/tormenta/regras/pericias-classe-preview')}?${sp}`,
            { headers: this._headers() }
        );
        return this._handleJson(res, 'Erro ao carregar perícias de classe');
    }

    async calcularBonusPericia(body) {
        const payload = this._normalizarBonusPayload(body);
        const cacheKey = this._bonusCacheKey(payload);
        if (this._bonusCache && this._bonusCache.has(cacheKey)) {
            return this._bonusCache.get(cacheKey);
        }
        if (this._bonusInflight && this._bonusInflight.has(cacheKey)) {
            return this._bonusInflight.get(cacheKey);
        }
        const promise = (async () => {
            const res = await fetch(window.getApiUrl('/tormenta/regras/pericias/calcular-bonus'), {
                method: 'POST',
                headers: { ...this._headers(), 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await this._handleJson(res, 'Erro ao calcular bônus de perícia');
            this._guardarBonusCache(cacheKey, data);
            return data;
        })();
        if (!this._bonusInflight) this._bonusInflight = new Map();
        this._bonusInflight.set(cacheKey, promise);
        try {
            return await promise;
        } finally {
            this._bonusInflight.delete(cacheKey);
        }
    }

    async calcularBonusPericiaLote(itens) {
        const lista = Array.isArray(itens) ? itens : [];
        if (!lista.length) return [];
        if (lista.length === 1) {
            const um = await this.calcularBonusPericia(lista[0]);
            return [um];
        }
        const payloads = lista.map((item) => this._normalizarBonusPayload(item));
        const res = await fetch(
            window.getApiUrl('/tormenta/regras/pericias/calcular-bonus-lote'),
            {
                method: 'POST',
                headers: { ...this._headers(), 'Content-Type': 'application/json' },
                body: JSON.stringify({ itens: payloads }),
            }
        );
        const data = await this._handleJson(res, 'Erro ao calcular bônus de perícias');
        const rows = Array.isArray(data.itens) ? data.itens : [];
        payloads.forEach((payload, idx) => {
            if (rows[idx]) this._guardarBonusCache(this._bonusCacheKey(payload), rows[idx]);
        });
        return rows;
    }

    _normalizarBonusPayload(body) {
        const payload = { ...body };
        if (body.regraVersao && payload.regra_versao == null) {
            payload.regra_versao = body.regraVersao;
        }
        return payload;
    }

    _bonusCacheKey(payload) {
        return JSON.stringify(payload);
    }

    _guardarBonusCache(key, data) {
        if (!this._bonusCache) this._bonusCache = new Map();
        if (this._bonusCache.size > 240) {
            const first = this._bonusCache.keys().next().value;
            if (first != null) this._bonusCache.delete(first);
        }
        this._bonusCache.set(key, data);
    }

    limparCacheBonusPericia() {
        if (this._bonusCache) this._bonusCache.clear();
    }

    async rolarPericia(body) {
        const res = await fetch(window.getApiUrl('/tormenta/regras/pericias/rolar'), {
            method: 'POST',
            headers: { ...this._headers(), 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        return this._handleJson(res, 'Erro ao rolar perícia');
    }

    async condicoesModificadores(body) {
        const res = await fetch(window.getApiUrl('/tormenta/regras/condicoes/modificadores'), {
            method: 'POST',
            headers: { ...this._headers(), 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        return this._handleJson(res, 'Erro ao calcular modificadores de condições');
    }

    async rolarAtaque(body) {
        const res = await fetch(window.getApiUrl('/tormenta/regras/ataque/rolar'), {
            method: 'POST',
            headers: { ...this._headers(), 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        return this._handleJson(res, 'Erro ao rolar ataque');
    }

    async rolarIniciativa(body) {
        const res = await fetch(window.getApiUrl('/tormenta/regras/iniciativa/rolar'), {
            method: 'POST',
            headers: { ...this._headers(), 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        return this._handleJson(res, 'Erro ao rolar iniciativa');
    }

    async ajustarBonusAtaque(body) {
        const res = await fetch(window.getApiUrl('/tormenta/regras/ataque/ajustar-bonus'), {
            method: 'POST',
            headers: { ...this._headers(), 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        return this._handleJson(res, 'Erro ao ajustar bônus de ataque');
    }

    async previewCarga(body) {
        const res = await fetch(window.getApiUrl('/tormenta/regras/carga-preview'), {
            method: 'POST',
            headers: { ...this._headers(), 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        return this._handleJson(res, 'Erro ao calcular carga');
    }

    /**
     * PV máximos por classe, nível e CON.
     * @param {{ classe_slug: string, nivel?: number, con_valor?: number, regraVersao?: string }} p
     */
    async obterPvPreview(p) {
        const sp = new URLSearchParams();
        sp.set('classe_slug', String(p.classe_slug || '').trim());
        sp.set('nivel', String(p.nivel != null ? p.nivel : 1));
        sp.set('con_valor', String(p.con_valor != null ? p.con_valor : 10));
        if (p.regraVersao) sp.set('regra_versao', String(p.regraVersao).trim());
        if (p.arcanista_caminho) sp.set('arcanista_caminho', String(p.arcanista_caminho).trim());
        if (p.slug_raca) sp.set('slug_raca', String(p.slug_raca).trim());
        ['for', 'des', 'int', 'sab', 'car'].forEach((k) => {
            const key = `${k}_valor`;
            if (p[key] != null) sp.set(key, String(p[key]));
        });
        const res = await fetch(
            `${window.getApiUrl('/tormenta/regras/pv-preview')}?${sp}`,
            { headers: this._headers() }
        );
        return this._handleJson(res, 'Erro ao calcular PV');
    }

    /**
     * PV máximos v1.3 — multiclasse (classe primária + demais, p.34).
     * @param {{ classes: Array<{slug: string, nivel: number}>, slug_primario: string, con_valor?: number, slug_raca?: string, regraVersao?: string }} p
     */
    async obterPvPreviewMulticlasse(p) {
        const res = await fetch(window.getApiUrl('/tormenta/regras/pv-preview-multiclasse'), {
            method: 'POST',
            headers: { ...this._headers(), 'Content-Type': 'application/json' },
            body: JSON.stringify({
                classes: Array.isArray(p.classes) ? p.classes : [],
                slug_primario: String(p.slug_primario || '').trim(),
                con_valor: p.con_valor != null ? Number(p.con_valor) : 0,
                slug_raca: p.slug_raca ? String(p.slug_raca).trim() : undefined,
                regra_versao: p.regraVersao || 'v13',
            }),
        });
        return this._handleJson(res, 'Erro ao calcular PV multiclasse');
    }

    /**
     * PM máximos v1.3 — soma multiclasse (nível × pm/nível por classe).
     * @param {{ classes: Array<{slug: string, nivel: number}>, regraVersao?: string }} p
     */
    async obterPmPreviewMulticlasse(p) {
        const res = await fetch(window.getApiUrl('/tormenta/regras/pm-preview-multiclasse'), {
            method: 'POST',
            headers: { ...this._headers(), 'Content-Type': 'application/json' },
            body: JSON.stringify({
                classes: Array.isArray(p.classes) ? p.classes : [],
                regra_versao: p.regraVersao || 'v13',
            }),
        });
        return this._handleJson(res, 'Erro ao calcular PM multiclasse');
    }

    /**
     * Dinheiro inicial v1.3 — Tabela 3-1 por nível.
     * @param {{ nivel?: number, regraVersao?: string }} p
     */
    async obterDinheiroInicial(p) {
        const sp = new URLSearchParams();
        sp.set('nivel', String(p.nivel != null ? p.nivel : 1));
        if (p.regraVersao) sp.set('regra_versao', String(p.regraVersao).trim());
        const res = await fetch(
            `${window.getApiUrl('/tormenta/regras/dinheiro-inicial')}?${sp}`,
            { headers: this._headers() }
        );
        return this._handleJson(res, 'Erro ao carregar dinheiro inicial');
    }

    async obterTruquesMelhorAmigo(opts = {}) {
        const sp = new URLSearchParams();
        sp.set('nivel_treinador', String(opts.nivelTreinador != null ? opts.nivelTreinador : 1));
        const res = await fetch(
            `${window.getApiUrl('/tormenta/regras/truques-melhor-amigo')}?${sp}`,
            { headers: this._headers() }
        );
        return this._handleJson(res, 'Erro ao carregar truques do Melhor Amigo');
    }

    async obterTiposMelhorAmigo() {
        const res = await fetch(window.getApiUrl('/tormenta/regras/tipos-melhor-amigo'), {
            headers: this._headers(),
        });
        return this._handleJson(res, 'Erro ao carregar tipos do Melhor Amigo');
    }

    async obterPresentesDuende() {
        const res = await fetch(window.getApiUrl('/tormenta/regras/presentes-duende'), {
            headers: this._headers(),
        });
        return this._handleJson(res, 'Erro ao carregar presentes do Duende');
    }

    async obterDuendeOpcoes() {
        const res = await fetch(window.getApiUrl('/tormenta/regras/duende-opcoes'), {
            headers: this._headers(),
        });
        return this._handleJson(res, 'Erro ao carregar opções do Duende');
    }

    async obterDuendeAleatorio() {
        const res = await fetch(window.getApiUrl('/tormenta/regras/duende-aleatorio'), {
            headers: this._headers(),
        });
        return this._handleJson(res, 'Erro ao rolar Duende aleatório');
    }

    async calcularDuende(payload) {
        const res = await fetch(window.getApiUrl('/tormenta/regras/duende-calcular'), {
            method: 'POST',
            headers: this._headers({ 'Content-Type': 'application/json' }),
            body: JSON.stringify(payload || {}),
        });
        return this._handleJson(res, 'Erro ao calcular Duende');
    }

    /**
     * Valida orçamento de perícias treinadas e graduações (MB).
     */
    async validarPericiasCriacao(body) {
        const payload = { ...body };
        if (body.regraVersao && payload.regra_versao == null) {
            payload.regra_versao = body.regraVersao;
        }
        if (body.humanoVersatil && payload.humano_versatil == null) {
            payload.humano_versatil = body.humanoVersatil;
        }
        if (body.origemSlug && payload.origem_slug == null) {
            payload.origem_slug = body.origemSlug;
        }
        if (body.origemBeneficios && payload.origem_beneficios == null) {
            payload.origem_beneficios = body.origemBeneficios;
        }
        if (body.origemTrocasPericia && payload.origem_trocas_pericia == null) {
            payload.origem_trocas_pericia = body.origemTrocasPericia;
        }
        const res = await fetch(window.getApiUrl('/tormenta/regras/pericias/validar-criacao'), {
            method: 'POST',
            headers: { ...this._headers(), 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        return this._handleJson(res, 'Erro ao validar orçamento de perícias');
    }

    /** RF-T08g — valida pré-requisitos de poder v1.3 antes de vincular na ficha. */
    async validarPreRequisitosPoder(body) {
        const payload = { ...body };
        if (body.regraVersao && payload.regra_versao == null) {
            payload.regra_versao = body.regraVersao;
        }
        if (body.nomePoder && payload.nome_poder == null) {
            payload.nome_poder = body.nomePoder;
        }
        if (body.poderesEscolhidos && payload.poderes_escolhidos == null) {
            payload.poderes_escolhidos = body.poderesEscolhidos;
        }
        const res = await fetch(
            window.getApiUrl('/tormenta/regras/poderes/validar-pre-requisitos'),
            {
                method: 'POST',
                headers: { ...this._headers(), 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            }
        );
        return this._handleJson(res, 'Erro ao validar pré-requisitos do poder');
    }
}

window.TormentaRegrasService = TormentaRegrasService;
