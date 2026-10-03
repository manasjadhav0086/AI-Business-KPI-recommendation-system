import os
import streamlit as st
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

_GROQ_CLIENT_CACHE = None

def get_groq_api_key() -> Optional[str]:
    """
    Retrieves the Groq API key from environment variables or Streamlit secrets.
    Never exposes or logs the key.
    """
    # 1. Check Streamlit secrets (production deployment)
    try:
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            key = str(st.secrets["GROQ_API_KEY"]).strip()
            if key and not key.startswith("your_"):
                return key
    except Exception:
        pass

    # 2. Check local environment variable
    env_key = os.getenv("GROQ_API_KEY", "").strip()
    if env_key and not env_key.startswith("your_"):
        return env_key

    return None

def get_groq_model() -> str:
    """
    Retrieves configured Groq model. Defaults to ultra-fast llama-3.1-8b-instant.
    """
    try:
        if hasattr(st, "secrets") and "GROQ_MODEL" in st.secrets:
            return str(st.secrets["GROQ_MODEL"]).strip()
    except Exception:
        pass

    return os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()

def get_groq_client():
    """
    Reuses persistent Groq client connection pool to minimize TLS handshake overhead.
    """
    global _GROQ_CLIENT_CACHE
    api_key = get_groq_api_key()
    if not api_key:
        return None

    if _GROQ_CLIENT_CACHE is None:
        try:
            from groq import Groq
            _GROQ_CLIENT_CACHE = Groq(api_key=api_key, timeout=10.0, max_retries=1)
        except Exception:
            return None
    return _GROQ_CLIENT_CACHE

def call_groq_llm(
    messages: List[Dict[str, str]],
    temperature: float = 0.1,
    max_tokens: int = 450
) -> Dict[str, Any]:
    """
    Executes a high-speed chat completion call to Groq API.
    Returns {"success": bool, "content": str, "source": "groq" | "fallback"}.
    """
    api_key = get_groq_api_key()
    model = get_groq_model()

    if not api_key:
        return {
            "success": False,
            "has_key": False,
            "content": (
                "🤖 **AI Analyst (Rule-Based Mode)**\n\n"
                "*Groq API Key is not configured. The AI Analyst is running in deterministic verified analytics mode.*\n\n"
                "To enable ultra-fast LLM reasoning:\n"
                "1. Add `GROQ_API_KEY=your_key_here` to your `.env` file or `st.secrets`.\n"
                "2. Get a free API key at [console.groq.com](https://console.groq.com)."
            ),
            "source": "fallback"
        }

    client = get_groq_client()
    if not client:
        return {
            "success": False,
            "has_key": True,
            "content": "⚠️ *Unable to initialize Groq client.*",
            "source": "fallback"
        }

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        content = response.choices[0].message.content
        return {
            "success": True,
            "has_key": True,
            "content": content,
            "source": "groq",
            "model": model
        }
    except Exception as e:
        error_msg = str(e)
        safe_msg = "Rate limit or auth issue." if "401" in error_msg or "429" in error_msg else "Service busy."
        return {
            "success": False,
            "has_key": True,
            "content": f"⚠️ *Groq LLM temporarily unavailable ({safe_msg}). Falling back to verified Python analytics.*",
            "source": "fallback",
            "error": safe_msg
        }
