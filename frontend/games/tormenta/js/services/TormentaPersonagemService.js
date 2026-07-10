/**
 * Cliente API — personagens Tormenta (`/api/v1/tormenta/personagens`).
 */
class TormentaPersonagemService {
    static humanizarErroApi(status, detail, fallbackMessage) {
        const raw = typeof detail === 'string' ? detail.trim() : '';
        const d = raw.toLowerCase();
        if (status === 409) {
            if (d.includes('equipamento') && d.includes('invent')) {
                return {
                    code: 'DUPLICATE_EQUIP',
                    message:
                        'Este equipamento já está no inventário. A quantidade será somada se você adicionar de novo.',
                };
            }
            if (d.includes('talento') && d.includes('vincul')) {
                return {
                    code: 'DUPLICATE_TALENTO',
                    message: 'Este poder/talento já está na ficha.',
                };
            }
            if (d.includes('consum') && d.includes('invent')) {
                return {
                    code: 'DUPLICATE_CONSUMIVEL',
                    message: 'Este consumível já está na ficha.',
                };
            }
            if (d.includes('magia') && d.includes('vincul')) {
                return {
                    code: 'DUPLICATE_MAGIA',
                    message: 'Esta magia já está na ficha com o mesmo papel (grimório/preparada/conhecida).',
                };
            }
            return {
                code: 'CONFLICT',
                message: raw || 'Este item já existe na ficha.',
            };
        }
        return { code: 'API_ERROR', message: raw || fallbackMessage };
    }

    static isErroDuplicado(err) {
        if (!err) return false;
        if (err.status === 409) return true;
        const code = String(err.code || '');
        return code.startsWith('DUPLICATE_') || code === 'CONFLICT';
    }

    _url(path = '') {
        return window.getApiUrl('/tormenta/personagens' + path);
    }

    _headers(json = true) {
        const headers = {};
        if (json) headers['Content-Type'] = 'application/json';
        const token = AuthService.getToken();
        if (token) headers.Authorization = `Bearer ${token}`;
        return headers;
    }

    async _handleResponse(res, fallbackMessage) {
        if (res.status === 401) {
            if (typeof AuthService.logout === 'function') AuthService.logout();
            throw new Error('Sessão expirada. Faça login novamente.');
        }
        if (!res.ok) {
            const e = await res.json().catch(() => ({}));
            let d = e.detail;
            if (Array.isArray(d)) {
                d = d
                    .map((x) => {
                        if (typeof x === 'string') return x;
                        const loc = Array.isArray(x.loc) ? x.loc.filter((p) => p !== 'body').join('.') : '';
                        const msg = x.msg || JSON.stringify(x);
                        return loc ? `${loc}: ${msg}` : msg;
                    })
                    .join('; ');
            } else if (d && typeof d === 'object') {
                d = JSON.stringify(d);
            }
            const detail = typeof d === 'string' ? d : '';
            const { code, message } = TormentaPersonagemService.humanizarErroApi(
                res.status,
                detail,
                fallbackMessage
            );
            const err = new Error(message);
            err.status = res.status;
            err.code = code;
            err.apiDetail = detail;
            throw err;
        }
        if (res.status === 204) return null;
        return res.json();
    }

    async listar(params = {}) {
        const q = new URLSearchParams();
        if (params.tipo) q.set('tipo', params.tipo);
        if (params.meus) q.set('meus', 'true');
        if (params.campanha_id != null) q.set('campanha_id', String(params.campanha_id));
        if (params.skip != null) q.set('skip', String(params.skip));
        if (params.limit != null) q.set('limit', String(params.limit));
        const qs = q.toString();
        const res = await fetch(this._url(qs ? `?${qs}` : ''), {
            headers: this._headers(false),
            cache: 'no-store',
        });
        return this._handleResponse(res, 'Erro ao listar personagens');
    }

    async obter(id) {
        const res = await fetch(this._url(`/${id}`), { headers: this._headers(false) });
        return this._handleResponse(res, 'Erro ao carregar personagem');
    }

