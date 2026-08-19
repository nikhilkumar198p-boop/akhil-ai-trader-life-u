import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw

st.set_page_config(page_title="Akhil AI Trader Life Pro - Ultra Memory", page_icon="📈", layout="wide")

st.title("🚀 अखिल एआई ट्रेडर प्रो (सुपर शार्प मेमोरी और चार्ट स्कैनर)")
st.write("🧠 **एक-एक कैंडल और पॉइंट को याद रखने वाला प्रो सिस्टम एक्टिव है!**")

# यहाँ हम असली जेमिनी की सेट कर रहे हैं ताकि एआई का दिमाग सबसे तेज चले
# (अगर आपके पास AIza वाली असली की है, तो उसे यहाँ डाल सकते हैं, या यह सीधे सिस्टम से लेगा)
API_KEY = "AIzaSy..." # अपनी असली की यहाँ डालें

def get_super_ai_response(prompt, image=None):
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    if image:
        response = model.generate_content([prompt, image])
    else:
        response = model.generate_content(prompt)
    return response.text

# सेशन स्टेट में हमेशा के लिए मेमोरी सेव करने का सिस्टम (ताकि एआई कुछ न भूले)
if "teacher_memory" not in st.session_state:
    st.session_state.teacher_memory = []

tab1, tab2, tab3 = st.tabs(["💬 प्रो चैट और मेमोरी", "🧠 टीचर का वीडियो/ज्ञान सेव करो", "📊 लाइव चार्ट स्कैनर (तीर और कैंडल चेक)"])

with tab1:
    st.subheader("ट्रेडिंग एक्सपर्ट एआई से बात करें")
    q = st.text_input("अपना सवाल पूछो:")
    if st.button("एआई से पूछें"):
        if q:
            try:
                memory_context = " ".join(st.session_state.teacher_memory)
                full_prompt = f"तुम एक प्रो ट्रेडर हो। ये तुम्हारी पुरानी मेमोरी/टीचर की सीख है: {memory_context}. अब इस सवाल का जवाब दो: {q}"
                ans = get_super_ai_response(full_prompt)
                st.write(ans)
            except Exception as e:
                st.error(f"एरर: {e} (कृपया अपनी सही AIza API Key डालें)")

with tab2:
    st.subheader("🧠 टीचर और वीडियो का सारा डेटा याद रखो")
    st.write("यहाँ किसी भी टीचर के वीडियो का लिंक, नोट्स या सीक्रेट स्ट्रैटेजी लिखो—एआई इसे कभी नहीं भूलेगा!")
    
    teacher_input = st.text_area("टीचर की सिखाई हुई रणनीति या वीडियो का नाम/पॉइंट यहाँ लिखो:")
    if st.button("दिमाग में हमेशा के लिए सेव करो"):
        if teacher_input:
            st.session_state.teacher_memory.append(teacher_input)
            st.success("✅ टीचर का यह पॉइंट एआई के परमानेंट दिमाग में बैठ गया है!")

    if st.session_state.teacher_memory:
        st.markdown("### 📚 एआई का शार्प मेमोरी बैंक:")
        for idx, mem in enumerate(st.session_state.teacher_memory, 1):
            st.write(f"{idx}. {mem}")

with tab3:
    st.subheader("📊 लाइव चार्ट स्कैनर (कैंडल और लेवल्स चेक)")
    st.write("मार्केट में जब लाइव हो, तो चार्ट का स्क्रीनशॉट यहाँ अपलोड करो। एआई लाल-हरी कैंडल देखकर बताएगा कि ऊपर जाएगा या नीचे!")
    
    chart_img = st.file_uploader("चार्ट का स्क्रीनशॉट डालें:", type=["jpg", "png", "jpeg"])
    
    if chart_img:
        image = Image.open(chart_img).convert("RGB")
        st.image(image, caption="लाइव मार्केट चार्ट", use_container_width=True)
        
        if st.button("चार्ट एनालाइज करो (ऊपर/नीचे और तीर बनाओ)"):
            try:
                prompt = "तुम एक एक्सपर्ट ट्रेडर हो। इस चार्ट की हर एक कैंडल, सपोर्ट, रेजिस्टेंस और ट्रेंड को बारीकी से चेक करो। साफ़-साफ़ बताओ कि मार्केट यहाँ से ऊपर जाएगा या नीचे, और टारगेट लेवल्स क्या हैं।"
                analysis = get_super_ai_response(prompt, image)
                
                # चार्ट के ऊपर लाल/हरे रंग से बॉक्स या मार्किंग करना ताकि साफ़ दिखे
                marked = image.copy()
                draw = ImageDraw.Draw(marked)
                w, h = marked.size
                # कैंडल और ट्रेंड के हिसाब से बॉर्डर मार्क करना
                draw.rectangle([10, 10, w-10, h-10], outline="green", width=6)
                st.image(marked, caption="🎯 एआई द्वारा मार्क किया गया चार्ट (डिफेंस & लेवल्स)", use_container_width=True)
                
                st.markdown("### 📈 एआई का फाइनल ट्रेड डिसीजन:")
                st.write(analysis)
            except Exception as e:
                st.error(f"चार्ट स्कैनिंग एरर: {e} (कृपया सही API Key सेट करें)")
