"""Searchable LCEL coding-reference catalog.

Snippets are written for current langchain-core + ChatOpenAI / ChatAnthropic.
Both providers implement the same Runnable interface, so most pipes are identical.
"""

from __future__ import annotations

from typing import Any

CATEGORIES = [
    "All",
    "Composition",
    "Invocation",
    "Prompts & Models",
    "Parsing",
    "Parallelism",
    "Data shaping",
    "Resilience",
    "Routing",
    "RAG",
    "Agents & Tools",
    "Configuration",
]

ENTRIES: list[dict[str, Any]] = [
    {
        "id": "pipe",
        "title": "Pipe operator  |  (RunnableSequence)",
        "category": "Composition",
        "tags": ["pipe", "sequence", "lcel", "basic"],
        "summary": "The `|` operator composes Runnables left-to-right. Output of each step is the input of the next.",
        "when": "Any linear chain: prompt → model → parser, or retrieve → prompt → model.",
        "openai": '''from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a concise Python tutor."),
    ("human", "{question}"),
])
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = prompt | model | StrOutputParser()

print(chain.invoke({"question": "What is LCEL in one sentence?"}))
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a concise Python tutor."),
    ("human", "{question}"),
])
model = ChatAnthropic(model="claude-3-5-haiku-latest", temperature=0)
chain = prompt | model | StrOutputParser()

print(chain.invoke({"question": "What is LCEL in one sentence?"}))
''',
        "notes": "Equivalent explicit form: `RunnableSequence(prompt, model, parser)`. Prefer `|` for readability.",
    },
    {
        "id": "invoke-stream-batch",
        "title": "invoke / stream / batch / ainvoke",
        "category": "Invocation",
        "tags": ["invoke", "stream", "batch", "async"],
        "summary": "Every Runnable exposes the same execution API. Swap providers without changing call sites.",
        "when": "Use invoke for one result, stream for tokens, batch for many inputs, ainvoke in async apps.",
        "openai": '''from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

chain = (
    ChatPromptTemplate.from_template("Explain {topic} in 12 words.")
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)

chain.invoke({"topic": "LCEL"})
for token in chain.stream({"topic": "RAG"}):
    print(token, end="", flush=True)
chain.batch([{"topic": "prompts"}, {"topic": "parsers"}])
# await chain.ainvoke({"topic": "fallbacks"})
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

chain = (
    ChatPromptTemplate.from_template("Explain {topic} in 12 words.")
    | ChatAnthropic(model="claude-3-5-haiku-latest")
    | StrOutputParser()
)

chain.invoke({"topic": "LCEL"})
for token in chain.stream({"topic": "RAG"}):
    print(token, end="", flush=True)
chain.batch([{"topic": "prompts"}, {"topic": "parsers"}])
# await chain.ainvoke({"topic": "fallbacks"})
''',
        "notes": "`batch` fans out inputs (optionally with `config={'max_concurrency': N}`). Streaming yields string chunks after a StrOutputParser, or message chunks before it.",
    },
    {
        "id": "init-chat-model",
        "title": "Provider-agnostic init_chat_model",
        "category": "Prompts & Models",
        "tags": ["init_chat_model", "openai", "anthropic", "portable"],
        "summary": "One factory, two providers. Keep the rest of the LCEL graph unchanged.",
        "when": "Apps that must switch OpenAI ↔ Anthropic from env/config without rewriting chains.",
        "openai": '''from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-4o-mini", temperature=0)
# model = init_chat_model("gpt-4o-mini", model_provider="openai")
''',
        "anthropic": '''from langchain.chat_models import init_chat_model

model = init_chat_model("anthropic:claude-3-5-haiku-latest", temperature=0)
# model = init_chat_model("claude-3-5-haiku-latest", model_provider="anthropic")
''',
        "notes": "Requires `langchain` plus the provider package (`langchain-openai` or `langchain-anthropic`). API keys still come from OPENAI_API_KEY / ANTHROPIC_API_KEY.",
    },
    {
        "id": "chat-prompt",
        "title": "ChatPromptTemplate + MessagesPlaceholder",
        "category": "Prompts & Models",
        "tags": ["prompt", "messages", "history", "system"],
        "summary": "Build chat messages declaratively. Placeholders accept chat history or tool results.",
        "when": "Multi-turn chats, RAG answers that inject context, or any system+human+history pattern.",
        "openai": '''from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer using only the provided context.\\n{context}"),
    MessagesPlaceholder("history"),
    ("human", "{question}"),
])
chain = prompt | ChatOpenAI(model="gpt-4o-mini")

chain.invoke({
    "context": "LCEL composes Runnables with |",
    "history": [
        HumanMessage(content="What is a Runnable?"),
        AIMessage(content="A unit of work with invoke/stream/batch."),
    ],
    "question": "How do I compose two of them?",
})
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer using only the provided context.\\n{context}"),
    MessagesPlaceholder("history"),
    ("human", "{question}"),
])
chain = prompt | ChatAnthropic(model="claude-3-5-haiku-latest")

chain.invoke({
    "context": "LCEL composes Runnables with |",
    "history": [
        HumanMessage(content="What is a Runnable?"),
        AIMessage(content="A unit of work with invoke/stream/batch."),
    ],
    "question": "How do I compose two of them?",
})
''',
        "notes": "Use `MessagesPlaceholder('history', optional=True)` when history may be missing.",
    },
    {
        "id": "bind",
        "title": "bind() — freeze call-time kwargs",
        "category": "Prompts & Models",
        "tags": ["bind", "stop", "tools", "temperature"],
        "summary": "Attach default kwargs (stop sequences, tools, temperature) without wrapping the model.",
        "when": "Reuse one model instance with different stop words, tools, or sampling settings per chain.",
        "openai": '''from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

model = ChatOpenAI(model="gpt-4o-mini")
stopped = model.bind(stop=["\\n\\n"])
jsonish = model.bind(temperature=0, response_format={"type": "json_object"})

chain = ChatPromptTemplate.from_template("List 3 {item} names:") | stopped
print(chain.invoke({"item": "Runnable"}))
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

model = ChatAnthropic(model="claude-3-5-haiku-latest")
stopped = model.bind(stop_sequences=["\\n\\n"])
precise = model.bind(temperature=0, max_tokens=256)

chain = ChatPromptTemplate.from_template("List 3 {item} names:") | stopped
print(chain.invoke({"item": "Runnable"}))
''',
        "notes": "OpenAI uses `stop=`; Anthropic uses `stop_sequences=`. Everything downstream of `|` stays the same.",
    },
    {
        "id": "structured",
        "title": "with_structured_output(Pydantic)",
        "category": "Parsing",
        "tags": ["structured", "pydantic", "json", "schema"],
        "summary": "Force a typed object back from the model. Ideal for extraction and routing payloads.",
        "when": "You need validated fields, not free-form prose.",
        "openai": '''from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class Cheat(BaseModel):
    concept: str
    one_liner: str = Field(description="12 words or fewer")
    pitfall: str

model = ChatOpenAI(model="gpt-4o-mini").with_structured_output(Cheat)
chain = ChatPromptTemplate.from_template("Summarize this LCEL idea: {idea}") | model
print(chain.invoke({"idea": "RunnableParallel fans out the same input"}))
''',
        "anthropic": '''from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

class Cheat(BaseModel):
    concept: str
    one_liner: str = Field(description="12 words or fewer")
    pitfall: str

model = ChatAnthropic(model="claude-3-5-haiku-latest").with_structured_output(Cheat)
chain = ChatPromptTemplate.from_template("Summarize this LCEL idea: {idea}") | model
print(chain.invoke({"idea": "RunnableParallel fans out the same input"}))
''',
        "notes": "Both providers support tool/function calling under the hood. Prefer Pydantic v2 models with Field descriptions.",
    },
    {
        "id": "parsers",
        "title": "Str / Json / Pydantic output parsers",
        "category": "Parsing",
        "tags": ["parser", "json", "string"],
        "summary": "Parsers are Runnables. Pipe them after the model to normalize message objects into data.",
        "when": "Turning AIMessage → str/dict/model, or teaching the prompt to emit JSON.",
        "openai": '''from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel

class Pair(BaseModel):
    term: str
    meaning: str

parser = JsonOutputParser(pydantic_object=Pair)
prompt = ChatPromptTemplate.from_messages([
    ("system", "Return JSON only.\\n{format_instructions}"),
    ("human", "Define {term}"),
]).partial(format_instructions=parser.get_format_instructions())

chain = prompt | ChatOpenAI(model="gpt-4o-mini") | parser
print(chain.invoke({"term": "RunnablePassthrough"}))
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel

class Pair(BaseModel):
    term: str
    meaning: str

parser = JsonOutputParser(pydantic_object=Pair)
prompt = ChatPromptTemplate.from_messages([
    ("system", "Return JSON only.\\n{format_instructions}"),
    ("human", "Define {term}"),
]).partial(format_instructions=parser.get_format_instructions())

chain = prompt | ChatAnthropic(model="claude-3-5-haiku-latest") | parser
print(chain.invoke({"term": "RunnablePassthrough"}))
''',
        "notes": "`StrOutputParser` is the usual last step for chat UIs. Prefer `with_structured_output` over JSON-in-the-prompt when the provider supports tools.",
    },
    {
        "id": "parallel",
        "title": "RunnableParallel — fan-out the same input",
        "category": "Parallelism",
        "tags": ["parallel", "dict", "fan-out"],
        "summary": "A dict literal inside a pipe becomes RunnableParallel. Each branch sees the same input and runs concurrently.",
        "when": "Retrieve + rewrite at once, or generate two views (joke + poem, summary + tags).",
        "openai": '''from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

model = ChatOpenAI(model="gpt-4o-mini")
joke = ChatPromptTemplate.from_template("Joke about {topic}") | model | StrOutputParser()
poem = ChatPromptTemplate.from_template("Two-line poem about {topic}") | model | StrOutputParser()

fanout = RunnableParallel(joke=joke, poem=poem)
# shorthand inside a sequence:
# {"joke": joke, "poem": poem}
print(fanout.invoke({"topic": "vector databases"}))
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

model = ChatAnthropic(model="claude-3-5-haiku-latest")
joke = ChatPromptTemplate.from_template("Joke about {topic}") | model | StrOutputParser()
poem = ChatPromptTemplate.from_template("Two-line poem about {topic}") | model | StrOutputParser()

fanout = RunnableParallel(joke=joke, poem=poem)
print(fanout.invoke({"topic": "vector databases"}))
''',
        "notes": "Output is a dict of branch names. Downstream steps can pick keys with `itemgetter` or `.pick()`.",
    },
    {
        "id": "passthrough",
        "title": "RunnablePassthrough + assign()",
        "category": "Data shaping",
        "tags": ["passthrough", "assign", "merge"],
        "summary": "Keep the original input while adding computed keys. Classic RAG glue.",
        "when": "You have a raw question and need to attach retrieved context without losing the question.",
        "openai": '''from operator import itemgetter
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

def fake_retriever(question: str) -> str:
    return "LCEL uses | to compose Runnables."

prompt = ChatPromptTemplate.from_template(
    "Context: {context}\\nQuestion: {question}\\nAnswer:"
)
chain = (
    RunnablePassthrough.assign(context=RunnableLambda(fake_retriever))
    | prompt
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)
# input can be a string if the retriever + prompt agree,
# or a dict: {"question": "..."} with itemgetter("question")
print(chain.invoke("What is LCEL?"))
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

def fake_retriever(question: str) -> str:
    return "LCEL uses | to compose Runnables."

prompt = ChatPromptTemplate.from_template(
    "Context: {context}\\nQuestion: {question}\\nAnswer:"
)
chain = (
    {"question": RunnablePassthrough(), "context": RunnableLambda(fake_retriever)}
    | prompt
    | ChatAnthropic(model="claude-3-5-haiku-latest")
    | StrOutputParser()
)
print(chain.invoke("What is LCEL?"))
''',
        "notes": "`assign` merges new keys into the incoming dict. Bare `RunnablePassthrough()` forwards the input unchanged.",
    },
    {
        "id": "lambda",
        "title": "RunnableLambda and @chain",
        "category": "Data shaping",
        "tags": ["lambda", "function", "custom"],
        "summary": "Wrap any Python function as a Runnable so it can sit inside a pipe.",
        "when": "Light transforms: strip text, format docs, compute scores, call a helper.",
        "openai": '''from langchain_core.runnables import RunnableLambda, chain

upper = RunnableLambda(lambda text: text.upper())
print(upper.invoke("lcel"))

@chain
def word_count(text: str) -> dict:
    return {"text": text, "n": len(text.split())}

print(word_count.invoke("pipe parallel assign"))
# word_count is a full Runnable: .invoke / .batch / .stream work
''',
        "anthropic": '''from langchain_core.runnables import RunnableLambda, chain

# Provider-agnostic — no model required
normalize = RunnableLambda(lambda d: {**d, "question": d["question"].strip()})

@chain
def clip(text: str) -> str:
    return text[:240]

print(normalize.invoke({"question": "  What is assign()?  "}))
print(clip.invoke("x" * 400))
''',
        "notes": "Type hints improve input/output schemas. Raise normally; LCEL surfaces the exception from invoke.",
    },
    {
        "id": "pick-itemgetter",
        "title": "pick() and itemgetter",
        "category": "Data shaping",
        "tags": ["pick", "itemgetter", "keys"],
        "summary": "Select a subset of dict keys before the next step. Keeps prompts from seeing extra fields.",
        "when": "After RunnableParallel / assign you only want `context` + `question`.",
        "openai": '''from operator import itemgetter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

prep = (
    RunnablePassthrough.assign(
        context=RunnableLambda(lambda x: f"docs for {x['question']}"),
        debug=RunnableLambda(lambda x: "trace-id"),
    )
    .pick(["question", "context"])
)
print(prep.invoke({"question": "What is pick?"}))

# or: itemgetter("question") as a Runnable inside a dict
route = {"q": itemgetter("question")}
''',
        "anthropic": '''from operator import itemgetter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Same shaping code — no provider lock-in
prep = (
    RunnablePassthrough.assign(
        context=RunnableLambda(lambda x: f"docs for {x['question']}"),
        debug=RunnableLambda(lambda x: "trace-id"),
    )
    .pick(["question", "context"])
)
print(prep.invoke({"question": "What is pick?"}))
''',
        "notes": "`itemgetter('k')` works as a Runnable in LCEL. `pick` is the fluent alternative on a Runnable.",
    },
    {
        "id": "fallbacks",
        "title": "with_fallbacks — OpenAI then Anthropic",
        "category": "Resilience",
        "tags": ["fallback", "openai", "anthropic", "reliability"],
        "summary": "If the primary model errors (rate limit, outage), LCEL tries the next Runnable.",
        "when": "Production chains that must survive a single-provider failure.",
        "openai": '''from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

primary = ChatOpenAI(model="gpt-4o-mini", max_retries=0)
backup = ChatAnthropic(model="claude-3-5-haiku-latest")
model = primary.with_fallbacks([backup])

chain = (
    ChatPromptTemplate.from_template("One fact about {topic}:")
    | model
    | StrOutputParser()
)
print(chain.invoke({"topic": "LCEL fallbacks"}))
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

primary = ChatAnthropic(model="claude-3-5-haiku-latest", max_retries=0)
backup = ChatOpenAI(model="gpt-4o-mini")
model = primary.with_fallbacks([backup])

chain = (
    ChatPromptTemplate.from_template("One fact about {topic}:")
    | model
    | StrOutputParser()
)
print(chain.invoke({"topic": "LCEL fallbacks"}))
''',
        "notes": "Fallbacks can be whole chains, not just models. Exceptions from the primary trigger the next option.",
    },
    {
        "id": "retry",
        "title": "with_retry",
        "category": "Resilience",
        "tags": ["retry", "transient", "errors"],
        "summary": "Retry a Runnable on transient failures before giving up or falling back.",
        "when": "429 / 5xx / timeout from a provider. Combine with fallbacks for layered resilience.",
        "openai": '''from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

model = ChatOpenAI(model="gpt-4o-mini").with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True,
)
chain = ChatPromptTemplate.from_template("{q}") | model
chain.invoke({"q": "Ping"})
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

model = ChatAnthropic(model="claude-3-5-haiku-latest").with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True,
)
chain = ChatPromptTemplate.from_template("{q}") | model
chain.invoke({"q": "Ping"})
''',
        "notes": "Chat model clients already retry some HTTP errors. `with_retry` is useful around custom lambdas and whole sub-chains.",
    },
    {
        "id": "branch",
        "title": "RunnableBranch — input-based routing",
        "category": "Routing",
        "tags": ["branch", "router", "if", "conditional"],
        "summary": "Pick a sub-chain from predicates. First matching condition wins; else default.",
        "when": "Cheap classifier or keyword gate before an expensive model call.",
        "openai": '''from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda

model = ChatOpenAI(model="gpt-4o-mini")
code = ChatPromptTemplate.from_template("Review this code:\\n{text}") | model
docs = ChatPromptTemplate.from_template("Edit this sentence:\\n{text}") | model

router = RunnableBranch(
    (lambda x: "def " in x["text"] or "class " in x["text"], code),
    (lambda x: len(x["text"]) < 40, RunnableLambda(lambda x: f"echo: {x['text']}")),
    docs,  # default
) | StrOutputParser()

print(router.invoke({"text": "def pipe(a, b): return a | b"}))
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda

model = ChatAnthropic(model="claude-3-5-haiku-latest")
code = ChatPromptTemplate.from_template("Review this code:\\n{text}") | model
docs = ChatPromptTemplate.from_template("Edit this sentence:\\n{text}") | model

router = RunnableBranch(
    (lambda x: "def " in x["text"] or "class " in x["text"], code),
    (lambda x: len(x["text"]) < 40, RunnableLambda(lambda x: f"echo: {x['text']}")),
    docs,
) | StrOutputParser()

print(router.invoke({"text": "def pipe(a, b): return a | b"}))
''',
        "notes": "For LLM-based routing, classify first (`with_structured_output`) then branch on the label.",
    },
    {
        "id": "rag",
        "title": "RAG chain (retriever + prompt + model)",
        "category": "RAG",
        "tags": ["rag", "retriever", "passthrough", "context"],
        "summary": "The canonical LCEL RAG graph: parallel retrieve + pass question, then prompt | model | parse.",
        "when": "Grounded Q&A over manuals, tickets, or any vector store — including this repo's medical RAG flow.",
        "openai": '''from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import Chroma

vectorstore = Chroma.from_texts(
    ["LCEL composes Runnables with the pipe operator."],
    embedding=OpenAIEmbeddings(),
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
format_docs = lambda docs: "\\n\\n".join(d.page_content for d in docs)

prompt = ChatPromptTemplate.from_template(
    "Use the context to answer. If missing, say you do not know.\\n"
    "Context:\\n{context}\\n\\nQuestion: {question}"
)
rag = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)
print(rag.invoke("How does LCEL compose steps?"))
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_openai import OpenAIEmbeddings  # or any Embeddings impl
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import Chroma

vectorstore = Chroma.from_texts(
    ["LCEL composes Runnables with the pipe operator."],
    embedding=OpenAIEmbeddings(),
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
format_docs = lambda docs: "\\n\\n".join(d.page_content for d in docs)

prompt = ChatPromptTemplate.from_template(
    "Use the context to answer. If missing, say you do not know.\\n"
    "Context:\\n{context}\\n\\nQuestion: {question}"
)
rag = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | ChatAnthropic(model="claude-3-5-haiku-latest")
    | StrOutputParser()
)
print(rag.invoke("How does LCEL compose steps?"))
''',
        "notes": "Embeddings provider and chat provider can differ. Retrievers are Runnables: `retriever | format_docs` is valid LCEL.",
    },
    {
        "id": "history",
        "title": "RunnableWithMessageHistory",
        "category": "Agents & Tools",
        "tags": ["memory", "history", "session"],
        "summary": "Wrap a chat chain so LCEL injects/reads message history by session_id.",
        "when": "Multi-turn coding assistants or support bots.",
        "openai": '''from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

store: dict = {}

def history_for(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an LCEL coding reference."),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])
inner = prompt | ChatOpenAI(model="gpt-4o-mini")
chat = RunnableWithMessageHistory(
    inner,
    history_for,
    input_messages_key="input",
    history_messages_key="history",
)
cfg = {"configurable": {"session_id": "dev-1"}}
chat.invoke({"input": "What is assign?"}, config=cfg)
chat.invoke({"input": "Show a one-liner."}, config=cfg)
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

store: dict = {}

def history_for(session_id: str) -> InMemoryChatMessageHistory:
    return store.setdefault(session_id, InMemoryChatMessageHistory())

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an LCEL coding reference."),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])
inner = prompt | ChatAnthropic(model="claude-3-5-haiku-latest")
chat = RunnableWithMessageHistory(
    inner, history_for,
    input_messages_key="input",
    history_messages_key="history",
)
cfg = {"configurable": {"session_id": "dev-1"}}
chat.invoke({"input": "What is assign?"}, config=cfg)
''',
        "notes": "Replace InMemoryChatMessageHistory with Redis/SQL history for production. Session id is required in `config`.",
    },
    {
        "id": "tools",
        "title": "bind_tools + tool-calling loop",
        "category": "Agents & Tools",
        "tags": ["tools", "bind_tools", "agent"],
        "summary": "Expose Python functions to the model. Both OpenAI and Anthropic speak tool calls.",
        "when": "Lookups, calculators, retrieval hops, or any side effect the model should request.",
        "openai": '''from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

@tool
def add(a: int, b: int) -> int:
    "Add two integers."
    return a + b

model = ChatOpenAI(model="gpt-4o-mini").bind_tools([add])
msg = model.invoke([HumanMessage("What is 21 + 21?")])
print(msg.tool_calls)
# then execute tools and call the model again with ToolMessage results
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

@tool
def add(a: int, b: int) -> int:
    "Add two integers."
    return a + b

model = ChatAnthropic(model="claude-3-5-haiku-latest").bind_tools([add])
msg = model.invoke([HumanMessage("What is 21 + 21?")])
print(msg.tool_calls)
''',
        "notes": "For a full loop, use `create_agent` (LangChain) or LangGraph. `bind_tools` is the LCEL primitive underneath.",
    },
    {
        "id": "config",
        "title": "config, tags, callbacks, with_config",
        "category": "Configuration",
        "tags": ["config", "tags", "callbacks", "run_name"],
        "summary": "Pass runtime metadata into every step. Useful for LangSmith traces and per-request knobs.",
        "when": "Naming runs, tagging environments, attaching callbacks, or setting recursion limits.",
        "openai": '''from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

chain = (
    ChatPromptTemplate.from_template("{q}")
    | ChatOpenAI(model="gpt-4o-mini")
).with_config({"run_name": "lcel-demo", "tags": ["cheatsheet"]})

chain.invoke(
    {"q": "ping"},
    config={"configurable": {}, "metadata": {"user": "dev"}},
)
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

chain = (
    ChatPromptTemplate.from_template("{q}")
    | ChatAnthropic(model="claude-3-5-haiku-latest")
).with_config({"run_name": "lcel-demo", "tags": ["cheatsheet"]})

chain.invoke({"q": "ping"}, config={"metadata": {"user": "dev"}})
''',
        "notes": "`configurable` fields are how `RunnableWithMessageHistory` and `configurable_fields` receive per-call values.",
    },
    {
        "id": "configurable-alt",
        "title": "configurable_alternatives — swap models live",
        "category": "Configuration",
        "tags": ["configurable", "openai", "anthropic", "ab"],
        "summary": "Declare OpenAI as default and Anthropic as an alternative selected via config.",
        "when": "One deployed graph, caller chooses the provider per request.",
        "openai": '''from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

model = ChatOpenAI(model="gpt-4o-mini").configurable_alternatives(
    "model",
    default_key="openai",
    anthropic=ChatAnthropic(model="claude-3-5-haiku-latest"),
)
chain = ChatPromptTemplate.from_template("{q}") | model | StrOutputParser()

chain.invoke({"q": "Define LCEL"}, config={"configurable": {"model": "openai"}})
chain.invoke({"q": "Define LCEL"}, config={"configurable": {"model": "anthropic"}})
''',
        "anthropic": '''from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Same graph — Anthropic selected at invoke time
model = ChatOpenAI(model="gpt-4o-mini").configurable_alternatives(
    "model",
    default_key="openai",
    anthropic=ChatAnthropic(model="claude-3-5-haiku-latest"),
)
chain = ChatPromptTemplate.from_template("{q}") | model | StrOutputParser()
print(chain.invoke({"q": "Define LCEL"}, config={"configurable": {"model": "anthropic"}}))
''',
        "notes": "Great for A/B tests. Missing alternative keys raise at invoke, not at graph-build time.",
    },
    {
        "id": "graph",
        "title": "get_graph() and get_prompts()",
        "category": "Configuration",
        "tags": ["graph", "debug", "inspect"],
        "summary": "Inspect a compiled LCEL chain: ASCII graph, prompts, and input schema.",
        "when": "Debugging a pipe that 'should work' or generating docs for a chain.",
        "openai": '''from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

chain = (
    ChatPromptTemplate.from_template("{q}")
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)
chain.get_graph().print_ascii()
print(chain.get_prompts())
print(chain.input_schema.model_json_schema())
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

chain = (
    ChatPromptTemplate.from_template("{q}")
    | ChatAnthropic(model="claude-3-5-haiku-latest")
    | StrOutputParser()
)
chain.get_graph().print_ascii()
print(chain.get_prompts())
print(chain.input_schema.model_json_schema())
''',
        "notes": "ASCII graphs are ideal for cheatsheets and code reviews. They work the same for both providers.",
    },
    {
        "id": "partial",
        "title": "partial() — bake variables early",
        "category": "Prompts & Models",
        "tags": ["partial", "prompt", "defaults"],
        "summary": "Fill some template variables now, leave the rest for invoke.",
        "when": "Shared system style, format instructions, or tenant-specific preamble.",
        "openai": '''from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template(
    "Style: {style}\\nUser: {q}"
).partial(style="terse bullet points")

chain = prompt | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()
print(chain.invoke({"q": "Name 3 LCEL primitives"}))
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template(
    "Style: {style}\\nUser: {q}"
).partial(style="terse bullet points")

chain = prompt | ChatAnthropic(model="claude-3-5-haiku-latest") | StrOutputParser()
print(chain.invoke({"q": "Name 3 LCEL primitives"}))
''',
        "notes": "`partial` accepts values or callables (lazy). Useful for `get_format_instructions()`.",
    },
    {
        "id": "map",
        "title": "map() — apply a chain per list item",
        "category": "Parallelism",
        "tags": ["map", "batch", "list"],
        "summary": "Turn a chain that handles one item into one that handles a list, concurrently.",
        "when": "Summarize each retrieved chunk, or classify a batch of tickets.",
        "openai": '''from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

one = (
    ChatPromptTemplate.from_template("Tag this in 1 word: {text}")
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)
many = one.map()
print(many.invoke([
    {"text": "pipe operator"},
    {"text": "fallback chain"},
]))
''',
        "anthropic": '''from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

one = (
    ChatPromptTemplate.from_template("Tag this in 1 word: {text}")
    | ChatAnthropic(model="claude-3-5-haiku-latest")
    | StrOutputParser()
)
many = one.map()
print(many.invoke([{"text": "pipe operator"}, {"text": "fallback chain"}]))
''',
        "notes": "Control fan-out with `config={'max_concurrency': 4}`. Different from `batch`, which maps over invoke inputs of the same chain.",
    },
]

