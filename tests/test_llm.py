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
    result = generate("Say hello", model="llama3")
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