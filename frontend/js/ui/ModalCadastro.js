/**
 * Componente de Modal de Cadastro
 * Princípio SOLID: Single Responsibility - gerenciar modais de cadastro
 */
import { CombatenteService } from '../services/CombatenteService.js';
import { UploadService } from '../services/UploadService.js';
import { Toast } from './toast.module.js';
import { atualizarModificadorDOM } from '../utils/dnd.js';

export class ModalCadastro {
    
    constructor(tipo) {
        this.tipo = tipo; // 'jogador', 'monstro', 'npc'
        this.combatenteService = new CombatenteService();
        this.uploadService = new UploadService();
        
        // ← CORREÇÃO: Tratar NPC de forma especial
        if (tipo === 'jogador') {
            this.modalId = 'modalCadastro';
            this.formId = 'formCadastroJogador';
        } else if (tipo === 'monstro') {
            this.modalId = 'modalCadastroMonstro';
            this.formId = 'formCadastroMonstro';
        } else if (tipo === 'npc') {
            this.modalId = 'modalCadastroNPC'; // ← NPC todo maiúsculo
            this.formId = 'formCadastroNPC';   // ← NPC todo maiúsculo
        }
        
            modalId: this.modalId,
            formId: this.formId
        });
        
        this.inicializar();
    }
    
    /**
     * Inicializa o modal
     */
    inicializar() {
        this.configurarFormulario();
        this.configurarUpload();
    }
    
    /**
     * Configura submit do formulário
     */
    configurarFormulario() {
        const form = document.getElementById(this.formId);
        
        if (!form) {
            console.error(`❌ Formulário não encontrado: ${this.formId}`);
            return;
        }
        
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.cadastrar(form);
        });
    }
    
    /**
     * Configura upload de imagem
     */
    configurarUpload() {
        const sufixo = this.getSufixo();
        const inputId = `inputFoto${sufixo}`;
        const areaId = `uploadArea${sufixo}`;
        const placeholderId = `uploadPlaceholder${sufixo}`;
        const previewId = `uploadPreview${sufixo}`;
        const previewImageId = `previewImage${sufixo}`;
        
        const input = document.getElementById(inputId);
        const area = document.getElementById(areaId);
        const placeholder = document.getElementById(placeholderId);
        const preview = document.getElementById(previewId);
        const previewImage = document.getElementById(previewImageId);
        
        if (!input || !area) {
            console.warn(`⚠️ Elementos de upload não encontrados para ${this.tipo}`);
            return;
        }
        
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
     * Cadastra um novo combatente
     */
    async cadastrar(form) {
        try {
            const formData = new FormData(form);
            
            const combatente = await this.combatenteService.criar(formData);
            
            Toast.success(`${combatente.nome} cadastrado com sucesso!`);
            
            this.fechar();
            this.limparFormulario(form);
            
            // Disparar evento para recarregar lista
            document.dispatchEvent(new CustomEvent('combatenteCriado'));
            
        } catch (error) {
            Toast.error(error.message || 'Erro ao cadastrar');
            console.error(error);
        }
    }
    
    /**
     * Abre o modal
     */
    abrir() {
        const modal = document.getElementById(this.modalId);
        
        if (modal) {
            modal.classList.add('show');
        } else {
            console.error(`❌ Modal não encontrado: ${this.modalId}`);
        }
    }
    
    /**
     * Fecha o modal
     */
    fechar() {
        const modal = document.getElementById(this.modalId);
        if (modal) {
            modal.classList.remove('show');
        }
    }
    
    /**
     * Limpa o formulário
     */
    limparFormulario(form) {
        form.reset();
        
        // Resetar preview de imagem
        const sufixo = this.getSufixo();
        const placeholder = document.getElementById(`uploadPlaceholder${sufixo}`);
        const preview = document.getElementById(`uploadPreview${sufixo}`);
        
        if (placeholder && preview) {
            placeholder.style.display = 'flex';
            preview.style.display = 'none';
        }
        
        // Resetar modificadores para +0
        form.querySelectorAll('.atributo-modificador').forEach(span => {
            span.textContent = '+0';
        });
    }
    
    /**
     * ← NOVO: Retorna sufixo correto para IDs de elementos
     */
    getSufixo() {
        if (this.tipo === 'jogador') return '';
        if (this.tipo === 'monstro') return 'Monstro';
        if (this.tipo === 'npc') return 'NPC'; // ← NPC todo maiúsculo
        return '';
    }
    
    /**
     * Capitaliza primeira letra (mantido para compatibilidade)
     */
    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}