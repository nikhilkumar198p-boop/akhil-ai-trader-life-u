# -*- coding: utf-8 -*-
"""
app.py
निखिल का ट्रेडिंग एआई मेंटर — Streamlit एप्लिकेशन
- लोकल इमेज-प्रोसेसिंग से कैंडल्स detect कर के हिन्दी में विश्लेषण करता है
- Optional: Gemini/Generative API integration के लिए प्लेसहोल्डर (commented)
"""
import io
import base64
import textwrap
from typing import List, Tuple

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# OpenCV and NumPy (for image processing)
try:
    import numpy as np
    import cv2
except Exception:
    st.warning(
        "OpenCV/NumPy इंस्टॉल नहीं मिला। यदि आप लोकल इमेज-एनालिसिस चलाना चाहते हैं तो चलाएँ:\n"
        "`pip install numpy opencv-python-headless`"
    )
    raise

# -------------------------
# पेज सेटअप और स्टाइल
# -------------------------
st.set_page_config(page_title="निखिल का ट्रेडिंग एआई मेंटर", page_icon="📈", layout="centered")
st.title("🚀 निखिल का ट्रेडिंग एआई विज़न मेंटर")
st.write("यह टूल स्क्रीनशॉट के आधार पर कैंडल पैटर्न का बेसिक विश्लेषण करता है — जानकारी के लिए, निवेश सलाह नहीं।")

st.markdown(
    "<small>Disclaimer: यह केवल शैक्षिक/जानकारी उद्देश्य के लिए है। किसी भी ट्रेडिंग निर्णय से पहले अपनी रिसर्च और प्रोफ़ेशनल सलाह लें।</small>",
    unsafe_allow_html=True,
)

# -------------------------
# API Key: st.secrets का इस्तेमाल
# -------------------------
# Streamlit Cloud में: Secrets => GEMINI_API_KEY = "आपकी_की"
# लोकल डेवलपमेंट के लिए आप नीचे टेक्स्ट इनपुट में डाल सकते हैं (यह स्टोर नहीं करेगा)
api_key_from_secrets = st.secrets.get("GEMINI_API_KEY") if st.secrets else None
api_key = api_key_from_secrets or st.text_input("यदि आपने Streamlit secrets में नहीं डाली है तो यहाँ Gemini API Key डालें (dev only):", type="password")

if api_key_from_secrets:
    st.info("API Key: st.secrets से ली गई। (Streamlit Cloud में सेटेड)")

# -------------------------
# फ़ाइल अपलोड
# -------------------------
uploaded_file = st.file_uploader("चार्ट का स्क्रीनशॉट अपलोड करें (jpg/png/jpeg)...", type=["jpg", "png", "jpeg"])

# -------------------------
# सहायक फ़ंक्शंस: इमेज प्रोसेसिंग और कैंडल डिटेक्शन
# -------------------------
def pil_to_cv2(img_pil: Image.Image) -> np.ndarray:
    """PIL Image -> OpenCV BGR numpy array"""
    img_rgb = img_pil.convert("RGB")
    arr = np.array(img_rgb)
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    return bgr


def detect_candles(img_bgr: np.ndarray, min_area: int = 200) -> List[dict]:
    """
    सरल heuristic-based candle detector:
    - HSV में green/red मास्क बनाकर blobs ढूँढे जाते हैं
    - हर blob के लिए bounding box निकाला जाता है और वर्टिकल आकार वाली वस्तुओं को कैंडल माना जाता है
    Returns: list of dicts {x,y,w,h, color('green'/'red'), area}
    """
    h, w = img_bgr.shape[:2]
    resized_w = 1000
    scale = resized_w / float(w)
    img = cv2.resize(img_bgr, (resized_w, int(h * scale)), interpolation=cv2.INTER_AREA)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Green mask (approx)
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Red mask (two ranges)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)

    # Combine masks to find candidate candle bodies
    mask = cv2.medianBlur(mask_green | mask_red, 5)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 9))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candles = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        x, y, cw, ch = cv2.boundingRect(cnt)
        # Heuristic: vertical-ish shapes only
        if ch < cw * 1.0:  # require taller than wide
            continue
        # determine color by sampling center
        cx, cy = x + cw // 2, y + ch // 2
        px = img[cy, cx]
        hsv_px = cv2.cvtColor(np.uint8([[px]]), cv2.COLOR_BGR2HSV)[0][0]
        hue = hsv_px[0]
        # simple color pick from masks
        if mask_green[cy, cx]:
            color = "green"
        elif mask_red[cy, cx]:
            color = "red"
        else:
            # fallback: decide by hue numeric
            color = "green" if 35 <= hue <= 85 else "red"
        candles.append({"x": int(x / scale), "y": int(y / scale), "w": int(cw / scale), "h": int(ch / scale), "area": int(area), "color": color})

    # Sort left->right by x
    candles_sorted = sorted(candles, key=lambda c: c["x"])
    return candles_sorted


