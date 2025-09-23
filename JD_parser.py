import re

def extract_skills_from_JD(JD_text, skills_db):
    matched_skills = []
    for skill in skills_db:
        if re.search(rf"\b{skill}\b", JD_text, re.IGNORECASE):
            matched_skills.append(skill)
    return list(set(matched_skills))