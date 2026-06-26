import streamlit as st
import yfinance as yf
import requests
import urllib3
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="ALHANOUF ALBATTAH | Financial Terminal", layout="wide")

# تجاوز خطأ شهادة الأمان SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- كود التصميم المخصص (خلفية بيضاء، مربعات رمادية، كتابة سوداء) ---
st.markdown("""
    <style>
    /* 1. جعل الصفحة كاملة باللون الأبيض */
    .stApp {
        background-color: #FFFFFF !important;
    }

    /* 2. إجبار كل النصوص على اللون الأسود */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {
        color: #000000 !important;
    }

    /* 3. تنسيق صناديق الأرقام (Metrics) لتكون رمادية فاتحة */
    div[data-testid="stMetric"] {
        background-color: #f2f2f2 !important; /* رمادي فاتح */
        border: 1px solid #e0e0e0 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05) !important;
    }

    /* 4. إجبار قيمة الرقم المالي على اللون الأسود */
    div[data-testid="stMetricValue"] > div {
        color: #000000 !important;
        font-weight: 800 !important;
    }

    /* 5. تنسيق صناديق الإدخال (Input Boxes) */
    input {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1px solid #000000 !important;
    }

    /* 6. تنسيق الأزرار (Buttons) لتبدو احترافية */
    .stButton>button {
        background-color: #000000 !important; /* زر أسود */
        color: #ffffff !important; /* كتابة بيضاء داخل الزر للوضوح */
        border-radius: 8px !important;
        width: 100% !important;
        font-weight: bold !important;
    }

    /* 7. تنسيق السايدبار (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #f9f9f9 !important;
        border-right: 1px solid #eeeeee !important;
    }

    /* اسمك في السايدبار */
    .my-name-sidebar {
        font-size: 20px;
        font-weight: bold;
        color: #000000;
        text-align: center;
        padding: 10px;
        border: 2px solid #000000;
        border-radius: 5px;
        margin-bottom: 20px;
    }

    /* صندوق رد الذكاء الاصطناعي (رمادي فاتح مع نص أسود) */
    .ai-response-box {
        background-color: #f2f2f2 !important;
        color: #000000 !important;
        padding: 20px;
        border-radius: 10px;
        border-right: 5px solid #000000;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. جلب المفتاح السري
try:
    MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]
except:
    MISTRAL_API_KEY = None

# 3. وظائف جلب البيانات
def get_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if not info or 'longName' not in info: return None, None
        return info, ticker
    except: return None, None

def ask_ai(prompt_text):
    if not MISTRAL_API_KEY: return "⚠️ مفتاح الـ API مفقود في إعدادات Secrets."
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "system", "content": "أنت مستشار مالي. أجب بالعربية بوضوح."}, {"role": "user", "content": prompt_text}]
    }
    try:
        r = requests.post(url, json=payload, headers=headers, verify=False)
        return r.json()['choices'][0]['message']['content']
    except: return "المستشار مشغول حالياً."

# --- واجهة المستخدم (الشريط الجانبي) ---
with st.sidebar:
    st.markdown("<div class='my-name-sidebar'>ALHANOUF ALBATTAH</div>", unsafe_allow_html=True)
    symbol = st.text_input("ادخل رمز السهم:", "7010.SR")
    st.write(f"📅 نظام 2026")

# جلب البيانات وعرضها
info, ticker_obj = get_stock_data(symbol)

if info:
    st.markdown(f"<h1>🏢 {info['longName']}</h1>", unsafe_allow_html=True)
    
    # صف المؤشرات المالية (صناديق رمادية)
    col1, col2 = st.columns(2)
    price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
    
    with col1:
        st.metric("السعر الحالي", f"{price} SAR")
    with col2:
        st.metric("مكرر الربحية P/E", info.get('trailingPE', 'N/A'))

    st.write("---")

    # التبويبات
    tab1, tab2 = st.tabs(["📈 الرسم البياني", "🤖 استشارة المستشار"])

    with tab1:
        hist = ticker_obj.history(period="6mo")
        st.area_chart(hist['Close'])

    with tab2:
        st.markdown("### اسأل المستشار الذكي")
        user_q = st.text_input("ما هو سؤالك المالي؟", key="q_input")
        if st.button("بدء التحليل الفوري"):
            with st.spinner("جاري التفكير..."):
                answer = ask_ai(f"حلل سهم {info['longName']} سعره {price}. السؤال: {user_q}")
                # عرض الإجابة في صندوق رمادي فاتح
                st.markdown(f"<div class='ai-response-box'>{answer}</div>", unsafe_allow_html=True)

else:
    st.error("الرمز غير صحيح، حاول مرة أخرى.")

# --- التذييل ---
st.markdown("<div style='text-align:center; padding:20px; font-weight:bold;'>Developed by: ALHANOUF ALBATTAH © 2026</div>", unsafe_allow_html=True)
