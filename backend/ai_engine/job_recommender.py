"""
==========================================
TalentIQ AI
Job Recommendation Engine
Version 6.5 Enterprise
==========================================
"""


def recommend_jobs(predicted_job):

    job = predicted_job.lower()

    recommendations = []

    if "python" in job:

        recommendations = [

            {
                "title": "Python Developer",
                "match": 95,
                "salary": "₹6 - ₹12 LPA",
                "growth": "★★★★★"
            },

            {
                "title": "Backend Developer",
                "match": 91,
                "salary": "₹7 - ₹14 LPA",
                "growth": "★★★★☆"
            },

            {
                "title": "Automation Engineer",
                "match": 88,
                "salary": "₹6 - ₹10 LPA",
                "growth": "★★★★☆"
            }

        ]

    elif "data" in job:

        recommendations = [

            {
                "title": "Data Scientist",
                "match": 94,
                "salary": "₹8 - ₹18 LPA",
                "growth": "★★★★★"
            },

            {
                "title": "Data Analyst",
                "match": 90,
                "salary": "₹6 - ₹12 LPA",
                "growth": "★★★★☆"
            },

            {
                "title": "Business Analyst",
                "match": 86,
                "salary": "₹7 - ₹13 LPA",
                "growth": "★★★★☆"
            }

        ]

    elif "ai" in job or "machine" in job:

        recommendations = [

            {
                "title": "AI Engineer",
                "match": 96,
                "salary": "₹10 - ₹22 LPA",
                "growth": "★★★★★"
            },

            {
                "title": "Machine Learning Engineer",
                "match": 93,
                "salary": "₹12 - ₹25 LPA",
                "growth": "★★★★★"
            },

            {
                "title": "Computer Vision Engineer",
                "match": 87,
                "salary": "₹10 - ₹20 LPA",
                "growth": "★★★★☆"
            }

        ]

    else:

        recommendations = [

            {
                "title": predicted_job,
                "match": 85,
                "salary": "₹5 - ₹10 LPA",
                "growth": "★★★★☆"
            }

        ]

    return recommendations