#!/usr/bin/env bash
# Create or update the Hugging Face Space from this directory.
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

hf repos create "$SPACE_ID" --type space --space-sdk gradio --public --exist-ok
hf upload "$SPACE_ID" "$HERE" --type space \
  --commit-message "Deploy LCEL coding cheatsheet" \
  --exclude ".venv/**" \
  --exclude "__pycache__/**" \
  --exclude ".git/**" \
  --exclude "*.pyc"

echo
echo "Space: https://huggingface.co/spaces/${SPACE_ID}"
echo "Optional secrets: hf spaces secrets add ${SPACE_ID} --secrets OPENAI_API_KEY=\$OPENAI_API_KEY"
echo "                  hf spaces secrets add ${SPACE_ID} --secrets ANTHROPIC_API_KEY=\$ANTHROPIC_API_KEY"
echo "Logs: hf spaces logs ${SPACE_ID} --follow"
