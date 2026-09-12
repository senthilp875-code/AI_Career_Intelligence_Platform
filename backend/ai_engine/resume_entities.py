import re


def extract_entities(resume_text):

    text = resume_text

    entities = {

        "email": "",

        "phone": "",

        "linkedin": "",

        "github": "",

        "education": [],

        "certifications": [],

        "projects": [],

        "internships": []

    }

    # Email
    email = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    if email:
        entities["email"] = email[0]

    # Phone
    phone = re.findall(
        r"(?:\+91[- ]?)?[6-9]\d{9}",
        text
    )

    if phone:
        entities["phone"] = phone[0]

    # LinkedIn
    linkedin = re.findall(
        r"https?://(?:www\.)?linkedin\.com/\S+",
        text,
        re.IGNORECASE
    )

    if linkedin:
        entities["linkedin"] = linkedin[0]

    # GitHub
    github = re.findall(
        r"https?://(?:www\.)?github\.com/\S+",
        text,
        re.IGNORECASE
    )

    if github:
        entities["github"] = github[0]

    return entities