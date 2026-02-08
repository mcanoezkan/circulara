# ============================================================================
# UTILITY FUNCTIONS - CHARTS, PDF, CALCULATIONS
# ============================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
import json

# ============================================================================
# SCORING & CALCULATIONS
# ============================================================================

def calculate_theme_score(theme_answers):
    """
    Berechne Score für ein Thema (Durchschnitt der Indikatoren)

    Args:
        theme_answers (dict): {Indikator: {Frage1: score, Frage2: score, ...}}

    Returns:
        float: Theme Score (0-1)
    """
    all_scores = []
    for indicator, questions in theme_answers.items():
        for question, score in questions.items():
            all_scores.append(score)
    
    return sum(all_scores) / len(all_scores) if all_scores else 0

def calculate_total_score(theme_scores, weights):
    """
    Berechne Gesamt-Zirkularitätsscore (gewichtet)

    Args:
        theme_scores (dict): {Thema: Score}
        weights (dict): {Thema: Gewichtung}

    Returns:
        float: Gewichteter Gesamtscore (0-1)
    """
    weighted_sum = sum(theme_scores[theme] * weights[theme] 
                       for theme in theme_scores.keys())
    total_weight = sum(weights.values())
    
    return weighted_sum / total_weight if total_weight > 0 else 0

def get_maturity_level(score):
    """
    Mapping Score → Reifegradlevel

    Args:
        score (float): Score 0-1

    Returns:
        dict: {name, emoji, description}
    """
    from config import MATURITY_LEVELS

    for level in MATURITY_LEVELS:
        if level["min_score"] <= score < level["max_score"]:
            return level
    return MATURITY_LEVELS[-1]

def get_improvement_areas(theme_scores, threshold=0.5):
    """
    Identifiziere Verbesserungsfelder (Scores < Schwellenwert)

    Args:
        theme_scores (dict): {Thema: Score}
        threshold (float): Schwellenwert (0-1)

    Returns:
        list: Themen mit niedrigen Scores
    """
    return [theme for theme, score in theme_scores.items() if score < threshold]

# ============================================================================
# VISUALISIERUNGEN (PLOTLY)
# ============================================================================

def create_radar_chart(theme_scores, title="Circularity Fit Check - Radar Chart", theme_colors=None):
    """
    Erstelle interaktives Radar-Diagramm
    
    Args:
        theme_scores (dict): {Thema: Score}
        title (str): Chart-Titel
    
    Returns:
        plotly.graph_objects.Figure
    """
    themes = list(theme_scores.keys())
    scores = [theme_scores.get(t, 0) or 0 for t in themes]
    
    max_score = 1.0 if scores and max(scores) <= 1.01 else 5.0

    closed_scores = scores + [scores[0]] if scores else scores
    closed_themes = themes + [themes[0]] if themes else themes

    fig = go.Figure(
        data=go.Scatterpolar(
            r=closed_scores,
            theta=closed_themes,
            fill='toself',
            name='Gesamtprofil',
            line=dict(color='#0F172A', width=2),
            fillcolor='rgba(15, 23, 42, 0.08)',
        )
    )

    if theme_colors:
        for theme, value in zip(themes, scores):
            color = theme_colors.get(theme, "#0F766E")
            fig.add_trace(
                go.Scatterpolar(
                    r=[value],
                    theta=[theme],
                    mode="markers+text",
                    text=[f"{value:.2f}"],
                    textposition="top center",
                    marker=dict(size=11, color=color, line=dict(color="#0B1220", width=0.6)),
                    name=theme,
                )
            )

    if themes:
        fig.add_trace(
            go.Scatterpolar(
                r=[max_score] * (len(themes) + 1),
                theta=closed_themes,
                mode="lines",
                line=dict(color="rgba(15,23,42,0.15)", width=1, dash="dash"),
                hoverinfo="skip",
                showlegend=False,
            )
        )
    
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(255,255,255,0.92)",
            radialaxis=dict(
                visible=True,
                range=[0, max_score],
                tickfont=dict(size=10, color="rgba(15,23,42,0.7)"),
                gridcolor='rgba(15,23,42,0.10)',
                gridwidth=1,
                tickformat=".2f" if max_score <= 1.01 else ".0f",
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="rgba(15,23,42,0.8)"),
                gridcolor='rgba(15,23,42,0.10)',
                linecolor='rgba(15,23,42,0.2)',
            ),
        ),
        title=dict(text=title, font=dict(size=20, color='#0F172A')),
        template='plotly_white',
        hovermode='closest',
        font=dict(family="Avenir, Helvetica, Arial, sans-serif", size=11),
        height=520,
        showlegend=False,
        margin=dict(l=30, r=30, t=60, b=30),
    )
    
    return fig

