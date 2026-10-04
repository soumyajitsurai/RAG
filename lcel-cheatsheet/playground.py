"""Live LCEL runners for the cheatsheet playground.

Local patterns never call a provider. LLM patterns accept a user-supplied
OpenAI or Anthropic key (or Space secrets) and never log the key.
"""

from __future__ import annotations

import os
import traceback
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from pydantic import BaseModel, Field

LOCAL_PATTERNS = [
    "Local · pipe + lambda",
    "Local · parallel + assign",
    "Local · branch router",
]

LLM_PATTERNS = [
    "LLM · prompt | model | parser",
    "LLM · stream tokens",
    "LLM · parallel joke + definition",
    "LLM · structured output",
    "LLM · RAG-style (fake retriever)",
    "LLM · fallback OpenAI ↔ Anthropic",
]

ALL_PATTERNS = LOCAL_PATTERNS + LLM_PATTERNS

OPENAI_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"]
ANTHROPIC_MODELS = [
    "claude-3-5-haiku-latest",
    "claude-3-5-sonnet-latest",
    "claude-sonnet-4-0",
]


def resolve_key(provider: str, openai_key: str, anthropic_key: str) -> str:
    if provider == "OpenAI":
        return (openai_key or "").strip() or os.getenv("OPENAI_API_KEY", "")
    return (anthropic_key or "").strip() or os.getenv("ANTHROPIC_API_KEY", "")


def build_model(provider: str, model_name: str, api_key: str):
    if provider == "OpenAI":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model_name, api_key=api_key, temperature=0.3)
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(model=model_name, api_key=api_key, temperature=0.3)


def draw_graph(runnable: Any) -> str:
    try:
        return runnable.get_graph().draw_ascii()
    except Exception as exc:  # noqa: BLE001 — grandalf is optional at runtime
        return f"(install grandalf to draw ASCII graphs: {exc})"


def _format_result(value: Any) -> str:
    if hasattr(value, "model_dump"):
        data = value.model_dump()
        return "\n".join(f"{k}: {v}" for k, v in data.items())
    return str(value)


def run_local(pattern: str, user_text: str) -> tuple[str, str]:
    text = (user_text or "").strip() or "LangChain Expression Language"
    graph = ""

    if pattern == "Local · pipe + lambda":
        chain = (
            RunnableLambda(str.strip)
            | RunnableLambda(lambda s: s.replace("  ", " "))
            | RunnableLambda(lambda s: {"original": s, "upper": s.upper(), "words": len(s.split())})
        )
        graph = draw_graph(chain)
        return _format_result(chain.invoke(text)), graph

    if pattern == "Local · parallel + assign":
        to_dict = RunnableLambda(lambda s: {"text": s})
        chain = (
            to_dict
            | RunnablePassthrough.assign(
                length=RunnableLambda(lambda d: len(d["text"])),
                tokens=RunnableLambda(lambda d: d["text"].split()),
            )
            | RunnableParallel(
                preview=RunnableLambda(lambda d: d["tokens"][:8]),
                stats=RunnableLambda(lambda d: {"chars": d["length"], "n_tokens": len(d["tokens"])}),
            )
        )
        graph = draw_graph(chain)
        return _format_result(chain.invoke(text)), graph

    # Local · branch router
    chain = RunnableBranch(
        (lambda s: any(k in s.lower() for k in ("def ", "class ", "import ")), RunnableLambda(lambda s: f"[code-route] {s[:160]}")),
        (lambda s: "?" in s, RunnableLambda(lambda s: f"[question-route] {s}")),
        RunnableLambda(lambda s: f"[default-route] {s.upper()}"),
    )
    graph = draw_graph(chain)
    return _format_result(chain.invoke(text)), graph


