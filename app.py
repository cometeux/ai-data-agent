# -*- coding: utf-8 -*-
import html
import json
import pandas as pd
import streamlit as st
import plotly.express as px
from openai import OpenAI

st.set_page_config(
    page_title="Data Analysis AI Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------------
# Localization (EN / AR)
# -----------------------------
TRANSLATIONS = {
    "en": {
        "app_title": "Data Analysis AI Agent",
        "badge": "AI-Powered Analytics",
        "hero_desc": "Upload your dataset, and I'll automatically generate insights, visual summaries, and actionable recommendations.",
        "data_source": "Data Source",
        "drag_drop": "Drag & drop your dataset",
        "supports": "Supports CSV, XLSX up to 50MB",
        "browse_files": "Browse files",
        "dataset_overview": "Dataset Overview",
        "data_type": "Data Type",
        "shape": "Shape",
        "total_rows": "Total Rows",
        "total_columns": "Total Columns",
        "preview_rows": "Preview Rows",
        "data_preview": "Data Preview",
        "generate_summary": "Generate Summary and Charts",
        "analysis_summary": "Analysis Summary",
        "overview": "Overview",
        "overview_sub": "General trends and descriptive stats",
        "key_insights": "Key Insights",
        "key_insights_sub": "Anomalies, correlations, and highlights",
        "recommendations": "Recommendations",
        "recommendations_sub": "Actionable next steps based on data",
        "final_summary": "Final Summary",
        "final_summary_sub": "Executive brief and conclusion",
        "visualizations": "Visualizations",
        "ask_ai_placeholder": "Ask AI to slice the data, find specific metrics, or generate new charts...",
        "ask_questions": "Ask questions about your data",
        "theme_dark": "Dark",
        "theme_light": "Light",
        "lang_en": "English",
        "lang_ar": "العربية",
        "chart_not_available": "Chart not available",
        "analyzing": "Analyzing data...",
        "file_meta": "{size} MB • {rows:,} rows",
    },
    "ar": {
        "app_title": "وكيل تحليل البيانات بالذكاء الاصطناعي",
        "badge": "تحليلات مدعومة بالذكاء الاصطناعي",
        "hero_desc": "ارفع مجموعة البيانات وسأقوم تلقائياً بتوليد الرؤى والملخصات المرئية والتوصيات القابلة للتطبيق.",
        "data_source": "مصدر البيانات",
        "drag_drop": "اسحب وأفلت مجموعة البيانات",
        "supports": "يدعم CSV و XLSX حتى 50 ميجابايت",
        "browse_files": "استعراض الملفات",
        "dataset_overview": "نظرة عامة على مجموعة البيانات",
        "data_type": "نوع البيانات",
        "shape": "الشكل",
        "total_rows": "إجمالي الصفوف",
        "total_columns": "إجمالي الأعمدة",
        "preview_rows": "صفوف المعاينة",
        "data_preview": "معاينة البيانات",
        "generate_summary": "إنشاء الملخص والرسوم البيانية",
        "analysis_summary": "ملخص التحليل",
        "overview": "نظرة عامة",
        "overview_sub": "الاتجاهات العامة والإحصائيات الوصفية",
        "key_insights": "رؤى أساسية",
        "key_insights_sub": "شذوذات وارتباطات ونقاط بارزة",
        "recommendations": "التوصيات",
        "recommendations_sub": "خطوات قابلة للتطبيق بناءً على البيانات",
        "final_summary": "الملخص النهائي",
        "final_summary_sub": "ملخص تنفيذي واستنتاج",
        "visualizations": "المرئيات",
        "ask_ai_placeholder": "اسأل الذكاء الاصطناعي لتقسيم البيانات أو إيجاد مقاييس أو إنشاء رسوم...",
        "ask_questions": "اسأل عن بياناتك",
        "theme_dark": "داكن",
        "theme_light": "فاتح",
        "lang_en": "English",
        "lang_ar": "العربية",
        "chart_not_available": "الرسم غير متوفر",
        "analyzing": "جاري التحليل...",
        "file_meta": "{size} ميجابايت • {rows:,} صف",
    },
}


def t(key):
    lang = st.session_state.get("lang", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


# -----------------------------
# Session state
# -----------------------------
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = None
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "lang" not in st.session_state:
    st.session_state.lang = "en"


# -----------------------------
# Helpers
# -----------------------------
def reset_app_state():
    st.session_state.analysis_result = None
    st.session_state.chat_history = []
    st.session_state.last_uploaded_name = None


def load_data(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    return pd.read_excel(uploaded_file)


def file_size_mb(uploaded_file):
    return round(uploaded_file.size / (1024 * 1024), 1)


def infer_data_types(df):
    kinds = set()
    for col in df.columns:
        dtype = str(df[col].dtype)
        if "int" in dtype or "float" in dtype:
            kinds.add("Numeric")
        elif "object" in dtype or "category" in dtype:
            kinds.add("Categorical")
        elif "datetime" in dtype:
            kinds.add("Time-series")
    return ", ".join(sorted(kinds)) if kinds else "Mixed"


def ask_agent_for_analysis(df):
    columns = list(df.columns)
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
    sample_rows = df.head(10).to_dict(orient="records")
    prompt = f"""
You are a professional data analysis AI agent.
Analyze the uploaded dataset and return ONLY valid JSON.
Dataset columns: {columns}
Dataset types: {dtypes}
Sample rows: {sample_rows}
Return JSON in exactly this structure:
{{
  "summary": {{
    "overview": "brief overview of the dataset",
    "key_insights": ["insight 1", "insight 2", "insight 3"],
    "recommendations": ["recommendation 1", "recommendation 2"],
    "final_summary": "clear professional final summary"
  }},
  "charts": [
    {{ "title": "chart title", "chart_type": "bar", "x_column": "exact column name", "y_column": "exact column name", "aggregation": "sum" }},
    {{ "title": "chart title", "chart_type": "line", "x_column": "exact column name", "y_column": "exact column name", "aggregation": "mean" }}
  ]
}}
Rules: Return at least 2 charts; chart_type: bar, line, pie, scatter; aggregation: sum, mean, count, none; use exact column names; keep summary concise.
"""
    response = client.responses.create(model="gpt-4.1-mini", input=prompt)
    return json.loads(response.output_text)


def ask_agent_question(df, analysis_result, user_question):
    columns = list(df.columns)
    sample_rows = df.head(10).to_dict(orient="records")
    prompt = f"""
You are a helpful data analysis AI agent.
Dataset columns: {columns}
Sample rows: {sample_rows}
Existing analysis: {json.dumps(analysis_result, ensure_ascii=False)}
User question: {user_question}
Answer clearly and directly based only on the uploaded data and existing analysis.
"""
    response = client.responses.create(model="gpt-4.1-mini", input=prompt)
    return response.output_text


def prepare_chart_data(df, x_column, y_column, aggregation):
    data = df.copy()
    if aggregation == "sum":
        data = data.groupby(x_column, as_index=False)[y_column].sum()
    elif aggregation == "mean":
        data = data.groupby(x_column, as_index=False)[y_column].mean()
    elif aggregation == "count":
        data = data.groupby(x_column, as_index=False).size()
        data.columns = [x_column, "count"]
        y_column = "count"
    return data, y_column


def render_chart_fig(df, chart, is_dark):
    chart_type = chart.get("chart_type", "bar")
    x_column = chart.get("x_column")
    y_column = chart.get("y_column")
    aggregation = chart.get("aggregation", "sum")
    title = chart.get("title", "Chart")
    if not x_column or not y_column:
        return None
    data, final_y = prepare_chart_data(df, x_column, y_column, aggregation)
    if chart_type == "bar":
        fig = px.bar(data, x=x_column, y=final_y, title=None, template="plotly_white")
    elif chart_type == "line":
        fig = px.line(data, x=x_column, y=final_y, title=None, template="plotly_white")
    elif chart_type == "pie":
        fig = px.pie(data, names=x_column, values=final_y, title=None)
    elif chart_type == "scatter":
        fig = px.scatter(data, x=x_column, y=final_y, title=None, template="plotly_white")
    else:
        return None
    if is_dark:
        fig.update_layout(
            paper_bgcolor="rgba(18,18,22,0.35)",
            plot_bgcolor="rgba(18,18,22,0.15)",
            font=dict(color="#F3F4F6", size=12),
            margin=dict(l=24, r=24, t=12, b=24),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.06)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.06)")
        )
    else:
        fig.update_layout(
            paper_bgcolor="rgba(255,255,255,0.6)",
            plot_bgcolor="rgba(248,250,252,0.8)",
            font=dict(color="#0f172a", size=12),
            margin=dict(l=24, r=24, t=12, b=24),
            xaxis=dict(gridcolor="rgba(15,23,42,0.08)", zerolinecolor="rgba(15,23,42,0.1)"),
            yaxis=dict(gridcolor="rgba(15,23,42,0.08)", zerolinecolor="rgba(15,23,42,0.1)")
        )
    return fig


# -----------------------------
# Premium CSS (reference-fidelity + light + RTL + animations)
# -----------------------------
def inject_css(theme, lang):
    is_dark = theme == "dark"
    is_rtl = lang == "ar"

    if is_dark:
        bg_base = "#060608"
        text_primary = "#F3F4F6"
        text_secondary = "#9CA3AF"
        glass_panel = "rgba(18, 18, 22, 0.6)"
        border_subtle = "rgba(255, 255, 255, 0.06)"
        border_highlight = "rgba(255, 255, 255, 0.12)"
        border_left_glass = "rgba(255, 255, 255, 0.09)"
        border_card = "rgba(255, 255, 255, 0.08)"
        th_bg = "rgba(255, 255, 255, 0.02)"
        td_border = "rgba(255, 255, 255, 0.03)"
        shadow_glass = "0 24px 48px rgba(0, 0, 0, 0.6)"
        dot_opacity = "0.6"
        dot_opacity_2 = "0.4"
    else:
        bg_base = "#eef2f7"
        text_primary = "#0c1222"
        text_secondary = "#334155"
        glass_panel = "rgba(255, 255, 255, 0.88)"
        border_subtle = "rgba(15, 23, 42, 0.1)"
        border_highlight = "rgba(15, 23, 42, 0.14)"
        border_left_glass = "rgba(15, 23, 42, 0.08)"
        border_card = "rgba(15, 23, 42, 0.12)"
        th_bg = "rgba(15, 23, 42, 0.05)"
        td_border = "rgba(15, 23, 42, 0.08)"
        shadow_glass = "0 24px 48px rgba(15, 23, 42, 0.1)"
        dot_opacity = "0.35"
        dot_opacity_2 = "0.2"

    rtl_extra = ""
    if is_rtl:
        rtl_extra = """
        [data-testid="stAppViewContainer"] { direction: rtl; }
        .block-container { text-align: right; }
        .hero { text-align: center; }
        .ref-list-item { flex-direction: row-reverse; }
        .ref-text-box { text-align: right; }
        .chart-header { flex-direction: row-reverse; }
        .table-wrap table { direction: rtl; text-align: right; }
        [data-testid="column"] { text-align: right; }
        """

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap');

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, .stApp, [data-testid="stAppViewContainer"] {{
    font-family: {"'IBM Plex Sans Arabic', 'Inter', sans-serif" if lang == "ar" else "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"} !important;
    background-color: {bg_base} !important;
    color: {text_primary} !important;
    line-height: {"1.6" if lang == "ar" else "1.5"};
}}
[data-testid="stAppViewContainer"] > section {{ background: transparent !important; }}

/* Single container: max-width 1100px, consistent padding. No layout hacks. */
.block-container {{
    max-width: 1100px !important;
    margin: 0 auto !important;
    padding: 60px 24px 160px !important;
}}

/* Sidebar utility bar only - does not affect main content */
[data-testid="stSidebar"] .stRadio label {{ font-size: 0.8125rem; }}
[data-testid="stSidebar"] > div {{ padding: 1rem 1rem 0; }}

/* Design body background: 6 radial gradients, 150px, fixed */
.stApp::before {{
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 0;
    background-image: {"radial-gradient(1px 1px at 10% 10%, rgba(255,255,255,0.6) 100%, transparent), radial-gradient(1.5px 1.5px at 80% 20%, rgba(255,255,255,0.4) 100%, transparent), radial-gradient(1px 1px at 30% 60%, rgba(255,255,255,0.7) 100%, transparent), radial-gradient(2px 2px at 70% 80%, rgba(255,255,255,0.3) 100%, transparent), radial-gradient(1px 1px at 50% 30%, rgba(255,255,255,0.5) 100%, transparent), radial-gradient(1.5px 1.5px at 90% 90%, rgba(255,255,255,0.6) 100%, transparent)" if is_dark else "radial-gradient(1px 1px at 10% 10%, rgba(15,23,42,0.35) 100%, transparent), radial-gradient(1.5px 1.5px at 80% 20%, rgba(15,23,42,0.2) 100%, transparent), radial-gradient(1px 1px at 30% 60%, rgba(15,23,42,0.3) 100%, transparent)"};
    background-size: 150px 150px;
    background-attachment: fixed;
}}
[data-testid="stAppViewContainer"] {{ position: relative; z-index: 1; }}

/* Design body::after noise overlay */
.stApp::after {{
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 9999;
    opacity: {0.12 if is_dark else 0};
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
    mix-blend-mode: overlay;
}}

/* Light flares (dark only) */
/* Design light flares */
.light-flare-1 {{
    position: fixed;
    top: -10vh; left: 50%;
    transform: translateX(-50%);
    width: 30vw; height: 90vh;
    background: radial-gradient(ellipse 50% 100% at top center, rgba(79, 70, 229, 0.4) 0%, transparent 100%);
    pointer-events: none;
    z-index: 0;
    filter: blur(50px);
}}
.light-flare-2 {{
    position: fixed;
    top: -5vh; left: 50%;
    transform: translateX(-50%);
    width: 8vw; height: 70vh;
    background: radial-gradient(ellipse 50% 100% at top center, rgba(147, 51, 234, 0.7) 0%, transparent 100%);
    pointer-events: none;
    z-index: 0;
    filter: blur(30px);
}}

/* Animations */
@keyframes heroReveal {{
    from {{ opacity: 0; transform: translateY(-12px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes orbGlow {{
    0%, 100% {{ box-shadow: 0 0 30px rgba(168, 85, 247, 0.5), inset 0 -4px 12px rgba(0,0,0,0.3); }}
    50% {{ box-shadow: 0 0 40px rgba(168, 85, 247, 0.65), inset 0 -4px 12px rgba(0,0,0,0.3); }}
}}

.hero {{ animation: heroReveal 0.6s ease-out; }}
.hero-orb {{ animation: orbGlow 4s ease-in-out infinite; }}

/* Header bar (theme + language) */
.header-bar {{
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 12px;
    margin-bottom: 8px;
}}
.header-bar .lang-btn {{
    padding: 8px 14px;
    border-radius: 12px;
    border: 1px solid {border_card};
    background: rgba(255,255,255,{"0.06" if is_dark else "0.5"});
    color: {text_primary};
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.25s ease;
}}
.header-bar .lang-btn:hover {{
    background: rgba(255,255,255,{"0.1" if is_dark else "0.7"});
}}
.header-bar .lang-btn.active {{
    background: linear-gradient(135deg, #4F46E5, #9333EA);
    color: white;
    border-color: rgba(255,255,255,0.2);
}}
.theme-toggle {{ display: flex; gap: 4px; }}
.theme-toggle label {{ cursor: pointer; font-size: 0.8rem; color: {text_secondary}; padding: 6px 10px; border-radius: 10px; transition: all 0.2s; }}
.theme-toggle label:hover {{ color: {text_primary}; background: rgba(255,255,255,{"0.05" if is_dark else "0.1"}); }}

/* Hero */
/* Design hero */
.hero {{
    text-align: center;
    margin-bottom: 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
}}
.hero-orb {{
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #ffffff 0%, #A855F7 40%, #4F46E5 100%);
    box-shadow: 0 0 30px rgba(168, 85, 247, 0.5), inset 0 -4px 12px rgba(0,0,0,0.5);
    margin-bottom: 8px;
}}
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    font-size: 0.85rem;
    font-weight: 500;
    color: #E0E7FF;
}}
.badge svg {{ color: #A855F7; }}
.hero h1 {{
    font-size: 2.5rem;
    font-weight: 500;
    letter-spacing: -0.02em;
    color: {text_primary} !important;
    line-height: 1.2;
}}
.hero-desc, .hero p {{
    color: {text_secondary} !important;
    font-size: 1.05rem;
    max-width: 500px;
    line-height: 1.55;
}}

/* Glass panels */
/* Design glass-panel */
.glass-panel {{
    background: {glass_panel};
    backdrop-filter: blur(32px);
    -webkit-backdrop-filter: blur(32px);
    border: 1px solid {border_subtle};
    border-top: 1px solid {border_highlight};
    border-left: 1px solid {border_left_glass};
    border-radius: 24px;
    box-shadow: {shadow_glass};
    padding: 32px;
    transition: all 0.3s ease;
}}
.glass-panel:hover {{
    transform: translateY(-1px);
    box-shadow: {"0 28px 56px rgba(0,0,0,0.5)" if is_dark else "0 28px 56px rgba(15,23,42,0.14)"};
}}

/* Design section-title */
.section-title {{
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 16px;
    color: {text_secondary} !important;
}}

/* Design dropzone */
.dropzone, .dropzone-outer {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
    border: 1px dashed rgba(255,255,255,0.15);
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.01);
    transition: all 0.3s ease;
    text-align: center;
}}
.dropzone:hover, .dropzone-outer:hover {{
    border-color: rgba(168, 85, 247, 0.5);
    background: rgba(168, 85, 247, 0.05);
}}
.dropzone-icon {{
    width: 48px; height: 48px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 16px;
    color: {text_primary};
}}
.dropzone h3, .dropzone-outer h3 {{ font-weight: 500; margin-bottom: 8px; font-size: 1rem; }}
.dropzone p, .dropzone-outer p {{ color: {text_secondary}; font-size: 0.9rem; }}
/* Uploader: keep inside container, no overflow */
.uploader-wrap {{ width: 100%; max-width: 100%; overflow: hidden; box-sizing: border-box; }}
[data-testid="stFileUploader"] {{
    background: transparent !important; border: none !important; padding: 0 !important;
    width: 100% !important; max-width: 100% !important; box-sizing: border-box !important;
}}
[data-testid="stFileUploader"] section {{ max-width: 100% !important; }}
[data-testid="stFileUploader"] label {{ color: {text_primary} !important; font-weight: 500 !important; }}

/* Design dashboard-grid, overview-card */
.dashboard-grid {{ display: grid; grid-template-columns: 1fr 2fr; gap: 24px; }}
.overview-card {{ display: flex; flex-direction: column; gap: 12px; }}
@media (max-width: 900px) {{ .dashboard-grid {{ grid-template-columns: 1fr; }} }}

/* Design ref-list-item, ref-icon-box, ref-text-box */
.ref-list-item {{
    display: flex;
    align-items: center;
    padding: 12px 8px;
    background: transparent;
    border-radius: 10px;
    gap: 16px;
    transition: background 0.2s ease;
}}
.ref-list-item:hover {{ background: rgba(255, 255, 255, 0.03); }}
.ref-icon-box {{
    width: 36px;
    height: 36px;
    min-width: 36px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid {border_card};
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #E5E7EB !important;
}}
.ref-text-box {{ flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }}
.ref-title {{ font-size: 0.95rem; font-weight: 500; color: {text_primary} !important; }}
.ref-subtitle {{ font-size: 0.8rem; color: {text_secondary} !important; }}
.ref-action-box {{ width: 32px; height: 32px; display: flex; align-items: center; justify-content: flex-end; color: #A855F7; }}

/* Design kpi-grid, kpi-card */
.kpi-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; height: 100%; }}
.kpi-card {{
    background: transparent;
    border-radius: 16px;
    border: 1px solid {border_card};
    padding: 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}
.kpi-label {{
    color: {text_secondary} !important;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}}
.kpi-value {{
    font-size: 1.75rem;
    font-weight: 500;
    letter-spacing: -0.02em;
    color: {text_primary} !important;
}}

/* Design table-container */
.table-container, .table-wrap {{
    width: 100%;
    overflow-x: auto;
    border-radius: 16px;
    border: 1px solid {border_card};
    background: transparent;
}}
.table-container table, .table-wrap table {{ width: 100%; border-collapse: collapse; text-align: left; }}
.table-container th, .table-wrap th {{
    color: {text_secondary} !important;
    font-weight: 500;
    border-bottom: 1px solid {border_card};
    background: {th_bg} !important;
    padding: 16px 20px;
    font-size: 0.9rem;
}}
.table-container td, .table-wrap td {{
    border-bottom: 1px solid {td_border};
    color: {text_primary} !important;
    padding: 16px 20px;
    font-size: 0.9rem;
}}
.table-container tr:last-child td, .table-wrap tr:last-child td {{ border-bottom: none; }}

/* Design cta-container, btn-primary */
.cta-container {{ display: flex; justify-content: center; margin: 8px 0; }}
.cta-container .stButton > button,
.stButton > button[kind="primary"],
.stButton > button {{
    background: linear-gradient(90deg, #4F46E5, #9333EA) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    padding: 16px 40px !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 32px rgba(147, 51, 234, 0.4) !important;
    transition: all 0.3s ease !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 12px !important;
}}
.stButton > button:hover {{
    box-shadow: 0 12px 40px rgba(147, 51, 234, 0.6) !important;
}}

/* Design analysis-section */
.analysis-section {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }}

/* Design charts-grid, chart-card */
.charts-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }}
.chart-card {{
    background: transparent;
    border-radius: 16px;
    border: 1px solid {border_card};
    padding: 24px;
    min-height: 300px;
    display: flex;
    flex-direction: column;
}}
.chart-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }}
.chart-title {{ font-weight: 500; font-size: 0.95rem; color: {text_primary} !important; }}
.chart-placeholder {{
    flex: 1;
    border-radius: 8px;
    border: 1px dashed rgba(255,255,255,0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    color: {text_secondary};
    font-size: 0.85rem;
    background: rgba(255, 255, 255, 0.01);
}}
@media (max-width: 900px) {{
    .dashboard-grid, .charts-grid, .analysis-section {{ grid-template-columns: 1fr; }}
    .kpi-grid {{ grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }}
}}

/* Design chat-console */
.chat-section-label {{ font-size: 0.85rem; font-weight: 600; color: {text_secondary}; margin-bottom: 12px; margin-top: 40px; }}
[data-testid="stChatInput"] {{
    position: sticky !important;
    bottom: 24px !important;
    margin-top: 40px !important;
    background: linear-gradient(90deg, #5B42F3, #8B5CF6) !important;
    backdrop-filter: blur(40px) !important;
    -webkit-backdrop-filter: blur(40px) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 16px !important;
    padding: 16px 24px !important;
    box-shadow: 0 8px 32px rgba(139, 92, 246, 0.5) !important;
    display: flex !important;
    align-items: center !important;
    gap: 16px !important;
}}
[data-testid="stChatInput"] input {{ flex: 1; background: transparent; border: none; color: #FFFFFF !important; font-size: 1rem !important; outline: none; }}
[data-testid="stChatInput"] input::placeholder {{ color: rgba(255, 255, 255, 0.9); font-weight: 500; }}
[data-testid="stChatMessage"] {{ color: {text_primary} !important; }}

.summary-block {{ margin-bottom: 20px; }}
.summary-block h4 {{ font-size: 0.9375rem; font-weight: 600; color: {text_primary}; margin-bottom: 10px; }}
.summary-block p, .summary-block ul {{ color: {text_secondary}; font-size: 0.9375rem; line-height: 1.6; }}

#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
{rtl_extra}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Render
# -----------------------------
inject_css(st.session_state.theme, st.session_state.lang)

# Top utility: language + theme in sidebar (keeps main layout untouched)
with st.sidebar:
    st.caption("Language")
    lang = st.radio("Language", options=["en", "ar"], format_func=lambda x: "English" if x == "en" else "العربية", index=0 if st.session_state.lang == "en" else 1, key="lang_radio", label_visibility="collapsed")
    st.caption("Theme")
    theme = st.radio("Theme", options=["dark", "light"], format_func=lambda x: "Dark" if x == "dark" else "Light", index=0 if st.session_state.theme == "dark" else 1, key="theme_radio", label_visibility="collapsed")
if lang != st.session_state.lang or theme != st.session_state.theme:
    st.session_state.lang = lang
    st.session_state.theme = theme
    st.rerun()

# Light flares (dark only)
if st.session_state.theme == "dark":
    st.markdown('<div class="light-flare-1"></div><div class="light-flare-2"></div>', unsafe_allow_html=True)

# Hero
st.markdown(f"""
<div class="hero">
    <div class="hero-orb"></div>
    <div class="badge">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
        {t("badge")}
    </div>
    <h1>{t("app_title")}</h1>
    <p class="hero-desc">{t("hero_desc")}</p>
</div>
""", unsafe_allow_html=True)

# Data Source (uploader wrapped to prevent overflow)
st.markdown(f'<div class="glass-panel"><h2 class="section-title">{t("data_source")}</h2><div class="dropzone-outer uploader-wrap">', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    t("drag_drop") + " — " + t("supports"),
    type=["csv", "xlsx"],
    label_visibility="collapsed"
)
st.markdown("</div></div>", unsafe_allow_html=True)

if uploaded_file is None:
    if st.session_state.last_uploaded_name is not None:
        reset_app_state()
    st.stop()

if st.session_state.last_uploaded_name != uploaded_file.name:
    st.session_state.analysis_result = None
    st.session_state.chat_history = []
    st.session_state.last_uploaded_name = uploaded_file.name

try:
    df = load_data(uploaded_file)
    data_types_str = infer_data_types(df)
    size_mb = file_size_mb(uploaded_file)
    n_rows, n_cols = df.shape
    preview_n = min(100, n_rows)

    # Dashboard grid
    st.markdown(f"""
    <div class="dashboard-grid">
        <div class="glass-panel overview-card">
            <h2 class="section-title">{t("dataset_overview")}</h2>
            <div class="ref-list-item">
                <div class="ref-icon-box">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                </div>
                <div class="ref-text-box">
                    <div class="ref-title">{uploaded_file.name}</div>
                    <div class="ref-subtitle">{t("file_meta").format(size=size_mb, rows=n_rows)}</div>
                </div>
            </div>
            <div class="ref-list-item">
                <div class="ref-icon-box" style="color: #A78BFA;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline></svg>
                </div>
                <div class="ref-text-box">
                    <div class="ref-title">{t("data_type")}</div>
                    <div class="ref-subtitle">{data_types_str}</div>
                </div>
            </div>
        </div>
        <div class="glass-panel">
            <h2 class="section-title">{t("shape")}</h2>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">{t("total_rows")}</div>
                    <div class="kpi-value">{n_rows:,}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">{t("total_columns")}</div>
                    <div class="kpi-value">{n_cols}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">{t("preview_rows")}</div>
                    <div class="kpi-value">{preview_n}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Data Preview table
    preview_df = df.head(10)
    thead = "".join(f"<th>{c}</th>" for c in preview_df.columns)
    trows = ""
    for _, row in preview_df.iterrows():
        trows += "<tr>" + "".join(f"<td>{row[c]}</td>" for c in preview_df.columns) + "</tr>"
    st.markdown(f"""
    <div class="glass-panel">
        <h2 class="section-title">{t("data_preview")}</h2>
        <div class="table-container">
            <table><thead><tr>{thead}</tr></thead><tbody>{trows}</tbody></table>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA
    st.markdown('<div class="cta-container">', unsafe_allow_html=True)
    if st.button(t("generate_summary")):
        with st.spinner(t("analyzing")):
            st.session_state.analysis_result = ask_agent_for_analysis(df)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    result = st.session_state.analysis_result

    if result is not None:
        summary = result["summary"]
        charts = result.get("charts", [])

        # Analysis Summary panel
        st.markdown(f"""
        <div class="glass-panel">
            <h2 class="section-title">{t("analysis_summary")}</h2>
            <div class="analysis-section">
                <div class="ref-list-item">
                    <div class="ref-icon-box" style="color: #34D399;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>
                    </div>
                    <div class="ref-text-box">
                        <div class="ref-title">{t("overview")}</div>
                        <div class="ref-subtitle">{t("overview_sub")}</div>
                    </div>
                </div>
                <div class="ref-list-item">
                    <div class="ref-icon-box" style="color: #FBBF24;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path></svg>
                    </div>
                    <div class="ref-text-box">
                        <div class="ref-title">{t("key_insights")}</div>
                        <div class="ref-subtitle">{t("key_insights_sub")}</div>
                    </div>
                </div>
                <div class="ref-list-item">
                    <div class="ref-icon-box" style="color: #60A5FA;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                    </div>
                    <div class="ref-text-box">
                        <div class="ref-title">{t("recommendations")}</div>
                        <div class="ref-subtitle">{t("recommendations_sub")}</div>
                    </div>
                </div>
                <div class="ref-list-item">
                    <div class="ref-icon-box" style="color: #F87171;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
                    </div>
                    <div class="ref-text-box">
                        <div class="ref-title">{t("final_summary")}</div>
                        <div class="ref-subtitle">{t("final_summary_sub")}</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Summary content (escape for HTML)
        def esc(s):
            return html.escape(str(s)) if s else ""
        st.markdown(f'<div class="summary-block"><h4>{t("overview")}</h4><p>{esc(summary.get("overview"))}</p></div>', unsafe_allow_html=True)
        insights_html = "".join(f"<li>{esc(item)}</li>" for item in summary.get("key_insights", []))
        st.markdown(f'<div class="summary-block"><h4>{t("key_insights")}</h4><ul>{insights_html}</ul></div>', unsafe_allow_html=True)
        recs_html = "".join(f"<li>{esc(item)}</li>" for item in summary.get("recommendations", []))
        st.markdown(f'<div class="summary-block"><h4>{t("recommendations")}</h4><ul>{recs_html}</ul></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary-block"><h4>{t("final_summary")}</h4><p>{esc(summary.get("final_summary"))}</p></div>', unsafe_allow_html=True)

        # Visualizations
        st.markdown(f'<div class="glass-panel"><h2 class="section-title">{t("visualizations")}</h2><div class="charts-grid">', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, chart in enumerate(charts):
            with cols[i % 2]:
                title_esc = chart.get("title", "Chart").replace("<", "&lt;").replace(">", "&gt;")
                st.markdown(f'<div class="chart-card"><div class="chart-header"><div class="chart-title">{title_esc}</div></div>', unsafe_allow_html=True)
                fig = render_chart_fig(df, chart, st.session_state.theme == "dark")
                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.markdown(f'<div class="chart-placeholder">{t("chart_not_available")}</div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    # Chat
    st.markdown(f'<div class="chat-section-label">{t("ask_questions")}</div>', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_question = st.chat_input(t("ask_ai_placeholder"))
    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.write(user_question)
        with st.chat_message("assistant"):
            answer = ask_agent_question(df, result if result else {}, user_question)
            st.write(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

except Exception as e:
    st.error(str(e))
