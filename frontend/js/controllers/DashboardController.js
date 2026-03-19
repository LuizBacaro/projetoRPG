/**
 * DashboardController.js
 * ✅ Sem imports ES module — carregado via carregar() no dashboard.html
 * Dependências via window: AuthService, Toast, AtaqueService
 */

class DashboardController {

    constructor() {
        this.service            = new CombatenteServiceGlobal();
        this.ataqueService      = new AtaqueService();
        this.filtroAtual        = 'todos';
        this.combatenteEmEdicao = null;
        this.perfil             = (typeof AuthService !== 'undefined') ? AuthService.getPerfil() : 'mestre';
        this._registrarGlobais();
        this._inicializar();
    }

    _isMestre() {
        return this.perfil === 'mestre' || this.perfil === 'administrador';
    }

    _registrarGlobais() {
        var self = this;
        window.fecharModalCadastro        = function() { self._fecharModal('modalCadastroJogador'); };
        window.fecharModalCadastroMonstro = function() { self._fecharModal('modalCadastroMonstro'); };
        window.fecharModalCadastroNPC     = function() { self._fecharModal('modalCadastroNPC'); };
        window.fecharSeletorTipo          = function() { self._fecharModal('seletorTipo'); };
        window.fecharModalEdicao          = function() { self._fecharModal('modalEdicaoDashboard'); };

        window.abrirModalCadastro = function(tipo) {
            if (!self._isMestre() && (tipo === 'monstro' || tipo === 'npc')) {
                Toast.error('Acesso restrito: apenas Mestre pode cadastrar monstros e NPCs.');
                return;
            }
            self._fecharModal('seletorTipo');
            var mapa = {
                jogador: 'modalCadastroJogador',
                monstro: 'modalCadastroMonstro',
                npc:     'modalCadastroNPC'
            };
            self._abrirModal(mapa[tipo]);
        };

        window.confirmarDelecao     = function() { self._deletarCombatente(); };
        window.atualizarModificador = function(input) { self._calcularModificador(input); };

        window.previewImagemUpload = function(input, previewId, imgId, placeholderId) {
            self._previewImagem(input, previewId, imgId, placeholderId);
        };
        window.removerImagem        = function() { self._removerImagem('', false); };
        window.removerImagemMonstro = function() { self._removerImagem('Monstro', false); };
        window.removerImagemNPC     = function() { self._removerImagem('NPC', false); };
        window.removerImagemEdicao  = function() { self._removerImagem('', true); };

        window.adicionarLinhaAtaque = function() { self._adicionarLinhaAtaque(); };
        window.removerLinhaAtaque   = function(btn) { btn.closest('.ataque-linha').remove(); };

        // ✅ NOVO: Registrar funções de perícias
        window.abrirPaginaPericias             = function() { self._abrirPaginaPericias(); };
        window.recuperarPericiasDoSessionStorage = function() { self._recuperarPericiasDoSessionStorage(); };
    }

    _inicializar() {
        this._aplicarRestricoesPerfil();
        this._configurarAbas();
        this._configurarFiltros();
        this._configurarBotaoNovo();
        this._configurarFormCadastro('formCadastroJogador', 'jogador', 'modalCadastroJogador');
        this._configurarFormCadastro('formCadastroMonstro', 'monstro', 'modalCadastroMonstro');
        this._configurarFormCadastro('formCadastroNPC',     'npc',     'modalCadastroNPC');
        this._configurarFormEdicao();
        this._configurarUpload('');
        this._configurarUpload('Monstro');
        this._configurarUpload('NPC');
        this._configurarUploadEdicao();
        this.carregarCombatentes();
    }

    _aplicarRestricoesPerfil() {
        if (this._isMestre()) return;

        // ✅ Oculta aba Arena para Jogador
        const tabArena = document.querySelector('.nav-tab[data-tab="arena"]');
        if (tabArena) tabArena.style.display = 'none';

        // Oculta filtros de monstro e NPC
        const filtroMonstro = document.querySelector('.filter-btn[data-tipo="monstro"]');
        const filtroNPC     = document.querySelector('.filter-btn[data-tipo="npc"]');
        if (filtroMonstro) filtroMonstro.style.display = 'none';
        if (filtroNPC)     filtroNPC.style.display     = 'none';

        // Oculta botão Novo Combatente
        const btnNovo = document.getElementById('btnNovoCombatente');
        if (btnNovo) btnNovo.style.display = 'none';

        // Oculta cards de resumo de Monstros e NPCs
        const resumoMonstros = document.getElementById('totalMonstros')?.closest('.resumo-card');
        const resumoNPCs     = document.getElementById('totalNPCs')?.closest('.resumo-card');
        if (resumoMonstros) resumoMonstros.style.display = 'none';
        if (resumoNPCs)     resumoNPCs.style.display     = 'none';
    }

