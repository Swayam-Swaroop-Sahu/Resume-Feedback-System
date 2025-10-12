import pdfplumber
import docx
import re
import spacy
import pytesseract
import pdf2image
from difflib import SequenceMatcher
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
import warnings
warnings.filterwarnings('ignore')

# Pre-compiled regex patterns for better performance
EMAIL_REGEX = re.compile(r'\S+@\S+')
PHONE_PATTERNS = [
    re.compile(r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'),  # US format
    re.compile(r'\+?[0-9]{1,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}'),  # International
    re.compile(r'\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'),  # US without country code
    re.compile(r'[0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'),  # Simple US format
    re.compile(r'\+?[0-9]{10,15}'),  # Long number format
    re.compile(r'\+?[\s\-\(]?\d{0,3}[\s\-\)]?\d[\d\-\s]{8,12}\d')  # Original pattern as fallback
]
PHONE_NORMALIZE_REGEX = re.compile(r'[\s\-\(\)\.]')  # For removing formatting characters

try:
    nltk.data.find('tokenizers/punkt_tab')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)

try:
    nlp = spacy.load('en_core_web_md')
except OSError:
    try:
        # Fallback to small model if medium is not available
        nlp = spacy.load('en_core_web_sm')
        print("Warning: Using 'en_core_web_sm' model. For better accuracy, install 'en_core_web_md' using: python -m spacy download en_core_web_md")
    except OSError:
        print("Warning: No spaCy model found. Please install one using: python -m spacy download en_core_web_md")
        nlp = None

# lemmatizer will convert all english words to its base form also know as lemma
lemmatizer = WordNetLemmatizer()

# stop words are words like a, an, the,...
stop_words = set(stopwords.words('english'))

def preprocess_text_nlp(text):
    """Advanced NLP preprocessing of text"""
    # Convert to lowercase for uniform processing of text
    text = text.lower()
    
    # Remove extra whitespace and special characters
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s-]', ' ', text)
    
    # Tokenize and lemmatize
    # To tokenize means dividing the sentence into words
    tokens = word_tokenize(text)
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    # Remove stop words
    filtered_tokens = [token for token in lemmatized_tokens if token not in stop_words]
    
    return ' '.join(filtered_tokens)

def detect_resume_sections(text):
    """Use NLP to detect different sections of the resume"""
    if nlp is None:
        return {'skills': [], 'experience': [], 'education': [], 'projects': [], 'certifications': []}
    doc = nlp(text)
    sections = {
        'skills': [],   
        'experience': [],
        'education': [],
        'projects': [],
        'certifications': []
    }
    
    # Section headers and keywords
    section_keywords = {
        'skills': ['skills', 'soft skills','technical skills', 'technologies', 'programming languages', 'tools', 'expertise', 'competencies','ability','abilities','capabilities','area of expertise','core competencies'],
        'experience': ['experience', 'work experience', 'employement history','relevant experience','employment', 'career', 'professional experience', 'work history'],
        'education': ['education', 'academic', 'degree', 'university', 'college', 'school', 'qualification'],
        'projects': ['projects', 'portfolio', 'work samples', 'case studies', 'achievements'],
        'certifications': ['certifications', 'certificates', 'licenses', 'credentials', 'awards']
    }
    
    # Split text into sentences
    sentences = sent_tokenize(text)
    
    for i, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        if nlp is not None:
            doc_sentence = nlp(sentence)
        else:
            doc_sentence = None
        
        # Check for section headers
        for section, keywords in section_keywords.items():
            if any(keyword in sentence_lower for keyword in keywords):
                # Extract content until next section or end
                start_idx = text.find(sentence)
                next_section_start = len(text)
                
                # Find next section
                for j in range(i + 1, len(sentences)):
                    next_sentence = sentences[j].lower()
                    for other_section, other_keywords in section_keywords.items():
                        if other_section != section and any(keyword in next_sentence for keyword in other_keywords):
                            next_section_start = text.find(sentences[j])
                            break
                    if next_section_start < len(text):
                        break
                
                section_content = text[start_idx:next_section_start]
                sections[section].append(section_content)
                break
    
    return sections

