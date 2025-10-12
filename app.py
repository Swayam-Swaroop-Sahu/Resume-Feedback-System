import streamlit as st
import json
import os

# Import heavy modules only when needed
def get_imports():
    """Lazy import of heavy modules to improve initial load time"""
    from resume_parser import parse_resume
    from JD_parser import extract_skills_from_JD
    from matcher import calculate_skill_match, calculate_ats_score
    from feedback import generate_feedback
    import google.generativeai as genai
    return parse_resume, extract_skills_from_JD, calculate_skill_match, calculate_ats_score, generate_feedback, genai

# Cache the skills database loading
@st.cache_data
def load_skills_database():
    """Load skills database with caching for better performance"""
    base_dir = os.path.dirname(__file__)
    skills_path = os.path.join(base_dir, 'data', 'skills_list.json')
    with open(skills_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Cache the resume parsing function
@st.cache_data
def cached_parse_resume(file_input, skills_db):
    """Cached version of parse_resume for better performance"""
    parse_resume, _, _, _, _, _ = get_imports()
    return parse_resume(file_input, skills_db)

# Cache the job description parsing function
@st.cache_data
def cached_extract_skills_from_JD(job_description, skills_db):
    """Cached version of extract_skills_from_JD for better performance"""
    _, extract_skills_from_JD, _, _, _, _ = get_imports()
    return extract_skills_from_JD(job_description, skills_db)

@st.cache_data
def resume_feedback(resume_text, job_description=""):
    """
    Generate enhanced feedback for a given resume using Google AI Studio (Gemini).
    Cached for better performance to avoid repeated API calls.

    Args:
        resume_text (str): Extracted text from the uploaded resume.
        job_description (str, optional): Job description to tailor feedback.

    Returns:
        str: Markdown-formatted feedback from the LLM.
    """
    # Get imports
    _, _, _, _, generate_feedback, genai = get_imports()
    
    # Configure API key from Streamlit secrets
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        # Minimal graceful fallback using rule-based feedback
        return (
            "### AI Feedback (fallback)\n"
            "The AI feedback service is not configured. Please add `GOOGLE_API_KEY` to your `.streamlit/secrets.toml` file.\n\n"
            "- " + "\n- ".join(generate_feedback(0, [], []))
        )
    genai.configure(api_key=api_key)

    jd_context = job_description.strip()

    system_msg = (
        "You are an expert technical recruiter and resume consultant. "
        "Provide concise, highly actionable feedback. Use markdown with clear sections. "
        "Prefer bullet points. Keep to 250-400 words. Tailor advice to the job when provided."
    )

    user_prompt = (
        ("Job Description:\n" + jd_context + "\n\n" if jd_context else "") +
        "Resume Text:\n" + resume_text + "\n\n" +
        "Return sections in this order with short bullets: \n"
        "1) Summary Match (0-100 and one line rationale)\n"
        "2) Strengths\n"
        "3) Gaps/Missing Skills\n"
        "4) ATS & Formatting Fixes\n"
        "5) Impact Upgrades (rewrite 2 bullets as achievement-oriented)\n"
        "6) Priority Next Steps (top 3)."
    )

    try:
        # Use the default model without specifying model_name
        model = genai.GenerativeModel(
            generation_config={
                "temperature": 0.3,
                "top_p": 0.9,
                "max_output_tokens": 800,
            },
        )
        prompt = system_msg + "\n\n" + user_prompt
        response = model.generate_content(prompt)
        return (response.text or "").strip()
    except Exception as e:
        # Fallback to rule-based if API call fails
        fallback = generate_feedback(0, [], [])
        return (
            "### AI Feedback (fallback)\n"
            f"AI feedback is temporarily unavailable. Here's rule-based feedback:\n\n"
            + ("- " + "\n- ".join(fallback) if fallback else "Please try again later.")
        )


# Load skills database using cached function
skills_db = load_skills_database()


st.title("Resume Scorer & ATS Feedback Generator")

# Upload resume file
resume_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=['pdf', 'docx'])

