from __future__ import annotations

from io import BytesIO

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def excel_bytes(sheets: dict[str, pd.DataFrame]) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, df in sheets.items():
            safe = name[:31].replace("/", "-")
            df.to_excel(writer, sheet_name=safe, index=False)
    return output.getvalue()


def csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def pdf_report(title: str, metadata: dict, conclusions: list[str], table: pd.DataFrame | None = None) -> bytes:
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter, title=title)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
    story.append(Paragraph("SPC Agroindustrial - Reporte automatico", styles["Heading2"]))
    for key, value in metadata.items():
        story.append(Paragraph(f"<b>{key}:</b> {value}", styles["BodyText"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Conclusiones", styles["Heading2"]))
    for item in conclusions:
        story.append(Paragraph(f"- {item}", styles["BodyText"]))
    if table is not None and not table.empty:
        story.append(Spacer(1, 12))
        story.append(Paragraph("Resumen tabular", styles["Heading2"]))
        preview = table.head(12).round(4).astype(str)
        data = [preview.columns.tolist()] + preview.values.tolist()
        tbl = Table(data)
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b2545")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), .25, colors.lightgrey),
            ("FONT", (0, 0), (-1, -1), "Helvetica", 7),
        ]))
        story.append(tbl)
    doc.build(story)
    return output.getvalue()
