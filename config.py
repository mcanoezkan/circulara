"""Configuration for the Circular Readiness assessment model."""

from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path

DEFAULT_WEIGHTS = {
    "Design": 0.35,
    "Strategie": 0.20,
    "Wirtschaftlichkeit": 0.15,
    "Regulatorik": 0.15,
    "Systemische Befähiger": 0.15,
}

QUESTION_TYPES = ["mc"]

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

MODEL_PATH = DATA_DIR / "circular_model.json"
MATURITY_PATH = DATA_DIR / "maturity_levels.json"
RECOMMENDATIONS_PATH = DATA_DIR / "indicator_recommendations.json"

DEFAULT_MATURITY_LEVELS = [
    {
        "min_score": 0.0,
        "max_score": 0.25,
        "name": "Stufe 1",
        "label": "Inert",
        "emoji": "🔴",
        "description": "Es liegen keine Erfahrungen und nur minimales Wissen zur systematischen Umsetzung zirkulärer Prinzipien vor; der Nutzen der Integration zirkulärer Prinzipien in die Produktgestaltung wird nicht erkannt.",
    },
    {
        "min_score": 0.25,
        "max_score": 0.5,
        "name": "Stufe 2",
        "label": "Conversant",
        "emoji": "🟠",
        "description": "Erste Aktivitäten bzgl. Kreislaufwirtschaft sind vorhanden und die Relevanz zirkulärer Prinzipien wird grundsätzlich anerkannt; die Umsetzung erfolgt jedoch punktuell und mit geringer Ausprägung externer Zusammenarbeit entlang der Wertschöpfungskette.",
    },
    {
        "min_score": 0.5,
        "max_score": 0.75,
        "name": "Stufe 3",
        "label": "Applied",
        "emoji": "🟡",
        "description": "Zirkuläre Strategien werden in konkreten Entwicklungsprojekten angewandt und über Lebenszyklusphasen hinweg berücksichtigt; Daten werden als Entscheidungsinput genutzt, einschließlich lebenszyklusbezogener Bewertungen; die Zusammenarbeit mit Anspruchsgruppen nimmt zu.",
    },
    {
        "min_score": 0.75,
        "max_score": 1.0,
        "name": "Stufe 4",
        "label": "Monitored",
        "emoji": "🟢",
        "description": "Die Integration zirkulärer Prinzipien ist proaktiv und in einer etablierten Struktur verankert; die Bewertung erfolgt mittels Indikatoren und quantitativer Metriken, um die Leistungsfähigkeit der zirkulären Strategien zu messen und zu steuern.",
    },
    {
        "min_score": 1.0,
        "max_score": 1.01,
        "name": "Stufe 5",
        "label": "Optimized",
        "emoji": "🟣",
        "description": "Zirkuläre Leistungsfähigkeit wird kontinuierlich verbessert; Ergebnisse aus Indikatoren werden systematisch als Input für Optimierungen genutzt; die Zusammenarbeit mit Anspruchsgruppen wird fortlaufend weiterentwickelt; Reife wird als dynamischer Entwicklungszustand verstanden.",
    },
]


def _load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Konfigurationsdatei nicht gefunden: {path}")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _load_model() -> OrderedDict[str, dict]:
    data = _load_json(MODEL_PATH)
    return OrderedDict(
        (theme, OrderedDict((indicator, indicator_data) for indicator, indicator_data in indicators.items()))
        for theme, indicators in data.items()
    )


CIRCULAR_MODEL = _load_model()
MATURITY_LEVELS = _load_json(MATURITY_PATH) or DEFAULT_MATURITY_LEVELS
INDICATOR_RECOMMENDATIONS = _load_json(RECOMMENDATIONS_PATH)
