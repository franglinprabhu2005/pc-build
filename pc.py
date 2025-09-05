import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import requests
from io import BytesIO

# Page setup
st.set_page_config(page_title="TechSpark PC Build Assistant", layout="wide")

# Background and styles for PC build vibe + 3D model container
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
    .chat-history {
        max-height: 300px;
        overflow-y: auto;
        padding: 10px;
        background: #010409;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #00ffc3;
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
    .input-container {
        margin-top: 10px;
        display: flex;
        gap: 10px;
    }
    input[type="text"] {
        flex-grow: 1;
        padding: 10px;
        border-radius: 15px;
        border: 1px solid #00ffc3;
        background: #010409;
        color: #c9d1d9;
        font-size: 16px;
    }
    button {
        background-color: #00ffc3;
        border: none;
        padding: 10px 20px;
        border-radius: 15px;
        font-weight: bold;
        cursor: pointer;
        color: black;
        font-size: 16px;
    }
    button:hover {
        background-color: #00cca3;
    }
    /* 3D model container */
    .model-container {
        width: 100%;
        max-width: 600px;
        margin: 20px auto;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 0 20px #00ffc3;
    }
    </style>
""", unsafe_allow_html=True)

# Load PDF text function (cache)
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
        st.error("❌ Failed to load PDF from URL.")
        return ""

# Gemini API setup
api_key = "AIzaSyBoGkf3vaZuMWmegTLM8lmVpvvoSOFYLYU"
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# Use your brochure PDF URL for PC build info
pdf_url = "https://drive.google.com/uc?export=download&id=1wbSL6iBTGQDIM-FJSA6X8KfS-KUOToiD"
brochure_text = load_pdf_from_url(pdf_url)

# Title
st.title("💻 TechSpark PC Build Assistant")

st.markdown("""
Welcome to the TechSpark PC Build Assistant!  
Ask me about PC builds, components, and recommendations based on our brochure content.
""")

# 3D Model Embed (example: cool rotating PC case)
st.markdown("""
<div class="model-container">
  <model-viewer src="https://cdn.shopify.com/s/files/1/0251/7221/4406/files/PC_Case.glb?v=1647045024"  
                alt="Rotating PC Case"  
                auto-rotate camera-controls background-color="#010409"  
                style="width:100%; height:400px;">
  </model-viewer>
</div>
<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
""", unsafe_allow_html=True)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Show chat messages
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f'<div class="user-msg">{msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg">{msg}</div>', unsafe_allow_html=True)

# Input + send button
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Ask your PC build question here:")
    submit = st.form_submit_button("Send")

if submit and user_input.strip():
    st.session_state.chat_history.append(("user", user_input))

    # Update: Send up to 12000 characters (not just 3000)
    prompt = f"""
You are a professional PC Build Assistant.

Use the following brochure content to answer user questions clearly and accurately.
If the user asks about specific types of builds (like gaming, billing, bank, office, etc.), provide answers from the corresponding section.

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

    st.session_state.chat_history.append(("bot", answer))

    # ✅ Use st.rerun() instead of deprecated experimental_rerun
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
