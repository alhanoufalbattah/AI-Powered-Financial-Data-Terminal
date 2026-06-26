import streamlit as st
import yfinance as yf
import requests
import urllib3
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="ALHANOUF ALBATTAH | Terminal", layout="wide")

# تجاوز خطأ شهادة الأمان SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- كود التصميم المطور (حل مشكلة السواد وعدم الوضوح) ---
st.markdown("""
    <style>
    /* إجبار خلفية الصفحة على اللون الأبيض */
    .stApp {
        background-color: #FFFFFF !important;
    }

    /* تنسيق النصوص العامة */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #1e3a8a !important; /* كحلي غامق */
    }

    /* --- تحسين شكل صناديق الكتابة (اللي طالعة سوداء بالصورة) --- */
    input {
        color: #000000 !important; /* الكتابة بالأسود */
        background-color: #f8fafc !important; /* خلفية رمادية فاتحة جداً */
        border: 2px solid #cbd5e1 !important; /* إطار واضح */
    }

    /* --- تحسين شكل الزر (عشان ما يطلع أسود وباهت) --- */
    .stButton>button {
        background-color: #1e3a8a !important; /* لون كحلي ملكي */
        color: #FFFFFF !important; /* كتابة بيضاء واضحة جداً */
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 20px !important;
        font-size: 18px !important;
    }

    /* تنسيق بطاقات الأرقام الملونة */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 2px solid #1e3a8a !important;
        border-radius: 15px !important;
        padding: 15px !important;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.1) !important;
    }

    div[data-testid="stMetricValue"] > div {
        color: #1e3a8a !important;
        font-weight: 800 !important;
    }

    /* تنسيق السايدبار (الجانبي) */
    section[data-testid="stSidebar"] {
        background-color: #f1f5f9 !important;
    }
    
    .my-name-sidebar {
        background-color: #1e3a8a;
        color: white !important;
        padding: 15px;
        text-align: center;
        font-weight: bold;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. جلب المفتاح
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
    if not MISTRAL_API_KEY: return "⚠️ مفتاح الـ API مفقود."
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "system", "content": "أنت خبير مالي محترف. أجب باللغة العربية."}, {"role": "user", "content": prompt_text}]
    }
    try:
        r = requests.post(url, json=payload, headers=headers, verify=False)
        return r.json()['choices'][0]['message']['content']
    except: return "المستشار مشغول حالياً."

# --- واجهة المستخدم ---
with st.sidebar:
    st.markdown("<div class='my-name-sidebar'>ALHANOUF ALBATTAH</div>", unsafe_allow_html=True)
    symbol = st.text_input("رمز السهم (مثلاً 7010.SR):", "7010.SR")
    st.write(f"📅 2026 Terminal")

info, ticker_obj = get_stock_data(symbol)

if info:
    st.markdown(f"<h2>🏢 {info['longName']}</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
    
    with col1:
        st.metric("السعر الحالي", f"{price} SAR")
    with col2:
        st.metric("مكرر الربحية P/E", info.get('trailingPE', 'N/A'))

    st.write("---")
    
    tab1, tab2 = st.tabs(["📊 المخطط", "🤖 التحليل"])
    
    with tab1:
        hist = ticker_obj.history(period="6mo")
        st.area_chart(hist['Close'])

    with tab2:
        st.write("### اسأل المستشار عن هذا السهم")
        user_q = st.text_input("اكتب سؤالك هنا:", key="user_input")
        if st.button("تحليل البيانات فوراً"):
            with st.spinner("جاري التحليل..."):
                answer = ask_ai(f"حلل سهم {info['longName']} سعره {price}. السؤال: {user_q}")
                st.markdown(f"<div style='color:black; background-color:#f1f5f9; padding:15px; border-radius:10px; border-left: 5px solid #1e3a8a;'>{answer}</div>", unsafe_allow_html=True)
else:
    st.error("رمز السهم غير صحيح.")
