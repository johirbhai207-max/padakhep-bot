import streamlit as st
import google.generativeai as genai

# ১. কনফিগারেশন: আপনার দেওয়া এপিআই কি
API_KEY = "AIzaSyAnrjqKli8VoFuLLxeX7bFF3bLayOB3gd8" 

# ২. ফোল্ডার ডাটা
FOLDER_DATA = {
    "অগ্রসর": "https://drive.google.com/drive/folders/1UJ5pVxSF25TpbgaHAT6BS7fv47ewSlpw",
    "আর্থিক ও প্রশাসনিক অনিয়ম": "https://drive.google.com/drive/folders/1thXY_XJwHFEh6qsuezQeZ714SHCb2VwF",
    "ঋণ অনুমোদন- ToA": "https://drive.google.com/drive/folders/1WVfFil5LCwM_1C4NRUEt6tF3GKzaN5di",
    "টর- TOR": "https://drive.google.com/drive/folders/1XNO4lHSKuRKCVfkgTFJO7REZa8Otr3EB",
    "টিএ ডিএ": "https://drive.google.com/drive/folders/11XHxpbzG10zBhBDHlL9tpCA5XWoM65o3",
    "লীপ- LEAP": "https://drive.google.com/drive/folders/1OdJQRU75A8o-CvjEXKjv4q9Ok8lUvVIO",
    "সকত- MWF": "https://drive.google.com/drive/folders/1nhN83f2k_7KwEiTivzyh024WZoTOZ_Lb",
    "সার্ভিস চার্জ রিবেট": "https://drive.google.com/drive/folders/197sBN3AmwesaY3pDizn9-YctxoCl3_VQ"
}

# ৩. ইউজার ইন্টারফেস
st.set_page_config(page_title="পদক্ষেপ মিত্র", page_icon="🤖")
st.title("🤖 পদক্ষেপ মিত্র (Padakhep Mitra)")

# সাইডবার
selected_keyword = st.sidebar.selectbox("বিভাগ নির্বাচন করুন:", list(FOLDER_DATA.keys()))
folder_link = FOLDER_DATA[selected_keyword]
st.sidebar.markdown(f"📁 [ফোল্ডার লিংক]({folder_link})")

# এপিআই সেটআপ (Error Fix)
try:
    genai.configure(api_key=API_KEY)
    # মডেলের নাম 'models/gemini-1.5-flash-latest' দিয়ে ট্রাই করা হচ্ছে যা সাধারণত ৪০৪ এরর দেয় না
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Configuration Error: {e}")

# চ্যাট হিস্ট্রি
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": f"নমস্কার! আমি আপনাকে **{selected_keyword}** গাইডলাইন নিয়ে সাহায্য করতে পারি।"})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ৪. প্রশ্ন ও উত্তর
if prompt := st.chat_input("আপনার প্রশ্ন লিখুন..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # সিস্টেম মেসেজ
            system_msg = f"তুমি পদক্ষেপ মানবিক উন্নয়ন কেন্দ্রের ডিজিটাল বিশেষজ্ঞ। '{selected_keyword}' বিষয়ে পদক্ষেপের গাইডলাইন অনুযায়ী উত্তর দাও। শেষে এই লিংকটি দাও: {folder_link}"
            
            # জেনারেশন
            response = model.generate_content(f"{system_msg}\n\nUser Question: {prompt}")
            
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.warning("এআই কোনো উত্তর দিতে পারছে না।")
        except Exception as e:
            st.error("⚠️ একটি কারিগরি সমস্যা হয়েছে।")
            st.code(f"New Error Details: {str(e)}")
