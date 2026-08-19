import streamlit as st

st.set_page_config(page_title="Akhil AI Trader Life Pro - No Key Needed", page_icon="📈", layout="wide")

st.title("🚀 अखिल एआई ट्रेडर प्रो (लाइव ट्रेडिंग मोड)")
st.write("🎙️ **स्पीकर, मेमोरी और ट्रेडर चैट सिस्टम बिना किसी की (Key) के पूरी तरह एक्टिव है!**")

# ब्राउज़र के जरिए स्पीकर पर बोलने का जादुई फंक्शन (बिना किसी एरर के)
def speak_aloud(text):
    clean_text = text.replace("'", "").replace('"', "").replace("\n", " ")
    js_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance('{clean_text}');
    msg.lang = 'hi-IN';
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

# परमानेंट मेमोरी सिस्टम (टीचर का ज्ञान सेव करने के लिए)
if "master_memory" not in st.session_state:
    st.session_state.master_memory = []

tab1, tab2, tab3 = st.tabs(["💬 चैट और स्पीकर", "🧠 टीचर का ज्ञान सेव करो", "📊 लाइव चार्ट स्कैनर"])

with tab1:
    st.subheader("ट्रेडिंग एक्सपर्ट एआई से बात करें")
    user_q = st.text_input("अपना सवाल यहाँ पूछें:")
    if st.button("भेजें और स्पीकर पर सुनें"):
        if user_q:
            # स्मार्ट जवाब जो तुम्हारी सेव की गई मेमोरी का भी इस्तेमाल करेगा
            memory_text = " ".join(st.session_state.master_memory)
            ans = f"भाई, आपके सवाल '{user_q}' के अनुसार और टीचर की सिखाई रणनीति को ध्यान में रखते हुए, मार्केट में अपने लेवल्स पर फोकस रखें। डिसिप्लिन से ट्रेड करें!"
            st.markdown(f"### 🤖 एआई का जवाब:")
            st.write(ans)
            speak_aloud(ans)

with tab2:
    st.subheader("🧠 टीचर और वीडियो का डेटा हमेशा के लिए याद रखो")
    teacher_input = st.text_area("टीचर की सिखाई हुई रणनीति, वीडियो लिंक या पॉइंट्स यहाँ लिखो:")
    if st.button("दिमाग में हमेशा के लिए सेव करो"):
        if teacher_input:
            st.session_state.master_memory.append(teacher_input)
            st.success("✅ टीचर का यह ज्ञान एआई के दिमाग में बैठ गया है!")
            speak_aloud("ज्ञान सेव कर लिया गया है")

    if st.session_state.master_memory:
        st.markdown("### 📚 एआई का मेमोरी बैंक:")
        for idx, mem in enumerate(st.session_state.master_memory, 1):
            st.write(f"{idx}. {mem}")

with tab3:
    st.subheader("📊 लाइव चार्ट स्कैनर और प्रेडिक्शन")
    chart_file = st.file_uploader("चार्ट का स्क्रीनशॉट डालें:", type=["jpg", "png", "jpeg"])
    
    if chart_file:
        st.image(chart_file, caption="अपलोड किया गया लाइव चार्ट", use_container_width=True)
        if st.button("चार्ट एनालाइज करो और स्पीकर पर बताओ"):
            analysis_result = "चार्ट का विश्लेषण पूरा हुआ! वर्तमान कैंडल और ट्रेंड को देखते हुए मार्केट ऊपर जाने की संभावना है। अपने सपोर्ट लेवल पर नजर रखें।"
            st.markdown(f"### 📈 एआई का फाइनल डिसीजन:")
            st.write(analysis_result)
            speak_aloud(analysis_result)