def extract_entities_nlp(text):
    """Extract named entities using spaCy"""
    if nlp is None:
        return {'ORG': [], 'PERSON': [], 'GPE': [], 'DATE': [], 'MONEY': [], 'PERCENT': []}
    doc = nlp(text)
    entities = {
        'ORG': [],  # Organizations
        'PERSON': [],  # People
        'GPE': [],  # Geopolitical entities (countries, cities)
        'DATE': [],  # Dates
        'MONEY': [],  # Money amounts
        'PERCENT': []  # Percentages
    }
    
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    
    return entities

def calculate_semantic_similarity(text1, text2):
    """Calculate semantic similarity between two texts using TF-IDF and cosine similarity"""
    if not text1 or not text2:
        return 0.0
    
    # Preprocess texts
    text1_processed = preprocess_text_nlp(text1)
    text2_processed = preprocess_text_nlp(text2)
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform([text1_processed, text2_processed])
    
    # Calculate cosine similarity
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return similarity

def extract_skills_from_context(sections, skills_db):
    """Extract skills with better context using NLP section detection"""
    skills_found = []
    skill_contexts = {}
    
    # Focus on skills section first
    skills_section = ' '.join(sections.get('skills', []))
    if skills_section and nlp is not None:
        # Use NLP to extract noun phrases that might be skills
        doc = nlp(skills_section)
        noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text.split()) <= 3]
        
        for skill in skills_db:
            skill_lower = skill.lower()
            for phrase in noun_phrases:
                if skill_lower in phrase or phrase in skill_lower:
                    skills_found.append(skill)
                    skill_contexts[skill] = 'skills_section'
                    break
    
    # Also check experience section for technical skills
    experience_section = ' '.join(sections.get('experience', []))
    if experience_section and nlp is not None:
        doc = nlp(experience_section)
        # Look for technical terms in experience
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop:
                for skill in skills_db:
                    if skill.lower() in token.text.lower() or token.text.lower() in skill.lower():
                        if skill not in skills_found:
                            skills_found.append(skill)
                            skill_contexts[skill] = 'experience_section'
    
    return skills_found, skill_contexts

def analyze_resume_quality(text, skills_result):
    """
    Advanced NLP-based resume quality analysis
    """
    if nlp is None:
        return {
            'ats_score': 0,
            'text_metrics': {'total_words': 0, 'total_sentences': 0, 'avg_sentence_length': 0, 'avg_word_length': 0},
            'skill_analysis': {'total_skills': 0, 'technical_skills': 0, 'soft_skills': 0, 'high_confidence_skills': 0},
            'section_completeness': {'has_skills': False, 'has_experience': False, 'has_education': False, 'has_projects': False},
            'recommendations': ['Install spaCy model: python -m spacy download en_core_web_sm']
        }
    doc = nlp(text)
    
    # Analyze text structure
    sentences = list(doc.sents)
    words = [token.text for token in doc if not token.is_space and not token.is_punct]
    
    # Calculate readability metrics
    avg_sentence_length = sum(len(sent) for sent in sentences) / len(sentences) if sentences else 0
    avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
    
    # Analyze skill distribution
    skills = skills_result['skills']
    skill_confidence = skills_result['confidence_scores']
    
    technical_skills = [skill for skill, info in skill_confidence.items() 
                       if info.get('category') in ['programming_languages', 'web_technologies', 'tools_frameworks']]
    soft_skills = [skill for skill, info in skill_confidence.items() 
                  if info.get('category') == 'soft_skills']
    
    # Analyze section completeness
    sections = skills_result['sections_detected']
    section_completeness = {
        'has_skills': bool(sections.get('skills')),
        'has_experience': bool(sections.get('experience')),
        'has_education': bool(sections.get('education')),
        'has_projects': bool(sections.get('projects'))
    }
    
    # Calculate ATS score based on multiple factors
    ats_score = 0
    
    # Skills factor (40% of score)
    if len(technical_skills) >= 5:
        ats_score += 40
    elif len(technical_skills) >= 3:
        ats_score += 30
    elif len(technical_skills) >= 1:
        ats_score += 20
    
    # Section completeness (30% of score)
    section_score = sum(section_completeness.values()) * 7.5  # 4 sections * 7.5 = 30
    ats_score += section_score
    
    # Text quality (20% of score)
    if 15 <= avg_sentence_length <= 25:  # Good sentence length
        ats_score += 10
    if 4 <= avg_word_length <= 6:  # Good word length
        ats_score += 10
    
    # High confidence skills (10% of score)
    high_confidence_count = len([s for s in skill_confidence.values() if s.get('confidence', 0) >= 0.8])
    ats_score += min(high_confidence_count * 2, 10)
    
    # Ensure score is between 0 and 100
    ats_score = min(max(ats_score, 0), 100)
    
    return {
        'ats_score': round(ats_score, 1),
        'text_metrics': {
            'total_words': len(words),
            'total_sentences': len(sentences),
            'avg_sentence_length': round(avg_sentence_length, 1),
            'avg_word_length': round(avg_word_length, 1)
        },
        'skill_analysis': {
            'total_skills': len(skills),
            'technical_skills': len(technical_skills),
            'soft_skills': len(soft_skills),
            'high_confidence_skills': len([s for s in skill_confidence.values() if s.get('confidence', 0) >= 0.8])
        },
        'section_completeness': section_completeness,
        'recommendations': generate_recommendations(ats_score, section_completeness, len(technical_skills), len(soft_skills))
    }

