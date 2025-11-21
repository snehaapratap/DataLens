# app/utils/pdf_generator.py

import os
from typing import Dict, Any, List

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

import matplotlib.pyplot as plt


def _build_key_metrics_table(key_metrics: Dict[str, Any]) -> Table:
    data = [["Metric", "Value"]]
    for k, v in key_metrics.items():
        data.append([str(k), str(v)])

    table = Table(data, colWidths=[3 * inch, 3 * inch])
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    )
    table.setStyle(style)
    return table


def _make_chart_image(key_metrics: Dict[str, Any], chart_path: str) -> bool:
    numeric_items = {k: v for k, v in key_metrics.items() if isinstance(v, (int, float))}
    if not numeric_items:
        return False

    labels = list(numeric_items.keys())
    values = list(numeric_items.values())

    plt.figure(figsize=(6, 3))
    plt.bar(labels, values)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return True


def generate_pdf(report: Dict[str, Any], pdf_path: str) -> None:
    """
    Create a nicely formatted PDF with:
    - Title + summary
    - Key metrics table
    - Lists of trends and correlations
    - Simple bar chart from numeric key metrics (if any)
    """
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story: List[Any] = []

    # Title
    title = Paragraph("DataLens AI Report", styles["Title"])
    story.append(title)
    story.append(Spacer(1, 0.2 * inch))

    # Summary
    summary_text = report.get("summary", "No summary available.")
    story.append(Paragraph("<b>Executive Summary</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(summary_text, styles["BodyText"]))
    story.append(Spacer(1, 0.2 * inch))

    # Key metrics table
    key_metrics = report.get("key_metrics", {}) or {}
    if key_metrics:
        story.append(Paragraph("<b>Key Metrics</b>", styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))
        story.append(_build_key_metrics_table(key_metrics))
        story.append(Spacer(1, 0.2 * inch))

    # Trends
    trends = report.get("trends", []) or []
    if trends:
        story.append(Paragraph("<b>Trends</b>", styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))
        for t in trends:
            desc = t.get("description") or ""
            metric = t.get("metric", "")
            direction = t.get("direction", "")
            bullet = f"{metric} ({direction}): {desc}"
            story.append(Paragraph(f"• {bullet}", styles["BodyText"]))
        story.append(Spacer(1, 0.2 * inch))

    # Correlations
    corrs = report.get("correlations", []) or []
    if corrs:
        story.append(Paragraph("<b>Correlations</b>", styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))
        for c in corrs:
            a = c.get("a", "")
            b = c.get("b", "")
            coef = c.get("coefficient", 0)
            bullet = f"{a} ↔ {b}: correlation {coef:.2f}"
            story.append(Paragraph(f"• {bullet}", styles["BodyText"]))
        story.append(Spacer(1, 0.2 * inch))

    # Recommendations
    recs = report.get("recommendations", []) or []
    if recs:
        story.append(Paragraph("<b>Recommendations</b>", styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))
        for r in recs:
            story.append(Paragraph(f"• {r}", styles["BodyText"]))
        story.append(Spacer(1, 0.2 * inch))

    # Chart (if any numeric key metrics)
    chart_path = pdf_path.replace(".pdf", "_chart.png")
    if key_metrics and _make_chart_image(key_metrics, chart_path):
        from reportlab.platypus import Image

        story.append(Paragraph("<b>Key Metrics Chart</b>", styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Image(chart_path, width=5 * inch, height=3 * inch))
        story.append(Spacer(1, 0.2 * inch))

    doc.build(story)
