from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models import Application


def generate_pdf_report(application: Application, output_dir: str = "reports") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    path = Path(output_dir) / f"creditwise_report_{application.id}.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=letter, title=f"CreditWise Report #{application.id}")
    styles = getSampleStyleSheet()
    prediction = application.prediction
    story = [Paragraph("CreditWise AI Credit Card Decision Report", styles["Title"]), Spacer(1, 14)]
    applicant_rows = [
        ["Applicant", application.applicant_name],
        ["Age", application.age],
        ["Education", application.education],
        ["Employment", application.employment_type],
        ["Annual Income", f"${application.annual_income:,.2f}"],
        ["Debt-to-Income Ratio", f"{application.debt_to_income_ratio:.2%}"],
        ["Previous Defaults", application.previous_defaults],
    ]
    decision_rows = [
        ["Decision", prediction.decision],
        ["Approval Probability", f"{prediction.approval_probability:.2%}"],
        ["Confidence", f"{prediction.confidence_score:.2%}"],
        ["Credit Score", prediction.credit_score],
        ["Risk Level", prediction.risk_level],
        ["Recommended Credit Limit", f"${prediction.recommended_credit_limit:,.2f}"],
    ]
    for title, rows in [("Applicant Details", applicant_rows), ("Decision Summary", decision_rows)]:
        story.append(Paragraph(title, styles["Heading2"]))
        table = Table(rows, colWidths=[180, 320])
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef2f7")), ("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("PADDING", (0, 0), (-1, -1), 8)]))
        story.extend([table, Spacer(1, 12)])
    story.append(Paragraph("Decision Explanation", styles["Heading2"]))
    story.append(Paragraph(prediction.explanation, styles["BodyText"]))
    story.append(Spacer(1, 12))
    factors = [["Approval Factors", "Impact"]] + [[x["label"], x["impact"]] for x in prediction.top_approval_factors]
    story.append(Table(factors, colWidths=[380, 120], style=[("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d1fae5")), ("PADDING", (0, 0), (-1, -1), 7)]))
    story.append(Spacer(1, 12))
    risks = [["Risk Factors", "Impact"]] + [[x["label"], x["impact"]] for x in prediction.top_rejection_factors]
    story.append(Table(risks, colWidths=[380, 120], style=[("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#fee2e2")), ("PADDING", (0, 0), (-1, -1), 7)]))
    doc.build(story)
    return str(path)
