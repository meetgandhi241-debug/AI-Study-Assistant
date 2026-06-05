Replace your current app.py with this structure

import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import pandas as pd

# ==========================
# GEMINI API KEY
# ==========================
API_KEY = "YOUR_API_KEY_HERE"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ==========================
# PAGE SETTINGS
# ==========================
st.set_page_config(
    page_title="AI Study Assistant Pro",
    page_icon="📚",
    layout="wide"
)

# ==========================
# SESSION STATE
# ==========================
if "history" not in st.session_state:
    st.session_state.history = []

if "question_count" not in st.session_state:
    st.session_state.question_count = 0

if "physics_count" not in st.session_state:
    st.session_state.physics_count = 0

if "chemistry_count" not in st.session_state:
    st.session_state.chemistry_count = 0

if "math_count" not in st.session_state:
    st.session_state.math_count = 0

# ==========================
# SIDEBAR
# ==========================
with st.sidebar:

    st.header("📚 AI Study Assistant Pro")

    st.metric(
        "Questions Asked",
        st.session_state.question_count
    )

    st.write("---")

    st.subheader("📊 Subject Usage")

    st.write(
        f"Physics: {st.session_state.physics_count}"
    )

    st.write(
        f"Chemistry: {st.session_state.chemistry_count}"
    )

    st.write(
        f"Mathematics: {st.session_state.math_count}"
    )

    counts = {
        "Physics": st.session_state.physics_count,
        "Chemistry": st.session_state.chemistry_count,
        "Mathematics": st.session_state.math_count
    }

    weakest = min(counts, key=counts.get)

    st.warning(
        f"Weakest Subject: {weakest}"
    )

# ==========================
# TITLE
# ==========================
st.title("📚 AI Study Assistant Pro")

st.write(
    """
    Ask Questions
    Generate MCQs
    Upload PDFs
    Summarize Notes
    Generate Study Plans
    """
)

# ==========================
# CLEAR CHAT
# ==========================
if st.button("🗑 Clear Chat"):

    st.session_state.history = []
    st.session_state.question_count = 0

    st.rerun()

# ==========================
# SUBJECT
# ==========================
subject = st.selectbox(
    "Choose Subject",
    [
        "Physics",
        "Chemistry",
        "Mathematics"
    ]
)

# ==========================
# PDF UPLOAD
# ==========================
uploaded_pdf = st.file_uploader(
    "📄 Upload PDF Notes",
    type=["pdf"]
)

pdf_text = ""

if uploaded_pdf:

    try:

        reader = PdfReader(uploaded_pdf)

        for page in reader.pages:

            text = page.extract_text()

            if text:
                pdf_text += text

        st.success(
            "PDF Uploaded Successfully"
        )

    except Exception as e:

        st.error(str(e))

# ==========================
# QUESTION BOX
# ==========================
question = st.text_area(
    "Enter your question or topic"
)

# ==========================
# BUTTONS
# ==========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    answer_btn = st.button(
        "Get Answer"
    )

with col2:
    mcq_btn = st.button(
        "Generate MCQs"
    )

with col3:
    summary_btn = st.button(
        "PDF Summary"
    )

with col4:
    planner_btn = st.button(
        "Study Planner"
    )

# ==========================
# ANSWER MODE
# ==========================
if answer_btn:

    if question:

        prompt = f"""
You are an expert {subject} teacher.

Use PDF notes if available.

PDF Notes:
{pdf_text}

Question:
{question}

Explain simply.
"""

        try:

            with st.spinner(
                "Thinking..."
            ):

                response = model.generate_content(
                    prompt
                )

            st.subheader(
                "Answer"
            )

            st.write(
                response.text
            )

            st.session_state.history.append(
                {
                    "type":"Answer",
                    "question":question,
                    "response":response.text
                }
            )

            st.session_state.question_count += 1

            if subject == "Physics":
                st.session_state.physics_count += 1
            elif subject == "Chemistry":
                st.session_state.chemistry_count += 1
            else:
                st.session_state.math_count += 1

        except Exception:

            st.error(
                "AI service unavailable or quota exceeded."
            )

# ==========================
# MCQ MODE
# ==========================
if mcq_btn:

    if question:

        prompt = f"""
Generate 5 MCQs.

Subject:
{subject}

Topic:
{question}

Provide answers too.
"""

        try:

            response = model.generate_content(
                prompt
            )

            st.subheader(
                "MCQ Quiz"
            )

            st.write(
                response.text
            )

        except Exception:

            st.error(
                "AI service unavailable or quota exceeded."
            )

# ==========================
# PDF SUMMARY
# ==========================
if summary_btn:

    if pdf_text:

        prompt = f"""
Summarize:

{pdf_text}

Give:
1. Key Concepts
2. Formulas
3. Revision Notes
"""

        try:

            response = model.generate_content(
                prompt
            )

            st.subheader(
                "PDF Summary"
            )

            st.write(
                response.text
            )

            st.download_button(
                "Download Summary",
                response.text,
                "summary.txt"
            )

        except Exception:

            st.error(
                "AI service unavailable."
            )

# ==========================
# STUDY PLANNER
# ==========================
st.write("---")

exam_date = st.date_input(
    "Exam Date"
)

if planner_btn:

    prompt = f"""
Create a study plan.

Subject:
{subject}

Exam Date:
{exam_date}

Student Level:
Class 12
"""

    try:

        response = model.generate_content(
            prompt
        )

        st.subheader(
            "Study Plan"
        )

        st.write(
            response.text
        )

    except Exception:

        st.error(
            "AI service unavailable."
        )

# ==========================
# CHARTS
# ==========================
st.write("---")

st.subheader(
    "Progress Dashboard"
)

chart_data = pd.DataFrame(
    {
        "Questions":[
            st.session_state.physics_count,
            st.session_state.chemistry_count,
            st.session_state.math_count
        ]
    },
    index=[
        "Physics",
        "Chemistry",
        "Mathematics"
    ]
)

st.bar_chart(chart_data)

# ==========================
# CHAT HISTORY
# ==========================
st.write("---")

st.subheader(
    "Chat History"
)

if len(
    st.session_state.history
) == 0:

    st.info(
        "No history yet."
    )

else:

    for item in reversed(
        st.session_state.history
    ):

        st.markdown(
            f"### {item['type']}"
        )

        st.write(
            item["question"]
        )

        st.write(
            item["response"]
        )

        st.write("---")
