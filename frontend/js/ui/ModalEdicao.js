/**
 * Componente de Modal de Edição
 * Princípio SOLID: Single Responsibility - gerenciar modal de edição
 */
import { CombatenteService } from '../services/CombatenteService.js';
import { UploadService } from '../services/UploadService.js';
import { Toast } from '../ui/Toast.js';
import { atualizarModificadorDOM } from '../utils/dnd.js';

export class ModalEdicao {
    constructor() {
        this.combatenteService = new CombatenteService();
        this.uploadService = new UploadService();
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
            if (this.combatenteAtual) {
                this.carregar(this.combatenteAtual.id);
            }
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
        const input = document.getElementById('editFoto');
        const area = document.getElementById('editUploadArea');
        const placeholder = document.getElementById('editUploadPlaceholder');
        const preview = document.getElementById('editUploadPreview');
        const previewImage = document.getElementById('editPreviewImage');

        if (!input || !area) return;

        area.addEventListener('click', () => input.click());

        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            try {
                this.uploadService.criarPreview(file, (dataUrl) => {
                    previewImage.src = dataUrl;
                    placeholder.style.display = 'none';
                    preview.style.display = 'block';
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

            // Identificação
            document.getElementById('editId').value = combatente.id;
            document.getElementById('editNome').value = combatente.nome;
            document.getElementById('editHP').value = combatente.hp_maximo;
            document.getElementById('editIniciativa').value = combatente.iniciativa;
            document.getElementById('editClasse').value = combatente.classe;
            document.getElementById('editTipo').value = combatente.tipo;
            document.getElementById('editNivel').value = combatente.nivel;
            document.getElementById('editPontos').value = combatente.pontos;

            // ✅ Defesa - CA, Toque, Surpresa
            document.getElementById('editCA').value = combatente.ca || 10;
            document.getElementById('editToque').value = combatente.toque || 10;
            document.getElementById('editSurpresa').value = combatente.surpresa || 10;

            // Atributos
            document.getElementById('editFOR').value = combatente.forca;
            document.getElementById('editDES').value = combatente.destreza;
            document.getElementById('editCON').value = combatente.constituicao;
            document.getElementById('editINT').value = combatente.inteligencia;
            document.getElementById('editSAB').value = combatente.sabedoria;
            document.getElementById('editCAR').value = combatente.carisma;

            // Resistências
            document.getElementById('editFortitude').value = combatente.fortitude || 0;
            document.getElementById('editReflexos').value = combatente.reflexos || 0;
            document.getElementById('editVontade').value = combatente.vontade || 0;

            // Atualizar modificadores
            ['editFOR', 'editDES', 'editCON', 'editINT', 'editSAB', 'editCAR'].forEach(id => {
                const input = document.getElementById(id);
                if (input) atualizarModificadorDOM(input);
            });

            // Preview de foto
            const placeholder = document.getElementById('editUploadPlaceholder');
            const preview = document.getElementById('editUploadPreview');
            const previewImage = document.getElementById('editPreviewImage');

            if (combatente.foto_url) {
                previewImage.src = combatente.foto_url;
                placeholder.style.display = 'none';
                preview.style.display = 'block';
            } else {
                placeholder.style.display = 'flex';
                preview.style.display = 'none';
            }

        } catch (error) {
            console.error('Erro ao carregar combatente:', error);
            throw error;
        }
    }

    async salvar(form) {
        try {
            const formData = new FormData(form);
            const id = parseInt(document.getElementById('editId').value);
            await this.combatenteService.atualizar(id, formData);
            Toast.success('Combatente atualizado! ✅');
            this.fechar();
            document.dispatchEvent(new CustomEvent('combatenteAtualizado'));
        } catch (error) {
            Toast.error(error.message || 'Erro ao atualizar');
            console.error(error);
        }
    }

    async deletar() {
        if (!this.combatenteAtual) return;
        if (!confirm(`Deseja realmente deletar ${this.combatenteAtual.nome}?`)) return;

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
}