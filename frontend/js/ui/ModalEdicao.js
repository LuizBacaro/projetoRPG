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
    
    /**
     * Inicializa o modal
     */
    inicializar() {
        this.configurarEventos();
        this.configurarFormulario();
        this.configurarUpload();
    }
    
    /**
     * Configura eventos customizados
     */
    configurarEventos() {
        // Evento: abrir edição
        document.addEventListener('abrirEdicao', async (e) => {
            await this.abrir(e.detail.id);
        });
        
        // Evento: combatente criado (recarregar se modal aberto)
        document.addEventListener('combatenteCriado', () => {
            if (this.combatenteAtual) {
                this.carregar(this.combatenteAtual.id);
            }
        });
    }
    
    /**
     * Configura submit do formulário
     */
    configurarFormulario() {
        const form = document.getElementById('formEdicaoCombatente');
        
        if (!form) return;
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.salvar(form);
        });
    }
    
    /**
     * Configura upload de imagem
     */
    configurarUpload() {
        const input = document.getElementById('editFoto');
        const area = document.getElementById('editUploadArea');
        const placeholder = document.getElementById('editUploadPlaceholder');
        const preview = document.getElementById('editUploadPreview');
        const previewImage = document.getElementById('editPreviewImage');
        
        if (!input || !area) return;
        
        // Clique na área abre seletor
        area.addEventListener('click', () => input.click());
        
        // Quando arquivo selecionado
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
    
    /**
     * Abre o modal para editar um combatente
     */
    async abrir(combatenteId) {
        try {
            await this.carregar(combatenteId);
            
            const modal = document.getElementById('modalEdicao');
            if (modal) {
                modal.classList.add('show');
            }
        } catch (error) {
            Toast.error('Erro ao carregar combatente');
            console.error(error);
        }
    }
    
    /**
     * Carrega dados do combatente no formulário
     */
    async carregar(combatenteId) {
        try {
            const combatente = await this.combatenteService.obterPorId(combatenteId);
            this.combatenteAtual = combatente;
            
            // Preencher campos
            document.getElementById('editId').value = combatente.id;
            document.getElementById('editNome').value = combatente.nome;
            document.getElementById('editHP').value = combatente.hp_maximo;
            document.getElementById('editIniciativa').value = combatente.iniciativa;
            document.getElementById('editClasse').value = combatente.classe;
            document.getElementById('editTipo').value = combatente.tipo;
            document.getElementById('editNivel').value = combatente.nivel;
            document.getElementById('editPontos').value = combatente.pontos;
            
            // Atributos
            document.getElementById('editFOR').value = combatente.forca;
            document.getElementById('editDES').value = combatente.destreza;
            document.getElementById('editCON').value = combatente.constituicao;
            document.getElementById('editINT').value = combatente.inteligencia;
            document.getElementById('editSAB').value = combatente.sabedoria;
            document.getElementById('editCAR').value = combatente.carisma;
            
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
    
    /**
     * Salva as alterações
     */
    async salvar(form) {
        try {
            const formData = new FormData(form);
            const id = parseInt(document.getElementById('editId').value);
            
            await this.combatenteService.atualizar(id, formData);
            
            Toast.success('Combatente atualizado!');
            
            this.fechar();
            
            // Disparar evento para recarregar lista
            document.dispatchEvent(new CustomEvent('combatenteAtualizado'));
            
        } catch (error) {
            Toast.error(error.message || 'Erro ao atualizar');
            console.error(error);
        }
    }
    
    /**
     * Deleta o combatente
     */
    async deletar() {
        if (!this.combatenteAtual) return;
        
        if (!confirm(`Deseja realmente deletar ${this.combatenteAtual.nome}?`)) {
            return;
        }
        
        try {
            await this.combatenteService.deletar(this.combatenteAtual.id);
            
            Toast.success('Combatente deletado!');
            
            this.fechar();
            
            // Disparar evento para recarregar lista
            document.dispatchEvent(new CustomEvent('combatenteDeletado'));
            
        } catch (error) {
            Toast.error('Erro ao deletar');
            console.error(error);
        }
    }
    
    /**
     * Fecha o modal
     */
    fechar() {
        const modal = document.getElementById('modalEdicao');
        if (modal) {
            modal.classList.remove('show');
        }
        this.combatenteAtual = null;
    }
}