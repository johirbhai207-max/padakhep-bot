import streamlit as st
import google.generativeai as genai
import os
import time

# ১. এপিআই কি সেটিংস
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Secrets-এ 'GEMINI_API_KEY' পাওয়া যায়নি।")
    st.stop()

# ২. ফাইল আপলোড এবং প্রসেসিং ফাংশন
def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    # ফাইল প্রসেস হওয়া পর্যন্ত অপেক্ষা করা
    while file.state.name == "PROCESSING":
        time.sleep(2)
        file = genai.get_file(file.name)
    return file

@st.cache_resource
def prepare_knowledge_base():
    files_to_use = []
    knowledge_dir = "knowledge"
    if os.path.exists(knowledge_dir):
        for f in os.listdir(knowledge_dir):
            if f.lower().endswith(".pdf"):
                file_path = os.path.join(knowledge_dir, f)
                # গুগল এপিআই-তে ফাইল আপলোড করা
                gemini_file = upload_to_gemini(file_path, mime_type="application/pdf")
                files_to_use.append(gemini_file)
    return files_to_use

# ফাইলগুলো রেডি করা
uploaded_files = prepare_knowledge_base()

# ৩. ইউজার ইন্টারফেস
st.set_page_config(page_title="পদক্ষেপ মিত্র", page_icon="🤖")
st.title("🤖 পদক্ষেপ মিত্র (Official Assistant)")

if not uploaded_files:
    st.warning("আপনার 'knowledge' ফোল্ডারে কোনো পিডিএফ পাওয়া যায়নি।")

# ৪. চ্যাট ইন্টারফেস
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("গাইডলাইন সম্পর্কে প্রশ্ন করুন..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # মডেল তৈরি (Gemini 1.5 Flash সবচেয়ে ভালো পিডিএফ বুঝতে পারে)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction="তুমি 'পদক্ষেপ মানবিক উন্নয়ন কেন্দ্র'-এর একজন বিশেষজ্ঞ। তোমার কাছে দেওয়া ফাইলগুলো খুব সাবধানে পড়ো। বিশেষ করে টাকার অংক এবং সার্ভিস চার্জের চার্টগুলো দেখে নির্ভুল উত্তর দাও। যদি কোনো তথ্য ফাইলে না থাকে, তবে হাবিজাবি উত্তর না দিয়ে সরাসরি বলো যে তথ্যটি ফাইলে নেই।"
            )
            
            # ফাইল এবং প্রম্পট একসাথে পাঠানো
            content = uploaded_files + [prompt]
            response = model.generate_content(content)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error("দুঃখিত, সমস্যা হয়েছে।")
            st.code(str(e))
