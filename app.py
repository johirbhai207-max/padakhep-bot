import streamlit as st
import google.generativeai as genai

# ১. কনফিগারেশন: আপনার দেওয়া এপিআই কি (API Key)
API_KEY = "AIzaSyAnrjqKli8VoFuLLxeX7bFF3bLayOB3gd8" 

# ২. কিওয়ার্ড এবং পদক্ষেপের ফোল্ডার ডাটা
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

# ৩. ইউজার ইন্টারফেস ডিজাইন
st.set_page_config(page_title="পদক্ষেপ মিত্র", page_icon="🤖")

st.title("🤖 পদক্ষেপ মিত্র (Padakhep Mitra)")
st.markdown("### পদক্ষেপ মানবিক উন্নয়ন কেন্দ্র - গাইডলাইন সহায়িকা")

# সাইডবার সেটিংস
st.sidebar.header("বিভাগ নির্বাচন")
selected_keyword = st.sidebar.selectbox("আপনি কোন বিষয়ে জানতে চান?", list(FOLDER_DATA.keys()))
folder_link = FOLDER_DATA[selected_keyword]

st.sidebar.info(f"📁 বর্তমানে দেখা হচ্ছে: **{selected_keyword}**")
st.sidebar.markdown(f"[সংশ্লিষ্ট ফোল্ডারটি দেখুন]({folder_link})")

# এপিআই সেটআপ
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# চ্যাট হিস্ট্রি
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": f"নমস্কার! আমি আপনাকে **{selected_keyword}** সংক্রান্ত পদক্ষেপের গাইডলাইন বুঝতে সাহায্য করতে পারি। আপনার প্রশ্নটি নিচে লিখুন।"
    })

# চ্যাট হিস্ট্রি প্রদর্শন
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ৪. ইউজারের প্রশ্ন এবং এআই প্রসেসিং
if prompt := st.chat_input("এখানে আপনার প্রশ্ন লিখুন..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # সিস্টেম ইন্সট্রাকশন
            system_context = f"""
            তুমি পদক্ষেপ মানবিক উন্নয়ন কেন্দ্রের ডিজিটাল বিশেষজ্ঞ। 
            ইউজার এখন '{selected_keyword}' ক্যাটাগরির গাইডলাইন নিয়ে প্রশ্ন করছে। 
            বাংলা বা ইংরেজি যে ভাষায় প্রশ্ন করা হোক, তুমি সেই ভাষাতেই উত্তর দেবে। 
            উত্তর শেষে অবশ্যই এই লিংকটি রেফারেন্স হিসেবে দেবে: {folder_link}
            """
            
            # রেসপন্স জেনারেট করা
            response = model.generate_content(f"{system_context}\n\nপ্রশ্ন: {prompt}")
            
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.warning("দুঃখিত, এআই কোনো তথ্য খুঁজে পায়নি।")

        except Exception as e:
            st.error("⚠️ একটি সমস্যা হয়েছে!")
            st.code(f"Error Details: {str(e)}")
