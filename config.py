"""Configuration for the Circular Readiness assessment model."""

from __future__ import annotations

import os
import re
from collections import OrderedDict
from functools import lru_cache
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

DEFAULT_WEIGHTS = {
    "Design": 0.35,
    "Strategie": 0.20,
    "Wirtschaftlichkeit": 0.15,
    "Regulatorik": 0.15,
    "Systemische Befähiger": 0.15,
}

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

QUESTION_TYPES = ["mc"]

MODEL_DOCUMENT_PATH = Path(
    os.getenv(
        "CIRCULAR_MODEL_DOCX",
        "/Users/mehmetcan/Desktop/RWTH Master/Masterarbeit/Vorbereitung der Leitfragen/Leitfragen_Quellen_v9.docx",
    )
)

MASTER_THESIS_DOCUMENT_PATH = Path(
    os.getenv(
        "CIRCULAR_MASTER_THESIS_DOCX",
        "/Users/mehmetcan/Desktop/RWTH Master/Masterarbeit/Versionen /MA_komplet_v3.docx",
    )
)

THEME_DESCRIPTIONS = {
    "Design": "Bewertet produktseitige Voraussetzungen wie Demontage, Materialprofil und Aufbereitbarkeit.",
    "Strategie": "Bewertet Markt, Organisation und Entscheidungslogik für zirkuläre Geschäftsmodelle.",
    "Wirtschaftlichkeit": "Bewertet die ökonomische Tragfähigkeit von Rückführung und Aufbereitung.",
    "Regulatorik": "Bewertet regulatorische Voraussetzungen, Kennzeichnung und Rechte-Compliance.",
    "Systemische Befähiger": "Bewertet Datenverfügbarkeit, Rückführungssysteme und Nutzeraktivierung.",
}

INDICATOR_DESCRIPTIONS = {
    "1.1": "Bewertet zerstörungsfreie Demontage, Werkzeugeinsatz und Demontageaufwand.",
    "1.2": "Bewertet Upgradefähigkeit, Standardisierung und generationenübergreifende Kompatibilität.",
    "1.3": "Bewertet Rezyklatanteile sowie Materialtrennbarkeit für hochwertiges Recycling.",
    "1.4": "Bewertet strukturelle Restfestigkeit, Oberflächenaufbereitung und emotionale Haltbarkeit.",
    "2.1": "Bewertet Sekundärmarktattraktivität und Ersatzteilverfügbarkeit.",
    "2.2": "Bewertet Budget, Know-how und verfügbare Tools für Aufbereitung.",
    "2.3": "Bewertet Marktverständnis und Entscheidungslogik für Folgezyklen.",
    "2.4": "Bewertet Partnernetzwerke und soziale Integration zirkulärer Strategien.",
    "3.1": "Bewertet Preisniveau, Werterhalt und Lagerdauer von Rückläufern.",
    "4.1": "Bewertet Stoffrecht, rechtliche Wiederverwendung und Sicherheitskonformität.",
    "4.2": "Bewertet Software-Rechte, Kennzeichnung und Datenrückverfolgbarkeit.",
    "5.1": "Bewertet Zustandsdaten, Prognosefähigkeit und Dateninteroperabilität.",
    "5.2": "Bewertet Planbarkeit von Rückflüssen und Rückversandverpackung.",
    "5.3": "Bewertet Rückgabeunterstützung und Anreizsysteme für Endnutzer.",
}

INDICATOR_NAME_OVERRIDES = {
    "1.1": "Operative Demontierbarkeit",
    "1.2": "Standardisierung & Upgradefähigkeit",
    "1.3": "Materialprofil",
    "1.4": "Dauerhaltbarkeit & Aufbereitbarkeit",
    "2.1": "Marktattraktivität & Teileversorgung",
    "2.2": "Ressourcen, Know-how & Tools",
    "2.3": "Marktverständnis & Entscheidungslogik",
    "2.4": "Stakeholder & Soziale Integration",
    "3.1": "Wirtschaftliche Tragfähigkeit",
    "4.1": "Produkt- und Sicherheitskonformität",
    "4.2": "Daten-, Kennzeichnungs- und Rechte-Compliance",
    "5.1": "Digitale Identität & Prognose & Interoperabilität",
    "5.2": "Rückführungsinfrastruktur",
    "5.3": "Nutzeraktivierung & Rückgabeunterstützung",
}

