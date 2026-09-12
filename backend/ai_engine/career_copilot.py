"""
==========================================
TalentIQ AI
Career Copilot Engine
Version 7.0 Enterprise
==========================================
"""


def generate_career_advice(analysis):

    advice = []

    # ==========================================
    # Resume Score
    # ==========================================

    if analysis["resume_score"] < 70:

        advice.append(
            "Improve your resume by adding more projects and measurable achievements."
        )

    else:

        advice.append(
            "Your resume has a strong foundation. Continue updating it with recent work."
        )

    # ==========================================
    # ATS Score
    # ==========================================

    if analysis["ats_score"] < 80:

        advice.append(
            "Increase ATS compatibility by using keywords from your target job descriptions."
        )

    else:

        advice.append(
            "Your resume is ATS-friendly."
        )

    # ==========================================
    # Missing Skills
    # ==========================================

    missing = analysis["skill_gap"]["missing_skills"]

    if missing:

        advice.append(

            "Focus on learning: " +

            ", ".join(missing)

        )

    # ==========================================
    # Career Roadmap
    # ==========================================

    advice.append(

        f"Follow the {analysis['predicted_job']} roadmap to improve your career opportunities."

    )

    # ==========================================
    # Final Motivation
    # ==========================================

    advice.append(

        "Stay consistent. Build projects, practice coding daily, and keep improving your portfolio."

    )

    return advice