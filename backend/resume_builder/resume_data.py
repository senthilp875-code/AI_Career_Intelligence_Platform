import copy
import re

from .template_engine import TEMPLATES, get_template

DEFAULT_TEMPLATE = "modern_professional"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

EMPTY_EXPERIENCE = {
    "role": "",
    "company": "",
    "location": "",
    "start": "",
    "end": "",
    "current": "",
    "bullets": "",
}

EMPTY_EDUCATION = {
    "degree": "",
    "school": "",
    "field": "",
    "location": "",
    "start": "",
    "end": "",
    "gpa": "",
    "details": "",
}

EMPTY_PROJECT = {
    "name": "",
    "tech": "",
    "description": "",
    "url": "",
    "github": "",
    "live": "",
}

EMPTY_CERTIFICATION = {
    "name": "",
    "issuer": "",
    "year": "",
}

EMPTY_ACHIEVEMENT = {
    "title": "",
    "description": "",
}

EMPTY_LANGUAGE = {
    "name": "",
    "level": "",
}

EMPTY_CUSTOM = {
    "title": "",
    "content": "",
}


def empty_resume():
    return {
        "id": None,
        "title": "Untitled Resume",
        "template": DEFAULT_TEMPLATE,
        "full_name": "",
        "professional_title": "",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "github": "",
        "portfolio": "",
        "summary": "",
        "skills": "",
        "interests": "",
        "experience": [copy.deepcopy(EMPTY_EXPERIENCE)],
        "education": [copy.deepcopy(EMPTY_EDUCATION)],
        "projects": [copy.deepcopy(EMPTY_PROJECT)],
        "certifications": [copy.deepcopy(EMPTY_CERTIFICATION)],
        "achievements": [copy.deepcopy(EMPTY_ACHIEVEMENT)],
        "languages": [copy.deepcopy(EMPTY_LANGUAGE)],
        "custom_sections": [],
        "ats_score": None,
    }


