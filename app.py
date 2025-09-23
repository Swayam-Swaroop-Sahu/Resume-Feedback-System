import streamlit as st
import json
import os
from resume_parser import parse_resume
from JD_parser import extract_skills_from_JD
from matcher import calculate_skill_match, calculate_ats_score
from feedback import generate_feedback
import google.generativeai as genai

def resume_feedback(resume_text, job_description=""):
    """
    Generate enhanced feedback for a given resume using Google AI Studio (Gemini).

    Args:
        resume_text (str): Extracted text from the uploaded resume.
        job_description (str, optional): Job description to tailor feedback.

    Returns:
        str: Markdown-formatted feedback from the LLM.
    """
    # Configure API key (use provided key or env var)
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = "AIzaSyCvMKBCIKMe97yMlfH6mNCAVZKGEPTPvGw"
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        # Minimal graceful fallback using rule-based feedback
        return (
            "### LLM Feedback (fallback)\n"
            "The AI feedback service is not configured. Set `GOOGLE_API_KEY`.\n\n"
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
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
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
            "### LLM Feedback (fallback)\n"
            f"There was an issue generating AI feedback: {e}\n\n"
            + ("- " + "\n- ".join(fallback) if fallback else "Please try again later.")
        )


# Load skills database using a path relative to this file
base_dir = os.path.dirname(__file__)
skills_path = os.path.join(base_dir, 'data', 'skills_list.json')
with open(skills_path, 'r', encoding='utf-8') as f:
    skills_db = json.load(f)

st.title("📄 Resume Scorer & ATS Feedback Generator")

# Upload resume file
resume_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=['pdf', 'docx'])

# Paste Job Description text
job_description = st.text_area("Paste Job Description Here")

if st.button("Generate ATS Score and Feedback"):
    if not resume_file or not job_description:
        st.error("Please upload a resume and paste the job description!")
    else:
        # Parse resume
        resume_data = parse_resume(resume_file, skills_db)
        
        # Check if resume is scanned
        if resume_data.get('is_scanned', False):
            st.header("⚠️ Scanned Resume Detected")
            st.error("This appears to be a scanned resume or image-based PDF. Please upload a text-based resume for accurate ATS scoring.")
            st.write("📊 ATS Score: **0 / 100** (Cannot process scanned documents)")
            st.write("💡 **Recommendation**: Convert your resume to a text-based PDF or DOCX format for better ATS compatibility.")
        else:
            # Parse job description
            job_skills = extract_skills_from_JD(job_description, skills_db)
            
            # Calculate matching score
            skill_match = calculate_skill_match(resume_data['skills'], job_skills)
            ats_score = calculate_ats_score(skill_match, bool(resume_data['contact_info']['email']))
            
            # Generate feedback
            feedback = generate_feedback(skill_match, resume_data['skills'], job_skills)
            # Generate LLM feedback (with spinner)
            with st.spinner("Generating AI feedback..."):
                llm_feedback_md = resume_feedback(resume_data.get('text', ''), job_description)
            
            # Display results
            st.header("✅ ATS Score")
            st.write(f"📊 ATS Score: **{ats_score:.2f} / 100**")
            
            st.header("🛠 Extracted Resume Info")
            st.write("📧 Contact Info:", resume_data['contact_info'])
            st.write("📝 Extracted Skills:", resume_data['skills'])
            
            st.header("🎯 Feedback")
            if feedback:
                for f in feedback:
                    st.write(f"- {f}")
            else:
                st.write("Your resume looks great! 👍")

            st.header("💬 LLM Feedback")
            if llm_feedback_md:
                st.markdown(llm_feedback_md)
