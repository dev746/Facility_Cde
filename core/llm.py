"""
Central LLM client — Nemotron Nano 3 via NVIDIA API (OpenAI-compatible).
All modules import from here. Swap model in .env without touching other files.
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("NEMOTRON_API_KEY", "no-key"),
            base_url=os.getenv("NEMOTRON_BASE_URL", "https://integrate.api.nvidia.com/v1"),
        )
    return _client


MODEL = os.getenv("NEMOTRON_MODEL", "nvidia/llama-3.1-nemotron-nano-8b-instruct")


def chat(system: str, user: str, temperature: float = 0.2, max_tokens: int = 512) -> str:
    """Single call wrapper. Returns text or raises."""
    client = get_client()
    resp   = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


def chat_json(system: str, user: str, max_tokens: int = 256) -> str:
    """For structured JSON outputs — lower temperature, explicit format reminder."""
    system_with_reminder = system + "\n\nCRITICAL: Reply ONLY with valid JSON. No markdown fences. No explanation."
    return chat(system_with_reminder, user, temperature=0.1, max_tokens=max_tokens)
