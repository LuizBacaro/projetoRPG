"""Catálogos de referência do D&D 3.5.

Este pacote agrupa loaders de catálogos canônicos (raças, classes,
habilidades especiais, divindades oficiais, talentos…) que lêem dados
estáticos do PHB/Tomos a partir de JSONs gerados pelas planilhas em
`docs/dados/`.

São catálogos somente leitura, em memória (`lru_cache`), e sem
persistência em banco de dados próprio. Ficam aqui em
`app.games.dnd35.catalogs` por serem inerentemente regras D&D 3.5.

Compatibilidade: enquanto os catálogos antigos em `app.core.*` forem
migrados, shims em `app.core/` re-exportam os símbolos (ex.:
`habilidades_especiais_catalog`, `racas_catalog`, `talentos_catalog_seed`).
"""
