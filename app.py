import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# ১. এপিআই কি সেটিংস (Streamlit Secrets থেকে আসবে)
try:
    if "GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=API_KEY)
    else:
        st.error("Secrets-এ 'GEMINI_API_KEY' পাওয়া যায়নি।")
        st.stop()
except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

# ২. নলেজ ফোল্ডার থেকে পিডিএফ ডাটা পড়া
@st.cache_resource
def load_padakhep_data():
    combined_text = ""
    path = "knowledge" 
    if os.path.exists(path) and os.path.isdir(path):
        files = os.listdir(path)
        for f in files:
            if f.lower().endswith(".pdf"):
                try:
                    pdf_path = os.path.join(path, f)
                    reader = PdfReader(pdf_path)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            combined_text += text + "\n"
                except Exception:
                    continue
    return combined_text

# ডাটা লোড করা
full_knowledge = load_padakhep_data()

# ৩. স্মার্ট মডেল সিলেকশন (এটিই ৪-০-৪ এরর সমাধান করবে)
@st.cache_resource
def get_working_model():
    try:
        # আপনার এপিআই কি দিয়ে কোন মডেলগুলো এভেইলএবল তা দেখা
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # অগ্রাধিকার ভিত্তিতে মডেল চেক করা
        target_models = [
            'models/gemini-1.5-flash-latest', 
            'models/gemini-1.5-flash', 
            'models/gemini-pro'
        ]
        
        for tm in target_models:
            if tm in models:
                return genai.GenerativeModel(
                    model_name=tm,
                    system_instruction=f"তুমি পদক্ষেপ মানবিক উন্নয়ন কেন্দ্রের বিশেষজ্ঞ। নিচের গাইডলাইন থেকে উত্তর দাও:\n\n{full_knowledge[:30000]}"
                )
        
        # যদি কোনোটিই না মেলে তবে প্রথমটি নেওয়া
        return genai.GenerativeModel(model_name=models[0], system_instruction="পদক্ষেপ বিশেষজ্ঞ হিসেবে উত্তর দাও।")
    except Exception as e:
        st.error(f"মডেল লোড করতে সমস্যা: {e}")
        return None

model = get_working_model()

# ৪. ইউজার ইন্টারফেস
st.set_page_config(page_title="পদক্ষেপ মিত্র", page_icon="🤖")
st.title("🤖 পদক্ষেপ মিত্র (Padakhep Mitra)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ৫. চ্যাট প্রসেসিং
if prompt := st.chat_input("প্রশ্ন করুন..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        if model:
            try:
                # সরাসরি মডেলকে কল করা হচ্ছে
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("দুঃখিত, উত্তর তৈরি করা যায়নি।")
                st.code(str(e))
        else:
            st.error("সিস্টেম কনফিগারেশনে সমস্যা হয়েছে।")
