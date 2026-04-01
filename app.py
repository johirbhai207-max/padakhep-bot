import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# ১. এপিআই কি সেটিংস
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Secrets-এ 'GEMINI_API_KEY' পাওয়া যায়নি।")
    st.stop()

# ২. অনেকগুলো ফাইল থেকে স্মার্টলি ডাটা পড়া
@st.cache_resource
def load_massive_knowledge():
    combined_data = {}
    path = "knowledge"
    if os.path.exists(path):
        for f in os.listdir(path):
            if f.lower().endswith(".pdf"):
                try:
                    pdf_reader = PdfReader(os.path.join(path, f))
                    text = ""
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text
                    # ফাইলের নাম অনুযায়ী ডাটা ভাগ করে রাখা
                    combined_data[f] = text
                except:
                    continue
    return combined_data

all_docs = load_massive_knowledge()

# ৩. ইন্টারফেস সাজানো
st.set_page_config(page_title="পদক্ষেপ মিত্র - প্রো", layout="wide")
st.title("🤖 পদক্ষেপ মিত্র (Advanced Assistant)")
st.sidebar.info(f"মোট ফাইল লোড হয়েছে: {len(all_docs)}টি")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ৪. স্মার্ট সার্চ এবং রেসপন্স
if prompt := st.chat_input("আপনার প্রশ্নটি লিখুন..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # সব ফাইল থেকে প্রাসঙ্গিক অংশ খোঁজা (সহজ ফিল্টারিং)
            # এটি আপনার কোটা বাঁচাবে কারণ আমরা শুধু প্রয়োজনীয় অংশ পাঠাচ্ছি
            relevant_context = ""
            for doc_name, doc_text in all_docs.items():
                # যদি প্রশ্নের কোনো শব্দ ফাইলের ভেতরে থাকে, তবেই সেটি কনটেক্সটে যাবে
                keywords = prompt.split()
                if any(word in doc_text for word in keywords):
                    relevant_context += f"\n--- {doc_name} ---\n{doc_text[:5000]}" # প্রতি ফাইল থেকে নির্দিষ্ট অংশ

            full_instruction = f"""
            তুমি পদক্ষেপ মানবিক উন্নয়ন কেন্দ্রের ডিজিটাল বিশেষজ্ঞ। 
            নিচের গাইডলাইনগুলো থেকে উত্তর দাও। যদি উত্তর না পাও, তবে বানিয়ে কিছু বলবে না।
            
            গাইডলাইন তথ্য:
            {relevant_context[:30000]} 
            
            প্রশ্ন: {prompt}
            """
            
            response = model.generate_content(full_instruction)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("দুঃখিত, তথ্য প্রসেস করতে সমস্যা হচ্ছে। সম্ভবত আপনার আজকের ফ্রি কোটা শেষ।")
