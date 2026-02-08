# ============================================================================
# CIRCULARITY FIT CHECK TOOL - STREAMLIT APP (MC INTEGRATION)
# ============================================================================
# Styled UI: top status bar, dynamic backgrounds per dimension,
# main layout with dimension list + question cards.
# Local storage via assessments.json
# ============================================================================

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import textwrap
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional
from datetime import datetime
from pathlib import Path

from config import (
    CIRCULAR_MODEL,
    DEFAULT_WEIGHTS,
    MATURITY_LEVELS,
)

from utils import (
    get_maturity_level,
    get_improvement_areas,
    create_radar_chart,
    generate_pdf_report,
)

# ============================================================================
# UI THEME (DYNAMIC BACKGROUND + CARD STYLES)
# ============================================================================

THEME_UI = {
    "Design": {"bg": "#E9FBF5", "bg2": "#F6FFFC", "accent": "#1F7E8A", "pill": "#D8F6EE"},
    "Strategie": {"bg": "#EAF3FF", "bg2": "#F6FAFF", "accent": "#2B6CB0", "pill": "#DCEBFF"},
    "Wirtschaftlichkeit": {"bg": "#FFF6E8", "bg2": "#FFFBF3", "accent": "#B7791F", "pill": "#FFE9C8"},
    "Regulatorik": {"bg": "#F3EEFF", "bg2": "#FAF7FF", "accent": "#6B46C1", "pill": "#E8DEFF"},
    "Systemische Befähiger": {"bg": "#FFF0F5", "bg2": "#FFF7FB", "accent": "#C026D3", "pill": "#FAD5E8"},
}


