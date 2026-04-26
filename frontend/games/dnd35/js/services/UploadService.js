/**
 * Service de Upload (Gerenciamento de arquivos)
 * Princípio SOLID: Single Responsibility - apenas upload de arquivos
 */
export class UploadService {
    
    /**
     * Valida um arquivo de imagem
     */
    validarImagem(file) {
        const MAX_SIZE = 5 * 1024 * 1024; // 5MB
        const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        
        if (!file) {
            return { valid: false, error: 'Nenhum arquivo selecionado' };
        }
        
        if (!ALLOWED_TYPES.includes(file.type)) {
            return { 
                valid: false, 
                error: 'Formato inválido. Use JPG, PNG, GIF ou WebP' 
            };
        }
        
        if (file.size > MAX_SIZE) {
            return { 
                valid: false, 
                error: 'Arquivo muito grande. Máximo: 5MB' 
            };
        }
        
        return { valid: true };
    }
    
    /**
     * Cria preview de imagem
     */
    criarPreview(file, callback) {
        const validation = this.validarImagem(file);
        
        if (!validation.valid) {
            throw new Error(validation.error);
        }
        
        const reader = new FileReader();
        
        reader.onload = (e) => {
            callback(e.target.result);
        };
        
        reader.onerror = () => {
            throw new Error('Erro ao ler arquivo');
        };
        
        reader.readAsDataURL(file);
    }
}