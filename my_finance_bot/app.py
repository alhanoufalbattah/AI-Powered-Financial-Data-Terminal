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

# --- تنسيق CSS احترافي (حل مشكلة اللون الأبيض) ---
st.markdown(f"""
    <style>
    /* تغيير خلفية الصفحة بالكامل */
    .stApp {{
        background-color: #f0f2f6;
    }}
    /* تنسيق بطاقات الأرقام (Metrics) لتبدو بارزة */
    div[data-testid="stMetric"] {{
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        padding: 20px 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }}
    /* توضيح لون الخط للأرقام */
    div[data-testid="stMetricValue"] > div {{
        color: #1e3a8a !important; /* لون كحلي غامق */
        font-weight: bold !important;
        font-size: 28px !important;
    }}
    /* توضيح لون الخط للعناوين الصغيرة */
    div[data-testid="stMetricLabel"] > div {{
        color: #4b5563 !important; /* رمادي غامق */
        font-size: 16px !important;
        font-weight: 600 !important;
    }}
    .main-header {{
        font-size: 35px;
        font-weight: 800;
        color: #1e3a8a;
        text-align: right;
        margin-bottom: 30px;
    }}
    .my-name-sidebar {{
        font-size: 20px;
        font-weight: bold;
        color: #ffffff;
        background-color: #1e3a8a;
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }}
    .footer {{
        text-align: center;
        padding: 20px;
        font-weight: bold;
        color: #1e3a8a;
        margin-top: 50px;
    }}
    /* تحسين شكل الأزرار */
    .stButton>button {{
        background-color: #1e3a8a;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. جلب مفتاح الـ API من Secrets
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

def ask_ai(prompt):
    if not MISTRAL_API_KEY: return "⚠️ مفتاح الـ API مفقود في إعدادات Secrets."
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "system", "content": "أنت خبير مالي محترف. أجب بالعربية."}, {"role": "user", "content": prompt}]
    }
    try:
        r = requests.post(url, json=payload, headers=headers, verify=False)
        return r.json()['choices'][0]['message']['content']
    except: return "المستشار مشغول حالياً، يرجى المحاولة لاحقاً."

# --- الشريط الجانبي (Sidebar) ---
with st.sidebar:
    st.markdown("<div class='my-name-sidebar'>ALHANOUF ALBATTAH</div>", unsafe_allow_html=True)
    st.title("🔍 البحث والتحليل")
    symbol = st.text_input("أدخل رمز السهم:", "7010.SR")
    st.markdown("---")
    st.write("📅 **تاريخ اليوم:**")
    st.info(datetime.now().strftime("%Y-%m-%d"))

# جلب البيانات
info, ticker_obj = get_stock_data(symbol)

if info:
    st.markdown(f"<div class='main-header'>🏢 {info['longName']}</div>", unsafe_allow_html=True)
    
    # توزيع الأرقام (Metrics)
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
    prev = info.get('previousClose', 1)
    diff = ((price - prev) / prev) * 100
    
    with col1:
        st.metric("السعر اللحظي (2026)", f"{price}", f"{diff:.2f}%")
    with col2:
        st.metric("مكرر الربحية P/E", info.get('trailingPE', 'N/A'))
    with col3:
        st.metric("أعلى سعر/سنة", info.get('fiftyTwoWeekHigh', 'N/A'))
    with col4:
        div = info.get('dividendYield', 0)
        st.metric("توزيعات الأرباح", f"{div*100:.2f}%" if div else "0%")

    st.write("---")

    # التبويبات
    t1, t2 = st.tabs(["📈 الرسم البياني", "🤖 استشارة الذكاء الاصطناعي"])
    
    with t1:
        st.subheader("تحركات السهم - 2026")
        hist = ticker_obj.history(period="6mo")
        if not hist.empty:
            st.area_chart(hist['Close'])
    
    with t2:
        st.subheader("اسأل مستشارك المالي الذكي")
        user_q = st.text_input("اكتب سؤالك هنا:", "ما هي توقعاتك للسهم في 2026؟")
        if st.button("بدء التحليل الفوري"):
            with st.spinner("جاري قراءة البيانات..."):
                answer = ask_ai(f"حلل سهم {info['longName']} سعره {price}. السؤال: {user_q}")
                st.info(answer)

else:
    st.error("❌ رمز السهم غير صحيح.")

# --- تذييل الصفحة ---
st.markdown(f"""
    <div class="footer">
        <p>Developed & Designed by: ALHANOUF ALBATTAH © 2026</p>
    </div>
    """, unsafe_allow_html=True)