QUICK_REF = [
    ("`a | b | c`", "RunnableSequence — left-to-right composition"),
    ("`{'k': r}` in a pipe", "RunnableParallel — same input, concurrent branches"),
    ("`RunnablePassthrough()`", "Forward input unchanged"),
    ("`.assign(k=r)`", "Merge new keys into a dict input"),
    ("`.pick([...])`", "Keep only listed keys"),
    ("`RunnableLambda(fn)` / `@chain`", "Wrap a Python function"),
    ("`.bind(**kwargs)`", "Freeze model/tool/stop kwargs"),
    ("`.bind_tools([fn])`", "Advertise tools to the chat model"),
    ("`.with_structured_output(Model)`", "Typed Pydantic/JSON result"),
    ("`.with_fallbacks([other])`", "Try next Runnable on failure"),
    ("`.with_retry(...)`", "Retry transient errors"),
    ("`.with_config({...})`", "Default run name, tags, metadata"),
    ("`.configurable_alternatives`", "Swap OpenAI/Anthropic at invoke time"),
    ("`.map()`", "Apply chain to each list item"),
    ("`.invoke / .stream / .batch / .ainvoke`", "Standard execution API"),
    ("`.get_graph().print_ascii()`", "Debug the compiled graph"),
]


def filter_entries(query: str = "", category: str = "All") -> list[dict[str, Any]]:
    q = (query or "").strip().lower()
    scored: list[tuple[int, dict[str, Any]]] = []
    for entry in ENTRIES:
        if category not in ("All", "", None) and entry["category"] != category:
            continue
        if not q:
            scored.append((0, entry))
            continue
        title_blob = f"{entry['id']} {entry['title']} {' '.join(entry['tags'])}".lower()
        meta_blob = f"{entry['summary']} {entry['when']} {entry['notes']} {entry['category']}".lower()
        code_blob = f"{entry['openai']} {entry['anthropic']}".lower()
        if q in title_blob:
            scored.append((0, entry))
        elif q in meta_blob:
            scored.append((1, entry))
        elif q in code_blob:
            scored.append((2, entry))
    scored.sort(key=lambda item: item[0])
    return [entry for _, entry in scored]


def by_id(entry_id: str) -> dict[str, Any] | None:
    for entry in ENTRIES:
        if entry["id"] == entry_id:
            return entry
    return None


def titles_for(entries: list[dict[str, Any]]) -> list[str]:
    return [f"{e['title']}  ·  {e['category']}" for e in entries]


def entry_from_label(label: str) -> dict[str, Any] | None:
    title = label.split("  ·  ")[0].strip() if label else ""
    for entry in ENTRIES:
        if entry["title"] == title:
            return entry
    return ENTRIES[0] if ENTRIES else None
