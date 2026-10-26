import streamlit as st
import engine

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Skill Gap & Job Fit Analyzer",
    page_icon="🎯",
    layout="wide",
)

# ─────────────────────────────────────────────
# SESSION STATE DEFAULTS
# ─────────────────────────────────────────────
if "results"       not in st.session_state: st.session_state.results       = None
if "chat_history"  not in st.session_state: st.session_state.chat_history  = []
if "messages"      not in st.session_state: st.session_state.messages      = []
if "analyzed"      not in st.session_state: st.session_state.analyzed      = False

# ─────────────────────────────────────────────
# SIDEBAR — resume upload + instructions
# ─────────────────────────────────────────────
with st.sidebar:
    st.title("🎯 Job Fit Analyzer")
    st.markdown("---")

    uploaded_pdf = st.file_uploader(
        "Upload your Resume (PDF)",
        type=["pdf"],
        help="Your resume will be parsed and compared against the job description.",
    )

    if uploaded_pdf:
        st.success(f"✅ {uploaded_pdf.name} uploaded")
    else:
        st.info("Upload a PDF resume to get started.")

    st.markdown("---")
    st.markdown("**How it works**")
    st.markdown(
        "1. Upload your resume PDF\n"
        "2. Paste the job description\n"
        "3. Click **Analyze**\n"
        "4. Ask follow-up questions below"
    )
    st.markdown("---")
    st.caption("Powered by SBERT · Gemini · Streamlit")

# ─────────────────────────────────────────────
# MAIN — header + JD input
# ─────────────────────────────────────────────
st.title("Skill Gap & Job Fit Analyzer")
st.markdown(
    "Paste a Job Description below and upload your resume to get an AI-powered "
    "fit score, skill gap breakdown, and personalized career coaching."
)

job_desc = st.text_area(
    "Job Description",
    height=220,
    placeholder=(
        "Paste the full job description here...\n\n"
        "e.g. We are looking for a Data Engineer with experience in Python, "
        "PySpark, Azure Databricks, SQL, and Airflow..."
    ),
)

analyze_btn = st.button(
    "🔍 Analyze",
    type="primary",
    disabled=not (uploaded_pdf and job_desc.strip()),
    use_container_width=False,
)

# ─────────────────────────────────────────────
# ANALYSIS — run on button click
# ─────────────────────────────────────────────
if analyze_btn:
    with st.spinner("Running analysis..."):
        results = engine.run_analysis(uploaded_pdf, job_desc.strip())

    # Store in session so chat can access it later
    st.session_state.results      = results
    st.session_state.chat_history = []
    st.session_state.messages     = []
    st.session_state.analyzed     = True

# ─────────────────────────────────────────────
# RESULTS DISPLAY
# ─────────────────────────────────────────────
if st.session_state.analyzed and st.session_state.results:
    r = st.session_state.results
    score    = r["score"]
    category = r["category"]
    matched  = r["matched"]
    missing  = r["missing"]

    st.markdown("---")

    # ── Score + category ────────────────────
    score_col, cat_col, spacer = st.columns([1, 1.4, 3])

    with score_col:
        color = "#1D9E75" if score >= 80 else "#BA7517" if score >= 50 else "#E24B4A"
        st.markdown(
            f"""
            <div style="
                background:#f8f9fa; border-radius:12px; padding:20px 16px;
                text-align:center; border: 1px solid #e0e0e0;
            ">
                <div style="font-size:13px; color:#666; margin-bottom:6px;">Fit Score</div>
                <div style="font-size:42px; font-weight:700; color:{color}; line-height:1;">
                    {score}%
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cat_col:
        badge_colors = {
            "Strong Fit":    ("#d4edda", "#155724", "#c3e6cb"),
            "Potential Fit": ("#fff3cd", "#856404", "#ffeeba"),
            "Low Fit":       ("#f8d7da", "#721c24", "#f5c6cb"),
        }
        bg, fg, border = badge_colors[category]
        st.markdown(
            f"""
            <div style="
                background:{bg}; border-radius:12px; padding:20px 16px;
                text-align:center; border: 1px solid {border};
            ">
                <div style="font-size:13px; color:{fg}; margin-bottom:6px;">Category</div>
                <div style="font-size:24px; font-weight:600; color:{fg}; line-height:1.2;">
                    {category}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Score bar ───────────────────────────
    st.markdown(
        f"""
        <div style="background:#e9ecef; border-radius:6px; height:10px; margin-bottom:20px;">
            <div style="
                width:{score}%; background:{color};
                height:10px; border-radius:6px; transition: width 1s;
            "></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Matched / Missing skills ─────────────
    col_match, col_miss = st.columns(2)

    with col_match:
        st.markdown(f"**✅ Matched Skills** &nbsp; `{len(matched)}`")
        if matched:
            badges = " ".join(
                f'<span style="background:#d4edda;color:#155724;padding:3px 10px;'
                f'border-radius:999px;font-size:12px;margin:3px;display:inline-block;">'
                f'{s}</span>'
                for s in matched
            )
            st.markdown(badges, unsafe_allow_html=True)
        else:
            st.caption("No matching skills detected from keyword scan.")

    with col_miss:
        st.markdown(f"**❌ Missing Skills** &nbsp; `{len(missing)}`")
        if missing:
            badges = " ".join(
                f'<span style="background:#f8d7da;color:#721c24;padding:3px 10px;'
                f'border-radius:999px;font-size:12px;margin:3px;display:inline-block;">'
                f'{s}</span>'
                for s in missing
            )
            st.markdown(badges, unsafe_allow_html=True)
        else:
            st.caption("No skill gaps detected — great coverage!")

    # ─────────────────────────────────────────
    # CHAT INTERFACE
    # ─────────────────────────────────────────
    st.markdown("---")
    st.subheader("💬 Ask the Career Coach")
    st.caption(
        "Ask anything about your results — score explanation, learning roadmap, "
        "project ideas, certifications, or how to improve."
    )

    # Render existing messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask a follow-up question about your analysis...")

    if user_input:
        # Show user message immediately
        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Build context for the LLM
        context_data = {
            **st.session_state.results,
            "chat_history": st.session_state.chat_history,
        }

        # Get and show AI response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                reply = engine.get_ai_guidance(user_input, context_data)
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

        # Update chat history for LLM memory
        st.session_state.chat_history.append({"role": "user",  "content": user_input})
        st.session_state.chat_history.append({"role": "model", "content": reply})

# ─────────────────────────────────────────────
# PRE-ANALYSIS PLACEHOLDER
# ─────────────────────────────────────────────
elif not st.session_state.analyzed:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "⬆️ Upload your resume in the sidebar and paste a job description above, "
        "then click **Analyze** to get started.",
        icon="💡",
    )