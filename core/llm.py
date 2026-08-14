"""
Central LLM client — Nemotron Nano 3 via NVIDIA API (OpenAI-compatible).
All modules import from here. Swap model in .env without touching other files.
"""
import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = None
_model = None

def get_client() -> OpenAI:
    """Lazy singleton — reads env vars on first call so .env is always loaded first."""
    global _client
    if _client is None:
        api_key = (
            os.getenv("NEMOTRON_API_KEY")
            or os.getenv("OPENROUTER_API_KEY")
            or os.getenv("OPENAI_API_KEY", "")
        )
        base_url = (
            os.getenv("NEMOTRON_BASE_URL")
            or os.getenv("OPENAI_BASE_URL")
            # Correct NVIDIA endpoint — matches .env.example
            or "https://integrate.api.nvidia.com/v1"
        )
        _client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000"),
                "X-Title": "Facility CDE",
            },
        )
    return _client


def get_model() -> str:
    """Lazy model name — reads env vars on first call."""
    global _model
    if _model is None:
        _model = (
            os.getenv("NEMOTRON_MODEL")
            or os.getenv("OPENROUTER_MODEL")
            or "nvidia/llama-3.1-nemotron-nano-8b-v1"
        )
    return _model


# Backwards-compatible module-level alias (read lazily on first access)
class _LazyModel(str):
    """Thin str subclass that resolves the model name on first use."""
    _resolved: str | None = None

    def __new__(cls):
        return super().__new__(cls, "")

    def _resolve(self) -> str:
        if self._resolved is None:
            self._resolved = get_model()
        return self._resolved

    def __str__(self):  return self._resolve()
    def __repr__(self): return repr(self._resolve())
    def __eq__(self, other): return self._resolve() == other
    def __hash__(self):      return hash(self._resolve())


MODEL = _LazyModel()


def chat(system: str, user: str, temperature: float = 0.2, max_tokens: int = 512, json_mode: bool = False) -> str:
    """Single call wrapper. Returns text or raises. Includes automatic fallback to alternate free models on 429/502/503."""
    client = get_client()
    
    primary_model = get_model()
    # Define a list of fallback free models in case of rate limits or service exhaustion
    fallback_models = [
        "nvidia/nemotron-3.5-lightning:free",
        "liquid/lfm-2.5-2.6b:free",
        "google/gemma-4-26b-a4b-it:free",
        "openai/gpt-oss-20b:free",
    ]
    
    # Put the primary model at the start of our attempts list
    models_to_try = [primary_model]
    for model in fallback_models:
        if model != primary_model:
            models_to_try.append(model)
            
    last_err = None
    for model_name in models_to_try:
        try:
            kwargs = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            resp = client.chat.completions.create(**kwargs)
            if not resp or not getattr(resp, "choices", None) or not resp.choices:
                raise ValueError(f"Invalid API response: {resp}")
            first_choice = resp.choices[0]
            if not first_choice:
                raise ValueError("API response choices[0] is None")
            msg = getattr(first_choice, "message", None)
            if not msg:
                raise ValueError("API response message is None")
            content = getattr(msg, "content", None)
            if content is None and isinstance(msg, dict):
                content = msg.get("content")
            if not content:
                raise ValueError("API response content is empty or None")
            return content.strip()
        except Exception as e:
            last_err = e
            # Log the failure and try next model
            print(f"[llm] Model '{model_name}' failed: {e}. Trying next fallback...")
            continue
            
    # If all OpenRouter models failed, try direct Google Gemini API as ultimate fallback
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key:
        print("[llm] Attempting ultimate fallback to direct Google Gemini API...")
        try:
            import google.generativeai as genai
            genai.configure(api_key=google_api_key)
            # Use gemini-2.5-flash as the fallback model
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # Combine system instruction and user prompt for Gemini API
            prompt = f"System Instruction:\n{system}\n\nUser Query:\n{user}"
            response = model.generate_content(
                prompt,
                generation_config={"temperature": temperature, "max_output_tokens": max_tokens}
            )
            if response and response.text:
                return response.text.strip()
        except Exception as gemini_err:
            print(f"[llm] Ultimate direct Gemini fallback failed: {gemini_err}")
            
    # If everything failed, raise the last encountered exception
    raise last_err or ValueError("All chat completion models failed.")


def chat_json(system: str, user: str, max_tokens: int = 256) -> str:
    """For structured JSON outputs — lower temperature, explicit format reminder."""
    system_with_reminder = system + "\n\nCRITICAL: Reply ONLY with valid JSON. Do NOT output thinking, explanations, or code fences. Start directly with '{'."
    raw = chat(system_with_reminder, user, temperature=0.1, max_tokens=max_tokens, json_mode=False)
    
    # Strip thinking blocks if present
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
    cleaned = re.sub(r"```json|```", "", raw).strip()
    
    start_obj = cleaned.find('{')
    start_arr = cleaned.find('[')
    
    start = -1
    end = -1
    if start_obj != -1 and (start_arr == -1 or start_obj < start_arr):
        start = start_obj
        end = cleaned.rfind('}')
    elif start_arr != -1:
        start = start_arr
        end = cleaned.rfind(']')
        
    if start != -1 and end != -1 and end > start:
        return cleaned[start:end+1]
        
    return cleaned


def detect_language(text: str) -> str:
    """Detects if text is english, hindi, kannada, or hinglish."""
    if not text or not text.strip():
        return "english"
    
    # Check Unicode script ranges first
    if re.search(r'[\u0C80-\u0CFF]', text):
        return "kannada"
    if re.search(r'[\u0900-\u097F]', text):
        return "hindi"
        
    # Check Hinglish keywords
    hinglish_words = {"kahan", "hai", "kya", "kaise", "kab", "kisko", "chahiye", "problem", "kitna", "batao", "dikhao", "yahan", "par"}
    words = set(re.findall(r'\w+', text.lower()))
    if len(words.intersection(hinglish_words)) >= 1:
        return "hinglish"
        
    try:
        from langdetect import detect
        lang = detect(text)
        if lang == 'kn':
            return "kannada"
        elif lang == 'hi':
            return "hindi"
    except Exception:
        pass
        
    return "english"


def chat_natural(system: str, user: str, language: str = "english", context_data: dict = None, temperature: float = 0.4, max_tokens: int = 600) -> str:
    """Generates natural, conversational reply in the requested language given structured context."""
    lang_instructions = {
        "hindi": "Respond in warm, clear Hindi (using Devanagari script or natural Hinglish as appropriate).",
        "kannada": "Respond in warm, clear Kannada script.",
        "hinglish": "Respond in natural Hinglish (Hindi written in Roman script).",
        "english": "Respond in clear, professional, concise English.",
    }
    lang_prompt = lang_instructions.get(language.lower(), lang_instructions["english"])
    
    context_str = ""
    if context_data:
        import json
        context_str = f"\n\nCONTEXT DATA:\n{json.dumps(context_data, indent=2, default=str)}"
        
    full_system = f"{system}\n\nLANGUAGE INSTRUCTION: {lang_prompt}\nFormat for WhatsApp using *bold*, bullet points, concise lines. Keep under 1500 chars.{context_str}"
    
    raw = chat(full_system, user, temperature=temperature, max_tokens=max_tokens)
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
    return raw

