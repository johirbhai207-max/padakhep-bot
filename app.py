import streamlit as st
import google.generativeai as genai

# ১. Secrets থেকে API Key গ্রহণ (সুরক্ষার জন্য এটি কোডে সরাসরি নেই)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Error: Streamlit Secrets-এ 'GEMINI_API_KEY' সেট করা নেই।")
    st.info("Streamlit Dashboard > Settings > Secrets-এ গিয়ে আপনার নতুন API Key-টি সেভ করুন।")
    st.stop()

# ২. ড্রাইভ ফোল্ডার ডাটা (পদক্ষেপ গাইডলাইন)
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

# ৩. এপিআই এবং মডেল সিলেকশন (এটি 404 Error দূর করবে)
@st.cache_resource
def load_ai_model():
    try:
        genai.configure(api_key=API_KEY)
        
        # আপনার অ্যাকাউন্টে বর্তমানে কোন কোন মডেল কাজ করছে তা দেখা
        all_models = genai.list_models()
        valid_models = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
        
        # অগ্রাধিকার ভিত্তিতে মডেল নির্বাচন
        for preferred in ['models/gemini-1.5-flash', 'models/gemini-pro', 'models/gemini-1.5-pro']:
            if preferred in valid_models:
                return genai.GenerativeModel(preferred)
        
        # যদি উপরেরগুলো না থাকে তবে লিস্টিংয়ের প্রথম মডেলটি নেবে
        if valid_models:
            return genai.GenerativeModel(valid_models[0])
        return None
    except Exception as e:
        st.error(f"এআই মডেল লোড করতে সমস্যা: {e}")
        return None

model = load_ai_model()

# ৪. চ্যাট ইন্টারফেস
selected_keyword = st.sidebar.selectbox("গাইডলাইন বিভাগ নির্বাচন করুন:", list(FOLDER_DATA.keys()))
folder_link = FOLDER_DATA[selected_keyword]

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": f"নমস্কার! আমি আপনাকে **{selected_keyword}** গাইডলাইন নিয়ে সাহায্য করতে পারি।"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("আপনার প্রশ্নটি এখানে লিখুন..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if model:
            try:
                system_context = f"তুমি পদক্ষেপ মানবিক উন্নয়ন কেন্দ্রের ডিজিটাল অ্যাসিস্ট্যান্ট। '{selected_keyword}' বিষয়ে উত্তর দাও। শেষে এই লিংকটি দাও: {folder_link}"
                response = model.generate_content(f"{system_context}\n\nUser Question: {prompt}")
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("দুঃখিত, আমি এই মুহূর্তে উত্তর দিতে পারছি না।")
                st.code(f"Error Code: {str(e)}")
        else:
            st.error("আপনার API Key দিয়ে কোনো এআই মডেল খুঁজে পাওয়া যায়নি।")