    async criar(payload) {
        const res = await fetch(this._url(''), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(payload),
        });
        return this._handleResponse(res, 'Erro ao criar personagem');
    }

    async atualizar(id, payload) {
        const res = await fetch(this._url(`/${id}`), {
            method: 'PATCH',
            headers: this._headers(true),
            body: JSON.stringify(payload),
        });
        return this._handleResponse(res, 'Erro ao salvar personagem');
    }

    async excluir(id) {
        const res = await fetch(this._url(`/${id}`), {
            method: 'DELETE',
            headers: this._headers(false),
        });
        return this._handleResponse(res, 'Erro ao excluir personagem');
    }

    /**
     * Envia retrato (multipart). Atualiza `foto_url` no servidor.
     * @param {number|string} id
     * @param {File} file
     */
    async enviarFoto(id, file) {
        const fd = new FormData();
        fd.append('foto', file);
        const headers = {};
        const token = AuthService.getToken();
        if (token) headers.Authorization = `Bearer ${token}`;
        const res = await fetch(this._url(`/${id}/foto`), {
            method: 'POST',
            headers,
            body: fd,
        });
        return this._handleResponse(res, 'Erro ao enviar retrato');
    }

    async importarInventarioLegado(id) {
        const res = await fetch(this._url(`/${id}/inventario/importar-legado`), {
            method: 'POST',
            headers: this._headers(true),
            body: '{}',
        });
        return this._handleResponse(res, 'Erro ao importar inventário legado');
    }

    async adicionarTalento(id, body) {
        const res = await fetch(this._url(`/${id}/talentos`), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(body),
        });
        return this._handleResponse(res, 'Erro ao adicionar talento');
    }

    async removerTalento(id, vinculoId) {
        const res = await fetch(this._url(`/${id}/talentos/${vinculoId}`), {
            method: 'DELETE',
            headers: this._headers(false),
        });
        return this._handleResponse(res, 'Erro ao remover talento');
    }

    async ativarPoder(id, body) {
        const res = await fetch(this._url(`/${id}/poderes/ativar`), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(body),
        });
        return this._handleResponse(res, 'Erro ao ativar poder');
    }

    async adicionarEquipamento(id, body) {
        const res = await fetch(this._url(`/${id}/equipamentos`), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(body),
        });
        return this._handleResponse(res, 'Erro ao adicionar equipamento');
    }

    async atualizarEquipamentoQuantidade(id, vinculoId, quantidade) {
        const res = await fetch(this._url(`/${id}/equipamentos/${vinculoId}`), {
            method: 'PATCH',
            headers: this._headers(true),
            body: JSON.stringify({ quantidade }),
        });
        return this._handleResponse(res, 'Erro ao atualizar quantidade do equipamento');
    }

    async removerEquipamento(id, vinculoId) {
        const res = await fetch(this._url(`/${id}/equipamentos/${vinculoId}`), {
            method: 'DELETE',
            headers: this._headers(false),
        });
        return this._handleResponse(res, 'Erro ao remover equipamento');
    }

    async listarConsumiveis(id) {
        const res = await fetch(this._url(`/${id}/consumiveis`), { headers: this._headers(false) });
        return this._handleResponse(res, 'Erro ao listar consumíveis');
    }

    async adicionarConsumivel(id, body) {
        const res = await fetch(this._url(`/${id}/consumiveis`), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(body),
        });
        return this._handleResponse(res, 'Erro ao adicionar consumível');
    }

    async atualizarConsumivelQuantidade(id, vinculoId, quantidade) {
        const res = await fetch(this._url(`/${id}/consumiveis/${vinculoId}`), {
            method: 'PATCH',
            headers: this._headers(true),
            body: JSON.stringify({ quantidade }),
        });
        return this._handleResponse(res, 'Erro ao atualizar quantidade do consumível');
    }

    async removerConsumivel(id, vinculoId) {
        const res = await fetch(this._url(`/${id}/consumiveis/${vinculoId}`), {
            method: 'DELETE',
            headers: this._headers(false),
        });
        return this._handleResponse(res, 'Erro ao remover consumível');
    }

    async listarMagias(id) {
        const res = await fetch(this._url(`/${id}/magias`), { headers: this._headers(false) });
        return this._handleResponse(res, 'Erro ao listar magias do personagem');
    }

    async adicionarMagia(id, body) {
        const res = await fetch(this._url(`/${id}/magias`), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(body),
        });
        return this._handleResponse(res, 'Erro ao adicionar magia');
    }

    async removerMagia(id, vinculoId) {
        const res = await fetch(this._url(`/${id}/magias/${vinculoId}`), {
            method: 'DELETE',
            headers: this._headers(false),
        });
        return this._handleResponse(res, 'Erro ao remover magia');
    }

    /** Lança magia MB debitando PM (`pa_atual`). */
    async lancarMagia(id, magiaSlug) {
        const res = await fetch(this._url(`/${id}/magias/lancar`), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify({ magia_slug: magiaSlug }),
        });
        return this._handleResponse(res, 'Erro ao lançar magia');
    }

    async previewMagiasConhecidas(id) {
        const res = await fetch(this._url(`/${id}/magias/conhecidas-preview`), {
            headers: this._headers(false),
        });
        return this._handleResponse(res, 'Erro ao carregar limite de magias conhecidas');
    }

    async previewGrimorio(id) {
        const res = await fetch(this._url(`/${id}/magias/grimorio-preview`), {
            headers: this._headers(false),
        });
        return this._handleResponse(res, 'Erro ao carregar limite do livro (grimório)');
    }

    async previewRepertorio(id) {
        const res = await fetch(this._url(`/${id}/magias/repertorio-preview`), {
            headers: this._headers(false),
        });
        return this._handleResponse(res, 'Erro ao carregar limite do repertório aprendido');
    }

    async previewPreparadas(id) {
        const res = await fetch(this._url(`/${id}/magias/preparadas-preview`), {
            headers: this._headers(false),
        });
        return this._handleResponse(res, 'Erro ao carregar limite de magias preparadas');
    }

    async limparPreparadas(id) {
        const res = await fetch(this._url(`/${id}/magias/limpar-preparadas`), {
            method: 'POST',
            headers: this._headers(true),
            body: '{}',
        });
        return this._handleResponse(res, 'Erro ao limpar magias preparadas');
    }

    async previewSubirNivel(id, nivelAlvo, opts = {}) {
        const qs = new URLSearchParams({ nivel_alvo: String(nivelAlvo) });
        const slug = opts && opts.classeSlug;
        if (slug) qs.set('classe_slug', String(slug));
        const res = await fetch(this._url(`/${id}/subir-nivel-preview?${qs}`), {
            headers: this._headers(false),
        });
        return this._handleResponse(res, 'Erro ao carregar preview de subir de nível');
    }

    async aplicarSubirNivel(id, body = {}) {
        const res = await fetch(this._url(`/${id}/subir-nivel`), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(body),
        });
        return this._handleResponse(res, 'Erro ao subir de nível');
    }

    async trocarMagiaConhecida(id, body) {
        const res = await fetch(this._url(`/${id}/magias/trocar`), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(body),
        });
        return this._handleResponse(res, 'Erro ao trocar magia conhecida');
    }

    async migrarMagiasDoJson(id, body) {
        const opts = {
            method: 'POST',
            headers: this._headers(body != null),
        };
        if (body != null) opts.body = JSON.stringify(body);
        const res = await fetch(this._url(`/${id}/magias/migrar-do-json`), opts);
        return this._handleResponse(res, 'Erro ao sincronizar magias da ficha');
    }

    async migrarTalentosDoJson(id) {
        const res = await fetch(this._url(`/${id}/talentos/migrar-do-json`), {
            method: 'POST',
            headers: this._headers(false),
        });
        return this._handleResponse(res, 'Erro ao vincular poderes da ficha');
    }

    async encerrarConcentracao(id) {
        const res = await fetch(this._url(`/${id}/magias/encerrar-concentracao`), {
            method: 'POST',
            headers: this._headers(false),
        });
        return this._handleResponse(res, 'Erro ao encerrar concentração');
    }
}
