import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# ==========================
# GEMINI API KEY
# ==========================
API_KEY = "PASTE_YOUR_API_KEY_HERE"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ==========================
# PAGE SETTINGS
# ==========================
st.set_page_config(
    page_title="AI Study Assistant",
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

# ==========================
# SIDEBAR
# ==========================
with st.sidebar:
    st.header("📚 AI Study Assistant")
    st.write("Version 4.0")

    st.write("### Features")
    st.write("✅ Ask Questions")
    st.write("✅ Generate MCQs")
    st.write("✅ Chat History")
    st.write("✅ Question Counter")
    st.write("✅ PDF Upload")

    st.write("---")
    st.write(f"📊 Questions Asked: {st.session_state.question_count}")

# ==========================
# MAIN PAGE
# ==========================
st.title("📚 AI Study Assistant")

st.write(
    "Ask questions, generate MCQs and learn Physics, Chemistry and Mathematics."
)

# Clear Chat
if st.button("🗑️ Clear Chat"):
    st.session_state.history = []
    st.session_state.question_count = 0
    st.rerun()

# Subject
subject = st.selectbox(
    "Choose Subject",
    ["Physics", "Chemistry", "Mathematics"]
)

# PDF Upload
uploaded_pdf = st.file_uploader(
    "📄 Upload PDF Notes",
    type=["pdf"]
)

pdf_text = ""

if uploaded_pdf:
    reader = PdfReader(uploaded_pdf)

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pdf_text += text

    st.success("✅ PDF Loaded Successfully")

# Question Box
question = st.text_area("Enter your question or topic")

# Buttons
col1, col2 = st.columns(2)

with col1:
    answer_btn = st.button("Get Answer")

with col2:
    mcq_btn = st.button("📝 Generate 5 MCQs")

# ==========================
# ANSWER MODE
# ==========================
if answer_btn:

    if question:

        prompt = f"""
You are an expert {subject} teacher.

Use the PDF notes if available.

PDF Notes:
{pdf_text}

Question:
{question}

Explain in simple language for a Class 12 student.
"""

        with st.spinner("🤔 Thinking..."):
            response = model.generate_content(prompt)

        st.subheader("✅ Answer")
        st.write(response.text)

        st.session_state.history.append(
            {
                "type": "Answer",
                "question": question,
                "response": response.text
            }
        )

        st.session_state.question_count += 1

    else:
        st.warning("Please enter a question.")

# ==========================
# MCQ MODE
# ==========================
if mcq_btn:

    if question:

        prompt = f"""
Generate 5 multiple-choice questions.

Subject:
{subject}

PDF Notes:
{pdf_text}

Topic:
{question}

Format:

1. Question

A)
B)
C)
D)

Answer:
"""

        with st.spinner("📝 Generating MCQs..."):
            response = model.generate_content(prompt)

        st.subheader("📝 MCQ Quiz")
        st.write(response.text)

        st.session_state.history.append(
            {
                "type": "MCQ",
                "question": question,
                "response": response.text
            }
        )

        st.session_state.question_count += 1

    else:
        st.warning("Please enter a topic.")

# ==========================
# CHAT HISTORY
# ==========================
st.write("---")
st.subheader("📜 Chat History")

if len(st.session_state.history) == 0:
    st.info("No history yet.")

else:

    for item in reversed(st.session_state.history):

        if item["type"] == "MCQ":
            st.markdown("### 📝 MCQ")
        else:
            st.markdown("### ❓ Question")

        st.markdown(
            f"**Topic / Question:** {item['question']}"
        )

        st.write(item["response"])

        st.write("---")