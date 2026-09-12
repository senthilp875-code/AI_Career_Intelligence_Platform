"""
=========================================
TalentIQ AI
Job Recommendation Engine
Real skill-based matching against job database
=========================================
"""

import json
import os
import copy


# Role keyword mapping for fuzzy title/category matching

ROLE_KEYWORDS = {

    "Data Analyst": [
        "data analyst", "analytics", "sql developer",
        "tableau", "business analyst"
    ],

    "Business Intelligence Analyst": [
        "business intelligence", "bi developer", "bi analyst",
        "power bi", "tableau developer"
    ],

    "Python Developer": [
        "python", "backend", "django", "flask",
        "fastapi", "software engineer", "full stack",
        "qa automation"
    ],

    "Machine Learning Engineer": [
        "machine learning", "ml ", "ai engineer",
        "data scientist", "nlp", "computer vision",
        "deep learning"
    ],

    "Java Developer": [
        "java", "spring boot", "android"
    ],

    "Frontend Developer": [
        "frontend", "react", "vue", "ui developer",
        "angular", "react native"
    ],

    "Cloud Engineer": [
        "cloud", "devops", "aws", "azure",
        "sre", "site reliability", "data engineer",
        "mlops"
    ]

}


def _get_database_path():

    return os.path.join(
        os.path.dirname(__file__),
        "..",
        "resources",
        "jobs_database.json"
    )


def load_jobs():

    json_path = _get_database_path()

    try:

        with open(json_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError) as error:
        print("Job Database Error:", error)
        return []


def _normalize(text):

    return text.lower().strip()


def _skill_matches(user_skill, job_skill):

    user = _normalize(user_skill)
    job = _normalize(job_skill)

    if user == job:
        return True

    if user in job or job in user:
        return True

    aliases = {
        "js": "javascript",
        "ml": "machine learning",
        "ai": "artificial intelligence",
        "postgres": "postgresql",
    }

    for alias, full in aliases.items():
        if user == alias and full in job:
            return True
        if job == alias and full in user:
            return True

    return False


def _calculate_role_score(job, predicted_job):

    category = job.get("category", "")
    title = job.get("job_title", "")

    if category == predicted_job:
        return 35

    if _normalize(predicted_job) in _normalize(title):
        return 30

    keywords = ROLE_KEYWORDS.get(predicted_job, [])

    for keyword in keywords:
        if keyword in _normalize(title):
            return 22

    if category and _normalize(category) in _normalize(predicted_job):
        return 18

    return 0


def _calculate_skill_score(job_skills, user_skills):

    if not job_skills:
        return 0, [], []

    matched = []
    missing = []

    for job_skill in job_skills:

        found = False

        for user_skill in user_skills:

            if _skill_matches(user_skill, job_skill):
                matched.append(job_skill)
                found = True
                break

        if not found:
            missing.append(job_skill)

    ratio = len(matched) / len(job_skills)
    score = round(ratio * 50)

    return score, matched, missing


def _calculate_title_score(job, predicted_job):

    title = _normalize(job.get("job_title", ""))
    predicted = _normalize(predicted_job)

    if predicted in title:
        return 15

    words = predicted.split()

    hits = sum(1 for word in words if len(word) > 3 and word in title)

    if hits >= 2:
        return 12

    if hits == 1:
        return 8

    return 0


def calculate_job_match(job, predicted_job, user_skills):

    job_copy = copy.deepcopy(job)

    role_score = _calculate_role_score(job_copy, predicted_job)

    skill_score, matched, missing = _calculate_skill_score(
        job_copy.get("skills", []),
        user_skills
    )

    title_score = _calculate_title_score(job_copy, predicted_job)

    total = min(100, role_score + skill_score + title_score)

    # Minimum relevance floor — hide very poor matches on dedicated page
    if total < 15 and role_score == 0 and skill_score == 0:
        total = max(total, 5)

    job_copy["match_score"] = total
    job_copy["matched_skills"] = matched
    job_copy["missing_skills"] = missing
    job_copy["skill_match_pct"] = (
        round((len(matched) / len(job_copy["skills"])) * 100)
        if job_copy.get("skills") else 0
    )

    return job_copy


def recommend_jobs(
    predicted_job,
    user_skills,
    limit=10,
    min_score=20
):

    jobs = load_jobs()
    recommendations = []

    for job in jobs:

        scored = calculate_job_match(
            job,
            predicted_job,
            user_skills
        )

        if scored["match_score"] >= min_score:
            recommendations.append(scored)

    recommendations.sort(
        key=lambda item: item["match_score"],
        reverse=True
    )

    return recommendations[:limit]


def filter_jobs(
    jobs,
    location=None,
    job_type=None,
    min_match=None,
    search=None
):

    filtered = jobs

    if location and location != "all":
        filtered = [
            job for job in filtered
            if location.lower() in job.get("location", "").lower()
        ]

    if job_type and job_type != "all":
        filtered = [
            job for job in filtered
            if job.get("job_type", "").lower() == job_type.lower()
        ]

    if min_match:
        try:
            threshold = int(min_match)
            filtered = [
                job for job in filtered
                if job.get("match_score", 0) >= threshold
            ]
        except ValueError:
            pass

    if search:
        query = search.lower().strip()
        filtered = [
            job for job in filtered
            if (
                query in job.get("job_title", "").lower()
                or query in job.get("company", "").lower()
                or query in job.get("description", "").lower()
                or any(
                    query in skill.lower()
                    for skill in job.get("skills", [])
                )
            )
        ]

    return filtered


def get_filter_options(jobs):

    locations = sorted({
        job.get("location", "")
        for job in jobs
        if job.get("location")
    })

    job_types = sorted({
        job.get("job_type", "")
        for job in jobs
        if job.get("job_type")
    })

    return {
        "locations": locations,
        "job_types": job_types
    }


def get_recommendation_stats(jobs, predicted_job):

    if not jobs:
        return {
            "total_jobs": 0,
            "avg_match": 0,
            "best_match": 0,
            "top_company": "N/A"
        }

    scores = [job.get("match_score", 0) for job in jobs]

    return {
        "total_jobs": len(jobs),
        "avg_match": round(sum(scores) / len(scores), 1),
        "best_match": max(scores),
        "top_company": jobs[0].get("company", "N/A"),
        "predicted_role": predicted_job
    }


def format_for_analysis(jobs):

    """Compact format for resume analysis pipeline."""

    formatted = []

    for job in jobs[:5]:

        formatted.append({

            "title": job.get("job_title"),
            "company": job.get("company"),
            "match": job.get("match_score"),
            "salary": job.get("salary"),
            "location": job.get("location"),
            "growth": _growth_stars(job.get("match_score", 0))

        })

    return formatted


def _growth_stars(match_score):

    if match_score >= 90:
        return "★★★★★"

    if match_score >= 75:
        return "★★★★☆"

    if match_score >= 60:
        return "★★★☆☆"

    return "★★☆☆☆"
