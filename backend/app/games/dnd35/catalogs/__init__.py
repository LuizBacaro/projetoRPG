"""Catálogos de referência do D&D 3.5.

Este pacote agrupa loaders de catálogos canônicos (raças, classes,
habilidades especiais, divindades oficiais, talentos…) que lêem dados
estáticos do PHB/Tomos a partir de JSONs gerados pelas planilhas em
`docs/dados/`.

São catálogos somente leitura, em memória (`lru_cache`), e sem
persistência em banco de dados próprio. Ficam aqui em
`app.games.dnd35.catalogs` por serem inerentemente regras D&D 3.5.

Imports de catálogo D&D 3.5 (incl. divindades oficiais) devem usar este pacote
(`app.games.dnd35.catalogs`). Normalização de nomes de classe para magias:
`app.games.dnd35.text_utils`. BBA, resistências de salvamento base e
habilidades especiais por nível: `app.games.dnd35.bonus_base_ataque` (módulo
irmão deste pacote, não dentro de `catalogs/`). Sincronização em lote no BD:
`app.games.dnd35.sync_progressao_combatentes`.
"""
