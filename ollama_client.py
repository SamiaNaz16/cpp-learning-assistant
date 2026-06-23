import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "tinyllama"


def query_ollama(prompt: str, system_prompt: str = "") -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response received from model.")
    except requests.exceptions.ConnectionError:
        return "ERROR: Cannot connect to Ollama. Make sure Ollama is running (run: ollama serve)."
    except requests.exceptions.Timeout:
        return "ERROR: Request to Ollama timed out. The model may be loading — please try again."
    except requests.exceptions.RequestException as e:
        return f"ERROR: Ollama request failed — {str(e)}"
    except json.JSONDecodeError:
        return "ERROR: Invalid response from Ollama server."