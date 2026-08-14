import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

if __name__ == "__main__":
    client = OpenAI(
        api_key=os.getenv("NEMOTRON_API_KEY") or os.getenv("OPENROUTER_API_KEY"),
        base_url=os.getenv("NEMOTRON_BASE_URL") or "https://openrouter.ai/api/v1",
    )

    try:
        resp = client.chat.completions.create(
            model=os.getenv("NEMOTRON_MODEL", "nvidia/llama-3.1-nemotron-nano-8b-instruct"),
            messages=[
                {"role": "system", "content": "You are the intent parser. Reply ONLY with valid JSON. Schema: {\"intent\": string, \"asset_id\": string or null}"},
                {"role": "user", "content": "why is the llm failing"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        print("RAW OUTPUT:", repr(resp.choices[0].message.content))
    except Exception as e:
        print("Error:", e)
