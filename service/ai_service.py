import httpx
import json
import re
from typing import List
from core.config import settings

GEMINI_MODEL = "models/gemini-2.5-flash-lite"
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    f"{GEMINI_MODEL}:generateContent"
)

def extract_json(text: str) -> list[dict]:
    if not text:
        raise ValueError("Empty AI response")

    # Убираем ```json ``` и ```
    text = text.strip()
    text = re.sub(r"^```json", "", text)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)
    text = text.strip()

    # Пытаемся вытащить JSON массив
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON array found in: {text[:200]}")

    return json.loads(match.group())

async def enrich_words(words: List[str]) -> List[dict]:
    prompt = f"""
Aşağıdaki Türkçe kelimeler için:

- Rusça çeviri
- Kelime türü (isim, fiil, bağlaç vb.)
- CEFR seviyesi (A1–C1)
- Konu
- Türkçe örnek cümle

SADECE JSON ARRAY döndür.
Başka hiçbir metin ekleme.

Format:
[
  {{
    "word": "kelime",
    "translation": "translation",
    "part_of_speech": "noun",
    "level": "A1",
    "topic": "food",
    "example": "örnek cümle"
  }}
]

Kelimeler:
{", ".join(words)}
"""

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{GEMINI_URL}?key={settings.GEMINI_API_KEY}",
            json={
                "contents": [
                    {"parts": [{"text": prompt}]}
                ]
            },
        )

    response.raise_for_status()
    data = response.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"]

    print("🔥 GEMINI RAW TEXT >>>", repr(text))

    return extract_json(text)
