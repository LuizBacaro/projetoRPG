/**
 * Service de Combatente (Business Logic + API Calls)
 * Princípio SOLID: Single Responsibility - apenas lógica de combatente
 */
import { getApiUrl } from '../config/api.config.js';
import { Combatente } from '../models/Combatente.js';

export class CombatenteService {
    
    /**
     * Lista todos os combatentes ou filtra por tipo
     */
    async listar(tipo = null) {
        try {
            const url = tipo 
                ? `${getApiUrl('/combatentes')}?tipo=${tipo}`
                : getApiUrl('/combatentes');
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error('Erro ao carregar combatentes');
            }
            
            const data = await response.json();
            return data.map(c => new Combatente(c));
        } catch (error) {
            console.error('Erro ao listar combatentes:', error);
            throw error;
        }
    }
    
    /**
     * Obtém um combatente por ID
     */
    async obterPorId(id) {
        try {
            const response = await fetch(`${getApiUrl('/combatentes')}/${id}`);
            
            if (!response.ok) {
                throw new Error('Combatente não encontrado');
            }
            
            const data = await response.json();
            return new Combatente(data);
        } catch (error) {
            console.error('Erro ao obter combatente:', error);
            throw error;
        }
    }
    
    /**
     * Cria um novo combatente
     */
    async criar(formData) {
        try {
            const response = await fetch(getApiUrl('/combatentes'), {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erro ao criar combatente');
            }
            
            const data = await response.json();
            return new Combatente(data);
        } catch (error) {
            console.error('Erro ao criar combatente:', error);
            throw error;
        }
    }
    
    /**
     * Atualiza um combatente
     */
    async atualizar(id, formData) {
        try {
            const response = await fetch(`${getApiUrl('/combatentes')}/${id}`, {
                method: 'PUT',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erro ao atualizar combatente');
            }
            
            const data = await response.json();
            return new Combatente(data);
        } catch (error) {
            console.error('Erro ao atualizar combatente:', error);
            throw error;
        }
    }
    
    /**
     * Atualiza apenas o HP de um combatente
     */
    async atualizarHP(id, hpAtual) {
        try {
            const response = await fetch(`${getApiUrl('/combatentes')}/${id}/hp`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ hp_atual: parseInt(hpAtual) })
            });
            
            if (!response.ok) {
                throw new Error('Erro ao atualizar HP');
            }
            
            const data = await response.json();
            return new Combatente(data);
        } catch (error) {
            console.error('Erro ao atualizar HP:', error);
            throw error;
        }
    }
    
    /**
     * Atualiza apenas a iniciativa de um combatente
     */
    async atualizarIniciativa(id, iniciativa) {
        try {
            const response = await fetch(`${getApiUrl('/combatentes')}/${id}/iniciativa`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ iniciativa: parseInt(iniciativa) })
            });
            
            if (!response.ok) {
                throw new Error('Erro ao atualizar iniciativa');
            }
            
            const data = await response.json();
            return new Combatente(data);
        } catch (error) {
            console.error('Erro ao atualizar iniciativa:', error);
            throw error;
        }
    }
    
    /**
     * Deleta um combatente
     */
    async deletar(id) {
        try {
            const response = await fetch(`${getApiUrl('/combatentes')}/${id}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Erro ao deletar combatente');
            }
            
            return true;
        } catch (error) {
            console.error('Erro ao deletar combatente:', error);
            throw error;
        }
    }
}