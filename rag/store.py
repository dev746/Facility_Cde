import chromadb

_client = chromadb.PersistentClient(path="data/vectorstore")
_col    = _client.get_or_create_collection("facility_docs")


def upsert(doc_id: str, text: str, embedding: list, meta: dict):
    _col.upsert(ids=[doc_id], embeddings=[embedding],
                documents=[text], metadatas=[meta])


def search(embedding: list, n: int = 5) -> list:
    results = _col.query(query_embeddings=[embedding], n_results=n)
    return [
        {"text": d, "meta": m}
        for d, m in zip(results["documents"][0], results["metadatas"][0])
    ]
