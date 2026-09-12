from resume_builder.resume_data import build_resume_from_sources


def generate_resume(analysis):
    resume = build_resume_from_sources(analysis=analysis or {})
    skills = [
        item.strip()
        for item in str(resume.get("skills") or "").split(",")
        if item.strip()
    ]
    projects = [
        item["name"] or item["description"]
        for item in resume.get("projects") or []
        if (item.get("name") or item.get("description"))
    ]
    education = [
        " — ".join(
            part
            for part in (item.get("degree"), item.get("school"), item.get("field"))
            if part
        )
        for item in resume.get("education") or []
        if item.get("degree") or item.get("school")
    ]
    certifications = [
        item["name"]
        for item in resume.get("certifications") or []
        if item.get("name")
    ]
    return {
        "name": resume.get("full_name") or "",
        "email": resume.get("email") or "",
        "phone": resume.get("phone") or "",
        "summary": resume.get("summary") or "",
        "skills": skills,
        "projects": projects,
        "education": education,
        "certifications": certifications,
    }