_CODE_PATTERN = re.compile(r"^\d\.\d\.\d$")
_OPTION_START_PATTERN = re.compile(r"(?=\((?:0(?:\.\d+)?|1\.0)\))")
_OPTION_PATTERN = re.compile(r"^\((0(?:\.\d+)?|1\.0)\)\s*(.*)$")


def _extract_docx_paragraphs(path: Path) -> list[str]:
    with ZipFile(path) as archive:
        xml = archive.read("word/document.xml")

    root = ET.fromstring(xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []

    for paragraph in root.findall(".//w:p", ns):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", ns)).strip()
        if text:
            paragraphs.append(text)

    return paragraphs


def _normalize_line(text: str) -> str:
    return " ".join(text.replace("\xa0", " ").split()).strip()


def _split_embedded_options(lines: list[str]) -> list[str]:
    normalized = []
    for line in lines:
        cleaned = _normalize_line(line)
        if not cleaned:
            continue

        matches = list(_OPTION_START_PATTERN.finditer(cleaned))
        if len(matches) <= 1:
            normalized.append(cleaned)
            continue

        starts = [match.start() for match in matches] + [len(cleaned)]
        for start, end in zip(starts, starts[1:]):
            part = cleaned[start:end].strip()
            if part:
                normalized.append(part)

    return normalized


def _build_indicator_overview(paragraphs: list[str]) -> OrderedDict[str, dict]:
    start = paragraphs.index("1.1")
    end = paragraphs.index("Leitfrage Nr.")
    overview = OrderedDict()
    i = start

    while i < end:
        code = paragraphs[i]
        if not re.match(r"^\d\.\d$", code):
            i += 1
            continue

        theme = paragraphs[i + 1]
        name = paragraphs[i + 2]
        next_index = i + 4

        if theme == "Systemische" and paragraphs[i + 2] == "Befähiger":
            theme = "Systemische Befähiger"
            name = paragraphs[i + 3]
            next_index = i + 5

        overview[code] = {"theme": theme, "name": name}
        i = next_index

    return overview


def _extract_question_text(lines: list[str]) -> str:
    for index, line in enumerate(lines):
        if line.startswith("Leitfrage:"):
            text = line.split(":", 1)[1].strip()
            if text:
                return text
            if index + 1 < len(lines):
                return lines[index + 1].strip()
    raise ValueError(f"Leitfrage konnte nicht extrahiert werden: {lines[:6]}")


def _extract_explanation(lines: list[str], question_text: str) -> str:
    explanation_parts = []
    collecting = False

    for line in lines:
        if not collecting:
            if line == question_text:
                collecting = True
            elif line.startswith("Leitfrage:") and question_text in line:
                collecting = True
            continue

        if _OPTION_PATTERN.match(line):
            break
        if line.startswith("(vgl.") or line.startswith("- Quellen") or line.startswith("-weitere Quellen"):
            continue
        explanation_parts.append(line)

    explanation = " ".join(explanation_parts).strip()
    explanation = re.sub(r"\s+", " ", explanation)
    return explanation


def _extract_options(lines: list[str]) -> list[dict]:
    options = []
    for line in lines:
        match = _OPTION_PATTERN.match(line)
        if not match:
            continue
        options.append(
            {
                "label": match.group(2).strip().rstrip(".") + ".",
                "score": float(match.group(1)),
            }
        )
    return options


@lru_cache(maxsize=1)
def load_circular_model() -> OrderedDict[str, dict]:
    if not MODEL_DOCUMENT_PATH.exists():
        raise FileNotFoundError(
            f"Die Modellquelle wurde nicht gefunden: {MODEL_DOCUMENT_PATH}. "
            "Setze bei Bedarf CIRCULAR_MODEL_DOCX auf die aktuelle .docx-Datei."
        )

    paragraphs = _extract_docx_paragraphs(MODEL_DOCUMENT_PATH)
    indicator_overview = _build_indicator_overview(paragraphs)

    model = OrderedDict()
    for theme in DEFAULT_WEIGHTS:
        model[theme] = OrderedDict()

    index = 0
    while index < len(paragraphs):
        code = paragraphs[index]
        if not _CODE_PATTERN.match(code):
            index += 1
            continue

        next_index = index + 1
        block_lines = []
        while next_index < len(paragraphs) and not _CODE_PATTERN.match(paragraphs[next_index]):
            block_lines.append(paragraphs[next_index])
            next_index += 1

        block_lines = _split_embedded_options(block_lines)
        indicator_code = ".".join(code.split(".")[:2])
        indicator_meta = indicator_overview[indicator_code]
        theme = indicator_meta["theme"]
        indicator_label = INDICATOR_NAME_OVERRIDES.get(indicator_code, indicator_meta["name"])
        indicator_name = f"{indicator_code} {indicator_label}"
        question_text = _extract_question_text(block_lines)
        options = _extract_options(block_lines)

        model[theme].setdefault(
            indicator_name,
            {
                "description": INDICATOR_DESCRIPTIONS.get(indicator_code, THEME_DESCRIPTIONS.get(theme, "")),
                "questions": [],
            },
        )
        model[theme][indicator_name]["questions"].append(
            {
                "code": code,
                "text": question_text,
                "type": "mc",
                "explanation": _extract_explanation(block_lines, question_text),
                "options": options,
            }
        )
        index = next_index

    indicator_count = sum(len(indicators) for indicators in model.values())
    question_count = sum(len(indicator["questions"]) for indicators in model.values() for indicator in indicators.values())
    if indicator_count != 14 or question_count != 36:
        raise ValueError(
            f"Unerwartete Modellgröße aus {MODEL_DOCUMENT_PATH}: "
            f"{indicator_count} Indikatoren, {question_count} Fragen."
        )

    return model


CIRCULAR_MODEL = load_circular_model()


def _recommendation_keys() -> list[tuple[str, str]]:
    keys = []
    for indicators in CIRCULAR_MODEL.values():
        for indicator_name in indicators.keys():
            indicator_code = indicator_name.split(" ", 1)[0]
            indicator_label = indicator_name.split(" ", 1)[1]
            keys.append((indicator_code, indicator_label))
    return keys


@lru_cache(maxsize=1)
def load_master_thesis_metadata() -> tuple[list[dict], dict[str, str]]:
    if not MASTER_THESIS_DOCUMENT_PATH.exists():
        return DEFAULT_MATURITY_LEVELS, {}

    paragraphs = [_normalize_line(p) for p in _extract_docx_paragraphs(MASTER_THESIS_DOCUMENT_PATH)]

    maturity_levels = []
    maturity_pattern = re.compile(r'^Stufe\s+(\d+)\s+\("([^"]+)"\):\s*(.+)$')
    for line in paragraphs:
        match = maturity_pattern.match(line)
        if not match:
            continue
        stage = int(match.group(1))
        level_defaults = DEFAULT_MATURITY_LEVELS[stage - 1]
        maturity_levels.append(
            {
                "min_score": level_defaults["min_score"],
                "max_score": level_defaults["max_score"],
                "name": f"Stufe {stage}",
                "label": match.group(2),
                "emoji": level_defaults["emoji"],
                "description": match.group(3),
            }
        )

    recommendation_start = None
    for idx, line in enumerate(paragraphs):
        if line == "Anhang III Handlungsempfehlungen":
            recommendation_start = idx + 1
            break

    recommendations: dict[str, str] = {}
    if recommendation_start is not None:
        for line in paragraphs[recommendation_start:]:
            if not re.match(r"^\d\.\d\s", line):
                continue
            for indicator_code, indicator_label in _recommendation_keys():
                prefix = f"{indicator_code} {indicator_label}"
                if line.startswith(prefix):
                    recommendations[f"{indicator_code} {indicator_label}"] = line[len(prefix):].strip()
                    break

    if len(maturity_levels) != 5:
        maturity_levels = DEFAULT_MATURITY_LEVELS

    return maturity_levels, recommendations


MATURITY_LEVELS, INDICATOR_RECOMMENDATIONS = load_master_thesis_metadata()
