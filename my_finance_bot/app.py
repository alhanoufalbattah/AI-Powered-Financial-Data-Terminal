import streamlit as st
import yfinance as yf
import requests
import urllib3
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة (يجب أن يكون أول سطر)
st.set_page_config(page_title="ALHANOUF ALBATTAH | Financial Terminal", layout="wide")

# تجاوز خطأ شهادة الأمان SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# الحصول على السنة الحالية
current_year = datetime.now().year

# --- تنسيق CSS المظهر والحقوق ---
st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; }}
    .stMetric {{ 
        background: white; 
        padding: 15px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-bottom: 4px solid #007bff;
    }}
    .main-header {{ font-size: 32px; font-weight: bold; color: #1e3a8a; }}
    .my-name-sidebar {{
        font-size: 20px;
        font-weight: bold;
        color: #007bff;
        text-align: center;
        border: 2px solid #007bff;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
    }}
    .footer {{
        text-align: center;
        padding: 20px;
        font-weight: bold;
        color: #1e3a8a;
        border-top: 1px solid #ddd;
        margin-top: 50px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. جلب مفتاح الـ API من الخزنة السرية (Secrets)
# ملاحظة: يجب إضافته في إعدادات موقع Streamlit Cloud
try:
    MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]
except:
    st.warning("⚠️ مفتاح الـ API غير مفعّل في الخزنة السرية. يرجى إضافته في إعدادات Streamlit.")
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
    if not MISTRAL_API_KEY:
        return "عذراً، مفتاح الـ API مفقود."
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": "أنت خبير مالي محترف. أجب باللغة العربية."},
            {"role": "user", "content": prompt}
        ]
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
    st.write("📅 **توقيت النظام:**")
    st.info(datetime.now().strftime("%Y-%m-%d"))

# جلب البيانات
info, ticker_obj = get_stock_data(symbol)

if info:
    st.markdown(f" <div class='main-header'>🏢 {info['longName']}</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
    prev = info.get('previousClose', 1)
    diff = ((price - prev) / prev) * 100
    
    col1.metric("السعر اللحظي (2026)", f"{price}", f"{diff:.2f}%")
    col2.metric("مكرر الربحية P/E", info.get('trailingPE', 'N/A'))
    col3.metric("أعلى سعر/سنة", info.get('fiftyTwoWeekHigh', 'N/A'))
    div = info.get('dividendYield', 0)
    col4.metric("توزيعات الأرباح", f"{div*100:.2f}%" if div else "0%")

    st.write("---")

    t1, t2 = st.tabs(["📈 الرسم البياني", "🤖 استشارة الذكاء الاصطناعي"])
    
    with t1:
        st.subheader("تحركات السهم - بيانات 2026")
        hist = ticker_obj.history(period="6mo")
        if not hist.empty:
            st.area_chart(hist['Close'])
            st.caption(f"آخر تحديث للبيانات: {hist.index[-1].strftime('%Y-%m-%d')}")

    with t2:
        st.subheader("اسأل مستشارك المالي الذكي")
        user_q = st.text_input("اكتب سؤالك هنا:", "ما هي توقعاتك للسهم في 2026؟")
        if st.button("بدء التحليل الفوري"):
            with st.spinner("جاري قراءة البيانات..."):
                full_prompt = f"حلل سهم {info['longName']} سعره {price}. السؤال: {user_q}"
                answer = ask_ai(full_prompt)
                st.info(answer)

else:
    st.error("❌ رمز السهم غير صحيح أو البيانات غير متوفرة.")

# --- تذييل الصفحة ---
st.markdown(f"""
    <div class="footer">
        <p>Developed & Designed by: ALHANOUF ALBATTAH © {current_year}</p>
        <p style='font-size: 0.8em;'>Financial Data Terminal | v3.0 Secured</p>
    </div>
    """, unsafe_allow_html=True)