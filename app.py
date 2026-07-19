import streamlit as st
import pdfplumber
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-flash-latest")

st.set_page_config(page_title="AI Study Assistant", page_icon="📚", layout="centered")

st.title("📚 AI Study Assistant")
st.write("Upload your notes as a PDF, get a quick summary, and ask questions about them.")

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_file is not None:
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    st.session_state.pdf_text = text
    st.success(f"PDF loaded successfully! ({len(pdf.pages)} pages)")

    if st.button("Generate Summary"):
        with st.spinner("Generating summary..."):
            response = model.generate_content(
                f"Summarize these notes in clear, concise bullet points, using simple language:\n\n{st.session_state.pdf_text[:8000]}"
            )
            st.session_state.summary = response.text

if st.session_state.summary:
    st.subheader("📝 Summary")
    st.write(st.session_state.summary)

st.divider()

st.subheader("❓ Ask a Question")
question = st.text_input("Ask anything related to your notes:")

if st.button("Get Answer") and question:
    if st.session_state.pdf_text == "":
        st.warning("Please upload a PDF first!")
    else:
        with st.spinner("Thinking..."):
            response = model.generate_content(
                f"Based on these notes, answer the following question:\n\nNotes:\n{st.session_state.pdf_text[:8000]}\n\nQuestion: {question}"
            )
            st.subheader("💡 Answer")
            st.write(response.text)