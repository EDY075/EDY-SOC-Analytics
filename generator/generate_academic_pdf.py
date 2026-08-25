"""Render the academic report as a polished, verifiable PDF."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "RELATORIO_ACADEMICO.md"
OUTPUT = ROOT / "output" / "pdf" / "RELATORIO_ACADEMICO.pdf"


def register_fonts() -> None:
    regular = Path(r"C:\Windows\Fonts\segoeui.ttf")
    bold = Path(r"C:\Windows\Fonts\segoeuib.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("SegoeUI", str(regular)))
        pdfmetrics.registerFont(TTFont("SegoeUI-Bold", str(bold)))
    else:
        raise FileNotFoundError("Segoe UI fonts were not found.")


def escape(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def header_footer(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#39C6E6"))
    canvas.setLineWidth(0.8)
    canvas.line(22 * mm, height - 16 * mm, width - 22 * mm, height - 16 * mm)
    canvas.setFont("SegoeUI", 8)
    canvas.setFillColor(colors.HexColor("#566579"))
    canvas.drawString(22 * mm, 11 * mm, "EDY SOC Analytics | Edmilson Gomes")
    canvas.drawRightString(width - 22 * mm, 11 * mm, f"Página {doc.page}")
    canvas.restoreState()


def build_story() -> list:
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "BodyEDY", parent=styles["BodyText"], fontName="SegoeUI", fontSize=9.5,
        leading=14, alignment=TA_JUSTIFY, textColor=colors.HexColor("#253247"),
        spaceAfter=7,
    )
    h1 = ParagraphStyle(
        "H1EDY", parent=styles["Heading1"], fontName="SegoeUI-Bold", fontSize=18,
        leading=22, textColor=colors.HexColor("#0D5670"), spaceBefore=11, spaceAfter=7,
    )
    h2 = ParagraphStyle(
        "H2EDY", parent=styles["Heading2"], fontName="SegoeUI-Bold", fontSize=13,
        leading=17, textColor=colors.HexColor("#1A354C"), spaceBefore=9, spaceAfter=5,
    )
    bullet = ParagraphStyle(
        "BulletEDY", parent=body, leftIndent=12, firstLineIndent=-7, bulletIndent=3,
        spaceAfter=4,
    )
    cover_title = ParagraphStyle(
        "CoverTitle", fontName="SegoeUI-Bold", fontSize=28, leading=34,
        alignment=TA_CENTER, textColor=colors.HexColor("#0C506B"), spaceAfter=8,
    )
    cover_sub = ParagraphStyle(
        "CoverSub", fontName="SegoeUI", fontSize=13, leading=19,
        alignment=TA_CENTER, textColor=colors.HexColor("#53677D"),
    )

    story: list = [Spacer(1, 34 * mm)]
    story.append(Paragraph("EDY SOC Analytics", cover_title))
    story.append(Paragraph("Camada analítica profissional para operações de segurança", cover_sub))
    story.append(Spacer(1, 10 * mm))
    cover = ROOT / "screenshots" / "desktop-final" / "1. Command Center.png"
    story.append(Image(str(cover), width=166 * mm, height=102 * mm))
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("Edmilson Gomes", cover_sub))
    story.append(Paragraph("Power BI • Engenharia de Dados • Blue Team", cover_sub))
    story.append(Paragraph("24 de agosto de 2026", cover_sub))
    story.append(PageBreak())

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            story.append(Paragraph(escape(" ".join(paragraph)), body))
            paragraph.clear()

    for line in lines:
        value = line.strip()
        if not value:
            flush()
            continue
        if value.startswith("# "):
            continue
        if value.startswith("## "):
            flush()
            story.append(Paragraph(escape(value[3:]), h1))
        elif value.startswith("### "):
            flush()
            story.append(Paragraph(escape(value[4:]), h2))
        elif value.startswith("- "):
            flush()
            story.append(Paragraph("• " + escape(value[2:]), bullet))
        elif value.startswith("**Autor:") or value.startswith("**Data:") or value.startswith("**Área:"):
            flush()
            story.append(Paragraph(escape(value.replace("  ", "")), body))
        else:
            paragraph.append(value)
    flush()

    story.append(PageBreak())
    story.append(Paragraph("Anexo visual", h1))
    story.append(Paragraph("Resumo das dez páginas renderizadas no Power BI Desktop.", body))
    contact = ROOT / "screenshots" / "desktop-contact-sheet-final.png"
    story.append(Image(str(contact), width=122 * mm, height=205 * mm))
    return story


def main() -> None:
    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=22 * mm, leftMargin=22 * mm,
        topMargin=22 * mm, bottomMargin=18 * mm,
        title="EDY SOC Analytics - Relatório acadêmico",
        author="Edmilson Gomes",
        subject="Power BI, SOC e Engenharia de Dados",
    )
    doc.build(build_story(), onFirstPage=header_footer, onLaterPages=header_footer)
    print(OUTPUT)


if __name__ == "__main__":
    main()
