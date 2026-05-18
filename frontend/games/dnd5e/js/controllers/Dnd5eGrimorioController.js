/**
 * Grimório D&D 5e — estende o controller compartilhado com preview PT e metadados PHB.
 */
import { GrimorioController } from '/games/dnd35/js/controllers/GrimorioController.js?v=20260519a';
import { escapeHtml } from '/games/dnd35/js/utils/formatters.js';

export class Dnd5eGrimorioController extends GrimorioController {
    _ehModo5e() {
        return true;
    }

    _mapearItemGrimorio(item, extras = {}) {
        const mapped = super._mapearItemGrimorio(item, extras);
        const magiaDetalhada = this.catalogoIndex.get(Number(item.magia_id ?? item.id));
        const magia = mapped.magia || {};

        Object.assign(magia, {
            tempo_conjuracao:
                item.tempo_conjuracao || magiaDetalhada?.tempo_conjuracao || magia.tempo_conjuracao || '',
            alcance:
                item.alcance_texto ||
                item.alcance ||
                magiaDetalhada?.alcance_texto ||
                magiaDetalhada?.alcance ||
                magia.alcance ||
                '',
            duracao: item.duracao || magiaDetalhada?.duracao || magia.duracao || '',
            descricao_nivel_superior:
                item.descricao_nivel_superior ||
                magiaDetalhada?.descricao_nivel_superior ||
                magia.descricao_nivel_superior ||
                '',
            teste_resistencia:
                item.teste_resistencia || magiaDetalhada?.teste_resistencia || magia.teste_resistencia || '',
            ritual: !!(item.ritual ?? magiaDetalhada?.ritual ?? magia.ritual),
            material_consumido: !!(
                item.material_consumido ?? magiaDetalhada?.material_consumido ?? magia.material_consumido
            ),
            componentes_material:
                item.componentes_material ||
                magiaDetalhada?.componentes_material ||
                magia.componentes_material ||
                '',
            requer_concentracao: !!(
                item.requer_concentracao ??
                magiaDetalhada?.requer_concentracao ??
                magia.requer_concentracao
            ),
        });

        mapped.magia = magia;
        return mapped;
    }

    _teaserDescricaoPt(texto, max = 140) {
        const t = String(texto || '').trim();
        if (!t) return 'Sem descrição em português.';
        if (t.length <= max) return t;
        return `${t.slice(0, max).trimEnd()}…`;
    }

    _renderizarBadgesExtrasCard(magia) {
        const badges = [];
        if (magia.ritual) {
            badges.push('<span class="grimorio-badge grimorio-badge-ritual">Ritual</span>');
        }
        if (magia.material_consumido) {
            badges.push('<span class="grimorio-badge grimorio-badge-consumivel">Consumível</span>');
        }
        return badges.join('');
    }

    _renderizarLinhaDescricaoDetalhes(_magia) {
        return '';
    }

    _renderizarBlocoDescricaoCard(magia, aberta) {
        const desc = String(magia.descricao || '').trim();
        const up = String(magia.descricao_nivel_superior || '').trim();

        if (!aberta) {
            return `<p class="grimorio-card-descricao grimorio-descricao-teaser">${escapeHtml(this._teaserDescricaoPt(desc))}</p>`;
        }

        const badgesRegras = [];
        if (magia.requer_concentracao) {
            badgesRegras.push(
                '<span class="grimorio-badge grimorio-badge-concentracao">Concentração</span>'
            );
        }

        return `
            ${badgesRegras.length ? `<div class="grimorio-5e-badges-regras">${badgesRegras.join('')}</div>` : ''}
            <div class="grimorio-descricao-pt-preview">
                <p class="grimorio-descricao-pt-texto">${escapeHtml(desc || 'Sem descrição em português.')}</p>
                ${
                    up
                        ? `<div class="grimorio-descricao-pt-upcast">
                    <span class="grimorio-descricao-pt-subtitulo">Em círculos superiores</span>
                    <p class="grimorio-descricao-pt-texto">${escapeHtml(up)}</p>
                </div>`
                        : ''
                }
                ${
                    magia.componentes_material
                        ? `<p class="grimorio-descricao-pt-material"><strong>Material:</strong> ${escapeHtml(magia.componentes_material)}</p>`
                        : ''
                }
            </div>
        `;
    }
}
