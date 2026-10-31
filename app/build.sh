#!/usr/bin/env bash
# يبني app/hilal_map.html من القالب وبيانات اليابسة (Natural Earth 110m عبر world-atlas)
set -euo pipefail
cd "$(dirname "$0")"
python3 - <<'PY'
t = open('src/hilal_map.template.html', encoding='utf-8').read()
open('hilal_map.html', 'w', encoding='utf-8').write(t.replace('__LAND__', open('src/land.js', encoding='utf-8').read()))
PY
