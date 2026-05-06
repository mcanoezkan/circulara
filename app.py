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
import html
import re
import textwrap
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional
from datetime import datetime
from pathlib import Path

from config import (
    CIRCULAR_MODEL,
    DEFAULT_WEIGHTS,
    INDICATOR_RECOMMENDATIONS,
    MATURITY_LEVELS,
)

from utils import (
    get_maturity_level,
    get_improvement_areas,
    create_radar_chart,
    generate_pdf_report,
)

import llm

# ============================================================================
# UI THEME (DYNAMIC BACKGROUND + CARD STYLES)
# ============================================================================

UNITY_NAVY     = "#0B1830"
UNITY_NAVY_MID = "#1A3A6B"
UNITY_BLUE     = "#1A3A6B"
UNITY_LIGHT    = "#EEF3FB"

THEME_UI = {
    "Design":                {"bg": "#EEF3FB", "bg2": "#F4F7FD", "accent": UNITY_BLUE,     "pill": "#D6E4F7"},
    "Strategie":             {"bg": "#EAF0F8", "bg2": "#F0F5FA", "accent": UNITY_NAVY_MID, "pill": "#C8D9EF"},
    "Wirtschaftlichkeit":    {"bg": "#EDF3F8", "bg2": "#F2F6FB", "accent": "#1E7CB8",      "pill": "#CBE0F2"},
    "Regulatorik":           {"bg": "#EEF2F7", "bg2": "#F3F6FA", "accent": UNITY_NAVY,     "pill": "#C5D4E8"},
    "Systemische Befähiger": {"bg": "#EBF0F7", "bg2": "#F1F5FB", "accent": "#16437D",      "pill": "#C4D5E9"},
}

THEME_SUMMARIES = {
    "Design": "Produktseitige Voraussetzungen wie Demontage, Materialprofil und Aufbereitbarkeit.",
    "Strategie": "Markt, Organisation und Entscheidungslogik für zirkuläre Geschäftsmodelle.",
    "Wirtschaftlichkeit": "Preisniveau, Werterhalt und wirtschaftliche Tragfähigkeit der Aufbereitung.",
    "Regulatorik": "Rechtliche Wiederverwendung, Kennzeichnung und Daten- bzw. Rechte-Compliance.",
    "Systemische Befähiger": "Daten, Rückführungssysteme und nutzerseitige Aktivierung.",
}


