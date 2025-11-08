import streamlit as st
import json
import os
import pandas as pd

# DB imports
from db import init_db, insert_resume, insert_jd, insert_match, fetch_recent_matches


# Import heavy modules only when needed
def get_imports():
    from resume_parser import parse_resume
    from JD_parser import extract_skills_from_JD
    from matcher import calculate_weighted_skill_match, calculate_format_score, calculate_ats_score
    from feedback import generate_feedback
    import google.generativeai as genai
    return parse_resume, extract_skills_from_JD, calculate_weighted_skill_match, calculate_format_score, calculate_ats_score, generate_feedback, genai

@st.cache_data
def load_skills_database():
    base_dir = os.path.dirname(__file__)
    try_paths = [
        os.path.join(base_dir, 'data', 'skills_list.json'),
        os.path.join(base_dir, 'data', 'skill_list.json'),
    ]
    for p in try_paths:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                return json.load(f)
    st.error("skills_list.json not found!")
    return []


@st.cache_data
def cached_parse_resume(file_input, skills_db):
    parse_resume, _, _, _, _, _, _ = get_imports()
    return parse_resume(file_input, skills_db)

@st.cache_data
def cached_extract_skills_from_JD(job_description, skills_db):
    _, extract_skills_from_JD, _, _, _, _, _ = get_imports()
    return extract_skills_from_JD(job_description, skills_db)

@st.cache_data
def resume_feedback(resume_text, job_description=""):
    _, _, _, _, _, generate_feedback, genai = get_imports()
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except:
        return "API key missing"

    system_msg = "You are an expert technical recruiter..."
    user_prompt = ("Job Description:\n" + job_description + "\n\n" if job_description else "") + \
                  "Resume Text:\n" + resume_text

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        generation_config={"temperature": 0.3, "max_output_tokens": 800}
    )
    prompt = system_msg + "\n\n" + user_prompt
    response = model.generate_content(prompt)
    return (response.text or "").strip()


# MAIN
skills_db = load_skills_database()
st.title("Resume Scorer & ATS Feedback Generator")

init_db()

st.markdown("<h4 style='text-align:center; opacity:0.8;'>AI + ATS Resume Improvement Engine</h4>", unsafe_allow_html=True)

# --- PREMIUM SAAS THEME (FINAL FIXED VERSION) ---
premium_saas_css = """
<style>
/* Import a premium neutral font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif !important;
}

/* App Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f8faff 0%, #eef2ff 100%);
    background-attachment: fixed;
    color: #2b3445;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e5e9f2;
    padding-top: 1.5rem;
}

/* Headings */
h1 {
    color: #1a2b4d !important;
    font-size: 2.4rem !important;
    font-weight: 700 !important;
    text-align: center;
    margin-bottom: 0.3rem !important;
}

h2, h3, h4 {
    color: #24344d !important;
    font-weight: 600 !important;
}

/* Top tagline */
h4 {
    text-align: center !important;
    color: #67789e !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-size: 0.95rem !important;
    margin-bottom: 2rem;
}

/* Card Container */
.block-container {
    background: #ffffff;
    border-radius: 18px;
    padding: 2.5rem 2.2rem;
    border: 1px solid #eef2fc;
    box-shadow:
        0 2px 6px rgba(0,0,0,0.04),
        0 6px 20px rgba(0,0,0,0.06);
    transition: all 0.25s ease;
    max-width: 900px;
    margin: 2.5rem auto;
}

.block-container:hover {
    box-shadow:
        0 6px 25px rgba(0,0,0,0.08),
        0 12px 35px rgba(0,0,0,0.06);
}

/* Buttons */
.stButton > button {
    background: #4c6ef5 !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 0.9rem 2rem !important;
    border: none !important;
    font-weight: 600 !important;
    box-shadow: 0 3px 10px rgba(76,110,245,0.25) !important;
    transition: all 0.18s ease-in-out !important;
}

.stButton > button:hover {
    background: #4359d0 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(76,110,245,0.32) !important;
}

/* Progress bar */
[data-testid="stProgress"] > div > div > div {
    background: linear-gradient(90deg,#4c6ef5,#7e9dfa) !important;
    border-radius: 4px;
}

/* Metrics */
[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #1a2b4d !important;
}

[data-testid="stMetricLabel"] {
    color: #5f6f95 !important;
}

/* Dataframe */
.stDataFrame {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid #e6eaf6 !important;
    background: white !important;
    box-shadow:
        0 1px 3px rgba(0,0,0,0.04),
        0 6px 16px rgba(0,0,0,0.06);
}

/* Textarea input */
textarea {
    border-radius: 14px !important;
    border: 1.5px solid #d3d9f5 !important;
    background: #ffffff !important;
    padding: 1rem 1.2rem !important;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
    transition: all 0.25s ease;
}

textarea:focus {
    border-color: #4c6ef5 !important;
    box-shadow: 0 0 0 3px rgba(76,110,245,0.18) !important;
    outline: none !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #f9fbff !important;
    border: 2px dashed #b8c5ff;
    border-radius: 14px;
    padding: 1.5rem;
    transition: all 0.25s ease;
}

[data-testid="stFileUploader"]:hover {
    border-color: #4c6ef5 !important;
    background: #eef2ff !important;
    transform: translateY(-1px);
}

/* Success alert */
.stSuccess {
    background: #eafff6 !important;
    border-left: 4px solid #1aa06d !important;
    color: #146c4f !important;
    border-radius: 8px;
}

/* Info alert */
.stInfo {
    background: #eaf4ff !important;
    border-left: 4px solid #4c8df5 !important;
    color: #285fb6 !important;
    border-radius: 8px;
}

/* === EXPANDER ICON FIX (FINAL) === */

/* Hide the keyboard_arrow icons completely */
span[data-testid="st-expander-toggle-icon"] {
    display: none !important;
    visibility: hidden !important;
}

/* Keep header alignment and spacing clean */
.streamlit-expanderHeader {
    white-space: normal !important;
    padding-left: 10px !important;
    padding-right: 10px !important;
    font-weight: 600;
    color: #1a2b4d;
}

/* Hover style for expander header */
.streamlit-expanderHeader:hover {
    background: #f7f9ff !important;
    border-radius: 6px;
    cursor: pointer;
}

/* Smooth transitions for UI elements */
button, textarea, .block-container, [data-testid="stFileUploader"] {
    transition: all .20s ease-in-out;
}

/* Hide footer & menu */
footer, #MainMenu {visibility: hidden;}
</style>
"""

