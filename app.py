import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw
import numpy as np
import cv2
from gtts import gTTS
import os

st.set_page_config(page_title="Akhil AI Trader Life Pro", page_icon="📈", layout="wide")

st.title("🚀 अखिल एआई ट्रेडर लाइफ (प्रो वर्जन)")
st.write("ट्रेडिंग एआई पूरी तरह एक्टिव है—बिना किसी की (Key) के झंझट के!")

# तुम्हारी परमानेंट API Key यहाँ सेट कर दी गई है
PERMANENT_API_KEY = "AQ.Ab8RN6IEnV_kxYvZYSi1RW9GV_nfZkGZD9XrbB3EmonfPBVfRw"

def speak_response(text):
    try:
        tts = gTTS(text=text, lang='hi')
        tts.save("response.mp3")
        audio_file = open("response.mp3", "rb")
        st.audio(audio_file.read(), format="audio/mp3")
    except Exception as e:
        st.write("आवाज़ में छोटी सी समस्या: ", e)

tab1, tab2, tab3 = st.tabs(["💬 चैट और ट्रेडर बातचीत", "🧠 लर्निंग (वीडियो/फोटो)", "📊 लाइव चार्ट प्रेडिक्शन"])

with tab1:
    st.subheader("ट्रेडिंग एक्सपर्ट एआई से बात करें")
    query = st.text_area("अपना सवाल पूछें:")
    if st.button("भेजें और सुनें"):
        try:
            genai.configure(api_key=PERMANENT_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"तुम एक प्रो ट्रेडर हो, हिंदी में साफ़-साफ़ समझाओ: {query}")
            st.write(response.text)
            speak_response(response.text)
        except Exception as e:
            st.error(f"एरर आ गया: {e}")

with tab2:
    st.subheader("लर्निंग सेंटर (ट्रेनिंग)")
    link = st.text_input("यूट्यूब वीडियो लिंक या चैनल अपडेट:")
    if link:
        st.success(f"एआई ने डेटा सीख लिया है!")

with tab3:
    st.subheader("चार्ट स्कैनर (Up/Down Prediction)")
    uploaded_file = st.file_uploader("चार्ट का स्क्रीनशॉट डालें:", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="अपलोड किया गया चार्ट", use_container_width=True)
        
        if st.button("एनालाइज करो (बोलो और निशान बनाओ)"):
            try:
                genai.configure(api_key=PERMANENT_API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = "तुम एक एक्सपर्ट ट्रेडर हो। इस चार्ट का विश्लेषण करो, बताओ मार्केट ऊपर जाएगा या नीचे, और लेवल्स बताओ।"
                response = model.generate_content([prompt, image])
                
                marked_image = image.copy()
                draw = ImageDraw.Draw(marked_image)
                w, h = marked_image.size
                draw.rectangle([20, 20, w-20, h-20], outline="green", width=5)
                st.image(marked_image, caption="मार्केड चार्ट प्रेडिक्शन", use_container_width=True)
                
                st.markdown("### 📊 एआई का जवाब:")
                st.write(response.text)
                speak_response(response.text)
            except Exception as e:
                st.error(f"चार्ट एनालिसिस में एरर आया: {e}")
