import streamlit as st
import json
import os
from resume_parser import parse_resume
from JD_parser import extract_skills_from_JD
from matcher import calculate_skill_match, calculate_ats_score
from feedback import generate_feedback

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
