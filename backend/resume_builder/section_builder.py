def build_resume_sections(analysis):

    return {

        "summary": {
            "title": "Professional Summary",
            "content": analysis.get(
                "professional_summary",
                "Professional summary not available."
            )
        },

        "skills": {
            "title": "Technical Skills",
            "content": analysis.get("skills", [])
        },

        "projects": {
            "title": "Projects",
            "content": analysis.get("projects", [])
        },

        "education": {
            "title": "Education",
            "content": analysis.get("education", [])
        },

        "certifications": {
            "title": "Certifications",
            "content": analysis.get("certifications", [])
        }

    }