def analyze_candles(candles: List[dict]) -> Tuple[str, dict]:
    """
    Simple rule-based analysis in Hindi.
    Returns (summary_text, details_dict)
    """
    details = {"total": len(candles)}
    if not candles:
        return "कैंडल्स डिटेक्ट नहीं हुए — कृपया एक साफ़ चार्ट भेजें (बैकग्राउंड और ग्रिड हटाकर देखें)।", details

    # focus on last N candles
    N = min(10, len(candles))
    last = candles[-N:]
    greens = sum(1 for c in last if c["color"] == "green")
    reds = sum(1 for c in last if c["color"] == "red"])
    avg_height = sum(c["h"] for c in last) / N

    # very simple momentum heuristic
    # compare average body height of last half vs previous half (if possible)
    momentum = 0.0
    if N >= 4:
        half = N // 2
        recent_avg = sum(c["h"] for c in last[-half:]) / half
        prev_avg = sum(c["h"] for c in last[:half]) / half
        momentum = (recent_avg - prev_avg) / (prev_avg + 1e-6)

    # prediction rules (very basic, informational only)
    if greens > reds and momentum > 0.05:
        prediction = "ऊपर"
        confidence = min(90, 50 + int((greens - reds) / N * 50 + momentum * 100))
    elif reds > greens and momentum < -0.05:
        prediction = "नीचे"
        confidence = min(90, 50 + int((reds - greens) / N * 50 - momentum * 100))
    else:
        prediction = "न्यूट्रल / अस्पष्ट"
        confidence = 40 + int(abs(greens - reds) / N * 20)

    # Build Hindi summary
    summary = textwrap.dedent(
        f"""
        अंतिम {N} कैंडल्स में:
        - हरा: {greens} , लाल: {reds}
        - औसत कैंडल बॉडी ऊँचाई: {avg_height:.1f} पिक्सल (सापेक्ष)
        - सरल मूवमेंट हिसाब से भविष्यवाणी: {prediction} (विश्वास ~ {confidence}%)
        """
    ).strip()

    details.update({"last_N": N, "greens": greens, "reds": reds, "avg_height": avg_height, "momentum": momentum, "prediction": prediction, "confidence": confidence})
    return summary, details


def draw_detections_on_image(pil_img: Image.Image, candles: List[dict]) -> Image.Image:
    """
    Draw rectangles and small labels on the image to show detected candles.
    """
    draw = ImageDraw.Draw(pil_img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 14)
    except Exception:
        font = ImageFont.load_default()

    for i, c in enumerate(candles):
        x, y, w, h = c["x"], c["y"], c["w"], c["h"]
        color = (0, 200, 0) if c["color"] == "green" else (200, 0, 0)
        draw.rectangle([x, y, x + w, y + h], outline=color, width=2)
        draw.text((x, max(0, y - 18)), f"{i}:{c['color']}", fill=color, font=font)
    return pil_img


