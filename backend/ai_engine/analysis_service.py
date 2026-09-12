"""
=========================================
TalentIQ AI
Analysis Service
Version 5.0 Premium
=========================================
"""

# =========================================
# Resume Analysis Modules
# =========================================

from skill_analyzer import detect_skills, calculate_score
from job_predictor import predict_job

from ai_engine.ats_checker import calculate_ats_score
from ai_engine.resume_quality import analyze_resume_quality
from ai_engine.skill_gap import analyze_skill_gap
from ai_engine.feedback_engine import generate_feedback
from ai_engine.career_roadmap import get_career_roadmap
from ai_engine.resume_entities import extract_entities
from ai_engine.ai_copilot import generate_ai_summary
from ai_engine.interview_generator import generate_interview_questions
from ai_engine.job_recommender import recommend_jobs


# =========================================
# Main Resume Analysis
# =========================================

def analyze_resume(resume_text):

    # =====================================
    # Resume Entity Extraction
    # =====================================

    entities = extract_entities(resume_text)

    # =====================================
    # Skill Detection
    # =====================================

    skills = detect_skills(resume_text)

    # =====================================
    # Resume Score
    # =====================================

    resume_score = calculate_score(
        resume_text,
        skills
    )

    # =====================================
    # ATS Score
    # =====================================

    ats_score = calculate_ats_score(
        resume_text
    )

    # =====================================
    # Resume Quality Report
    # =====================================

    quality = analyze_resume_quality(
        resume_text
    )

    # =====================================
    # AI Job Prediction
    # =====================================

    prediction = predict_job(
        skills
    )

    predicted_job = prediction["best_job"]

    job_match = prediction["best_score"]

    top_careers = prediction["top3"]

    # =====================================
    # Skill Gap Analysis
    # =====================================

    skill_gap = analyze_skill_gap(
        predicted_job,
        skills
    )

    # =====================================
    # Career Roadmap
    # =====================================

    career_roadmap = get_career_roadmap(
        predicted_job
    )

    # =====================================
    # AI Feedback
    # =====================================

    feedback = generate_feedback(
        resume_score,
        ats_score,
        quality,
        skill_gap,
        predicted_job
    )

    # =====================================
    # AI Resume Copilot
    # =====================================

    ai_summary = generate_ai_summary({

        "resume_score": resume_score,

        "ats_score": ats_score,

        "predicted_job": predicted_job

    })

    # =====================================
    # AI Interview Questions
    # =====================================

    interview_questions = generate_interview_questions(
        predicted_job
    )

    # =====================================
    # AI Job Recommendations
    # =====================================

    recommended_jobs = recommend_jobs(
        predicted_job
    )

    # =====================================
    # Resume Improvement
    # =====================================

    resume_strengths = []

    if resume_score >= 70:
        resume_strengths.append(
            "Your resume has a good overall score."
        )

    if ats_score >= 70:
        resume_strengths.append(
            "Your resume has good ATS compatibility."
        )

    if skills:
        resume_strengths.append(
            f"Your resume shows relevant technical skills for {predicted_job}."
        )

    if job_match >= 70:
        resume_strengths.append(
            "Your skills have a strong match with the predicted career."
        )

    if not resume_strengths:
        resume_strengths.append(
            "Your resume provides a good foundation that can be improved further."
        )

    # =====================================
    # Areas to Improve
    # =====================================

    resume_improvements = []

    if resume_score < 70:
        resume_improvements.append(
            "Improve your overall resume structure and content."
        )

    if ats_score < 70:
        resume_improvements.append(
            "Add relevant ATS keywords and improve section headings."
        )

    missing_skills = []

    if isinstance(skill_gap, dict):
        missing_skills = skill_gap.get(
            "missing_skills",
            []
        )

    if missing_skills:
        resume_improvements.append(
            "Add or develop the missing skills required for your target role."
        )

    resume_improvements.append(
        "Add measurable achievements and results to your project or work descriptions."
    )

    resume_improvements.append(
        "Use strong action verbs when describing your experience and projects."
    )

    # =====================================
    # Recommended Action Verbs
    # =====================================

    action_verbs = [
        "Developed",
        "Designed",
        "Implemented",
        "Analyzed",
        "Optimized",
        "Automated",
        "Created",
        "Built",
        "Improved",
        "Managed",
        "Led"
    ]

    # =====================================
    # Final Result
    # =====================================

    analysis = {

        # Candidate Information
        "entities": entities,

        # Skills
        "skills": skills,

        # Scores
        "resume_score": resume_score,

        "ats_score": ats_score,

        "job_match": job_match,

        # Career
        "predicted_job": predicted_job,

        "top_careers": top_careers,

        "career_roadmap": career_roadmap,

        # Analysis
        "quality": quality,

        "skill_gap": skill_gap,

        # Resume Improvement
        "resume_strengths": resume_strengths,

        "resume_improvements": resume_improvements,

        "action_verbs": action_verbs,

        # AI
        "feedback": feedback,

        "ai_summary": ai_summary,

        "interview_questions": interview_questions,

        "recommended_jobs": recommended_jobs
    }

    return analysis


# =========================================
# TalentIQ AI Chat Assistant
# =========================================

def generate_ai_reply(message, analysis):

    message = message.lower()

    # =====================================
    # Resume Review
    # =====================================

    if "resume" in message:

        return f"""
📄 Resume Review

Resume Score : {analysis['resume_score']}/100

Your resume is well structured.
I recommend improving project descriptions,
adding measurable achievements,
and including more ATS keywords.
"""

    # =====================================
    # ATS Score
    # =====================================

    elif "ats" in message:

        return f"""
📊 ATS Analysis

ATS Score : {analysis['ats_score']}/100

Improve keyword matching,
section headings,
and relevant technical skills
to increase your ATS score.
"""

    # =====================================
    # Skills
    # =====================================

    elif "skill" in message:

        skills = ", ".join(analysis["skills"])

        return f"""
🧠 Your Skills

{skills}

Continue strengthening these skills
and learn the missing technologies
for better opportunities.
"""

    # =====================================
    # Career Prediction
    # =====================================

    elif "career" in message or "job" in message:

        return f"""
💼 Career Prediction

Best Role :

{analysis['predicted_job']}

Job Match :

{analysis['job_match']}%

Keep building projects related
to this career path.
"""

    # =====================================
    # Career Roadmap
    # =====================================

    elif "roadmap" in message:

        roadmap = analysis["career_roadmap"]

        if isinstance(roadmap, list):
            roadmap = "\n".join(
                f"• {step}"
                for step in roadmap
            )

        return f"""
🚀 Career Roadmap

{roadmap}
"""

    # =====================================
    # Interview
    # =====================================

    elif "interview" in message:

        questions = analysis["interview_questions"]

        if isinstance(questions, list):
            questions = "\n".join(
                f"• {q}"
                for q in questions
            )

        return f"""
🎤 Interview Preparation

Practice these questions:

{questions}
"""

    # =====================================
    # Jobs
    # =====================================

    elif "recommend" in message or "jobs" in message:

        jobs = analysis["recommended_jobs"]

        if isinstance(jobs, list):
            jobs = "\n".join(
                f"• {job}"
                for job in jobs
            )

        return f"""
💼 Recommended Jobs

{jobs}
"""

    # =====================================
    # Default
    # =====================================

    else:

        return """
🤖 Hello!

I can help you with:

• Resume Review
• ATS Score
• Skill Analysis
• Career Prediction
• Career Roadmap
• Interview Preparation
• Job Recommendations

Ask me anything related to your career.
"""