def inject_dynamic_theme_css(theme_name: str):
    """Inject theme-dependent CSS. Sidebar remains untouched."""
    ui = THEME_UI.get(theme_name, THEME_UI["Design"])

    st.markdown(
        f"""
<style>
  /* ── ASSESSMENT: WHITE BACKGROUND ── */
  .stApp {{
    background: #FFFFFF !important;
  }}
  [data-testid="stAppViewContainer"] > .main {{
    padding-top: 16px;
    padding-bottom: 48px;
    background: #FFFFFF !important;
  }}
  [data-testid="stAppViewContainer"] > .main > div {{
    max-width: 1240px;
    margin: 0 auto;
    padding-left: 24px;
    padding-right: 24px;
  }}

  /* ── HEADINGS – UNITY NAVY ── */
  h1, h2, h3, h4 {{
    font-family: 'Barlow', system-ui, sans-serif !important;
    color: #0B1830 !important;
    font-weight: 900 !important;
    letter-spacing: -0.5px !important;
  }}
  h3 {{ font-size: 22px !important; }}

  /* ── TOP STATUS BAR — UNITY STYLE ── */
  [class*="st-key-topbar"] {{
    background: linear-gradient(135deg, #FFFFFF 0%, #F4F6FB 100%) !important;
    border: 1px solid rgba(11,24,48,0.10) !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 20px rgba(11,24,48,0.06) !important;
    margin: 6px 0 24px 0 !important;
  }}
  [class*="st-key-topbar"] .topbar-inner {{
    max-width: 1240px;
    margin: 0 auto;
    padding: 16px 22px;
  }}
  [class*="st-key-topbar"] .topbar-inner * {{
    visibility: visible !important;
    opacity: 1 !important;
  }}
  .topbar-meta {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 10px;
  }}
  .topbar-meta-label {{
    font-size: 11px !important;
    font-weight: 800 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: rgba(11,24,48,0.45) !important;
  }}
  .topbar-meta-value {{
    font-size: 15px !important;
    font-weight: 900 !important;
    color: #0B1830 !important;
    letter-spacing: -0.3px !important;
  }}
  .topbar-meta-value .pct {{
    color: rgba(30,95,171,1) !important;
    margin-left: 4px;
  }}
  .topbar-rail {{
    width: 100%;
    height: 10px;
    background: rgba(11,24,48,0.06);
    border-radius: 999px;
    overflow: hidden;
    position: relative;
    border: 1px solid rgba(11,24,48,0.04);
  }}
  .topbar-fill {{
    height: 100%;
    width: var(--p);
    background: linear-gradient(90deg, #1A3A6B 0%, #1E5FAB 50%, #5BA3E8 100%);
    border-radius: 999px;
    transition: width 0.5s cubic-bezier(0.22, 1, 0.36, 1);
    box-shadow: 0 0 12px rgba(30,95,171,0.25);
    position: relative;
  }}
  .topbar-fill::after {{
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.25) 50%, transparent 100%);
    border-radius: 999px;
    animation: topbar-shine 2.4s ease-in-out infinite;
  }}
  @keyframes topbar-shine {{
    0% {{ transform: translateX(-100%); }}
    100% {{ transform: translateX(100%); }}
  }}

  /* ── UNITY CARD BASE ── */
  [class*="st-key-dim-card-"] {{
    background: #FFFFFF !important;
    border: 1px solid rgba(11,24,48,0.12) !important;
    border-radius: 6px !important;
    box-shadow: none !important;
    padding: 20px 20px 14px 20px !important;
    margin: 0 0 10px 0 !important;
    transition: box-shadow 0.18s ease, border-color 0.18s ease !important;
  }}
  [class*="st-key-dim-card-"]:hover {{
    box-shadow: 0 4px 20px rgba(11,24,48,0.10) !important;
    border-color: rgba(30,95,171,0.30) !important;
  }}

  /* ── DIMENSION CARD CONTENT ── */
  .dim-row {{
    display: flex;
    align-items: flex-start;
    gap: 14px;
  }}
  .dim-left {{
    display: flex;
    gap: 14px;
    align-items: flex-start;
    flex: 1;
  }}
  .dim-icon {{
    width: 40px; height: 40px;
    border-radius: 4px;
    background: rgba(30,95,171,0.08);
    border: 1px solid rgba(30,95,171,0.18);
    display: flex; align-items: center; justify-content: center;
    flex: 0 0 auto;
    margin-top: 2px;
  }}
  .dim-icon svg {{
    width: 20px; height: 20px;
    stroke: #1A3A6B;
    stroke-width: 2;
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
  }}
  .dim-title {{
    font-family: 'Barlow', system-ui, sans-serif !important;
    font-weight: 800 !important;
    color: #0B1830 !important;
    font-size: 18px !important;
    line-height: 1.2;
    margin: 0;
    letter-spacing: -0.2px;
  }}
  .dim-meta {{
    margin-top: 4px;
    font-size: 13px;
    font-weight: 500;
    color: rgba(11,24,48,0.40);
    letter-spacing: 0;
  }}
  .dim-desc {{
    font-size: 14px;
    color: rgba(11,24,48,0.60);
    margin-top: 10px;
    line-height: 1.55;
    font-weight: 400;
  }}

  /* ── "Mehr erfahren" = pure Unity text link ── */
  [class*="st-key-dim-btn-"] div[data-testid="stButton"],
  [class*="st-key-dim-btn-"] div[data-testid="stButton"] > button,
  [class*="st-key-dim-btn-"] div[data-testid="stButton"] > button[kind="secondary"],
  [class*="st-key-dim-btn-"] div[data-testid="stButton"] > button[kind="primary"] {{
    background: transparent !important;
    border: none !important;
    color: #1A3A6B !important;
    font-weight: 800 !important;
    font-size: 14px !important;
    padding: 6px 0 4px 0 !important;
    box-shadow: none !important;
    text-align: left !important;
    width: auto !important;
    letter-spacing: 0 !important;
    transform: none !important;
  }}
  [class*="st-key-dim-btn-"] div[data-testid="stButton"] > button:hover,
  [class*="st-key-dim-btn-"] div[data-testid="stButton"] > button[kind="secondary"]:hover {{
    color: #0B1830 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    transform: none !important;
    text-decoration: underline !important;
  }}

  /* ── HIDE Streamlit keyboard shortcut badges (keyb overlay) ── */
  kbd {{ display: none !important; visibility: hidden !important; width: 0 !important; height: 0 !important; }}
  [data-testid="stExpander"] summary kbd {{ display: none !important; }}
  div[data-testid="stExpander"] summary > div > p:empty {{ display: none !important; }}
  div[data-testid="stExpander"] summary span[aria-hidden="true"] {{ display: none !important; }}
  [data-testid="stExpander"] summary [data-testid="stExpanderToggleIcon"] + span {{ display: none !important; }}
  button[kind="secondary"] kbd,
  button[kind="primary"] kbd {{ display: none !important; }}

  /* ── QUESTION CARDS ── */
  [class*="st-key-q-card-"] {{
    background: #FFFFFF !important;
    border: 1px solid rgba(11,24,48,0.12) !important;
    border-radius: 6px !important;
    box-shadow: none !important;
    padding: 20px !important;
    margin: 0 0 10px 0 !important;
    transition: box-shadow 0.18s ease, border-color 0.18s ease !important;
  }}
  [class*="st-key-q-card-"]:hover {{
    box-shadow: 0 4px 16px rgba(11,24,48,0.08) !important;
  }}
  .q-head {{ display: flex; gap: 14px; align-items: flex-start; margin-bottom: 14px; }}
  .q-num {{
    width: 32px; height: 32px;
    border-radius: 4px;
    background: #0B1830;
    color: #FFFFFF;
    font-weight: 800;
    font-size: 14px;
    display: flex; align-items: center; justify-content: center;
    flex: 0 0 auto;
    letter-spacing: 0;
    margin-top: 2px;
  }}
  .q-text {{
    font-family: 'Barlow', system-ui, sans-serif !important;
    font-weight: 800 !important;
    color: #0B1830 !important;
    font-size: 17px !important;
    line-height: 1.35;
    letter-spacing: -0.2px;
  }}
  .q-text-wrap {{ display: flex; gap: 10px; align-items: flex-start; flex: 1; }}
  .q-info {{ position: relative; display: inline-flex; flex: 0 0 auto; }}
  .q-info-icon {{
    width: 22px; height: 22px; border-radius: 4px;
    border: 1px solid rgba(11,24,48,0.18);
    background: #FFFFFF;
    color: #1A3A6B;
    font-size: 12px; font-weight: 800;
    display: inline-flex; align-items: center; justify-content: center;
    cursor: help;
  }}
  .q-info-bubble {{
    position: absolute; top: 30px; right: 0;
    width: min(360px, calc(100vw - 80px));
    padding: 14px 16px;
    border-radius: 6px;
    background: #0B1830;
    color: #FFFFFF;
    font-size: 13px; line-height: 1.55;
    box-shadow: 0 12px 32px rgba(11,24,48,0.25);
    opacity: 0; visibility: hidden;
    transform: translateY(6px);
    transition: opacity 0.16s ease, transform 0.16s ease;
    z-index: 1000;
  }}
  .q-info:hover .q-info-bubble,
  .q-info:focus-within .q-info-bubble {{
    opacity: 1; visibility: visible; transform: translateY(0);
  }}

  /* Answer option buttons */
  [class*="st-key-q-card-"] div[data-testid="stButton"] {{ width: 100% !important; }}
  [class*="st-key-q-card-"] div[data-testid="stButton"] > button {{
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
    border-radius: 4px !important;
    border: 1px solid rgba(11,24,48,0.12) !important;
    background: #FFFFFF !important;
    color: #0B1830 !important;
    padding: 11px 16px !important;
    margin-bottom: 5px !important;
    box-shadow: none !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    transition: border-color 0.14s ease, background 0.14s ease !important;
  }}
  [class*="st-key-q-card-"] div[data-testid="stButton"] > button:hover {{
    border-color: rgba(30,95,171,0.40) !important;
    background: rgba(30,95,171,0.04) !important;
    transform: none !important;
    box-shadow: none !important;
  }}
  [class*="st-key-q-card-"] div[data-testid="stButton"] > button[kind="primary"] {{
    background: rgba(30,95,171,0.08) !important;
    border-color: #1A3A6B !important;
    border-left-width: 3px !important;
    color: #0B1830 !important;
    font-weight: 800 !important;
  }}
  /* Selected answer text (primary) — schwarz statt weiß, überschreibt globale Regel */
  [class*="st-key-q-card-"] div[data-testid="stButton"] > button p,
  [class*="st-key-q-card-"] div[data-testid="stButton"] > button span,
  [class*="st-key-q-card-"] div[data-testid="stButton"] > button *,
  [class*="st-key-q-card-"] div[data-testid="stButton"] > button[kind="primary"] p,
  [class*="st-key-q-card-"] div[data-testid="stButton"] > button[kind="primary"] span,
  [class*="st-key-q-card-"] div[data-testid="stButton"] > button[kind="primary"] * {{
    color: #0B1830 !important;
  }}

  /* ── INDICATOR BUTTONS ── */
  .indicator-acc {{ width: 100%; }}
  .indicator-acc div[data-testid="stButton"] > button {{
    width: 100% !important;
    height: auto !important;
    min-height: 42px !important;
    border-radius: 4px !important;
    border: 1px solid rgba(11,24,48,0.12) !important;
    background: #FFFFFF !important;
    color: #0B1830 !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    box-shadow: none !important;
    padding: 10px 14px !important;
    text-align: left !important;
    transition: border-color 0.14s ease !important;
  }}
  .indicator-acc div[data-testid="stButton"] > button:hover {{
    border-color: rgba(30,95,171,0.35) !important;
    background: rgba(30,95,171,0.03) !important;
  }}

  /* ── EXPANDER ── */
  div[data-testid="stExpander"] {{
    background: #FFFFFF !important;
    border: 1px solid rgba(11,24,48,0.12) !important;
    border-radius: 6px !important;
    box-shadow: none !important;
    padding: 4px 0 !important;
  }}
  div[data-testid="stExpander"] > details {{ background: #FFFFFF !important; border-radius: 6px !important; }}
  div[data-testid="stExpander"] summary {{
    font-weight: 700 !important;
    font-size: 15px !important;
    color: #0B1830 !important;
    padding: 14px 16px !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    background: transparent !important;
  }}
  div[data-testid="stExpander"] summary * {{
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #0B1830 !important;
    background: transparent !important;
  }}
  div[data-testid="stExpander"] summary::before,
  div[data-testid="stExpander"] summary::after {{ border: none !important; }}
  div[data-testid="stExpander"] summary,
  div[data-testid="stExpander"] summary *,
  div[data-testid="stExpander"] > details {{ border-color: transparent !important; }}
</style>
""",
        unsafe_allow_html=True,
    )


# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Unity - Circularity Fit Check",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# BASE CSS (Sidebar stays as-is)
# ============================================================================

st.markdown(
    """
<style>
  /* ── UNITY FONT (Barlow) ── */
  @import url('https://fonts.googleapis.com/css2?family=Barlow:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,700;1,900&display=swap');
  /* ── Material Symbols Icons komplett ausblenden (Font lädt unzuverlässig → zeigt sonst Text wie "keyboard_arrow_down") ── */
  span.material-symbols-outlined,
  span.material-symbols-rounded,
  span.material-symbols-sharp,
  [class*="material-symbols"],
  [class*="MaterialSymbols"],
  [data-testid="stIconMaterial"],
  [data-testid="stExpanderIcon"],
  [data-testid="stTooltipIcon"],
  [data-testid="stToolbarActionButtonIcon"],
  [data-testid="stAlertDynamicIcon"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    font-size: 0 !important;
    overflow: hidden !important;
  }
  *, *::before, *::after {
    font-family: 'Barlow', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
  }
  .stApp { background: #FFFFFF !important; }

  /* ── UNITY NAVY SIDEBAR ── */
  [data-testid="stSidebar"] {
    background: #0B1830 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    backdrop-filter: none !important;
  }
  [data-testid="stSidebar"] > div { background: #0B1830 !important; }
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] label { color: rgba(255,255,255,0.65) !important; }
  [data-testid="stSidebar"] h5 {
    color: rgba(255,255,255,0.28) !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    font-weight: 700 !important;
  }
  [data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.07) !important;
    margin: 14px 0 !important;
  }
  [data-testid="stSidebar"] small,
  [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: rgba(255,255,255,0.30) !important;
    font-size: 12px !important;
  }
  /* Sidebar nav buttons */
  [data-testid="stSidebar"] div[data-testid="stButton"] > button {
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    color: rgba(255,255,255,0.55) !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
    padding: 9px 14px !important;
    text-align: left !important;
    box-shadow: none !important;
    letter-spacing: -0.1px !important;
    transition: background 0.14s ease, color 0.14s ease !important;
  }
  [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.07) !important;
    color: rgba(255,255,255,0.90) !important;
    border: none !important;
    box-shadow: none !important;
  }
  [data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {
    background: rgba(30,95,171,0.22) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    border-left: 3px solid #1A3A6B !important;
    border-radius: 0 8px 8px 0 !important;
    padding-left: 16px !important;
    box-shadow: none !important;
  }
  [data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: rgba(30,95,171,0.32) !important;
    color: #FFFFFF !important;
  }

  /* ── MAIN LAYOUT ── */
  header[data-testid="stHeader"] { display: block; z-index: 1500; background: transparent; }
  [data-testid="stAppViewContainer"] > .main { padding-top: 24px; }
  div[data-testid="stStatusWidget"] { display: none !important; }
  div[data-testid="stSpinner"] { display: none !important; }
  .js-plotly-plot .plotly .loading,
  .js-plotly-plot .plotly .loading-text,
  .js-plotly-plot .plotly .plotly-loading { display: none !important; }

  /* ── KEYBOARD-ICON TEXT & BADGES AUSBLENDEN ── */
  kbd { display: none !important; }
  /* Sidebar-Toggle-Buttons komplett ausblenden (collapsed + expanded state) */
  [data-testid="collapsedControl"] { display: none !important; }
  [data-testid="stSidebarCollapseButton"] { display: none !important; }
  [data-testid="stSidebarHeader"] > button { display: none !important; }
  button[data-testid="stBaseButton-headerNoPadding"] { display: none !important; }
  /* Streamlit-Header komplett ausblenden */
  header[data-testid="stHeader"] {
    display: none !important;
  }
  /* Footer & deploy ausblenden */
  #MainMenu { visibility: hidden !important; }
  footer { visibility: hidden !important; }
  .stDeployButton { display: none !important; }

  /* ── GLOBAL BUTTON BASE ── */
  div[data-testid="stButton"] > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    letter-spacing: -0.1px !important;
    transition: all 0.14s ease !important;
  }
  div[data-testid="stButton"] > button[kind="primary"] {
    background: #0B1830 !important;
    color: #FFFFFF !important;
    border: 1px solid #0B1830 !important;
    box-shadow: 0 2px 6px rgba(11,24,48,0.25) !important;
  }
  div[data-testid="stButton"] > button[kind="primary"] *,
  div[data-testid="stButton"] > button[kind="primary"] p,
  div[data-testid="stButton"] > button[kind="primary"] span {
    color: #FFFFFF !important;
  }
  div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #1A3A6B !important;
    border-color: #1A3A6B !important;
    box-shadow: 0 4px 14px rgba(11,24,48,0.30) !important;
    transform: translateY(-1px) !important;
  }
  div[data-testid="stButton"] > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #0B1830 !important;
    border: 1px solid rgba(11,24,48,0.15) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
  }
  div[data-testid="stButton"] > button[kind="secondary"] *,
  div[data-testid="stButton"] > button[kind="secondary"] p,
  div[data-testid="stButton"] > button[kind="secondary"] span {
    color: #0B1830 !important;
  }
  /* ── SIDEBAR BUTTON TEXT — nach globalen Regeln, um cascade zu gewinnen ── */
  [data-testid="stSidebar"] div[data-testid="stButton"] > button p,
  [data-testid="stSidebar"] div[data-testid="stButton"] > button span,
  [data-testid="stSidebar"] div[data-testid="stButton"] > button * {
    color: rgba(255,255,255,0.65) !important;
  }
  [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover p,
  [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover span,
  [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover * {
    color: rgba(255,255,255,0.95) !important;
  }
  [data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] p,
  [data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] span,
  [data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] * {
    color: #FFFFFF !important;
  }
  [data-testid="stSidebar"] div[data-testid="stButton"] > button:disabled p,
  [data-testid="stSidebar"] div[data-testid="stButton"] > button:disabled span,
  [data-testid="stSidebar"] div[data-testid="stButton"] > button:disabled *,
  [data-testid="stSidebar"] div[data-testid="stButton"] > button[disabled] p,
  [data-testid="stSidebar"] div[data-testid="stButton"] > button[disabled] span,
  [data-testid="stSidebar"] div[data-testid="stButton"] > button[disabled] * {
    color: rgba(255,255,255,0.35) !important;
  }
  div[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: rgba(11,24,48,0.28) !important;
    box-shadow: 0 3px 10px rgba(0,0,0,0.08) !important;
    transform: translateY(-1px) !important;
  }

  /* ── GLOBAL HEADINGS ── */
  h1, h2, h3, h4, h5, h6 {
    font-family: 'Barlow', system-ui, sans-serif !important;
    color: #0B1830 !important;
    letter-spacing: -0.5px !important;
    font-weight: 800 !important;
  }
  h1 { font-size: 36px !important; font-weight: 900 !important; letter-spacing: -1px !important; }
  h2 { font-size: 28px !important; font-weight: 900 !important; }
  h3 { font-size: 22px !important; font-weight: 800 !important; }
  p, label, span, div { font-family: 'Barlow', system-ui, sans-serif !important; }

  /* ── TABS ── */
  div[data-testid="stTabs"] button[role="tab"] {
    font-weight: 700 !important;
    font-size: 14px !important;
    color: rgba(11,24,48,0.45) !important;
    letter-spacing: 0 !important;
  }
  div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #0B1830 !important;
    border-bottom-color: #1A3A6B !important;
  }

  /* ── METRICS ── */
  div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.06) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
  }
  div[data-testid="stMetric"] label { color: rgba(10,10,10,0.45) !important; font-size:12px !important; }
  div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #0A0A0A !important; font-weight: 800 !important; }

  /* ── FORM INPUTS ── */
  div[data-testid="stTextInput"] input,
  div[data-testid="stNumberInput"] input {
    border-radius: 8px !important;
    border: 1px solid rgba(0,0,0,0.12) !important;
    background: #FFFFFF !important;
    font-size: 14px !important;
    color: #0A0A0A !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
  }
  div[data-testid="stTextInput"] input:focus,
  div[data-testid="stNumberInput"] input:focus {
    border-color: #1A3A6B !important;
    box-shadow: 0 0 0 3px rgba(0,102,255,0.10) !important;
  }
  div[data-testid="stSelectbox"] > div {
    border-radius: 8px !important;
    border: 1px solid rgba(0,0,0,0.12) !important;
    background: #FFFFFF !important;
  }

  /* ── EXPANDER ── */
  div[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.07) !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05) !important;
  }
  div[data-testid="stExpander"] summary {
    font-weight: 700 !important;
    font-size: 14px !important;
    color: #0A0A0A !important;
    padding: 14px 16px !important;
  }

  /* ── ICON BOX ── */
  .dim-icon {
    width: 40px; height: 40px; border-radius: 4px;
    background: rgba(30,95,171,0.08);
    border: 1px solid rgba(30,95,171,0.18);
    display: flex; align-items: center; justify-content: center;
  }
  .dim-icon svg { width: 20px; height: 20px; }

  /* ── FORM SUBMIT BUTTON ── */
  div[data-testid="stFormSubmitButton"] > button,
  div[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"],
  div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
    background: #0B1830 !important;
    color: #FFFFFF !important;
    border: 1px solid #0B1830 !important;
    border-radius: 4px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px rgba(11,24,48,0.20) !important;
    padding: 12px 24px !important;
    min-height: 46px !important;
  }
  div[data-testid="stFormSubmitButton"] > button p,
  div[data-testid="stFormSubmitButton"] > button span {
    color: #FFFFFF !important;
    font-weight: 700 !important;
  }
  div[data-testid="stFormSubmitButton"] > button:hover,
  div[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"]:hover {
    background: #1A3A6B !important;
    border-color: #1A3A6B !important;
    color: #FFFFFF !important;
    transform: none !important;
  }
  /* Global: alle primary buttons weißer Text */
  div[data-testid="stButton"] > button[kind="primary"] p,
  div[data-testid="stButton"] > button[kind="primary"] span {
    color: #FFFFFF !important;
  }
  /* Download button */
  div[data-testid="stDownloadButton"] > button {
    background: #0B1830 !important;
    color: #FFFFFF !important;
    border: 1px solid #0B1830 !important;
    border-radius: 4px !important;
    font-weight: 700 !important;
  }
  div[data-testid="stDownloadButton"] > button p,
  div[data-testid="stDownloadButton"] > button span {
    color: #FFFFFF !important;
  }

  /* ── SIDEBAR: DEFINITIVELY OVERRIDE BUTTON APPEARANCE ── */
  /* secondary (inactive) nav items — transparent, white text */
  [data-testid="stSidebar"] div[data-testid="stButton"] > button,
  [data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"],
  [data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondaryFormSubmit"] {
    background: transparent !important;
    border: none !important;
    border-radius: 4px !important;
    color: rgba(255,255,255,0.72) !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    padding: 12px 18px !important;
    text-align: left !important;
    box-shadow: none !important;
    letter-spacing: 0 !important;
    transform: none !important;
  }
  [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover,
  [data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: none !important;
    transform: none !important;
  }
  /* primary (active) nav item */
  [data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {
    background: rgba(30,95,171,0.20) !important;
    border: none !important;
    border-left: 3px solid #1A3A6B !important;
    border-radius: 0 4px 4px 0 !important;
    color: #FFFFFF !important;
    font-weight: 800 !important;
    font-size: 16px !important;
    padding: 12px 18px !important;
    box-shadow: none !important;
    transform: none !important;
  }
  [data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: rgba(30,95,171,0.30) !important;
    transform: none !important;
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
if "company_name" not in st.session_state:
    st.session_state.company_name = ""
if "sector" not in st.session_state:
    st.session_state.sector = ""
if "product_name" not in st.session_state:
    st.session_state.product_name = ""
if "dimension_priority" not in st.session_state:
    st.session_state.dimension_priority = list(CIRCULAR_MODEL.keys())
if "intake_completed" not in st.session_state:
    st.session_state.intake_completed = False


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
        "Sektor": st.session_state.sector,
        "Dimensionen_Prioritaet": st.session_state.dimension_priority,
        "answers": answers,
        "scores": calculate_scores(answers),
        "weights": st.session_state.weights,
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


def _is_intake_complete() -> bool:
    return bool(
        st.session_state.company_name.strip()
        and st.session_state.sector.strip()
        and st.session_state.product_name.strip()
        and st.session_state.intake_completed
    )


def _weights_from_priority(priority_order: list[str]) -> dict[str, float]:
    points = list(range(len(priority_order), 0, -1))
    total_points = sum(points)
    return {
        theme: (points[idx] / total_points) if theme in priority_order else 0.0
        for idx, theme in enumerate(priority_order)
    }


def _weights_to_integer_percentages(weights: dict[str, float], themes: list[str]) -> dict[str, int]:
    raw_values = {theme: max(0.0, weights.get(theme, 0.0) * 100) for theme in themes}
    floored = {theme: int(raw_values[theme]) for theme in themes}
    remainder = 100 - sum(floored.values())

    ranked_remainders = sorted(
        themes,
        key=lambda theme: (raw_values[theme] - floored[theme], raw_values[theme]),
        reverse=True,
    )

    for theme in ranked_remainders[:max(0, remainder)]:
        floored[theme] += 1

    return floored


def _set_current_page(page: str):
    if page != "welcome" and not _is_intake_complete():
        st.session_state.current_page = "welcome"
        return
    st.session_state.current_page = page


def _start_assessment():
    if not _is_intake_complete():
        st.session_state.current_page = "welcome"
        return
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
    if not _is_intake_complete():
        st.session_state.current_page = "welcome"
        return
    st.session_state.current_page = "results"


# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    logo_path = Path("assets") / "unity-logo.png"
    if logo_path.exists():
        st.markdown("<div style='padding: 28px 16px 8px 16px;'>", unsafe_allow_html=True)
        st.image(str(logo_path))
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <div style="padding: 28px 20px 12px 20px;">
              <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:32px;height:32px;background:#1A3A6B;border-radius:8px;
                            display:flex;align-items:center;justify-content:center;">
                  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                    <path d="M3 3h5v12H3V3zm7 0h5v12h-5V3z" fill="white"/>
                  </svg>
                </div>
                <span style="font-size:18px;font-weight:900;color:#FFFFFF;letter-spacing:-0.4px;">Unity</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div style='margin:0 16px;border-top:1px solid rgba(255,255,255,0.07);'></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='padding:16px 6px 6px 6px;font-size:10px;font-weight:700;"
        "text-transform:uppercase;letter-spacing:0.12em;color:rgba(255,255,255,0.28);'>Navigation</div>",
        unsafe_allow_html=True,
    )

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
    if not _is_intake_complete():
        st.caption("Bitte vervollständigen Sie zuerst die Angaben auf der Startseite.")


# ============================================================================
# PAGE: WELCOME
# ============================================================================

def render_welcome():
    st.markdown(
        textwrap.dedent(
            """
        <style>
          /* ── UNITY DARK HERO BACKGROUND ── */
          .stApp {
            background: #0B1830 !important;
          }

          /* ── HERO ── */
          .hero-wrap {
            text-align: center;
            padding: 72px 20px 52px 20px;
          }
          .hero-eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 16px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
            color: rgba(255,255,255,0.75);
            letter-spacing: 0.10em;
            margin-bottom: 28px;
            text-transform: uppercase;
          }
          .hero-title {
            font-size: 72px;
            font-weight: 900;
            letter-spacing: -3px;
            color: #FFFFFF;
            line-height: 1.0;
            margin: 0 0 22px 0;
          }
          .hero-title em {
            font-style: normal;
            color: #5BA3E8;
          }
          .hero-sub {
            font-size: 19px;
            color: rgba(255,255,255,0.60);
            line-height: 1.70;
            max-width: 600px;
            margin: 0 auto 38px auto;
            font-weight: 400;
          }

          /* ── STATS ROW ── */
          .stats-row {
            display: inline-flex;
            align-items: center;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 56px;
          }
          .stat-cell {
            padding: 18px 32px;
            text-align: center;
            border-right: 1px solid rgba(255,255,255,0.08);
          }
          .stat-cell:last-child { border-right: none; }
          .stat-num {
            font-size: 26px;
            font-weight: 900;
            color: #FFFFFF;
            letter-spacing: -0.5px;
            line-height: 1.1;
          }
          .stat-label {
            font-size: 10.5px;
            font-weight: 600;
            color: rgba(255,255,255,0.40);
            text-transform: uppercase;
            letter-spacing: 0.09em;
            margin-top: 4px;
          }

          /* ── FEATURE CARDS ── */
          .feat-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 14px;
            padding: 24px;
            height: 100%;
            transition: background 0.20s ease, border-color 0.20s ease, transform 0.20s ease;
            margin-bottom: 14px;
          }
          .feat-card:hover {
            background: rgba(255,255,255,0.09);
            border-color: rgba(91,163,232,0.35);
            transform: translateY(-3px);
          }
          .feat-icon {
            width: 38px; height: 38px;
            border-radius: 10px;
            background: rgba(30,95,171,0.35);
            border: 1px solid rgba(91,163,232,0.25);
            display: flex; align-items: center; justify-content: center;
            font-size: 17px;
            margin-bottom: 16px;
            color: #5BA3E8;
          }
          .feat-title {
            font-weight: 800;
            font-size: 14.5px;
            color: #FFFFFF;
            letter-spacing: -0.2px;
            margin-bottom: 8px;
          }
          .feat-text {
            font-size: 13px;
            color: rgba(255,255,255,0.50);
            line-height: 1.65;
          }

          /* ── SECTION DIVIDER ── */
          .section-divider {
            display: flex;
            align-items: center;
            gap: 16px;
            margin: 48px 0 0 0;
          }
          .section-divider-line { flex: 1; height: 1px; background: rgba(255,255,255,0.10); }
          .section-divider-label {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: rgba(255,255,255,0.28);
            white-space: nowrap;
          }

          /* ── FORM CARD ── */
          .form-card {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 32px 32px 8px 32px;
            margin-top: 24px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.35);
          }
          .form-card-title {
            font-size: 21px;
            font-weight: 900;
            color: #0B1830;
            letter-spacing: -0.5px;
            margin-bottom: 5px;
          }
          .form-card-sub {
            font-size: 13px;
            color: rgba(11,24,48,0.48);
            margin-bottom: 0;
            line-height: 1.55;
          }

          /* ── FORM CARD: WHITE ON DARK BACKGROUND ── */
          [data-testid="stForm"] {
            background: #FFFFFF !important;
            border-radius: 8px !important;
            padding: 32px 32px 24px 32px !important;
            box-shadow: 0 24px 64px rgba(0,0,0,0.35) !important;
            margin-top: 20px !important;
            border: none !important;
          }
          /* All text inside form = navy */
          [data-testid="stForm"] label,
          [data-testid="stForm"] p,
          [data-testid="stForm"] span,
          [data-testid="stForm"] div,
          [data-testid="stForm"] h3,
          [data-testid="stForm"] h4 {
            color: #0B1830 !important;
            font-size: 15px !important;
          }
          [data-testid="stForm"] h3 { font-size: 20px !important; font-weight: 900 !important; }
          [data-testid="stForm"] h4 { font-size: 17px !important; font-weight: 800 !important; }
          [data-testid="stForm"] input { color: #0B1830 !important; font-size: 15px !important; }
          /* Select boxes in form */
          [data-testid="stForm"] [data-testid="stSelectbox"] > div,
          [data-testid="stForm"] [data-testid="stSelectbox"] > div * {
            color: #0B1830 !important;
            background: #FFFFFF !important;
          }
          /* Caption text */
          [data-testid="stForm"] [data-testid="stCaptionContainer"] p {
            color: rgba(11,24,48,0.50) !important;
            font-size: 13px !important;
          }
          /* The "Assessment starten" button after the form — white on dark */
          [data-testid="stMainBlockContainer"] > div > [data-testid="stVerticalBlock"] > div:last-child div[data-testid="stButton"] > button[kind="primary"] {
            font-size: 18px !important;
            padding: 16px 32px !important;
            font-weight: 800 !important;
          }
        </style>
        """
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-wrap">
          <div class="hero-eyebrow">Unity Consulting &amp; Innovation &nbsp;·&nbsp; Circularity Assessment</div>
          <div class="hero-title">Ihre Herausforderungen –<br><em>unsere Lösungen.</em></div>
          <div class="hero-sub">
            Bewerten Sie die Zirkularitätsreife Ihres Produkts strukturiert,
            gewichtet und mit konkreten Handlungsempfehlungen für Stakeholder.
          </div>
          <div style="display:flex;justify-content:center;">
            <div class="stats-row">
              <div class="stat-cell">
                <div class="stat-num">5</div>
                <div class="stat-label">Dimensionen</div>
              </div>
              <div class="stat-cell">
                <div class="stat-num">25+</div>
                <div class="stat-label">Indikatoren</div>
              </div>
              <div class="stat-cell">
                <div class="stat-num">60+</div>
                <div class="stat-label">Leitfragen</div>
              </div>
              <div class="stat-cell">
                <div class="stat-num">PDF</div>
                <div class="stat-label">Export</div>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-divider">
          <div class="section-divider-line"></div>
          <div class="section-divider-label">Schritt 1 von 2 &nbsp;·&nbsp; Unternehmensprofil</div>
          <div class="section-divider-line"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    themes = list(CIRCULAR_MODEL.keys())
    priority_options = ["Bitte wählen"] + themes
    current_priority = list(st.session_state.dimension_priority)
    while len(current_priority) < len(themes):
        current_priority.append(themes[len(current_priority)])

    with st.form("intake_form", clear_on_submit=False):
        col_a, col_b = st.columns(2, gap="large")
        with col_a:
            company_name = st.text_input(
                "Unternehmensname",
                value=st.session_state.company_name,
                placeholder="z. B. Muster GmbH",
            )
            sector = st.text_input(
                "Sektor",
                value=st.session_state.sector,
                placeholder="z. B. Maschinenbau, Elektronik, Medizintechnik",
            )
        with col_b:
            product_name = st.text_input(
                "Bezeichnung des Produkts",
                value=st.session_state.product_name,
                placeholder="z. B. Kreiselpumpe X200",
            )

        st.markdown("#### Relevanzreihenfolge der Dimensionen")
        st.caption("1 = höchste Relevanz für Ihr Unternehmen. Die Reihenfolge wird als Startgewichtung in die Einstellungen übernommen.")
        priority_selection = []
        p_col1, p_col2 = st.columns(2, gap="large")
        for idx, theme in enumerate(themes):
            target_col = p_col1 if idx < 3 else p_col2
            with target_col:
                default_value = current_priority[idx] if idx < len(current_priority) else themes[idx]
                default_index = priority_options.index(default_value) if default_value in priority_options else 0
                selection = st.selectbox(
                    f"Priorität {idx + 1}",
                    priority_options,
                    index=default_index,
                    key=f"priority_rank_{idx + 1}",
                )
                priority_selection.append(selection)

        submitted = st.form_submit_button("Angaben speichern und Gewichtung vorbereiten", use_container_width=True, type="primary")

    priority_is_complete = all(item in themes for item in priority_selection)
    duplicates_exist = len(set(priority_selection)) != len(themes) if priority_is_complete else False

    if submitted:
        st.session_state.company_name = company_name.strip()
        st.session_state.sector = sector.strip()
        st.session_state.product_name = product_name.strip()

        if not st.session_state.company_name or not st.session_state.sector or not st.session_state.product_name:
            st.session_state.intake_completed = False
            st.error("Bitte füllen Sie Unternehmensname, Sektor und Produktbezeichnung vollständig aus.")
        elif not priority_is_complete:
            st.session_state.intake_completed = False
            st.error("Bitte vergeben Sie für alle fünf Prioritäten jeweils eine Dimension.")
        elif duplicates_exist:
            st.session_state.intake_completed = False
            st.error("Jede Dimension darf in der Relevanzreihenfolge nur einmal vorkommen.")
        else:
            st.session_state.dimension_priority = priority_selection
            st.session_state.weights = _weights_from_priority(priority_selection)
            st.session_state.intake_completed = True
            st.success("Pflichtangaben gespeichert. Die vorgeschlagenen Gewichtungen wurden in die Einstellungen übernommen.")

    st.markdown(
        """<style>
        /* Assessment starten CTA — navy bg, white text, prominent */
        [class*="st-key-cta-start"] button,
        [class*="st-key-cta_start"] button {
          background: #0B1830 !important;
          color: #FFFFFF !important;
          border: none !important;
          font-size: 18px !important;
          font-weight: 900 !important;
          padding: 16px 32px !important;
          border-radius: 8px !important;
          box-shadow: 0 4px 20px rgba(11,24,48,0.35) !important;
          letter-spacing: -0.3px !important;
          margin-top: 12px !important;
        }
        [class*="st-key-cta-start"] button:hover,
        [class*="st-key-cta_start"] button:hover {
          background: #1A3A6B !important;
          box-shadow: 0 8px 28px rgba(11,24,48,0.40) !important;
          transform: translateY(-2px) !important;
        }
        [class*="st-key-cta-start"] button p,
        [class*="st-key-cta-start"] button span,
        [class*="st-key-cta-start"] button *,
        [class*="st-key-cta_start"] button p,
        [class*="st-key-cta_start"] button span,
        [class*="st-key-cta_start"] button * {
          color: #FFFFFF !important;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    st.button(
        "Assessment starten →",
        key="cta_start",
        use_container_width=True,
        type="primary",
        on_click=_start_assessment,
        disabled=not _is_intake_complete(),
    )


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
            <div class="topbar-inner" style="padding:14px 20px;">
              <div style="width:100%;">
                <div class="topbar-rail">
                  <div class="topbar-fill" style="--p:{pct}%;"></div>
                </div>
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
            teaser = THEME_SUMMARIES.get(theme) or CIRCULAR_MODEL[theme][first_ind].get("description", "")
            teaser = (teaser[:120] + "...") if len(teaser) > 120 else teaser

            outline = f"2px solid {ui['accent']}" if active else "none"

            if active:
                st.markdown(
                    f"<style>[class*='st-key-dim-card-{idx}']{{border-left:3px solid #1A3A6B !important;"
                    f"background:rgba(30,95,171,0.03) !important;}}</style>",
                    unsafe_allow_html=True,
                )
            with st.container(key=f"dim-card-{idx}"):
                st.markdown(
                    f"""
                    <div class="dim-row">
                      <div class="dim-left">
                        <div class="dim-icon">{icon_map.get(theme, "")}</div>
                        <div>
                          <p class="dim-title">{theme}</p>
                          <div class="dim-meta">{q_count} Leitfragen</div>
                        </div>
                      </div>
                    </div>
                    <div class="dim-desc">{teaser}</div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.container(key=f"dim-btn-{idx}"):
                    st.button(
                        "Mehr erfahren →",
                        key=f"arrow_theme_{idx}",
                        use_container_width=False,
                        on_click=_open_dimension,
                        args=(idx,),
                    )

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
                        f"<style>[class*='st-key-indicator-btn-{i}'] button{{"
                        f"background:rgba(30,95,171,0.07) !important;"
                        f"border-color:#1A3A6B !important;"
                        f"border-left-width:3px !important;"
                        f"color:#0B1830 !important;"
                        f"font-weight:800 !important;}}</style>",
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
            explanation = question_data.get("explanation", "")
            options = question_data.get("options", [])
            escaped_code = html.escape(code)
            escaped_text = html.escape(text)
            tooltip_html = ""
            if explanation:
                tooltip_html = (
                    f"<span class='q-info'>"
                    f"<span class='q-info-icon'>i</span>"
                    f"<span class='q-info-bubble'>{html.escape(explanation)}</span>"
                    f"</span>"
                )

            with st.container(key=f"q-card-{current_theme}-{current_indicator}-{code}"):
                st.markdown(f"<div id='q-{code}'></div>", unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div class="q-head">
                      <div class="q-num">{q_idx}</div>
                      <div class="q-text-wrap">
                        <div class="q-text">{escaped_code}: {escaped_text}</div>
                        {tooltip_html}
                      </div>
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
    if st.session_state.dimension_priority:
        st.caption(
            "Ausgangsbasis aus der Startseite: "
            + " > ".join(st.session_state.dimension_priority)
            + ". Die Gewichtungen bleiben hier frei anpassbar."
        )
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
    display_weights = _weights_to_integer_percentages(st.session_state.weights, themes)

    with col1:
        for theme in themes[:3]:
            raw_weights[theme] = st.number_input(
                f"**{theme}**",
                min_value=0,
                max_value=100,
                value=display_weights.get(theme, 0),
                step=1,
                key=f"weight_{theme}",
            )

    with col2:
        for theme in themes[3:]:
            raw_weights[theme] = st.number_input(
                f"**{theme}**",
                min_value=0,
                max_value=100,
                value=display_weights.get(theme, 0),
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
        ("Stufe 1", "0–25%"),
        ("Stufe 2", ">25–50%"),
        ("Stufe 3", ">50–75%"),
        ("Stufe 4", ">75–100%"),
        ("Stufe 5", "100%"),
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
    recommendation_df = indicator_df.copy()
    recommendation_df = recommendation_df[recommendation_df["Score"].notna()]
    recommendation_df = recommendation_df[recommendation_df["Score"] < 0.5]
    recommendation_df = recommendation_df.sort_values(["ThemeOrder", "Order", "Indikator"], ascending=True)

    theme_df = pd.DataFrame(
        [{"Thema": k, "Score": v, "Score_%": v * 100} for k, v in theme_scores.items()]
    ).sort_values("Score", ascending=True)

    tab_overview, tab_themes, tab_indicators, tab_questions, tab_recommendations, tab_export = st.tabs(
        ["Überblick", "Dimensionen", "Indikatoren", "Leitfragen", "Handlungsempfehlungen", "Export"]
    )

    with tab_overview:
        st.markdown("### Ihre Zirkularitätsreife")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            scale_html = "<br/>".join(
                [
                    f"{m['emoji']} {m['name']} ({m.get('label', '')}) ({rng})"
                    for m, (_, rng) in zip(MATURITY_LEVELS, maturity_scale)
                ]
            )
            st.markdown(
                f"""
            <div style='padding:28px 24px; background:#FFFFFF; border-radius:14px;
                        border:1px solid rgba(0,0,0,0.07); box-shadow:0 2px 12px rgba(0,0,0,0.05);
                        text-align:center;'>
              <div style='font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.10em;
                          color:rgba(10,10,10,0.35);margin-bottom:14px;'>Reifegrad</div>
              <div style='font-size:2.8em;margin:0 0 10px 0;'>{level['emoji']}</div>
              <div style='font-size:22px;font-weight:900;color:#0A0A0A;letter-spacing:-0.5px;margin-bottom:6px;'>
                {level['name']} <span style="font-weight:500;color:rgba(10,10,10,0.45);">({level.get('label', '')})</span>
              </div>
              <div style='font-size:13px;color:rgba(10,10,10,0.52);line-height:1.6;max-width:320px;margin:0 auto 18px auto;'>
                {level['description']}
              </div>
              <div style='display:flex;justify-content:center;gap:24px;
                          padding:14px 24px;background:#F4F6FB;border-radius:10px;margin-bottom:18px;'>
                <div style='text-align:center;'>
                  <div style='font-size:22px;font-weight:900;color:#1A3A6B;letter-spacing:-0.5px;'>{total_score:.2f}<span style="font-size:14px;color:rgba(10,10,10,0.4);font-weight:600;">/5.0</span></div>
                  <div style='font-size:11px;font-weight:600;color:rgba(10,10,10,0.38);text-transform:uppercase;letter-spacing:0.07em;margin-top:3px;'>Score</div>
                </div>
                <div style='width:1px;background:rgba(0,0,0,0.08);'></div>
                <div style='text-align:center;'>
                  <div style='font-size:22px;font-weight:900;color:#1A3A6B;letter-spacing:-0.5px;'>{total_01*100:.0f}<span style="font-size:14px;color:rgba(10,10,10,0.4);font-weight:600;">%</span></div>
                  <div style='font-size:11px;font-weight:600;color:rgba(10,10,10,0.38);text-transform:uppercase;letter-spacing:0.07em;margin-top:3px;'>Prozentwert</div>
                </div>
              </div>
              <div style='text-align:left;font-size:12px;color:rgba(10,10,10,0.55);line-height:1.7;
                          border-top:1px solid rgba(0,0,0,0.07);padding-top:14px;'>
                <div style='font-weight:700;color:rgba(10,10,10,0.35);font-size:10.5px;text-transform:uppercase;
                            letter-spacing:0.09em;margin-bottom:8px;'>Reifegrad-Skala</div>
                {scale_html}
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
        st.markdown("### Reifestufen im Überblick")
        for stage, (_, interval) in zip(MATURITY_LEVELS, maturity_scale):
            st.markdown(
                f"""
                <div style="margin-bottom:12px; padding:16px 18px; background:#ffffff; border:1px solid rgba(15,23,42,0.08);
                            border-radius:14px; box-shadow:0 8px 22px rgba(15,23,42,0.05);">
                    <div style="font-weight:900; color:#0F172A;">{stage['emoji']} {stage['name']} ({stage.get('label', '')})</div>
                    <div style="font-size:13px; color:rgba(15,23,42,0.56); margin:4px 0 8px 0;">Zuordnung: {interval}</div>
                    <div style="color:#334155; line-height:1.55;">{html.escape(stage['description'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
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
                scale = ["#E8F0FE", theme_colors.get(q_theme, "#1A3A6B")]
            else:
                scale = ["#E8F0FE", "#1A3A6B"]
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

    with tab_recommendations:
        st.markdown("### Handlungsempfehlungen")
        st.caption("Angezeigt werden nur Indikatoren mit einer Einzelbewertung unter 50 %.")

        llm_ok = llm.is_available()
        if llm_ok:
            st.markdown(
                '<div style="display:inline-flex;align-items:center;gap:8px;padding:6px 12px;'
                'background:#E8F5E9;border:1px solid #66BB6A;border-radius:999px;'
                'font-size:12px;font-weight:700;color:#2E7D32;margin-bottom:12px;">'
                '<span style="width:8px;height:8px;background:#2E7D32;border-radius:50%;"></span>'
                f'KI-Berater verbunden · {llm.DEFAULT_MODEL}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.warning(
                "Lokales LLM (Ollama) ist nicht erreichbar. "
                "Starte Ollama mit `ollama serve` und stelle sicher, dass das Modell "
                f"`{llm.DEFAULT_MODEL}` verfügbar ist (`ollama pull {llm.DEFAULT_MODEL}`). "
                "Die statischen Empfehlungen aus Anhang III bleiben verfügbar."
            )

        # Per-indicator state:
        # { measures: [{titel, kurz}], selected_idx: int|None, history: [...], generating_initial: bool }
        if "llm_chats" not in st.session_state:
            st.session_state.llm_chats = {}

        if recommendation_df.empty:
            st.success("Aktuell liegt kein Indikator unter 50 %. Es werden daher keine Handlungsempfehlungen angezeigt.")
        else:
            for row in recommendation_df.itertuples(index=False):
                recommendation_text = INDICATOR_RECOMMENDATIONS.get(row.Indikator)
                score_pct = int(round((row.Score or 0) * 100))
                if not recommendation_text:
                    st.warning(f"Für {row.Indikator} wurde in Anhang III keine Handlungsempfehlung gefunden.")
                    continue

                indicator_key = f"{row.Thema}::{row.Indikator}"
                safe_key = re.sub(r"[^A-Za-z0-9_]+", "_", indicator_key)
                theme_color = theme_colors.get(row.Thema, '#0F172A')

                st.markdown(
                    f"""
                    <div style="margin-bottom:0; padding:18px 18px 12px 18px; background:#ffffff; border-radius:16px 16px 0 0;
                                border:1px solid rgba(15,23,42,0.08); border-bottom:none;">
                        <div style="font-size:13px; font-weight:800; color:{theme_color}; text-transform:uppercase; letter-spacing:0.03em;">
                            {html.escape(row.Thema)}
                        </div>
                        <div style="margin-top:4px; font-size:18px; font-weight:900; color:#0F172A;">
                            {html.escape(row.Indikator)}
                        </div>
                        <div style="margin:6px 0 10px 0; color:rgba(15,23,42,0.62); font-weight:700;">
                            Einzelbewertung: {score_pct} %
                        </div>
                        <div style="color:#334155; line-height:1.6;"><strong>Standard (Anhang III):</strong><br>{html.escape(recommendation_text)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.container():
                    st.markdown(
                        '<div style="padding:6px 18px 18px 18px; background:#ffffff; border-radius:0 0 16px 16px;'
                        'border:1px solid rgba(15,23,42,0.08); border-top:none;'
                        'box-shadow:0 10px 24px rgba(15,23,42,0.05); margin-bottom:14px;">',
                        unsafe_allow_html=True,
                    )

                    with st.expander("KI-Berater: Maßnahmen erarbeiten", expanded=False):
                        chat = st.session_state.llm_chats.setdefault(
                            indicator_key,
                            {"measures": [], "selected_idx": None, "history": []},
                        )

                        ctx = dict(
                            product=st.session_state.get("product_name") or "",
                            company=st.session_state.get("company_name") or "",
                            sector=st.session_state.get("sector") or "",
                            theme=row.Thema,
                            indicator=row.Indikator,
                            score_pct=score_pct,
                            base_recommendation=recommendation_text,
                        )

                        # ── PHASE 1: generate measure list ────────────────
                        if not chat["measures"]:
                            st.caption(
                                "Der KI-Berater schlägt 4–6 konkrete Maßnahmen vor. "
                                "Anschließend kannst du eine auswählen und gemeinsam die Umsetzung erarbeiten."
                            )
                            if st.button(
                                "Maßnahmen-Vorschläge generieren",
                                key=f"gen_measures_{safe_key}",
                                type="primary",
                                disabled=not llm_ok,
                                use_container_width=True,
                            ):
                                with st.spinner("KI-Berater erarbeitet Maßnahmen…"):
                                    try:
                                        raw = llm.query_ollama(
                                            llm.build_measures_messages(**ctx),
                                            json_mode=True,
                                        )
                                        measures = llm.parse_measures(raw)
                                    except Exception as e:
                                        st.error(f"LLM-Fehler: {e}")
                                        measures = []
                                if measures:
                                    chat["measures"] = measures
                                    st.rerun()
                                else:
                                    st.error("Konnte keine Maßnahmen extrahieren. Bitte erneut versuchen.")

                        # ── PHASE 2: show measure cards & detail ──────────
                        else:
                            col_back, col_reset = st.columns([3, 1])
                            with col_back:
                                if chat["selected_idx"] is not None:
                                    if st.button(
                                        "← Andere Maßnahme wählen",
                                        key=f"back_{safe_key}",
                                        use_container_width=True,
                                    ):
                                        chat["selected_idx"] = None
                                        chat["history"] = []
                                        st.rerun()
                            with col_reset:
                                if st.button(
                                    "Zurücksetzen",
                                    key=f"reset_{safe_key}",
                                    use_container_width=True,
                                ):
                                    st.session_state.llm_chats[indicator_key] = {
                                        "measures": [], "selected_idx": None, "history": []
                                    }
                                    st.rerun()

                            if chat["selected_idx"] is None:
                                # Show measure list
                                st.markdown("**Vorgeschlagene Maßnahmen — wähle eine zur vertieften Beratung:**")
                                for i, m in enumerate(chat["measures"]):
                                    st.markdown(
                                        f'<div style="padding:10px 14px; margin:6px 0; background:#F4F6FB; '
                                        f'border-left:3px solid {theme_color}; border-radius:6px;">'
                                        f'<div style="font-weight:800; color:#0F172A; font-size:14.5px;">{html.escape(m["titel"])}</div>'
                                        f'<div style="font-size:13px; color:#475569; margin-top:2px;">{html.escape(m.get("kurz", ""))}</div>'
                                        f'</div>',
                                        unsafe_allow_html=True,
                                    )
                                    if st.button(
                                        f"Diese Maßnahme vertiefen →",
                                        key=f"pick_{safe_key}_{i}",
                                        use_container_width=True,
                                    ):
                                        chat["selected_idx"] = i
                                        chat["history"] = []
                                        # Trigger initial drilldown on next run via flag
                                        chat["pending_drilldown"] = True
                                        st.rerun()

                            else:
                                # Drilldown view for selected measure
                                m = chat["measures"][chat["selected_idx"]]
                                st.markdown(
                                    f'<div style="padding:12px 16px; background:linear-gradient(135deg,{theme_color}15 0%,#F4F6FB 100%); '
                                    f'border-left:4px solid {theme_color}; border-radius:6px; margin:8px 0 14px 0;">'
                                    f'<div style="font-size:11px; font-weight:800; letter-spacing:0.08em; '
                                    f'text-transform:uppercase; color:{theme_color};">Aktuelle Maßnahme</div>'
                                    f'<div style="font-weight:900; color:#0F172A; font-size:16px; margin-top:2px;">{html.escape(m["titel"])}</div>'
                                    f'<div style="font-size:13px; color:#475569; margin-top:2px;">{html.escape(m.get("kurz", ""))}</div>'
                                    f'</div>',
                                    unsafe_allow_html=True,
                                )

                                # Render history FIRST (avoids duplicate when streaming new content)
                                for msg in chat["history"]:
                                    with st.chat_message(msg["role"]):
                                        st.markdown(msg["content"])

                                # Initial drilldown on first entry
                                if chat.get("pending_drilldown"):
                                    chat["pending_drilldown"] = False
                                    drill_msgs = llm.build_drilldown_messages(
                                        **ctx,
                                        measure_title=m["titel"],
                                        measure_summary=m.get("kurz", ""),
                                    )
                                    with st.chat_message("assistant"):
                                        placeholder = st.empty()
                                        buffer = ""
                                        try:
                                            for piece in llm.stream_ollama(drill_msgs):
                                                buffer += piece
                                                placeholder.markdown(buffer + "▌")
                                            placeholder.markdown(buffer)
                                        except Exception as e:
                                            st.error(f"LLM-Fehler: {e}")
                                            buffer = ""
                                    if buffer:
                                        chat["history"].append({"role": "assistant", "content": buffer})

                                # Free chat input
                                if llm_ok and chat["history"]:
                                    user_input = st.chat_input(
                                        "Nachfrage stellen (z. B. 'Was tun wenn Schritt 2 nicht klappt?')",
                                        key=f"chat_{safe_key}",
                                    )
                                    if user_input:
                                        with st.chat_message("user"):
                                            st.markdown(user_input)
                                        chat["history"].append({"role": "user", "content": user_input})

                                        followup_msgs = llm.build_followup_messages(
                                            **ctx,
                                            measure_title=m["titel"],
                                            measure_summary=m.get("kurz", ""),
                                            history=chat["history"][:-1],
                                            user_question=user_input,
                                        )
                                        with st.chat_message("assistant"):
                                            placeholder = st.empty()
                                            buffer = ""
                                            try:
                                                for piece in llm.stream_ollama(followup_msgs):
                                                    buffer += piece
                                                    placeholder.markdown(buffer + "▌")
                                                placeholder.markdown(buffer)
                                            except Exception as e:
                                                st.error(f"LLM-Fehler: {e}")
                                                buffer = ""
                                        if buffer:
                                            chat["history"].append({"role": "assistant", "content": buffer})

                    st.markdown("</div>", unsafe_allow_html=True)

    with tab_export:
        st.markdown("### Export & Speicherung")
        col1, col2 = st.columns(2)

        with col1:
            product_name = st.text_input("Produktname", st.session_state.product_name or "Mein Produkt")
            company = st.text_input("Unternehmensname", st.session_state.company_name or "Mein Unternehmen")
            sector = st.text_input("Sektor", st.session_state.sector or "Nicht angegeben")

            if st.button("Assessment speichern", use_container_width=True, type="primary"):
                st.session_state.product_name = product_name
                st.session_state.company_name = company
                st.session_state.sector = sector
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
                        file_name=f"Unity_Circularity_Assessment_{datetime.now().strftime('%Y%m%d')}.pdf",
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
    if st.session_state.current_page != "welcome" and not _is_intake_complete():
        st.session_state.current_page = "welcome"

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
