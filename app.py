import streamlit as st
import google.generativeai as genai

# ১. কনফিগারেশন: আপনার জেমিনি এপিআই কি (API Key) এখানে বসান
API_KEY = "AIzaSyAt1uAcNgzU__d_0OeT2MI9F9KzUf2lGK8"
genai.configure(api_key=API_KEY)

# ২. কিওয়ার্ড এবং গুগল ড্রাইভ ফোল্ডার লিংক (আপনার লিংকগুলো এখানে দিন)
FOLDER_DATA = {
    "অগ্রসর": "https://drive.google.com/drive/folders/1UJ5pVxSF25TpbgaHAT6BS7fv47ewSlpw",
    "আর্থিক ও প্রশাসনিক অনিয়ম": "https://drive.google.com/drive/folders/1thXY_XJwHFEh6qsuezQeZ714SHCb2VwF",
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
st.markdown("### পদক্ষেপ মানবিক উন্নয়ন কেন্দ্র - নির্দেশিকা সহায়িকা")

# সাইডবারে কিওয়ার্ড সিলেকশন
st.sidebar.header("বিভাগ নির্বাচন করুন")
selected_keyword = st.sidebar.selectbox("আপনি কোন বিষয়ে জানতে চান?", list(FOLDER_DATA.keys()))

# ড্রাইভ লিংক প্রদর্শন
folder_link = FOLDER_DATA[selected_keyword]
st.sidebar.markdown(f"📁 [এই বিভাগের মূল ফাইলগুলো দেখুন]({folder_link})")

# চ্যাট হিস্ট্রি সেটআপ
if "messages" not in st.session_state:
    st.session_state.messages = []
    # স্বাগতম বার্তা
    welcome_msg = f"স্বাগতম! আমি আপনাকে **{selected_keyword}** সংক্রান্ত তথ্য দিয়ে সাহায্য করতে পারি। আপনার কি কোনো প্রশ্ন আছে?"
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# চ্যাট হিস্ট্রি প্রদর্শন
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ৪. ইউজারের প্রশ্ন গ্রহণ এবং এআই উত্তর তৈরি
if prompt := st.chat_input("আপনার প্রশ্নটি এখানে লিখুন..."):
    # ইউজারের প্রশ্ন চ্যাটে দেখানো
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # এআই-এর প্রসেসিং (Gemini 1.5 Flash ব্যবহার করা হয়েছে যা স্ক্যান করা বাংলা পড়তে পারে)
    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # সিস্টেম ইন্সট্রাকশন
            system_instruction = f"""
            তুমি 'পদক্ষেপ মানবিক উন্নয়ন কেন্দ্র'-এর একজন বিশেষজ্ঞ এআই অ্যাসিস্ট্যান্ট। 
            ইউজার এখন '{selected_keyword}' নিয়ে প্রশ্ন করছে। 
            তোমার কাজ হলো পদক্ষেপের বাংলা নির্দেশিকা (যা স্ক্যান করা পিডিএফ হতে পারে) অনুযায়ী উত্তর দেওয়া।
            ইউজার যদি ইংরেজিতে প্রশ্ন করে, তবে বাংলা নির্দেশিকা থেকে তথ্য নিয়ে ইংরেজিতে উত্তর দাও।
            যদি ইউজার বাংলায় প্রশ্ন করে, তবে বাংলায় উত্তর দাও।
            প্রতিটি উত্তরের শেষে এই লিংকটি যুক্ত করে দাও: {folder_link}
            """
            
            full_prompt = f"{system_instruction}\n\nপ্রশ্ন: {prompt}"
            response = model.generate_content(full_prompt)
            
            final_answer = response.text
            st.markdown(final_answer)
            st.session_state.messages.append({"role": "assistant", "content": final_answer})
            
        except Exception as e:
            st.error("দুঃখিত, একটি কারিগরি সমস্যা হয়েছে। অনুগ্রহ করে আপনার API Key চেক করুন।")
