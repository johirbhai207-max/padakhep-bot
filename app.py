import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# এপিআই সেটআপ
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key খুঁজে পাওয়া যায়নি!")
    st.stop()

# ২৫+ ফাইল থেকে ডাটা পড়া (মেমোরি সেভার মোড)
@st.cache_resource
def load_padakhep_files():
    docs = {}
    if os.path.exists("knowledge"):
        for f in os.listdir("knowledge"):
            if f.endswith(".pdf"):
                try:
                    reader = PdfReader(os.path.join("knowledge", f))
                    # শুধু প্রথম ৫-১০ পাতা পড়বে যাতে কোটা বাঁচে
                    text = ""
                    for i in range(min(len(reader.pages), 10)):
                        text += reader.pages[i].extract_text()
                    docs[f] = text
                except: continue
    return docs

all_docs = load_padakhep_files()

st.title("🤖 পদক্ষেপ মিত্র (Lite Version)")

if prompt := st.chat_input("প্রশ্ন লিখুন..."):
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        # স্মার্ট সার্চ: শুধু প্রাসঙ্গিক ফাইল খুঁজে বের করা
        relevant_text = ""
        for name, content in all_docs.items():
            if any(word in content.lower() for word in prompt.lower().split()):
                relevant_text += f"\nফাইল: {name}\n{content[:2000]}"
        
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(f"গাইডলাইন: {relevant_text[:10000]}\n\nপ্রশ্ন: {prompt}")
            st.markdown(response.text)
        except Exception as e:
            st.error("কোটা শেষ! অনুগ্রহ করে অন্য একটি API Key ব্যবহার করুন।")
