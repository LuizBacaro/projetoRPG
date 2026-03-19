/**
 * Componente de Modal de Edição
 * SRP: gerenciar modal de edição
 */
import { CombatenteService }    from '../services/CombatenteService.js';
import { UploadService }        from '../services/UploadService.js';
import { Toast }                from './toast.module.js';
import { atualizarModificadorDOM } from '../utils/dnd.js';

export class ModalEdicao {
    constructor() {
        this.combatenteService = new CombatenteService();
        this.uploadService     = new UploadService();
        this.combatenteAtual   = null;
        this.inicializar();
    }

    inicializar() {
        this.configurarEventos();
        this.configurarFormulario();
        this.configurarUpload();
    }

    configurarEventos() {
        document.addEventListener('abrirEdicao', async (e) => {
            await this.abrir(e.detail.id);
        });
        document.addEventListener('combatenteCriado', () => {
            if (this.combatenteAtual) this.carregar(this.combatenteAtual.id);
        });
    }

    configurarFormulario() {
        const form = document.getElementById('formEdicaoCombatente');
        if (!form) return;
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.salvar(form);
        });
    }

    configurarUpload() {
        const input       = document.getElementById('editFoto');
        const area        = document.getElementById('editUploadArea');
        const placeholder = document.getElementById('editUploadPlaceholder');
        const preview     = document.getElementById('editUploadPreview');
        const previewImage = document.getElementById('editPreviewImage');
        if (!input || !area) return;

        area.addEventListener('click', () => input.click());
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            try {
                this.uploadService.criarPreview(file, (dataUrl) => {
                    previewImage.src          = dataUrl;
                    placeholder.style.display = 'none';
                    preview.style.display     = 'block';
                });
            } catch (error) {
                Toast.error(error.message);
                input.value = '';
            }
        });
    }

    async abrir(combatenteId) {
        try {
            await this.carregar(combatenteId);
            const modal = document.getElementById('modalEdicao');
            if (modal) modal.classList.add('show');
        } catch (error) {
            Toast.error('Erro ao carregar combatente');
            console.error(error);
        }
    }

    async carregar(combatenteId) {
        try {
            const combatente = await this.combatenteService.obterPorId(combatenteId);
            this.combatenteAtual = combatente;

            document.getElementById('editId').value        = combatente.id;
            document.getElementById('editNome').value      = combatente.nome;
            document.getElementById('editHP').value        = combatente.hp_maximo;
            document.getElementById('editIniciativa').value = combatente.iniciativa;
            document.getElementById('editClasse').value    = combatente.classe;
            document.getElementById('editTipo').value      = combatente.tipo;
            document.getElementById('editNivel').value     = combatente.nivel;
            document.getElementById('editPontos').value    = combatente.pontos;

            document.getElementById('editCA').value       = combatente.ca       ?? 10;
            document.getElementById('editToque').value    = combatente.toque    ?? 10;
            document.getElementById('editSurpresa').value = combatente.surpresa ?? 10;

            document.getElementById('editFOR').value = combatente.forca;
            document.getElementById('editDES').value = combatente.destreza;
            document.getElementById('editCON').value = combatente.constituicao;
            document.getElementById('editINT').value = combatente.inteligencia;
            document.getElementById('editSAB').value = combatente.sabedoria;
            document.getElementById('editCAR').value = combatente.carisma;

            document.getElementById('editFortitude').value = combatente.fortitude ?? 0;
            document.getElementById('editReflexos').value  = combatente.reflexos  ?? 0;
            document.getElementById('editVontade').value   = combatente.vontade   ?? 0;

            ['editFOR','editDES','editCON','editINT','editSAB','editCAR'].forEach(id => {
                const input = document.getElementById(id);
                if (input) atualizarModificadorDOM(input);
            });

            const placeholder  = document.getElementById('editUploadPlaceholder');
            const preview      = document.getElementById('editUploadPreview');
            const previewImage = document.getElementById('editPreviewImage');

            if (combatente.foto_url) {
                previewImage.src          = combatente.foto_url;
                placeholder.style.display = 'none';
                preview.style.display     = 'block';
            } else {
                placeholder.style.display = 'flex';
                preview.style.display     = 'none';
            }

        } catch (error) {
            console.error('Erro ao carregar combatente:', error);
            throw error;
        }
    }

    async salvar(form) {
        try {
            const formData = new FormData(form);
            const id       = parseInt(document.getElementById('editId').value);
            await this.combatenteService.atualizar(id, formData);
            Toast.success('Combatente atualizado! ✅');
            this.fechar();
            document.dispatchEvent(new CustomEvent('combatenteAtualizado'));
        } catch (error) {
            Toast.error(error.message || 'Erro ao atualizar');
            console.error(error);
        }
    }

    /**
     * ✅ CORRIGIDO: modal customizado em vez de confirm() nativo
     * SRP: confirmação delegada ao modal — HTTP delegado a _executarDeletar()
     */
    deletar() {
        if (!this.combatenteAtual) return;
        this._mostrarModalConfirmacao({
            icone:          '🗑️',
            titulo:         'Deletar Combatente',
            texto:          `Deseja realmente deletar <strong>${this.combatenteAtual.nome}</strong>? Esta ação não pode ser desfeita.`,
            textoCancelar:  'Cancelar',
            textoConfirmar: '🗑️ Deletar',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar:    () => this._executarDeletar(),
        });
    }

    async _executarDeletar() {
        try {
            await this.combatenteService.deletar(this.combatenteAtual.id);
            Toast.success('Combatente deletado! 🗑️');
            this.fechar();
            document.dispatchEvent(new CustomEvent('combatenteDeletado'));
        } catch (error) {
            Toast.error('Erro ao deletar');
            console.error(error);
        }
    }

    fechar() {
        const modal = document.getElementById('modalEdicao');
        if (modal) modal.classList.remove('show');
        this.combatenteAtual = null;
    }

    // ──────────────────────────────────────────
    // Modal customizado de confirmação
    // SRP: apenas criação e controle do modal DOM
    // ──────────────────────────────────────────

    _mostrarModalConfirmacao(opcoes) {
        const anterior = document.getElementById('_modalConfirmGlobal');
        if (anterior) anterior.remove();

        const overlay = document.createElement('div');
        overlay.id        = '_modalConfirmGlobal';
        overlay.className = 'modal-confirm-overlay';
        overlay.innerHTML = `
            <div class="modal-confirm-box">
                <div class="modal-confirm-header">
                    <span class="modal-confirm-icone">${opcoes.icone || '⚠️'}</span>
                    <h3 class="modal-confirm-titulo">${opcoes.titulo || 'Confirmar'}</h3>
                </div>
                <p class="modal-confirm-texto">${opcoes.texto || 'Deseja continuar?'}</p>
                <div class="modal-confirm-botoes">
                    <button class="modal-confirm-btn modal-confirm-cancelar" id="_confirmCancelar">
                        ${opcoes.textoCancelar || 'Cancelar'}
                    </button>
                    <button class="modal-confirm-btn ${opcoes.classeConfirmar || 'modal-confirm-ok'}" id="_confirmOk">
                        ${opcoes.textoConfirmar || 'Confirmar'}
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);
        requestAnimationFrame(() => overlay.classList.add('show'));

        const fechar = () => {
            overlay.classList.remove('show');
            setTimeout(() => { if (overlay.parentNode) overlay.remove(); }, 250);
        };

        document.getElementById('_confirmCancelar').addEventListener('click', () => {
            fechar();
            if (opcoes.onCancelar) opcoes.onCancelar();
        });
        document.getElementById('_confirmOk').addEventListener('click', () => {
            fechar();
            if (opcoes.onConfirmar) opcoes.onConfirmar();
        });
        overlay.addEventListener('click', (e) => { if (e.target === overlay) fechar(); });

        const onEsc = (e) => {
            if (e.key === 'Escape') { fechar(); document.removeEventListener('keydown', onEsc); }
        };
        document.addEventListener('keydown', onEsc);
    }
}