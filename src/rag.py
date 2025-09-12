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
SYSTEM_PROMPT = "Responde preguntas sobre inversiones inmobiliarias que encuentre en el contexto proporcionado."


def ask_llm(query: str) -> str:
    url = f"https://api.edenai.run/v2/aiproducts/askyoda/v2/{os.getenv('RAG_PROJECT_ID')}/ask_llm/"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer " + (os.getenv("EDENAI_API_KEY") or ""),
    }
    payload = {
        "query": query,
        "k": 8,
        "min_score": 0.4,
        "temperature": 0.1,
        "max_tokens": 4096,
        "chatbot_global_action": SYSTEM_PROMPT,
    }
    # Retry mechanism for potential 404 errors
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers,
                                     json=payload, timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                return data.get("response", data.get("result", "No response received"))
            elif response.status_code == 404 and attempt < max_retries - 1:
                print(f"EdenAI API 404 on attempt {attempt + 1}, retrying...")
                import time
                time.sleep(1)  # Wait 1 second before retry
                continue
            else:
                print(f"EdenAI API Error {response.status_code}: {response.text}")
                return f"Error: Unable to get response from AI service (Status: {response.status_code})"
        
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                print(f"Request error on attempt {attempt + 1}, retrying: {str(e)}")
                import time
                time.sleep(1)
                continue
            else:
                print(f"Request error: {str(e)}")
                return f"Error: Failed to connect to AI service - {str(e)}"
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return f"Error: Unexpected issue occurred - {str(e)}"
    
    return "Error: Unable to get response after multiple attempts"