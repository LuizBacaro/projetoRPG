#!/usr/bin/env bash
# Extrai pp.150–209 do PDF licenciado MB e enriquece magias_mb_catalogo.json (G5).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PDF="${T20_MB_PDF:-$HOME/Downloads/tormenta-rpg-modulo-basico.pdf}"
OUT="$ROOT/backend/app/games/tormenta/data/sources/magias_mb_pp150-209.txt"
CATALOG="$ROOT/backend/app/games/tormenta/data/magias_mb_catalogo.json"

if [[ ! -f "$PDF" ]]; then
  echo "PDF não encontrado: $PDF (defina T20_MB_PDF)" >&2
  exit 1
fi

pdftotext -f 150 -l 209 "$PDF" "$OUT"
python3 "$ROOT/backend/scripts/enrich_magias_mb_catalogo.py" --detalhes "$OUT" "$CATALOG"
python3 "$ROOT/backend/scripts/check_magias_mb_catalogo.py"
