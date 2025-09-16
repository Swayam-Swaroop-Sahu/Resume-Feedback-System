import pdfplumber
import docx
import re
import spacy
import pytesseract
import pdf2image

nlp = spacy.load('en_core_web_sm')

def extract_text_from_pdf(file_or_path):
    text = ""
    try:
        with pdfplumber.open(file_or_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text: 
                    text += page_text + "\n"
    except Exception as e:
        print(f"PDF extraction failed: {e}")
        return ""
    
    # If very little text extracted, try OCR
    if len(text.strip()) < 50:
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(file_or_path)
            ocr_text = ""
            for img in images:
                ocr_text += pytesseract.image_to_string(img) + "\n"
            return ocr_text
        except Exception as e:
            print(f"OCR fallback failed: {e}")
            return text
    
    return text

def extract_text_from_docx(file_or_path):
    doc = docx.Document(file_or_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_contact_info(text):
    email = re.findall(r'\S+@\S+', text)
    phone = re.findall(r'\+?[\s-(]?\d{0,3}[\s-)]?\d[\d-\s]{8,12}\d', text)
    return {"email": email[0] if email else None,
            "phone": phone[0] if phone else None}

def extract_skills(text, skills_db):
    extracted_skills = []
    for skill in skills_db:
        if re.search(rf"\b{skill}\b", text, re.IGNORECASE):
            extracted_skills.append(skill)
    return list(set(extracted_skills))

def parse_resume(file_input, skills_db):
    if hasattr(file_input, 'name'):
        filename = file_input.name.lower()
        try:
            file_input.seek(0)
        except Exception:
            pass
        file_obj_or_path = file_input
    else:
        filename = str(file_input).lower()
        file_obj_or_path = file_input

    if filename.endswith('.pdf'):
        text = extract_text_from_pdf(file_obj_or_path)
    elif filename.endswith('.docx'):
        text = extract_text_from_docx(file_obj_or_path)
    else:
        raise ValueError("Unsupported file format.")

    # Check if resume is parseable (scanned or very little text)
    is_scanned = len(text.strip()) < 50
    
    if is_scanned:
        print("Warning: Resume appears to be scanned or has very little text")
        return {
            "text": text,
            "contact_info": {"email": None, "phone": None},
            "skills": [],
            "is_scanned": True,
            "ats_score": 0
        }
    
    contact_info = extract_contact_info(text)
    skills = extract_skills(text, skills_db)
    
    new_skills_added = []
    for skill in skills:
        if skill not in skills_db:
            skills_db.append(skill)
            new_skills_added.append(skill)
    
    if new_skills_added:
        import json
        import os
        base_dir = os.path.dirname(__file__)
        skills_path = os.path.join(base_dir, 'data', 'skills_list.json')
        with open(skills_path, 'w', encoding='utf-8') as f:
            json.dump(skills_db, f, indent=4)
    
    return {
        "text": text,
        "contact_info": contact_info,
        "skills": skills,
        "is_scanned": False,
        "new_skills_added": new_skills_added
    }