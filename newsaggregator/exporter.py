# Export report in PDF con ReportLab

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

OUTPUT_DIR = os.path.join("output")


def export_pdf(keyword, date, summary, articles):
    """
    Genera un PDF con i risultati di una ricerca.

    Args:
        keyword:  la keyword cercata
        date:     data della ricerca (YYYY-MM-DD)
        summary:  riassunto generato da Groq (può essere None)
        articles: lista di articoli trovati

    Returns:
        Il percorso del file PDF generato.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Il nome del file viene costruito dalla keyword e dalla data
    # Gli spazi nella keyword vengono sostituiti con underscore
    safe_keyword = keyword.replace(" ", "_")
    filename = f"{safe_keyword}_{date}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    # Stili base forniti da ReportLab, li usiamo come punto di partenza
    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=6,
    )
    style_meta = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=16,
    )
    style_section = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#16213e"),
        spaceBefore=16,
        spaceAfter=6,
    )
    style_body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=6,
    )
    style_article_title = ParagraphStyle(
        "ArticleTitle",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica-Bold",
        spaceAfter=2,
    )
    style_article_meta = ParagraphStyle(
        "ArticleMeta",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=8,
    )

    # elements è la lista di blocchi che compongono il PDF,
    # ReportLab li dispone in sequenza dall'alto verso il basso
    elements = []

    elements.append(Paragraph(f"Report: {keyword}", style_title))
    elements.append(Paragraph(
        f"Data ricerca: {date} &nbsp;&nbsp;|&nbsp;&nbsp; Keyword: <b>{keyword}</b>",
        style_meta
    ))

    if summary:
        elements.append(Paragraph("Riassunto", style_section))
        elements.append(Paragraph(summary, style_body))

    elements.append(Paragraph(f"Articoli trovati ({len(articles)})", style_section))

    for article in articles:
        elements.append(Paragraph(article["title"], style_article_title))
        elements.append(Paragraph(
            f"{article['feed_name']} &nbsp;|&nbsp; {article['published']} &nbsp;|&nbsp; "
            f"<a href='{article['url']}'><font color='#0066cc'>{article['url'][:60]}...</font></a>",
            style_article_meta
        ))

    doc.build(elements)
    print(f"PDF generato: {filepath}")
    return filepath