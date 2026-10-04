#!/usr/bin/env bash
# Publish the static LCEL cheatsheet Space.
# New Gradio cpu-basic Spaces require a PRO plan; static Spaces are free.
# Requires: hf auth login  (write token)   https://huggingface.co/settings/tokens
set -euo pipefail

SPACE_ID="${SPACE_ID:-soumya-ai/lcel-coding-cheatsheet}"
HERE="$(cd "$(dirname "$0")" && pwd)"

if ! command -v hf >/dev/null 2>&1; then
  echo "Install the Hub CLI: pip install -U huggingface_hub" >&2
  exit 1
fi

if ! hf auth whoami >/dev/null 2>&1; then
  echo "Not logged in. Run: hf auth login" >&2
  echo "Create a write token at https://huggingface.co/settings/tokens" >&2
  exit 1
fi

python3 "$HERE/export_catalog.py"
hf repos create "$SPACE_ID" --type space --space-sdk static --public --exist-ok
hf upload "$SPACE_ID" "$HERE/space-static" --type space \
  --commit-message "Deploy LCEL coding cheatsheet"

echo
echo "Hub:    https://huggingface.co/spaces/${SPACE_ID}"
echo "Direct: https://${SPACE_ID/\//-}.static.hf.space/"
