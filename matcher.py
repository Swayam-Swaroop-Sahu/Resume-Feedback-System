def calculate_skill_match(resume_skills, job_skills):
    matched = set(resume_skills) & set(job_skills)
    if not job_skills:
        return 0
    return (len(matched)/len(job_skills)) * 100

def calculate_ats_score(skill_match, has_contact_info):
    score = (skill_match*0.8) + (has_contact_info * 20)
    return min(score, 100)