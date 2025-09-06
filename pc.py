import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import requests
from io import BytesIO
from gtts import gTTS
import base64
import tempfile

# ------------------ UI Setup ------------------
st.set_page_config(page_title="TechSpark PC Build Assistant", layout="wide")

st.markdown("""
    <style>
    body {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stApp {
        max-width: 900px;
        margin: auto;
        padding: 1rem 2rem;
        background: #161b22dd;
        border-radius: 10px;
        box-shadow: 0 0 20px #00ffc3;
    }
    h1, h2 {
        color: #00ffc3;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .user-msg {
        background-color: #00ffc3aa;
        color: black;
        padding: 8px 12px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 80%;
        align-self: flex-end;
    }
    .bot-msg {
        background-color: #222b33;
        padding: 8px 12px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 80%;
        color: #00ffc3;
        align-self: flex-start;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ PDF Load ------------------
@st.cache_data
def load_pdf_from_url(pdf_url):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        pdf_file = BytesIO(response.content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    else:
        return ""

# Gemini setup
api_key = "AIzaSyBoGkf3vaZuMWmegTLM8lmVpvvoSOFYLYU"  # 🔑 replace with your Gemini API Key
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# PDF with PC info
pdf_url = "https://drive.google.com/uc?export=download&id=1wbSL6iBTGQDIM-FJSA6X8KfS-KUOToiD"
brochure_text = load_pdf_from_url(pdf_url)

# ------------------ App Title ------------------
st.title("💻 TECHSPARK WORLD PC BUILD ASSISTANT")

st.markdown("""
Ask me about **PC builds, components, and recommendations**  
👉 I will answer **first in text, then speak format ** 😎
""")

# ------------------ Chat History ------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f'<div class="user-msg">{msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg">{msg}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ------------------ User Input ------------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Ask your PC build question here:")
    submit = st.form_submit_button("Send")

if submit and user_input.strip():
    # Save user question
    st.session_state.chat_history.append(("user", user_input))

    # Prepare prompt
    prompt = f"""
You are a professional PC Build Assistant.

Use the following brochure content to answer user questions clearly and accurately.

--- Brochure Content Start ---
{brochure_text[:12000]}
--- Brochure Content End ---

User Question: {user_input}
"""

    try:
        response = model.generate_content(prompt)
        answer = response.text.strip()
    except Exception as e:
        answer = f"❌ Error: {e}"

    # 1️⃣ Add bot answer to chat (text shown first)
    st.session_state.chat_history.append(("bot", answer))

    # 2️⃣ Show text first
    st.markdown(f'<div class="bot-msg">{answer}</div>', unsafe_allow_html=True)

    # 3️⃣ Then voice autoplay
    if answer:
        tts = gTTS(text=answer, lang="en")  # Tamil use panna "ta"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            audio_bytes = open(tmp_file.name, "rb").read()
            b64 = base64.b64encode(audio_bytes).decode()
            md = f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
            st.markdown(md, unsafe_allow_html=True)
