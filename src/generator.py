import requests
import os

def generate_response(prompt: str):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment variables.")

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o",  # or gpt-3.5-turbo
        "messages": [
            {"role": "system", "content": "You are a helpful, concise support assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
