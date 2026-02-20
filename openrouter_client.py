# VERSION 3 START
# Reference: OpenRouter API via OpenAI Python SDK (OpenRouter, 2024; OpenAI, 2024)
# https://openrouter.ai/docs
# https://platform.openai.com/docs/api-reference/chat
# Provides an OpenAI-compatible client configured to communicate with OpenRouter
from openai import OpenAI
from flask import current_app

# Custom error type for OpenRouter-related failures
class OpenRouterError(Exception):
    pass

# Reference: Flask application configuration access (Pallets Projects, 2024)
# https://flask.palletsprojects.com/en/stable/config/
# Creates and returns an OpenAI client configured for OpenRouter using app config
def _client() -> OpenAI:
    # Read config values from the Flask app
    cfg = current_app.config
    # Get API key from config
    key = cfg.get("OPENROUTER_API_KEY", "")
    if not key:
        # Fail early if the key is missing
        raise OpenRouterError("Missing OPENROUTER_API_KEY")

    # Create and return an OpenAI client pointed at OpenRouter
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
    )

# Reference: Defensive object-to-dictionary conversion (OpenAI SDK, 2024)
# https://platform.openai.com/docs/api-reference/chat/object
# Converts SDK response objects into dictionaries safely across SDK versions
def _to_dict(obj):
    # Convert SDK response objects into a dictionary safely

    # Newer SDK versions support model_dump()
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    
    # Fallback for older / dict-like responses
    try:
        return dict(obj)
    except Exception:
        return None

# Reference: Chat Completions API abstraction (OpenRouter, 2024)
# https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request
# Sends structured system and user prompts to an LLM and returns generated text
def chat(messages, *, model=None, temperature=0.7, max_tokens=500) -> str:
    # Main helper used by routes to send prompts to OpenRouter
    cfg = current_app.config

    # Choose model: passed in > config value > default model
    model = model or cfg.get("OPENROUTER_MODEL") or "arcee-ai/trinity-large-preview:free"

    try:
        # Send chat completion request to OpenRouter
        resp = _client().chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers={
                # Reference: Optional OpenRouter request headers (OpenRouter, 2024)
                # https://openrouter.ai/docs/api/reference/overview
                "HTTP-Referer": cfg.get("OPENROUTER_SITE_URL", ""),
                "X-Title": cfg.get("OPENROUTER_SITE_NAME", "CharityConnect"),
            },
        )

        # First attempt: access response using SDK attributes
        choices = getattr(resp, "choices", None)
        if choices and len(choices) > 0:
            msg = getattr(choices[0], "message", None)
            if msg and getattr(msg, "content", None) is not None:
                return (msg.content or "").strip()

        # Second attempt: convert response to dict and extract content
        d = _to_dict(resp)
        if d:
            # Handle OpenRouter error payloads
            if isinstance(d.get("error"), dict):
                raise OpenRouterError(d["error"].get("message", "OpenRouter error"))

            try:
                return (d["choices"][0]["message"]["content"] or "").strip()
            except Exception:
                pass
        # If no usable content was found
        raise OpenRouterError("OpenRouter returned an unexpected response (no choices).")

    except OpenRouterError:
        # Re-raise known OpenRouter errors
        raise
    except Exception as e:
        # Catch-all to avoid leaking raw exceptions into routes
        raise OpenRouterError(str(e))
# VERSION 3 END
