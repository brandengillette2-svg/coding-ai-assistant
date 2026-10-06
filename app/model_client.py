import json
import os
from typing import Dict, List


class ModelClient:
    def __init__(self, provider: str | None = None, model: str | None = None, api_key: str | None = None):
        self.provider = (provider or os.getenv("MODEL_PROVIDER", "openai")).lower()
        self.model = model or os.getenv("MODEL_NAME", "gpt-4o-mini")
        self.api_key = api_key or os.getenv("MODEL_API_KEY", "")
        self.enabled = bool(self.api_key)
        self._client = None

        if self.enabled:
            if self.provider == "openai":
                try:
                    from openai import OpenAI
                except ImportError as exc:
                    raise RuntimeError("Install openai package to use OpenAI") from exc
                self._client = OpenAI(api_key=self.api_key)
            elif self.provider == "anthropic":
                try:
                    import anthropic
                except ImportError as exc:
                    raise RuntimeError("Install anthropic package to use Anthropic") from exc
                self._client = anthropic.Anthropic(api_key=self.api_key)
            else:
                raise ValueError(f"Unsupported model provider: {self.provider}")

    def _fallback_response(self, messages: List[Dict[str, str]]) -> str:
        user_text = "\n".join(msg.get("content", "") for msg in messages if msg.get("role") == "user")
        return json.dumps(
            {
                "summary": "Local planner mode active because no model API key was configured.",
                "files_to_edit": [],
                "patch_hints": [
                    "Locate the likely implementation sites by file and symbol name.",
                    "Keep the patch narrow and validate with focused tests or compile checks.",
                ],
                "verification_steps": ["pytest -q", "python -m compileall ."],
                "context": user_text[:2000],
            },
            indent=2,
        )

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.1, max_tokens: int = 1200) -> str:
        if not self.enabled:
            return self._fallback_response(messages)

        if self.provider == "openai":
            response = self._client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=messages,
            )
            return response.choices[0].message.content or ""

        if self.provider == "anthropic":
            response = self._client.messages.create(
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=messages,
            )
            text_parts = []
            for block in response.content:
                if getattr(block, "type", None) == "text":
                    text_parts.append(block.text)
            return "\n".join(text_parts)

        raise ValueError(f"Unsupported provider: {self.provider}")
