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

# --- كود التصميم المطور (إجبار المربعات على اللون الرمادي والنص على الأسود) ---
st.markdown("""
    <style>
    /* 1. جعل الصفحة كاملة بيضاء */
    .stApp {
        background-color: #FFFFFF !important;
    }

    /* 2. إجبار كل النصوص على اللون الأسود */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {
        color: #000000 !important;
    }

    /* 3. تنسيق بطاقات الأرقام (Metrics) لتكون رمادية فاتحة */
    div[data-testid="stMetric"] {
        background-color: #f0f2f6 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: #000000 !important;
        font-weight: 800 !important;
    }

    /* 4. حل مشكلة المربع الأسود (تنسيق صندوق الكتابة بدقة) */
    div[data-baseweb="input"] {
        background-color: #f0f2f6 !important; /* رمادي فاتح */
        border: 1px solid #000000 !important; /* إطار أسود خفيف */
        border-radius: 10px !important;
    }
    
    input {
        color: #000000 !important; /* لون الكتابة أسود */
        background-color: transparent !important;
    }

    /* 5. تنسيق الزر (Button) */
    .stButton>button {
        background-color: #000000 !important; /* زر أسود */
        color: #ffffff !important; /* كتابة بيضاء */
        border-radius: 10px !important;
        width: 100% !important;
        font-weight: bold !important;
        border: none !important;
        height: 3em !important;
    }

    /* 6. السايدبار */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }
    .my-name-sidebar {
        font-size: 20px;
        font-weight: bold;
        color: #000000;
        text-align: center;
        padding: 10px;
        border: 2px solid #000000;
        border-radius: 8px;
        margin-bottom: 20px;
    }

    /* 7. صندوق رد الذكاء الاصطناعي */
    .ai-box {
        background-color: #f0f2f6 !important;
        color: #000000 !important;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #000000;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. جلب المفتاح السري من Secrets
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
    if not MISTRAL_API_KEY: return "⚠️ عذراً، مفتاح الـ API غير مفعّل في الإعدادات."
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "system", "content": "أنت مستشار مالي. أجب بالعربية بوضوح."}, {"role": "user", "content": prompt_text}]
    }
    try:
        r = requests.post(url, json=payload, headers=headers, verify=False)
        return r.json()['choices'][0]['message']['content']
    except: return "المستشار مشغول حالياً، جرب لاحقاً."

# --- واجهة المستخدم ---
with st.sidebar:
    st.markdown("<div class='my-name-sidebar'>ALHANOUF ALBATTAH</div>", unsafe_allow_html=True)
    symbol = st.text_input("رمز السهم:", "7010.SR")
    st.write(f"📅 تحديثات 2026")

info, ticker_obj = get_stock_data(symbol)

if info:
    st.markdown(f"<h1>🏢 {info['longName']}</h1>", unsafe_allow_html=True)
    
    # بطاقات البيانات (رمادي فاتح)
    c1, c2 = st.columns(2)
    price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
    
    with c1: st.metric("السعر الحالي", f"{price} SAR")
    with c2: st.metric("مكرر الربحية P/E", info.get('trailingPE', 'N/A'))

    st.write("---")

    # التبويبات
    t1, t2 = st.tabs(["📊 الرسم البياني", "🤖 استشارة المستشار"])

    with t1:
        hist = ticker_obj.history(period="6mo")
        st.area_chart(hist['Close'])

    with t2:
        st.markdown("### اسأل المستشار الذكي")
        # الصندوق الذي كان يظهر باللون الأسود:
        user_q = st.text_input("ما هو سؤالك حول هذا السهم؟", value="هل تنصحني بالاستثمار في هذا السهم؟", key="input_field")
        
        if st.button("تحليل البيانات فوراً"):
            with st.spinner("جاري التحليل..."):
                res = ask_ai(f"حلل سهم {info['longName']} سعره {price}. السؤال: {user_q}")
                # عرض الرد في صندوق رمادي منسق
                st.markdown(f"<div class='ai-box'>{res}</div>", unsafe_allow_html=True)
else:
    st.error("الرمز غير موجود.")

# --- التذييل ---
st.markdown("<div style='text-align:center; padding:30px; font-weight:bold; color:black;'>Developed by: ALHANOUF ALBATTAH © 2026</div>", unsafe_allow_html=True)
