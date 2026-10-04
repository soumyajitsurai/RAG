const OPENAI_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"];
const ANTHROPIC_MODELS = [
  "claude-3-5-haiku-latest",
  "claude-3-5-sonnet-latest",
  "claude-sonnet-4-0",
];

const LOCAL_PATTERNS = [
  "Local · pipe + lambda",
  "Local · parallel + assign",
  "Local · branch router",
];

const LLM_PATTERNS = [
  "LLM · prompt | model | parser",
  "LLM · stream tokens",
  "LLM · parallel joke + definition",
  "LLM · structured output",
  "LLM · RAG-style (fake retriever)",
  "LLM · fallback OpenAI ↔ Anthropic",
];

const $ = (id) => document.getElementById(id);

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function filterEntries(entries, query, category) {
  const q = (query || "").trim().toLowerCase();
  const scored = [];
  for (const entry of entries) {
    if (category && category !== "All" && entry.category !== category) continue;
    if (!q) {
      scored.push([0, entry]);
      continue;
    }
    const title = `${entry.id} ${entry.title} ${entry.tags.join(" ")}`.toLowerCase();
    const meta = `${entry.summary} ${entry.when} ${entry.notes} ${entry.category}`.toLowerCase();
    const code = `${entry.openai} ${entry.anthropic}`.toLowerCase();
    if (title.includes(q)) scored.push([0, entry]);
    else if (meta.includes(q)) scored.push([1, entry]);
    else if (code.includes(q)) scored.push([2, entry]);
  }
  scored.sort((a, b) => a[0] - b[0]);
  return scored.map((item) => item[1]);
}

function labelFor(entry) {
  return `${entry.title}  ·  ${entry.category}`;
}

function codeBlock(kind, title, source) {
  const id = `code-${kind}`;
  return `
    <div class="code-wrap ${kind}">
      <h4>${title}</h4>
      <button class="copy" type="button" data-target="${id}">Copy</button>
      <pre><code id="${id}">${escapeHtml(source)}</code></pre>
    </div>`;
}

function renderEntry(entry, view) {
  $("meta").innerHTML = `
    <h3>${escapeHtml(entry.title)}</h3>
    <p><strong>Category:</strong> ${escapeHtml(entry.category)} · <strong>Tags:</strong> ${entry.tags.map(escapeHtml).join(", ")}</p>
    <p>${escapeHtml(entry.summary)}</p>
    <p><strong>When to use:</strong> ${escapeHtml(entry.when)}</p>
    <p><strong>Notes:</strong> ${escapeHtml(entry.notes)}</p>`;

  const grid = $("code-grid");
  grid.className = `code-grid ${view === "Both" ? "both" : "one"}`;
  if (view === "OpenAI") {
    grid.innerHTML = codeBlock("openai", "OpenAI", entry.openai);
  } else if (view === "Anthropic") {
    grid.innerHTML = codeBlock("anthropic", "Anthropic", entry.anthropic);
  } else {
    grid.innerHTML =
      codeBlock("openai", "OpenAI", entry.openai) +
      codeBlock("anthropic", "Anthropic", entry.anthropic);
  }
}

function currentView() {
  return document.querySelector('input[name="view"]:checked')?.value || "Both";
}

function fillSelect(select, values, selected) {
  select.innerHTML = values
    .map((value) => `<option${value === selected ? " selected" : ""}>${escapeHtml(value)}</option>`)
    .join("");
}

function runLocal(pattern, text) {
  const value = (text || "").trim() || "LangChain Expression Language";
  if (pattern === "Local · pipe + lambda") {
    const stripped = value.trim().replaceAll("  ", " ");
    return {
      output: JSON.stringify(
        { original: stripped, upper: stripped.toUpperCase(), words: stripped.split(/\s+/).filter(Boolean).length },
        null,
        2
      ),
      code: `from langchain_core.runnables import RunnableLambda

chain = (
    RunnableLambda(str.strip)
    | RunnableLambda(lambda s: s.replace("  ", " "))
    | RunnableLambda(lambda s: {"original": s, "upper": s.upper(), "words": len(s.split())})
)
print(chain.invoke(${JSON.stringify(value)}))
`,
    };
  }
  if (pattern === "Local · parallel + assign") {
    const tokens = value.split(/\s+/).filter(Boolean);
    return {
      output: JSON.stringify(
        { preview: tokens.slice(0, 8), stats: { chars: value.length, n_tokens: tokens.length } },
        null,
        2
      ),
      code: `from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough

chain = (
    RunnableLambda(lambda s: {"text": s})
    | RunnablePassthrough.assign(
        length=RunnableLambda(lambda d: len(d["text"])),
        tokens=RunnableLambda(lambda d: d["text"].split()),
    )
    | RunnableParallel(
        preview=RunnableLambda(lambda d: d["tokens"][:8]),
        stats=RunnableLambda(lambda d: {"chars": d["length"], "n_tokens": len(d["tokens"])}),
    )
)
print(chain.invoke(${JSON.stringify(value)}))
`,
    };
  }
  const route = /def |class |import /.test(value)
    ? "code-route"
    : value.includes("?")
      ? "question-route"
      : "default-route";
  const body = route === "default-route" ? value.toUpperCase() : value.slice(0, 160);
  return {
    output: `[${route}] ${body}`,
    code: `from langchain_core.runnables import RunnableBranch, RunnableLambda

router = RunnableBranch(
    (lambda x: any(k in x for k in ("def ", "class ", "import ")), RunnableLambda(lambda x: f"[code-route] {x[:160]}")),
    (lambda x: "?" in x, RunnableLambda(lambda x: f"[question-route] {x}")),
    RunnableLambda(lambda x: f"[default-route] {x.upper()}"),
)
print(router.invoke(${JSON.stringify(value)}))
`,
  };
}