def create_heatmap(theme_answers, theme_name):
    """
    Erstelle Heatmap der Indikatoren im Thema
    
    Args:
        theme_answers (dict): {Indikator: {Frage: Score}}
        theme_name (str): Name des Themas
    
    Returns:
        plotly.graph_objects.Figure
    """
    indicators = []
    questions = []
    scores = []
    
    for indicator, qs in theme_answers.items():
        for question, score in qs.items():
            indicators.append(indicator)
            questions.append(question[:40] + "..." if len(question) > 40 else question)
            scores.append(score)
    
    # Erstelle Matrix
    unique_indicators = list(theme_answers.keys())
    unique_questions = []
    score_matrix = []
    
    for indicator in unique_indicators:
        row = []
        for question, score in theme_answers[indicator].items():
            if question not in unique_questions:
                unique_questions.append(question)
            row.append(score)
        score_matrix.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=score_matrix,
        x=unique_questions,
        y=unique_indicators,
        colorscale='RdYlGn',
        zmid=2.5,
        zmin=0,
        zmax=5,
        colorbar=dict(title="Score")
    ))
    
    fig.update_layout(
        title=f"Heatmap: {theme_name}",
        xaxis_title="Leitfragen",
        yaxis_title="Indikatoren",
        height=400,
        template='plotly_white'
    )
    
    return fig

def create_comparison_chart(assessments_df):
    """
    Vergleich mehrerer Assessments
    
    Args:
        assessments_df (pd.DataFrame): Assessment-Historie
    
    Returns:
        plotly.graph_objects.Figure
    """
    theme_cols = ["Design_Score", "Strategie_Score", "Wirtschaftlichkeit_Score", 
                  "Regulatorik_Score", "Systemische_Befaehiger_Score"]
    
    fig = go.Figure()
    
    for idx, row in assessments_df.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row[col] for col in theme_cols],
            theta=['Design', 'Strategie', 'Wirtschaftlichkeit', 'Regulatorik', 'Systemische Befähiger'],
            fill='toself',
            name=f"{row['Product_Name']} ({row['Timestamp'][:10]})",
            opacity=0.7
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5]),
            angularaxis=dict(tickfont=dict(size=10))
        ),
        title="Assessment Vergleich",
        template='plotly_white',
        height=500
    )
    
    return fig

