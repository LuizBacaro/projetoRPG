/**
 * Service de Combate (Business Logic + API Calls)
 * Princípio SOLID: Single Responsibility - apenas lógica de combate
 */
import { getApiUrl } from '../config/api.config.js';
import { Combate } from '../models/Combate.js';
import { Combatente } from '../models/Combatente.js';

export class CombateService {
    
    /**
     * Inicia um novo combate
     */
    async iniciar(combatenteIds) {
        try {
            const response = await fetch(`${getApiUrl('/combate')}/iniciar`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ combatente_ids: combatenteIds })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erro ao iniciar combate');
            }
            
            const data = await response.json();
            return this._parseCombateResponse(data);
        } catch (error) {
            console.error('Erro ao iniciar combate:', error);
            throw error;
        }
    }
    
    /**
     * Obtém o status do combate ativo
     */
    async obterStatus() {
        try {
            const response = await fetch(`${getApiUrl('/combate')}/status`);
            const data = await response.json();
            
            if (!data.ativo) {
                return null;
            }
            
            return this._parseCombateResponse(data);
        } catch (error) {
            console.error('Erro ao obter status:', error);
            throw error;
        }
    }
    
    /**
     * Avança para o próximo turno
     */
    async avancarTurno() {
        try {
            const response = await fetch(`${getApiUrl('/combate')}/avancar-turno`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erro ao avançar turno');
            }
            
            const data = await response.json();
            return this._parseCombateResponse(data);
        } catch (error) {
            console.error('Erro ao avançar turno:', error);
            throw error;
        }
    }
    
    /**
     * Aplica dano a um combatente
     */
    async aplicarDano(combatenteId, dano) {
        try {
            const response = await fetch(`${getApiUrl('/combate')}/aplicar-dano`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    combatente_id: combatenteId, 
                    dano: dano 
                })
            });
            
            if (!response.ok) {
                throw new Error('Erro ao aplicar dano');
            }
            
            const data = await response.json();
            return new Combatente(data);
        } catch (error) {
            console.error('Erro ao aplicar dano:', error);
            throw error;
        }
    }
    
    /**
     * Finaliza o combate ativo
     */
    async finalizar() {
        try {
            const response = await fetch(`${getApiUrl('/combate')}/finalizar`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error('Erro ao finalizar combate');
            }
            
            return true;
        } catch (error) {
            console.error('Erro ao finalizar combate:', error);
            throw error;
        }
    }
    
    /**
     * Reseta todos os combatentes
     */
    async resetar() {
        try {
            const response = await fetch(`${getApiUrl('/combate')}/resetar`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error('Erro ao resetar combate');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro ao resetar combate:', error);
            throw error;
        }
    }
    
    /**
     * Parser privado para converter response em objeto Combate
     */
    _parseCombateResponse(data) {
        const combate = new Combate(data);
        
        // Converter combatentes para instâncias da classe
        if (data.combatentes) {
            combate.combatentes = data.combatentes.map(c => new Combatente(c));
        }
        
        return combate;
    }
}