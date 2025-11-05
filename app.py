import streamlit as st
import json
import os
import pandas as pd

# Import heavy modules only when needed
def get_imports():
    """Lazy import of heavy modules to improve initial load time"""
    from resume_parser import parse_resume
    from JD_parser import extract_skills_from_JD
    # --- UPDATED IMPORTS ---
    from matcher import calculate_weighted_skill_match, calculate_format_score, calculate_ats_score
    from feedback import generate_feedback
    import google.generativeai as genai
    return parse_resume, extract_skills_from_JD, calculate_weighted_skill_match, calculate_format_score, calculate_ats_score, generate_feedback, genai

# Cache the skills database loading
@st.cache_data
def load_skills_database():
    """Load skills database with caching for better performance"""
    base_dir = os.path.dirname(__file__)
    skills_path = os.path.join(base_dir, 'data', 'skills_list.json')
    try:
        with open(skills_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"FATAL ERROR: skills_list.json not found at {skills_path}")
        return []
    except json.JSONDecodeError:
        st.error(f"FATAL ERROR: skills_list.json is not valid JSON.")
        return []

# Cache the resume parsing function
@st.cache_data
def cached_parse_resume(file_input, skills_db):
    """Cached version of parse_resume for better performance"""
    parse_resume, _, _, _, _, _, _ = get_imports()
    return parse_resume(file_input, skills_db)

# Cache the job description parsing function
@st.cache_data
def cached_extract_skills_from_JD(job_description, skills_db):
    """Cached version of extract_skills_from_JD for better performance"""
    _, extract_skills_from_JD, _, _, _, _, _ = get_imports()
    return extract_skills_from_JD(job_description, skills_db)

@st.cache_data
def resume_feedback(resume_text, job_description=""):
    """
    Generate enhanced feedback for a given resume using Google AI Studio (Gemini).
    """
    # Get imports
    _, _, _, _, _, generate_feedback, genai = get_imports()
    
    try:
        # Get API key from Streamlit Secrets
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except KeyError:
        return "### AI Feedback Error\nAPI key (GOOGLE_API_KEY) not found in Streamlit secrets."
    except Exception as e:
        return f"### AI Feedback Error\nCould not configure AI service: {e}"

    jd_context = job_description.strip()
    system_msg = (
        "You are an expert technical recruiter... [Your system prompt here]..."
    )
    user_prompt = (
        ("Job Description:\n" + jd_context + "\n\n" if jd_context else "") +
        "Resume Text:\n" + resume_text + "\n\n" +
        "Return sections in this order..."
    )

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            generation_config={
                "temperature": 0.3, "top_p": 0.9, "max_output_tokens": 800,
            },
        )
        prompt = system_msg + "\n\n" + user_prompt
        response = model.generate_content(prompt)
        return (response.text or "").strip()
    
    except Exception as e:
        st.error(f"An error occurred while generating AI feedback: {e}")
        fallback = generate_feedback(0, [], {}) # Pass empty dict for job skills
        return (
            "### AI Feedback (fallback)\n"
            f"AI feedback is temporarily unavailable. Here's rule-based feedback:\n\n"
            + ("- " + "\n- ".join(fallback) if fallback else "Please try again later.")
        )


# --- Main App Logic ---

# Load skills database using cached function
skills_db = load_skills_database()

st.title("Resume Scorer & ATS Feedback Generator")

# Upload resume file
resume_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=['pdf', 'docx'])

# Paste Job Description text
job_description = st.text_area("Paste Job Description Here", height=200)

if st.button("Generate ATS Score and Feedback"):
    if not resume_file or not job_description:
        st.error("Please upload a resume and paste the job description!")
    else:
        with st.spinner("Analyzing your resume and job description..."):
            # Parse resume using cached function
            resume_data = cached_parse_resume(resume_file, skills_db)
            
            # Check if resume is scanned
            if resume_data.get('is_scanned', False):
                st.header("Scanned Resume Detected")
                st.error("This appears to be a scanned resume or image-based PDF. Please upload a text-based resume for accurate ATS scoring.")
                st.write("ATS Score: **0 / 100** (Cannot process scanned documents)")
                st.write("**Recommendation**: Convert your resume to a text-based PDF or DOCX format for better ATS compatibility.")
            
            # --- NEW SCORING LOGIC ---
            else:
                # Get imports for processing
                _, _, calculate_weighted_skill_match, calculate_format_score, calculate_ats_score, generate_feedback, _ = get_imports()
                
                # Parse job description using cached function (now returns a dict of weights)
                job_skill_weights = cached_extract_skills_from_JD(job_description, skills_db)
                
                if not job_skill_weights:
                    st.warning("Could not extract any skills from the Job Description. Make sure it's detailed enough.")
                    # Still, proceed to show formatting score and AI feedback
                
                # Normalize resume skills
                resume_skills_set = {skill.lower().strip() for skill in resume_data.get('skills', [])}
                
                # Calculate new scores
                skill_match_score = calculate_weighted_skill_match(resume_skills_set, job_skill_weights)
                format_score = calculate_format_score(resume_data)
                ats_score = calculate_ats_score(skill_match_score, format_score)
                
                # --- NEW DISPLAY ---
                
                # Display final ATS Score
                st.header("ATS Score")
                st.metric("Final ATS Score", f"{ats_score:.2f} / 100")
                
                # Breakdown of the score
                st.subheader("Score Breakdown")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Skill Match Score (70%)", f"{skill_match_score:.1f}%")
                with col2:
                    st.metric("Format & Completeness Score (30%)", f"{format_score:.1f}%")
                
                st.progress(ats_score / 100)
                
                # --- UPDATED SKILL ANALYSIS ---
                st.header("Weighted Skill Match Analysis")
                
                if job_skill_weights:
                    job_skills_normalized = set(job_skill_weights.keys())
                    
                    found_skills = resume_skills_set & job_skills_normalized
                    missing_skills = job_skills_normalized - resume_skills_set
                    
                    # Create a DataFrame for a cleaner table display
                    skill_data = []
                    
                    # Add found skills
                    for skill in sorted(list(found_skills)):
                        skill_data.append({
                            "Skill": skill.title(),
                            "Status": "✅ Found",
                            "Importance (JD Mentions)": job_skill_weights[skill]
                        })
                    
                    # Add missing skills
                    for skill in sorted(list(missing_skills)):
                        skill_data.append({
                            "Skill": skill.title(),
                            "Status": "❌ Missing",
                            "Importance (JD Mentions)": job_skill_weights[skill]
                        })
                    
                    # Sort by importance, then alphabetically
                    if skill_data:
                        df = pd.DataFrame(skill_data)
                        df = df.sort_values(by=["Importance (JD Mentions)", "Skill"], ascending=[False, True])
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No relevant skills from the database were found in the job description.")

                else:
                    st.info("No skills from our database were found in the job description to match against.")

                
                # --- AI FEEDBACK (Spinner is now separate) ---
                st.header("AI-Powered Feedback")
                with st.spinner("Generating detailed AI feedback..."):
                    llm_feedback_md = resume_feedback(resume_data.get('text', ''), job_description)
                
                st.markdown(llm_feedback_md)

                # --- Extracted Info (for debugging/info) ---
                with st.expander("See Extracted Resume Data"):
                    st.write("Contact Info:", resume_data.get('contact_info', {}))
                    st.write("Extracted Skills (from resume):", resume_data.get('skills', []))