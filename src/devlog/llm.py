import requests

DEFAULT_URL = "http://localhost:11434"


def generate(
    prompt: str,
    model: str = "llama3",
    base_url: str = DEFAULT_URL,
    system: str | None = None,
) -> str:
    """Call the Ollama /api/generate endpoint and return the response text."""
    payload: dict = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    if system:
        payload["system"] = system

    resp = requests.post(f"{base_url}/api/generate", json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["response"]