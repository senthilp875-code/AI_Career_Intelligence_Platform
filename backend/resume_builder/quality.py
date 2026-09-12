import re

from ai_engine.ats_checker import calculate_ats_score
from ai_engine.skill_gap import JOB_SKILLS, analyze_skill_gap

from .resume_data import (
    csv_list,
    entry_has_content,
    normalize_resume,
    skill_list,
    validate_resume,
)

ACTION_VERBS = {
    "achieved",
    "analyzed",
    "automated",
    "built",
    "created",
    "delivered",
    "designed",
    "developed",
    "implemented",
    "improved",
    "led",
    "managed",
    "optimized",
    "reduced",
    "shipped",
}


def resume_plain_text(resume):
    data = normalize_resume(resume)
    parts = [
        "education skills project experience internship certification achievement",
        data.get("full_name") or "",
        data.get("professional_title") or "",
        data.get("email") or "",
        data.get("phone") or "",
        data.get("location") or "",
        data.get("linkedin") or "",
        data.get("github") or "",
        data.get("portfolio") or "",
        data.get("summary") or "",
        ", ".join(skill_list(data)),
        ", ".join(csv_list(data.get("languages"))),
    ]

    phone_digits = re.sub(r"\D", "", data.get("phone") or "")
    if len(phone_digits) >= 10:
        parts.append(phone_digits[-10:])

    if data.get("linkedin"):
        parts.append("linkedin")
    if data.get("github"):
        parts.append("github")

    for item in data.get("experience") or []:
        if not entry_has_content(item):
            continue
        parts.extend(
            [
                item.get("role") or "",
                item.get("company") or "",
                item.get("location") or "",
                item.get("bullets") or "",
            ]
        )
    for item in data.get("education") or []:
        if not entry_has_content(item):
            continue
        parts.extend(
            [
                item.get("degree") or "",
                item.get("school") or "",
                item.get("field") or "",
                item.get("details") or "",
                item.get("gpa") or "",
            ]
        )
    for item in data.get("projects") or []:
        if not entry_has_content(item):
            continue
        parts.extend(
            [
                item.get("name") or "",
                item.get("tech") or "",
                item.get("description") or "",
            ]
        )
    for item in data.get("certifications") or []:
        if entry_has_content(item):
            parts.append(item.get("name") or "")
    for item in data.get("achievements") or []:
        if entry_has_content(item):
            parts.extend([item.get("title") or "", item.get("description") or ""])
    for item in data.get("custom_sections") or []:
        if entry_has_content(item):
            parts.extend([item.get("title") or "", item.get("content") or ""])

    return "\n".join(part for part in parts if str(part).strip())


def _weak_bullets(data):
    findings = []
    for item in data.get("experience") or []:
        role = item.get("role") or item.get("company") or "Experience"
        for line in str(item.get("bullets") or "").split("\n"):
            text = line.strip(" •-\t")
            if not text:
                continue
            issues = []
            words = text.split()
            if len(words) < 8:
                issues.append("too short")
            if not re.search(r"\d", text):
                issues.append("no measurable result")
            first = re.sub(r"[^A-Za-z]", "", words[0]).lower() if words else ""
            if first not in ACTION_VERBS:
                issues.append("weak or missing action verb")
            if issues:
                findings.append(
                    {
                        "context": role,
                        "text": text,
                        "issues": issues,
                    }
                )
    return findings[:10]


def evaluate_resume(resume, analysis=None):
    data = normalize_resume(resume)
    validation = validate_resume(data)
    text = resume_plain_text(data)
    ats_score = calculate_ats_score(text) if text.strip() else 0

    skills = skill_list(data)
    has_experience = any(entry_has_content(item) for item in data["experience"])
    has_education = any(entry_has_content(item) for item in data["education"])
    has_projects = any(entry_has_content(item) for item in data["projects"])
    has_certs = any(entry_has_content(item) for item in data["certifications"])
    two_column = data.get("template") == "modern_two_column"

    checklist = [
        {"id": "name", "label": "Full name is present", "ok": bool(data["full_name"])},
        {"id": "email", "label": "Email is present", "ok": bool(data["email"])},
        {
            "id": "contact",
            "label": "Phone or location is present",
            "ok": bool(data["phone"] or data["location"]),
        },
        {
            "id": "summary",
            "label": "Professional summary is present",
            "ok": bool(data["summary"]),
        },
        {"id": "skills", "label": "Skills are listed", "ok": bool(skills)},
        {"id": "education", "label": "Education is present", "ok": has_education},
        {
            "id": "experience",
            "label": "Experience is present",
            "ok": has_experience,
        },
        {"id": "projects", "label": "Projects are present", "ok": has_projects},
        {
            "id": "links",
            "label": "LinkedIn or GitHub is present",
            "ok": bool(data["linkedin"] or data["github"]),
        },
        {
            "id": "structure",
            "label": "ATS-friendly single-column structure",
            "ok": not two_column,
        },
    ]

    passed = sum(1 for item in checklist if item["ok"])
    readiness = round((passed / len(checklist)) * 100) if checklist else 0

    predicted_job = ""
    missing_skills = []
    keyword_suggestions = []
    analysis = analysis if isinstance(analysis, dict) else {}
    predicted_job = analysis.get("predicted_job") or ""
    existing_gap = analysis.get("skill_gap") if analysis else None

    if predicted_job:
        if isinstance(existing_gap, dict) and existing_gap.get("missing_skills"):
            missing_skills = [
                skill
                for skill in existing_gap.get("missing_skills") or []
                if skill.lower() not in {item.lower() for item in skills}
            ]
        else:
            gap = analyze_skill_gap(predicted_job, skills)
            missing_skills = gap.get("missing_skills") or []
        required = JOB_SKILLS.get(predicted_job, [])
        have = {item.lower() for item in skills}
        keyword_suggestions = [skill for skill in required if skill.lower() not in have]

    summary_suggestions = []
    words = [word for word in data["summary"].split() if word]
    if not data["summary"]:
        summary_suggestions.append(
            "Write a 3–5 sentence summary that names your target role and strongest skills."
        )
    elif len(words) < 30:
        summary_suggestions.append(
            "Expand the summary to about 30–80 words so recruiters get a complete snapshot."
        )
    elif len(words) > 90:
        summary_suggestions.append(
            "Tighten the summary to under 80 words and keep only the most relevant achievements."
        )
    if predicted_job:
        summary_suggestions.append(
            f"Mention {predicted_job} and 2–3 matching keywords if that is your target role."
        )
    if analysis.get("ai_summary"):
        summary_suggestions.append(str(analysis.get("ai_summary")))

    formatting = []
    if two_column:
        formatting.append(
            "Two-column layouts can confuse some ATS parsers. Use Minimal ATS for strict screening."
        )
    if not has_certs:
        formatting.append("Consider adding certifications if they support the target role.")
    if has_experience and not any(
        str(item.get("bullets") or "").strip() for item in data["experience"]
    ):
        formatting.append("Add accomplishment bullets under work experience.")

    return {
        "ats_score": ats_score,
        "readiness": readiness,
        "checklist": checklist,
        "warnings": validation["warnings"],
        "errors": validation.get("errors") or [],
        "missing_skills": missing_skills,
        "keyword_suggestions": keyword_suggestions,
        "weak_bullets": _weak_bullets(data),
        "summary_suggestions": summary_suggestions[:4],
        "formatting": formatting,
        "predicted_job": predicted_job,
        "template": data.get("template"),
    }