def _as_text(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else ""
    if isinstance(value, (list, tuple)):
        parts = []
        for item in value:
            if isinstance(item, dict):
                text = _as_text(item.get("name") or item.get("title") or item.get("skill"))
            else:
                text = str(item).strip()
            if text:
                parts.append(text)
        return ", ".join(parts)
    return str(value).strip()


def _truthy(value):
    if value is True:
        return "yes"
    text = _as_text(value).lower()
    return "yes" if text in ("1", "true", "yes", "on", "present") else ""


def _normalize_url(value):
    text = _as_text(value)
    if not text:
        return ""
    if re.match(r"^https?://", text, re.I):
        return text
    lowered = text.lower()
    if lowered.startswith("linkedin.com") or lowered.startswith("www.linkedin.com"):
        return "https://" + text.lstrip("/")
    if lowered.startswith("github.com") or lowered.startswith("www.github.com"):
        return "https://" + text.lstrip("/")
    if "." in text and " " not in text:
        return "https://" + text.lstrip("/")
    return text


def _looks_like_url(value):
    text = _as_text(value)
    if not text:
        return True
    if re.match(r"^https?://", text, re.I):
        return True
    lowered = text.lower()
    return "linkedin.com" in lowered or "github.com" in lowered or "." in text


def _normalize_entries(items, blank):
    if not isinstance(items, list):
        return [copy.deepcopy(blank)]
    normalized = []
    for item in items:
        if not isinstance(item, dict):
            continue
        row = copy.deepcopy(blank)
        for key in row:
            if key == "bullets":
                bullets = item.get("bullets")
                if isinstance(bullets, list):
                    row[key] = "\n".join(
                        str(line).strip() for line in bullets if str(line).strip()
                    )
                else:
                    row[key] = _as_text(bullets)
            elif key == "current":
                row[key] = _truthy(item.get("current"))
            elif key in ("url", "github", "live"):
                row[key] = _normalize_url(item.get(key))
            else:
                row[key] = _as_text(item.get(key))
        if row.get("current"):
            row["end"] = row.get("end") or "Present"
        normalized.append(row)
    return normalized or [copy.deepcopy(blank)]


def _normalize_languages(value):
    if isinstance(value, list):
        rows = []
        for item in value:
            row = copy.deepcopy(EMPTY_LANGUAGE)
            if isinstance(item, dict):
                row["name"] = _as_text(item.get("name"))
                row["level"] = _as_text(item.get("level"))
            else:
                row["name"] = _as_text(item)
            if row["name"]:
                rows.append(row)
        return rows or [copy.deepcopy(EMPTY_LANGUAGE)]
    text = _as_text(value)
    if not text:
        return [copy.deepcopy(EMPTY_LANGUAGE)]
    rows = []
    for chunk in text.split(","):
        name = chunk.strip()
        if name:
            rows.append({"name": name, "level": ""})
    return rows or [copy.deepcopy(EMPTY_LANGUAGE)]


def normalize_resume(payload):
    base = empty_resume()
    if not isinstance(payload, dict):
        return base

    for key in (
        "title",
        "full_name",
        "professional_title",
        "email",
        "phone",
        "location",
        "summary",
        "skills",
        "interests",
    ):
        if key in payload:
            base[key] = _as_text(payload.get(key))

    for key in ("linkedin", "github", "portfolio"):
        if key in payload:
            base[key] = _normalize_url(payload.get(key))

    template = _as_text(payload.get("template")) or DEFAULT_TEMPLATE
    if template not in TEMPLATES:
        template = DEFAULT_TEMPLATE
    base["template"] = template

    resume_id = payload.get("id")
    if resume_id in ("", None):
        base["id"] = None
    else:
        try:
            base["id"] = int(resume_id)
        except (TypeError, ValueError):
            base["id"] = None

    ats_score = payload.get("ats_score")
    if ats_score in ("", None):
        base["ats_score"] = None
    else:
        try:
            base["ats_score"] = int(ats_score)
        except (TypeError, ValueError):
            base["ats_score"] = None

    if not base["title"]:
        name = base["full_name"] or "Untitled"
        base["title"] = f"{name} Resume"

    base["experience"] = _normalize_entries(payload.get("experience"), EMPTY_EXPERIENCE)
    base["education"] = _normalize_entries(payload.get("education"), EMPTY_EDUCATION)
    base["projects"] = _normalize_entries(payload.get("projects"), EMPTY_PROJECT)
    base["certifications"] = _normalize_entries(
        payload.get("certifications"), EMPTY_CERTIFICATION
    )
    base["achievements"] = _normalize_entries(
        payload.get("achievements"), EMPTY_ACHIEVEMENT
    )
    base["languages"] = _normalize_languages(
        payload.get("languages") if "languages" in payload else []
    )

    custom = payload.get("custom_sections")
    if isinstance(custom, list):
        base["custom_sections"] = [
            item
            for item in _normalize_entries(custom, EMPTY_CUSTOM)
            if entry_has_content(item)
        ]
    else:
        base["custom_sections"] = []

    return base


def skill_list(resume):
    raw = resume.get("skills") or ""
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    parts = []
    for chunk in str(raw).replace("\n", ",").split(","):
        item = chunk.strip()
        if item and item not in parts:
            parts.append(item)
    return parts


def csv_list(value):
    if isinstance(value, list):
        names = []
        for item in value:
            if isinstance(item, dict):
                name = _as_text(item.get("name"))
                level = _as_text(item.get("level"))
                if name and level:
                    names.append(f"{name} ({level})")
                elif name:
                    names.append(name)
            else:
                text = _as_text(item)
                if text:
                    names.append(text)
        return names
    return skill_list({"skills": value})


def entry_has_content(entry):
    return any(_as_text(value) for value in entry.values())


def format_dates(start, end, current=""):
    start = _as_text(start)
    end = "Present" if _truthy(current) else _as_text(end)
    if start and end:
        return f"{start} – {end}"
    return start or end


def validate_resume(resume):
    data = normalize_resume(resume)
    warnings = []
    errors = []

    if not data["full_name"]:
        warnings.append("Add your full name.")
        errors.append("Full name is required.")
    if not data["email"]:
        warnings.append("Add a professional email address.")
    elif not EMAIL_RE.match(data["email"]):
        warnings.append("Email address looks invalid.")
        errors.append("Enter a valid email address.")
    if not data["professional_title"]:
        warnings.append("Add a professional title.")

    for key, label in (
        ("linkedin", "LinkedIn"),
        ("github", "GitHub"),
        ("portfolio", "Portfolio"),
    ):
        if data.get(key) and not _looks_like_url(data.get(key)):
            warnings.append(f"{label} should be a valid URL.")
            errors.append(f"{label} URL is not valid.")

    words = [word for word in data["summary"].split() if word]
    if not data["summary"]:
        warnings.append("Write a professional summary.")
    elif len(words) < 30:
        warnings.append("Summary is short — aim for about 30–80 words.")
    elif len(words) > 90:
        warnings.append("Summary is long — try keeping it under 80 words.")
    if not skill_list(data):
        warnings.append("Add at least a few skills.")
    has_experience = any(entry_has_content(item) for item in data["experience"])
    has_education = any(entry_has_content(item) for item in data["education"])
    has_projects = any(entry_has_content(item) for item in data["projects"])
    if not (has_experience or has_education or has_projects):
        warnings.append("Add experience, education, or a project.")

    seen_roles = set()
    for item in data["experience"]:
        key = (item.get("role"), item.get("company"), item.get("start"))
        if entry_has_content(item) and key in seen_roles:
            warnings.append("Duplicate experience entries were found.")
            break
        if entry_has_content(item):
            seen_roles.add(key)

    return {
        "warnings": warnings,
        "errors": errors,
        "summary_words": len(words),
        "summary_chars": len(data["summary"]),
        "template": get_template(data["template"]),
        "ok": not errors,
    }


def resume_filename(resume, extension):
    data = normalize_resume(resume)
    name = data["full_name"] or "Resume"
    safe = "".join(ch if ch.isalnum() or ch in (" ", "_", "-") else "" for ch in name)
    safe = "_".join(safe.split()) or "Resume"
    return f"{safe}.{extension}"


def _first(*values):
    for value in values:
        text = _as_text(value)
        if text:
            return text
    return ""


def _fill_empty_scalars(target, source, keys):
    for key in keys:
        if not _as_text(target.get(key)) and _as_text(source.get(key)):
            target[key] = source[key]


def build_resume_from_sources(user=None, analysis=None, saved=None):
    resume = empty_resume()
    user = user or {}
    analysis = analysis or {}
    entities = analysis.get("entities") if isinstance(analysis, dict) else {}
    if not isinstance(entities, dict):
        entities = {}

    resume["full_name"] = _first(user.get("full_name"))
    resume["professional_title"] = _first(
        user.get("headline"),
        analysis.get("predicted_job"),
    )
    resume["email"] = _first(
        user.get("email"),
        analysis.get("email"),
        entities.get("email"),
    )
    resume["phone"] = _first(
        user.get("phone"),
        analysis.get("phone"),
        entities.get("phone"),
    )
    resume["location"] = _first(user.get("location"))
    resume["linkedin"] = _normalize_url(
        _first(user.get("linkedin"), entities.get("linkedin"))
    )
    resume["github"] = _normalize_url(_first(user.get("github"), entities.get("github")))
    resume["portfolio"] = _normalize_url(_first(user.get("portfolio")))
    resume["summary"] = _first(
        analysis.get("professional_summary"),
        analysis.get("ai_summary") if False else "",
    )

    skills = skill_list({"skills": user.get("skills")})
    analysis_skills = analysis.get("skills") if isinstance(analysis, dict) else []
    if isinstance(analysis_skills, list):
        for skill in analysis_skills:
            text = _as_text(skill)
            if text and text not in skills:
                skills.append(text)
    resume["skills"] = ", ".join(skills)

    education_items = entities.get("education") or analysis.get("education") or []
    if isinstance(education_items, list) and education_items:
        resume["education"] = []
        for item in education_items:
            row = copy.deepcopy(EMPTY_EDUCATION)
            if isinstance(item, dict):
                row.update({key: _as_text(item.get(key)) for key in row if key in item})
            else:
                row["degree"] = _as_text(item)
            resume["education"].append(row)

    project_items = entities.get("projects") or analysis.get("projects") or []
    if isinstance(project_items, list) and project_items:
        resume["projects"] = []
        for item in project_items:
            row = copy.deepcopy(EMPTY_PROJECT)
            if isinstance(item, dict):
                row.update({key: _as_text(item.get(key)) for key in row if key in item})
            else:
                row["name"] = _as_text(item)
            resume["projects"].append(row)

    cert_items = entities.get("certifications") or analysis.get("certifications") or []
    if isinstance(cert_items, list) and cert_items:
        resume["certifications"] = []
        for item in cert_items:
            row = copy.deepcopy(EMPTY_CERTIFICATION)
            if isinstance(item, dict):
                row.update({key: _as_text(item.get(key)) for key in row if key in item})
            else:
                row["name"] = _as_text(item)
            resume["certifications"].append(row)

    internships = entities.get("internships") or analysis.get("experience") or []
    if isinstance(internships, list) and internships:
        resume["experience"] = []
        for item in internships:
            row = copy.deepcopy(EMPTY_EXPERIENCE)
            if isinstance(item, dict):
                row.update({key: _as_text(item.get(key)) for key in row if key in item})
            else:
                row["role"] = _as_text(item)
            resume["experience"].append(row)

    if resume["full_name"]:
        resume["title"] = f"{resume['full_name']} Resume"

    prefilled = normalize_resume(resume)

    if isinstance(saved, dict):
        merged = normalize_resume(saved)
        merged["id"] = saved.get("id", merged.get("id"))
        _fill_empty_scalars(
            merged,
            prefilled,
            (
                "full_name",
                "professional_title",
                "email",
                "phone",
                "location",
                "linkedin",
                "github",
                "portfolio",
                "summary",
                "skills",
                "interests",
            ),
        )
        return merged

    return prefilled
