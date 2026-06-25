import streamlit as st
import yfinance as yf
import requests
import urllib3
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="ALHANOUF ALBATTAH | Live Terminal 2026", layout="wide")

# تجاوز خطأ شهادة الأمان SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# السنة الحالية
current_year = datetime.now().year

# --- تنسيق CSS ---
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

# 2. مفتاح الـ API الخاص بك
MISTRAL_API_KEY = "NhHxM2nPRC6drt54lSTpySuVJNtylcgh"

# 3. وظائف جلب البيانات (محدثة لجلب أحدث سعر)
def get_stock_data(symbol):
    try:
        # إضافة اسم مستخدم وهمي لتجنب حظر ياهو فاينانس للطلبات القديمة
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if not info or 'longName' not in info: return None, None
        return info, ticker
    except: return None, None

def ask_ai(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": "أنت خبير مالي. أجب بالعربية."},
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
    st.title("🔍 نظام التحليل اللحظي")
    symbol = st.text_input("أدخل رمز السهم:", "7010.SR")
    st.markdown("---")
    st.write("📅 **توقيت النظام الحالي:**")
    st.success(datetime.now().strftime("%Y-%m-%d %H:%M"))

# جلب البيانات
info, ticker_obj = get_stock_data(symbol)

if info:
    st.markdown(f"<div class='main-header'>🏢 {info['longName']}</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    # استخدام 'currentPrice' أو 'regularMarketPrice' لضمان أحدث سعر في 2026
    price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
    prev = info.get('previousClose', 1)
    diff = ((price - prev) / prev) * 100
    
    col1.metric("السعر اللحظي (2026)", f"{price}", f"{diff:.2f}%")
    col2.metric("مكرر الربحية P/E", info.get('trailingPE', 'N/A'))
    col3.metric("أعلى سعر/سنة", info.get('fiftyTwoWeekHigh', 'N/A'))
    div = info.get('dividendYield', 0)
    col4.metric("توزيعات الأرباح", f"{div*100:.2f}%" if div else "0%")

    st.write("---")

    t1, t2 = st.tabs(["📈 الرسم البياني المباشر", "🤖 استشارة الذكاء الاصطناعي"])
    
    with t1:
        st.subheader(f"أداء السهم وصولاً إلى {datetime.now().strftime('%B %Y')}")
        # جلب البيانات لآخر 6 أشهر من تاريخ اليوم الفعلي
        hist = ticker_obj.history(period="6mo")
        if not hist.empty:
            st.area_chart(hist['Close'])
            st.caption(f"آخر تحديث للبيانات: {hist.index[-1].strftime('%Y-%m-%d')}")
        else:
            st.error("تعذر جلب البيانات اللحظية. تأكد من اتصال الإنترنت وتحديث مكتبة yfinance.")

    with t2:
        st.subheader("تحليل المستشار المالي لعام 2026")
        user_q = st.text_input("اكتب سؤالك الاستثماري:", "كيف ترى أداء السهم في منتصف عام 2026؟")
        if st.button("بدء التحليل الفوري"):
            with st.spinner("جاري تحليل البيانات الحالية..."):
                full_prompt = f"حلل سهم {info['longName']} سعره {price}. نحن الآن في عام 2026. السؤال: {user_q}"
                answer = ask_ai(full_prompt)
                st.info(answer)

else:
    st.error("❌ رمز السهم غير صحيح أو البيانات غير متوفرة حالياً.")

# --- تذييل الصفحة ---
st.markdown(f"""
    <div class="footer">
        <p>Developed & Designed by: ALHANOUF ALBATTAH © {current_year}</p>
        <p style='font-size: 0.8em;'>Real-Time Data Terminal | 2026 Edition</p>
    </div>
    """, unsafe_allow_html=True)