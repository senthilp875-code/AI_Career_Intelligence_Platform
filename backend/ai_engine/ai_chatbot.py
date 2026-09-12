"""
=========================================
TalentIQ AI
Career Assistant v2.0
Context-aware chat using resume analysis
=========================================
"""


def _bullet_list(items, prefix="•"):

    if not items:
        return "None detected."

    return "\n".join(f"{prefix} {item}" for item in items)


def _format_jobs(jobs):

    if not jobs:
        return "No job recommendations available yet."

    lines = []

    for index, job in enumerate(jobs[:5], start=1):

        if isinstance(job, dict):

            title = job.get("title") or job.get("job_title", "Unknown Role")
            company = job.get("company", "")
            match = job.get("match") or job.get("match_score", "")
            salary = job.get("salary", "")

            line = f"{index}. {title}"

            if company:
                line += f" — {company}"

            if match:
                line += f" ({match}% match)"

            if salary:
                line += f"\n   Salary: {salary}"

            lines.append(line)

        else:
            lines.append(f"{index}. {job}")

    return "\n".join(lines)


def _format_roadmap(roadmap):

    if isinstance(roadmap, list):
        return _bullet_list(roadmap)

    if not isinstance(roadmap, dict):
        return "Roadmap data is not available for your predicted role."

    sections = []

    skills = roadmap.get("skills", [])
    if skills:
        sections.append(
            "Skills to Master:\n" + _bullet_list(skills)
        )

    projects = roadmap.get("projects", [])
    if projects:
        sections.append(
            "Recommended Projects:\n" + _bullet_list(projects)
        )

    certifications = roadmap.get("certifications", [])
    if certifications:
        sections.append(
            "Certifications:\n" + _bullet_list(certifications)
        )

    tips = roadmap.get("tips", [])
    if tips:
        sections.append(
            "Career Tips:\n" + _bullet_list(tips)
        )

    return "\n\n".join(sections) if sections else (
        "Complete skill-building projects and earn certifications "
        "for your target role."
    )


def _format_interview_questions(questions):

    if isinstance(questions, list):
        return _bullet_list(questions)

    if not isinstance(questions, dict):
        return (
            "Practice technical concepts, coding problems, "
            "and common HR questions daily."
        )

    sections = []

    technical = questions.get("technical", [])
    if technical:
        sections.append(
            "Technical Questions:\n" + _bullet_list(technical)
        )

    coding = questions.get("coding", [])
    if coding:
        sections.append(
            "Coding Questions:\n" + _bullet_list(coding)
        )

    hr = questions.get("hr", [])
    if hr:
        sections.append(
            "HR Questions:\n" + _bullet_list(hr)
        )

    return "\n\n".join(sections)


def _format_quality(quality):

    if not quality:
        return "Quality analysis is not available."

    lines = [
        f"Resume Length: {quality.get('length', 'N/A')}",
        f"Word Count: {quality.get('word_count', 0)}",
        f"Email: {'✓ Found' if quality.get('email') else '✗ Missing'}",
        f"Phone: {'✓ Found' if quality.get('phone') else '✗ Missing'}",
        f"LinkedIn: {'✓ Found' if quality.get('linkedin') else '✗ Missing'}",
        f"GitHub: {'✓ Found' if quality.get('github') else '✗ Missing'}",
    ]

    sections = quality.get("sections", {})
    if sections:
        section_lines = []
        for name, present in sections.items():
            status = "✓" if present else "✗"
            section_lines.append(
                f"{status} {name.title()}"
            )
        lines.append(
            "\nSections:\n" + _bullet_list(section_lines)
        )

    return "\n".join(lines)


def _handle_greeting(username):

    name = username or "there"

    return (
        f"Hello {name}! 👋\n\n"
        "I'm TalentIQ AI, your personal career mentor.\n\n"
        "I've analyzed your resume and I'm ready to help with:\n\n"
        "• Resume review & improvements\n"
        "• ATS score optimization\n"
        "• Skill analysis & gap detection\n"
        "• Career prediction & roadmap\n"
        "• Interview preparation\n"
        "• Job recommendations\n\n"
        "Ask me anything or use the quick prompts below!"
    )


