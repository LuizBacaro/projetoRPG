/**
 * Relíquias — itens mágicos HA em área separada do inventário.
 */
(function (global) {
    'use strict';

    let reliquias = [];

    function q(id) {
        return document.getElementById(id);
    }

    function renderLista() {
        const host = q('fichaReliquias');
        if (!host) return;
        if (!reliquias.length) {
            host.innerHTML = '<span class="ficha-vazio">Nenhuma relíquia cadastrada</span>';
            return;
        }
        host.innerHTML = reliquias
            .map((r, i) => {
                const nome = String(r.nome || '').trim() || 'Relíquia';
                const resumo = String(r.efeito_resumo || r.descricao_resumo || '').trim();
                return `<div class="ficha-equipamento-linha t20-reliquia-linha" data-idx="${i}">
          <input type="text" class="t20-reliquia-nome" value="${nome.replace(/"/g, '&quot;')}" placeholder="Nome" />
          <input type="text" class="t20-reliquia-resumo" value="${resumo.replace(/"/g, '&quot;')}" placeholder="Efeito (resumo)" />
          <button type="button" class="tormenta-btn tormenta-btn--ghost t20-reliquia-rem" title="Remover">✕</button>
        </div>`;
            })
            .join('');
        host.querySelectorAll('.t20-reliquia-rem').forEach((btn) => {
            btn.addEventListener('click', () => {
                const row = btn.closest('.t20-reliquia-linha');
                const idx = parseInt(row && row.dataset.idx, 10);
                if (Number.isFinite(idx)) {
                    reliquias.splice(idx, 1);
                    renderLista();
                    if (global.T20EfeitosFicha) global.T20EfeitosFicha.atualizarDebounced();
                }
            });
        });
        host.querySelectorAll('.t20-reliquia-nome, .t20-reliquia-resumo').forEach((inp) => {
            inp.addEventListener('change', sincronizarDoDom);
            inp.addEventListener('input', sincronizarDoDom);
        });
    }

    function sincronizarDoDom() {
        const host = q('fichaReliquias');
        if (!host) return;
        reliquias = [];
        host.querySelectorAll('.t20-reliquia-linha').forEach((row) => {
            const nome = row.querySelector('.t20-reliquia-nome');
            const res = row.querySelector('.t20-reliquia-resumo');
            reliquias.push({
                nome: (nome && nome.value) || '',
                efeito_resumo: (res && res.value) || '',
            });
        });
        if (global.T20EfeitosFicha) global.T20EfeitosFicha.atualizarDebounced();
    }

    function adicionar(item) {
        reliquias.push({
            nome: String((item && item.nome) || '').trim() || 'Relíquia',
            efeito_resumo: String(
                (item && item.descricao_resumo) || (item && item.efeito_resumo) || ''
            ).trim(),
            slug: item && item.slug,
        });
        renderLista();
        if (global.T20EfeitosFicha) global.T20EfeitosFicha.atualizarDebounced();
    }

    function lerLista() {
        sincronizarDoDom();
        return reliquias.slice();
    }

    function aplicarLista(lista) {
        reliquias = Array.isArray(lista)
            ? lista.map((r) => ({
                  nome: String(r.nome || '').trim(),
                  efeito_resumo: String(r.efeito_resumo || r.descricao_resumo || '').trim(),
                  slug: r.slug,
              }))
            : [];
        renderLista();
    }

    async function abrirCatalogo() {
        const svc = new TormentaRegrasService();
        try {
            const data = await svc.listarReliquias({ limit: 50 });
            const itens = (data && data.itens) || [];
            if (!itens.length) {
                adicionar({ nome: 'Relíquia personalizada' });
                return;
            }
            const nome = itens[0].nome;
            const pick = itens.find((x) => x.nome === nome) || itens[0];
            adicionar(pick);
        } catch (_e) {
            adicionar({ nome: 'Relíquia personalizada' });
        }
    }

    function init() {
        const btn = q('btnAdicionarReliquia');
        if (btn) btn.addEventListener('click', () => abrirCatalogo());
        renderLista();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    global.T20ReliquiasFicha = {
        lerLista,
        aplicarLista,
        adicionar,
        renderLista,
    };
})(typeof window !== 'undefined' ? window : globalThis);
