
import json
import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()  # reads .env in the project root, if present

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"

AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
]

REQUEST_TIMEOUT = 60


class LLMError(Exception):
    pass


def get_api_key() -> str | None:
    return os.environ.get("GROQ_API_KEY")


def is_configured() -> bool:
    return bool(get_api_key())


def _extract_json(text: str) -> dict:
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    candidate = fence_match.group(1) if fence_match else None

    if not candidate:
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        candidate = brace_match.group(0) if brace_match else None

    if not candidate:
        raise LLMError("No JSON object found in the model's output.")

    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        raise LLMError(f"Model returned malformed JSON: {e}")


def chat_json(system_prompt: str, user_prompt: str, model: str = DEFAULT_MODEL) -> dict:
    """Send a request to the Groq API and parse the reply as JSON."""
    api_key = get_api_key()
    if not api_key:
        raise LLMError(
            "No GROQ_API_KEY found. Add it to a .env file in the project "
            "root, e.g.:\n\nGROQ_API_KEY=gsk_your-key-here\n\n"
            "Get a free key at https://console.groq.com/keys"
        )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt + "\n\nRespond with ONLY the JSON object -- no prose, no markdown code fences."},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(GROQ_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        detail = ""
        if getattr(e, "response", None) is not None:
            detail = f" Details: {e.response.text}"
        raise LLMError(f"Groq API request failed: {e}.{detail}")

    data = resp.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    if not content:
        raise LLMError("Groq returned an empty response.")

    return _extract_json(content)
