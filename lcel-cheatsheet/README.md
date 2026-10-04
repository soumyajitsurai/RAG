---
title: LCEL Coding Cheatsheet
emoji: 🦜
colorFrom: yellow
colorTo: purple
sdk: gradio
sdk_version: 6.15.1
app_file: app.py
short_description: Interactive LCEL reference for OpenAI and Anthropic
python_version: "3.12"
---

# LCEL Coding Cheatsheet

Interactive LangChain Expression Language (LCEL) coding reference. Browse copy-paste snippets, run local Runnables without a key, and execute the same pipes against **OpenAI** or **Anthropic**.

## What you can do

- Search 20+ LCEL patterns: pipe, parallel, assign, bind, structured output, fallbacks, RAG, tools, history
- Toggle OpenAI vs Anthropic snippets (usually only the import and constructor change)
- Run a live playground (`prompt | model | parser`, streaming, parallel, structured output, fake-retriever RAG, OpenAI↔Anthropic fallbacks)
- Compare both providers on the same prompt

## Keys

The cheatsheet itself needs no keys. Live LLM patterns need one of:

1. Paste `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` in the **API keys** accordion, or
2. Add those names as Hugging Face Space **secrets**

Keys are used only to construct `ChatOpenAI` / `ChatAnthropic` and are not written to disk.

## Local run

```bash
cd lcel-cheatsheet
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install gradio
export OPENAI_API_KEY=...          # optional
export ANTHROPIC_API_KEY=...       # optional
python app.py
```

## Space deploy

```bash
hf repos create <namespace>/lcel-coding-cheatsheet --type space --space-sdk gradio --public
hf upload <namespace>/lcel-coding-cheatsheet . --type space
```

Use **cpu-basic** hardware. This Space is an API-proxy / reference app, not a local GPU model.
