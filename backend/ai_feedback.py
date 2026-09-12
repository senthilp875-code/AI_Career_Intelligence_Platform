def generate_feedback(resume_text, skills):

    strengths = []
    weaknesses = []
    suggestions = []

    text = resume_text.lower()

    # ---------------- Strengths ----------------
    if len(skills) >= 8:
        strengths.append("Strong technical skill set.")
    elif len(skills) >= 5:
        strengths.append("Good technical foundation.")
    else:
        weaknesses.append("Very few technical skills detected.")
        suggestions.append("Add more technical skills to your resume.")

    if "project" in text:
        strengths.append("Projects section is available.")
    else:
        weaknesses.append("Projects section is missing.")
        suggestions.append("Add 2–3 academic or personal projects.")

    if "experience" in text or "internship" in text:
        strengths.append("Experience/Internship is mentioned.")
    else:
        weaknesses.append("No experience or internship found.")
        suggestions.append("Mention internships, freelance work, or practical experience.")

    if "certification" in text or "certificate" in text:
        strengths.append("Certifications are included.")
    else:
        weaknesses.append("No certifications found.")
        suggestions.append("Complete certifications from Coursera, Google, Microsoft, or IBM.")

    if "github" in text:
        strengths.append("GitHub profile is included.")
    else:
        weaknesses.append("GitHub profile is missing.")
        suggestions.append("Add your GitHub profile link if you have coding projects.")

    if "linkedin" in text:
        strengths.append("LinkedIn profile is included.")
    else:
        suggestions.append("Add your LinkedIn profile to improve your professional presence.")

    return strengths, weaknesses, suggestions