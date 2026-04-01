import streamlit as st
import google.generativeai as genai
import time

# এপিআই কনফিগারেশন
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("API Key পাওয়া যায়নি।")
    st.stop()

# ৩. কোটা সেভ করার জন্য রেসপন্স ফাংশন
def generate_safe_response(model, content):
    max_retries = 3
    for i in range(max_retries):
        try:
            return model.generate_content(content)
        except Exception as e:
            if "429" in str(e):
                st.warning(f"কোটা শেষ হয়েছে। {15*(i+1)} সেকেন্ড অপেক্ষা করছি...")
                time.sleep(15 * (i+1)) # একটু অপেক্ষা করে আবার চেষ্টা করবে
            else:
                raise e
    return None
