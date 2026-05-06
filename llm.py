"""Ollama client for dynamic, consulting-style recommendations.

Requires Ollama running locally (http://localhost:11434) with the model
qwen3.5:4b pulled (`ollama pull qwen3.5:4b`).
"""

from __future__ import annotations

import json
import re
from typing import Iterator, List, Dict, Optional, Any

import requests

OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen3.5:4b"

# Maximize the model: large context, long answers, balanced sampling.
DEFAULT_OPTIONS: Dict[str, Any] = {
    "temperature": 0.5,
    "top_p": 0.9,
    "top_k": 40,
    "repeat_penalty": 1.1,
    "num_ctx": 8192,
    "num_predict": 1024,
}


def is_available(timeout: float = 2.0) -> bool:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=timeout)
        return r.ok
    except Exception:
        return False


def _options(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    opts = dict(DEFAULT_OPTIONS)
    if overrides:
        opts.update(overrides)
    return opts


def query_ollama(
    messages: List[Dict[str, str]],
    options: Optional[Dict[str, Any]] = None,
    model: str = DEFAULT_MODEL,
    json_mode: bool = False,
    timeout: float = 180.0,
) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": _options(options),
        "think": False,
    }
    if json_mode:
        payload["format"] = "json"
    res = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=timeout)
    res.raise_for_status()
    return res.json()["message"]["content"]


def stream_ollama(
    messages: List[Dict[str, str]],
    options: Optional[Dict[str, Any]] = None,
    model: str = DEFAULT_MODEL,
    timeout: float = 240.0,
) -> Iterator[str]:
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": _options(options),
        "think": False,
    }
    with requests.post(f"{OLLAMA_URL}/api/chat", json=payload, stream=True, timeout=timeout) as res:
        res.raise_for_status()
        for line in res.iter_lines():
            if not line:
                continue
            try:
                chunk = json.loads(line.decode("utf-8"))
            except json.JSONDecodeError:
                continue
            piece = (chunk.get("message") or {}).get("content")
            if piece:
                yield piece
            if chunk.get("done"):
                break


# ────────────────────────────────────────────────────────────────────────────
# CONSULTING-STYLE PROMPTS
# ────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT_DE = (
    "Du bist ein erfahrener Praxisberater für Kreislaufwirtschaft. "
    "Du arbeitest direkt mit den Verantwortlichen im Unternehmen und führst sie "
    "Schritt für Schritt durch die Umsetzung konkreter Maßnahmen — wie ein "
    "Coach, nicht wie ein Lehrbuch. "
    "Du redest auf Deutsch, klar, knapp, immer auf den nächsten machbaren Schritt fokussiert. "
    "Vermeide Stakeholder-Listen, theoretische Frameworks und Floskeln. "
    "Nutze konkrete Beispiele aus dem genannten Produktkontext. "
    "Wenn etwas unklar ist, frag nach."
)


def _context_block(
    *, product: str, company: str, sector: str,
    theme: str, indicator: str, score_pct: int, base_recommendation: str,
) -> str:
    return (
        f"Produkt: {product or 'nicht angegeben'}\n"
        f"Unternehmen: {company or 'nicht angegeben'}\n"
        f"Sektor: {sector or 'nicht angegeben'}\n"
        f"Dimension: {theme}\n"
        f"Indikator: {indicator}\n"
        f"Aktuelle Bewertung: {score_pct}% (unter 50%)\n\n"
        f"Standardempfehlung aus Anhang III:\n{base_recommendation}"
    )


