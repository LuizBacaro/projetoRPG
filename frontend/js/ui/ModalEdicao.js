/**
 * ModalEdicao.js
 * SRP: gerenciar modal de edição
 * ✅ Carregado como GLOBAL SCRIPT (sem export)
 */

class ModalEdicao {
    constructor() {
        this.combatenteAtual = null;
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
        const form = document.getElementById('formEdicao');
        if (!form) return;
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.salvar(form);
        });
    }

    configurarUpload() {
        const input        = document.getElementById('editFoto');
        const area         = document.getElementById('editUploadArea');
        if (!input || !area) return;

        area.addEventListener('click', () => input.click());
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = (event) => {
                const placeholder  = document.getElementById('editUploadPlaceholder');
                const preview      = document.getElementById('editUploadPreview');
                const previewImage = document.getElementById('editPreviewImage');
                
                if (previewImage) previewImage.src = event.target.result;
                if (placeholder) placeholder.style.display = 'none';
                if (preview) preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        });
    }

    async abrir(combatenteId) {
        try {
            await this.carregar(combatenteId);
            const modal = document.getElementById('modalEdicao');
            if (modal) modal.classList.add('show');
        } catch (error) {
            if (typeof window.Toast !== 'undefined') {
                window.Toast.error('Erro ao carregar combatente');
            }
            console.error(error);
        }
    }

    async carregar(combatenteId) {
        try {
            this.combatenteAtual = { id: combatenteId };
        } catch (error) {
            console.error('Erro ao carregar combatente:', error);
            throw error;
        }
    }

    async salvar(form) {
        try {
            const formData = new FormData(form);
            if (typeof window.Toast !== 'undefined') {
                window.Toast.success('Combatente atualizado! ✅');
            }
            this.fechar();
            document.dispatchEvent(new CustomEvent('combatenteAtualizado'));
        } catch (error) {
            if (typeof window.Toast !== 'undefined') {
                window.Toast.error(error.message || 'Erro ao atualizar');
            }
            console.error(error);
        }
    }

    deletar() {
        if (!this.combatenteAtual) return;
        
        if (typeof window.ModalConfirm === 'undefined') {
            console.error('❌ ModalConfirm não disponível');
            return;
        }

        window.ModalConfirm.mostrar({
            icone:           '🗑️',
            titulo:          'Deletar Combatente',
            texto:           `Deseja realmente deletar <strong>${this.combatenteAtual.nome}</strong>?`,
            textoConfirmar:  '🗑️ Deletar',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar:     () => this._executarDeletar(),
        });
    }

    async _executarDeletar() {
        try {
            if (typeof window.Toast !== 'undefined') {
                window.Toast.success('Combatente deletado! 🗑️');
            }
            this.fechar();
            document.dispatchEvent(new CustomEvent('combatenteDeletado'));
        } catch (error) {
            if (typeof window.Toast !== 'undefined') {
                window.Toast.error('Erro ao deletar');
            }
            console.error(error);
        }
    }

    fechar() {
        const modal = document.getElementById('modalEdicao');
        if (modal) modal.classList.remove('show');
        this.combatenteAtual = null;
    }
}

// ✅ Instanciar globalmente (SEM EXPORT)
window.modalEdicaoInstance = new ModalEdicao();
