
import os
import httpx


DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-flash"


async def send_to_deepseek(message: str) -> dict:
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        raise RuntimeError("DeepSeek API key is not configured")

    if not message or len(message) > 10000:
        raise ValueError("Invalid message length")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "user", "content": message}
        ],
        "max_tokens": 512,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )

        response.raise_for_status()
        return response.json()


def check_deepseek_config() -> dict:
    return {
        "api_key_configured": bool(os.getenv("DEEPSEEK_API_KEY")),
        "base_url_configured": bool(DEEPSEEK_BASE_URL),
        "model_configured": bool(DEEPSEEK_MODEL),
    }
