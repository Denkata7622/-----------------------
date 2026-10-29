#!/usr/bin/env python3
"""Тества дали response_format: json_object работи с HackClub proxy-то."""
import json
import requests
from pathlib import Path

BASE = Path(__file__).parent
cfg = json.load(open(BASE / "config.json", encoding="utf-8"))["generator"]

url = cfg["api_url"]
key = cfg["api_key"]
model = cfg["model"]

print(f"URL:   {url}")
print(f"Model: {model}")
print(f"Key:   {key[:20]}...{key[-6:]}" if key else "Key: (празен!)")
print()

headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
}

payload = {
    "model": model,
    "response_format": {"type": "json_object"},
    "messages": [
        {"role": "user", "content": 'Return valid JSON with a single key "a" and value 1.'}
    ],
    "max_tokens": 50,
}

print("Изпращам тестов request с response_format: json_object...")
print()

try:
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"HTTP {r.status_code}")
    print()
    print("Response (first 800 chars):")
    print(r.text[:800])
    print()

    if r.status_code == 200:
        try:
            data = r.json()
            content = data["choices"][0]["message"]["content"]
            print("✓ Content от модела:")
            print(repr(content))
            parsed = json.loads(content)
            print()
            print(f"✓ Парснато успешно: {parsed}")
            print()
            print("═══ РЕЗУЛТАТ: response_format: json_object РАБОТИ ═══")
        except Exception as e:
            print(f"⚠ Моделът върна 200, но content не е JSON: {e}")
    elif r.status_code == 400:
        print("═══ РЕЗУЛТАТ: response_format НЕ СЕ ПОДДЪРЖА (400) ═══")
    else:
        print(f"═══ РЕЗУЛТАТ: неочакван статус {r.status_code} ═══")

except Exception as e:
    print(f"✗ Грешка: {e}")