def _handle_help():

    return (
        "Here's what I can help you with:\n\n"
        "📄 Resume — Review score, quality, and improvements\n"
        "📊 ATS — Compatibility score and optimization tips\n"
        "🧠 Skills — Detected skills and skill gap analysis\n"
        "💼 Career — Job prediction and top career matches\n"
        "🚀 Roadmap — Personalized learning path\n"
        "🎤 Interview — Technical, coding & HR questions\n"
        "💡 Jobs — Recommended roles based on your profile\n"
        "⭐ Feedback — Strengths, improvements & actions\n"
        "🔗 GitHub / LinkedIn — Profile optimization tips\n\n"
        "Try: \"Review my resume\" or \"Show my career roadmap\""
    )


def _handle_roadmap(analysis):

    predicted_job = analysis.get("predicted_job", "your target role")
    roadmap = analysis.get("career_roadmap", {})

    return (
        f"🚀 Career Roadmap for {predicted_job}\n\n"
        f"{_format_roadmap(roadmap)}\n\n"
        "Focus on one skill at a time and build portfolio projects "
        "to demonstrate your expertise."
    )


def _handle_interview(analysis):

    predicted_job = analysis.get("predicted_job", "your role")
    questions = analysis.get("interview_questions", {})

    return (
        f"🎤 Interview Preparation — {predicted_job}\n\n"
        f"{_format_interview_questions(questions)}\n\n"
        "Tip: Practice answering out loud and prepare 2–3 "
        "project stories with measurable results."
    )


def _handle_missing_skills(analysis):

    skill_gap = analysis.get("skill_gap", {})
    missing = skill_gap.get("missing_skills", [])
    matched = skill_gap.get("matched_skills", [])
    match_pct = skill_gap.get("match_percentage", 0)
    predicted_job = analysis.get("predicted_job", "your target role")

    if not missing:
        return (
            f"✅ Excellent! You match {match_pct}% of skills for "
            f"{predicted_job}.\n\n"
            f"Your matched skills:\n{_bullet_list(matched)}\n\n"
            "Keep building projects to strengthen your profile."
        )

    return (
        f"📚 Skill Gap Analysis — {predicted_job}\n\n"
        f"Match: {match_pct}%\n\n"
        f"Skills you have:\n{_bullet_list(matched)}\n\n"
        f"Skills to learn:\n{_bullet_list(missing)}\n\n"
        "Start with the most in-demand missing skill and "
        "build a project using it."
    )


def _handle_skills(analysis):

    skills = analysis.get("skills", [])
    skill_gap = analysis.get("skill_gap", {})
    match_pct = skill_gap.get("match_percentage", 0)
    predicted_job = analysis.get("predicted_job", "your target role")

    if not skills:
        return (
            "No skills were detected in your resume.\n\n"
            "Add a dedicated Skills section with technologies "
            "you know (e.g., Python, SQL, React)."
        )

    missing = skill_gap.get("missing_skills", [])

    response = (
        f"🧠 Skill Analysis\n\n"
        f"Detected Skills ({len(skills)}):\n"
        f"{_bullet_list(skills)}\n\n"
        f"Career Match ({predicted_job}): {match_pct}%"
    )

    if missing:
        response += (
            f"\n\nMissing Skills:\n{_bullet_list(missing)}"
        )

    return response


def _handle_ats(analysis):

    ats_score = analysis.get("ats_score", 0)
    quality = analysis.get("quality", {})
    feedback = analysis.get("feedback", {})

    tips = []

    if not quality.get("email"):
        tips.append("Add a professional email address")

    if not quality.get("phone"):
        tips.append("Include a 10-digit phone number")

    sections = quality.get("sections", {})
    for section in ["education", "skills", "project", "experience"]:
        if not sections.get(section):
            tips.append(f"Add a {section.title()} section")

    if not quality.get("linkedin"):
        tips.append("Add your LinkedIn profile URL")

    improvements = feedback.get("improvements", [])
    for item in improvements:
        if "ATS" in item:
            tips.append(item)

    tips_text = _bullet_list(tips) if tips else (
        "• Use standard section headings\n"
        "• Include job-specific keywords\n"
        "• Avoid tables, images, and complex formatting"
    )

    if ats_score >= 85:
        verdict = "Your resume is highly ATS-compatible."
    elif ats_score >= 70:
        verdict = "Good ATS score with room for improvement."
    else:
        verdict = "Your ATS score needs improvement before applying."

    return (
        f"📊 ATS Analysis\n\n"
        f"ATS Score: {ats_score}/100\n"
        f"{verdict}\n\n"
        f"Optimization Tips:\n{tips_text}"
    )


