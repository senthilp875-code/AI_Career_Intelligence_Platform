import re

# Skill Database with aliases
SKILL_DATABASE = {

    "Python": ["python"],
    "Java": ["java"],
    "C++": ["c++"],
    "C#": ["c#"],

    "HTML": ["html"],
    "CSS": ["css"],
    "JavaScript": ["javascript", "js"],

    "React": ["react", "reactjs"],
    "Angular": ["angular"],
    "Vue": ["vue", "vuejs"],

    "Flask": ["flask"],
    "Django": ["django"],
    "FastAPI": ["fastapi"],

    "SQL": ["sql"],
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "SQLite": ["sqlite"],
    "MongoDB": ["mongodb"],
    "Oracle": ["oracle"],

    "Excel": [
        "excel",
        "ms excel",
        "microsoft excel"
    ],

    "Google Sheets": [
        "google sheets",
        "googlesheets"
    ],

    "Power BI": [
        "power bi",
        "powerbi"
    ],

    "Tableau": ["tableau"],
    "Looker": ["looker"],

    "Data Analysis": [
        "data analysis",
        "data analytics"
    ],

    "Machine Learning": [
        "machine learning",
        "ml"
    ],

    "Artificial Intelligence": [
        "artificial intelligence",
        "ai"
    ],

    "Deep Learning": [
        "deep learning"
    ],

    "Data Science": [
        "data science"
    ],

    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Matplotlib": ["matplotlib"],
    "Seaborn": ["seaborn"],
    "Scikit-learn": [
        "scikit-learn",
        "sklearn"
    ],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],

    "Git": ["git"],
    "GitHub": ["github"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes"],

    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "Google Cloud": [
        "google cloud",
        "gcp"
    ],

    "Statistics": [
        "statistics",
        "statistical"
    ],

    "Probability": ["probability"],
    "Linear Algebra": [
        "linear algebra"
    ],

    "ETL": ["etl"],
    "Data Cleaning": [
        "data cleaning"
    ],
    "Feature Engineering": [
        "feature engineering"
    ],

    "Business Intelligence": [
        "business intelligence",
        "bi"
    ],

    "Data Mining": [
        "data mining"
    ],

    "Linux": ["linux"],
    "Windows": ["windows"],

    "REST API": [
        "rest api",
        "restful api"
    ],

    "JSON": ["json"],
    "XML": ["xml"],

    "Microsoft Word": [
        "ms word",
        "microsoft word",
        "word"
    ],

    "Communication": [
        "communication",
        "communication skills"
    ],

    "Leadership": [
        "leadership",
        "leader"
    ],

    "Problem Solving": [
        "problem solving",
        "problem-solving"
    ],

    "Critical Thinking": [
        "critical thinking"
    ],

    "Teamwork": [
        "teamwork",
        "team collaboration",
        "collaboration"
    ],

    "Adaptability": [
        "adaptability",
        "adaptable"
    ],

    "Time Management": [
        "time management"
    ]
}


def detect_skills(resume_text):

    detected = []

    text = resume_text.lower()

    for skill, keywords in SKILL_DATABASE.items():

        for keyword in keywords:

            pattern = r"\b" + re.escape(keyword.lower()) + r"\b"

            if re.search(pattern, text):
                detected.append(skill)
                break

    return sorted(detected)


def calculate_score(resume_text, detected_skills):

    score = 0

    # Skill Score (Maximum 70)
    skill_score = min(len(detected_skills) * 7, 70)
    score += skill_score

    # Resume Length Score (Maximum 20)
    words = len(resume_text.split())

    if words >= 400:
        score += 20
    elif words >= 250:
        score += 15
    elif words >= 150:
        score += 10
    elif words >= 80:
        score += 5

    # Education Bonus (Maximum 10)
    education_keywords = [
        "b.sc",
        "b.e",
        "b.tech",
        "m.sc",
        "m.tech",
        "phd",
        "degree",
        "computer science",
        "data analytics"
    ]

    text = resume_text.lower()

    for keyword in education_keywords:
        if keyword in text:
            score += 2

    score = min(score, 100)

    return score