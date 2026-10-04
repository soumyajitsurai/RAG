"""LCEL coding cheatsheet — Gradio app for Hugging Face Spaces."""

from __future__ import annotations

import gradio as gr

from catalog import (
    CATEGORIES,
    ENTRIES,
    QUICK_REF,
    entry_from_label,
    filter_entries,
    titles_for,
)
from playground import (
    ALL_PATTERNS,
    ANTHROPIC_MODELS,
    LOCAL_PATTERNS,
    OPENAI_MODELS,
    compare_providers,
    run_pattern,
)

CSS = """
#col-container { max-width: 1180px; margin: 0 auto; }
.dark .gradio-container { color: var(--body-text-color); }
#hero h1 { letter-spacing: -0.03em; }
#quick-table table { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.92rem; }
"""

INTRO = """
# LCEL Coding Cheatsheet
Interactive **LangChain Expression Language** reference for **OpenAI** and **Anthropic**.

Same pipe (`|`), same `invoke` / `stream` / `batch`. Swap `ChatOpenAI` ↔ `ChatAnthropic` (or `init_chat_model`) and keep the graph.

Keys stay in this browser session unless you set Space secrets `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`. They are never written to disk.
"""


def _format_entry(entry: dict | None, provider_view: str) -> tuple[str, str, str, str]:
    if not entry:
        return "No match.", "", "", ""
    meta = (
        f"### {entry['title']}\n\n"
        f"**Category:** {entry['category']}  ·  **Tags:** {', '.join(entry['tags'])}\n\n"
        f"{entry['summary']}\n\n"
        f"**When to use:** {entry['when']}\n\n"
        f"**Notes:** {entry['notes']}"
    )
    openai_code = entry["openai"]
    anthropic_code = entry["anthropic"]
    if provider_view == "OpenAI":
        shown = openai_code
        other = ""
    elif provider_view == "Anthropic":
        shown = anthropic_code
        other = ""
    else:
        shown = openai_code
        other = anthropic_code
    return meta, shown, other, _visibility_note(provider_view)


def _visibility_note(provider_view: str) -> str:
    if provider_view == "Both":
        return "Showing both providers. Diff is usually the import + model constructor."
    return f"Showing the {provider_view} snippet. Switch the provider toggle to compare."


def search_catalog(query: str, category: str, provider_view: str):
    matches = filter_entries(query, category)
    labels = titles_for(matches)
    label = labels[0] if labels else None
    entry = entry_from_label(label) if label else None
    meta, left, right, note = _format_entry(entry, provider_view)
    return (
        gr.update(choices=labels, value=label),
        meta,
        left,
        gr.update(value=right, visible=provider_view == "Both"),
        note,
        f"{len(matches)} pattern(s)",
    )


def select_entry(label: str, provider_view: str):
    entry = entry_from_label(label)
    meta, left, right, note = _format_entry(entry, provider_view)
    return meta, left, gr.update(value=right, visible=provider_view == "Both"), note


def refresh_provider(label: str, provider_view: str):
    return select_entry(label, provider_view)


def models_for(provider: str) -> list[str]:
    return OPENAI_MODELS if provider == "OpenAI" else ANTHROPIC_MODELS


def on_provider_change(provider: str):
    choices = models_for(provider)
    return gr.update(choices=choices, value=choices[0])


def playground_hint(pattern: str) -> str:
    if pattern in LOCAL_PATTERNS:
        return "Runs entirely in-process. No API key required."
    if "fallback" in pattern.lower():
        return "Needs both OpenAI and Anthropic keys so LCEL can fail over."
    return "Needs the selected provider API key (textbox or Space secret)."


def run_live(pattern, provider, model_name, openai_key, anthropic_key, user_text):
    output, graph = run_pattern(pattern, provider, model_name, openai_key, anthropic_key, user_text)
    return output, graph or "(graph unavailable for this run)"


