"""
=========================================
TalentIQ AI
Job Service — page-level helpers
=========================================
"""

from services.job_engine import (
    recommend_jobs,
    filter_jobs,
    get_filter_options,
    get_recommendation_stats,
    load_jobs,
    calculate_job_match
)


def get_job_recommendations(
    analysis,
    location=None,
    job_type=None,
    min_match=None,
    search=None,
    limit=20
):

    predicted_job = analysis.get("predicted_job", "")
    user_skills = analysis.get("skills", [])

    jobs = recommend_jobs(
        predicted_job,
        user_skills,
        limit=50,
        min_score=15
    )

    jobs = filter_jobs(
        jobs,
        location=location,
        job_type=job_type,
        min_match=min_match,
        search=search
    )

    filters = get_filter_options(load_jobs())
    stats = get_recommendation_stats(jobs, predicted_job)

    return {
        "jobs": jobs[:limit],
        "filters": filters,
        "stats": stats,
        "predicted_job": predicted_job,
        "user_skills": user_skills
    }
