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

# --- كود التصميم الجذري (تبييض شامل ومنع السواد) ---
st.markdown("""
    <style>
    /* 1. تبييض الخلفية الأساسية */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: white !important;
    }

    /* 2. إجبار كل النصوص على اللون الأسود */
    h1, h2, h3, h4, h5, h6, p, span, label, div, li, .stMarkdown {
        color: black !important;
    }

    /* 3. حل مشكلة المربع الأسود (صندوق الكتابة) */
    /* هذا الجزء يستهدف الصندوق في اللابتوب والجوال بدقة */
    .stTextInput div[data-baseweb="input"] {
        background-color: #f0f2f6 !important; /* رمادي فاتح جداً */
        border: 1px solid #000000 !important; /* إطار أسود نحيف */
        color: black !important;
    }

    .stTextInput input {
        color: black !important;
        background-color: #f0f2f6 !important;
        -webkit-text-fill-color: black !important;
    }

    /* 4. تنسيق بطاقات الأرقام (Metrics) */
    div[data-testid="stMetric"] {
        background-color: #f0f2f6 !important; /* مربعات رمادية فاتحة */
        border-radius: 10px !important;
        padding: 15px !important;
        border: 1px solid #dddddd !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: black !important;
        font-weight: bold !important;
    }

    /* 5. تنسيق الزر (Button) */
    .stButton>button {
        background-color: black !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        width: 100% !important;
    }

    /* 6. السايدبار (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #eeeeee !important;
    }
    .my-name-tag {
        border: 2px solid black;
        padding: 10px;
        text-align: center;
        font-weight: bold;
        color: black !important;
        margin-bottom: 20px;
    }
    
    /* 7. صندوق رد الذكاء الاصطناعي */
    .ai-res {
        background-color: #f0f2f6 !important;
        color: black !important;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid black;
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
    if not MISTRAL_API_KEY: return "⚠️ مفتاح الـ API مفقود."
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

# --- واجهة المستخدم ---
with st.sidebar:
    st.markdown("<div class='my-name-tag'>ALHANOUF ALBATTAH</div>", unsafe_allow_html=True)
    symbol = st.text_input("رمز السهم:", value="7010.SR")
    st.write(f"📅 2026 Edition")

info, ticker_obj = get_stock_data(symbol)

if info:
    st.markdown(f"<h1>🏢 {info['longName']}</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
    
    with col1: st.metric("السعر الحالي", f"{price} SAR")
    with col2: st.metric("مكرر الربحية P/E", info.get('trailingPE', 'N/A'))

    st.write("---")
    
    tab1, tab2 = st.tabs(["📈 المخطط البياني", "🤖 استشارة المستشار"])

    with tab1:
        hist = ticker_obj.history(period="6mo")
        st.area_chart(hist['Close'])

    with tab2:
        st.write("### اسأل المستشار الذكي")
        # الصندوق الذي كان يظهر باللون الأسود
        user_q = st.text_input("اكتب سؤالك هنا:", value="ما رأيك في استثمار هذا السهم؟")
        
        if st.button("تحليل البيانات فوراً"):
            with st.spinner("جاري التحليل..."):
                answer = ask_ai(f"سعر سهم {info['longName']} هو {price}. السؤال: {user_q}")
                st.markdown(f"<div class='ai-res'>{answer}</div>", unsafe_allow_html=True)
else:
    st.error("الرمز غير موجود.")

st.markdown("<div style='text-align:center; padding-top:50px; color:black;'>Developed by: ALHANOUF ALBATTAH © 2026</div>", unsafe_allow_html=True)
