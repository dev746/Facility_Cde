import pandas as pd
from pathlib import Path
from rag.embedder import embed, chunk_text
from rag.store import upsert


def _extract_text(filepath: str) -> str:
    p = Path(filepath)
    if p.suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(filepath)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if p.suffix in (".xlsx", ".xls"):
        return pd.read_excel(filepath).to_string(index=False)
    if p.suffix == ".csv":
        return pd.read_csv(filepath).to_string(index=False)
    return p.read_text(encoding="utf-8", errors="ignore")


def ingest_document(filepath: str, source_label: str = "") -> int:
    text   = _extract_text(filepath)
    chunks = chunk_text(text)
    fname  = Path(filepath).name

    for i, chunk in enumerate(chunks):
        upsert(
            doc_id=f"{fname}_{i}",
            text=chunk,
            embedding=embed(chunk),
            meta={"source": fname, "label": source_label, "chunk": i},
        )

    print(f"[rag] {fname} → {len(chunks)} chunks")
    return len(chunks)