def build_measures_messages(
    *, product: str, company: str, sector: str,
    theme: str, indicator: str, score_pct: int, base_recommendation: str,
) -> List[Dict[str, str]]:
    """Initial turn: ask for 4-6 concrete, named measures as JSON."""
    context = _context_block(
        product=product, company=company, sector=sector,
        theme=theme, indicator=indicator, score_pct=score_pct,
        base_recommendation=base_recommendation,
    )
    user = (
        f"{context}\n\n"
        f"Schlage 4 bis 6 konkrete Maßnahmen vor, die das Unternehmen für "
        f"diesen Indikator umsetzen kann. Gib das Ergebnis als JSON zurück, "
        f"genau in diesem Schema:\n"
        f'{{ "massnahmen": [ '
        f'{{ "titel": "Kurzer prägnanter Titel (max 8 Wörter)", '
        f'"kurz": "Ein Satz, was die Maßnahme bewirkt." }} '
        f'] }}\n\n'
        f"Wichtig: präzise Titel, deutsch, auf das Produkt zugeschnitten. "
        f"Keine Erklärtexte vor oder nach dem JSON."
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT_DE},
        {"role": "user", "content": user},
    ]


def parse_measures(raw: str) -> List[Dict[str, str]]:
    """Robust extraction of measures from the model output."""
    # Try direct JSON
    candidates: List[Dict[str, str]] = []
    text = raw.strip()
    try:
        data = json.loads(text)
    except Exception:
        # Extract first JSON object
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                data = json.loads(m.group(0))
            except Exception:
                data = None
        else:
            data = None

    if isinstance(data, dict) and isinstance(data.get("massnahmen"), list):
        for item in data["massnahmen"]:
            if isinstance(item, dict):
                titel = (item.get("titel") or item.get("title") or "").strip()
                kurz = (item.get("kurz") or item.get("summary") or item.get("beschreibung") or "").strip()
                if titel:
                    candidates.append({"titel": titel, "kurz": kurz})
    return candidates


def build_drilldown_messages(
    *, product: str, company: str, sector: str,
    theme: str, indicator: str, score_pct: int, base_recommendation: str,
    measure_title: str, measure_summary: str,
) -> List[Dict[str, str]]:
    """User clicked a specific measure: deep, hands-on consulting."""
    context = _context_block(
        product=product, company=company, sector=sector,
        theme=theme, indicator=indicator, score_pct=score_pct,
        base_recommendation=base_recommendation,
    )
    user = (
        f"{context}\n\n"
        f"Der Nutzer möchte folgende Maßnahme umsetzen:\n"
        f"**{measure_title}** — {measure_summary}\n\n"
        f"Coache ihn jetzt konkret durch die Umsetzung. Struktur:\n"
        f"1. **Worauf es bei dieser Maßnahme ankommt** (2-3 Sätze)\n"
        f"2. **Voraussetzungen**, die geprüft werden müssen, bevor man startet\n"
        f"3. **Umsetzungs-Schritte** in der richtigen Reihenfolge (nummeriert, jeweils mit konkreter erster Aktion)\n"
        f"4. **Typische Stolpersteine** und wie man sie umgeht\n"
        f"5. **Wie man Erfolg misst** (eine konkrete Kennzahl)\n"
        f"6. **Was der Nutzer morgen früh als Erstes tun sollte** (eine einzige Aktion)\n\n"
        f"Sprich den Nutzer direkt an. Bezieh dich auf das Produkt. Keine Floskeln."
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT_DE},
        {"role": "user", "content": user},
    ]


def build_followup_messages(
    *, product: str, company: str, sector: str,
    theme: str, indicator: str, score_pct: int, base_recommendation: str,
    measure_title: str, measure_summary: str,
    history: List[Dict[str, str]], user_question: str,
) -> List[Dict[str, str]]:
    """Continue the conversation about a specific measure."""
    context = _context_block(
        product=product, company=company, sector=sector,
        theme=theme, indicator=indicator, score_pct=score_pct,
        base_recommendation=base_recommendation,
    )
    initial_user = (
        f"{context}\n\n"
        f"Wir besprechen die Umsetzung folgender Maßnahme:\n"
        f"**{measure_title}** — {measure_summary}\n\n"
        f"Du coachst den Nutzer praktisch durch die Realisierung. "
        f"Antworte präzise auf seine Nachfragen, immer auf den nächsten machbaren Schritt fokussiert."
    )
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT_DE},
        {"role": "user", "content": initial_user},
    ]
    # Trim history to last 10 turns to stay in context window
    messages.extend(history[-10:])
    messages.append({"role": "user", "content": user_question})
    return messages