def run_llm(
    pattern: str,
    provider: str,
    model_name: str,
    openai_key: str,
    anthropic_key: str,
    user_text: str,
) -> tuple[str, str]:
    text = (user_text or "").strip() or "What is LCEL?"
    key = resolve_key(provider, openai_key, anthropic_key)
    if not key:
        return (
            f"Add an {provider} API key in the Keys panel (or set "
            f"{'OPENAI_API_KEY' if provider == 'OpenAI' else 'ANTHROPIC_API_KEY'} as a Space secret) to run this pattern.",
            "",
        )

    model = build_model(provider, model_name, key)

    if pattern == "LLM · prompt | model | parser":
        chain = (
            ChatPromptTemplate.from_messages(
                [
                    ("system", "You are an LCEL coding reference. Answer in 3 short bullets."),
                    ("human", "{text}"),
                ]
            )
            | model
            | StrOutputParser()
        )
        return chain.invoke({"text": text}), draw_graph(chain)

    if pattern == "LLM · stream tokens":
        chain = (
            ChatPromptTemplate.from_template("Explain this in two sentences:\\n{text}")
            | model
            | StrOutputParser()
        )
        chunks: list[str] = []
        for token in chain.stream({"text": text}):
            chunks.append(token)
        return "".join(chunks), draw_graph(chain)

    if pattern == "LLM · parallel joke + definition":
        joke = (
            ChatPromptTemplate.from_template("One short clean joke about: {text}")
            | model
            | StrOutputParser()
        )
        definition = (
            ChatPromptTemplate.from_template("Define in one sentence: {text}")
            | model
            | StrOutputParser()
        )
        chain = RunnableParallel(joke=joke, definition=definition)
        result = chain.invoke({"text": text})
        rendered = f"JOKE\n{result['joke']}\n\nDEFINITION\n{result['definition']}"
        return rendered, draw_graph(chain)

    if pattern == "LLM · structured output":
        class Card(BaseModel):
            title: str = Field(description="Concept name")
            one_liner: str = Field(description="Single sentence")
            next_api: str = Field(description="LCEL method or class to try next")

        structured = model.with_structured_output(Card)
        chain = ChatPromptTemplate.from_template("Turn this into an LCEL flashcard: {text}") | structured
        return _format_result(chain.invoke({"text": text})), draw_graph(chain)

    if pattern == "LLM · RAG-style (fake retriever)":
        docs = {
            "lcel": "LCEL composes Runnables with |. Every step has invoke, stream, and batch.",
            "rag": "A RAG chain is {context: retriever, question: Passthrough} | prompt | model | parser.",
            "fallback": "with_fallbacks lets OpenAI fail over to Anthropic (or the reverse).",
        }

        def retrieve(question: str) -> str:
            q = question.lower()
            hits = [v for k, v in docs.items() if k in q]
            return " ".join(hits) or " ".join(docs.values())

        prompt = ChatPromptTemplate.from_template(
            "Answer using only the context. If the context is thin, say so.\\n"
            "Context: {context}\\nQuestion: {question}"
        )
        chain = (
            {"question": RunnablePassthrough(), "context": RunnableLambda(retrieve)}
            | prompt
            | model
            | StrOutputParser()
        )
        return chain.invoke(text), draw_graph(chain)

    # LLM · fallback OpenAI ↔ Anthropic
    openai_key_resolved = resolve_key("OpenAI", openai_key, anthropic_key)
    anthropic_key_resolved = resolve_key("Anthropic", openai_key, anthropic_key)
    if not openai_key_resolved or not anthropic_key_resolved:
        return (
            "Fallback demo needs both OpenAI and Anthropic keys so the chain can fail over.",
            "",
        )

    from langchain_anthropic import ChatAnthropic
    from langchain_openai import ChatOpenAI

    primary = ChatOpenAI(model="gpt-4o-mini", api_key=openai_key_resolved, max_retries=0, temperature=0)
    backup = ChatAnthropic(
        model="claude-3-5-haiku-latest",
        api_key=anthropic_key_resolved,
        temperature=0,
    )
    if provider == "Anthropic":
        primary, backup = (
            ChatAnthropic(
                model="claude-3-5-haiku-latest",
                api_key=anthropic_key_resolved,
                max_retries=0,
                temperature=0,
            ),
            ChatOpenAI(model="gpt-4o-mini", api_key=openai_key_resolved, temperature=0),
        )
    model_fb = primary.with_fallbacks([backup])
    chain = (
        ChatPromptTemplate.from_template("One sentence on: {text}")
        | model_fb
        | StrOutputParser()
    )
    return chain.invoke({"text": text}), draw_graph(chain)


def run_pattern(
    pattern: str,
    provider: str,
    model_name: str,
    openai_key: str,
    anthropic_key: str,
    user_text: str,
) -> tuple[str, str]:
    try:
        if pattern in LOCAL_PATTERNS:
            return run_local(pattern, user_text)
        return run_llm(pattern, provider, model_name, openai_key, anthropic_key, user_text)
    except Exception as exc:  # noqa: BLE001 — surface provider errors in the UI
        detail = "".join(traceback.format_exception_only(type(exc), exc)).strip()
        return f"Run failed: {detail}", ""


def compare_providers(
    openai_key: str,
    anthropic_key: str,
    openai_model: str,
    anthropic_model: str,
    user_text: str,
) -> tuple[str, str]:
    text = (user_text or "").strip() or "Explain RunnablePassthrough.assign in one sentence."
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Reply in one precise sentence. No preamble."),
            ("human", "{text}"),
        ]
    )
    outputs: list[str] = []
    for provider, model_name, key in (
        ("OpenAI", openai_model, resolve_key("OpenAI", openai_key, anthropic_key)),
        ("Anthropic", anthropic_model, resolve_key("Anthropic", openai_key, anthropic_key)),
    ):
        if not key:
            outputs.append(f"{provider}: missing API key")
            continue
        try:
            chain = prompt | build_model(provider, model_name, key) | StrOutputParser()
            outputs.append(f"{provider} ({model_name}):\n{chain.invoke({'text': text})}")
        except Exception as exc:  # noqa: BLE001
            outputs.append(f"{provider}: {exc}")
    return outputs[0], outputs[1]
