## Task 3: Ollama Client Wrapper

**Files:**
- Create: `src/devlog/llm.py`
- Create: `tests/test_llm.py`

**Step 1: Write the failing test (mocked HTTP)**

```python
# tests/test_llm.py
from unittest.mock import patch, MagicMock

from devlog.llm import generate


def _mock_response(text: str) -> MagicMock:
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"response": text}
    return resp


@patch("devlog.llm.requests.post")
def test_generate_returns_text(mock_post):
    mock_post.return_value = _mock_response("Hello from Ollama")
    result = generate("Say hello", model="qwen3:8b")
    assert result == "Hello from Ollama"


@patch("devlog.llm.requests.post")
def test_generate_sends_correct_payload(mock_post):
    mock_post.return_value = _mock_response("ok")
    generate("my prompt", model="mistral")
    call_kwargs = mock_post.call_args
    body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
    assert body["model"] == "mistral"
    assert body["prompt"] == "my prompt"


@patch("devlog.llm.requests.post")
def test_generate_raises_on_http_error(mock_post):
    resp = MagicMock()
    resp.status_code = 500
    resp.raise_for_status.side_effect = Exception("Server Error")
    mock_post.return_value = resp
    try:
        generate("fail")
        assert False, "Should have raised"
    except Exception:
        pass
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_llm.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/devlog/llm.py
import requests

DEFAULT_URL = "http://localhost:11434"


def generate(
    prompt: str,
    model: str = "qwen3:8b",
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
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_llm.py -v
```

Expected: 3 PASS

**Step 5: Commit**

```bash
git add src/devlog/llm.py tests/test_llm.py
git commit -m "feat: add Ollama LLM client wrapper"
```