def _handle_resume(analysis):

    resume_score = analysis.get("resume_score", 0)
    ats_score = analysis.get("ats_score", 0)
    feedback = analysis.get("feedback", {})
    ai_summary = analysis.get("ai_summary", "")
    quality = analysis.get("quality", {})

    strengths = feedback.get("strengths", [])
    improvements = feedback.get("improvements", [])
    actions = feedback.get("priority_actions", [])
    overall = feedback.get("overall", "")

    response = (
        f"📄 Resume Review\n\n"
        f"Resume Score: {resume_score}/100\n"
        f"ATS Score: {ats_score}/100\n"
    )

    if overall:
        response += f"\nVerdict: {overall}\n"

    if ai_summary:
        response += f"\n{ai_summary}\n"

    if strengths:
        response += f"\nStrengths:\n{_bullet_list(strengths)}\n"

    if improvements:
        response += f"\nAreas to Improve:\n{_bullet_list(improvements)}\n"

    if actions:
        response += f"\nPriority Actions:\n{_bullet_list(actions)}\n"

    if quality:
        response += (
            f"\nQuality Check:\n"
            f"• Length: {quality.get('length', 'N/A')}\n"
            f"• Words: {quality.get('word_count', 0)}"
        )

    return response.strip()


def _handle_jobs(analysis):

    predicted_job = analysis.get("predicted_job", "")
    job_match = analysis.get("job_match", 0)
    recommended = analysis.get("recommended_jobs", [])
    live_jobs = analysis.get("live_jobs", [])

    response = (
        f"💼 Job Recommendations\n\n"
        f"Best Career Match: {predicted_job} ({job_match}%)\n"
    )

    top_careers = analysis.get("top_careers", [])
    if top_careers:
        career_lines = []
        for career in top_careers[:3]:
            if isinstance(career, dict):
                name = career.get("job", career.get("name", ""))
                score = career.get("score", "")
                career_lines.append(
                    f"{name} ({score}%)" if score else name
                )
            else:
                career_lines.append(str(career))

        if career_lines:
            response += (
                f"\nTop Career Matches:\n"
                f"{_bullet_list(career_lines)}\n"
            )

    if recommended:
        response += (
            f"\nAI Recommended Roles:\n"
            f"{_format_jobs(recommended)}\n"
        )

    if live_jobs:
        response += (
            f"\nLive Job Openings:\n"
            f"{_format_jobs(live_jobs)}"
        )

    if not recommended and not live_jobs:
        response += (
            "\nBuild more projects and improve your ATS score "
            "to unlock better job matches."
        )

    return response.strip()


def _handle_career(analysis):

    predicted_job = analysis.get("predicted_job", "Unknown")
    job_match = analysis.get("job_match", 0)
    top_careers = analysis.get("top_careers", [])

    response = (
        f"💼 Career Prediction\n\n"
        f"Best Role: {predicted_job}\n"
        f"Match Score: {job_match}%\n"
    )

    if top_careers:
        lines = []
        for career in top_careers:
            if isinstance(career, dict):
                name = career.get("job", career.get("name", ""))
                score = career.get("score", "")
                lines.append(
                    f"{name} — {score}%" if score else name
                )
            elif isinstance(career, (list, tuple)) and len(career) >= 2:
                lines.append(f"{career[0]} — {career[1]}%")
            else:
                lines.append(str(career))

        response += f"\nTop Career Options:\n{_bullet_list(lines)}\n"

    response += (
        "\nKeep building projects related to this career path "
        "and customize your resume for each application."
    )

    return response


def _handle_feedback(analysis):

    feedback = analysis.get("feedback", {})

    if not feedback:
        return _handle_resume(analysis)

    strengths = feedback.get("strengths", [])
    improvements = feedback.get("improvements", [])
    recommendations = feedback.get("recommendations", [])
    actions = feedback.get("priority_actions", [])
    overall = feedback.get("overall", "")

    response = "⭐ AI Feedback\n\n"

    if overall:
        response += f"{overall}\n\n"

    if strengths:
        response += f"Strengths:\n{_bullet_list(strengths)}\n\n"

    if improvements:
        response += f"Improvements:\n{_bullet_list(improvements)}\n\n"

    if recommendations:
        response += f"Recommendations:\n{_bullet_list(recommendations)}\n\n"

    if actions:
        response += f"Priority Actions:\n{_bullet_list(actions)}"

    return response.strip()


def _handle_quality(analysis):

    quality = analysis.get("quality", {})

    return (
        f"📋 Resume Quality Report\n\n"
        f"{_format_quality(quality)}"
    )


