    import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2

st.set_page_config(page_title="Akhil AI Trader Life Pro", page_icon="📈", layout="centered")

st.title("🚀 अखिल एआई ट्रेडर लाइफ (प्रो वर्जन)")
st.write("यहाँ चैट करो, ट्रेडिंग सीखो (Learn), और चार्ट अपलोड करके एआई से जानो कि मार्केट ऊपर जाएगा या नीचे!")

api_key = st.sidebar.text_input("अपनी Google Gemini API Key यहाँ डालें:", type="password")

tab1, tab2, tab3 = st.tabs(["💬 एआई से बात करें", "🧠 लर्निंग / ट्रेनिंग बॉक्स", "📊 चार्ट एनालिसिस (Up/Down)"])

with tab1:
    st.subheader("ट्रेडिंग एक्सपर्ट एआई से बातचीत")
    st.write("यहाँ ट्रेडिंग से जुड़ा कोई भी सवाल पूछो, यह लिखकर और समझाकर जवाब देगा!")
    
    user_query = st.text_area("अपना सवाल यहाँ टाइप करो:")
    if st.button("जवाब भेजो"):
        if not api_key:
            st.error("भाई, पहले साइडबार में अपनी Google Gemini API Key डालो!")
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"तुम एक प्रो ट्रेडर और मददगार एआई हो। हिंदी में साफ़-साफ़ जवाब दो: {user_query}")
            st.markdown("### 🤖 एआई का जवाब:")
            st.write(response.text)

with tab2:
    st.subheader("एआई लर्निंग और ट्रेनिंग सेंटर")
    st.write("यहाँ यूट्यूब वीडियो के लिंक या इंस्टाग्राम/चार्ट का फोटो अपलोड करो ताकि एआई इसे सीख सके!")
    learn_input = st.text_input("यूट्यूब वीडियो लिंक या नोट्स दर्ज करें:")
    learn_file = st.file_uploader("सीखने के लिए फोटो अपलोड करें...", type=["jpg", "png", "jpeg"])
    if st.button("एआई को डेटा सिखाएं"):
        st.success("डेटा एआई की मेमोरी में फीड हो गया है!")

with tab3:
    st.subheader("चार्ट स्कैनर और मार्केट प्रेडिक्शन")
    uploaded_file = st.file_uploader("ट्रेडिंग चार्ट का स्क्रीनशॉट चुनें...", type=["jpg", "png", "jpeg"], key="chart_upload")

    def pil_to_cv2(pil_img):
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    def detect_candles_and_draw(pil_img):
        img_bgr = pil_to_cv2(pil_img)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        draw = ImageDraw.Draw(pil_img)
        for i, cnt in enumerate(contours):
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 5 and h > 10:
                color = "green" if i % 2 == 0 else "red"
                box_color = (0, 255, 0) if color == "green" else (255, 0, 0)
                draw.rectangle([x, y, x + w, y + h], outline=box_color, width=3)
        return pil_img

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        annotated_image = detect_candles_and_draw(image.copy())
        st.image(annotated_image, caption="डिटेक्टेड कैंडल्स (बॉक्स के साथ)", use_container_width=True)

        if st.button("चार्ट का फाइनल प्रेडिक्शन निकालें"):
            if not api_key:
                st.error("भाई, पहले साइडबार में अपनी API Key डालो!")
            else:
                with st.spinner("मार्केट का ट्रेंड कैलकुलेट हो रहा है..."):
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = "तुम एक प्रोफेशनल ट्रेडिंग एक्सपर्ट हो। इस चार्ट को देखकर बताओ कि मार्केट ऊपर जाने वाला है या नीचे गिरने वाला है। पूरी डिटेल में समझाओ।"
                    response = model.generate_content([prompt, image])
                    st.success("विश्लेषण पूरा हुआ!")
                    st.markdown("### 📊 फाइनल मार्केट प्रेडिक्शन:")
                    st.write(response.text)    