def build_demo() -> gr.Blocks:
    initial = ENTRIES[0]
    initial_labels = titles_for(ENTRIES)
    quick_md = "| Primitive | Meaning |\n|---|---|\n" + "\n".join(
        f"| {name} | {meaning} |" for name, meaning in QUICK_REF
    )

    theme = gr.themes.Soft(font=[gr.themes.GoogleFont("Source Sans 3"), "ui-sans-serif", "system-ui"])

    with gr.Blocks(theme=theme, css=CSS, title="LCEL Coding Cheatsheet") as demo:
        with gr.Column(elem_id="col-container"):
            gr.Markdown(INTRO, elem_id="hero")

            with gr.Accordion("API keys & default provider", open=False):
                gr.Markdown(
                    "Paste keys to run live chains. Local patterns work without keys. "
                    "On Spaces you can also add secrets instead of pasting."
                )
                with gr.Row():
                    openai_key = gr.Textbox(
                        label="OpenAI API key",
                        type="password",
                        placeholder="sk-...",
                    )
                    anthropic_key = gr.Textbox(
                        label="Anthropic API key",
                        type="password",
                        placeholder="sk-ant-...",
                    )
                with gr.Row():
                    default_provider = gr.Radio(
                        ["OpenAI", "Anthropic"],
                        value="OpenAI",
                        label="Playground provider",
                    )
                    default_model = gr.Dropdown(
                        choices=OPENAI_MODELS,
                        value=OPENAI_MODELS[0],
                        label="Playground model",
                    )

            with gr.Tabs():
                with gr.Tab("Cheatsheet"):
                    with gr.Row():
                        query = gr.Textbox(
                            label="Search",
                            placeholder="pipe, fallback, RAG, structured, assign…",
                            scale=3,
                        )
                        category = gr.Dropdown(CATEGORIES, value="All", label="Category", scale=1)
                        provider_view = gr.Radio(
                            ["Both", "OpenAI", "Anthropic"],
                            value="Both",
                            label="Snippet view",
                            scale=1,
                        )
                    count = gr.Markdown(f"{len(ENTRIES)} pattern(s)")
                    picker = gr.Dropdown(
                        choices=initial_labels,
                        value=initial_labels[0],
                        label="Pattern",
                    )
                    meta = gr.Markdown(_format_entry(initial, "Both")[0])
                    note = gr.Markdown(_visibility_note("Both"))
                    with gr.Row():
                        openai_code = gr.Code(
                            value=initial["openai"],
                            language="python",
                            label="OpenAI",
                            lines=18,
                        )
                        anthropic_code = gr.Code(
                            value=initial["anthropic"],
                            language="python",
                            label="Anthropic",
                            lines=18,
                        )

                    search_inputs = [query, category, provider_view]
                    search_outputs = [picker, meta, openai_code, anthropic_code, note, count]
                    query.submit(search_catalog, search_inputs, search_outputs)
                    query.change(search_catalog, search_inputs, search_outputs)
                    category.change(search_catalog, search_inputs, search_outputs)
                    provider_view.change(refresh_provider, [picker, provider_view], [meta, openai_code, anthropic_code, note])
                    picker.change(select_entry, [picker, provider_view], [meta, openai_code, anthropic_code, note])

                with gr.Tab("Live playground"):
                    gr.Markdown(
                        "Execute the selected LCEL graph. Local rows are key-free. "
                        "LLM rows call OpenAI or Anthropic with the key above."
                    )
                    pattern = gr.Dropdown(ALL_PATTERNS, value=ALL_PATTERNS[0], label="Runnable pattern")
                    hint = gr.Markdown(playground_hint(ALL_PATTERNS[0]))
                    user_text = gr.Textbox(
                        label="Input",
                        value="What is LangChain Expression Language?",
                        lines=3,
                    )
                    run_btn = gr.Button("Run chain", variant="primary")
                    live_out = gr.Textbox(label="Output", lines=10)
                    graph_out = gr.Textbox(label="chain.get_graph().draw_ascii()", lines=14)
                    pattern.change(playground_hint, pattern, hint)
                    run_btn.click(
                        run_live,
                        [pattern, default_provider, default_model, openai_key, anthropic_key, user_text],
                        [live_out, graph_out],
                    )
                    default_provider.change(on_provider_change, default_provider, default_model)

                    gr.Examples(
                        examples=[
                            ["Local · pipe + lambda", "OpenAI", "gpt-4o-mini", "  pipe   parallel assign  "],
                            ["Local · branch router", "OpenAI", "gpt-4o-mini", "def compose(a, b): return a | b"],
                            ["LLM · prompt | model | parser", "OpenAI", "gpt-4o-mini", "When do I use RunnableParallel?"],
                            ["LLM · RAG-style (fake retriever)", "Anthropic", "claude-3-5-haiku-latest", "How does a RAG chain look in LCEL?"],
                        ],
                        inputs=[pattern, default_provider, default_model, user_text],
                        cache_examples=False,
                    )

                with gr.Tab("Compare providers"):
                    gr.Markdown(
                        "Same prompt and LCEL pipe. OpenAI and Anthropic run independently so you can compare tone and API wiring."
                    )
                    compare_text = gr.Textbox(
                        label="Prompt",
                        value="Explain RunnablePassthrough.assign in one sentence.",
                        lines=3,
                    )
                    with gr.Row():
                        cmp_openai_model = gr.Dropdown(OPENAI_MODELS, value=OPENAI_MODELS[0], label="OpenAI model")
                        cmp_anthropic_model = gr.Dropdown(
                            ANTHROPIC_MODELS, value=ANTHROPIC_MODELS[0], label="Anthropic model"
                        )
                    compare_btn = gr.Button("Run both providers", variant="primary")
                    with gr.Row():
                        openai_out = gr.Textbox(label="OpenAI", lines=8)
                        anthropic_out = gr.Textbox(label="Anthropic", lines=8)
                    compare_btn.click(
                        compare_providers,
                        [openai_key, anthropic_key, cmp_openai_model, cmp_anthropic_model, compare_text],
                        [openai_out, anthropic_out],
                    )

                with gr.Tab("Quick reference"):
                    gr.Markdown(quick_md, elem_id="quick-table")
                    gr.Markdown(
                        """
### Install
```bash
pip install langchain-core langchain-openai langchain-anthropic langchain
export OPENAI_API_KEY=...
export ANTHROPIC_API_KEY=...
```

### Mental model
1. Everything is a **Runnable**.
2. `|` builds a **sequence**; a dict builds **parallel** branches.
3. `invoke` / `stream` / `batch` work on the whole graph.
4. OpenAI and Anthropic are interchangeable chat-model Runnables.

Official docs: [LangChain](https://docs.langchain.com/) · [ChatOpenAI](https://python.langchain.com/docs/integrations/chat/openai/) · [ChatAnthropic](https://python.langchain.com/docs/integrations/chat/anthropic/)
"""
                    )

    return demo


demo = build_demo()

if __name__ == "__main__":
    demo.launch()
