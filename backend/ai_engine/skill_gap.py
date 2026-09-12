# ==========================================
# AI Career Intelligence Platform
# Skill Gap Analyzer
# Version 1.0
# ==========================================

JOB_SKILLS = {

    "Data Analyst": [
        "Python",
        "SQL",
        "Excel",
        "Power BI",
        "Tableau",
        "Statistics",
        "Data Analysis",
        "Communication"
    ],

    "Data Scientist": [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "Statistics",
        "Pandas",
        "NumPy",
        "TensorFlow",
        "Scikit-learn",
        "SQL"
    ],

    "Machine Learning Engineer": [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "TensorFlow",
        "PyTorch",
        "Docker",
        "Git",
        "AWS"
    ],

    "Python Developer": [
        "Python",
        "Flask",
        "Django",
        "SQL",
        "Git",
        "REST API"
    ],

    "Frontend Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Git"
    ]
}


def analyze_skill_gap(predicted_job, detected_skills):

    required_skills = JOB_SKILLS.get(predicted_job, [])

    detected = set(detected_skills)

    missing = []

    matched = []

    for skill in required_skills:

        if skill in detected:
            matched.append(skill)
        else:
            missing.append(skill)

    if len(required_skills) == 0:
        match_percentage = 0
    else:
        match_percentage = round(
            (len(matched) / len(required_skills)) * 100
        )

    return {

        "required_skills": required_skills,

        "matched_skills": matched,

        "missing_skills": missing,

        "match_percentage": match_percentage
    }