def generate_recommendations(ats_score, section_completeness, tech_skills_count, soft_skills_count):
    """Generate personalized recommendations based on analysis"""
    recommendations = []
    
    if ats_score < 60:
        recommendations.append("Consider adding more technical skills to improve ATS compatibility")
    
    if not section_completeness['has_skills']:
        recommendations.append("Add a dedicated skills section to highlight your technical abilities")
    
    if not section_completeness['has_experience']:
        recommendations.append("Include a work experience section with detailed project descriptions")
    
    if not section_completeness['has_projects']:
        recommendations.append("Add a projects section to showcase your practical experience")
    
    if tech_skills_count < 3:
        recommendations.append("Include more programming languages and technical tools")
    
    if soft_skills_count < 2:
        recommendations.append("Add soft skills like communication, leadership, or teamwork")
    
    if ats_score >= 80:
        recommendations.append("Great job! Your resume has strong ATS compatibility")
    
    return recommendations

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
    # Use pre-compiled email regex for better performance
    email = EMAIL_REGEX.findall(text)
    
    # Use pre-compiled phone patterns for better performance
    phones = []
    for pattern in PHONE_PATTERNS:
        matches = pattern.findall(text)
        phones.extend(matches)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_phones = []
    for phone in phones:
        if phone not in seen:
            seen.add(phone)
            unique_phones.append(phone)
    
    # Normalize the phone number by removing common non-digit characters
    phone_number = unique_phones[0] if unique_phones else None
    if phone_number:
        # Remove spaces, hyphens, parentheses, and dots using pre-compiled regex
        phone_number = PHONE_NORMALIZE_REGEX.sub('', phone_number)
        # Remove leading +1 or 1 for US numbers
        if phone_number.startswith('+1'):
            phone_number = phone_number[2:]
        elif phone_number.startswith('1') and len(phone_number) == 11:
            phone_number = phone_number[1:]
        
        # Validate that we have a reasonable phone number (7-15 digits)
        if not (7 <= len(phone_number) <= 15 and phone_number.isdigit()):
            phone_number = None
    
    return {"email": email[0] if email else None,
            "phone": phone_number}

