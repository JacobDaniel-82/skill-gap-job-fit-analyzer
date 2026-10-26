import re
import os
import pdfplumber
import google.generativeai as genai
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# STARTUP — env + model + LLM
# ─────────────────────────────────────────────
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

_embed_model = SentenceTransformer("all-MiniLM-L6-v2")
_llm         = genai.GenerativeModel("gemini-2.5-flash")

# ─────────────────────────────────────────────
# SKILL LISTS
# ─────────────────────────────────────────────
_DATA_AI_SKILLS = [
    "python", "sql", "r", "scala",
    "pandas", "numpy", "matplotlib", "seaborn", "plotly",
    "scikit-learn", "sklearn", "xgboost", "lightgbm",
    "tensorflow", "pytorch", "keras",
    "pyspark", "spark", "hadoop", "hive", "kafka", "flink",
    "airflow", "dbt", "prefect", "dagster", "luigi",
    "azure", "aws", "gcp", "databricks", "snowflake",
    "bigquery", "redshift", "synapse", "data factory",
    "power bi", "tableau", "looker", "metabase",
    "delta lake", "iceberg", "parquet",
    "mongodb", "cassandra", "postgres", "postgresql", "mysql",
    "machine learning", "deep learning", "nlp", "llm", "mlops",
    "etl", "elt", "data pipeline", "medallion architecture",
    "star schema", "dimensional modeling", "data modeling",
]

_SOFTWARE_DEV_SKILLS = [
    "java", "javascript", "typescript", "c++", "c#", "go", "rust", "php",
    "react", "angular", "vue", "node.js", "next.js",
    "fastapi", "flask", "django", "spring boot",
    "docker", "kubernetes", "terraform", "ansible",
    "git", "github", "gitlab", "ci/cd",
    "rest api", "graphql", "grpc", "microservices",
    "linux", "bash", "shell scripting",
    "redis", "elasticsearch", "rabbitmq",
]

IT_SKILLS = list(dict.fromkeys(_DATA_AI_SKILLS + _SOFTWARE_DEV_SKILLS))

# ─────────────────────────────────────────────
# PDF PARSING
# ─────────────────────────────────────────────
def get_resume_text(file_path: str) -> str:
    """
    Extracts and returns all text from a PDF as a single string.
    Accepts a file path string or a file-like object (e.g. Streamlit UploadedFile).
    """
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

# ─────────────────────────────────────────────
# FIT SCORE
# ─────────────────────────────────────────────
def calculate_fit_score(resume_text: str, job_description: str) -> float:
    """
    Returns cosine similarity between resume and JD embeddings as a percentage.
    Range: 0.0 – 100.0
    """
    resume_emb = _embed_model.encode(resume_text, convert_to_tensor=True)
    jd_emb     = _embed_model.encode(job_description, convert_to_tensor=True)
    similarity = util.cos_sim(resume_emb, jd_emb)
    return round(float(similarity[0][0]) * 100, 2)

# ─────────────────────────────────────────────
# SKILL GAP ANALYSIS
# ─────────────────────────────────────────────
def _find_mentions(text: str) -> list:
    """Returns all IT skills found in the given text via whole-word matching."""
    text_lower = text.lower()
    return [
        skill for skill in IT_SKILLS
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower)
    ]

def identify_skill_gaps(resume_text: str, job_description: str) -> tuple[list, list]:
    """
    Scans the JD for required skills, then checks which are absent from the resume.

    Returns:
        matched_skills  — skills present in both JD and resume
        missing_skills  — skills the JD requires but resume lacks
    """
    required  = set(_find_mentions(job_description))
    in_resume = set(_find_mentions(resume_text))
    matched = sorted(required & in_resume)
    missing = sorted(required - in_resume)
    return matched, missing

# ─────────────────────────────────────────────
# FIT CATEGORY
# ─────────────────────────────────────────────
def get_fit_category(score: float) -> str:
    """Maps a numeric score to a human-readable fit category."""
    if score >= 80:   return "Strong Fit"
    elif score >= 50: return "Potential Fit"
    else:             return "Low Fit"

# ─────────────────────────────────────────────
# AI GUIDANCE  (LLM-powered)
# ─────────────────────────────────────────────
def get_ai_guidance(question: str, context_data: dict) -> str:
    """
    Sends the user's question + analysis context to Gemini and returns the reply.

    context_data keys expected:
        score         : float  — e.g. 73.5
        matched       : list   — e.g. ["python", "sql"]
        missing       : list   — e.g. ["pyspark", "airflow"]
        resume_text   : str    — full resume content
        job_desc      : str    — full job description
        chat_history  : list   — [{"role": "user"/"model", "content": "..."}]
                                  pass [] for a fresh session
    """
    score    = context_data.get("score", 0)
    matched  = context_data.get("matched", [])
    missing  = context_data.get("missing", [])
    resume   = context_data.get("resume_text", "")
    job_desc = context_data.get("job_desc", "")
    history  = context_data.get("chat_history", [])

    system_prompt = (
        "You are a career mentor for IT students. "
        "Use the provided analysis to answer the user's question accurately. "
        "Focus on Data & AI or Software Dev. "
        "Be encouraging, specific, and concise (3–5 sentences unless more detail is asked). "
        "Do not answer questions outside career and tech scope."
    )

    analysis_block = f"""
── CANDIDATE ANALYSIS ──
Fit Score      : {score}%  ({get_fit_category(score)})
Matched Skills : {", ".join(matched) if matched else "None detected"}
Missing Skills : {", ".join(missing) if missing else "None detected"}

Job Description:
{job_desc.strip()}

Resume:
{resume.strip()}
────────────────────────
""".strip()

    history_block = ""
    for turn in history:
        role  = "Student"  if turn["role"] == "user"  else "Mentor"
        history_block += f"{role}: {turn['content']}\n"

    full_prompt = (
        f"{system_prompt}\n\n"
        f"{analysis_block}\n\n"
        f"{history_block}"
        f"Student: {question}\n"
        f"Mentor:"
    )

    response = _llm.generate_content(full_prompt)
    return response.text.strip()

# ─────────────────────────────────────────────
# FULL ANALYSIS  (single call for app.py)
# ─────────────────────────────────────────────
def run_analysis(resume_source, job_desc: str) -> dict:
    """
    Master function that app.py calls with one line.

    Args:
        resume_source : file path string OR Streamlit UploadedFile object
        job_desc      : raw job description string

    Returns a dict with all results ready to render in the UI:
        score, category, matched, missing, resume_text, job_desc
    """
    resume_text      = get_resume_text(resume_source)
    score            = calculate_fit_score(resume_text, job_desc)
    matched, missing = identify_skill_gaps(resume_text, job_desc)
    category         = get_fit_category(score)

    return {
        "score":       score,
        "category":    category,
        "matched":     matched,
        "missing":     missing,
        "resume_text": resume_text,
        "job_desc":    job_desc,
    }