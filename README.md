# Resume-Feedback-System

ATS Score Tracker & Resume Feedback System Using NLP, Explainable AI, and Weighted Skill Matching

## Overview

The Resume Feedback System is a Streamlit-based application designed to analyze resumes against specific Job Descriptions (JD). It performs weighted skill matching, ATS-style formatting checks, provides AI-powered feedback, stores evaluation history, and highlights skill gaps. This project demonstrates practical applications of NLP, explainability, database integration, and full-stack development.

## Authors / Contributors

- **Swayam Swaroop Sahu** (Database logic, backend integration, explainability layer, UI improvements)
- **Ayush Saraf** (NLP parsing module, JD-resume extraction logic, weighted keyword matching)
- **Ankush** (User interface components, display formatting, user interaction flows)
- **Akash** (Frontend layout, input handling, data visualization elements)

## Features

- Resume parsing (skills, contact info, text extraction)
- JD keyword and frequency extraction
- Weighted skill match scoring
- Format and completeness scoring
- Final ATS score calculation
- AI-powered improvement suggestions (Gemini API)
- Missing skill detection
- Relevance-sorted skill tables
- SQLite database storage for:
  - Resume submissions
  - Job descriptions
  - Match scoring history
- Score history viewer inside the app
- Scanned resume detection
- Professionally themed frontend (light SaaS theme)

## Tech Stack

- **Python 3.x**
- **Streamlit** (frontend)
- **SQLite** (database)
- **spaCy / NLP** (resume extraction)
- **Google Gemini API** (feedback generation)
- **Pandas** (tabular analysis)

## Project Structure
Resume-Feedback-System/
│
├── app.py # Main Streamlit application
├── db.py # Database schema + operations
├── matcher.py # ATS scoring logic
├── resume_parser.py # Resume text + skill extraction
├── JD_parser.py # JD keyword extraction
├── feedback.py # Rule-based fallback feedback
├── data/
│ ├── skills_list.json # Master skills vocabulary
│ └── app.db # SQLite history database (auto-created)
├── requirements.txt # Dependencies
└── .streamlit/
└── secrets.toml # API key (ignored by git)

text

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Swayam-Swaroop-Sahu/Resume-Feedback-System.git
cd Resume-Feedback-System
2. Create a Virtual Environment (recommended)
bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
3. Install Dependencies
bash
pip install -r requirements.txt
python -m spacy download en_core_web_md
4. Configure API Key
Copy the template file:

bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
Edit .streamlit/secrets.toml and add your Google AI API key:

toml
GOOGLE_API_KEY = "your_actual_api_key_here"
5. Run the Application
bash
streamlit run app.py
The application will open in your browser at:

text
http://localhost:8501
How It Works (Simplified Pipeline)
User uploads resume (PDF/DOCX)

User pastes Job Description text

System extracts:

Skills

Contact info

Resume raw text

JD is processed and skill weights are assigned based on frequency

Weighted skill matching occurs

Formatting completeness is evaluated

Final ATS score is computed

Missing critical skills are highlighted

Gemini AI generates improvement feedback

Results are stored in the database

Database Storage
The following data is stored automatically:

Resume text

Contact email and phone

Extracted skills

JD skill weighting

Final ATS score

Missing skills

AI feedback text

Timestamp

The database file is located at:

text
./data/app.db
Resetting Score History
Delete the database file:

bash
cd data
del app.db       # Windows
rm app.db        # macOS / Linux
It will recreate automatically on next run.

Security Notice
secrets.toml is git-ignored

Never commit API keys to version control

API usage costs are tied to your account

Future Enhancements (Planned)
PDF download of feedback

Skill recommendation using embeddings

Resume formatting suggestions with examples

JD-to-resume similarity visualization

Authentication roles

Exportable evaluation reports

License
This project is published under the MIT License. You are free to use, modify, and distribute the software with attribution.

Acknowledgements
This project combines coursework theory with practical industry-aligned implementation across:

NLP

Explainable AI

ATS pipeline reasoning

Scoring strategy design

Database management

UI/UX modeling