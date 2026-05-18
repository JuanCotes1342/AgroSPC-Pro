from __future__ import annotations

from io import BytesIO

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
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
    doc = SimpleDocTemplate(output, pagesize=landscape(letter), title=title, leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle("TableCell", parent=styles["BodyText"], fontSize=6, leading=7)
    header_style = ParagraphStyle("TableHeader", parent=cell_style, textColor=colors.white)
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
        preview = table.copy()
        numeric_cols = preview.select_dtypes(include="number").columns
        preview[numeric_cols] = preview[numeric_cols].round(4)
        preview = preview.astype(str)
        data = [[Paragraph(col, header_style) for col in preview.columns.tolist()]]
        data.extend([[Paragraph(value, cell_style) for value in row] for row in preview.values.tolist()])
        page_width = doc.width
        col_width = page_width / max(len(preview.columns), 1)
        tbl = Table(data, colWidths=[col_width] * len(preview.columns), repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b2545")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), .25, colors.lightgrey),
            ("FONT", (0, 0), (-1, -1), "Helvetica", 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(tbl)
    doc.build(story)
    return output.getvalue()
