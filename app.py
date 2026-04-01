import streamlit as st
import google.generativeai as genai

# ১. সুরক্ষা নিশ্চিত করতে এপিআই কি সরাসরি কোডে নেই (Secrets থেকে আসবে)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("Streamlit Secrets-এ 'GEMINI_API_KEY' পাওয়া যায়নি।")
    st.stop()

# ২. ড্রাইভ ফোল্ডার ডাটা
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

st.set_page_config(page_title="পদক্ষেপ মিত্র", page_icon="🤖")
st.title("🤖 পদক্ষেপ মিত্র (Padakhep Mitra)")

# সাইডবার
selected_keyword = st.sidebar.selectbox("বিভাগ নির্বাচন করুন:", list(FOLDER_DATA.keys()))
folder_link = FOLDER_DATA[selected_keyword]
st.sidebar.markdown(f"📁 [ফোল্ডার লিংক]({folder_link})")

# ৩. এপিআই কনফিগারেশন ও মডেল সিলেকশন
@st.cache_resource
def setup_ai():
    try:
        genai.configure(api_key=API_KEY)
        # সবচেয়ে আপডেট এবং নির্ভরযোগ্য মডেল ব্যবহার করা হচ্ছে
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"এআই কনফিগারেশনে সমস্যা: {e}")
        return None

model = setup_ai()

# চ্যাট ইন্টারফেস
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": f"নমস্কার! আমি আপনাকে **{selected_keyword}** গایدলাইন নিয়ে সাহায্য করতে পারি।"})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("আপনার প্রশ্ন লিখুন..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if model:
            try:
                system_msg = f"তুমি পদক্ষেপ মানবিক উন্নয়ন কেন্দ্রের বিশেষজ্ঞ। '{selected_keyword}' বিষয়ে উত্তর দাও। শেষে এই লিংকটি দাও: {folder_link}"
                response = model.generate_content(f"{system_msg}\n\nUser Question: {prompt}")
                if response.text:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("⚠️ দুঃখিত, উত্তর তৈরি করতে সমস্যা হয়েছে।")
                st.code(f"Error: {str(e)}")
        else:
            st.error("এআই মডেল লোড করা সম্ভব হয়নি।")
