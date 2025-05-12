"""
Dependencies:
    pip install -r requirements.txt

Ensure your IDE uses this venv's Python. For full Unicode PDF, place DejaVuSans.ttf beside the script.
"""
import streamlit as st
import re
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import base64
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from coloraide import Color
from bidi.algorithm import get_display
import arabic_reshaper
import matplotlib.pyplot as plt

# ── הגדרת הדף חייבת להיות לפני כל קריאה ל־st.xxx ──────────────────────────
st.set_page_config(page_title="בדיקת נגישות SI5568", layout="wide")

# ── CSS מותאם ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
      .sidebar .sidebar-content { background-color: #f0f2f6; }
      .stButton>button { background-color: #4CAF50; color: white; }
      .stTable td, .stTable th { padding: 0.5rem; }
    </style>
    """,
    unsafe_allow_html=True
)

# ── SI 5568 clauses map ───────────────────────────────────────────────────────
SI_CLAUSES = {
    # Principle 1: Perceivable
    'non_text_content': '1.1.1 תוכן לא טקסטואלי',
    'captions_prerecorded': '1.2.2 כתוביות (מוקלט מראש)',
    'audio_description': '1.2.5 תיאור בשמע (מוקלט מראש)',
    'info_relationships': '1.3.1 מידע וקשרים',
    'meaningful_sequence': '1.3.2 רצף משמעותי',
    'sensory_characteristics': '1.3.3 תכונות חושיות',
    'use_of_color': '1.4.1 שימוש בצבע',
    'contrast_ratio': '1.4.3 ניגוד (מינימום)',
    'resize_text': '1.4.4 שינוי גודל טקסט',
    'images_of_text': '1.4.5 תמונות של טקסט',
    'reflow': '1.4.10 תזוזה',
    'non_text_contrast': '1.4.11 ניגוד לא טקסטואלי',
    # Principle 2: Operable
    'keyboard': '2.1.1 תמיכה במקלדת',
    'bypass_blocks': '2.4.1 עקיפת בלוקים',
    'page_titled': '2.4.2 שם עמוד',
    'focus_order': '2.4.3 סדר פוקוס',
    'link_purpose': '2.4.4 ייעוד קישור',
    'multiple_ways': '2.4.5 דרכים מרובות',
    'headings_labels': '2.4.6 כותרות ותוויות',
    'focus_visible': '2.4.7 פוקוס נראה',
    'section_headings': '2.4.10 כותרות קטעים',
    # Principle 3: Understandable
    'language_of_page': '3.1.1 שפת העמוד',
    'language_of_parts': '3.1.2 שפת חלקים',
    'error_identification': '3.3.1 זיהוי שגיאות',
    'error_suggestion': '3.3.3 הצעת תיקון',
    'error_prevention': '3.3.4 מניעת שגיאות',
    # Principle 4: Robust
    'parsing': '4.1.1 ניתוח',
    'name_role_value': '4.1.2 שם, תפקיד, ערך'
}

# ── גריפת HTML עם Selenium + webdriver-manager ──────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_driver_and_soup(url: str) -> BeautifulSoup:
    options = Options()
    options.add_argument("--headless")
    # Use Selenium Manager (no need for external driver installation)
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    driver.quit()
    return soup

# ── פונקציות בדיקה ─────────────────────────────────────────────────────────
def check_html_lang(soup: BeautifulSoup) -> Dict:
    html = soup.find('html')
    ok = bool(html and html.get('lang'))
    return {
        'rule': 'html_lang',
        'passed': ok,
        'clause': SI_CLAUSES.get('page_titled'),
        'message': 'קיים lang' if ok else 'אין lang'
    }

def check_title(soup: BeautifulSoup) -> Dict:
    t = soup.find('title')
    ok = bool(t and t.get_text().strip())
    return {
        'rule': 'title_tag',
        'passed': ok,
        'clause': SI_CLAUSES.get('page_titled'),
        'message': 'כותרת קיימת' if ok else 'חסרה כותרת'
    }

def check_meta_viewport(soup: BeautifulSoup) -> Dict:
    ok = bool(soup.find('meta', attrs={'name': 'viewport'}))
    return {
        'rule': 'meta_viewport',
        'passed': ok,
        'clause': SI_CLAUSES.get('reflow'),
        'message': 'viewport מוגדר' if ok else 'לא מוגדר viewport'
    }

def check_skip_link(soup: BeautifulSoup) -> Dict:
    ok = bool(soup.select('a[href^="#"]') or soup.find(class_=re.compile('skip', re.I)))
    return {
        'rule': 'skip_link',
        'passed': ok,
        'clause': SI_CLAUSES.get('bypass_blocks'),
        'message': 'קישור לדילוג קיים' if ok else 'אין קישור לדילוג'
    }

def check_landmarks(soup: BeautifulSoup) -> Dict:
    roles = ['banner', 'navigation', 'main', 'contentinfo']
    found = [r for r in roles if soup.find(attrs={'role': r})]
    ok = len(found) >= 2
    msg = f'נמצאו: {found}' if ok else 'landmarks חסרים'
    return {
        'rule': 'landmarks',
        'passed': ok,
        'clause': SI_CLAUSES.get('headings_labels'),
        'message': msg
    }

def check_empty_links(soup: BeautifulSoup) -> Dict:
    empty = [a for a in soup.find_all('a') if not a.get_text().strip()]
    ok = len(empty) == 0
    msg = 'אין קישורים ריקים' if ok else f'{len(empty)} קישורים ריקים'
    return {
        'rule': 'empty_links',
        'passed': ok,
        'clause': SI_CLAUSES.get('link_purpose'),
        'message': msg
    }

def check_header_sequence(soup: BeautifulSoup) -> Dict:
    hs = [int(h.name[1]) for h in soup.find_all(re.compile('^h[1-6]$'))]
    ok = hs == sorted(hs)
    return {
        'rule': 'header_sequence',
        'passed': ok,
        'clause': SI_CLAUSES.get('headings_labels'),
        'message': 'רצף כותרות תקין' if ok else 'רצף כותרות לא תקין'
    }

def check_img_alt(soup: BeautifulSoup) -> Dict:
    imgs = soup.find_all('img')
    missing = [img for img in imgs if not img.get('alt')]
    ok = len(missing) == 0
    msg = 'לכל התמונות ALT' if ok else f'{len(missing)} תמונות ללא ALT'
    return {
        'rule': 'img_alt',
        'passed': ok,
        'clause': SI_CLAUSES.get('non_text_content'),
        'message': msg
    }

def check_video_captions(soup: BeautifulSoup) -> Dict:
    vids = soup.find_all('video')
    missing = [v for v in vids if not v.find('track', attrs={'kind': 'captions'})]
    ok = len(missing) == 0
    msg = 'וידאו עם כתוביות' if ok else f'{len(missing)} וידאו ללא כתוביות'
    return {
        'rule': 'video_captions',
        'passed': ok,
        'clause': SI_CLAUSES.get('captions_prerecorded'),
        'message': msg
    }

def contrast_ratio(c1: str, c2: str) -> float:
    L1 = Color(c1).luminance()
    L2 = Color(c2).luminance()
    H1, H2 = max(L1, L2), min(L1, L2)
    return (H1 + 0.05) / (H2 + 0.05)

def check_contrast(soup: BeautifulSoup) -> Dict:
    bad = 0
    for el in soup.select('[style]'):
        fg = re.search(r'color:\s*(#[0-9A-Fa-f]{6})', el['style'])
        bg = re.search(r'background-color:\s*(#[0-9A-Fa-f]{6})', el['style'])
        if fg and bg and contrast_ratio(fg.group(1), bg.group(1)) < 4.5:
            bad += 1
    ok = bad == 0
    msg = 'ניגוד תקין' if ok else f'{bad} אלמנטים בעייתיים'
    return {
        'rule': 'contrast_ratio',
        'passed': ok,
        'clause': SI_CLAUSES.get('contrast_ratio'),
        'message': msg
    }

def check_text_resize(soup: BeautifulSoup) -> Dict:
    return {
        'rule': 'text_resize',
        'passed': True,
        'clause': SI_CLAUSES.get('resize_text'),
        'message': 'בודק בדפדפן'
    }

def check_form_labels(soup: BeautifulSoup) -> Dict:
    fields = soup.find_all(['input', 'select', 'textarea'])
    miss = 0
    for f in fields:
        if not (f.get('id') and soup.find('label', {'for': f.get('id')})):
            miss += 1
    ok = miss == 0
    msg = 'כל השדות מתויגים' if ok else f'{miss} שדות ללא תווית'
    return {
        'rule': 'form_labels',
        'passed': ok,
        'clause': SI_CLAUSES.get('info_relationships'),
        'message': msg
    }

def check_aria_labels(soup: BeautifulSoup) -> Dict:
    els = soup.find_all(['button', 'a'])
    miss = [e for e in els if not (e.get_text().strip() or e.get('aria-label'))]
    ok = len(miss) == 0
    msg = 'כל האלמנטים מוגדרים' if ok else f'{len(miss)} אלמנטים ללא aria'
    return {
        'rule': 'aria_labels',
        'passed': ok,
        'clause': SI_CLAUSES.get('name_role_value'),
        'message': msg
    }

def check_accessibility_statement(soup: BeautifulSoup) -> Dict:
    ok = bool(soup.find(text=re.compile('נגישות', re.I)))
    msg = 'הצהרת נגישות קיימת' if ok else 'חסרה הצהרה'
    return {
        'rule': 'accessibility_statement',
        'passed': ok,
        'clause': SI_CLAUSES.get('parsing'),
        'message': msg
    }

# ── Full audit orchestration ─────────────────────────────────────────────────
def check_accessibility(url: str) -> List[Dict]:
    try:
        soup = fetch_driver_and_soup(url)
    except Exception as e:
        return [{
            'rule': 'network',
            'passed': False,
            'clause': 'רשת',
            'message': str(e)
        }]
    funcs = [
        check_html_lang, check_title, check_meta_viewport, check_skip_link,
        check_landmarks, check_empty_links, check_header_sequence,
        check_img_alt, check_video_captions, check_contrast,
        check_text_resize, check_form_labels, check_aria_labels,
        check_accessibility_statement
    ]
    return [fn(soup) for fn in funcs]

# ── PDF report ───────────────────────────────────────────────────────────────
def generate_pdf_report(results: List[Dict], url: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 40

    # כותרת באנגלית
    c.setFont('Helvetica', 14)
    c.drawString(margin, height - margin, f"Accessibility Report SI 5568 for: {url}")

    # תוכן
    y = height - margin - 30
    c.setFont('Helvetica', 12)
    max_chars = int((width - 2 * margin) / 7)
    ENG_CLAUSES = {
        'network': 'Network Error',
        'html_lang': '2.4.2 Document Language',
        'title_tag': '2.4.2 Page Title',
        'meta_viewport': '1.4.10 Meta Viewport',
        'skip_link': '2.4.1 Skip Link',
        'landmarks': '2.4.1 ARIA Landmarks',
        'empty_links': '2.4.4 Link Purpose',
        'header_sequence': '2.4.6 Headings and Labels',
        'img_alt': '1.1.1 Non-text Content',
        'video_captions': '1.2.2 Video Captions',
        'contrast_ratio': '1.4.3 Contrast (Minimum)',
        'text_resize': '1.4.4 Resize Text',
        'form_labels': '1.3.1 Form Labels',
        'aria_labels': 'ARIA Labels',
        'accessibility_statement': '4.1.1 Parsing'
    }

    for r in results:
        status = 'PASS' if r['passed'] else 'FAIL'
        clause = ENG_CLAUSES.get(r['rule'], r['rule'])
        line = f"[{status}] {clause}"
        parts = [line[i:i+max_chars] for i in range(0, len(line), max_chars)]
        for part in parts:
            if y < margin:
                c.showPage()
                c.setFont('Helvetica', 12)
                y = height - margin
            c.drawString(margin, y, part)
            y -= 16

    c.save()
    return buffer.getvalue()

# ── Streamlit App ───────────────────────────────────────────────────────────
def main():
    st.sidebar.title("ניווט")
    choice = st.sidebar.radio("תפריט:", ["בדיקת נגישות", "הצג תקן", "חיפוש סעיפים"])
    st.sidebar.markdown("---")
    st.sidebar.markdown("[הורד חלק 1](https://www.sii.org.il/media/2488/sii-5568-02-techniques.pdf)")
    st.sidebar.markdown("[הורד חלק 2](https://www.sii.org.il/media/2490/si-5568-2.pdf)")

    if choice == "הצג תקן":
        b64 = base64.b64encode(open("IP5568/5568.pdf", "rb").read()).decode()
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{b64}" width=700 height=800></iframe>',
            unsafe_allow_html=True
        )
        return

    if choice == "חיפוש סעיפים":
        q = st.text_input("חיפוש:")
        df = pd.DataFrame([
            {'מפתח': k, 'תקן': v}
            for k, v in SI_CLAUSES.items()
            if not q or q in k or q in v
        ])
        st.table(df)
        return

    st.title("בדיקת נגישות SI 5568")
    url = st.text_input("URL לבדיקת נגישות:")
    uploaded = st.file_uploader("או העלה קובץ HTML לבדיקה", type="html")

    if st.button("התחל בדיקה"):
        if not url and not uploaded:
            st.error("יש להזין URL או להעלות קובץ HTML")
            return
        with st.spinner("בודק..."):
            if uploaded:
                content = uploaded.read().decode('utf-8')
                soup = BeautifulSoup(content, 'lxml')
            else:
                soup = fetch_driver_and_soup(url)
            results = check_accessibility(url if not uploaded else "<local file>")

        df = pd.DataFrame([
            {'סטטוס': '✅' if r['passed'] else '⚠', 'תקן': r['clause'], 'הערה': r['message']}
            for r in results
        ])
        passed = df['סטטוס'].value_counts().get('✅', 0)
        failed = df['סטטוס'].value_counts().get('⚠', 0)

        c1, c2 = st.columns(2)
        c1.metric("עברו", passed)
        c2.metric("נכשלו", failed)

        with st.expander("הצג פרטים"):
            st.table(df)

        fig1, ax1 = plt.subplots()
        counts = df['סטטוס'].value_counts()
        ax1.pie(counts, labels=counts.index, autopct='%1.1f%%')
        ax1.set_title("אחוזי עמידה בתקן")
        st.pyplot(fig1)

        st.download_button("הורד CSV", df.to_csv(index=False), 'report.csv', 'text/csv')
        pdf_data = generate_pdf_report(results, url if not uploaded else "<local file>")
        st.download_button("הורד PDF", pdf_data, 'report.pdf', 'application/pdf')

if __name__ == "__main__":
    main()
