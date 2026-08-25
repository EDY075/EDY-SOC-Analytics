"""Render the academic report as a polished, verifiable PDF."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, LongTable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, TableStyle

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "RELATORIO_ACADEMICO.md"
OUTPUT = ROOT / "output" / "pdf" / "RELATORIO_ACADEMICO.pdf"
FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"


def register_fonts() -> None:
    global FONT_REGULAR, FONT_BOLD
    candidates = [
        (
            Path(r"C:\Windows\Fonts\segoeui.ttf"),
            Path(r"C:\Windows\Fonts\segoeuib.ttf"),
            Path(r"C:\Windows\Fonts\segoeuii.ttf"),
            Path(r"C:\Windows\Fonts\segoeuiz.ttf"),
            "SegoeUI", "SegoeUI-Bold", "SegoeUI-Italic", "SegoeUI-BoldItalic",
        ),
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
            "DejaVu", "DejaVu-Bold", "DejaVu-Italic", "DejaVu-BoldItalic",
        ),
    ]
    for regular, bold, italic, bold_italic, regular_name, bold_name, italic_name, bold_italic_name in candidates:
        if all(path.exists() for path in (regular, bold, italic, bold_italic)):
            pdfmetrics.registerFont(TTFont(regular_name, str(regular)))
            pdfmetrics.registerFont(TTFont(bold_name, str(bold)))
            pdfmetrics.registerFont(TTFont(italic_name, str(italic)))
            pdfmetrics.registerFont(TTFont(bold_italic_name, str(bold_italic)))
            pdfmetrics.registerFontFamily(
                regular_name,
                normal=regular_name,
                bold=bold_name,
                italic=italic_name,
                boldItalic=bold_italic_name,
            )
            FONT_REGULAR, FONT_BOLD = regular_name, bold_name
            return


def escape(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    return text


def header_footer(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#39C6E6"))
    canvas.setLineWidth(0.8)
    canvas.line(22 * mm, height - 16 * mm, width - 22 * mm, height - 16 * mm)
    canvas.setFont(FONT_REGULAR, 8)
    canvas.setFillColor(colors.HexColor("#566579"))
    canvas.drawString(22 * mm, 11 * mm, "EDY SOC Analytics | Edmilson Gomes")
    canvas.drawRightString(width - 22 * mm, 11 * mm, f"Página {doc.page}")
    canvas.restoreState()


def build_story() -> list:
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "BodyEDY", parent=styles["BodyText"], fontName=FONT_REGULAR, fontSize=9.25,
        leading=14, alignment=TA_JUSTIFY, textColor=colors.HexColor("#253247"),
        spaceAfter=7,
    )
    h1 = ParagraphStyle(
        "H1EDY", parent=styles["Heading1"], fontName=FONT_BOLD, fontSize=17,
        leading=21, textColor=colors.HexColor("#0D5670"), spaceBefore=11, spaceAfter=7,
        keepWithNext=True,
    )
    h2 = ParagraphStyle(
        "H2EDY", parent=styles["Heading2"], fontName=FONT_BOLD, fontSize=12.5,
        leading=16, textColor=colors.HexColor("#1A354C"), spaceBefore=9, spaceAfter=5,
        keepWithNext=True,
    )
    bullet = ParagraphStyle(
        "BulletEDY", parent=body, leftIndent=12, firstLineIndent=-7, bulletIndent=3,
        spaceAfter=4,
    )
    reference_body = ParagraphStyle(
        "ReferenceEDY", parent=body, fontSize=8.5, leading=12,
        alignment=TA_LEFT, leftIndent=8, firstLineIndent=-8, spaceAfter=7,
    )
    cover_title = ParagraphStyle(
        "CoverTitle", fontName=FONT_BOLD, fontSize=28, leading=34,
        alignment=TA_CENTER, textColor=colors.HexColor("#0C506B"), spaceAfter=8,
    )
    cover_sub = ParagraphStyle(
        "CoverSub", fontName=FONT_REGULAR, fontSize=13, leading=19,
        alignment=TA_CENTER, textColor=colors.HexColor("#53677D"),
    )
    table_header = ParagraphStyle(
        "TableHeader", parent=body, fontName=FONT_BOLD, fontSize=8.2,
        leading=10, alignment=TA_LEFT, textColor=colors.white, spaceAfter=0,
    )
    table_cell = ParagraphStyle(
        "TableCell", parent=body, fontSize=7.8, leading=10,
        alignment=TA_LEFT, spaceAfter=0,
    )

    story: list = [Spacer(1, 34 * mm)]
    story.append(Paragraph("EDY SOC Analytics", cover_title))
    story.append(Paragraph("Camada analítica profissional para operações de segurança", cover_sub))
    story.append(Spacer(1, 10 * mm))
    cover = ROOT / "docs" / "assets" / "edy-soc-analytics-hero.png"
    story.append(Image(str(cover), width=166 * mm, height=93.5 * mm))
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("Edmilson Gomes", cover_sub))
    story.append(Paragraph("Power BI • Engenharia de Dados • Blue Team", cover_sub))
    story.append(Paragraph("25 de agosto de 2026", cover_sub))
    story.append(PageBreak())

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    paragraph: list[str] = []
    in_references = False

    def flush() -> None:
        if paragraph:
            story.append(Paragraph(escape(" ".join(paragraph)), reference_body if in_references else body))
            paragraph.clear()

    def add_image(relative: str, alt_text: str) -> None:
        path = (SOURCE.parent / relative).resolve()
        if not path.is_file():
            story.append(Paragraph(f"[Imagem ausente: {escape(alt_text)}]", body))
            return
        image = Image(str(path))
        image._restrictSize(166 * mm, 108 * mm)
        story.extend([Spacer(1, 2 * mm), image, Spacer(1, 4 * mm)])

    def add_table(rows: list[list[str]]) -> None:
        if len(rows) < 2:
            return
        cleaned = [rows[0]] + rows[2:]
        cells = []
        for row_index, row in enumerate(cleaned):
            style = table_header if row_index == 0 else table_cell
            cells.append([Paragraph(escape(cell), style) for cell in row])
        available = 166 * mm
        widths = [available / len(cells[0])] * len(cells[0])
        table = LongTable(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D5670")),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F3F6FA")),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B7C3D3")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.extend([table, Spacer(1, 3 * mm)])

    index = 0
    while index < len(lines):
        value = lines[index].strip()
        if not value:
            flush()
            index += 1
            continue
        if value.startswith("# "):
            index += 1
            continue
        image_match = re.fullmatch(r"!\[([^]]+)]\(([^)]+)\)", value)
        if image_match:
            flush()
            add_image(image_match.group(2), image_match.group(1))
            index += 1
            continue
        if value.startswith("|"):
            flush()
            rows: list[list[str]] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")])
                index += 1
            add_table(rows)
            continue
        if value.startswith("## "):
            flush()
            in_references = value[3:].strip().casefold() == "referências"
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
        index += 1
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
