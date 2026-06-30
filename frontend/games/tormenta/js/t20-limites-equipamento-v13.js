/**
 * Limites vestido/empunhado v1.3 — paridade com limites_equipamento_v13_t20.py (RF-T07h-1).
 */
(function (global) {
    'use strict';

    const MAX_VESTIDOS = 4;
    const MAX_EMPUNHADOS = 2;

    const COSMETICOS = new Set([
        'roupas de viajante',
        'roupas de plebeu',
        'traje de plebeu',
        'traje de sacerdote',
        'traje da corte',
        'traje estrangeiro',
        'uniforme militar',
    ]);

    function normNome(texto) {
        return String(texto || '')
            .normalize('NFD')
            .replace(/\p{M}/gu, '')
            .trim()
            .toLowerCase();
    }

    function normalizarTipo(tipo) {
        const t = String(tipo || '')
            .trim()
            .toLowerCase();
        if (t === 'média' || t === 'media') return 'media';
        if (t === 'leve' || t === 'pesada' || t === 'escudo' || t === 'arma') return t;
        return '';
    }

    function ataqueEmpunhadoMecanico(ataque) {
        if (!ataque || typeof ataque !== 'object') return false;
        if (ataque.empunhado !== true) return false;
        const nome = String(ataque.nome || '').trim();
        if (!nome) return false;
        const dano = String(ataque.dano || '').trim();
        const bonus = String(
            ataque.bonus_ataque != null ? ataque.bonus_ataque : ataque.teste || ''
        ).trim();
        return Boolean(dano || bonus);
    }

    function aplicarLimitesFicha(armaduras, ataques) {
        const outArm = [];
        const outAtq = [];
        let vestidos = 0;
        let empunhados = 0;

        (armaduras || []).forEach((raw) => {
            const it = Object.assign({}, raw || {});
            if (!itemBeneficioMecanico(it)) {
                if (it.bonus_ativo == null) it.bonus_ativo = true;
                outArm.push(it);
                return;
            }
            const slot = slotEquipamento(it);
            if (slot === 'vestido') {
                vestidos += 1;
                it.bonus_ativo = vestidos <= MAX_VESTIDOS;
            } else if (slot === 'empunhado') {
                empunhados += 1;
                it.bonus_ativo = empunhados <= MAX_EMPUNHADOS;
            } else if (it.bonus_ativo == null) {
                it.bonus_ativo = true;
            }
            outArm.push(it);
        });

        (ataques || []).forEach((raw) => {
            const atk = Object.assign({}, raw || {});
            if (ataqueEmpunhadoMecanico(atk)) {
                empunhados += 1;
                atk.bonus_ativo = empunhados <= MAX_EMPUNHADOS;
            } else {
                delete atk.bonus_ativo;
            }
            outAtq.push(atk);
        });

        return { armaduras: outArm, ataques: outAtq };
    }

    function resumoLimitesFicha(armaduras, ataques) {
        const aplicado = aplicarLimitesFicha(armaduras, ataques);
        const marcadosArm = aplicado.armaduras;
        const marcadosAtq = aplicado.ataques;
        const vestidos = marcadosArm.filter(
            (it) => slotEquipamento(it) === 'vestido' && itemBeneficioMecanico(it)
        ).length;
        const empunhados =
            marcadosArm.filter(
                (it) => slotEquipamento(it) === 'empunhado' && itemBeneficioMecanico(it)
            ).length +
            marcadosAtq.filter((atk) => ataqueEmpunhadoMecanico(atk)).length;
        const avisos = [];
        if (vestidos > MAX_VESTIDOS) {
            avisos.push(
                `Máximo ${MAX_VESTIDOS} itens vestidos com benefício — ` +
                    `${vestidos - MAX_VESTIDOS} excedente(s) não aplicam bônus.`
            );
        }
        if (empunhados > MAX_EMPUNHADOS) {
            avisos.push(
                `Máximo ${MAX_EMPUNHADOS} itens empunhados — ` +
                    `${empunhados - MAX_EMPUNHADOS} excedente(s) não aplicam bônus.`
            );
        }
        return {
            vestidos,
            empunhados,
            max_vestidos: MAX_VESTIDOS,
            max_empunhados: MAX_EMPUNHADOS,
            armaduras: marcadosArm,
            ataques: marcadosAtq,
            avisos,
        };
    }

    function slotEquipamento(item) {
        if (!item || typeof item !== 'object') return 'outro';
        if (item.empunhado === true || item.slot === 'empunhado') return 'empunhado';
        if (item.slot === 'vestido') return 'vestido';
        if (item.cosmetico === true) return 'cosmetico';
        const tipo = normalizarTipo(item.tipo);
        if (tipo === 'leve' || tipo === 'media' || tipo === 'pesada') return 'vestido';
        if (tipo === 'escudo' || tipo === 'arma') return 'empunhado';
        return 'outro';
    }

    function itemCosmetico(item) {
        if (!item || typeof item !== 'object') return false;
        if (item.cosmetico === true || item.beneficio_mecanico === false) return true;
        if (COSMETICOS.has(normNome(item.nome))) return true;
        return false;
    }

    function itemBeneficioMecanico(item) {
        if (!item || typeof item !== 'object' || itemCosmetico(item)) return false;
        const slot = slotEquipamento(item);
        if (slot !== 'vestido' && slot !== 'empunhado') return false;
        const bonus = Number(item.bonus_ca) || 0;
        const pen = Number(item.penalidade) || 0;
        if (bonus !== 0 || pen !== 0) return true;
        if (slot === 'empunhado' && (item.dano || item.bonus_ataque != null)) return true;
        return slot === 'vestido' || slot === 'empunhado';
    }

    function aplicarLimitesEquipamento(itens) {
        const out = [];
        let vestidos = 0;
        let empunhados = 0;
        (itens || []).forEach((raw) => {
            const it = Object.assign({}, raw || {});
            if (!itemBeneficioMecanico(it)) {
                if (it.bonus_ativo == null) it.bonus_ativo = true;
                out.push(it);
                return;
            }
            const slot = slotEquipamento(it);
            if (slot === 'vestido') {
                vestidos += 1;
                it.bonus_ativo = vestidos <= MAX_VESTIDOS;
            } else if (slot === 'empunhado') {
                empunhados += 1;
                it.bonus_ativo = empunhados <= MAX_EMPUNHADOS;
            } else if (it.bonus_ativo == null) {
                it.bonus_ativo = true;
            }
            out.push(it);
        });
        return out;
    }

    function resumoLimitesEquipamento(itens) {
        const marcados = aplicarLimitesEquipamento(itens);
        const vestidos = marcados.filter(
            (it) => slotEquipamento(it) === 'vestido' && itemBeneficioMecanico(it)
        ).length;
        const empunhados = marcados.filter(
            (it) => slotEquipamento(it) === 'empunhado' && itemBeneficioMecanico(it)
        ).length;
        const avisos = [];
        if (vestidos > MAX_VESTIDOS) {
            avisos.push(
                `Máximo ${MAX_VESTIDOS} itens vestidos com benefício — ` +
                    `${vestidos - MAX_VESTIDOS} excedente(s) não aplicam bônus.`
            );
        }
        if (empunhados > MAX_EMPUNHADOS) {
            avisos.push(
                `Máximo ${MAX_EMPUNHADOS} itens empunhados — ` +
                    `${empunhados - MAX_EMPUNHADOS} excedente(s) não aplicam bônus.`
            );
        }
        return {
            vestidos,
            empunhados,
            max_vestidos: MAX_VESTIDOS,
            max_empunhados: MAX_EMPUNHADOS,
            itens: marcados,
            avisos,
        };
    }

    function somaBonusCaAtivos(itens) {
        return aplicarLimitesEquipamento(itens).reduce((acc, it) => {
            if (it.bonus_ativo === false) return acc;
            return acc + (Number(it.bonus_ca) || 0);
        }, 0);
    }

    function somaBonusCaFicha(armaduras, ataques) {
        const aplicado = aplicarLimitesFicha(armaduras, ataques);
        return somaBonusCaAtivos(aplicado.armaduras);
    }

    function validarAdicionarEquipamento(itensAtuais, novoItem, ataques) {
        const lista = (itensAtuais || []).concat([novoItem || {}]);
        const res = resumoLimitesFicha(lista, ataques);
        return {
            permitir: true,
            slot: slotEquipamento(novoItem),
            resumo: res,
            aviso: res.avisos.length ? res.avisos[res.avisos.length - 1] : '',
        };
    }

    global.T20LimitesEquipamento = {
        MAX_VESTIDOS,
        MAX_EMPUNHADOS,
        slotEquipamento,
        ataqueEmpunhadoMecanico,
        aplicarLimitesEquipamento,
        aplicarLimitesFicha,
        resumoLimitesEquipamento,
        resumoLimitesFicha,
        somaBonusCaAtivos,
        somaBonusCaFicha,
        validarAdicionarEquipamento,
    };
})(typeof window !== 'undefined' ? window : globalThis);