# Paste Job Description text
job_description = st.text_area("Paste Job Description Here")

if st.button("Generate ATS Score and Feedback"):
    if not resume_file or not job_description:
        st.error("Please upload a resume and paste the job description!")
    else:
        # Parse resume using cached function
        resume_data = cached_parse_resume(resume_file, skills_db)
        
        # Check if resume is scanned
        if resume_data.get('is_scanned', False):
            st.header("Scanned Resume Detected")
            st.error("This appears to be a scanned resume or image-based PDF. Please upload a text-based resume for accurate ATS scoring.")
            st.write("ATS Score: **0 / 100** (Cannot process scanned documents)")
            st.write("**Recommendation**: Convert your resume to a text-based PDF or DOCX format for better ATS compatibility.")
        else:
            # Get imports for processing
            _, _, calculate_skill_match, calculate_ats_score, generate_feedback, _ = get_imports()
            
            # Parse job description using cached function
            job_skills = cached_extract_skills_from_JD(job_description, skills_db)
            
            # Calculate matching score
            skill_match = calculate_skill_match(resume_data['skills'], job_skills)
            ats_score = calculate_ats_score(skill_match, bool(resume_data['contact_info']['email']))
            
            # Generate feedback
            feedback = generate_feedback(skill_match, resume_data['skills'], job_skills)
            # Generate LLM feedback (with spinner)
            with st.spinner("Generating AI feedback..."):
                llm_feedback_md = resume_feedback(resume_data.get('text', ''), job_description)
            
            # Display results
            st.header("ATS Score")
            st.write(f"ATS Score: **{ats_score:.2f} / 100**")
            
            # Skill Match Analysis
            st.header("Skill Match Analysis")
            
            # Normalize skills for better matching (lowercase, strip whitespace)
            resume_skills_normalized = {skill.lower().strip() for skill in resume_data['skills']}
            job_skills_normalized = {skill.lower().strip() for skill in job_skills}
            
            # Calculate skill match percentage
            total_job_skills = len(job_skills)
            found_skills_count = len(resume_skills_normalized & job_skills_normalized)
            match_percentage = (found_skills_count / total_job_skills * 100) if total_job_skills > 0 else 0
            
            # Display match percentage with progress bar
            st.metric("Skill Match Rate", f"{match_percentage:.1f}%", f"{found_skills_count}/{total_job_skills} skills")
            st.progress(match_percentage / 100)
            
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Skills Found")
                found_skills = resume_skills_normalized & job_skills_normalized
                if found_skills:
                    # Convert back to original case for display
                    found_skills_display = []
                    for found_skill in found_skills:
                        # Find the original case version
                        for original_skill in resume_data['skills']:
                            if original_skill.lower().strip() == found_skill:
                                found_skills_display.append(original_skill)
                                break
                    st.write(", ".join(sorted(found_skills_display)))
                    st.success(f"Found {len(found_skills)} matching skills!")
                else:
                    st.write("None")
                    st.warning("No matching skills found")

            with col2:
                st.subheader("Skills Missing")
                missing_skills = job_skills_normalized - resume_skills_normalized
                if missing_skills:
                    # Convert back to original case for display
                    missing_skills_display = []
                    for missing_skill in missing_skills:
                        # Find the original case version
                        for original_skill in job_skills:
                            if original_skill.lower().strip() == missing_skill:
                                missing_skills_display.append(original_skill)
                                break
                    st.write(", ".join(sorted(missing_skills_display)))
                    st.error(f"Missing {len(missing_skills)} required skills")
                else:
                    st.write("None")
                    st.success("All required skills found!")
            
            st.header("Extracted Resume Info")
            st.write("Contact Info:", resume_data['contact_info'])
            st.write("Extracted Skills:", resume_data['skills'])
            
            st.header("Feedback")
            if feedback:
                for f in feedback:
                    st.write(f"- {f}")
            else:
                st.write("Your resume looks great!")

            st.header("AI Feedback")
            if llm_feedback_md:
                st.markdown(llm_feedback_md)
