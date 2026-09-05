"""PDF Report Generator for RiskLens AI using ReportLab."""
import io
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


def generate_investigation_pdf(investigation: Dict[str, Any]) -> io.BytesIO:
    """Generate a clean, professional banking analyst investigation PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0F172A")    # Slate 900
    accent_blue = colors.HexColor("#1D4ED8")      # Blue 700
    alert_red = colors.HexColor("#DC2626")        # Red 600
    alert_green = colors.HexColor("#16A34A")      # Green 600
    border_gray = colors.HexColor("#CBD5E1")      # Slate 300
    bg_light = colors.HexColor("#F8FAFC")         # Slate 50

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#64748B")
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    bold_body_style = ParagraphStyle(
        "BoldBody_Custom",
        parent=body_style,
        fontName="Helvetica-Bold"
    )

    disclaimer_style = ParagraphStyle(
        "Disclaimer_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#475569")
    )

    elements = []

    # Header section
    header_data = [
        [
            Paragraph("<b>RiskLens AI</b> — Banking Risk Investigation Assistant", title_style),
            Paragraph(f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}<br/>Confidential Bank Artifact", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[350, 180])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=8, spaceAfter=12))

    # Case Summary Box
    cid = investigation.get("customer_id", "N/A")
    cname = investigation.get("customer_name", "N/A")
    status_text = investigation.get("badge_text", "Under Review")
    score = investigation.get("priority_score", 0)
    risk_level = investigation.get("risk_level", "NORMAL")

    status_color = alert_green if "NO ATTENTION" in status_text.upper() else alert_red

    case_info = [
        [Paragraph("<b>Customer ID:</b>", body_style), Paragraph(cid, bold_body_style),
         Paragraph("<b>Overall Status:</b>", body_style), Paragraph(f"<font color='{status_color.hexval()}'><b>{status_text}</b></font>", bold_body_style)],
        [Paragraph("<b>Customer Name:</b>", body_style), Paragraph(cname, body_style),
         Paragraph("<b>Priority Score:</b>", body_style), Paragraph(f"{score}/100 ({risk_level})", bold_body_style)],
        [Paragraph("<b>Analyzed Records:</b>", body_style), Paragraph(str(investigation.get("baseline", {}).get("transaction_count", 0)), body_style),
         Paragraph("<b>Active Hours:</b>", body_style), Paragraph(investigation.get("baseline", {}).get("typical_hours", {}).get("display", "N/A"), body_style)]
    ]
    info_table = Table(case_info, colWidths=[95, 170, 95, 170])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg_light),
        ("BOX", (0, 0), (-1, -1), 0.5, border_gray),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 14))

    # Executive Summary
    elements.append(Paragraph("EXECUTIVE SUMMARY", h1_style))
    summary_text = investigation.get("summary", "Investigation completed.")
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 12))

    # Deterministic Findings
    findings: List[Dict[str, Any]] = investigation.get("findings", [])
    elements.append(Paragraph(f"DETERMINISTIC FINDINGS ({len(findings)})", h1_style))

    if not findings:
        elements.append(Paragraph("✓ No risk rules were triggered. All transactions conform to the customer's behavioral baseline.", body_style))
    else:
        finding_rows = [
            [
                Paragraph("<b>Finding ID</b>", bold_body_style),
                Paragraph("<b>Rule</b>", bold_body_style),
                Paragraph("<b>Severity</b>", bold_body_style),
                Paragraph("<b>Transactions</b>", bold_body_style),
                Paragraph("<b>Observed vs Baseline Deviation</b>", bold_body_style)
            ]
        ]
        for f in findings:
            txns_str = ", ".join(f.get("transaction_ids", [])[:3])
            if len(f.get("transaction_ids", [])) > 3:
                txns_str += f" (+{len(f.get('transaction_ids', [])) - 3} more)"

            dev_text = f.get("description", "")
            if f.get("evidence"):
                dev_text = f"{f['evidence'][0].get('deviation', '')} — {f['evidence'][0].get('explanation', '')}"

            finding_rows.append([
                Paragraph(f.get("finding_id", ""), body_style),
                Paragraph(f.get("rule_id", ""), bold_body_style),
                Paragraph(f.get("severity", ""), bold_body_style),
                Paragraph(txns_str, body_style),
                Paragraph(dev_text, body_style)
            ])

        f_table = Table(finding_rows, colWidths=[65, 55, 60, 110, 240])
        f_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("BOX", (0, 0), (-1, -1), 0.5, border_gray),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("PADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "TOP")
        ]))
        elements.append(f_table)

    elements.append(Spacer(1, 14))

    # Correlated Events
    correlated = investigation.get("correlated_events", [])
    if correlated:
        elements.append(Paragraph(f"CORRELATED INCIDENT CLUSTERS ({len(correlated)})", h1_style))
        for c in correlated:
            elements.append(Paragraph(f"<b>Cluster {c['event_id']}</b>: {c['summary']}", body_style))
            elements.append(Paragraph(f"Involved Transactions: {', '.join(c['transaction_ids'])} | Duration: {c['time_window']['duration_minutes']} minutes", subtitle_style))
            elements.append(Spacer(1, 4))
        elements.append(Spacer(1, 10))

    # Recommended Investigator Actions
    actions = investigation.get("recommended_actions", [])
    elements.append(Paragraph("RECOMMENDED INVESTIGATOR ACTIONS", h1_style))
    if not actions:
        elements.append(Paragraph("No immediate investigator action required. Maintain standard account monitoring.", body_style))
    else:
        for idx, act in enumerate(actions, 1):
            elements.append(Paragraph(f"<b>{idx}.</b> {act}", body_style))
            elements.append(Spacer(1, 2))
    elements.append(Spacer(1, 12))

    # Explicit Unknowns Section
    unknowns = investigation.get("unknowns", [])
    elements.append(Paragraph("INFORMATION REMAINING UNKNOWN", h1_style))
    for u in unknowns:
        elements.append(Paragraph(f"• {u}", body_style))
        elements.append(Spacer(1, 2))
    elements.append(Spacer(1, 14))

    # Mandatory Human Review Disclaimer Box
    elements.append(HRFlowable(width="100%", thickness=0.5, color=border_gray, spaceBefore=4, spaceAfter=8))
    disclaimer_p = Paragraph(
        "<b>HUMAN INVESTIGATOR REVIEW REQUIRED:</b><br/>"
        "RiskLens AI provides evidence-first behavioral analysis and identifies unusual activity requiring attention. "
        "This system does not determine whether fraud occurred, does not decide guilt, and does not replace human judgment. "
        "The final investigative conclusion must be made by a qualified human investigator.",
        disclaimer_style
    )
    elements.append(disclaimer_p)

    doc.build(elements)
    buffer.seek(0)
    return buffer
