import os
from dotenv import load_dotenv
import requests
load_dotenv()


MAX_TOKENS = 4096
TIMEOUT = 60.0
LLM_SETTINGS = {
    "llm_provider": "openai",
    "llm_model": "gpt-4o",
    "max_tokens": MAX_TOKENS,
    "k": 8,
    "min_score": 0.4,
    "temperature": 0.1,
}
SYSTEM_PROMPT = "\"\"\"Responde preguntas sobre inversiones inmobiliarias que encuentre en el contexto proporcionado.\"\"\""


def ask_llm(query: str) -> str:
    url = f"https://api.edenai.run/v2/aiproducts/askyoda/v2/{os.getenv('RAG_PROJECT_ID')}/ask_llm/"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer " + (os.getenv("EDENAI_API_KEY") or ""),
    }
    payload = {
        **LLM_SETTINGS,
        "question": query,
        "chatbot_global_action": SYSTEM_PROMPT,
    }
    response = requests.post(url, headers=headers,
                             json=payload, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()

    return data.get("response", data.get("result", "No response received"))