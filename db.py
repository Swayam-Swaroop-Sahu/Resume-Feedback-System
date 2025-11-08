# db.py
import os
import json
import sqlite3
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "app.db")


def get_conn():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # Resume table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS resumes(
        resume_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_text   TEXT NOT NULL,
        extracted_skills_json TEXT,
        contact_email TEXT,
        contact_phone TEXT,
        created_at    TEXT NOT NULL
    );
    """)

    # JD table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS job_descriptions(
        jd_id         INTEGER PRIMARY KEY AUTOINCREMENT,
        jd_text       TEXT NOT NULL,
        required_skills_json TEXT,
        created_at    TEXT NOT NULL
    );
    """)

    # Match scoring table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS matches(
        match_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id     INTEGER NOT NULL,
        jd_id         INTEGER NOT NULL,
        skill_score   REAL NOT NULL,
        format_score  REAL NOT NULL,
        final_ats_score REAL NOT NULL,
        missing_skills_json TEXT,
        feedback_text TEXT,
        created_at    TEXT NOT NULL,
        FOREIGN KEY(resume_id) REFERENCES resumes(resume_id) ON DELETE CASCADE,
        FOREIGN KEY(jd_id)     REFERENCES job_descriptions(jd_id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()


def insert_resume(resume_text: str, skills: list, contact_email: str, contact_phone: str) -> int:
    """
    Store the parsed resume text, skills, and extracted contact info.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO resumes(resume_text, extracted_skills_json, contact_email, contact_phone, created_at)
        VALUES (?, ?, ?, ?, ?);
    """, (
        resume_text,
        json.dumps(skills or []),
        contact_email,
        contact_phone,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def insert_jd(jd_text: str, required_skills: dict) -> int:
    """
    Store the job description text and extracted weighted skills.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO job_descriptions(jd_text, required_skills_json, created_at)
        VALUES (?, ?, ?);
    """, (
        jd_text,
        json.dumps(required_skills or {}),
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    jdid = cur.lastrowid
    conn.close()
    return jdid


def insert_match(resume_id: int, jd_id: int, skill_score: float, format_score: float,
                 final_ats_score: float, missing_skills: list, feedback_text: str) -> int:
    """
    Store one scoring evaluation event.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO matches(resume_id, jd_id, skill_score, format_score, final_ats_score,
                            missing_skills_json, feedback_text, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        resume_id,
        jd_id,
        skill_score,
        format_score,
        final_ats_score,
        json.dumps(missing_skills or []),
        feedback_text or "",
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    mid = cur.lastrowid
    conn.close()
    return mid


def fetch_recent_matches(limit: int = 20):
    """
    Fetch the latest ATS evaluations, joining resume + JD metadata.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.match_id, m.created_at, m.final_ats_score,
               r.resume_id, r.contact_email, r.contact_phone,
               j.jd_id
        FROM matches m
        JOIN resumes r ON r.resume_id = m.resume_id
        JOIN job_descriptions j ON j.jd_id = m.jd_id
        ORDER BY m.match_id DESC
        LIMIT ?;
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows
