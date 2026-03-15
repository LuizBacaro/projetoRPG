/**
 * ============================================
 * PERICIA SERVICE - Camada de Serviço
 * Organiza todas as classes de perícias
 * Localização: frontend/services/PericiaService.js
 * ============================================
 */

/**
 * SkillStorageService - Gerencia persistência de dados
 * Single Responsibility: Apenas localStorage
 */
class SkillStorageService {
    constructor(prefix = 'skill') {
        this.prefix = prefix;
    }

    generateKey(skillId) {
        return `${this.prefix}_${skillId}`;
    }

    saveSkill(skillId, skillData) {
        try {
            const key = this.generateKey(skillId);
            localStorage.setItem(key, JSON.stringify(skillData));
            return true;
        } catch (error) {
            console.error(`Erro ao salvar perícia ${skillId}:`, error);
            return false;
        }
    }

    loadSkill(skillId) {
        try {
            const key = this.generateKey(skillId);
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error(`Erro ao carregar perícia ${skillId}:`, error);
            return null;
        }
    }

    removeSkill(skillId) {
        try {
            const key = this.generateKey(skillId);
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error(`Erro ao remover perícia ${skillId}:`, error);
            return false;
        }
    }

    clearAll() {
        try {
            const keys = Object.keys(localStorage).filter(key =>
                key.startsWith(this.prefix)
            );
            keys.forEach(key => localStorage.removeItem(key));
            return true;
        } catch (error) {
            console.error('Erro ao limpar todas as perícias:', error);
            return false;
        }
    }

    exportAll() {
        try {
            const keys = Object.keys(localStorage).filter(key =>
                key.startsWith(this.prefix)
            );
            const data = {};
            keys.forEach(key => {
                data[key] = JSON.parse(localStorage.getItem(key));
            });
            return data;
        } catch (error) {
            console.error('Erro ao exportar perícias:', error);
            return {};
        }
    }

    importAll(data) {
        try {
            Object.entries(data).forEach(([key, value]) => {
                localStorage.setItem(key, JSON.stringify(value));
            });
            return true;
        } catch (error) {
            console.error('Erro ao importar perícias:', error);
            return false;
        }
    }
}

/**
 * NotificationService - Gerencia notificações do usuário
 * Single Responsibility: Apenas notificações
 */
class NotificationService {
    static TYPES = {
        SUCCESS: 'success',
        ERROR: 'error',
        INFO: 'info',
        WARNING: 'warning'
    };

    static DURATION = {
        SHORT: 2000,
        NORMAL: 3000,
        LONG: 5000
    };

    static show(message, type = this.TYPES.INFO, duration = this.DURATION.NORMAL) {
        const container = document.getElementById('toast-container');
        if (!container) {
            console.warn('Toast container não encontrado');
            return;
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'polite');
        toast.textContent = message;

        container.appendChild(toast);

        toast.offsetHeight;
        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    static success(message, duration = this.DURATION.NORMAL) {
        this.show(message, this.TYPES.SUCCESS, duration);
    }

    static error(message, duration = this.DURATION.LONG) {
        this.show(message, this.TYPES.ERROR, duration);
    }

    static info(message, duration = this.DURATION.NORMAL) {
        this.show(message, this.TYPES.INFO, duration);
    }

    static warning(message, duration = this.DURATION.LONG) {
        this.show(message, this.TYPES.WARNING, duration);
    }
}

/**
 * ValidationService - Validação de inputs
 * Single Responsibility: Apenas validações
 */
class ValidationService {
    static RULES = {
        modifier: {
            min: -20,
            max: 20,
            message: 'Modificador deve ser um número entre -20 e 20'
        },
        bonus: {
            min: 0,
            max: 10,
            message: 'Bônus deve ser um número entre 0 e 10'
        }
    };

    static isValidInteger(value) {
        const num = parseInt(value);
        return !isNaN(num) && value !== '' && isFinite(num);
    }

    static isValidModifier(value) {
        if (!this.isValidInteger(value)) return false;
        const num = parseInt(value);
        const rule = this.RULES.modifier;
        return num >= rule.min && num <= rule.max;
    }

    static isValidBonus(value) {
        if (!this.isValidInteger(value)) return false;
        const num = parseInt(value);
        const rule = this.RULES.bonus;
        return num >= rule.min && num <= rule.max;
    }

    static getErrorMessage(fieldType) {
        return this.RULES[fieldType]?.message || 'Valor inválido';
    }

    static isValidSkillConfig(config) {
        return (
            config.nome &&
            config.atributo &&
            config.descricao &&
            config.cor &&
            typeof config.nome === 'string' &&
            typeof config.atributo === 'string' &&
            typeof config.descricao === 'string' &&
            typeof config.cor === 'string'
        );
    }
}

/**
 * SkillData - Modelo de dados de uma perícia
 * Single Responsibility: Representar dados de perícia
 */
class SkillData {
    constructor(id, config) {
        this.id = id;
        this.nome = config.nome;
        this.atributo = config.atributo;
        this.descricao = config.descricao;
        this.cor = config.cor;
        this.modificadorBase = config.modificadorBase || 0;
        this.bonusAdicional = config.bonusAdicional || 0;
    }

    calculateResult() {
        return this.modificadorBase + this.bonusAdicional;
    }

    toJSON() {
        return {
            modificadorBase: this.modificadorBase,
            bonusAdicional: this.bonusAdicional
        };
    }

    toFullJSON() {
        return {
            id: this.id,
            nome: this.nome,
            atributo: this.atributo,
            descricao: this.descricao,
            cor: this.cor,
            modificadorBase: this.modificadorBase,
            bonusAdicional: this.bonusAdicional,
            resultado: this.calculateResult()
        };
    }

    static fromJSON(id, config, savedData) {
        const skill = new SkillData(id, config);
        if (savedData) {
            skill.modificadorBase = savedData.modificadorBase || 0;
            skill.bonusAdicional = savedData.bonusAdicional || 0;
        }
        return skill;
    }

    reset() {
        this.modificadorBase = 0;
        this.bonusAdicional = 0;
    }
}

/**
 * SkillComponent - Componente de UI de uma perícia
 * Single Responsibility: Renderizar e gerenciar UI
 */
class SkillComponent {
    constructor(skillData, containerId, storageService) {
        this.skillData = skillData;
        this.containerId = containerId;
        this.storageService = storageService;
        this.container = document.getElementById(containerId);

        if (!this.container) {
            console.error(`Elemento com ID '${containerId}' não encontrado`);
            return;
        }

        this.loadData();
        this.render();
    }

    loadData() {
        const savedData = this.storageService.loadSkill(this.skillData.id);
        if (savedData) {
            this.skillData.modificadorBase = savedData.modificadorBase;
            this.skillData.bonusAdicional = savedData.bonusAdicional;
        }
    }

    saveData() {
        const success = this.storageService.saveSkill(
            this.skillData.id,
            this.skillData.toJSON()
        );
        if (!success) {
            NotificationService.error(`Erro ao salvar ${this.skillData.nome}`);
        }
    }

    render() {
        const resultado = this.skillData.calculateResult();
        const resultadoClass = resultado > 0 ? 'positivo' : resultado < 0 ? 'negativo' : 'neutro';

        this.container.innerHTML = `
            <div class="skill-card" style="border-left-color: ${this.skillData.cor}">
                <div class="skill-header">
                    <input 
                        type="radio" 
                        name="skill-select" 
                        id="select-${this.skillData.id}"
                        class="skill-radio"
                        aria-label="Selecionar ${this.skillData.nome}"
                    >
                    <label for="select-${this.skillData.id}" class="skill-nome">
                        ${this.skillData.nome}
                    </label>
                    <span class="skill-atributo">${this.skillData.atributo}</span>
                </div>

                <p class="skill-descricao">${this.skillData.descricao}</p>

                <div class="skill-inputs">
                    <div class="skill-input-group">
                        <label for="mod-base-${this.skillData.id}">Mod. Base</label>
                        <input 
                            type="number" 
                            id="mod-base-${this.skillData.id}"
                            class="skill-input-number"
                            value="${this.skillData.modificadorBase}"
                            min="-20"
                            max="20"
                            aria-label="Modificador base para ${this.skillData.nome}"
                        >
                    </div>

                    <div class="skill-input-group">
                        <label for="bonus-${this.skillData.id}">Bônus</label>
                        <input 
                            type="number" 
                            id="bonus-${this.skillData.id}"
                            class="skill-input-number"
                            value="${this.skillData.bonusAdicional}"
                            min="0"
                            max="10"
                            aria-label="Bônus adicional para ${this.skillData.nome}"
                        >
                    </div>

                    <div class="skill-resultado ${resultadoClass}" aria-label="Resultado total: ${resultado >= 0 ? '+' : ''}${resultado}">
                        <span class="label-resultado">Total</span>
                        <span class="valor-resultado">${resultado >= 0 ? '+' : ''}${resultado}</span>
                    </div>
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    attachEventListeners() {
        const inputModBase = this.container.querySelector(
            `#mod-base-${this.skillData.id}`
        );
        const inputBonus = this.container.querySelector(
            `#bonus-${this.skillData.id}`
        );

        if (inputModBase) inputModBase.addEventListener('change', (e) => this.handleModifierChange(e));
        if (inputBonus) inputBonus.addEventListener('change', (e) => this.handleBonusChange(e));
        if (inputModBase) inputModBase.addEventListener('input', (e) => this.handleModifierInput(e));
        if (inputBonus) inputBonus.addEventListener('input', (e) => this.handleBonusInput(e));
    }

    handleModifierChange(event) {
        const value = event.target.value;

        if (!ValidationService.isValidModifier(value)) {
            NotificationService.error(
                ValidationService.getErrorMessage('modifier')
            );
            event.target.value = this.skillData.modificadorBase;
            return;
        }

        this.skillData.modificadorBase = parseInt(value);
        this.saveData();
        this.render();
        NotificationService.success(`${this.skillData.nome} atualizado`);
    }

    handleModifierInput(event) {
        const value = event.target.value;
        if (ValidationService.isValidModifier(value)) {
            this.skillData.modificadorBase = parseInt(value);
            this.render();
        }
    }

    handleBonusChange(event) {
        const value = event.target.value;

        if (!ValidationService.isValidBonus(value)) {
            NotificationService.error(
                ValidationService.getErrorMessage('bonus')
            );
            event.target.value = this.skillData.bonusAdicional;
            return;
        }

        this.skillData.bonusAdicional = parseInt(value);
        this.saveData();
        this.render();
        NotificationService.success(`${this.skillData.nome} atualizado`);
    }

    handleBonusInput(event) {
        const value = event.target.value;
        if (ValidationService.isValidBonus(value)) {
            this.skillData.bonusAdicional = parseInt(value);
            this.render();
        }
    }

    getData() {
        return this.skillData.toFullJSON();
    }

    clear() {
        this.skillData.reset();
        this.saveData();
        this.render();
    }
}

/**
 * PericiaService - Orquestrador Central
 * Single Responsibility: Gerenciar ciclo de vida de perícias
 */
class PericiaService {
    constructor(storagePrefix = 'skill') {
        this.skills = new Map();
        this.storageService = new SkillStorageService(storagePrefix);
    }

    createSkill(id, config) {
        if (!ValidationService.isValidSkillConfig(config)) {
            NotificationService.error('Configuração de perícia inválida');
            return null;
        }

        const skillData = new SkillData(id, config);
        const containerId = `skill-${id}`;

        const skillComponent = new SkillComponent(
            skillData,
            containerId,
            this.storageService
        );

        this.skills.set(id, skillComponent);
        return skillComponent;
    }

    getSkill(id) {
        return this.skills.get(id);
    }

    getAllSkills() {
        const allSkills = [];
        this.skills.forEach((skillComponent) => {
            allSkills.push(skillComponent.getData());
        });
        return allSkills;
    }

    getSkillsByAttribute(attribute) {
        const filtered = [];
        this.skills.forEach((skillComponent) => {
            const data = skillComponent.getData();
            if (data.atributo === attribute) {
                filtered.push(data);
            }
        });
        return filtered;
    }

    getSkillsSorted(ascending = false) {
        const allSkills = this.getAllSkills();
        return allSkills.sort((a, b) => {
            return ascending 
                ? a.resultado - b.resultado 
                : b.resultado - a.resultado;
        });
    }

    getSkillsByMinResult(minResult) {
        const filtered = [];
        this.skills.forEach((skillComponent) => {
            const data = skillComponent.getData();
            if (data.resultado >= minResult) {
                filtered.push(data);
            }
        });
        return filtered.sort((a, b) => b.resultado - a.resultado);
    }

    getSkillsByMaxResult(maxResult) {
        const filtered = [];
        this.skills.forEach((skillComponent) => {
            const data = skillComponent.getData();
            if (data.resultado <= maxResult) {
                filtered.push(data);
            }
        });
        return filtered;
    }

    exportToJSON() {
        return {
            timestamp: new Date().toISOString(),
            version: '1.0',
            skills: this.getAllSkills()
        };
    }

    importFromJSON(data) {
        if (!data.skills || !Array.isArray(data.skills)) {
            NotificationService.error('Formato de importação inválido');
            return false;
        }

        try {
            data.skills.forEach(skillData => {
                this.storageService.saveSkill(skillData.id, {
                    modificadorBase: skillData.modificadorBase,
                    bonusAdicional: skillData.bonusAdicional
                });
            });
            NotificationService.success('Perícias importadas com sucesso');
            return true;
        } catch (error) {
            console.error('Erro ao importar perícias:', error);
            NotificationService.error('Erro ao importar perícias');
            return false;
        }
    }

    exportToFile() {
        const data = this.exportToJSON();
        const dataStr = JSON.stringify(data, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `pericias-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);
        NotificationService.success('Perícias exportadas para arquivo');
    }

    clearAllSkills() {
        this.storageService.clearAll();
        this.skills.forEach(skill => skill.clear());
        NotificationService.info('Todas as perícias foram limpas');
    }

    resetSkill(id) {
        const skill = this.getSkill(id);
        if (skill) {
            skill.clear();
            NotificationService.success('Perícia resetada');
        } else {
            NotificationService.error('Perícia não encontrada');
        }
    }

    getStats() {
        const allSkills = this.getAllSkills();
        const resultados = allSkills.map(s => s.resultado);
        
        return {
            total: allSkills.length,
            media: (resultados.reduce((a, b) => a + b, 0) / resultados.length).toFixed(2),
            maximo: Math.max(...resultados),
            minimo: Math.min(...resultados),
            positivas: resultados.filter(r => r > 0).length,
            negativas: resultados.filter(r => r < 0).length,
            neutras: resultados.filter(r => r === 0).length
        };
    }

    getTopSkill() {
        const allSkills = this.getAllSkills();
        return allSkills.length > 0 
            ? allSkills.reduce((a, b) => a.resultado > b.resultado ? a : b)
            : null;
    }

    getBottomSkill() {
        const allSkills = this.getAllSkills();
        return allSkills.length > 0 
            ? allSkills.reduce((a, b) => a.resultado < b.resultado ? a : b)
            : null;
    }
}