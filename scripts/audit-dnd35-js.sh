#!/usr/bin/env bash
# Auditoria estática leve do bundle D&D 3.5 JS (sem node_modules).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JS_DIR="$ROOT/frontend/games/dnd35/js"
ERR=0

echo "== Arena: auditoria dnd35/js =="

if [[ ! -d "$JS_DIR" ]]; then
  echo "ERRO: pasta não encontrada: $JS_DIR"
  exit 1
fi

# 1) URLs localhost hardcoded (produção quebra)
if grep -rEn "localhost:8000|127\.0\.0\.1:8000" "$JS_DIR" --include='*.js' 2>/dev/null | grep -q .; then
  grep -rEn "localhost:8000|127\.0\.0\.1:8000" "$JS_DIR" --include='*.js' 2>/dev/null || true
  echo "FALHA: URL localhost hardcoded em dnd35/js (usar getApiUrl / api.config.js)"
  ERR=1
else
  echo "OK: sem localhost hardcoded"
fi

# 2) fetch( sem getApiUrl no mesmo ficheiro — heurística
BAD_FETCH=0
while IFS= read -r f; do
  if grep -qE 'fetch\s*\(' "$f" && ! grep -q 'getApiUrl' "$f"; then
    echo "AVISO: fetch sem getApiUrl visível: ${f#$ROOT/}"
    BAD_FETCH=$((BAD_FETCH + 1))
  fi
done < <(find "$JS_DIR" -name '*.js' -type f)
if [[ "$BAD_FETCH" -gt 5 ]]; then
  echo "AVISO: $BAD_FETCH ficheiros com fetch — rever manualmente"
fi

# 3) config.js legado não deve voltar
if [[ -f "$JS_DIR/config.js" ]]; then
  echo "FALHA: config.js legado ainda presente (remover; usar api.config.js)"
  ERR=1
else
  echo "OK: config.js legado ausente"
fi

# 4) Ficheiros gigantes (>2500 linhas)
while IFS= read -r f; do
  n=$(wc -l < "$f" | tr -d ' ')
  if [[ "$n" -ge 2500 ]]; then
    echo "AVISO: ficheiro grande — ${n} linhas em ${f#$ROOT/}"
  fi
done < <(find "$JS_DIR" -name '*.js' -type f)

# 5) innerHTML sem escapeHtml no mesmo ficheiro (heurística)
RISKY=0
while IFS= read -r f; do
  if grep -q 'innerHTML' "$f" && ! grep -q 'escapeHtml' "$f"; then
    echo "AVISO: innerHTML sem escapeHtml no ficheiro: ${f#$ROOT/}"
    RISKY=$((RISKY + 1))
  fi
done < <(find "$JS_DIR" -name '*.js' -type f)
echo "Ficheiros com innerHTML e sem referência escapeHtml: $RISKY (ver docs/dnd35-js-auditoria-2026-06.md)"

if [[ "$ERR" -ne 0 ]]; then
  exit 1
fi
echo "== Auditoria concluída (avisos não falham o script) =="