def extract_skills(text, skills_db):
    """
    Advanced NLP-based skill extraction with semantic understanding, context analysis, and intelligent matching
    """
    extracted_skills = []
    skill_confidence = {}
    skill_contexts = {}
    
    # Detect resume sections using NLP
    sections = detect_resume_sections(text)
    
    # Extract named entities
    entities = extract_entities_nlp(text)
    
    # Define skill categories with enhanced NLP understanding
    skill_categories = {
        'programming_languages': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab'],
        'web_technologies': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'express', 'spring', 'laravel'],
        'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'cassandra'],
        'cloud_platforms': ['aws', 'azure', 'gcp', 'google cloud', 'amazon web services', 'microsoft azure'],
        'tools_frameworks': ['docker', 'kubernetes', 'git', 'jenkins', 'terraform', 'ansible', 'pandas', 'numpy', 'tensorflow', 'pytorch'],
        'soft_skills': ['communication', 'leadership', 'teamwork', 'problem solving', 'project management', 'time management']
    }
    
    # Process text with spaCy for advanced NLP analysis
    if nlp is None:
        return {
            'skills': [],
            'confidence_scores': {},
            'skill_contexts': {},
            'total_skills': 0,
            'sections_detected': {'skills': [], 'experience': [], 'education': [], 'projects': [], 'certifications': []},
            'entities': {'ORG': [], 'PERSON': [], 'GPE': [], 'DATE': [], 'MONEY': [], 'PERCENT': []},
            'potential_skills': []
        }
    doc = nlp(text)
    
    # Create a comprehensive text representation for semantic matching
    text_processed = preprocess_text_nlp(text)
    
    # Extract skills using multiple NLP approaches
    for skill in skills_db:
        skill_lower = skill.lower()
        confidence = 0
        match_found = False
        context_info = {}
        
        # 1. Exact word boundary match with POS validation
        exact_matches = []
        for token in doc:
            if token.text.lower() == skill_lower and token.pos_ in ['NOUN', 'PROPN', 'ADJ']:
                exact_matches.append(token)
        
        if exact_matches:
            confidence = 1.0
            match_found = True
            context_info['match_type'] = 'exact_pos_validated'
            
            # Analyze context around the match
            for match_token in exact_matches:
                # Check if it's in a skills section
                if any(skill_lower in section.lower() for section in sections.get('skills', [])):
                    confidence += 0.1
                    context_info['section'] = 'skills'
                
                # Check for skill-related dependencies
                for child in match_token.children:
                    if child.dep_ in ['amod', 'compound'] and child.text.lower() in ['technical', 'programming', 'software', 'web', 'data']:
                        confidence += 0.05
                        context_info['skill_modifier'] = child.text
        
        # 2. Semantic similarity matching using TF-IDF
        if not match_found and len(skill_lower) > 3:
            # Check against noun phrases in the document
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) <= 3:  # Focus on short phrases
                    similarity = calculate_semantic_similarity(skill_lower, chunk.text.lower())
                    if similarity > 0.7:
                        confidence = similarity * 0.9
                        match_found = True
                        context_info['match_type'] = 'semantic_similarity'
                        context_info['matched_phrase'] = chunk.text
                        break
        
        # 3. Fuzzy matching with enhanced context analysis
        if not match_found and len(skill_lower) > 3:
            words = text_processed.split()
            for word in words:
                if len(word) > 3:
                    similarity = SequenceMatcher(None, skill_lower, word).ratio()
                    if similarity > 0.8:
                        confidence = similarity * 0.8
                        match_found = True
                        context_info['match_type'] = 'fuzzy_match'
                        context_info['matched_word'] = word
                        break
        
        # 4. Compound skill matching with dependency parsing
        if not match_found and ' ' in skill_lower:
            skill_words = skill_lower.split()
            # Check if all words appear in the same sentence
            for sent in doc.sents:
                sent_text = sent.text.lower()
                if all(word in sent_text for word in skill_words) and nlp is not None:
                    # Use dependency parsing to check if words are related
                    sent_doc = nlp(sent.text)
                    word_tokens = [token for token in sent_doc if token.text.lower() in skill_words]
                    
                    if len(word_tokens) >= len(skill_words) * 0.8:  # At least 80% of words found
                        confidence = 0.8
                        match_found = True
                        context_info['match_type'] = 'compound_sentence'
                        context_info['sentence'] = sent.text
                        break
        
        # 5. Context-aware validation using section detection
        if match_found:
            # Determine which section the skill was found in
            skill_section = None
            for section_name, section_content in sections.items():
                if any(skill_lower in content.lower() for content in section_content):
                    skill_section = section_name
                    break
            
            if skill_section:
                context_info['section'] = skill_section
                # Boost confidence for skills found in relevant sections
                if skill_section == 'skills':
                    confidence += 0.15
                elif skill_section == 'experience':
                    confidence += 0.1
                elif skill_section == 'projects':
                    confidence += 0.05
            
            # Check for skill-related context words
            skill_context_words = ['proficient', 'experienced', 'skilled', 'expert', 'knowledge', 'familiar', 'competent']
            for token in doc:
                if token.text.lower() in skill_context_words:
                    # Check if this word is near our skill
                    if abs(token.i - len([t for t in doc if t.text.lower() == skill_lower])) < 5:
                        confidence += 0.05
                        context_info['context_word'] = token.text
                        break
        
        # 6. Category-based confidence adjustment
        skill_category = None
        for category, skills_list in skill_categories.items():
            if skill_lower in skills_list:
                skill_category = category
                break
        
        if skill_category:
            confidence += 0.05
            context_info['category'] = skill_category
        
        # 7. Named Entity Recognition validation
        # Check if skill appears as a named entity (organization, product, etc.)
        for ent in doc.ents:
            if skill_lower in ent.text.lower() and ent.label_ in ['ORG', 'PRODUCT']:
                confidence += 0.1
                context_info['ner_label'] = ent.label_
                break
        
        # 8. Final validation and filtering
        if match_found and confidence >= 0.6:
            # Additional validation: check if it's not a common word
            if skill_lower not in stop_words and len(skill_lower) > 2:
                extracted_skills.append(skill)
                skill_confidence[skill] = {
                    'confidence': round(min(confidence, 1.0), 2),
                    'category': skill_category,
                    'context': context_info,
                    'section': context_info.get('section', 'unknown')
                }
                skill_contexts[skill] = context_info
    
    # Sort by confidence score
    extracted_skills.sort(key=lambda x: skill_confidence.get(x, {}).get('confidence', 0), reverse=True)
    
    # Additional NLP-based skill discovery
    # Look for skills mentioned in noun phrases that might not be in our database
    potential_skills = []
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) <= 2 and chunk.text.lower() not in stop_words:
            # Check if this looks like a technical skill
            if any(char in chunk.text for char in ['+', '#', '.', '-']) or \
               any(word in chunk.text.lower() for word in ['js', 'sql', 'api', 'ui', 'ux']):
                potential_skills.append(chunk.text)
    
    return {
        'skills': list(set(extracted_skills)),
        'confidence_scores': skill_confidence,
        'skill_contexts': skill_contexts,
        'total_skills': len(set(extracted_skills)),
        'sections_detected': sections,
        'entities': entities,
        'potential_skills': potential_skills[:10]  # Top 10 potential new skills
    }

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
    skills_result = extract_skills(text, skills_db)
    skills = skills_result['skills']
    skill_confidence = skills_result['confidence_scores']
    skill_contexts = skills_result['skill_contexts']
    sections_detected = skills_result['sections_detected']
    entities = skills_result['entities']
    potential_skills = skills_result['potential_skills']
    
    new_skills_added = []
    for skill in skills:
        if skill not in skills_db:
            skills_db.append(skill)
            new_skills_added.append(skill)
    
    # Perform advanced NLP-based quality analysis
    quality_analysis = analyze_resume_quality(text, skills_result)
    
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
        "skill_confidence": skill_confidence,
        "skill_contexts": skill_contexts,
        "total_skills": skills_result['total_skills'],
        "sections_detected": sections_detected,
        "entities": entities,
        "potential_skills": potential_skills,
        "is_scanned": False,
        "new_skills_added": new_skills_added,
        "quality_analysis": quality_analysis,
        "nlp_analysis": {
            "sections_found": len([s for s in sections_detected.values() if s]),
            "entities_found": sum(len(ents) for ents in entities.values()),
            "high_confidence_skills": len([s for s in skill_confidence.values() if s.get('confidence', 0) >= 0.8]),
            "skills_by_section": {
                section: [skill for skill, info in skill_confidence.items() 
                         if info.get('section') == section] 
                for section in ['skills', 'experience', 'projects', 'education']
            }
        }
    }