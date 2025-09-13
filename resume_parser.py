import pdfplumber
import docx
import re
import spacy

nlp = spacy.load('en_core_web_sm')

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_contact_info(text):
    email = re.findall(r'\S+@\S+', text)
    phone = re.findall(r'\+?\d[\d -]{8,12}\d', text)
    return {"email": email[0] if email else None,
            "phone": phone[0] if phone else None}

def extract_skills(text, skills_db):
    extracted_skills = []
    for skill in skills_db:
        if re.search(rf"\b{skill}\b", text, re.IGNORECASE):
            extracted_skills.append(skill)
    return list(set(extracted_skills))

def parse_resume(file_path, skills_db):
    if file_path.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format.")

    contact_info = extract_contact_info(text)
    skills = extract_skills(text, skills_db)
    
    return {
        "text" : text,
        "contact_info" : contact_info,
        "skills" : skills
    }