    _configurarAbas() {
        document.querySelectorAll('.nav-tab').forEach(function(btn) {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.nav-tab').forEach(function(b) { b.classList.remove('active'); });
                document.querySelectorAll('.tab-section').forEach(function(s) { s.classList.remove('active'); });
                btn.classList.add('active');
                document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
            });
        });
    }

    _configurarFiltros() {
        var self = this;
        document.querySelectorAll('.filter-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                if (!self._isMestre() && (btn.dataset.tipo === 'monstro' || btn.dataset.tipo === 'npc')) return;
                document.querySelectorAll('.filter-btn').forEach(function(b) { b.classList.remove('active'); });
                btn.classList.add('active');
                self.filtroAtual = btn.dataset.tipo;
                self.carregarCombatentes();
            });
        });
    }

    _configurarBotaoNovo() {
        var self = this;
        var btn  = document.getElementById('btnNovoCombatente');
        if (btn) btn.addEventListener('click', function() { self._abrirModal('seletorTipo'); });
    }

    _configurarFormCadastro(formId, tipo, modalId) {
        var self = this;
        var form = document.getElementById(formId);
        if (!form) { console.error('Form nao encontrado: ' + formId); return; }

        var textos = { jogador: 'Cadastrar Jogador', monstro: 'Cadastrar Monstro', npc: 'Cadastrar NPC' };

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            var btn = form.querySelector('[type="submit"]');
            btn.disabled    = true;
            btn.textContent = 'Salvando...';
            try {
                var c = await self.service.criar(new FormData(form));
                Toast.success(c.nome + ' cadastrado com sucesso!');
                self._fecharModal(modalId);
                self._limparForm(form, tipo);
                self.carregarCombatentes();
            } catch (err) {
                Toast.error(err.message || 'Erro ao cadastrar');
                console.error(err);
            } finally {
                btn.disabled    = false;
                btn.textContent = textos[tipo];
            }
        });
    }

    _configurarFormEdicao() {
        var self = this;
        var form = document.getElementById('formEdicaoDashboard');
        if (!form) { console.error('Form de edicao nao encontrado'); return; }

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            var btn = form.querySelector('[type="submit"]');
            btn.disabled    = true;
            btn.textContent = 'Salvando...';
            try {
                var id = parseInt(document.getElementById('dashEditId').value);
                await self.service.atualizar(id, new FormData(form));
                await Promise.all([
                    self._salvarAtaquesEdicao(id),
                    // ✅ _salvarMagiasEdicao REMOVIDO — grimório gerencia os slots
                    self._salvarPericiasEdicao(id),
                ]);
                self._fecharModal('modalEdicaoDashboard');
                self.combatenteEmEdicao = null;
                self.carregarCombatentes();
                Toast.success('Alteracoes salvas com sucesso!');
            } catch (err) {
                Toast.error(err.message || 'Erro ao salvar alteracoes');
                console.error(err);
            } finally {
                btn.disabled    = false;
                btn.textContent = 'Salvar Alteracoes';
            }
        });
    }

    _configurarUpload(sufixo) {
        var self  = this;
        var input = document.getElementById('inputFoto' + sufixo);
        if (!input) return;
        input.addEventListener('change', function() {
            self._previewImagem(input, 'uploadPreview' + sufixo, 'previewImage' + sufixo, 'uploadPlaceholder' + sufixo);
        });
    }

    _configurarUploadEdicao() {
        var self  = this;
        var area  = document.getElementById('dashEditUploadArea');
        var input = document.getElementById('dashEditFoto');
        if (!area || !input) return;
        area.addEventListener('click', function() { input.click(); });
        input.addEventListener('change', function() {
            self._previewImagem(input, 'dashEditUploadPreview', 'dashEditPreviewImage', 'dashEditUploadPlaceholder');
        });
    }

    async carregarCombatentes() {
        try {
            var tipo = this.filtroAtual === 'todos' ? null : this.filtroAtual;

            // Jogador: nunca carrega monstros nem NPCs
            if (!this._isMestre() && (tipo === 'monstro' || tipo === 'npc')) tipo = 'jogador';
            if (!this._isMestre() && tipo === null) tipo = 'jogador';

            var combatentes = await this.service.listar(tipo);
            this._renderizarTabela(combatentes);
            this._atualizarResumo(combatentes);
        } catch (err) {
            Toast.error('Erro ao carregar combatentes');
            console.error(err);
        }
    }

    _renderizarTabela(combatentes) {
        var self  = this;
        var tbody = document.getElementById('tabelaCombatentes');

        if (!combatentes.length) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:2rem;color:#64748b">Nenhum combatente cadastrado.</td></tr>';
            return;
        }

        // ✅ Oculta colunas HP e Iniciativa para Jogador ver monstro/NPC
        var cabecalho = document.querySelectorAll('.tabela-combatentes th');
        if (cabecalho.length >= 6) {
            cabecalho[4].style.display = this._isMestre() ? '' : 'none'; // HP Máx
            cabecalho[5].style.display = this._isMestre() ? '' : 'none'; // Iniciativa
        }

        var rows = '';
        for (var i = 0; i < combatentes.length; i++) {
            var c          = combatentes[i];
            var podeVerStats = AuthService.podeVerStatsDe(c.tipo);
            var hpTexto      = podeVerStats ? c.hp_maximo  : '???';
            var iniTexto     = podeVerStats ? c.iniciativa : '???';

            rows += '<tr>';
            rows += '<td><span class="badge badge-' + c.tipo + '">' + c.tipo + '</span></td>';
            rows += '<td>' + c.nome + '</td>';
            rows += '<td>' + (c.classe || '-') + '</td>';
            rows += '<td>' + (c.nivel || 1) + '</td>';
            rows += '<td style="' + (this._isMestre() ? '' : 'display:none') + '">';
            rows += '<span class="' + (podeVerStats ? '' : 'stat-oculto') + '">' + hpTexto + '</span>';
            rows += '</td>';
            rows += '<td style="' + (this._isMestre() ? '' : 'display:none') + '">';
            rows += '<span class="' + (podeVerStats ? '' : 'stat-oculto') + '">' + iniTexto + '</span>';
            rows += '</td>';
            rows += '<td>';
            rows += '<div class="tabela-acoes">';
            rows += '<button class="btn-acao btn-ver-ficha" data-id="' + c.id + '" data-acao="ver" title="Ver ficha" onclick="window.open(\'/pages/ficha-personagem.html?id=' + c.id + '\', \'_blank\')">👁️</button>';
            rows += '<button class="btn-acao" data-id="' + c.id + '" data-acao="editar" title="Editar">✏️</button>';
            if (self._isMestre()) {
                rows += '<button class="btn-acao" data-id="' + c.id + '" data-acao="excluir" title="Excluir">🗑️</button>';
            }
            rows += '</div></td></tr>';
        }
        tbody.innerHTML = rows;

        tbody.querySelectorAll('[data-acao="editar"]').forEach(function(btn) {
            btn.addEventListener('click', function() { self._abrirEdicao(parseInt(btn.dataset.id)); });
        });
        if (self._isMestre()) {
            tbody.querySelectorAll('[data-acao="excluir"]').forEach(function(btn) {
                btn.addEventListener('click', function() { self._excluirCombatente(parseInt(btn.dataset.id)); });
            });
        }
    }

    _atualizarResumo(combatentes) {
        var totalEl = document.getElementById('totalGeral');
        var jogEl   = document.getElementById('totalJogadores');
        var monEl   = document.getElementById('totalMonstros');
        var npcEl   = document.getElementById('totalNPCs');
        if (totalEl) totalEl.textContent = combatentes.length;
        if (jogEl)   jogEl.textContent   = combatentes.filter(function(c) { return c.tipo === 'jogador'; }).length;
        if (monEl)   monEl.textContent   = combatentes.filter(function(c) { return c.tipo === 'monstro'; }).length;
        if (npcEl)   npcEl.textContent   = combatentes.filter(function(c) { return c.tipo === 'npc'; }).length;
    }

    async _abrirEdicao(id) {
        try {
            var c = await this.service.obterPorId(id);

            if (!this._isMestre() && (c.tipo === 'monstro' || c.tipo === 'npc')) {
                Toast.error('Acesso restrito: voce nao pode editar monstros ou NPCs.');
                return;
            }

            this.combatenteEmEdicao   = c;
            window.combatenteEmEdicao = c;

            document.getElementById('dashEditId').value         = c.id;
            document.getElementById('dashEditTipo').value       = c.tipo;
            document.getElementById('dashEditNome').value       = c.nome;
            document.getElementById('dashEditHP').value         = c.hp_maximo;
            document.getElementById('dashEditIniciativa').value = c.iniciativa;
            document.getElementById('dashEditClasse').value     = c.classe || '';
            document.getElementById('dashEditRaca').value       = c.raca   || '';
            document.getElementById('dashEditNivel').value      = c.nivel  || 1;
            document.getElementById('dashEditPontos').value     = c.pontos || 0;

            document.getElementById('dashEditCA').value        = c.ca        ?? 10;
            document.getElementById('dashEditToque').value     = c.toque     ?? 10;
            document.getElementById('dashEditSurpresa').value  = c.surpresa  ?? 10;
            document.getElementById('dashEditFortitude').value = c.fortitude ?? 0;
            document.getElementById('dashEditReflexos').value  = c.reflexos  ?? 0;
            document.getElementById('dashEditVontade').value   = c.vontade   ?? 0;

            document.getElementById('dashEditFOR').value = c.forca        || 10;
            document.getElementById('dashEditDES').value = c.destreza     || 10;
            document.getElementById('dashEditCON').value = c.constituicao || 10;
            document.getElementById('dashEditINT').value = c.inteligencia || 10;
            document.getElementById('dashEditSAB').value = c.sabedoria    || 10;
            document.getElementById('dashEditCAR').value = c.carisma      || 10;

            var self = this;
            ['dashEditFOR','dashEditDES','dashEditCON','dashEditINT','dashEditSAB','dashEditCAR'].forEach(function(fid) {
                var el = document.getElementById(fid);
                if (el) self._calcularModificador(el);
            });

            // ✅ NOVO: Página de referência — visível só para monstros
            var secPagRef   = document.getElementById('secaoPaginaReferencia');
            var inputPagRef = document.getElementById('dashEditPaginaReferencia');
            var isMonstro   = (c.tipo === 'monstro');
            if (secPagRef)   secPagRef.style.display   = isMonstro ? 'block' : 'none';
            if (inputPagRef) inputPagRef.value          = isMonstro ? (c.pagina_referencia || '') : '';

            var placeholder = document.getElementById('dashEditUploadPlaceholder');
            var preview     = document.getElementById('dashEditUploadPreview');
            var img         = document.getElementById('dashEditPreviewImage');
            if (c.foto_url) {
                img.src                   = c.foto_url;
                placeholder.style.display = 'none';
                preview.style.display     = 'block';
            } else {
                placeholder.style.display = 'flex';
                preview.style.display     = 'none';
            }

            // Ataques: apenas para jogadores
            var secAtaques = document.getElementById('secaoAtaquesEdicao');
            var isJogador  = (c.tipo === 'jogador');
            if (secAtaques) secAtaques.style.display = isJogador ? 'block' : 'none';
            if (isJogador)  this._renderizarAtaquesEdicao(c.ataques || []);

            this._recuperarPericiasDoSessionStorage();
            this._abrirModal('modalEdicaoDashboard');

        } catch (err) {
            Toast.error('Erro ao carregar combatente');
            console.error(err);
        }
    }

     // ✅ REFATORADO: usa ModalConfirm centralizado (carregado via window)
    async _excluirCombatente(id) {
        if (!this._isMestre()) { Toast.error('Acesso restrito.'); return; }
        var self = this;
        ModalConfirm.mostrar({
            icone:           '🗑️',
            titulo:          'Excluir Combatente',
            texto:           'Deseja excluir este combatente? Esta ação não pode ser desfeita.',
            textoConfirmar:  '🗑️ Excluir',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar: async function() {
                try {
                    await self.service.deletar(id);
                    Toast.success('Combatente excluido!');
                    self.carregarCombatentes();
                } catch (err) {
                    Toast.error('Erro ao excluir');
                    console.error(err);
                }
            }
        });
    }

    // ✅ REFATORADO: usa ModalConfirm centralizado
    async _deletarCombatente() {
        if (!this._isMestre()) { Toast.error('Acesso restrito.'); return; }
        if (!this.combatenteEmEdicao) return;
        var self = this;
        var nome = this.combatenteEmEdicao.nome;
        ModalConfirm.mostrar({
            icone:           '🗑️',
            titulo:          'Deletar Combatente',
            texto:           'Deletar <strong>' + nome + '</strong>? Esta ação não pode ser desfeita.',
            textoConfirmar:  '🗑️ Deletar',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar: async function() {
                try {
                    await self.service.deletar(self.combatenteEmEdicao.id);
                    Toast.success('Combatente deletado!');
                    self._fecharModal('modalEdicaoDashboard');
                    self.combatenteEmEdicao   = null;
                    window.combatenteEmEdicao = null;
                    self.carregarCombatentes();
                } catch (err) {
                    Toast.error('Erro ao deletar');
                    console.error(err);
                }
            }
        });
    }


    /**
     * Modal customizado de confirmação — SRP: apenas DOM
     * Reutilizável em qualquer ação destrutiva do DashboardController
     */
    _mostrarModalConfirmacao(opcoes) {
        var anterior = document.getElementById('_modalConfirmGlobal');
        if (anterior) anterior.remove();

        var overlay = document.createElement('div');
        overlay.id        = '_modalConfirmGlobal';
        overlay.className = 'modal-confirm-overlay';
        overlay.innerHTML =
            '<div class="modal-confirm-box">'
          + '<div class="modal-confirm-header">'
          + '<span class="modal-confirm-icone">' + (opcoes.icone || '⚠️') + '</span>'
          + '<h3 class="modal-confirm-titulo">'  + (opcoes.titulo || 'Confirmar') + '</h3>'
          + '</div>'
          + '<p class="modal-confirm-texto">' + (opcoes.texto || 'Deseja continuar?') + '</p>'
          + '<div class="modal-confirm-botoes">'
          + '<button class="modal-confirm-btn modal-confirm-cancelar" id="_confirmCancelar">'
          + (opcoes.textoCancelar || 'Cancelar') + '</button>'
          + '<button class="modal-confirm-btn ' + (opcoes.classeConfirmar || 'modal-confirm-ok') + '" id="_confirmOk">'
          + (opcoes.textoConfirmar || 'Confirmar') + '</button>'
          + '</div></div>';

        document.body.appendChild(overlay);
        requestAnimationFrame(function() { overlay.classList.add('show'); });

        function fechar() {
            overlay.classList.remove('show');
            setTimeout(function() { if (overlay.parentNode) overlay.remove(); }, 250);
        }

        document.getElementById('_confirmCancelar').addEventListener('click', function() {
            fechar();
            if (opcoes.onCancelar) opcoes.onCancelar();
        });
        document.getElementById('_confirmOk').addEventListener('click', function() {
            fechar();
            if (opcoes.onConfirmar) opcoes.onConfirmar();
        });
        overlay.addEventListener('click', function(e) { if (e.target === overlay) fechar(); });

        var onEsc = function(e) {
            if (e.key === 'Escape') { fechar(); document.removeEventListener('keydown', onEsc); }
        };
        document.addEventListener('keydown', onEsc);
    }

    _renderizarAtaquesEdicao(ataques) {
        var lista = document.getElementById('listaAtaquesEdicao');
        if (!lista) return;
        lista.innerHTML = '';
        if (!ataques.length) { this._adicionarLinhaAtaque(); return; }
        for (var i = 0; i < ataques.length; i++) { this._adicionarLinhaAtaque(ataques[i]); }
    }

    _adicionarLinhaAtaque(ataque) {
        var lista = document.getElementById('listaAtaquesEdicao');
        if (!lista) return;
        var div       = document.createElement('div');
        div.className = 'ataque-linha';
        div.innerHTML =
            '<input type="text" class="ataque-nome"  placeholder="Nome"  value="' + (ataque?.nome         || '') + '" />' +
            '<input type="text" class="ataque-bonus" placeholder="+0"    value="' + (ataque?.bonus_ataque  || '+0') + '" style="width:70px" />' +
            '<input type="text" class="ataque-dano"  placeholder="1d6"   value="' + (ataque?.dano          || '') + '" style="width:90px" />' +
            '<input type="text" class="ataque-tipo"  placeholder="tipo"  value="' + (ataque?.tipo_dano     || '') + '" style="width:120px" />' +
            '<button type="button" class="btn-dash-delete" onclick="removerLinhaAtaque(this)">✕</button>';
        lista.appendChild(div);
    }

    _coletarAtaquesEdicao() {
        return Array.from(document.querySelectorAll('#listaAtaquesEdicao .ataque-linha'))
            .map(function(l) {
                return {
                    nome:         l.querySelector('.ataque-nome').value.trim(),
                    bonus_ataque: l.querySelector('.ataque-bonus').value.trim() || '+0',
                    dano:         l.querySelector('.ataque-dano').value.trim()  || '1d6',
                    tipo_dano:    l.querySelector('.ataque-tipo').value.trim()
                };
            })
            .filter(function(a) { return a.nome; });
    }

    async _salvarAtaquesEdicao(combatenteId) {
        await this.ataqueService.salvarAtaques(combatenteId, this._coletarAtaquesEdicao());
    }

    _renderizarMagiasEdicao(slots) {
        var container = document.getElementById('gridMagiasEdicao');
        if (!container) return;
        var html = '';
        for (var nivel = 0; nivel <= 9; nivel++) {
            var slot  = slots.find(function(s) { return s.nivel === nivel; }) || null;
            var total = slot ? slot.total : 0;
            html += '<div class="magia-edicao-linha">';
            html += '<span class="magia-nivel-label">Nivel ' + nivel + '</span>';
            html += '<div style="flex:1">';
            html += '<input type="number" class="magia-total-input" data-nivel="' + nivel + '" value="' + total + '" min="0" max="20" style="width:100%;padding:.4rem .6rem;border-radius:.35rem;border:1px solid #334155;background:#0f0f23;color:#e2e8f0;font-size:.85rem;box-sizing:border-box" />';
            html += '</div></div>';
        }
        container.innerHTML = html;
    }

    _coletarMagiasEdicao() {
        return Array.from(document.querySelectorAll('#gridMagiasEdicao .magia-total-input'))
            .map(function(input) {
                return { nivel: parseInt(input.dataset.nivel), total: parseInt(input.value) || 0, usados: 0 };
            });
    }

    async _salvarMagiasEdicao(combatenteId) {
        await this.ataqueService.salvarMagias(combatenteId, this._coletarMagiasEdicao());
    }

    // ✅ NOVO: Salvar perícias
    async _salvarPericiasEdicao(combatenteId) {
        if (!window.combatenteEmEdicao || !window.combatenteEmEdicao.pericias) {
            return; // Nenhuma perícia selecionada
        }
        try {
            // Armazenar perícias para recuperação após volta
            sessionStorage.setItem('periciasEdit', JSON.stringify(window.combatenteEmEdicao.pericias));
            sessionStorage.setItem('combatenteEditId', combatenteId);
        } catch (err) {
            console.error('Erro ao salvar perícias em sessionStorage:', err);
        }
    }

    // ✅ NOVO: Abrir página de perícias
    _abrirPaginaPericias() {
        if (!this.combatenteEmEdicao || !this.combatenteEmEdicao.id) {
            Toast.error('❌ Selecione um combatente primeiro');
            return;
        }

        try {
            var id      = this.combatenteEmEdicao.id;
            var nome    = document.getElementById('dashEditNome')?.value || this.combatenteEmEdicao.nome;
            var tipo    = document.getElementById('dashEditTipo')?.value || this.combatenteEmEdicao.tipo;
            var pericias = window.combatenteEmEdicao?.pericias || [];

            var params = new URLSearchParams({
                combatente_id: id,
                nome: nome,
                tipo: tipo,
                pericias: JSON.stringify(pericias)
            });

            console.log('🔗 Navegando para perícias:', {
                id: id,
                nome: nome,
                tipo: tipo,
                periciasCount: pericias.length
            });

            window.location.href = '/pages/pericias.html?' + params.toString();
        } catch (erro) {
            Toast.error('❌ Erro ao abrir perícias');
            console.error(erro);
        }
    }

    // ✅ NOVO: Recuperar perícias do sessionStorage
    _recuperarPericiasDoSessionStorage() {
        var periciasEdit = sessionStorage.getItem('periciasEdit');
        var combatenteId = sessionStorage.getItem('combatenteEditId');

        if (periciasEdit && combatenteId) {
            try {
                var pericias = JSON.parse(periciasEdit);

                // Atualizar combatente se for o mesmo
                if (window.combatenteEmEdicao && window.combatenteEmEdicao.id == combatenteId) {
                    window.combatenteEmEdicao.pericias = pericias;
                    this.combatenteEmEdicao.pericias = pericias;
                    Toast.success('✅ ' + pericias.length + ' perícia(s) carregada(s)');

                    console.log('📚 Perícias recuperadas:', pericias);
                }

                // Limpar sessionStorage
                sessionStorage.removeItem('periciasEdit');
                sessionStorage.removeItem('combatenteEditId');
            } catch (erro) {
                console.error('❌ Erro ao recuperar perícias:', erro);
                Toast.error('⚠️ Erro ao carregar perícias salvas');
            }
        }
    }

    _abrirModal(id) {
        var el = document.getElementById(id);
        if (el) el.classList.add('show');
        else    console.error('Modal nao encontrado: ' + id);
    }

    _fecharModal(id) {
        var el = document.getElementById(id);
        if (el) el.classList.remove('show');
    }

    _previewImagem(input, previewId, imgId, placeholderId) {
        var file = input.files ? input.files[0] : null;
        if (!file) return;
        var reader    = new FileReader();
        reader.onload = function(e) {
            var ph = document.getElementById(placeholderId);
            var pv = document.getElementById(previewId);
            var im = document.getElementById(imgId);
            if (ph) ph.style.display = 'none';
            if (pv) pv.style.display = 'block';
            if (im) im.src           = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    _removerImagem(sufixo, isEdit) {
        var inputId       = isEdit ? 'dashEditFoto'              : 'inputFoto'         + sufixo;
        var placeholderId = isEdit ? 'dashEditUploadPlaceholder' : 'uploadPlaceholder' + sufixo;
        var previewId     = isEdit ? 'dashEditUploadPreview'     : 'uploadPreview'     + sufixo;
        var input         = document.getElementById(inputId);
        var placeholder   = document.getElementById(placeholderId);
        var preview       = document.getElementById(previewId);
        if (input)       input.value               = '';
        if (placeholder) placeholder.style.display = 'flex';
        if (preview)     preview.style.display     = 'none';
    }

    _calcularModificador(input) {
        var valor = parseInt(input.value) || 10;
        var mod   = Math.floor((valor - 10) / 2);
        var modId = 'mod' + input.id.charAt(0).toUpperCase() + input.id.slice(1);
        var span  = document.getElementById(modId);
        if (span) span.textContent = mod >= 0 ? ('+' + mod) : ('' + mod);
    }

    _limparForm(form, tipo) {
        form.reset();
        var sufixos = { jogador: '', monstro: 'Monstro', npc: 'NPC' };
        var sufixo  = sufixos[tipo] || '';
        var ph = document.getElementById('uploadPlaceholder' + sufixo);
        var pv = document.getElementById('uploadPreview'     + sufixo);
        if (ph) ph.style.display = 'flex';
        if (pv) pv.style.display = 'none';
    }
}

// ── Classes auxiliares 

class CombatenteServiceGlobal {
    _url(path) { return window.getApiUrl('/combatentes' + (path || '')); }
    _headers() {
        var h = {};
        if (typeof AuthService !== 'undefined') {
            var t = AuthService.getToken();
            if (t) h['Authorization'] = 'Bearer ' + t;
        }
        return h;
    }
    async listar(tipo) {
        var url = tipo ? (this._url() + '?tipo=' + tipo) : this._url();
        var res = await fetch(url, { headers: this._headers() });
        if (!res.ok) throw new Error('Erro ao carregar combatentes');
        return res.json();
    }
    async obterPorId(id) {
        var res = await fetch(this._url('/' + id), { headers: this._headers() });
        if (!res.ok) throw new Error('Combatente nao encontrado');
        return res.json();
    }
    async criar(formData) {
        var res = await fetch(this._url(), { method: 'POST', headers: this._headers(), body: formData });
        if (!res.ok) { var e = await res.json().catch(function() { return {}; }); throw new Error(e.detail || 'Erro ao criar'); }
        return res.json();
    }
    async atualizar(id, formData) {
        var res = await fetch(this._url('/' + id), { method: 'PUT', headers: this._headers(), body: formData });
        if (!res.ok) { var e = await res.json().catch(function() { return {}; }); throw new Error(e.detail || 'Erro ao atualizar'); }
        return res.json();
    }
    async deletar(id) {
        var res = await fetch(this._url('/' + id), { method: 'DELETE', headers: this._headers() });
        if (!res.ok) throw new Error('Erro ao deletar');
        return true;
    }
}

// ✅ Instancia após todos os serviços carregados
new DashboardController();