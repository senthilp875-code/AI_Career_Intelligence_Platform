"""
=========================================
AI Career Intelligence Platform
Career Roadmap Engine
Version 1.0
=========================================
"""

CAREER_ROADMAP = {

    "Data Analyst": {

        "skills": [
            "Python",
            "SQL",
            "Excel",
            "Power BI",
            "Tableau",
            "Statistics",
            "Data Visualization"
        ],

        "projects": [
            "Sales Dashboard",
            "HR Analytics Dashboard",
            "COVID-19 Data Analysis"
        ],

        "certifications": [
            "Google Data Analytics",
            "Microsoft Power BI",
            "IBM Data Analyst"
        ],

        "tips": [
            "Practice SQL daily.",
            "Build at least 3 dashboard projects.",
            "Upload projects to GitHub.",
            "Create a strong LinkedIn profile."
        ]
    },

    "Data Scientist": {

        "skills": [
            "Python",
            "Machine Learning",
            "Deep Learning",
            "Pandas",
            "NumPy",
            "TensorFlow",
            "Statistics"
        ],

        "projects": [
            "House Price Prediction",
            "Customer Churn Prediction",
            "Image Classification"
        ],

        "certifications": [
            "IBM Data Science",
            "Google Advanced Data Analytics"
        ],

        "tips": [
            "Master Machine Learning.",
            "Participate in Kaggle competitions.",
            "Build end-to-end AI projects."
        ]
    },

    "Python Developer": {

        "skills": [
            "Python",
            "Flask",
            "Django",
            "SQL",
            "REST API",
            "Git"
        ],

        "projects": [
            "Student Management System",
            "E-Commerce Website",
            "Blog Application"
        ],

        "certifications": [
            "Python Institute",
            "Meta Backend Developer"
        ],

        "tips": [
            "Learn API development.",
            "Use Git and GitHub daily.",
            "Deploy projects online."
        ]
    }

}


def get_career_roadmap(job_role):

    return CAREER_ROADMAP.get(
        job_role,
        {
            "skills": [],
            "projects": [],
            "certifications": [],
            "tips": []
        }
    )