function llmSnippet(pattern, provider, model, text) {
  const prompt = text || "What is LCEL?";
  const isOpen = provider === "OpenAI";
  const imp = isOpen
    ? "from langchain_openai import ChatOpenAI"
    : "from langchain_anthropic import ChatAnthropic";
  const ctor = isOpen
    ? `ChatOpenAI(model="${model}", temperature=0.3)`
    : `ChatAnthropic(model="${model}", temperature=0.3)`;

  const snippets = {
    "LLM · prompt | model | parser": `${imp}
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

chain = (
    ChatPromptTemplate.from_messages([
        ("system", "You are an LCEL coding reference. Answer in 3 short bullets."),
        ("human", "{text}"),
    ])
    | ${ctor}
    | StrOutputParser()
)
print(chain.invoke({"text": ${JSON.stringify(prompt)}}))
`,
    "LLM · stream tokens": `${imp}
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

chain = ChatPromptTemplate.from_template("Explain this in two sentences:\\n{text}") | ${ctor} | StrOutputParser()
for token in chain.stream({"text": ${JSON.stringify(prompt)}}):
    print(token, end="", flush=True)
`,
    "LLM · parallel joke + definition": `${imp}
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

model = ${ctor}
joke = ChatPromptTemplate.from_template("One short clean joke about: {text}") | model | StrOutputParser()
definition = ChatPromptTemplate.from_template("Define in one sentence: {text}") | model | StrOutputParser()
print(RunnableParallel(joke=joke, definition=definition).invoke({"text": ${JSON.stringify(prompt)}}))
`,
    "LLM · structured output": `from pydantic import BaseModel, Field
${imp}
from langchain_core.prompts import ChatPromptTemplate

class Card(BaseModel):
    title: str
    one_liner: str
    next_api: str

chain = ChatPromptTemplate.from_template("Turn this into an LCEL flashcard: {text}") | ${ctor}.with_structured_output(Card)
print(chain.invoke({"text": ${JSON.stringify(prompt)}}))
`,
    "LLM · RAG-style (fake retriever)": `${imp}
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

def retrieve(question: str) -> str:
    return "LCEL composes Runnables with |. A RAG chain is {context, question} | prompt | model | parser."

chain = (
    {"question": RunnablePassthrough(), "context": RunnableLambda(retrieve)}
    | ChatPromptTemplate.from_template("Context: {context}\\nQuestion: {question}")
    | ${ctor}
    | StrOutputParser()
)
print(chain.invoke(${JSON.stringify(prompt)}))
`,
    "LLM · fallback OpenAI ↔ Anthropic": `from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

primary = ChatOpenAI(model="gpt-4o-mini", max_retries=0)
backup = ChatAnthropic(model="claude-3-5-haiku-latest")
chain = (
    ChatPromptTemplate.from_template("One sentence on: {text}")
    | primary.with_fallbacks([backup])
    | StrOutputParser()
)
print(chain.invoke({"text": ${JSON.stringify(prompt)}}))
`,
  };
  return snippets[pattern] || "";
}

function compareSnippets(openaiModel, anthropicModel, text) {
  const prompt = text || "Explain RunnablePassthrough.assign in one sentence.";
  return {
    openai: `from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

chain = (
    ChatPromptTemplate.from_messages([
        ("system", "Reply in one precise sentence. No preamble."),
        ("human", "{text}"),
    ])
    | ChatOpenAI(model="${openaiModel}", temperature=0)
    | StrOutputParser()
)
print(chain.invoke({"text": ${JSON.stringify(prompt)}}))
`,
    anthropic: `from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

chain = (
    ChatPromptTemplate.from_messages([
        ("system", "Reply in one precise sentence. No preamble."),
        ("human", "{text}"),
    ])
    | ChatAnthropic(model="${anthropicModel}", temperature=0)
    | StrOutputParser()
)
print(chain.invoke({"text": ${JSON.stringify(prompt)}}))
`,
  };
}

