/**
 * Campanha na ficha GURPS — select, solicitação de entrada e estados.
 */
(function (global) {
    function q(id) {
        return document.getElementById(id);
    }

    function esc(s) {
        if (s == null) return '';
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    global.GurpsFichaCampanhaSolicitacao = {
        _campanhas: [],
        _pendente: null,
        _vinculadoId: null,
        _personagemId: null,
        _bound: false,

        async init(opts) {
            const getPersonagemId =
                opts && typeof opts.getPersonagemId === 'function'
                    ? opts.getPersonagemId
                    : () => null;
            const getCampanhaIdVinculada =
                opts && typeof opts.getCampanhaIdVinculada === 'function'
                    ? opts.getCampanhaIdVinculada
                    : () => null;
            const Toast = opts && opts.Toast ? opts.Toast : global.Toast;
            const campSvc = new global.GurpsCampanhaService();

            const sel = q('fg_campanha');
            const hint = q('gurpsCampanhaSolicitacaoHint');
            const btnCancel = q('gurpsBtnCancelarSolicitacaoCampanha');
            if (!sel) return;

            this._personagemId = getPersonagemId();
            this._vinculadoId = getCampanhaIdVinculada();

            try {
                this._campanhas = await campSvc.listarDisponiveis();
                if (!Array.isArray(this._campanhas)) this._campanhas = [];
            } catch (e) {
                this._campanhas = [];
                if (Toast && Toast.warning) {
                    Toast.warning(e.message || 'Não foi possível carregar campanhas.');
                }
            }

            if (this._personagemId) {
                try {
                    this._pendente = await campSvc.obterMinhaSolicitacao(this._personagemId);
                } catch (_e) {
                    this._pendente = null;
                }
            }

            this._renderSelect(sel);
            this._atualizarUi(sel, hint, btnCancel);

            if (!this._bound) {
                this._bound = true;
                sel.addEventListener('change', async () => {
                    const val = sel.value.trim();
                    if (!val) return;
                    const campanhaId = Number(val);
                    if (!Number.isFinite(campanhaId) || campanhaId <= 0) return;
                    const pid = getPersonagemId();
                    if (!pid) {
                        if (Toast && Toast.error) {
                            Toast.error('Salve a ficha antes de solicitar entrada numa campanha.');
                        }
                        sel.value = '';
                        return;
                    }
                    if (this._vinculadoId) return;
                    try {
                        const res = await campSvc.criarSolicitacao({
                            campanha_id: campanhaId,
                            personagem_id: Number(pid),
                        });
                        if (res && res.vinculado_direto) {
                            this._vinculadoId = campanhaId;
                            this._pendente = null;
                            if (Toast && Toast.success) {
                                Toast.success('Personagem vinculado à campanha.');
                            }
                        } else {
                            this._pendente = res;
                            if (Toast && Toast.success) {
                                Toast.success('Solicitação enviada ao mestre da campanha.');
                            }
                        }
                        this._atualizarUi(sel, hint, btnCancel);
                    } catch (e) {
                        if (Toast && Toast.error) Toast.error(e.message || 'Erro ao solicitar');
                        sel.value = this._valorSelectAtual();
                    }
                });

                btnCancel?.addEventListener('click', async () => {
                    if (!this._pendente || !this._pendente.id) return;
                    try {
                        await campSvc.cancelarSolicitacao(this._pendente.id);
                        this._pendente = null;
                        sel.value = '';
                        if (Toast && Toast.success) Toast.success('Solicitação cancelada.');
                        this._atualizarUi(sel, hint, btnCancel);
                    } catch (e) {
                        if (Toast && Toast.error) Toast.error(e.message || 'Erro ao cancelar');
                    }
                });
            }
        },

        _valorSelectAtual() {
            if (this._vinculadoId) return String(this._vinculadoId);
            if (this._pendente && this._pendente.campanha_id) {
                return String(this._pendente.campanha_id);
            }
            return '';
        },

        _renderSelect(sel) {
            const opts = ['<option value="">— Nenhuma / escolher —</option>'];
            this._campanhas.forEach((c) => {
                const id = Number(c.id);
                const nome = esc(c.nome || `Campanha #${id}`);
                const mestre = esc(c.mestre_nome || '');
                const rotulo = mestre ? `${nome} (mestre: ${mestre})` : nome;
                opts.push(`<option value="${id}">${rotulo}</option>`);
            });
            sel.innerHTML = opts.join('');
            sel.value = this._valorSelectAtual();
        },

        _atualizarUi(sel, hint, btnCancel) {
            const vinculado = this._vinculadoId != null && Number(this._vinculadoId) > 0;
            const pendente = this._pendente && this._pendente.status === 'pendente';

            if (vinculado) {
                sel.disabled = true;
                if (hint) {
                    const c = this._campanhas.find(
                        (x) => Number(x.id) === Number(this._vinculadoId)
                    );
                    const nome = (c && c.nome) || '';
                    hint.textContent = nome
                        ? `Vinculado à campanha «${nome}».`
                        : 'Vinculado a uma campanha.';
                    hint.hidden = false;
                }
                if (btnCancel) btnCancel.hidden = true;
            } else if (pendente) {
                sel.disabled = true;
                if (hint) {
                    hint.textContent = `Aguardando aprovação do mestre para «${this._pendente.campanha_nome || 'campanha'}».`;
                    hint.hidden = false;
                }
                if (btnCancel) btnCancel.hidden = false;
            } else {
                sel.disabled = false;
                if (hint) hint.hidden = true;
                if (btnCancel) btnCancel.hidden = true;
            }
        },

        setVinculadoCampanhaId(campanhaId) {
            this._vinculadoId = campanhaId;
            const sel = q('fg_campanha');
            if (sel) sel.value = campanhaId ? String(campanhaId) : '';
        },
    };
})(typeof window !== 'undefined' ? window : this);