def inject_dynamic_theme_css(theme_name: str):
    """Inject theme-dependent CSS. Sidebar remains untouched."""
    ui = THEME_UI.get(theme_name, THEME_UI["Design"])

    st.markdown(
        f"""
<style>
  .stApp {{
    background: linear-gradient(180deg, {ui['bg']} 0%, {ui['bg2']} 65%, #FFFFFF 100%) !important;
  }}

  /* main container spacing + max width */
  [data-testid="stAppViewContainer"] > .main {{
    padding-top: 140px;
    padding-bottom: 36px;
  }}
  [data-testid="stAppViewContainer"] > .main > div {{
    max-width: 1220px;
    margin: 0 auto;
    padding-left: 22px;
    padding-right: 22px;
  }}

  /* nicer headers in main */
  h1, h2, h3 {{
    color: #0F172A !important;
    letter-spacing: -0.3px;
  }}
  h3 {{
    font-size: 26px !important;
    font-weight: 900 !important;
  }}
  /* vertical "Dimensionen" label */

  /* top status bar */
  [class*="st-key-topbar"] {{
    background: rgba(255,255,255,0.85) !important;
    border: 1px solid rgba(15,23,42,0.08) !important;
    border-radius: 16px !important;
    box-shadow: 0 12px 28px rgba(15,23,42,0.06) !important;
    margin: 6px 0 18px 0 !important;
  }}
  [class*="st-key-topbar"] .topbar-inner {{
    max-width: 1220px;
    margin: 0 auto;
    padding: 20px 20px 26px 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  [class*="st-key-topbar"] .topbar-inner * {{
    color: #0F172A !important;
    visibility: visible !important;
    opacity: 1 !important;
  }}
  .topbar-title {{
    font-size:22px !important;
    font-weight:900 !important;
    color:#0F172A !important;
    text-align:center;
    line-height:1.2;
  }}
  .topbar-sub {{
    font-size:15px !important;
    color:rgba(15,23,42,0.65) !important;
    text-align:center;
    line-height:1.2;
  }}
  .topbar-rail {{
    width:100%;
    height:8px;
    background:rgba(15,23,42,0.08);
    border-radius:999px;
    overflow:hidden;
  }}
  .topbar-fill {{
    height:8px;
    width:var(--p);
    background:{ui['accent']};
    border-radius:999px;
  }}
  .topbar-left button, .topbar-right button {{
    height:36px !important;
    min-width:36px !important;
    border-radius:10px !important;
    border:1px solid rgba(15,23,42,0.12) !important;
    background:#fff !important;
    font-weight:900 !important;
  }}
  .topbar-left, .topbar-right {{
    pointer-events: auto;
  }}

  .progress-wrap {{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:18px;
    margin-top:10px;
  }}
  .progress-rail {{
    width:100%;
    height:10px;
    background:rgba(15,23,42,0.08);
    border-radius:999px;
    overflow:hidden;
  }}
  .progress-bar {{
    height:10px;
    width:var(--p);
    background:{ui['accent']};
    border-radius:999px;
  }}
  .progress-metric {{
    min-width:110px;
    text-align:right;
    color:#0F172A;
    font-weight:900;
  }}
  .progress-metric small {{
    display:block;
    font-weight:700;
    color:rgba(15,23,42,0.6);
  }}

  /* dimension cards (left column) */
  .dim-card {{
    background: rgba(255,255,255,0.72) !important;
    border: 1px solid rgba(15,23,42,0.06) !important;
    border-radius: 20px !important;
    box-shadow: 0 12px 32px rgba(15,23,42,0.06), 0 2px 10px rgba(15,23,42,0.04) !important;
    backdrop-filter: blur(8px);
    padding: 16px 16px !important;
    margin: 0 0 12px 0 !important;
    min-height: 140px;
  }}

  .dim-card, .q-card, .indicator-card, .indicator-bar, .topbar {{
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
  }}
  .dim-card:hover, .q-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 16px 38px rgba(15,23,42,0.08), 0 4px 14px rgba(15,23,42,0.06) !important;
    border-color: rgba(15,23,42,0.10) !important;
  }}

  .dim-row {{
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:12px;
  }}

  .dim-left {{
    display:flex;
    gap:12px;
    align-items:flex-start;
  }}

  .dim-icon {{
    width:44px;
    height:44px;
    border-radius:14px;
    background: rgba(15,23,42,0.04);
    border: 1px solid rgba(15,23,42,0.08);
    display:flex;
    align-items:center;
    justify-content:center;
    font-weight:900;
    color: rgba(15,23,42,0.72);
    font-size:18px;
    flex: 0 0 auto;
    margin-top:2px;
  }}
  .dim-icon svg {{
    width: 22px;
    height: 22px;
    stroke: rgba(15,23,42,0.7);
    stroke-width: 2;
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
  }}

  .dim-title {{
    font-weight:800 !important;
    color:#0F172A;
    font-size:20px !important;
    line-height:1.15;
    margin:0;
  }}

  .dim-meta {{
    margin-top:4px;
    font-size:14.5px;
    font-weight:800;
    color: rgba(15,23,42,0.55);
  }}

  .dim-desc {{
    color:rgba(15,23,42,0.62);
    font-size:15.5px;
    margin-top:10px;
    line-height:1.5;
  }}

  /* dimension container styled like a card */
  [class*="st-key-dim-card-"] {{
    background: rgba(255,255,255,0.72) !important;
    border: 1px solid rgba(15,23,42,0.06) !important;
    border-radius: 20px !important;
    box-shadow: 0 12px 32px rgba(15,23,42,0.06), 0 2px 10px rgba(15,23,42,0.04) !important;
    backdrop-filter: blur(8px);
    padding: 16px 16px !important;
    margin: 0 0 12px 0 !important;
  }}
  .dim-arrow-in {{
    margin-top: 10px;
  }}
  .dim-arrow-in div[data-testid="stButton"] {{
    width: 100% !important;
    display: block !important;
  }}
  .dim-arrow-in div[data-testid="stButton"] > button {{
    width: 100% !important;
    height: 38px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(15,23,42,0.10) !important;
    background: rgba(255,255,255,0.92) !important;
    color: rgba(15,23,42,0.65) !important;
    font-weight: 900 !important;
    font-size: 15px !important;
    line-height: 1 !important;
    padding: 0 !important;
    box-shadow: 0 8px 18px rgba(15,23,42,0.06) !important;
  }}
  .dim-arrow-in div[data-testid="stButton"] > button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 12px 24px rgba(15,23,42,0.08) !important;
    border-color: rgba(15,23,42,0.22) !important;
  }}

  /* question card (right column) */
  /* question card container */
  [class*="st-key-q-card-"] {{
    background: rgba(255,255,255,0.72) !important;
    border: 1px solid rgba(15,23,42,0.06) !important;
    border-radius: 20px !important;
    box-shadow: 0 12px 32px rgba(15,23,42,0.06), 0 2px 10px rgba(15,23,42,0.04) !important;
    backdrop-filter: blur(8px);
    padding: 16px !important;
    margin: 0 0 16px 0 !important;
  }}
  .q-head {{
    display:flex;
    gap:10px;
    align-items:flex-start;
  }}
  .q-num {{
    width:38px;
    height:38px;
    border-radius:999px;
    background:rgba(15,23,42,0.92);
    color:#fff;
    font-weight:900;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:16px;
    margin-top:2px;
    flex: 0 0 auto;
  }}
  .q-text {{
    font-weight:900;
    color:#0F172A;
    font-size:18px;
    line-height:1.35;
  }}
  .q-head {{
    margin-bottom: 14px;
  }}

  /* score buttons (horizontal tiles) */
  /* answer buttons inside question card */
  [class*="st-key-q-card-"] div[data-testid="stButton"] {{
    width: 100% !important;
  }}
  [class*="st-key-q-card-"] div[data-testid="stButton"] > button {{
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
    border-radius: 10px !important;
    border: 1px solid rgba(15,23,42,0.12) !important;
    background: #ffffff !important;
    color: rgba(15,23,42,0.85) !important;
    padding: 9px 14px !important;
    margin-bottom: 4px !important;
    box-shadow: 0 6px 18px rgba(15,23,42,0.04) !important;
    font-weight: 600 !important;
  }}
  [class*="st-key-q-card-"] div[data-testid="stButton"] > button:hover {{
    border-color: rgba(15,23,42,0.22) !important;
    box-shadow: 0 10px 22px rgba(15,23,42,0.06) !important;
  }}
  [class*="st-key-q-card-"] div[data-testid="stButton"] > button[kind="primary"] {{
    background: {ui['pill']} !important;
    border-color: {ui['accent']} !important;
    color: #0F172A !important;
  }}

  /* indicator accordion buttons */
  .indicator-acc {{
    width: 100%;
  }}
  .indicator-acc div[data-testid="stButton"] > button {{
    width: 100% !important;
    height: 44px !important;
    border-radius: 10px !important;
    border: 1px solid rgba(15,23,42,0.14) !important;
    background: #ffffff !important;
    color: #0B1220 !important;
    font-weight: 900 !important;
    font-size: 20px !important;
    box-shadow: 0 6px 14px rgba(15,23,42,0.05) !important;
    transition: none !important;
    padding: 0 12px !important;
    text-align: left !important;
  }}
  .indicator-acc div[data-testid="stButton"] > button * {{
    font-size: 20px !important;
    font-weight: 900 !important;
    color: #0B1220 !important;
  }}
  .indicator-acc div[data-testid="stButton"] {{
    font-size: 20px !important;
    font-weight: 900 !important;
    color: #0B1220 !important;
  }}
  .indicator-acc div[data-testid="stButton"] * {{
    font-size: 20px !important;
    font-weight: 900 !important;
    color: #0B1220 !important;
  }}
  .indicator-acc div[data-testid="stButton"] > button:hover {{
    border-color: rgba(15,23,42,0.25) !important;
    box-shadow: 0 10px 22px rgba(15,23,42,0.08) !important;
  }}

  /* expander header styling for indicator section */
  div[data-testid="stExpander"] summary {{
    font-weight: 700 !important;
    font-size: 20px !important;
    padding: 12px 0 !important;
    border: none !important;
  }}
  div[data-testid="stExpander"] summary * {{
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #0B1220 !important;
  }}
  div[data-testid="stExpander"] {{
    background: #ffffff !important;
    border: none !important;
    border-radius: 16px !important;
    box-shadow: 0 10px 24px rgba(15,23,42,0.06) !important;
    padding: 8px 10px !important;
  }}
  div[data-testid="stExpander"] > details {{
    background: #ffffff !important;
    border-radius: 16px !important;
    border: none !important;
  }}
  div[data-testid="stExpander"] summary {{
    padding: 12px 12px !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
  }}
  div[data-testid="stExpander"] summary,
  div[data-testid="stExpander"] summary * {{
    background: rgba(255,255,255,0.95) !important;
  }}
  div[data-testid="stExpander"] summary::before,
  div[data-testid="stExpander"] summary::after {{
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
  }}
  div[data-testid="stExpander"] summary,
  div[data-testid="stExpander"] summary *,
  div[data-testid="stExpander"] > details {{
    border-color: transparent !important;
  }}
</style>
""",
        unsafe_allow_html=True,
    )


# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Circulara - Circularity Fit Check",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# BASE CSS (Sidebar stays as-is)
# ============================================================================