function bindCopyButtons(root = document) {
  root.querySelectorAll(".copy").forEach((button) => {
    button.onclick = async () => {
      const target = document.getElementById(button.dataset.target);
      if (!target) return;
      await navigator.clipboard.writeText(target.textContent);
      button.textContent = "Copied";
      setTimeout(() => {
        button.textContent = "Copy";
      }, 1200);
    };
  });
}

async function main() {
  const data = await fetch("catalog_data.json").then((res) => res.json());
  const { categories, entries, quickRef } = data;
  let matches = entries;

  fillSelect($("category"), categories, "All");
  $("quick-body").innerHTML = quickRef
    .map(([name, meaning]) => `<tr><td><code>${escapeHtml(name)}</code></td><td>${escapeHtml(meaning)}</td></tr>`)
    .join("");

  fillSelect($("play-pattern"), [...LOCAL_PATTERNS, ...LLM_PATTERNS], LOCAL_PATTERNS[0]);
  fillSelect($("play-model"), OPENAI_MODELS, OPENAI_MODELS[0]);

  function refreshList() {
    matches = filterEntries(entries, $("search").value, $("category").value);
    $("count").textContent = `${matches.length} pattern(s)`;
    fillSelect($("picker"), matches.map(labelFor), matches[0] ? labelFor(matches[0]) : "");
    if (matches[0]) renderEntry(matches[0], currentView());
    else {
      $("meta").innerHTML = "<p>No match.</p>";
      $("code-grid").innerHTML = "";
    }
    bindCopyButtons();
  }

  function selectedEntry() {
    const label = $("picker").value;
    return matches.find((entry) => labelFor(entry) === label) || matches[0];
  }

  $("search").addEventListener("input", refreshList);
  $("category").addEventListener("change", refreshList);
  document.querySelectorAll('input[name="view"]').forEach((input) => {
    input.addEventListener("change", () => {
      const entry = selectedEntry();
      if (entry) renderEntry(entry, currentView());
      bindCopyButtons();
    });
  });
  $("picker").addEventListener("change", () => {
    const entry = selectedEntry();
    if (entry) renderEntry(entry, currentView());
    bindCopyButtons();
  });

  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".panel").forEach((panel) => panel.classList.remove("active"));
      tab.classList.add("active");
      $(`panel-${tab.dataset.tab}`).classList.add("active");
    });
  });

  $("play-provider").addEventListener("change", () => {
    const models = $("play-provider").value === "OpenAI" ? OPENAI_MODELS : ANTHROPIC_MODELS;
    fillSelect($("play-model"), models, models[0]);
  });

  $("play-pattern").addEventListener("change", () => {
    const pattern = $("play-pattern").value;
    $("play-hint").textContent = LOCAL_PATTERNS.includes(pattern)
      ? "Runs in the browser. No API key required."
      : "Generates a copy-paste LCEL chain for the selected provider. Run it locally with your OpenAI or Anthropic key.";
  });
  $("play-pattern").dispatchEvent(new Event("change"));

  $("play-run").addEventListener("click", () => {
    const pattern = $("play-pattern").value;
    const text = $("play-input").value;
    if (LOCAL_PATTERNS.includes(pattern)) {
      const result = runLocal(pattern, text);
      $("play-out").textContent = result.output;
      $("play-code").textContent = result.code;
    } else {
      const code = llmSnippet(pattern, $("play-provider").value, $("play-model").value, text);
      $("play-out").textContent =
        "This Space is static (free hosting). Copy the LCEL snippet and run it locally with OPENAI_API_KEY or ANTHROPIC_API_KEY.";
      $("play-code").textContent = code;
    }
    bindCopyButtons();
  });

  $("cmp-run").addEventListener("click", () => {
    const pair = compareSnippets($("cmp-openai").value, $("cmp-anthropic").value, $("cmp-input").value);
    $("cmp-oai").textContent = pair.openai;
    $("cmp-ant").textContent = pair.anthropic;
    bindCopyButtons();
  });

  refreshList();
  bindCopyButtons();
}

main().catch((error) => {
  document.body.insertAdjacentHTML(
    "beforeend",
    `<p style="color:#f66;padding:20px">Failed to load catalog: ${escapeHtml(error.message)}</p>`
  );
});
