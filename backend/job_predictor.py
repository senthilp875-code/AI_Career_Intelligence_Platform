"""
=========================================
TalentIQ AI
Career Prediction Engine
Version 3.0
=========================================
"""

JOB_DATABASE = {

    "Data Analyst": {
        "Python": 20,
        "SQL": 25,
        "Excel": 20,
        "Power BI": 20,
        "Tableau": 20,
        "Statistics": 15,
        "Data Analysis": 25
    },

    "Business Intelligence Analyst": {
        "Power BI": 30,
        "Tableau": 30,
        "Excel": 25,
        "SQL": 20
    },

    "Python Developer": {
        "Python": 30,
        "Flask": 20,
        "Django": 20,
        "REST API": 20,
        "Git": 15,
        "SQL": 15
    },

    "Machine Learning Engineer": {
        "Python": 25,
        "Machine Learning": 30,
        "Deep Learning": 25,
        "TensorFlow": 20,
        "PyTorch": 20,
        "Scikit-learn": 20
    },

    "Java Developer": {
        "Java": 35,
        "SQL": 15,
        "Git": 10
    },

    "Frontend Developer": {
        "HTML": 20,
        "CSS": 20,
        "JavaScript": 30,
        "React": 25
    },

    "Cloud Engineer": {
        "AWS": 30,
        "Azure": 25,
        "Docker": 20,
        "Kubernetes": 20
    }

}


def predict_job(skills):

    scores = {}

    detected = set(skills)

    for job, required in JOB_DATABASE.items():

        score = 0

        max_score = sum(required.values())

        for skill, weight in required.items():

            if skill in detected:
                score += weight

        percentage = round((score / max_score) * 100)

        scores[job] = percentage

    ranking = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return {
        "best_job": ranking[0][0],
        "best_score": ranking[0][1],
        "top3": ranking[:3]
    }