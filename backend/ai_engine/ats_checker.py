import re


def calculate_ats_score(resume_text):

    score = 0

    text = resume_text.lower()

    # Contact Information
    if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text):
        score += 10

    if re.search(r"\b\d{10}\b", text):
        score += 10

    # Resume Sections
    sections = [
        "education",
        "skills",
        "project",
        "experience",
        "internship",
        "certification"
    ]

    for section in sections:
        if section in text:
            score += 8

    # Resume Length
    words = len(text.split())

    if words >= 300:
        score += 15
    elif words >= 200:
        score += 10
    elif words >= 100:
        score += 5

    # LinkedIn
    if "linkedin" in text:
        score += 8

    # GitHub
    if "github" in text:
        score += 8

    # Limit maximum score
    return min(score, 100)