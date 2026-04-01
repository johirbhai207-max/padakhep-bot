import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# ১. এপিআই কি সেটিংস (Secrets থেকে)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Error: Streamlit Secrets-এ API Key পাওয়া যায়নি।")
    st.stop()

# ২. গিটহাবের ফোল্ডার থেকে পিডিএফ পড়ার ফাংশন
@st.cache_resource # এটি একবার ফাইলগুলো পড়লে বারবার পড়বে না, ফলে অ্যাপ দ্রুত কাজ করবে
def load_all_guidelines():
    combined_text = ""
    knowledge_dir = "knowledge" # আপনার গিটহাব ফোল্ডারের নাম
    
    if os.path.exists(knowledge_dir):
        for filename in os.listdir(knowledge_dir):
            if filename.endswith(".pdf"):
                file_path = os.path.join(knowledge_dir, filename)
                reader = PdfReader(file_path)
                for page in reader.pages:
                    combined_text += page.extract_text()
    return combined_text

# ৩. গাইডলাইন ডাটা লোড করা
guideline_knowledge = load_all_guidelines()

# ৪. সিস্টেম ইন্সট্রাকশন তৈরি (এআই-কে স্থায়ীভাবে শেখানো)
SYSTEM_INSTRUCTION = f"""
তুমি 'পদক্ষেপ মানবিক উন্নয়ন কেন্দ্র'-এর একজন ডিজিটাল গাইডলাইন বিশেষজ্ঞ। 
তোমার কাছে নিচের গাইডলাইনগুলোর সম্পূর্ণ জ্ঞান আছে। 
সব সময় এই তথ্যের ভিত্তিতে উত্তর দেবে। তথ্য না থাকলে বিনয়ের সাথে বলবে যে গাইডলাইনে নেই।

অফিসিয়াল গাইডলাইন ডাটা:
{guideline_knowledge}
"""

# ৫. ইউজার ইন্টারফেস
st.set_page_config(page_title="পদক্ষেপ মিত্র - অফিসিয়াল", page_icon="🤖")
st.title("🤖 পদক্ষেপ মিত্র (Guideline Expert)")
st.info("আমি আপনার আপলোড করা সব গাইডলাইন ফাইল থেকে উত্তর দিতে সক্ষম।")

# চ্যাট মডেল সেটআপ
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

# চ্যাট হিস্ট্রি
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ইউজারের প্রশ্ন গ্রহণ
if prompt := st.chat_input("গাইডলাইন সম্পর্কে জিজ্ঞাসা করুন..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # এআই রেসপন্স জেনারেট করা
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("দুঃখিত, উত্তর দিতে সমস্যা হয়েছে।")
            st.code(str(e))
