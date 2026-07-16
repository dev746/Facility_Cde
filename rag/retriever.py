from rag.embedder import embed_query
from rag.store import search
from core.llm import chat

SYSTEM = """You are a knowledgeable industrial facility assistant for an MSME manufacturing plant.
You help workers and engineers with questions about machines, maintenance, safety, and operations.

Rules:
- Answer ONLY from the provided context
- If partially found, give what you can and say what is missing
- If not found: say exactly "This information is not in the uploaded documents."
- Use bullet points for steps or lists
- Include specific values (measurements, tolerances, intervals) when present
- Prefix safety-critical info with ⚠️
- Be concise"""


def rag_query(question: str, asset_id: str = None) -> str:
    vec     = embed_query(question)
    results = search(vec, n=5)

    if not results:
        return "❓ No relevant documents found for your question."

    context = "\n\n---\n\n".join(
        f"[Source: {r['meta']['source']} | Chunk {r['meta']['chunk']}]\n{r['text']}"
        for r in results
    )
    sources = list({r["meta"]["source"] for r in results})
    asset_ctx = f"\nThis question relates to asset: {asset_id}" if asset_id else ""

    user_msg = f"{asset_ctx}\n\nContext:\n{context}\n\nQuestion: {question}"
    answer   = chat(SYSTEM, user_msg, temperature=0.1, max_tokens=512)

    return f"{answer}\n\n📄 *Sources: {', '.join(sources)}*"