def _handle_github():

    return (
        "🔗 GitHub Profile Tips\n\n"
        "• Create a professional README on your profile\n"
        "• Pin your 3–4 best projects\n"
        "• Add clear descriptions, screenshots, and tech stacks\n"
        "• Include setup instructions for each project\n"
        "• Contribute regularly — green commit graph matters\n"
        "• Use meaningful commit messages\n"
        "• Add your GitHub link to your resume and LinkedIn"
    )


def _handle_linkedin():

    return (
        "🔗 LinkedIn Profile Tips\n\n"
        "• Use a professional headshot photo\n"
        "• Write a compelling headline with your target role\n"
        "• Add a summary highlighting skills and achievements\n"
        "• List all projects, internships, and certifications\n"
        "• Request recommendations from mentors or managers\n"
        "• Engage with industry posts weekly\n"
        "• Add your LinkedIn URL to your resume"
    )


def _handle_improve(analysis):

    feedback = analysis.get("feedback", {})
    actions = feedback.get("priority_actions", [])
    improvements = feedback.get("improvements", [])
    missing = analysis.get("skill_gap", {}).get("missing_skills", [])

    lines = []

    for item in actions:
        lines.append(item)

    for item in improvements:
        if item not in lines:
            lines.append(item)

    if missing:
        lines.append(
            "Learn missing skills: " + ", ".join(missing[:5])
        )

    if not lines:
        lines = [
            "Add measurable achievements to project descriptions",
            "Include job-specific keywords for your target role",
            "Ensure all standard resume sections are present",
            "Build 2–3 portfolio projects on GitHub",
        ]

    return (
        f"📈 How to Improve Your Profile\n\n"
        f"{_bullet_list(lines)}"
    )


def _handle_summary(analysis):

    ai_summary = analysis.get("ai_summary", "")

    if ai_summary:
        return f"🤖 AI Summary\n\n{ai_summary}"

    return _handle_resume(analysis)


# Intent matching — order matters (most specific first)

INTENT_HANDLERS = [

    (
        ["hello", "hi", "hey", "good morning", "good evening"],
        lambda msg, analysis, username: _handle_greeting(username),
    ),

    (
        ["help", "what can you", "what do you", "commands"],
        lambda msg, analysis, username: _handle_help(),
    ),

    (
        ["roadmap", "learning path", "learning plan", "study plan"],
        lambda msg, analysis, username: _handle_roadmap(analysis),
    ),

    (
        ["interview", "questions", "prepare"],
        lambda msg, analysis, username: _handle_interview(analysis),
    ),

    (
        ["missing", "gap", "learn", "weak"],
        lambda msg, analysis, username: _handle_missing_skills(analysis),
    ),

    (
        ["improve", "better", "upgrade", "enhance"],
        lambda msg, analysis, username: _handle_improve(analysis),
    ),

    (
        ["feedback", "strength", "weakness", "suggestion"],
        lambda msg, analysis, username: _handle_feedback(analysis),
    ),

    (
        ["quality", "sections", "format"],
        lambda msg, analysis, username: _handle_quality(analysis),
    ),

    (
        ["summary", "overview", "insight"],
        lambda msg, analysis, username: _handle_summary(analysis),
    ),

    (
        ["ats", "applicant tracking", "keyword"],
        lambda msg, analysis, username: _handle_ats(analysis),
    ),

    (
        ["skill", "analyze my skill", "technical skill"],
        lambda msg, analysis, username: _handle_skills(analysis),
    ),

    (
        ["recommend", "opening", "hiring", "live job"],
        lambda msg, analysis, username: _handle_jobs(analysis),
    ),

    (
        ["resume", "cv", "review my"],
        lambda msg, analysis, username: _handle_resume(analysis),
    ),

    (
        ["career", "predict", "best role", "dream job"],
        lambda msg, analysis, username: _handle_career(analysis),
    ),

    (
        ["job", "find", "suggest", "opportunit"],
        lambda msg, analysis, username: _handle_jobs(analysis),
    ),

    (
        ["github"],
        lambda msg, analysis, username: _handle_github(),
    ),

    (
        ["linkedin"],
        lambda msg, analysis, username: _handle_linkedin(),
    ),

]


def generate_ai_reply(message, analysis, username=None):

    if not message or not message.strip():
        return "Please type a question so I can help you."

    if not analysis:
        return (
            "Please upload and analyze your resume first "
            "so I can provide personalized career guidance."
        )

    message_lower = message.lower().strip()

    for keywords, handler in INTENT_HANDLERS:
        if any(keyword in message_lower for keyword in keywords):
            return handler(message_lower, analysis, username)

    return _handle_help()
