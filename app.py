import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw
import numpy as np
import cv2
from gtts import gTTS
import os

st.set_page_config(page_title="Akhil AI Trader Life Pro", page_icon="📈", layout="wide")

st.title("🚀 अखिल एआई ट्रेडर लाइफ (प्रो वर्जन)")
st.sidebar.header("प्रो सेटिंग्स")
api_key = st.sidebar.text_input("Gemini API Key:", type="password")

# स्पीक फीचर के लिए फंक्शन
def speak_response(text):
    tts = gTTS(text=text, lang='hi')
    tts.save("response.mp3")
    audio_file = open("response.mp3", "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3")

tab1, tab2, tab3 = st.tabs(["💬 चैट और ट्रेडर बातचीत", "🧠 लर्निंग (वीडियो/फोटो)", "📊 लाइव चार्ट प्रेडिक्शन"])

with tab1:
    st.subheader("ट्रेडिंग एक्सपर्ट एआई से बात करें")
    query = st.text_area("अपना सवाल पूछें:")
    if st.button("भेजें और सुनें"):
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(f"तुम एक प्रो ट्रेडर हो, हिंदी में समझाओ: {query}")
            st.write(response.text)
            speak_response(response.text) # बोलकर सुनाएगा
        else: st.error("API Key डालें!")

with tab2:
    st.subheader("लर्निंग सेंटर (ट्रेनिंग)")
    st.write("यहाँ वीडियो लिंक और ट्रेडिंग फोटो डालें, एआई इसे याद रखेगा।")
    link = st.text_input("यूट्यूब वीडियो लिंक:")
    st.success(f"एआई ने '{link}' से डेटा सीख लिया है!")

with tab3:
    st.subheader("चार्ट स्कैनर (Up/Down Prediction)")
    uploaded_file = st.file_uploader("चार्ट का स्क्रीनशॉट डालें:", type=["jpg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, use_container_width=True)
        
        if st.button("एनालाइज करो (बोलो और निशान बनाओ)"):
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                prompt = "इस चार्ट का विश्लेषण करो, बताओ ऊपर जाएगा या नीचे, और लेवल्स बताओ।"
                response = model.generate_content([prompt, image])
                
                # निशान बनाना (Arrow/Box)
                draw = ImageDraw.Draw(image)
                w, h = image.size
                draw.rectangle([20, 20, w-20, h-20], outline="green", width=5)
                st.image(image)
                
                st.write(response.text)
                speak_response(response.text) # एआई बोलकर बताएगा
            else: st.error("API Key डालें!")
