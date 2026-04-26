/**
 * pericia-racial.js
 *
 * Utilitário para casar bônus raciais textuais (ex.: "+2 Observar", "+2 Procurar
 * (pedras e alvenaria)") com as perícias do catálogo, respeitando variações de
 * plural, especialização entre parênteses e sinônimos simples.
 *
 * Usado por `PericiaFichaController` (página de gerenciamento) e por
 * `FichaPersonagemController` (ficha em modo leitura) para que o valor exibido
 * e o total calculado fiquem sempre consistentes.
 */

function normalizarTexto(valor) {
    return String(valor || '')
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .replace(/[^a-z0-9() ]+/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}

export function normalizarNomePericiaLoose(valor) {
    const base = normalizarTexto(valor).replace(/\([^)]*\)/g, ' ').trim();
    return base
        .split(' ')
        .map((tok) => (tok.length > 4 && tok.endsWith('s') ? tok.slice(0, -1) : tok))
        .join(' ')
        .trim();
}

function parseLinhaBonusRacialPericia(linha) {
    const texto = String(linha || '').trim();
    if (!texto) return null;
    const m = texto.match(/^\s*\+?\s*(\d+)\s+(.+)$/);
    if (!m) return null;
    const bonus = parseInt(m[1], 10);
    if (!Number.isFinite(bonus) || bonus <= 0) return null;
    const rawNome = String(m[2] || '').trim();
    if (!rawNome) return null;
    const semParenteses = rawNome.replace(/\([^)]*\)/g, ' ').trim();
    return {
        bonus,
        alvoBase: normalizarNomePericiaLoose(semParenteses),
    };
}

function tokensSingularEquivalente(a, b) {
    if (!a || !b) return false;
    if (a === b) return true;
    if (a.length > 4 && a.endsWith('s') && a.slice(0, -1) === b) return true;
    if (b.length > 4 && b.endsWith('s') && b.slice(0, -1) === a) return true;
    return false;
}

/**
 * Match estrito entre o alvo declarado pela raça e o nome normalizado da
 * perícia, evitando falsos positivos por `includes`.
 */
export function matchAlvoPericia(alvoNorm, pNorm) {
    if (!alvoNorm || !pNorm) return false;
    const a = alvoNorm.replace(/-/g, ' ').replace(/\s+/g, ' ').trim();
    const b = pNorm.replace(/-/g, ' ').replace(/\s+/g, ' ').trim();
    if (a === b) return true;
    const pa = a.split(' ').filter(Boolean);
    const pb = b.split(' ').filter(Boolean);
    if (!pa.length || !pb.length) return false;
    if (pa.length === 1 && pb.length === 1) {
        return tokensSingularEquivalente(pa[0], pb[0]);
    }
    if (pa[0] !== pb[0] && !tokensSingularEquivalente(pa[0], pb[0])) {
        return false;
    }
    if (pb.length === 1 && pa.length >= 1) {
        return tokensSingularEquivalente(pa[0], pb[0]);
    }
    if (pa.length === 1 && pb.length >= 1) {
        return tokensSingularEquivalente(pa[0], pb[0]);
    }
    const restA = pa.slice(1).join(' ');
    const restB = pb.slice(1).join(' ');
    if (restA === restB) return true;
    if (restA.startsWith(restB) || restB.startsWith(restA)) return true;
    if (restA.length > 4 && restA.endsWith('s') && restA.slice(0, -1) === restB) return true;
    if (restB.length > 4 && restB.endsWith('s') && restB.slice(0, -1) === restA) return true;
    return false;
}

/**
 * Lista textual de bônus raciais aplicáveis a perícias, com fallback para
 * `passivos_raciais` quando `modificadores_pericia` estiver vazio.
 */
function fontesBonusRacial(combatente) {
    if (!combatente) return [];
    const primaria = Array.isArray(combatente.modificadores_pericia)
        ? combatente.modificadores_pericia
        : null;
    if (primaria && primaria.length) return primaria;
    return Array.isArray(combatente.passivos_raciais) ? combatente.passivos_raciais : [];
}

/**
 * Resolve o mapa `pericia_id → bonus_racial` a partir das descrições textuais
 * da raça e da lista de perícias disponíveis ao personagem.
 *
 * @param {object} combatente
 * @param {Array<{id:number, nome:string}>} pericias
 * @returns {Map<number, number>}
 */
export function resolverBonusRaciaisPorPericia(combatente, pericias) {
    const mapa = new Map();
    const fontes = fontesBonusRacial(combatente);
    if (!fontes.length || !Array.isArray(pericias) || !pericias.length) {
        return mapa;
    }

    const periciasNormalizadas = pericias.map((p) => ({
        id: p.id,
        nome: p.nome,
        normal: normalizarNomePericiaLoose(p.nome),
    }));

    for (const linha of fontes) {
        const parsed = parseLinhaBonusRacialPericia(linha);
        if (!parsed) continue;
        const alvo = parsed.alvoBase;
        if (!alvo) continue;

        const candidatos = periciasNormalizadas.filter((p) =>
            matchAlvoPericia(alvo, p.normal)
        );
        if (!candidatos.length) continue;

        for (const cand of candidatos) {
            mapa.set(cand.id, (mapa.get(cand.id) || 0) + parsed.bonus);
        }
    }
    return mapa;
}
