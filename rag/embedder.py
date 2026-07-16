import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))


def embed(text: str) -> list:
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_document",
    )
    return result["embedding"]


def embed_query(text: str) -> list:
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_query",
    )
    return result["embedding"]


def chunk_text(text: str, size: int = 400, overlap: int = 50) -> list:
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i: i + size]))
        i += size - overlap
    return [c for c in chunks if c.strip()]
