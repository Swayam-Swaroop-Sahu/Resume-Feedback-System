import re
from collections import Counter

def extract_skills_from_JD(job_description: str, skills_db: list) -> dict:
    """
    Extracts skills from a job description and returns a dictionary
    of their frequencies (weights).

    Args:
        job_description (str): The raw text of the job description.
        skills_db (list): The list of skills from skills_list.json.

    Returns:
        dict: A dictionary where keys are normalized skills and
              values are their frequency (count) in the JD.
    """
    job_description_lower = job_description.lower()
    skill_weights = {}

    # Create a set of normalized skills for fast lookup
    skills_db_normalized = {skill.lower().strip() for skill in skills_db}

    # Use regex to find whole-word matches to avoid partial matches
    # (e.g., matching "java" in "javascript")
    for skill in skills_db_normalized:
        try:
            # Create a regex pattern for the whole word
            pattern = r'\b' + re.escape(skill) + r'\b'
            matches = re.findall(pattern, job_description_lower)
            
            if matches:
                skill_weights[skill] = len(matches)
        except re.error:
            # Handle potential regex errors for skills with special chars
            continue
            
    # Fallback for JDs that are just comma-separated lists
    if not skill_weights:
        words = re.findall(r'\b\w+\b', job_description_lower)
        word_counts = Counter(words)
        for skill in skills_db_normalized:
            if skill in word_counts:
                skill_weights[skill] = word_counts[skill]

    return skill_weights