import re

def extract_skills_from_JD(JD_text, skills_db):
    # Create a single regex pattern from all skills
    # This joins all skills with '|' (OR operator)
    # e.g., r'\b(python|java|react|sql)\b'
    skills_pattern = r'\b(' + '|'.join(re.escape(skill) for skill in skills_db) + r')\b'

    # Find all matches in one go, ignoring case
    matched_skills = re.findall(skills_pattern, JD_text, re.IGNORECASE)

    # Return the unique skills found
    return list(set(skill.lower() for skill in matched_skills))