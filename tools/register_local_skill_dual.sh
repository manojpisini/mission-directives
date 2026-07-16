#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
if command -v python3 >/dev/null 2>&1; then PYTHON=python3
elif command -v python >/dev/null 2>&1; then PYTHON=python
else printf 'Python 3 was not found on PATH.\n' >&2; exit 127
fi
printf '[----------] 0%% register skill\r' >&2
set +e
"$PYTHON" "$ROOT/tools/register_local_skill_dual.py" "$@"
CODE=$?
set -e
printf '[####################] 100%% %s\n' "$([[ $CODE -eq 0 ]] && echo pass || echo fail)" >&2
exit "$CODE"
