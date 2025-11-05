# Resume-Feedback-System
ATS Score Tracker & Resume Feedback System Using NLP and Explainable AI

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_md
```

### 2. Configure API Key
1. Copy the template file: `cp .streamlit/secrets.toml.template .streamlit/secrets.toml`
2. Edit `.streamlit/secrets.toml` and add your Google AI API key:
```toml
GOOGLE_API_KEY = "your_actual_api_key_here"
```

### 3. Run the Application
```bash
streamlit run app.py
```

## Security Note
The `secrets.toml` file is gitignored to prevent accidental API key exposure. Never commit your actual API keys to version control.
