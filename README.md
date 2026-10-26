# Skill Gap & Job Fit Analyzer

A Python web application that analyzes how well a resume matches a job description. It combines semantic similarity scoring, keyword-based skill-gap detection, and an AI career-coach chatbot to help users understand their job fit and identify skills to improve.

## Features

- **Resume parsing:** Extracts text from an uploaded PDF resume using `pdfplumber`.
- **Job-fit score:** Uses Sentence Transformers (`all-MiniLM-L6-v2`) to create embeddings for the resume and job description, then calculates cosine similarity.
- **Skill-gap analysis:** Scans the job description and resume against a master IT skills list to identify matched and missing skills.
- **Fit category:** Labels the result as `Strong Fit`, `Potential Fit`, or `Low Fit`.
- **AI career guidance:** Uses the Google Gemini API to answer follow-up questions using the analysis context.
- **Interactive web interface:** Built with Streamlit, including result cards, skill badges, and a chat interface.

## Technology Stack

| Component | Technology |
|---|---|
| Web interface | Streamlit |
| Semantic similarity | Sentence Transformers — `all-MiniLM-L6-v2` |
| PDF text extraction | pdfplumber |
| AI chatbot | Google Gemini API |
| Environment variables | python-dotenv |
| Language | Python |

## How It Works

1. Upload a resume in PDF format and paste a job description.
2. The app extracts text from the resume.
3. Sentence Transformers generates embeddings for the resume and job description; cosine similarity is used to calculate the fit score.
4. The skill-gap engine scans the job description first, then checks which required skills appear in the resume.
5. The app displays the fit score, fit category, matched skills, and missing skills.
6. Ask follow-up questions in the career-coach chat interface for additional guidance.

### Fit categories

| Fit score | Category |
|---|---|
| 80% or higher | Strong Fit |
| 50%–79% | Potential Fit |
| Below 50% | Low Fit |

**Important:** The fit score is a semantic-similarity indicator, not a guarantee of interview selection or job performance. Skill-gap results are based on keyword matching and may not capture every equivalent skill or context.

## Project Structure

```text
skill-gap-job-fit-analyzer/
├── app.py              # Streamlit user interface
├── engine.py           # Resume parsing, scoring, skill analysis, and AI guidance
├── requirements.txt    # Python dependencies
├── .env                # Local API key; do not commit this file
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-github-username>/skill-gap-job-fit-analyzer.git
cd skill-gap-job-fit-analyzer
```

### 2. Create and activate a virtual environment

**Windows (Git Bash):**

```bash
python -m venv venv
source venv/Scripts/activate
```

If activation fails in your shell, you can run the environment's Python directly using `venv/Scripts/python`.

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root and add your API key:

```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
```

Get an API key through Google AI Studio. Keep the real key private and never commit `.env` to GitHub.

### 5. Run the application

```bash
streamlit run app.py
```

Streamlit will print a local URL in the terminal, usually `http://localhost:8501`.

## Dependencies

The project uses these packages (as listed in the project reference):

- `streamlit`
- `sentence-transformers`
- `pdfplumber`
- `python-dotenv`
- `google-generativeai`

Install them with `pip install -r requirements.txt`.

## Security Notes

- Never upload `.env`, API keys, credentials, private resumes, or other personal data to a public repository.
- Check `.gitignore` before the first commit. At minimum, exclude `.env`, virtual environments, Python cache files, and `.pyc` files.
- If an API key was ever committed, removing the file in a later commit is not enough: revoke/rotate the key and remove it from Git history if necessary.

## Future Improvements

- Add automated tests for scoring and skill-gap detection.
- Cache or optimize model loading for faster repeated use.
- Expand skill matching to recognize synonyms and related technologies.
- Add clearer explanations of score limitations and skill-match evidence.

## Academic Project

Developed as a final-year project to explore resume analysis, semantic text similarity, skill-gap identification, and AI-assisted career guidance.
