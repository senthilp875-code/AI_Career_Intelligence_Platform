"""
==========================================
TalentIQ AI
Feedback Engine
Version 2.0
==========================================
"""


def generate_feedback(
    score,
    ats_score,
    quality_report,
    skill_gap,
    predicted_job
):

    feedback = {
        "strengths": [],
        "improvements": [],
        "recommendations": [],
        "priority_actions": []
    }

    # ==========================================
    # Resume Score
    # ==========================================

    if score >= 90:

        feedback["strengths"].append(
            "Outstanding resume quality."
        )

    elif score >= 75:

        feedback["strengths"].append(
            "Strong resume with good technical skills."
        )

    elif score >= 60:

        feedback["improvements"].append(
            "Resume is good but can be strengthened."
        )

    else:

        feedback["improvements"].append(
            "Resume needs major improvements."
        )

        feedback["priority_actions"].append(
            "Rewrite your resume using a professional format."
        )

    # ==========================================
    # ATS
    # ==========================================

    if ats_score >= 85:

        feedback["strengths"].append(
            "Excellent ATS compatibility."
        )

    elif ats_score >= 70:

        feedback["strengths"].append(
            "Good ATS optimization."
        )

    else:

        feedback["improvements"].append(
            "ATS score is below industry standards."
        )

        feedback["priority_actions"].append(
            "Add more job-specific keywords."
        )

    # ==========================================
    # Resume Quality
    # ==========================================

    if not quality_report["github"]:

        feedback["recommendations"].append(
            "Create a professional GitHub profile with real projects."
        )

    else:

        feedback["strengths"].append(
            "GitHub profile detected."
        )

    if not quality_report["linkedin"]:

        feedback["recommendations"].append(
            "Create or update your LinkedIn profile."
        )

    else:

        feedback["strengths"].append(
            "LinkedIn profile detected."
        )

    # ==========================================
    # Skill Gap
    # ==========================================

    missing = skill_gap.get("missing_skills", [])

    if missing:

        feedback["improvements"].append(
            f"{len(missing)} important skills are missing."
        )

        feedback["recommendations"].append(
            "Focus on learning: " + ", ".join(missing)
        )

        feedback["priority_actions"].append(
            "Complete projects using the missing technologies."
        )

    else:

        feedback["strengths"].append(
            "No major skill gaps detected."
        )

    # ==========================================
    # Career Guidance
    # ==========================================

    feedback["recommendations"].append(
        f"Best career match: {predicted_job}"
    )

    feedback["recommendations"].append(
        "Build 3-5 portfolio projects related to your target career."
    )

    feedback["recommendations"].append(
        "Earn at least one industry-recognized certification."
    )

    feedback["recommendations"].append(
        "Customize your resume for every job application."
    )

    # ==========================================
    # Final Verdict
    # ==========================================

    if score >= 85 and ats_score >= 85:

        feedback["overall"] = (
            "Excellent! Your resume is highly competitive."
        )

    elif score >= 70:

        feedback["overall"] = (
            "Good resume with room for improvement."
        )

    else:

        feedback["overall"] = (
            "Your resume needs significant improvements before applying."
        )

    return feedback