st.markdown(premium_saas_css, unsafe_allow_html=True)

resume_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=['pdf', 'docx'])
job_description = st.text_area("Paste Job Description Here", height=200)

if st.button("Generate ATS Score and Feedback"):
    if not resume_file or not job_description.strip():
        st.error("Please upload a resume and paste the job description!")
    else:
        with st.spinner("Analyzing..."):
            parse_resume, _, calculate_weighted_skill_match, calculate_format_score, calculate_ats_score, generate_feedback, _ = get_imports()
            resume_data = cached_parse_resume(resume_file, skills_db)

            if resume_data.get('is_scanned', False):
                st.error("Scanned resume detected — cannot parse text.")
                st.write("ATS Score: **0 / 100**")

            else:
                job_skill_weights = cached_extract_skills_from_JD(job_description, skills_db)
                resume_skills_set = {skill.lower().strip() for skill in resume_data.get('skills', [])}

                skill_match_score = calculate_weighted_skill_match(resume_skills_set, job_skill_weights)
                format_score = calculate_format_score(resume_data)
                ats_score = calculate_ats_score(skill_match_score, format_score)

                st.header("ATS Score")
                st.metric("Final ATS Score", f"{ats_score:.2f} / 100")

                st.subheader("Score Breakdown")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Skill Match Score", f"{skill_match_score:.1f}%")
                with col2:
                    st.metric("Format Score", f"{format_score:.1f}%")

                st.progress(ats_score / 100)

                # Weighted Skill Analysis
                st.header("Weighted Skill Match Analysis")
                if job_skill_weights:
                    job_skills_normalized = set(job_skill_weights.keys())
                    found_skills = resume_skills_set & job_skills_normalized
                    missing_skills = job_skills_normalized - resume_skills_set

                    rows = []
                    for sk in found_skills:
                        rows.append({"Skill": sk.title(), "Status": "Found", "Weight": job_skill_weights[sk]})
                    for sk in missing_skills:
                        rows.append({"Skill": sk.title(), "Status": "Missing", "Weight": job_skill_weights[sk]})

                    df = pd.DataFrame(rows).sort_values(by=["Weight", "Skill"], ascending=[False, True])
                    st.dataframe(df, use_container_width=True)

                st.header("AI-Powered Feedback")
                with st.spinner("Generating feedback..."):
                    llm_feedback = resume_feedback(resume_data.get('text', ''), job_description)
                st.markdown(llm_feedback)

                # DB Store
                resume_id = insert_resume(
                    resume_data.get('text', ''),
                    resume_data.get('skills', []),
                    resume_data.get('contact_info', {}).get('email', ''),
                    resume_data.get('contact_info', {}).get('phone', '')
                )

                jd_id = insert_jd(job_description, job_skill_weights)

                insert_match(
                    resume_id,
                    jd_id,
                    skill_match_score,
                    format_score,
                    ats_score,
                    list(missing_skills),
                    llm_feedback
                )

                st.success("Data stored successfully!")


# HISTORY
st.header(" Recent Score History")
records = fetch_recent_matches(limit=10)

if records:
    df = pd.DataFrame(records, columns=[
        "Match ID",
        "Timestamp",
        "Final ATS Score",
        "Resume ID",
        "Email",
        "Phone",
        "JD ID"
    ])
    st.dataframe(df, use_container_width=True)
else:
    st.info("No history found yet.")

# Debug
# Debug (no header clipping)
with st.expander("", expanded=False):
    st.markdown("### See Extracted Resume Data")
    if resume_file:
        resume_data = cached_parse_resume(resume_file, skills_db)
        st.json(resume_data.get('contact_info', {}))
        st.json(resume_data.get('skills', []))
    else:
        st.info("Upload a resume to view extracted data.")


# --- CLEAR HISTORY BUTTON ---
import sqlite3
if st.button("Clear Score History"):
    conn = sqlite3.connect("data/app.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM matches;")
    conn.commit()
    conn.close()
    st.success("History cleared. Please refresh the page.")

