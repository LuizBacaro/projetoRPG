---
name: javascript-audit
description: Auditoria completa de JavaScript no projeto para identificar bugs, gargalos, riscos e oportunidades de melhoria com plano priorizado. Use quando precisar revisar o codigo JS de ponta a ponta e definir um roadmap tecnico.
license: Consulte LICENSE.txt para termos completos
---

# Skill de Auditoria JavaScript

Use esta skill para revisar todo o codigo JavaScript do projeto e gerar recomendacoes acionaveis.

## Resultado Esperado
- Diagnostico tecnico de qualidade, performance e seguranca.
- Lista de melhorias priorizadas por impacto x esforco.
- Plano por fases com risco e beneficio.

## Checklist de Revisao
1. Arquitetura e Organizacao
- Estrutura de pastas e modulos JS.
- Dependencias ciclicas e acoplamento indevido.
- Responsabilidades misturadas no mesmo arquivo.

2. Qualidade de Codigo
- Duplicacao de logica.
- Funcoes longas e complexidade elevada.
- Nomes pouco claros e falta de padrao.

3. Performance
- Loops e filtros custosos em fluxo frequente.
- Re-renderizacoes e recalculo desnecessario no frontend.
- Carga inicial e impacto de scripts no tempo de interacao.

4. Seguranca e Robustez
- Validacao de entradas no cliente e no servidor.
- Uso inseguro de dados em HTML/DOM.
- Tratamento de erro insuficiente e falhas silenciosas.

5. Testes e Confiabilidade
- Fluxos criticos sem testes.
- Casos de borda nao cobertos.
- Ausencia de testes de regressao em regras de negocio.

## Formato de Entrega
1. Resumo executivo (5-10 linhas)
2. Achados por severidade
- Critico
- Alto
- Medio
- Baixo
3. Plano de melhoria
- Fase 1: quick wins
- Fase 2: refatoracoes direcionadas
- Fase 3: melhorias estruturais
4. Proposta de testes para reduzir risco
5. Metricas para acompanhar evolucao

## Regra de Priorizacao
- Alto impacto + baixo esforco: executar primeiro.
- Alto impacto + alto esforco: quebrar em entregas menores.
- Baixo impacto + alto esforco: postergar.
