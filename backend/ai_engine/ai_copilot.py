"""
==========================================
TalentIQ AI
AI Resume Copilot
Version 1.0
==========================================
"""


def generate_ai_summary(analysis):

    score = analysis["resume_score"]
    ats = analysis["ats_score"]
    job = analysis["predicted_job"]

    summary = []

    # Resume Quality

    if score >= 85:

        summary.append(
            "Your resume is professionally written with a strong technical profile."
        )

    elif score >= 70:

        summary.append(
            "Your resume is good, but a few improvements can make it much stronger."
        )

    else:

        summary.append(
            "Your resume needs significant improvements before applying for competitive jobs."
        )

    # ATS

    if ats >= 80:

        summary.append(
            "Your resume is ATS-friendly and should perform well in most recruitment systems."
        )

    else:

        summary.append(
            "Improve ATS keywords to increase interview chances."
        )

    # Career

    summary.append(

        f"Our AI predicts that your strongest career path is {job}."

    )

    summary.append(

        "Continue building projects, improving your portfolio, and earning certifications."

    )

    return " ".join(summary)