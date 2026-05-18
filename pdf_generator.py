from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def gerar_pdf(texto):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "Relatório CredMed IA",
            styles["Title"]
        )
    )

    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            texto.replace("\n", "<br/>"),
            styles["BodyText"]
        )
    )

    doc.build(story)

    pdf_bytes = buffer.getvalue()

    buffer.close()

    return pdf_bytes