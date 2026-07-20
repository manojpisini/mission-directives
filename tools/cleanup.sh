#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if command -v python3 >/dev/null 2>&1; then PYTHON=python3
elif command -v python >/dev/null 2>&1; then PYTHON=python
else printf '[FAILURE] Python 3 was not found on PATH.\n' >&2; exit 127
fi
printf '[  0%%] Mission Directives cleanup\n'
set +e
"$PYTHON" "$SCRIPT_DIR/cleanup.py" "$@"
CODE=$?
set -e
printf '[100%%] Cleanup %s\n' "$([[ $CODE -eq 0 ]] && echo complete || echo failed)"
exit "$CODE"
