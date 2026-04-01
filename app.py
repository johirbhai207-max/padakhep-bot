import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# ১. এপিআই কি সেটিংস
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Error: Streamlit Secrets-এ API Key সেট করা নেই।")
    st.stop()

# ২. নলেজ ফোল্ডার থেকে ডাটা পড়া
@st.cache_resource
def load_padakhep_data():
    text = ""
    # ফোল্ডারের নাম ছোট হাতের অক্ষরে 'knowledge' নিশ্চিত করুন
    path = "knowledge" 
    if os.path.exists(path):
        files = os.listdir(path)
        for f in files:
            if f.lower().endswith(".pdf"):
                try:
                    pdf_reader = PdfReader(os.path.join(path, f))
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                except Exception as e:
                    st.warning(f"ফাইল {f} পড়তে সমস্যা হয়েছে।")
    return text

full_knowledge = load_padakhep_data()

# ৩. এআই কনফিগারেশন
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=f"তুমি পদক্ষেপ মানবিক উন্নয়ন কেন্দ্রের ডিজিটাল বিশেষজ্ঞ। নিচের গাইডলাইন থেকে উত্তর দাও:\n\n{full_knowledge}"
)

st.title("🤖 পদক্ষেপ মিত্র (Official Assistant)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("প্রশ্ন করুন..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        response = model.generate_content(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
