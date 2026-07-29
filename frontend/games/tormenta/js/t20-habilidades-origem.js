/**
 * Ações de origem na ficha: ativa habilidades, debita PM no backend e controla a cena.
 */
(function (global) {
    'use strict';

    let habilidades = [];
    let ocupada = false;

    function q(id) {
        return document.getElementById(id);
    }

    function esc(valor) {
        return String(valor == null ? '' : valor).replace(
            /[&<>"']/g,
            (c) =>
                ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[
                    c
                ]
        );
    }

    function personagemId() {
        return String((q('fichaId') && q('fichaId').value) || '').trim();
    }

    function chaveCena() {
        const id = personagemId();
        return id ? `t20:habilidades-origem:cena:${id}` : '';
    }

    function lerCena() {
        const chave = chaveCena();
        if (!chave) return {};
        try {
            const data = JSON.parse(global.localStorage.getItem(chave) || '{}');
            return data && typeof data === 'object' ? data : {};
        } catch (_e) {
            return {};
        }
    }

    function salvarCena(data) {
        const chave = chaveCena();
        if (!chave) return;
        try {
            global.localStorage.setItem(chave, JSON.stringify(data || {}));
        } catch (_e) {
            // A ação continua válida mesmo quando o navegador bloqueia localStorage.
        }
    }

    function eUmaVezPorCena(habilidade) {
        return String(habilidade.frequencia || '')
            .toLowerCase()
            .includes('cena');
    }

    function atualizarPm(atual, maximo) {
        const el = q('fichaPm');
        if (!el) return;
        const texto = `${atual} / ${maximo}`;
        if (el.matches('input, textarea')) el.value = texto;
        else el.textContent = texto;
        document.dispatchEvent(
            new CustomEvent('t20:pm-alterado', {
                detail: { pa_atual: atual, pa_max: maximo },
            })
        );
    }

    function estadoDa(habilidade, cena) {
        const uso = cena[habilidade.id] || null;
        return {
            uso,
            bloqueada: Boolean(uso && eUmaVezPorCena(habilidade)),
            ativa: Boolean(uso && String(habilidade.duracao || '').toLowerCase() === 'cena'),
        };
    }

    function cardHtml(habilidade, cena, fichaSalva) {
        const estado = estadoDa(habilidade, cena);
        const custo = Number(habilidade.custo_pm) || 0;
        const meta = [
            custo ? `${custo} PM` : 'Sem custo de PM',
            habilidade.frequencia || '',
            habilidade.duracao ? `duração: ${habilidade.duracao}` : '',
        ].filter(Boolean);
        const classeEstado = estado.ativa
            ? ' t20-habilidade-origem-card--ativa'
            : estado.bloqueada
              ? ' t20-habilidade-origem-card--usada'
              : '';
        const rotuloBotao = estado.ativa
            ? 'Ativa nesta cena'
            : estado.bloqueada
              ? 'Usada nesta cena'
              : custo
                ? `Ativar · ${custo} PM`
                : 'Usar habilidade';
        const origemPersistida = String(global.__t20OrigemPersistidaSlug || '');
        const origemAtual = String(habilidade.fonte_slug || '');
        const origemNaoSalva =
            Boolean(origemPersistida && origemAtual) && origemPersistida !== origemAtual;
        const desabilitada =
            ocupada || estado.bloqueada || estado.ativa || !fichaSalva || origemNaoSalva;
        const estadoHtml = estado.ativa
            ? '<span class="t20-habilidade-origem-status t20-habilidade-origem-status--ativa">Ativa</span>'
            : estado.bloqueada
              ? '<span class="t20-habilidade-origem-status">Usada</span>'
              : '';
        return (
            `<article class="t20-habilidade-origem-card${classeEstado}">` +
            '<div class="t20-habilidade-origem-card__conteudo">' +
            `<div class="t20-habilidade-origem-card__titulo"><strong>${esc(habilidade.nome)}</strong>${estadoHtml}</div>` +
            `<p>${esc(habilidade.resumo || '')}</p>` +
            `<div class="t20-habilidade-origem-card__meta">${meta.map((m) => `<span>${esc(m)}</span>`).join('')}</div>` +
            '</div>' +
            `<button type="button" class="tormenta-btn t20-habilidade-origem-ativar" data-habilidade-id="${esc(habilidade.id)}" ${desabilitada ? 'disabled' : ''}>${esc(rotuloBotao)}</button>` +
            '</article>'
        );
    }

    function render() {
        const wrap = q('t20HabilidadesOrigemWrap');
        const host = q('t20HabilidadesOrigemHost');
        if (!wrap || !host) return;
        const lista = habilidades.filter(
            (h) => h && h.tipo_ativo === 'habilidade_origem' && h.id
        );
        wrap.hidden = !lista.length;
        if (!lista.length) {
            host.innerHTML = '';
            return;
        }

        const fichaSalva = Boolean(personagemId());
        const origemAtual = String((lista[0] && lista[0].fonte_slug) || '');
        const origemPersistida = String(global.__t20OrigemPersistidaSlug || '');
        const origemNaoSalva =
            Boolean(origemAtual && origemPersistida) && origemAtual !== origemPersistida;
        const cena = lerCena();
        host.setAttribute('aria-busy', ocupada ? 'true' : 'false');
        host.innerHTML =
            lista.map((h) => cardHtml(h, cena, fichaSalva)).join('') +
            (!fichaSalva
                ? '<p class="t20-habilidade-origem-aviso">Salve a ficha para habilitar estas ações.</p>'
                : origemNaoSalva
                  ? '<p class="t20-habilidade-origem-aviso">Salve a nova origem antes de usar suas habilidades.</p>'
                : '');
        host.querySelectorAll('.t20-habilidade-origem-ativar').forEach((btn) => {
            btn.addEventListener('click', () => void ativar(btn.dataset.habilidadeId));
        });
    }

    async function ativar(habilidadeId) {
        if (ocupada) return;
        const habilidade = habilidades.find((h) => h.id === habilidadeId);
        const id = personagemId();
        if (!habilidade || !id) return;
        ocupada = true;
        render();
        try {
            const service = new TormentaPersonagemService();
            const resposta = await service.ativarHabilidadeOrigem(id, habilidadeId);
            atualizarPm(resposta.pa_atual_depois, resposta.pa_max);
            const cena = lerCena();
            cena[habilidadeId] = {
                usado_em: new Date().toISOString(),
                ativa: String(resposta.duracao || '').toLowerCase() === 'cena',
            };
            salvarCena(cena);
            if (global.Toast && global.Toast.success) {
                const saldo =
                    resposta.custo_pm > 0
                        ? ` −${resposta.custo_pm} PM; restam ${resposta.pa_atual_depois}/${resposta.pa_max}.`
                        : '';
                global.Toast.success(`${resposta.nome} usada.${saldo}`);
            }
        } catch (erro) {
            if (global.Toast && global.Toast.error) {
                global.Toast.error(erro.message || 'Não foi possível usar a habilidade.');
            }
        } finally {
            ocupada = false;
            render();
        }
    }

    function novaCena() {
        salvarCena({});
        render();
        if (global.Toast && global.Toast.success) {
            global.Toast.success('Nova cena iniciada: usos das habilidades foram liberados.');
        }
    }

    function init() {
        const btn = q('t20HabilidadesOrigemNovaCena');
        if (btn) btn.addEventListener('click', novaCena);
        document.addEventListener('t20:ficha-aplicada', () => {
            habilidades = [];
            render();
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    global.T20HabilidadesOrigem = {
        renderAtivos(ativos) {
            habilidades = Array.isArray(ativos) ? ativos.slice() : [];
            render();
        },
        novaCena,
    };
})(typeof window !== 'undefined' ? window : globalThis);
