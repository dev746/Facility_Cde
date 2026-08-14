# Semantic Replies, Multilingual Support & Cross-Dataset Robustness

## Background

The current bot produces template-formatted replies (hardcoded emoji + field labels). While functional, they feel robotic and break down when the asset name or data doesn't fit the template. The goal is to:

1. Generate **natural, conversational replies** in English/Hindi/Kannada/Hinglish via LLM.
2. Make intent parsing and asset resolution **work on any dataset** — no asset code assumptions.
3. Thorough **audit and hardening** of every layer.

---

## Audit Findings

| Layer | Issue |
|-------|-------|
| `query/intent.py` | `ASSET_PATTERN` only matches codes like `M14` — misses asset names mid-sentence |
| `query/intent.py` | `_keyword_parse` returns first matching keyword; order-dependent bugs with overlapping words |
| `query/engine.py` | `find_asset_by_name` sends full sentence to pg_trgm — dilutes similarity score |
| `whatsapp/commands.py` | All replies are hardcoded templates — no language adaptability |
| `whatsapp/commands.py` | `_resolve` passes full raw text to fuzzy match (e.g. "where is the hydraulic press") |
| `core/llm.py` | `chat_json` still fails when model outputs >512 tokens of thinking before JSON |
| `rag/retriever.py` | No language detection — English-only prompt even for Hindi questions |
| `ingestion/universal.py` | `ROUTES` for `bim_json`/`ifc_json` passes to `make_bim_element` but normalisers still produce `(assets, findings)` tuples, not medium dicts |
| `core/db.py` | `executemany` uses psycopg but doesn't use `%s` format — will fail on any batch write |

---

## Proposed Changes

### Component 1 — `core/llm.py` (LLM client hardening)

#### [MODIFY] [llm.py](file:///c:/Users/devan/Documents/GitHub/facility_cde_v2/core/llm.py)

- Add `chat_natural(system, user, language, context_data)` — generates a full conversational reply given structured data and detected language.
- Strip thinking tokens more robustly with a greedy `<think>` remover.
- Add `detect_language(text) -> str` returning `"english"`, `"hindi"`, `"kannada"`, or `"hinglish"`.

---

### Component 2 — `query/intent.py` (Multilingual intent parser)

#### [MODIFY] [intent.py](file:///c:/Users/devan/Documents/GitHub/facility_cde_v2/query/intent.py)

- Extend `KEYWORDS` with **Hindi and Kannada** trigger words.
- Add `_extract_asset_name(text)` — strips command words and filler words to extract the bare noun phrase (e.g. "where is the hydraulic press" → "hydraulic press").
- Replace `ASSET_PATTERN` with a two-pass: (a) code pattern `M14`, (b) asset name extraction for fuzzy lookup.
- Fix keyword priority ordering (most specific → least specific).

---

### Component 3 — `query/engine.py` (Cross-dataset asset resolution)

#### [MODIFY] [engine.py](file:///c:/Users/devan/Documents/GitHub/facility_cde_v2/query/engine.py)

- Update `find_asset_by_name(name)` to **strip filler words** before sending to `core.find_asset_by_name` — prevents dilution of trigram scores.
- Add `resolve_asset(raw_text) -> dict | None` — tries (1) exact ID match, (2) trigram on extracted noun, (3) full-text similarity as last resort. Works against any dataset regardless of naming convention.
- Add `get_cross_references(asset_id)` — pulls rows from `core.cross_references` so any related records across schemas appear in replies.

---

### Component 4 — `query/responder.py` (NEW — LLM reply generator)

#### [NEW] [responder.py](file:///c:/Users/devan/Documents/GitHub/facility_cde_v2/query/responder.py)

New module that converts structured DB data into a natural language reply using the LLM:

```python
def generate_reply(intent, data, language, user_question) -> str:
    """
    Sends structured data + intent + detected language to LLM.
    Returns a warm, conversational, WhatsApp-formatted reply.
    """
```

- The LLM is given: intent, all relevant DB rows as JSON, the user's original question, and the detected language.
- The system prompt instructs the model to reply in that language (Hindi/Kannada/Hinglish/English), using WhatsApp-friendly formatting.
- Falls back gracefully to the existing template formatters if the LLM call fails.

---

### Component 5 — `whatsapp/commands.py` (Wire responder into dispatch)

#### [MODIFY] [commands.py](file:///c:/Users/devan/Documents/GitHub/facility_cde_v2/whatsapp/commands.py)

- All `dispatch` handlers that currently call `fmt_*` formatters now call `responder.generate_reply(...)` first.
- The template `fmt_*` functions become the fallback.
- `_resolve` is updated to call the new `engine.resolve_asset(raw_text)` instead of passing the raw full sentence to pg_trgm.

---

### Component 6 — `requirements.txt` (Dependencies)

#### [MODIFY] [requirements.txt](file:///c:/Users/devan/Documents/GitHub/facility_cde_v2/requirements.txt)

Add:
```
langdetect>=1.0.9        # fast offline language detection
psycopg>=3.1.0           # already present
psycopg-pool>=3.2.0      # already present
asyncpg>=0.29.0          # already present
```

> [!NOTE]
> We are **not** adding the full LangChain stack (heavy dependency, ~50+ transitive packages). Instead we add **`langdetect`** for language detection (lightweight, offline) and use the existing OpenAI-compatible `core/llm.py` client — which already gives us LangChain-equivalent chaining without the bloat. If you want full LangChain later, the `query/responder.py` interface is designed so it can be swapped to `langchain.chains` without touching other files.

---

### Component 7 — Bug fixes from audit

#### [MODIFY] `core/db.py`
- Fix `executemany` to use `%s` params properly with psycopg cursor.

#### [MODIFY] `ingestion/universal.py`
- Fix `_write_batch` for BIM/IFC routes — currently expects `(assets, findings)` tuple but should route to `bim.elements` insert directly.

---

## Verification Plan

### Automated
```powershell
python -c "
import sys; sys.stdout.reconfigure(encoding='utf-8')
from query.intent import parse_intent
tests = [
    'hydraulic press kahan hai',
    'M14 ki kya problem hai',
    'summary of M14',
    'batch 1 torsion issue',
    'yantrada sthiti enu',   # Kannada: what is the machine status
]
for t in tests:
    print(parse_intent(t))
"
```

### Manual (terminal_chat.py)
- `hydraulic press kahan hai` → Hindi reply about M04
- `M14 ki kya problem hai` → Hindi findings list for M14
- `yantrada sthiti enu` → Kannada reply about machine status
- `summary M14` → Cross-functional summary with LLM narrative
- `where is batch 1` → Resolves BATCH1 regardless of dataset naming

---

## Open Questions

> [!IMPORTANT]
> **Language scope**: Should the bot always reply in the **same language** the user wrote in, or always in English with Hindi/Kannada terms mixed in (Hinglish style)? The current plan replies in the detected language. Let me know if you prefer a fixed language or a different mixing rule.

> [!NOTE]
> **LangChain vs raw LLM**: Full LangChain adds ~200MB of dependencies and requires restructuring chains. The current plan achieves the same semantic reply quality with the existing OpenAI-compatible client + a new `responder.py`. Recommend this lighter approach unless you specifically need LangChain's agents/tools ecosystem.