# -------------------------
# मुख्य UI लॉजिक
# -------------------------
if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file).convert("RGB")
    except Exception as e:
        st.error(f"इमेज पढ़ते समय त्रुटि: {e}")
        st.stop()

    st.image(image, caption="अपलोड किया गया चार्ट", use_column_width=True)

    use_gemini = st.checkbox("अगर आप चाहें तो Gemini से विस्तृत व्याख्या (Optional)", value=False)

    if st.button("चार्ट का विश्लेषण (Analyze) करें"):
        with st.spinner("कैंडल्स खोज रहे हैं और विश्लेषण कर रहे हैं..."):
            try:
                img_bgr = pil_to_cv2(image)
                candles = detect_candles(img_bgr)
                summary_text, details = analyze_candles(candles)

                # दिखाने के लिए image पर detections ड्रॉ करें
                annotated = draw_detections_on_image(image.copy(), candles)
                st.image(annotated, caption="डिटेक्टेड कैंडल्स", use_column_width=True)

                st.success("विश्लेषण पूरा हुआ!")
                st.markdown("### 📊 एआई का फाइनल नतीजा (लोकल एनालिसिस):")
                st.write(summary_text)

                st.markdown("#### विस्तृत विवरण:")
                st.json(details)

                # Optional: अगर user ने Gemini चुना और API Key है, तो नीचे विवरण भेजें (placeholder)
                if use_gemini:
                    if not api_key:
                        st.error("Gemini के लिए API Key नहीं दी गई — पहले ऊपर Key डालें या st.secrets में सेट करें।")
                    else:
                        st.info("Gemini से कॉल करने के लिए प्लेसहोल्डर रन करेगा — नीचे निर्देश पढ़ें।")
                        # हम यहाँ पूर्ण Gemini call नहीं करते; बजाय इसके हम उपयोगकर्ता को दो विकल्प देते हैं:
                        # 1) google.generativeai client का उदाहरण (commented)
                        # 2) REST example (commented)
                        # अगर आप चाहें तो नीचे दिए गए example में से एक को uncomment करके चलाएँ —
                        # ध्यान: आपके client-library वर्जन के हिसाब से argument नाम बदल सकते हैं।
                        st.markdown(
                            """
                            #### Gemini Integration के लिए निर्देश (Templates)
                            नीचे दिए गए code-templates को अपनी मशीन पर uncomment करके, और client-version के अनुसार adjust करके चलाएँ।

                            1) google.generativeai (यदि आपका पैकेज यही है):
                            ```python
                            import google.generativeai as genai
                            genai.configure(api_key=YOUR_KEY)
                            # उदाहरण - ध्यान दें: library versions के अनुसार method नाम अलग हो सकते हैं
                            resp = genai.responses.generate(
                                model="gemini-1.5-mini",  # अपने मॉडल के नाम से बदलें
                                input=f"चार्ट का संक्षेप: {summary_text}\\nपूरी इमेज context: (बाइनरी अटैचमेंट)"
                            )
                            print(resp)
                            ```

                            2) REST call (उदाहरण, Generative Language API के पुराने v1beta endpoints के जैसा):
                            ```python
                            import requests, json, base64
                            url = "https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generate?key=" + YOUR_KEY
                            payload = {
                                "prompt": {
                                  "text": "चार्ट का संक्षेप: " + summary_text + "\\nऔर विस्तृत व्याख्या दीजिए..."
                                },
                                "temperature": 0.2,
                                "maxOutputTokens": 512
                            }
                            r = requests.post(url, json=payload)
                            print(r.json())
                            ```
                            """
                        )

                        st.info("ऊपर templates दी गई हैं — अपने client/वर्जन के हिसाब से adjust करें।")
            except Exception as e:
                st.error(f"एनालिसिस के दौरान एरर आया: {e}")

else:
    st.info("ऊपर से चार्ट का स्क्रीनशॉट अपलोड करें, फिर 'Analyze' दबाएँ।")

# -------------------------
# Footnote: उपयोग और secrets
# -------------------------
st.markdown("---")
st.markdown(
    """
    ### कैसे स्ट्रीमलिट secrets में API key डालें:
    - Streamlit Cloud पर: App settings -> Secrets -> Add `GEMINI_API_KEY="आपकी_की"`
    - लोकल में एक फ़ाइल `.streamlit/secrets.toml` बनाकर उसमें लिखें:
    ```
    GEMINI_API_KEY = "आपकी_की"
    ```
    """
  )
