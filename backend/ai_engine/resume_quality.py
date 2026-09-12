import re


def analyze_resume_quality(resume_text):

    report = {}

    text = resume_text.lower()

    words = len(resume_text.split())

    # ---------------- Resume Length ----------------
    if words >= 400:
        report["length"] = "Excellent"
    elif words >= 250:
        report["length"] = "Good"
    elif words >= 150:
        report["length"] = "Average"
    else:
        report["length"] = "Poor"

    # ---------------- Contact ----------------
    report["email"] = bool(
        re.search(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            resume_text
        )
    )

    report["phone"] = bool(
        re.search(
            r"\b\d{10}\b",
            resume_text
        )
    )

    # ---------------- Important Sections ----------------
    sections = [
        "education",
        "skills",
        "project",
        "experience",
        "internship",
        "certification",
        "achievement"
    ]

    section_report = {}

    for section in sections:
        section_report[section] = section in text

    report["sections"] = section_report

    # ---------------- Professional Links ----------------
    report["linkedin"] = "linkedin" in text
    report["github"] = "github" in text

    # ---------------- Word Count ----------------
    report["word_count"] = words

    return report