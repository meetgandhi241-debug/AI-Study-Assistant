import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import pandas as pd
import json

# ==========================
# GEMINI API KEY
# ==========================
API_KEY = st.secrets["GEMINI_API_KEY"]

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

if "quiz_items" not in st.session_state:
    st.session_state.quiz_items = []

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = None
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
# ==========================
# MCQ MODE
if mcq_btn:

    if question:

        prompt = f"""
You are an expert {subject} teacher.
Create 5 multiple-choice questions about this topic:
{question}

Return only a JSON array with objects containing:
  question, options, answer
Options should be an object with keys A, B, C, D.
        """
        try:

            response = model.generate_content(
                prompt
            )

            raw = response.text
            raw = raw.replace("```json", "")
            raw = raw.replace("```", "")
            raw = raw.strip()

            try:
                quiz_items = json.loads(raw)
            except Exception:
                quiz_items = None

            if isinstance(quiz_items, list):
                st.session_state.quiz_items = quiz_items
                st.session_state.quiz_score = None
            else:
                st.error("Could not parse MCQs from the model response.")
                st.write(raw)

        except Exception:

            st.error(
                "AI service unavailable or quota exceeded."
            )

# --- MCQ Quiz Section (drop-in replacement) ---
user_answers = {}

quiz_items = st.session_state.get('quiz_items', [])
if not quiz_items:
    st.info("No quiz items available. Generate MCQs first.")
else:
    with st.form("quiz_form"):
        st.write("### Multiple-choice Quiz")
        temp_answers = []
        for i, item in enumerate(quiz_items):
            if isinstance(item, dict):
                question_text = item.get('question', f"Question {i+1}")
                options = item.get('options', []) or []
            else:
                question_text = str(item)
                options = []

            if options:
                selected = st.radio(question_text, options)
            else:
                selected = st.text_input(question_text, value="")

            temp_answers.append(selected)

        submit = st.form_submit_button("Submit Quiz")

    just_submitted = False
    if submit:
        just_submitted = True
        score = 0
        correct_count = 0
        for i, item in enumerate(quiz_items):
            correct = item.get('answer') if isinstance(item, dict) else None
            selected = temp_answers[i] if i < len(temp_answers) else None
            user_answers[i] = selected
            if selected is None or selected == "":
                continue
            if correct is not None and selected == correct:
                score += 1
                correct_count += 1

        st.session_state['quiz_score'] = score

    # Show review only after a submission occurred
    submitted_flag = just_submitted or ('quiz_score' in st.session_state and bool(user_answers))
    if submitted_flag:
        total = len(quiz_items)
        score_display = st.session_state.get('quiz_score', 0)
        st.write(f"**Score:** {score_display} / {total}")
        st.write("### Quiz Review")
        for i, item in enumerate(quiz_items):
            if isinstance(item, dict):
                question_text = item.get('question', f"Question {i+1}")
                correct = item.get('answer')
            else:
                question_text = str(item)
                correct = None

            selected = user_answers.get(i)
            is_correct = (selected == correct) if (correct is not None) else False
            status = "✅ Correct" if is_correct else "❌ Incorrect"
            st.write(f"Q{i+1}. {question_text}")
            st.write(f"- Your answer: {selected}")
            if (correct is not None) and (not is_correct):
                st.write(f"- Correct answer: {correct}")
            st.write(f"- {status}")

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
