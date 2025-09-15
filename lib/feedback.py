def generate_feedback(skill_match, resume_skills, job_skills):
    missing_skills = list(set(job_skills) - set(resume_skills))
    feedback = []
    if skill_match < 70:
        feedback.append(f"Consider adding these missing skills: {', '.join(missing_skills)}")
    return feedback