def create_gauge_chart(total_score, max_score=5):
    """
    Gauge-Chart für Gesamtscore
    
    Args:
        total_score (float): Gesamtscore
        max_score (float): Maximaler Score
    
    Returns:
        plotly.graph_objects.Figure
    """
    level = get_maturity_level(total_score)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=total_score,
        title={'text': f"Zirkularitäts-Score ({level['emoji']} {level['name']})"},
        delta={'reference': max_score * 0.7},
        gauge={
            'axis': {'range': [None, max_score]},
            'bar': {'color': level['color']},
            'steps': [
                {'range': [0, 1], 'color': "#d32f2f"},
                {'range': [1, 2], 'color': "#ff6f00"},
                {'range': [2, 3], 'color': "#fbc02d"},
                {'range': [3, 4], 'color': "#7cb342"},
                {'range': [4, 5], 'color': "#388e3c"}
            ],
            'threshold': {
                'line': {'color': 'red', 'width': 4},
                'thickness': 0.75,
                'value': 2.5
            }
        }
    ))
    
    fig.update_layout(
        title_font_size=20,
        font=dict(family="Arial", size=12),
        height=400,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig

# ============================================================================
# PDF-EXPORT
# ============================================================================

def generate_pdf_report(
    product_name,
    company,
    theme_scores,
    weights,
    detailed_answers,
    improvement_areas,
    theme_colors=None,
):
    """
    Generiere detaillierten PDF-Report
    
    Args:
        product_name (str)
        company (str)
        theme_scores (dict): {Thema: Score}
        weights (dict): {Thema: Gewichtung}
        detailed_answers (dict): Alle Fragen+Answers
        improvement_areas (list): Schwache Bereiche
    
    Returns:
        BytesIO: PDF als Bytes
    """
    
    # Erstelle PDF-Datei im Memory
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4,
                           rightMargin=0.5*inch, leftMargin=0.5*inch,
                           topMargin=0.6*inch, bottomMargin=0.6*inch)
    
    # Sammle Elemente
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1F7E8A',
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#1F7E8A',
        spaceAfter=6,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    # Title
    elements.append(Paragraph(
        f"🌍 Circularity Fit Check Report",
        title_style
    ))
    elements.append(Spacer(1, 0.15*inch))
    
    # Metadata
    metadata_text = f"""
    <b>Produkt:</b> {product_name}<br/>
    <b>Unternehmen:</b> {company}<br/>
    <b>Datum:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}<br/>
    <b>Bewertungsphase:</b> Post-Design Phase
    """
    elements.append(Paragraph(metadata_text, styles['Normal']))
    elements.append(Spacer(1, 0.18*inch))
    
    # Total Score
    weighted_sum = 0.0
    used_weights = 0.0
    for theme, score in theme_scores.items():
        if score is None:
            continue
        weight = weights.get(theme, 0.0)
        weighted_sum += score * weight
        used_weights += weight
    total_score_01 = (weighted_sum / used_weights) if used_weights else 0.0
    total_score_5 = total_score_01 * 5.0
    level = get_maturity_level(total_score_01)
    
    score_text = f"""
    <b>Gesamt-Zirkularitätsscore: {total_score_5:.2f}/5.0</b><br/>
    <b>Reifegradlevel:</b> {level['name']} ({level['emoji']})
    """
    elements.append(Paragraph(score_text, styles['Normal']))
    elements.append(Spacer(1, 0.18*inch))
    elements.append(Paragraph("Reifegrad-Skala", heading_style))
    elements.append(Paragraph(
        "Sehr gering (0.00–0.20)<br/>Gering (0.20–0.40)<br/>Mittel (0.40–0.60)<br/>"
        "Fortgeschritten (0.60–0.80)<br/>Sehr hoch (0.80–1.00)",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.12*inch))

    def plotly_to_rl_image(fig, width=900, height=520):
        try:
            img_bytes = pio.to_image(fig, format="png", width=width, height=height, scale=2)
        except Exception:
            return None
        return Image(BytesIO(img_bytes), width=6.8*inch, height=3.8*inch)

    # Charts
    try:
        from config import CIRCULAR_MODEL
        if theme_colors is None:
            theme_colors = {}
    except Exception:
        CIRCULAR_MODEL = {}
        if theme_colors is None:
            theme_colors = {}

    radar_fig = create_radar_chart(theme_scores, "Zirkularitäts-Profil", theme_colors=theme_colors)
    radar_img = plotly_to_rl_image(radar_fig, width=800, height=420)
    elements.append(Paragraph("📊 Zirkularitäts-Profil", heading_style))
    if radar_img:
        elements.append(radar_img)
    else:
        elements.append(Paragraph("Hinweis: Chart-Export nicht verfügbar (kaleido fehlt).", styles['Normal']))
    elements.append(Spacer(1, 0.18*inch))

    # Themen-Scores
    elements.append(Paragraph("📊 Themen-Scores", heading_style))
    
    score_table_data = [["Thema", "Score", "Gewichtung", "Beitrag"]]
    for theme in theme_scores.keys():
        score = theme_scores[theme]
        weight = weights.get(theme, 0.0)
        contrib = (score * weight) / used_weights if used_weights else 0.0
        score_table_data.append([
            theme,
            f"{(score or 0):.2f}",
            f"{weight:.2f}x",
            f"{contrib:.2f}"
        ])
    
    score_table = Table(score_table_data, colWidths=[2.2*inch, 0.7*inch, 0.8*inch, 0.8*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F7E8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Detaillierte Answers
    elements.append(PageBreak())
    elements.append(Paragraph("📋 Detaillierte Bewertung (inkl. Nicht-Bewertet)", heading_style))

    for theme, indicators in CIRCULAR_MODEL.items():
        elements.append(Paragraph(f"<b>{theme}</b>", styles['Heading3']))
        for indicator, indicator_data in indicators.items():
            elements.append(Paragraph(f"<i>{indicator}</i>", styles['Normal']))
            rows = [["Code", "Frage", "Score", "Bewertet"]]
            for q in indicator_data.get("questions", []):
                code = q.get("code", "")
                text = q.get("text", "")
                score = detailed_answers.get(theme, {}).get(indicator, {}).get(code)
                if score is None:
                    score_display = "—"
                    bewertet = "Nein"
                else:
                    score_display = f"{score:.2f}"
                    bewertet = "Ja"
                rows.append([code, Paragraph(text, styles['BodyText']), score_display, bewertet])

            table = Table(rows, colWidths=[0.7*inch, 4.6*inch, 0.7*inch, 0.8*inch], repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (3, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.2*inch))
    
    # Build PDF
    doc.build(elements)
    pdf_buffer.seek(0)
    
    return pdf_buffer

def create_quick_summary(theme_scores, improvement_areas):
    """
    Erstelle Text-Zusammenfassung
    
    Args:
        theme_scores (dict)
        improvement_areas (list)
    
    Returns:
        str: Markdown-Zusammenfassung
    """
    total_score = sum(theme_scores.values()) / len(theme_scores)
    level = get_maturity_level(total_score)
    
    summary = f"""
## 🎯 Zusammenfassung Circularity Fit Check
    
**Gesamtscore:** {total_score:.2f}/5.0 ({level['name']})

### Themen-Übersicht
"""
    for theme, score in theme_scores.items():
        emoji = "🔴" if score < 2 else "🟠" if score < 3 else "🟡" if score < 4 else "🟢"
        summary += f"- **{theme}**: {score:.2f}/5.0 {emoji}\n"
    
    if improvement_areas:
        summary += f"\n### 🔧 Prioritäre Verbesserungsfelder\n"
        for area in improvement_areas:
            summary += f"- {area}\n"
    
    summary += f"\n### ✨ Nächste Schritte\n"
    summary += "1. Priorisieren Sie die Verbesserungsfelder\n"
    summary += "2. Definieren Sie konkrete Maßnahmen\n"
    summary += "3. Tracken Sie Fortschritt in regelmäßigen Assessments\n"
    
    return summary
