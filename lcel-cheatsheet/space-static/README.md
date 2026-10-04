---
title: LCEL Coding Cheatsheet
emoji: 🦜
colorFrom: yellow
colorTo: purple
sdk: static
short_description: Interactive LCEL reference for OpenAI and Anthropic
---

# LCEL Coding Cheatsheet

Interactive LangChain Expression Language coding reference for **OpenAI** (`ChatOpenAI`) and **Anthropic** (`ChatAnthropic`).

This Space is **static** (free). Hugging Face now requires a PRO plan to host new Gradio Spaces on `cpu-basic`. The same catalog also ships as a local Gradio app in the [GitHub repo](https://github.com/soumyajitsurai/RAG/tree/main/lcel-cheatsheet).

## Use it

1. Search or filter LCEL patterns.
2. Toggle **Both / OpenAI / Anthropic** to copy the matching snippet.
3. In Playground, run local Runnables in the browser or generate a ready-to-paste Python chain for `gpt-4o-mini` or Claude.

Live LLM calls need your own keys in a local Python session:

```bash
pip install langchain-openai langchain-anthropic langchain-core
export OPENAI_API_KEY=...
export ANTHROPIC_API_KEY=...
python
```
