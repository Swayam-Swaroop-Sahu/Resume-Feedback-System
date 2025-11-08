# 🎯 Resume Feedback System  
### *ATS Score Tracker & Resume Feedback System using NLP, Explainable AI, and Weighted Skill Matching*

---

### 🧠 Overview  
The **Resume Feedback System** is an intelligent, explainable hiring-assist platform that evaluates resumes against job descriptions using **Natural Language Processing (NLP)**, **Explainable AI**, and **Database Management Systems (DBMS)**.  
It analyzes resumes for **ATS compliance**, detects missing skills, evaluates formatting, and generates **AI-powered personalized feedback** to help candidates optimize their resumes for specific roles.

This project bridges recruiter evaluation logic with candidate clarity, providing **transparent, data-driven, and actionable insights**.

---

## 👥 Team Members

| Name | Role | Key Contributions |
|------|------|--------------------|
| **Swayam Swaroop Sahu** | Backend, Database, Explainability | Designed DB schema, backend logic, integrated explainability layer, refined UI |
| **Ayush Saraf** | NLP & Matching Module | Built JD–Resume parser, keyword extractor, and weighted skill matcher |
| **Ankush** | UI Design & Frontend | Developed user interface layout, component structuring, and design consistency |
| **Akash** | Frontend Development | Implemented data visualization and front-end polish |

---

## 🚀 Features

- Resume parsing (skills, contact info, text extraction)
- Job Description analysis via weighted NLP matching  
- Skill match scoring with explainable weights  
- ATS format evaluation for readability & structure  
- Final ATS score combining multiple weighted metrics  
- AI feedback (via **Google Gemini API**)  
- Transparent skill visualization (matched/missing)  
- SQLite database storage for persistent analysis  
- History view for previous evaluations  
- Professionally themed **SaaS-grade UI**  

---

## 🧩 Tech Stack

| Layer | Tools / Technologies |
|-------|----------------------|
| **Frontend** | Streamlit |
| **Backend / Logic** | Python |
| **Database** | SQLite |
| **AI / NLP** | spaCy, Google Gemini API |
| **Data Processing** | Pandas, JSON |
| **Explainability** | Weighted skill transparency & ATS breakdown |

---

## **System Architecture**

```
Resume (PDF/DOCX)
        │
        ▼
Resume Parser ──► Extracted Text, Skills, Contact Info
        │
        ▼
Job Description Parser ──► Weighted Skill Extraction
        │
        ▼
Weighted Skill Matcher ──► Match %, Missing Skills
        │
        ▼
Format Scoring ──► Layout & Structure Evaluation
        │
        ▼
ATS Scoring ──► Final Composite Score
        │
        ▼
AI Feedback (Gemini) ──► Personalized Suggestions
        │
        ▼
SQLite Storage ──► Resumes, JDs, Matches, Feedback
        │
        ▼
Streamlit Visualization ──► Score Dashboard & History
```

---

## **Project Structure**

```
Resume-Feedback-System/
│
├── app.py                  # Main Streamlit application
├── db.py                   # Database schema and CRUD operations
├── matcher.py              # Scoring and weighting logic
├── resume_parser.py        # Resume skill and contact extraction
├── JD_parser.py            # JD keyword and skill analysis
├── feedback.py             # AI + fallback feedback system
│
├── data/
│   ├── skills_list.json    # Reference list of known skills
│   └── app.db              # SQLite database (auto-generated)
│
├── requirements.txt        # Project dependencies
└── .streamlit/
    └── secrets.toml        # Google Gemini API key config (gitignored)
```

---

## **Installation & Setup**

### 1. Clone the Repository

```bash
git clone https://github.com/Swayam-Swaroop-Sahu/Resume-Feedback-System.git
cd Resume-Feedback-System
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate        # For Windows
source venv/bin/activate     # For macOS / Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_md
```

### 4. Configure API Key

Copy the template and add your API key:

```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Then edit `.streamlit/secrets.toml`:

```toml
GOOGLE_API_KEY = "your_actual_api_key_here"
```

### 5. Run the Application

```bash
streamlit run app.py
```

App will be available at:

```
http://localhost:8501
```

---

## **Usage Guide**

1. Upload your **resume (PDF or DOCX)**
2. Paste your **job description (JD)**
3. Click **Generate ATS Score & Feedback**
4. View:

   * ATS Score Breakdown
   * Skill Match Analysis
   * AI-Powered Feedback
   * Missing Skill Suggestions
5. Access **Recent Score History** to review past evaluations

---

## **Database & Persistence**

All user evaluations are stored locally in:

```
./data/app.db
```

**Database Tables**

| Table              | Description                                  |
| ------------------ | -------------------------------------------- |
| `resumes`          | Stores resume text, skills, and contact info |
| `job_descriptions` | Stores JD text and extracted skills          |
| `matches`          | Stores scores, feedback, and timestamps      |

**Clear Previous History**

```bash
cd data
del app.db       # (Windows)
rm app.db        # (macOS / Linux)
```

The database will auto-recreate on next run.

---

## **Security Notes**

* `.streamlit/secrets.toml` is excluded from Git tracking.
* Never share or commit API keys.
* All AI calls and resume processing happen locally.

---

## **Future Enhancements**

* Resume formatting analysis
* Graphical skill-gap visualization
* Resume–JD similarity charts
* PDF report export
* User login and tracking
* Cloud deployment (AWS / GCP)

---

## **License**

This project is released under the **MIT License**.
You are free to use, modify, and distribute it with proper attribution.

---

## **Academic Context & Acknowledgements**

This project integrates:

| Area                     | Focus                                         |
| ------------------------ | --------------------------------------------- |
| **DBMS Concepts**        | Structured storage & relational schema design |
| **AI & NLP**             | Resume and JD parsing, skill extraction       |
| **Explainability**       | Transparent ATS scoring & skill reasoning     |
| **Software Engineering** | Modular design and UI/UX implementation       |

Developed collaboratively by:
**Swayam Swaroop Sahu**, **Ayush Saraf**, **Ankush**, and **Akash**
at **VIT Vellore (2025)**

---

