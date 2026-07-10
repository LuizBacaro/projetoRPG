/**
 * RF-T12b — drag-and-drop do compendium (modais) para zonas da ficha Tormenta.
 * Reutiliza handlers registrados em window.__t20DndHandlers pela ficha-personagem.html.
 */
(function (global) {
    const MIME = 'application/x-t20-compendium';

    const CATALOG_LIST_IDS = {
        equipamentosLista: 'equip',
        talentosListaMb: 'talento',
        grimorioTormentaListaCatalogo: 'magia',
        consumiveisListaCatalogoMb: 'consumivel',
    };

    const DROP_ZONES = [
        { id: 'fichaEquipamentos', accept: ['equip'] },
        { id: 't20FichaTalentosMb', accept: ['talento'] },
        { id: 't20FichaConsumiveis', accept: ['consumivel'] },
        { id: 'grimorioTormentaListaVinculos', accept: ['magia'] },
        { id: 't20GrimorioDropZone', accept: ['magia'] },
    ];

    function decodeNome(enc) {
        if (!enc) return '';
        try {
            return decodeURIComponent(String(enc)).trim();
        } catch (_e) {
            return String(enc).trim();
        }
    }

    function readPapelMagia(art) {
        const h = global.__t20DndHandlers;
        if (h && typeof h.readPapelGrimorio === 'function') {
            return h.readPapelGrimorio(art);
        }
        const hid = art && art.querySelector('input.grimorio-papel-value');
        return (hid && hid.value) || 'conhecida';
    }

    function buildPayload(art, kind) {
        const payload = { kind: kind || art.getAttribute('data-dnd-kind') || '' };
        if (payload.kind === 'equip') {
            const btn = art.querySelector('[data-equip-add]');
            payload.nome = decodeNome(btn && btn.getAttribute('data-equip-add'));
            payload.catalogId =
                btn && btn.getAttribute('data-equip-catalog-id')
                    ? String(btn.getAttribute('data-equip-catalog-id'))
                    : '';
        } else if (payload.kind === 'talento') {
            const btn = art.querySelector('[data-tal-add]');
            payload.nome = decodeNome(btn && btn.getAttribute('data-tal-add'));
        } else if (payload.kind === 'magia') {
            const btn = art.querySelector('[data-grim-add]');
            const enc = (btn && btn.getAttribute('data-grim-add')) || art.getAttribute('data-grim-slug') || '';
            payload.slug = decodeNome(enc).toLowerCase();
            payload.papel = readPapelMagia(art);
        } else if (payload.kind === 'consumivel') {
            const btn = art.querySelector('[data-cons-add]');
            payload.nome = decodeNome(btn && btn.getAttribute('data-cons-add'));
        }
        return payload;
    }

    function parsePayload(dt) {
        const raw = dt.getData(MIME) || dt.getData('text/plain');
        if (!raw) return null;
        try {
            const p = JSON.parse(raw);
            return p && p.kind ? p : null;
        } catch (_e) {
            return null;
        }
    }

    function enhanceArticle(art, listaId) {
        if (!art || art.tagName !== 'ARTICLE') return;
        const kind = CATALOG_LIST_IDS[listaId] || '';
        if (!kind) return;
        art.setAttribute('draggable', 'true');
        art.classList.add('t20-dnd-source');
        art.setAttribute('data-dnd-kind', kind);
        if (kind === 'magia' && art.getAttribute('data-grim-slug')) {
            art.setAttribute('data-dnd-slug', art.getAttribute('data-grim-slug'));
        }
    }

    function scanCatalogList(lista) {
        if (!lista || !lista.id) return;
        lista.querySelectorAll('article.equipamento-catalogo-linha').forEach((art) => {
            enhanceArticle(art, lista.id);
        });
    }

    function bindCatalogList(listaId) {
        const lista = document.getElementById(listaId);
        if (!lista || lista.dataset.t20DndCatalogBound) return;
        lista.dataset.t20DndCatalogBound = '1';
        scanCatalogList(lista);

        const obs = new MutationObserver(() => scanCatalogList(lista));
        obs.observe(lista, { childList: true, subtree: true });

        lista.addEventListener('dragstart', (ev) => {
            const art = ev.target.closest('article.equipamento-catalogo-linha');
            if (!art || !lista.contains(art)) return;
            if (ev.target.closest('button, input, textarea, select, .grimorio-papel-segmented')) {
                ev.preventDefault();
                return;
            }
            enhanceArticle(art, listaId);
            const payload = buildPayload(art, CATALOG_LIST_IDS[listaId]);
            if (!payload.kind) {
                ev.preventDefault();
                return;
            }
            if (payload.kind === 'equip' && !payload.nome) {
                ev.preventDefault();
                return;
            }
            if (payload.kind === 'talento' && !payload.nome) {
                ev.preventDefault();
                return;
            }
            if (payload.kind === 'magia' && !payload.slug) {
                ev.preventDefault();
                return;
            }
            if (payload.kind === 'consumivel' && !payload.nome) {
                ev.preventDefault();
                return;
            }
            const json = JSON.stringify(payload);
            ev.dataTransfer.setData(MIME, json);
            ev.dataTransfer.setData('text/plain', json);
            ev.dataTransfer.effectAllowed = 'copy';
            art.classList.add('t20-dnd-source--dragging');
            global.__t20DndDragKind = payload.kind;
        });

        lista.addEventListener('dragend', (ev) => {
            const art = ev.target.closest('article.t20-dnd-source--dragging');
            if (art) art.classList.remove('t20-dnd-source--dragging');
            global.__t20DndDragKind = null;
            document.querySelectorAll('.t20-dnd-drop-zone--over').forEach((z) => {
                z.classList.remove('t20-dnd-drop-zone--over');
            });
        });
    }

    function zoneAccepts(zoneCfg, kind) {
        return kind && zoneCfg.accept.includes(kind);
    }

    function bindDropZone(cfg) {
        const el = document.getElementById(cfg.id);
        if (!el || el.dataset.t20DndDropBound) return;
        el.dataset.t20DndDropBound = '1';
        el.classList.add('t20-dnd-drop-zone');
        el.setAttribute('data-dnd-accept', cfg.accept.join(','));

        el.addEventListener('dragover', (ev) => {
            const kind = global.__t20DndDragKind;
            if (!zoneAccepts(cfg, kind)) return;
            ev.preventDefault();
            ev.dataTransfer.dropEffect = 'copy';
            el.classList.add('t20-dnd-drop-zone--over');
        });

        el.addEventListener('dragleave', (ev) => {
            if (ev.currentTarget.contains(ev.relatedTarget)) return;
            el.classList.remove('t20-dnd-drop-zone--over');
        });

        el.addEventListener('drop', async (ev) => {
            ev.preventDefault();
            el.classList.remove('t20-dnd-drop-zone--over');
            const payload = parsePayload(ev.dataTransfer);
            if (!payload || !zoneAccepts(cfg, payload.kind)) return;
            await executeDrop(payload);
        });
    }

    async function executeDrop(payload) {
        const h = global.__t20DndHandlers;
        if (!h) return;

        if (payload.kind === 'equip' && typeof h.addEquip === 'function') {
            const qtdEl = document.getElementById('equipamentosQuantidade');
            const qtd = qtdEl ? qtdEl.value : '1';
            await h.addEquip(payload.nome, qtd, payload.catalogId);
            if (typeof h.afterEquipDrop === 'function') h.afterEquipDrop();
            return;
        }

        if (payload.kind === 'talento' && typeof h.addTalento === 'function') {
            await h.addTalento(encodeURIComponent(payload.nome));
            if (typeof h.afterTalentoDrop === 'function') h.afterTalentoDrop();
            return;
        }

        if (payload.kind === 'consumivel' && typeof h.addConsumivel === 'function') {
            const qtdEl = document.getElementById('consumiveisTormentaQuantidade');
            const qtd = qtdEl ? qtdEl.value : '1';
            await h.addConsumivel(payload.nome, qtd);
            if (typeof h.afterConsumivelDrop === 'function') h.afterConsumivelDrop();
            return;
        }

        if (payload.kind === 'magia' && typeof h.addMagia === 'function') {
            await h.addMagia(payload.slug, payload.papel || 'conhecida');
            if (typeof h.afterMagiaDrop === 'function') await h.afterMagiaDrop();
        }
    }

    function triggerAddFromArticle(art) {
        const btn = art.querySelector(
            '[data-equip-add],[data-tal-add],[data-grim-add],[data-cons-add],[data-grim-troca-nova]'
        );
        if (btn && !btn.disabled) btn.click();
    }

    function bindDoubleClick() {
        if (global.__t20DndDblBound) return;
        global.__t20DndDblBound = true;
        document.addEventListener('dblclick', (ev) => {
            const art = ev.target.closest('article.equipamento-catalogo-linha');
            if (!art) return;
            const lista = art.closest('[id]');
            if (!lista || !CATALOG_LIST_IDS[lista.id]) return;
            if (ev.target.closest('button, input, textarea, select, .grimorio-papel-segment')) return;
            ev.preventDefault();
            triggerAddFromArticle(art);
        });
    }

    function init() {
        if (global.__t20CompendiumDndInit) return;
        global.__t20CompendiumDndInit = true;
        Object.keys(CATALOG_LIST_IDS).forEach(bindCatalogList);
        DROP_ZONES.forEach(bindDropZone);
        bindDoubleClick();
    }

    global.T20CompendiumDnd = { init };
})(typeof window !== 'undefined' ? window : globalThis);
