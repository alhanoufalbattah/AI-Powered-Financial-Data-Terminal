import streamlit as st
import yfinance as yf
import requests
import urllib3
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة (يجب أن يكون أول سطر برمجي)
st.set_page_config(page_title="ALHANOUF ALBATTAH | Financial Terminal", layout="wide")

# تجاوز خطأ شهادة الأمان SSL (لضمان عمل البيانات في كل الأوقات)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- تنسيق CSS احترافي (إجبار الألوان على الأسود والكحلي ومنع الأبيض) ---
st.markdown("""
    <style>
    /* تغيير خلفية التطبيق للون فاتح جداً */
    .stApp {
        background-color: #ffffff !important;
    }

    /* إجبار كل العناوين والنصوص على اللون الأسود */
    h1, h2, h3, h4, h5, h6, p, span, label, div, .stMarkdown {
        color: #000000 !important;
    }

    /* تنسيق بطاقات الأرقام (Metrics) */
    div[data-testid="stMetric"] {
        background-color: #f1f5f9 !important; /* رمادي فاتح للخلفية */
        border: 2px solid #1e3a8a !important; /* إطار كحلي واضح */
        padding: 15px !important;
        border-radius: 12px !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1) !important;
    }

    /* تلوين الرقم المالي بالكحلي الغامق */
    div[data-testid="stMetricValue"] > div {
        color: #1e3a8a !important;
        font-weight: 800 !important;
    }

    /* تلوين اسم المؤشر بالأسود */
    div[data-testid="stMetricLabel"] > div {
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* تنسيق التبويبات (Tabs) لضمان وضوح النص */
    button[data-baseweb="tab"] {
        color: #000000 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #1e3a8a !important;
        border-bottom-color: #1e3a8a !important;
    }

    /* تنسيق الشريط الجانبي (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0 !important;
    }

    /* تصميم اسمك في السايدبار */
    .my-name-sidebar {
        font-size: 20px;
        font-weight: 900;
        color: #ffffff !important; /* النص هنا أبيض للتباين مع الخلفية الكحلية */
        background-color: #1e3a8a;
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }

    /* تذييل الصفحة */
    .footer {
        text-align: center;
        padding: 20px;
        font-weight: bold;
        color: #000000 !important;
        border-top: 2px solid #1e3a8a;
        margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. جلب مفتاح الـ API من Secrets (للأمان)
try:
    MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]
except:
    MISTRAL_API_KEY = None

# 3. وظائف جلب البيانات من ياهو فاينانس
def get_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if not info or 'longName' not in info: return None, None
        return info, ticker
    except: return None, None

# 4. وظيفة الاتصال بذكاء Mistral AI
def ask_ai(prompt_text):
    if not MISTRAL_API_KEY: return "⚠️ يرجى إضافة MISTRAL_API_KEY في إعدادات Secrets."
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": "أنت خبير مالي سعودي محترف. أجب باللغة العربية."},
            {"role": "user", "content": prompt_text}
        ]
    }
    try:
        r = requests.post(url, json=payload, headers=headers, verify=False)
        return r.json()['choices'][0]['message']['content']
    except: return "المستشار مشغول حالياً، يرجى المحاولة لاحقاً."

# --- واجهة المستخدم (Sidebar) ---
with st.sidebar:
    st.markdown("<div class='my-name-sidebar'>ALHANOUF ALBATTAH</div>", unsafe_allow_html=True)
    st.markdown("### 🔍 محرك البحث المالي")
    symbol = st.text_input("أدخل رمز السهم (مثلاً 7010.SR):", "7010.SR")
    st.write("---")
    st.write(f"📅 **تاريخ النظام:** {datetime.now().strftime('%Y-%m-%d')}")

# جلب البيانات
info, ticker_obj = get_stock_data(symbol)

if info:
    # اسم الشركة
    st.markdown(f"<h1 style='text-align:right; color:#1e3a8a;'>🏢 {info['longName']}</h1>", unsafe_allow_html=True)
    
    # صف المؤشرات (مقسمة لـ 2x2 لتناسب الجوال)
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    
    price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
    prev = info.get('previousClose', 1)
    diff = ((price - prev) / prev) * 100
    
    with c1:
        st.metric("السعر الحالي (2026)", f"{price} SAR", f"{diff:.2f}%")
    with c2:
        st.metric("مكرر الربحية P/E", info.get('trailingPE', 'N/A'))
    with c3:
        st.metric("أعلى سعر/سنة", info.get('fiftyTwoWeekHigh', 'N/A'))
    with c4:
        div = info.get('dividendYield', 0)
        st.metric("توزيعات الأرباح", f"{div*100:.2f}%" if div else "0%")

    st.write("---")

    # التبويبات للرسم البياني والذكاء الاصطناعي
    tab_chart, tab_ai = st.tabs(["📈 تحركات السهم المباشرة", "🤖 استشارة المستشار الذكي"])
    
    with tab_chart:
        st.subheader("أداء السهم في آخر 6 أشهر")
        hist = ticker_obj.history(period="6mo")
        if not hist.empty:
            st.area_chart(hist['Close'])
            st.caption(f"آخر تحديث للبيانات: {hist.index[-1].strftime('%Y-%m-%d')}")

    with tab_ai:
        st.subheader("التحليل المالي المدعوم بالذكاء الاصطناعي")
        user_q = st.text_input("اسأل المستشار عن هذا السهم:", "هل السهم فرصة جيدة للاستثمار في 2026؟")
        if st.button("تحليل البيانات فوراً"):
            with st.spinner("جاري قراءة مؤشرات السوق..."):
                answer = ask_ai(f"حلل شركة {info['longName']} سعره {price}. السؤال: {user_q}")
                # عرض الإجابة في صندوق ملون واضح
                st.markdown(f"""
                <div style='background-color: #e2e8f0; padding: 20px; border-radius: 10px; border-left: 5px solid #1e3a8a; color: #000000;'>
                {answer}
                </div>
                """, unsafe_allow_html=True)

else:
    st.error("❌ رمز السهم غير صحيح أو البيانات غير متوفرة حالياً.")

# --- تذييل الصفحة (الحقوق) ---
st.markdown(f"""
    <div class="footer">
        <p>Developed & Designed by: ALHANOUF ALBATTAH © 2026</p>
        <p style='font-size: 0.8em;'>Real-Time Financial Intelligence Terminal</p>
    </div>
    """, unsafe_allow_html=True)