st.markdown(
    """
<style>
  [data-testid="stSidebar"]{
    background: rgba(255,255,255,0.55) !important;
    border-right: 1px solid rgba(15,23,42,0.06);
    backdrop-filter: blur(10px);
  }
  header[data-testid="stHeader"] { display: block; z-index: 1500; background: transparent; }
  [data-testid="stAppViewContainer"] > .main { padding-top: 24px; }
  div[data-testid="stStatusWidget"] { display: none !important; }
  div[data-testid="stSpinner"] { display: none !important; }
  .js-plotly-plot .plotly .loading,
  .js-plotly-plot .plotly .loading-text,
  .js-plotly-plot .plotly .plotly-loading {
    display: none !important;
  }
  .dim-icon {
    width:44px;
    height:44px;
    border-radius:14px;
    background: rgba(15,23,42,0.04);
    border: 1px solid rgba(15,23,42,0.08);
    display:flex;
    align-items:center;
    justify-content:center;
  }
  .dim-icon svg {
    width: 22px;
    height: 22px;
  }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "current_page" not in st.session_state:
    st.session_state.current_page = "welcome"

if "current_theme" not in st.session_state:
    st.session_state.current_theme = 0

if "current_indicator" not in st.session_state:
    st.session_state.current_indicator = 0

if "theme_answers" not in st.session_state:
    st.session_state.theme_answers = {}

if "weights" not in st.session_state:
    st.session_state.weights = DEFAULT_WEIGHTS.copy()

if "assessment_started" not in st.session_state:
    st.session_state.assessment_started = False
if "scroll_target" not in st.session_state:
    st.session_state.scroll_target = None


# ============================================================================
# HELPER FUNCTIONS - LOCAL STORAGE
# ============================================================================

def calculate_scores(answers):
    scores = {}
    for theme, theme_data in CIRCULAR_MODEL.items():
        scores[theme] = {}
        for indicator_name, indicator_data in theme_data.items():
            indicator_scores = []
            for question in indicator_data.get("questions", []):
                q_code = question["code"]
                score = answers.get(theme, {}).get(indicator_name, {}).get(q_code)
                if score is not None:
                    indicator_scores.append(score)

            scores[theme][indicator_name] = (
                sum(indicator_scores) / len(indicator_scores) if indicator_scores else None
            )
    return scores


def get_overall_score(scores):
    total_score = 0.0
    used_weights = 0.0
    for theme, theme_score in scores.items():
        if theme_score:
            valid_scores = [v for v in theme_score.values() if v is not None]
            theme_avg = (sum(valid_scores) / len(valid_scores)) if valid_scores else None
            weight = DEFAULT_WEIGHTS.get(theme, 0.2)
            if theme_avg is not None:
                total_score += theme_avg * weight
                used_weights += weight
    if used_weights == 0:
        return 0.0
    return (total_score / used_weights) * 5.0


def save_assessment_mc(answers, product_name="Mein Produkt", company="Mein Unternehmen"):
    assessment_data = {
        "Timestamp": datetime.now().isoformat(),
        "Produkt": product_name,
        "Unternehmen": company,
        "answers": answers,
        "scores": calculate_scores(answers),
    }

    path = Path("assessments.json")
    history = []

    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if isinstance(existing, list):
                history = existing
            elif isinstance(existing, dict):
                history = [existing]
        except Exception:
            history = []

    history.append(assessment_data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def load_assessment_history_local():
    path = Path("assessments.json")
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        return []
    except Exception:
        return []


# ============================================================================
# HELPER FUNCTIONS - UI STATE UPDATES
# ============================================================================

def _ensure_answer_state(theme: str, indicator: str):
    if theme not in st.session_state.theme_answers:
        st.session_state.theme_answers[theme] = {}
    if indicator not in st.session_state.theme_answers[theme]:
        st.session_state.theme_answers[theme][indicator] = {}


def _set_scroll_target(target: Optional[str]):
    st.session_state.scroll_target = target


def _set_current_page(page: str):
    st.session_state.current_page = page


def _start_assessment():
    st.session_state.current_page = "assessment"
    st.session_state.assessment_started = True
    st.session_state.scroll_target = "top"


def _select_answer(theme: str, indicator: str, code: str, score_value):
    _ensure_answer_state(theme, indicator)
    st.session_state.theme_answers[theme][indicator][code] = score_value
    st.session_state.scroll_target = f"q-{code}"


def _set_scroll_to_progress_top():
    st.session_state.scroll_target = "progress-top"


def _open_dimension(theme_index: int):
    st.session_state.current_page = "assessment"
    st.session_state.current_theme = theme_index
    st.session_state.current_indicator = 0
    _set_scroll_to_progress_top()


def _select_indicator(indicator_index: int):
    st.session_state.current_indicator = indicator_index
    _set_scroll_to_progress_top()


def _go_prev_indicator_or_theme():
    themes = list(CIRCULAR_MODEL.keys())
    if st.session_state.current_indicator > 0:
        st.session_state.current_indicator -= 1
    else:
        st.session_state.current_theme -= 1
        prev_theme = themes[st.session_state.current_theme]
        st.session_state.current_indicator = len(list(CIRCULAR_MODEL[prev_theme].keys())) - 1
    _set_scroll_to_progress_top()


def _go_next_indicator_or_theme():
    themes = list(CIRCULAR_MODEL.keys())
    indicators = list(CIRCULAR_MODEL[themes[st.session_state.current_theme]].keys())
    if st.session_state.current_indicator < len(indicators) - 1:
        st.session_state.current_indicator += 1
    else:
        st.session_state.current_theme += 1
        st.session_state.current_indicator = 0
    _set_scroll_to_progress_top()


def _show_results():
    st.session_state.current_page = "results"


# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown(
        """
        <div style="
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:flex-start;
            padding-top:32px;
        ">
        """,
        unsafe_allow_html=True,
    )

    logo_path = Path("assets") / "circulara-logo.png"
    if logo_path.exists():
        st.image(str(logo_path))
    else:
        st.markdown("### 🌍")

    st.markdown(
        "<hr style='margin:16px 0 12px 0; border:none; border-top:1px solid #e0e0e0;'>",
        unsafe_allow_html=True,
    )

    st.markdown("##### Navigation")

    nav_items = [
        ("Start", "welcome"),
        ("Assessment", "assessment"),
        ("Einstellungen", "settings"),
        ("Ergebnisse", "results"),
        ("Historie", "history"),
    ]
    for label, page in nav_items:
        is_active = st.session_state.current_page == page
        st.button(
            label,
            key=f"nav_{page}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
            on_click=_set_current_page,
            args=(page,),
        )

    st.markdown("---")


# ============================================================================
# PAGE: WELCOME
# ============================================================================

def render_welcome():
    st.markdown(
        textwrap.dedent(
            """
        <style>
          .stApp {
            background:
              radial-gradient(800px 360px at 12% -8%, rgba(31,126,138,0.14) 0%, rgba(31,126,138,0.0) 60%),
              radial-gradient(900px 380px at 50% -6%, rgba(43,108,176,0.12) 0%, rgba(43,108,176,0.0) 60%),
              radial-gradient(900px 380px at 90% -6%, rgba(183,121,31,0.12) 0%, rgba(183,121,31,0.0) 60%),
              radial-gradient(900px 420px at 15% 10%, rgba(107,70,193,0.10) 0%, rgba(107,70,193,0.0) 65%),
              radial-gradient(900px 420px at 85% 12%, rgba(192,38,211,0.10) 0%, rgba(192,38,211,0.0) 65%),
              #F6F7FB !important;
          }
          [data-testid="stSidebar"] { background: #EEF1F5 !important; }

          .home-hero {
            background: transparent;
            border: none;
            padding: 12px 0 8px 0;
            box-shadow: none;
            margin: 8px 0 18px 0;
            display: flex;
            flex-direction: column;
            align-items: center;
          }
          .home-row {
            display:flex;
            gap:18px;
            flex-wrap:wrap;
          }
          .home-hero { flex: 1 1 100%; }

          .home-title {
            font-size: 64px;
            font-weight: 900;
            font-style: italic;
            letter-spacing: -1px;
            color: #0F172A;
            margin: 0;
            line-height: 1.0;
            text-align: center;
          }
          .home-hero .home-subtitle { text-align:center; }
          .home-badges { justify-content:center; }
          .home-steps { justify-items:center; }

          .home-subtitle {
            margin-top: 12px;
            color: rgba(15,23,42,0.72);
            font-size: 18px;
            line-height: 1.7;
            max-width: 860px;
            text-align: center;
          }

          .home-badges {
            display:flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 14px;
          }

          .home-badge {
            display:inline-block;
            padding: 8px 12px;
            border-radius: 999px;
            border: 1px solid rgba(15,23,42,0.08);
            background: rgba(255,255,255,0.85);
            font-size: 12px;
            font-weight: 800;
            color: rgba(15,23,42,0.72);
          }

          .home-card {
            background:#fff;
            border: 1px solid rgba(15,23,42,0.08);
            border-radius: 16px;
            padding: 18px 18px;
            box-shadow: 0 10px 26px rgba(15,23,42,0.05);
            height: 100%;
            transition: transform .18s ease, box-shadow .18s ease;
            margin-bottom: 10px;
          }
          .home-card * { text-align: center; }
          .home-cards { max-width: 1100px; margin: 0 auto; }
          .home-shell {
            min-height: 0;
            display: block;
          }
          .home-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 16px 38px rgba(15,23,42,0.08);
          }

          .home-card-title {
            font-weight: 900;
            color:#0F172A;
            font-size: 17px;
            margin-bottom: 6px;
          }

          .home-card-text {
            color: rgba(15,23,42,0.68);
            font-size: 15px;
            line-height: 1.65;
          }
          .home-steps {
            margin-top: 14px;
            display:grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap:10px;
          }
          .home-step {
            background: rgba(15,23,42,0.04);
            border: 1px solid rgba(15,23,42,0.08);
            border-radius: 12px;
            padding: 10px 12px;
            font-size: 13px;
            font-weight: 800;
            color:#0F172A;
          }
        </style>
        """
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        textwrap.dedent(
            """
          <div class="home-shell">
          <div class="home-row">
            <div class="home-hero">
            <div class="home-title">Circulara</div>
            <div class="home-subtitle">
              Dein virtueller Assistent zur Bewertung der <b>Zirkularitätsreife</b> deines Produktes.
            </div>

          </div>
        </div>
        </div>
        """
        ),
        unsafe_allow_html=True,
    )

    st.markdown("<div class='home-shell'>", unsafe_allow_html=True)
    st.markdown("<div class='home-cards'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(
            """
            <div class="home-card">
              <div class="home-card-title">Einfache Bedienung</div>
              <div class="home-card-text">
                Beantworte Leitfragen pro Indikator. Keine Setup-Hürden.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="home-card">
              <div class="home-card-title">Klare Visualisierung</div>
              <div class="home-card-text">
                Radar & Detailanalysen machen Stärken/Schwächen sofort sichtbar.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="home-card">
              <div class="home-card-title">Konkrete Ableitung</div>
              <div class="home-card-text">
                Identifiziere Top-Verbesserungsfelder und exportiere einen Report für Stakeholder.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    c4, c5, c6 = st.columns(3, gap="medium")
    with c4:
        st.markdown(
            """
            <div class="home-card">
              <div class="home-card-title">Gewichtete Bewertung</div>
              <div class="home-card-text">
                Passe Dimensionen an – der Gesamtscore wird automatisch gewichtet berechnet.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            """
            <div class="home-card">
              <div class="home-card-title">Detailtiefe</div>
              <div class="home-card-text">
                Ergebnisse bis auf Leitfragen-Ebene für Auditierbarkeit und Vergleich.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c6:
        st.markdown(
            """
            <div class="home-card">
              <div class="home-card-title">Sofort nutzbar</div>
              <div class="home-card-text">
                Keine Integration nötig – direkt starten und Ergebnisse sichern.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
    st.button(
        "Assessment starten",
        use_container_width=True,
        type="primary",
        on_click=_start_assessment,
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================================
# PAGE: ASSESSMENT (UPDATED LAYOUT)
# ============================================================================

def render_assessment():
    themes = list(CIRCULAR_MODEL.keys())
    current_theme = themes[st.session_state.current_theme]

    inject_dynamic_theme_css(current_theme)

    if st.session_state.scroll_target:
        target = st.session_state.scroll_target
        if target == "top":
            components.html(
                """
                <script>
                  const doScroll = () => {
                    if (window.parent) {
                      window.parent.scrollTo({top:0, behavior:'smooth'});
                    } else {
                      window.scrollTo({top:0, behavior:'smooth'});
                    }
                  };
                  requestAnimationFrame(doScroll);
                </script>
                """,
                height=0,
                width=0,
            )
        else:
            components.html(
                f"""
                <script>
                  const targetId = "{target}";
                  const getDoc = () => (window.parent ? window.parent.document : document);
                  const doScroll = () => {{
                    const doc = getDoc();
                    const el = doc.getElementById(targetId);
                    if (el && el.scrollIntoView) {{
                      el.scrollIntoView({{behavior:'smooth', block:'start'}});
                      return true;
                    }}
                    return false;
                  }};
                  if (!doScroll()) {{
                    setTimeout(doScroll, 200);
                  }}
                </script>
                """,
                height=0,
                width=0,
            )
        st.session_state.scroll_target = None

    total_questions = sum(
        len(CIRCULAR_MODEL[t][i]["questions"])
        for t in CIRCULAR_MODEL
        for i in CIRCULAR_MODEL[t]
    )

    answered_count = 0
    for t in CIRCULAR_MODEL.keys():
        if t in st.session_state.theme_answers:
            for ind in CIRCULAR_MODEL[t].keys():
                if ind in st.session_state.theme_answers[t]:
                    answered_count += len([v for v in st.session_state.theme_answers[t][ind].values() if v is not None])

    pct = 0 if total_questions == 0 else int((answered_count / total_questions) * 100)

    st.markdown("<div id='progress-top'></div>", unsafe_allow_html=True)
    with st.container(key="topbar"):
        st.markdown(
            f"""
            <div class="topbar-inner">
              <div class="topbar-title">Zirkularitäts-Assessment Status</div>
              <div class="topbar-sub">Aktuell: <b>{current_theme}</b> • {answered_count} von {total_questions} Fragen</div>
              <div style="margin-top:8px;" class="topbar-rail">
                <div class="topbar-fill" style="--p:{pct}%;"></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    left, right = st.columns([0.34, 0.66], gap="large")

    # ---------------- LEFT: DIMENSIONS (CARD + FULL-HEIGHT ARROW RIGHT NEXT TO IT) ----------------
    with left:
        st.markdown("### Dimensionen")

        icon_map = {
            "Design": (
                '<svg viewBox="0 0 24 24" aria-hidden="true">'
                '<circle cx="12" cy="12" r="9"></circle>'
                '<circle cx="12" cy="12" r="3"></circle>'
                '</svg>'
            ),
            "Strategie": (
                '<svg viewBox="0 0 24 24" aria-hidden="true">'
                '<path d="M12 2l2.5 5 5.5.8-4 3.9.9 5.5-4.9-2.6-4.9 2.6.9-5.5-4-3.9 5.5-.8z"></path>'
                '</svg>'
            ),
            "Wirtschaftlichkeit": (
                '<svg viewBox="0 0 24 24" aria-hidden="true">'
                '<path d="M4 14l4-4 4 3 6-7"></path>'
                '<path d="M14 6h6v6"></path>'
                '</svg>'
            ),
            "Regulatorik": (
                '<svg viewBox="0 0 24 24" aria-hidden="true">'
                '<path d="M12 3l7 3v6c0 4.5-3.1 7.7-7 9-3.9-1.3-7-4.5-7-9V6z"></path>'
                '<path d="M9 12l2 2 4-4"></path>'
                '</svg>'
            ),
            "Systemische Befähiger": (
                '<svg viewBox="0 0 24 24" aria-hidden="true">'
                '<circle cx="6" cy="12" r="2.5"></circle>'
                '<circle cx="18" cy="6" r="2.5"></circle>'
                '<circle cx="18" cy="18" r="2.5"></circle>'
                '<path d="M8.5 11l7-4"></path>'
                '<path d="M8.5 13l7 4"></path>'
                '</svg>'
            ),
        }
        for idx, theme in enumerate(themes):
            ui = THEME_UI.get(theme, THEME_UI["Design"])
            q_count = sum(len(CIRCULAR_MODEL[theme][i]["questions"]) for i in CIRCULAR_MODEL[theme])
            active = idx == st.session_state.current_theme

            first_ind = list(CIRCULAR_MODEL[theme].keys())[0]
            teaser = CIRCULAR_MODEL[theme][first_ind].get("description", "")
            teaser = (teaser[:120] + "...") if len(teaser) > 120 else teaser

            outline = f"2px solid {ui['accent']}" if active else "none"

            if active:
                st.markdown(
                    f"<style>[class*='st-key-dim-card-{idx}']{{outline:2px solid {ui['accent']};}}</style>",
                    unsafe_allow_html=True,
                )
            with st.container(key=f"dim-card-{idx}"):
                st.markdown(
                    f"""
                    <div class="dim-row">
                      <div class="dim-left">
                        <div class="dim-icon" style="border-color:rgba(15,23,42,0.08);">{icon_map.get(theme, "")}</div>
                        <div>
                          <p class="dim-title">{theme}</p>
                          <div class="dim-meta">{q_count} Fragen</div>
                        </div>
                      </div>
                    </div>
                    <div class="dim-desc">{teaser}</div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown("<div class='dim-arrow-in'>", unsafe_allow_html=True)
                st.button(
                    "Dimension öffnen",
                    key=f"arrow_theme_{idx}",
                    use_container_width=True,
                    on_click=_open_dimension,
                    args=(idx,),
                )
                st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- RIGHT: INDICATORS TOP + QUESTIONS ----------------
    with right:
        current_theme = themes[st.session_state.current_theme]
        indicators = list(CIRCULAR_MODEL[current_theme].keys())
        if not indicators:
            st.error("Keine Indikatoren gefunden!")
            return

        if current_theme not in st.session_state.theme_answers:
            st.session_state.theme_answers[current_theme] = {}

        # st.markdown(f"## {current_theme}")

        current_idx = min(st.session_state.current_indicator, len(indicators) - 1)

        def fmt_indicator(ind_name: str) -> str:
            parts = ind_name.split(" ", 1)
            if len(parts) > 1 and parts[0][0].isdigit():
                return f"{parts[0]} — {parts[1]}"
            return ind_name

        st.markdown("<div id='indicator-top'></div>", unsafe_allow_html=True)
        st.markdown("### Indikatoren")
        with st.expander("Indikatorauswahl", expanded=True):
            st.markdown("<div class='indicator-acc'>", unsafe_allow_html=True)
            for i, name in enumerate(indicators):
                is_active = i == current_idx
                if is_active:
                    st.markdown(
                        f"<style>[class*='st-key-indicator-btn-{i}'] button{{background:{THEME_UI[current_theme]['pill']} !important; border-color:{THEME_UI[current_theme]['accent']} !important; color:#0B1220 !important; font-weight:900 !important;}}</style>",
                        unsafe_allow_html=True,
                    )
                with st.container(key=f"indicator-btn-{i}"):
                    st.button(
                        fmt_indicator(name),
                        key=f"indicator_btn_{current_theme}_{i}",
                        use_container_width=True,
                        type="secondary",
                        on_click=_select_indicator,
                        args=(i,),
                    )
            st.markdown("</div>", unsafe_allow_html=True)
        current_indicator = indicators[min(st.session_state.current_indicator, len(indicators) - 1)]

        if current_indicator not in st.session_state.theme_answers[current_theme]:
            st.session_state.theme_answers[current_theme][current_indicator] = {}

        st.markdown("### Leitfragen")

        indicator_data = CIRCULAR_MODEL[current_theme][current_indicator]
        for q_idx, question_data in enumerate(indicator_data.get("questions", []), start=1):
            code = question_data.get("code", "")
            text = question_data.get("text", "")
            options = question_data.get("options", [])

            with st.container(key=f"q-card-{current_theme}-{current_indicator}-{code}"):
                st.markdown(f"<div id='q-{code}'></div>", unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div class="q-head">
                      <div class="q-num">{q_idx}</div>
                      <div class="q-text">{code}: {text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                prev_score = st.session_state.theme_answers[current_theme][current_indicator].get(code)

                def fmt_score(value: float) -> str:
                    return f"{value:.2f}".rstrip("0").rstrip(".")

                option_items = []
                for opt in options:
                    score = opt.get("score", 0.0)
                    label = opt.get("label", "")
                    display_label = f"{fmt_score(score)} — {label}"
                    option_items.append({"display": display_label, "score": score})

                display_labels = ["Keine Auswahl"] + [opt["display"] for opt in option_items]
                display_to_score = {opt["display"]: opt["score"] for opt in option_items}

                selected_label = "Keine Auswahl"
                if prev_score is not None:
                    for opt in option_items:
                        if opt["score"] == prev_score:
                            selected_label = opt["display"]
                            break

                for label in display_labels:
                    is_selected = label == selected_label
                    score_value = None if label == "Keine Auswahl" else display_to_score.get(label, 0.0)
                    st.button(
                        label,
                        key=f"q_{current_theme}_{current_indicator}_{code}_{label}",
                        use_container_width=True,
                        type="primary" if is_selected else "secondary",
                        on_click=_select_answer,
                        args=(current_theme, current_indicator, code, score_value),
                    )

    st.divider()

    indicators = list(CIRCULAR_MODEL[current_theme].keys())
    is_last = (
        st.session_state.current_theme == len(themes) - 1
        and st.session_state.current_indicator == len(indicators) - 1
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.session_state.current_indicator > 0 or st.session_state.current_theme > 0:
            st.button("◀ Zurück", use_container_width=True, on_click=_go_prev_indicator_or_theme)

    with col3:
        if is_last:
            st.button("Ergebnisse anzeigen ▶", use_container_width=True, type="primary", on_click=_show_results)
        else:
            st.button("Weiter ▶", use_container_width=True, on_click=_go_next_indicator_or_theme)


# ============================================================================
# PAGE: SETTINGS
# ============================================================================

def render_settings():
    st.header("Gewichtungen anpassen")
    st.info(
        "Hier definieren Sie, wie stark jede Dimension in den Gesamtscore einfließt. "
        "Jede Dimension darf maximal 100% Gewicht haben."
    )
    st.markdown(
        """
        **So gehen Sie bei der Bewertung vor:**
        1. Wählen Sie pro Leitfrage eine Antwort. Leitfragen mit **„Keine Auswahl“** werden **nicht** bewertet.
        2. Pro Indikator wird der Durchschnitt der bewerteten Leitfragen berechnet.
        3. Pro Dimension wird der Durchschnitt der bewerteten Indikatoren berechnet.
        4. Der **Gesamtscore** ist der gewichtete Durchschnitt aller Dimensionen (nur mit aktiven Gewichten).

        **Beispielrechnung:**
        - Design 0.60 bei Gewicht 0.35
        - Strategie 0.40 bei Gewicht 0.20
        - Wirtschaftlichkeit 0.50 bei Gewicht 0.15
        - Regulatorik 0.70 bei Gewicht 0.15
        - Systemische Befähiger 0.30 bei Gewicht 0.15
        """
    )
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.latex(
            r"\text{Allgemein: }\text{Gesamtscore}=\frac{\sum_{d=1}^{n}\left(\text{Score}_d \times \text{Gewicht}_d\right)}{\sum_{d=1}^{n}\text{Gewicht}_d}"
        )
    with col_b:
        st.latex(
            r"\text{Beispiel: }\frac{0.60\cdot0.35 + 0.40\cdot0.20 + 0.50\cdot0.15 + 0.70\cdot0.15 + 0.30\cdot0.15}{\sum \text{Gewicht}}"
        )

    col1, col2 = st.columns(2)
    themes = list(CIRCULAR_MODEL.keys())
    raw_weights = {}

    with col1:
        for theme in themes[:3]:
            raw_weights[theme] = st.number_input(
                f"**{theme}**",
                min_value=0,
                max_value=100,
                value=int(round(st.session_state.weights.get(theme, 0.2) * 100)),
                step=1,
                key=f"weight_{theme}",
            )

    with col2:
        for theme in themes[3:]:
            raw_weights[theme] = st.number_input(
                f"**{theme}**",
                min_value=0,
                max_value=100,
                value=int(round(st.session_state.weights.get(theme, 0.2) * 100)),
                step=1,
                key=f"weight_{theme}",
            )

    total_percent = sum(raw_weights.values())
    if total_percent == 0:
        normalized = {k: 0.0 for k in themes}
    else:
        normalized = {k: v / total_percent for k, v in raw_weights.items()}
    st.session_state.weights = normalized

    st.metric("Summe Gewichtungen", f"{total_percent:.0f}%", delta="Ziel: 100%")
    if total_percent != 100:
        st.warning("Die Gewichtungen werden automatisch auf 100% normalisiert.")


# ============================================================================
# PAGE: RESULTS
# ============================================================================

def render_results():
    st.header("Ergebnisse & Dashboard")
    st.markdown(
        "<style>div[data-testid='stSpinner']{display:none;}</style>",
        unsafe_allow_html=True,
    )

    scores = calculate_scores(st.session_state.theme_answers)

    theme_scores = {}
    for theme in CIRCULAR_MODEL.keys():
        if theme in scores:
            vals = [v for v in scores[theme].values() if v is not None]
            theme_scores[theme] = (sum(vals) / len(vals)) if vals else 0.0
        else:
            theme_scores[theme] = 0.0

    weights_sum = sum(st.session_state.weights.get(dim, 0.0) for dim in CIRCULAR_MODEL.keys())
    if weights_sum > 0:
        total_01 = sum(
            theme_scores.get(dim, 0.0) * st.session_state.weights.get(dim, 0.0)
            for dim in CIRCULAR_MODEL.keys()
        ) / weights_sum
    else:
        total_01 = 0.0
    total_score = total_01 * 5.0
    level = get_maturity_level(total_01)
    def soften_hex(hex_color: str, mix: float = 0.25) -> str:
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = int(r + (255 - r) * mix)
        g = int(g + (255 - g) * mix)
        b = int(b + (255 - b) * mix)
        return f"#{r:02x}{g:02x}{b:02x}"

    theme_colors = {k: v["accent"] for k, v in THEME_UI.items()}
    theme_colors_soft = {k: soften_hex(v["accent"], 0.28) for k, v in THEME_UI.items()}
    maturity_scale = [
        ("Sehr gering", "0–20%"),
        ("Gering", "20–40%"),
        ("Mittel", "40–60%"),
        ("Fortgeschritten", "60–80%"),
        ("Sehr hoch", "80–100%"),
    ]

    # Build detailed rows
    detail_rows = []
    for theme, indicators in CIRCULAR_MODEL.items():
        for indicator_name, indicator_data in indicators.items():
            questions = indicator_data.get("questions", [])
            for q in questions:
                code = q.get("code", "")
                text = q.get("text", "")
                selected_score = (
                    st.session_state.theme_answers.get(theme, {})
                    .get(indicator_name, {})
                    .get(code)
                )
                detail_rows.append(
                    {
                        "Thema": theme,
                        "Indikator": indicator_name,
                        "Frage-Code": code,
                        "Frage": text,
                        "Score": selected_score,
                        "Score_%": (selected_score * 100) if selected_score is not None else None,
                        "Bewertet": selected_score is not None,
                    }
                )

    detail_df = pd.DataFrame(detail_rows)

    indicator_rows = []
    for theme, indicators in scores.items():
        for indicator_name, indicator_score in indicators.items():
            score_pct = indicator_score * 100 if indicator_score is not None else None
            indicator_rows.append(
                {
                    "Thema": theme,
                    "Indikator": indicator_name,
                    "Score": indicator_score,
                    "Score_%": score_pct,
                }
            )
    indicator_df = pd.DataFrame(indicator_rows)
    indicator_df["Order"] = (
        indicator_df["Indikator"]
        .str.extract(r"^(\d+)\.")
        .fillna(99)
        .astype(int)
    )
    theme_order = {k: i for i, k in enumerate(CIRCULAR_MODEL.keys())}
    indicator_df["ThemeOrder"] = indicator_df["Thema"].map(theme_order).fillna(99).astype(int)

    theme_df = pd.DataFrame(
        [{"Thema": k, "Score": v, "Score_%": v * 100} for k, v in theme_scores.items()]
    ).sort_values("Score", ascending=True)

    tab_overview, tab_themes, tab_indicators, tab_questions, tab_export = st.tabs(
        ["Überblick", "Dimensionen", "Indikatoren", "Leitfragen", "Export"]
    )

    with tab_overview:
        st.markdown("### Ihre Zirkularitätsreife")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            scale_html = "<br/>".join(
                [f"{m['emoji']} {name} ({rng})" for m, (name, rng) in zip(MATURITY_LEVELS, maturity_scale)]
            )
            st.markdown(
                f"""
            <div style='padding: 20px; background: #ffffff; border-radius: 16px;
                        border: 1px solid rgba(15,23,42,0.08); box-shadow: 0 10px 28px rgba(15,23,42,0.06);
                        text-align: center;'>
                <h4 style='margin-top: 0; color: #0F172A;'>Reifegrad</h4>
                <div style='font-size: 3em; font-weight: 900; color: #0F172A; margin: 10px 0;'>{level['emoji']}</div>
                <p style='margin: 5px 0; font-size: 1.4em; font-weight: 800;'>{level['name']}</p>
                <p style='margin: 5px 0; color: rgba(15,23,42,0.65);'>{level['description']}</p>
                <hr style='margin: 10px 0; border:none; border-top:1px solid rgba(15,23,42,0.10);'>
                <p style='margin: 5px 0; font-size: 1em;'><strong>Gewichteter Score:</strong> {total_score:.2f}/5.0</p>
                <p style='margin: 5px 0; font-size: 1em;'><strong>Gewichteter Prozentwert:</strong> {total_01*100:.0f}%</p>
                <hr style='margin: 10px 0; border:none; border-top:1px dashed rgba(15,23,42,0.12);'>
                <div style='text-align:left; font-size:0.92em; color: rgba(15,23,42,0.8);'>
                  <strong>Reifegrad-Skala</strong><br/>{scale_html}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("### Radar-Chart")
        fig_radar = create_radar_chart(
            theme_scores, "", theme_colors=theme_colors
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown("### Detaillierte Berechnung mit Gewichtungen")
        weighted_terms = []
        for dim in CIRCULAR_MODEL.keys():
            score = theme_scores.get(dim, 0.0)
            weight = st.session_state.weights.get(dim, 0.0)
            weighted_terms.append(f"{score:.2f} \\cdot {weight:.2f}")
        numerator = " + ".join(weighted_terms) if weighted_terms else "0"
        denominator = " + ".join([f"{st.session_state.weights.get(dim, 0.0):.2f}" for dim in CIRCULAR_MODEL.keys()]) or "1"
        total_5 = total_01 * 5.0
        st.latex(
            rf"\text{{Gesamtscore}}=\frac{{{numerator}}}{{{denominator}}}={total_01:.2f}"
        )


    with tab_themes:
        st.markdown("### Dimensionenübersicht")
        theme_cols = st.columns(3, gap="large")
        theme_order = list(CIRCULAR_MODEL.keys())
        theme_df_ordered = theme_df.set_index("Thema").loc[theme_order].reset_index()
        for idx, row in theme_df_ordered.iterrows():
            col = theme_cols[idx % 3]
            with col:
                theme_color = theme_colors.get(row["Thema"], "#0F172A")
                theme_color_soft = theme_colors_soft.get(row["Thema"], theme_color)
                gauge = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=row["Score_%"],
                        number={"suffix": "%", "font": {"size": 28, "color": theme_color}},
                        gauge={
                            "axis": {"range": [0, 100]},
                            "bar": {"color": theme_color_soft},
                            "bgcolor": "#F8FAFC",
                            "bordercolor": "#E2E8F0",
                            "borderwidth": 2,
                            "steps": [{"range": [0, 100], "color": "#F1F5F9"}],
                        },
                        title={"text": row["Thema"], "font": {"size": 14, "color": "#0F172A"}},
                    )
                )
                gauge.update_layout(height=220, margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(gauge, use_container_width=True)
        st.markdown("### Dimensionen-Ranking")
        theme_order = list(CIRCULAR_MODEL.keys())
        theme_df_ordered = theme_df.set_index("Thema").loc[theme_order].reset_index()
        theme_bar = px.bar(
            theme_df_ordered,
            x="Score_%",
            y="Thema",
            orientation="h",
            text="Score_%",
            color="Thema",
            color_discrete_map=theme_colors_soft,
        )
        theme_bar.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
        theme_bar.update_layout(
            height=320,
            showlegend=False,
            xaxis_title="",
            yaxis_title="",
            bargap=0.25,
            yaxis=dict(tickfont=dict(color="#0F172A")),
        )
        st.plotly_chart(theme_bar, use_container_width=True)

    with tab_indicators:
        st.markdown("### Indikator-Details")
        selected_theme = st.selectbox("Thema filtern", ["Alle"] + list(CIRCULAR_MODEL.keys()))
        view_df = indicator_df
        if selected_theme != "Alle":
            view_df = indicator_df[indicator_df["Thema"] == selected_theme]
        chart_df = view_df.copy()
        chart_df["Score"] = chart_df["Score"].fillna(0)
        chart_df["Score_%"] = chart_df["Score_%"].fillna(0)
        chart_df = chart_df.sort_values(["ThemeOrder", "Order", "Indikator"], ascending=True)
        y_order = chart_df["Indikator"].tolist()
        if selected_theme == "Alle":
            bar_color = "Thema"
            color_map = theme_colors_soft
        else:
            bar_color = None
            color_map = None
        ind_bar = px.bar(
            chart_df,
            x="Score_%",
            y="Indikator",
            orientation="h",
            text="Score_%",
            color=bar_color,
            color_discrete_map=color_map,
        )
        ind_bar.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
        if selected_theme != "Alle":
            ind_bar.update_traces(marker_color=theme_colors_soft.get(selected_theme, "#0F172A"))
        chart_height = max(420, 28 * len(chart_df) + 120)
        ind_bar.update_layout(
            height=chart_height,
            showlegend=selected_theme == "Alle",
            xaxis_title="",
            yaxis_title="",
            yaxis=dict(categoryorder="array", categoryarray=y_order, autorange="reversed", tickfont=dict(color="#0F172A")),
        )
        with st.container(height=520):
            st.plotly_chart(ind_bar, use_container_width=True)
        display_df = view_df.copy()
        display_df = display_df.drop(columns=[c for c in ["Score_%", "Order", "ThemeOrder"] if c in display_df.columns])
        display_df = display_df.rename(columns={"Score": "Aggregierter Score"})
        st.dataframe(display_df.sort_values("Aggregierter Score", ascending=True), use_container_width=True, hide_index=True)

    with tab_questions:
        st.markdown("### Leitfragen-Details")
        col1, col2 = st.columns([1, 1])
        with col1:
            q_theme = st.selectbox("Dimension", ["Alle"] + list(CIRCULAR_MODEL.keys()), key="q_theme_filter")
        with col2:
            q_indicator = st.selectbox(
                "Indikator",
                ["Alle"]
                + (
                    list(CIRCULAR_MODEL.get(q_theme, {}).keys())
                    if q_theme != "Alle"
                    else sorted(detail_df["Indikator"].unique().tolist())
                ),
                key="q_indicator_filter",
            )

        q_df = detail_df
        if q_theme != "Alle":
            q_df = q_df[q_df["Thema"] == q_theme]
        if q_indicator != "Alle":
            q_df = q_df[q_df["Indikator"] == q_indicator]

        unanswered = q_df[q_df["Bewertet"] == False]
        answered = q_df[q_df["Bewertet"] == True]

        col_a, _ = st.columns([1, 2])
        with col_a:
            total_questions = len(q_df)
            st.markdown(
                f"""
                <div style="font-weight:900; font-size:16px; color:#0F172A;">Nicht bewertet</div>
                <div style="font-weight:900; font-size:28px; color:#0F172A;">{len(unanswered)}/{total_questions}</div>
                """,
                unsafe_allow_html=True,
            )

        score_counts = (
            answered.dropna(subset=["Score"])
            .groupby("Score")["Frage-Code"]
            .count()
            .reset_index()
            .rename(columns={"Frage-Code": "Anzahl"})
        )
        if not score_counts.empty:
            if q_theme != "Alle":
                scale = ["#F1F5F9", theme_colors.get(q_theme, "#B7791F")]
            else:
                scale = ["#FFF6E8", "#B7791F"]
            dist_chart = px.bar(
                score_counts,
                x="Score",
                y="Anzahl",
                text="Anzahl",
                color="Score",
                color_continuous_scale=scale,
            )
            dist_chart.update_traces(textposition="outside")
            dist_chart.update_layout(
                height=280,
                coloraxis_showscale=False,
                xaxis_title="Score",
                yaxis_title="Anzahl",
            )
            st.plotly_chart(dist_chart, use_container_width=True)
        else:
            st.info("Noch keine bewerteten Leitfragen vorhanden.")

        def format_question_table(df: pd.DataFrame) -> pd.DataFrame:
            display = df.copy()
            if "Score_%" in display.columns:
                display = display.drop(columns=["Score_%"])
            if "Score" in display.columns:
                display = display.rename(columns={"Score": "Aggregierter Score"})
            if "Bewertet" in display.columns:
                display["Bewertet"] = display["Bewertet"].map({True: "Ja", False: "Nein"})
            return display

        if len(unanswered) > 0:
            with st.expander("Nicht bewertete Leitfragen anzeigen", expanded=True):
                unanswered_display = format_question_table(
                    unanswered.sort_values(["Thema", "Indikator", "Frage-Code"])
                )
                st.dataframe(
                    unanswered_display,
                    use_container_width=True,
                    hide_index=True,
                    height=320,
                )

        with st.expander("Alle Leitfragen anzeigen", expanded=False):
            all_display = format_question_table(
                q_df.sort_values(["Thema", "Indikator", "Frage-Code"])
            )
            st.dataframe(
                all_display,
                use_container_width=True,
                hide_index=True,
                height=420,
            )

    with tab_export:
        st.markdown("### Export & Speicherung")
        col1, col2 = st.columns(2)

        with col1:
            product_name = st.text_input("Produktname", "Mein Produkt")
            company = st.text_input("Unternehmensname", "Mein Unternehmen")

            if st.button("Assessment speichern", use_container_width=True, type="primary"):
                save_assessment_mc(st.session_state.theme_answers, product_name=product_name, company=company)
                st.success("Lokal gespeichert (assessments.json)")

        with col2:
            if st.button("PDF-Report herunterladen", use_container_width=True):
                try:
                    pdf_buffer = generate_pdf_report(
                        product_name=product_name,
                        company=company,
                        theme_scores=theme_scores,
                        weights=st.session_state.weights,
                        detailed_answers=st.session_state.theme_answers,
                        improvement_areas=[],
                        theme_colors=theme_colors,
                    )
                except Exception as e:
                    st.error(f"PDF-Generierung fehlgeschlagen: {str(e)}")
                else:
                    st.download_button(
                        label="PDF herunterladen",
                        data=pdf_buffer.getvalue(),
                        file_name=f"Circularity_Assessment_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )


# ============================================================================
# PAGE: HISTORY
# ============================================================================

def render_history():
    st.header("Assessment-Historie (lokal)")

    history_local = load_assessment_history_local()
    history = pd.DataFrame(history_local) if history_local else None

    if history is not None and len(history) > 0:
        def extract_answers(row):
            if isinstance(row.get("answers"), dict):
                return row.get("answers")
            if isinstance(row.get("Detailed_Answers"), str):
                try:
                    return json.loads(row.get("Detailed_Answers"))
                except Exception:
                    return {}
            return {}

        def calc_dimension_scores_from_answers(ans):
            scores = {}
            for dim, indicators in CIRCULAR_MODEL.items():
                vals = []
                for ind_name, ind_data in indicators.items():
                    q_scores = []
                    for q in ind_data.get("questions", []):
                        code = q.get("code", "")
                        score = ans.get(dim, {}).get(ind_name, {}).get(code)
                        if score is not None:
                            q_scores.append(score)
                    if q_scores:
                        vals.append(sum(q_scores) / len(q_scores))
                scores[dim] = (sum(vals) / len(vals)) if vals else 0.0
            return scores

        def normalize_row(row):
            answers = extract_answers(row)
            dim_scores = calc_dimension_scores_from_answers(answers)
            weights = row.get("weights") or st.session_state.weights
            weights_sum = sum(weights.get(d, 0.0) for d in CIRCULAR_MODEL.keys()) if isinstance(weights, dict) else 0.0
            if weights_sum > 0:
                total_01 = sum(dim_scores.get(d, 0.0) * weights.get(d, 0.0) for d in CIRCULAR_MODEL.keys()) / weights_sum
            else:
                total_01 = 0.0
            total_5 = total_01 * 5.0
            base = {
                "Timestamp": row.get("Timestamp") or row.get("timestamp"),
                "Produkt": row.get("Produkt") or row.get("Product_Name"),
                "Unternehmen": row.get("Unternehmen") or row.get("Company"),
                "Gewichteter Gesamtscore": round(total_5, 2),
            }
            for dim in CIRCULAR_MODEL.keys():
                base[f"{dim} Score"] = round(dim_scores.get(dim, 0.0), 2)
            return base

        normalized = pd.DataFrame([normalize_row(r) for r in history_local])
        st.markdown("### Übersicht (gewichteter Gesamtscore + Dimensionen)")
        st.dataframe(normalized, use_container_width=True, hide_index=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Gesamt Assessments", len(normalized))
        with col2:
            avg_score = normalized["Gewichteter Gesamtscore"].dropna()
            st.metric("Ø Score", f"{avg_score.mean():.2f}" if len(avg_score) > 0 else "—")
        with col3:
            if "Timestamp" in normalized.columns and len(normalized) > 0:
                st.metric("Letztes Assessment", str(normalized["Timestamp"].iloc[-1])[:16])

        # Detailtabelle pro Leitfrage
        detail_rows = []
        for row in history_local:
            answers = extract_answers(row)
            ts = row.get("Timestamp") or row.get("timestamp")
            product = row.get("Produkt") or row.get("Product_Name")
            company = row.get("Unternehmen") or row.get("Company")
            for dim, indicators in CIRCULAR_MODEL.items():
                for ind_name, ind_data in indicators.items():
                    for q in ind_data.get("questions", []):
                        code = q.get("code", "")
                        score = answers.get(dim, {}).get(ind_name, {}).get(code)
                        if score is None:
                            continue
                        detail_rows.append(
                            {
                                "Timestamp": ts,
                                "Produkt": product,
                                "Unternehmen": company,
                                "Dimension": dim,
                                "Indikator": ind_name,
                                "Fragennummer": code,
                                "Fragenscore": score,
                            }
                        )
        detail_df = pd.DataFrame(detail_rows)
        st.markdown("### Detailtabelle (Leitfragen)")
        if not detail_df.empty:
            st.dataframe(detail_df, use_container_width=True, hide_index=True)
        else:
            st.info("Keine detaillierten Leitfragen in der Historie vorhanden.")
    else:
        st.info("Noch keine Assessments gespeichert.")


# ============================================================================
# MAIN APP LOGIC
# ============================================================================

def main():
    if st.session_state.current_page == "welcome":
        render_welcome()
    elif st.session_state.current_page == "assessment":
        render_assessment()
    elif st.session_state.current_page == "settings":
        render_settings()
    elif st.session_state.current_page == "results":
        render_results()
    elif st.session_state.current_page == "history":
        render_history()


if __name__ == "__main__":
    main()
