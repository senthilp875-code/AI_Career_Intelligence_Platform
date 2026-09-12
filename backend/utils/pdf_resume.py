from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def create_pdf(resume, output_path):

    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(output_path)

    story = []

    story.append(
        Paragraph(
            f"<b>{resume['name']}</b>",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            resume["email"],
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            resume["phone"],
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            "<br/><b>Professional Summary</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            resume["summary"],
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            "<br/><b>Skills</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            ", ".join(resume["skills"]),
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            "<br/><b>Projects</b>",
            styles["Heading2"]
        )
    )

    for project in resume["projects"]:

        story.append(
            Paragraph(
                "• " + project,
                styles["Normal"]
            )
        )

    story.append(
        Paragraph(
            "<br/><b>Education</b>",
            styles["Heading2"]
        )
    )

    for edu in resume["education"]:

        story.append(
            Paragraph(
                "• " + edu,
                styles["Normal"]
            )
        )

    story.append(
        Paragraph(
            "<br/><b>Certifications</b>",
            styles["Heading2"]
        )
    )

    for cert in resume["certifications"]:

        story.append(
            Paragraph(
                "• " + cert,
                styles["Normal"]
            )
        )

    doc.build(story)