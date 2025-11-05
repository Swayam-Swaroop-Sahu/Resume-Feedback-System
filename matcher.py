import numpy as np

def calculate_weighted_skill_match(resume_skills_set: set, job_skill_weights: dict) -> float:
    """
    Calculates a weighted skill match score based on keyword frequency in the JD.

    Args:
        resume_skills_set (set): A set of normalized skills from the resume.
        job_skill_weights (dict): A dict where keys are normalized skills from the JD
                                  and values are their frequency (weight).

    Returns:
        float: A score from 0 to 100.
    """
    if not job_skill_weights:
        return 0.0

    matched_score = 0
    total_possible_score = sum(job_skill_weights.values())

    for skill in resume_skills_set:
        if skill in job_skill_weights:
            matched_score += job_skill_weights[skill] # Add the weight of the matched skill

    match_percentage = (matched_score / total_possible_score) * 100
    return min(match_percentage, 100.0) # Cap at 100

def calculate_format_score(resume_data: dict) -> float:
    """
    Calculates a score based on the presence of key ATS-friendly sections.

    Args:
        resume_data (dict): The full dictionary returned by the resume_parser.

    Returns:
        float: A score from 0 to 100.
    """
    score = 0
    
    # Check for basic contact info (50 points)
    contact_info = resume_data.get('contact_info', {})
    if contact_info.get('email'):
        score += 25
    if contact_info.get('phone'):
        score += 25

    # Check for key sections (50 points)
    if resume_data.get('education'):
        score += 25
    if resume_data.get('experience'):
        score += 25
        
    return float(score)

def calculate_ats_score(skill_match_score: float, format_score: float) -> float:
    """
    Calculates the final ATS score by combining skill match and format scores.
    Weighs skill match as 70% and format/completeness as 30%.

    Args:
        skill_match_score (float): The 0-100 score from calculate_weighted_skill_match.
        format_score (float): The 0-100 score from calculate_format_score.

    Returns:
        float: The final ATS score, rounded to two decimal places.
    """
    
    # Skill match is 70% of the score
    skill_component = skill_match_score * 0.70
    
    # Format friendliness is 30% of the score
    format_component = format_score * 0.30
    
    final_score = skill_component + format_component
    
    return round(final_score, 2)