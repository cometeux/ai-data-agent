# -*- coding: utf-8 -*-
import html
import json
import pandas as pd
import streamlit as st
import plotly.express as px
from openai import OpenAI

st.set_page_config(
    page_title="Data Analysis AI Agent",
    page_icon="⚈",
    layout="wide",
    initial_sidebar_state="collapsed"
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
        "generate_summary_short": "Generate Summary",
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
        "suggested_questions": "Suggested questions",
        "q_top_revenue": "Top 5 rows by revenue",
        "q_region_growth": "Which region has the most growth?",
        "q_trends": "What are the main trends?",
        "q_anomalies": "Any anomalies or outliers?",
        "q_recommend": "What do you recommend?",
        "data_quality": "Data quality",
        "duplicates": "Duplicates",
        "missing_vals": "Missing",
        "studio": "Studio",
        "data_health": "Data Health",
        "readiness": "Readiness Score",
        "null_pct": "Null %",
        "dataset_profiling": "Dataset Profiling",
        "rec_measures": "Recommended Measures",
        "business_lens": "Business Lens",
        "quality_metrics": "Quality & Shape Metrics",
        "integrity": "Integrity Score",
        "usable_cols": "Usable Columns",
        "missing_cells": "Missing Cells",
        "top_finding": "Top Finding",
        "biggest_risk": "Biggest Risk",
        "notable_trend": "Notable Trend",
        "chart_studio": "Chart Studio",
        "regen": "Regenerate",
        "ai_insight": "AI Insight",
        "session_memory": "Session Memory",
        "segment_compare": "Segment Compare",
        "primary_segment": "Primary Segment",
        "compare_against": "Compare Against",
        "suggested_q": "Suggested Questions",
        "last_sync": "Last sync",
        "export_csv": "Export CSV",
        "gen_report": "Generate Executive Report",
        "exec": "Exec",
        "analyst": "Analyst",
        "story": "Story",
        "finance_lens": "Finance & Growth",
        "ops_lens": "Operations Efficiency",
        "sales_lens": "Sales Performance",
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
        "generate_summary_short": "إنشاء الملخص",
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
        "suggested_questions": "أسئلة مقترحة",
        "q_top_revenue": "أعلى 5 صفوف حسب الإيرادات",
        "q_region_growth": "أي منطقة لديها أكبر نمو؟",
        "q_trends": "ما الاتجاهات الرئيسية؟",
        "q_anomalies": "أي شذوذ أو قيم متطرفة؟",
        "q_recommend": "ماذا توصي؟",
        "data_quality": "جودة البيانات",
        "duplicates": "التكرارات",
        "missing_vals": "القيم المفقودة",
        "studio": "ستوديو",
        "data_health": "لوحة صحة البيانات",
        "readiness": "درجة الجاهزية",
        "null_pct": "نسبة الفراغات",
        "dataset_profiling": "تحليل مجموعة البيانات",
        "rec_measures": "المقاييس الموصى بها",
        "business_lens": "المنظور التجاري",
        "quality_metrics": "مقاييس الجودة والشكل",
        "integrity": "درجة النزاهة",
        "usable_cols": "الأعمدة القابلة للاستخدام",
        "missing_cells": "الخلايا المفقودة",
        "top_finding": "أبرز النتائج",
        "biggest_risk": "أكبر المخاطر",
        "notable_trend": "اتجاه لافت",
        "chart_studio": "استوديو الرسوم البيانية",
        "regen": "إعادة التوليد",
        "ai_insight": "رؤية الذكاء الاصطناعي",
        "session_memory": "ذاكرة الجلسة",
        "segment_compare": "مقارنة الشرائح",
        "primary_segment": "الشريحة الأساسية",
        "compare_against": "المقارنة مع",
        "last_sync": "آخر مزامنة",
        "export_csv": "تصدير CSV",
        "gen_report": "إنشاء تقرير تنفيذي",
        "exec": "تنفيذي",
        "analyst": "محلل",
        "story": "قصة",
        "finance_lens": "المالية والنمو",
        "ops_lens": "كفاءة العمليات",
        "sales_lens": "أداء المبيعات",
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
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None
if "business_lens" not in st.session_state:
    st.session_state.business_lens = None  # will be set by widget; do not assign after widget
if "analyst_mode" not in st.session_state:
    st.session_state.analyst_mode = "Exec"
if "chart_studio_type" not in st.session_state:
    st.session_state.chart_studio_type = "bar"
if "chart_studio_x" not in st.session_state:
    st.session_state.chart_studio_x = None
if "chart_studio_y" not in st.session_state:
    st.session_state.chart_studio_y = None
if "chart_studio_agg" not in st.session_state:
    st.session_state.chart_studio_agg = "sum"
if "segment_primary" not in st.session_state:
    st.session_state.segment_primary = None
if "segment_compare" not in st.session_state:
    st.session_state.segment_compare = "Global Average"


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


def profile_dataframe(df):
    """Smart dataset profiling: missing, duplicates, types, numeric stats, quality signals."""
    profile = {
        "missing_pct": {},
        "missing_total": 0,
        "duplicate_rows": int(df.duplicated().sum()),
        "total_rows": len(df),
        "column_types": {},
        "numeric_stats": {},
        "unique_counts": {},
        "quality_signals": [],
    }
    for col in df.columns:
        null_count = df[col].isna().sum()
        pct = round(100 * null_count / len(df), 1) if len(df) else 0
        profile["missing_pct"][col] = pct
        profile["missing_total"] += null_count
        profile["unique_counts"][col] = int(df[col].nunique())
        dtype = str(df[col].dtype)
        if "int" in dtype or "float" in dtype:
            profile["column_types"][col] = "numeric"
            profile["numeric_stats"][col] = {
                "min": df[col].min(),
                "max": df[col].max(),
                "mean": round(df[col].mean(), 2) if df[col].notna().any() else None,
            }
        elif "datetime" in dtype:
            profile["column_types"][col] = "datetime"
        else:
            profile["column_types"][col] = "categorical"
    if profile["duplicate_rows"] > 0:
        profile["quality_signals"].append(f"Duplicate rows: {profile['duplicate_rows']}")
    high_missing = [c for c, p in profile["missing_pct"].items() if p > 20]
    if high_missing:
        profile["quality_signals"].append(f"High missing (>20%): {', '.join(high_missing[:3])}{'...' if len(high_missing) > 3 else ''}")
    # Readiness: 100 - avg null pct - penalty for duplicates
    avg_null = sum(profile["missing_pct"].values()) / len(profile["missing_pct"]) if profile["missing_pct"] else 0
    dup_penalty = min(10, profile["duplicate_rows"] // 100)
    profile["readiness_pct"] = max(0, min(100, round(100 - avg_null - dup_penalty)))
    # Integrity score (usable columns = non-null-heavy)
    usable = sum(1 for c, p in profile["missing_pct"].items() if p < 50)
    profile["usable_columns"] = usable
    profile["integrity_score"] = round(100 * usable / len(df.columns)) if len(df.columns) else 0
    # Recommended measures: numeric columns
    profile["recommended_measures"] = [c for c, t in profile["column_types"].items() if t == "numeric"][:5]
    return profile


def parse_analysis_json(text):
    """Extract and parse JSON from model output with fallbacks."""
    text = (text or "").strip()
    if not text:
        return None
    # Try to find JSON block
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    end = -1
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end == -1:
        return None
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        pass
    # Fallback: minimal valid structure
    return {
        "summary": {
            "overview": "Analysis could not be parsed. Please try again.",
            "key_insights": [],
            "recommendations": [],
            "final_summary": "",
        },
        "charts": [],
    }


def ask_agent_for_analysis(df, profile=None):
    columns = list(df.columns)
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
    sample_rows = df.head(15).to_dict(orient="records")
    for row in sample_rows:
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
    profile = profile or profile_dataframe(df)
    prompt = f"""You are a professional data analysis AI agent. Analyze this dataset and return ONLY valid JSON, no markdown or explanation.

COLUMNS (use these exact names): {columns}
DTYPES: {dtypes}
SAMPLE (first 15 rows): {json.dumps(sample_rows, default=str)}
DATA QUALITY: duplicate_rows={profile['duplicate_rows']}, high_missing_columns={[c for c, p in profile['missing_pct'].items() if p > 10]}.

Return exactly this JSON structure (no other text):
{{
  "summary": {{
    "overview": "2-3 sentence overview of the dataset and what it contains",
    "key_insights": ["insight 1", "insight 2", "insight 3"],
    "recommendations": ["actionable recommendation 1", "recommendation 2"],
    "final_summary": "one sentence executive conclusion"
  }},
  "charts": [
    {{ "title": "Chart title", "chart_type": "bar", "x_column": "exact_column_name", "y_column": "exact_column_name", "aggregation": "sum" }},
    {{ "title": "Chart title", "chart_type": "line", "x_column": "exact_column_name", "y_column": "exact_column_name", "aggregation": "mean" }}
  ]
}}
RULES: Use ONLY column names from the list above. chart_type: bar, line, pie, scatter. aggregation: sum, mean, count, none. Return at least 2 charts. x_column and y_column must exist in columns. Output only the JSON object."""
    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        raw = (response.output_text or "").strip()
        result = parse_analysis_json(raw)
        if not result:
            result = {"summary": {"overview": "Analysis unavailable.", "key_insights": [], "recommendations": [], "final_summary": ""}, "charts": []}
        # Validate charts: only keep those with existing columns
        valid_cols = set(df.columns)
        valid_charts = []
        for ch in result.get("charts", []):
            x, y = ch.get("x_column"), ch.get("y_column")
            if x in valid_cols and (y in valid_cols or ch.get("aggregation") == "count"):
                valid_charts.append(ch)
        result["charts"] = valid_charts if valid_charts else result.get("charts", [])[:2]
        return result
    except Exception as e:
        return {
            "summary": {
                "overview": f"Analysis could not be completed: {str(e)[:200]}.",
                "key_insights": [],
                "recommendations": [],
                "final_summary": "",
            },
            "charts": [],
        }


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
        bg_base = "#F8FAFC"
        text_primary = "#1E293B"
        text_secondary = "#64748B"
        glass_panel = "rgba(255, 255, 255, 0.7)"
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
        .insight-card.priority { border-left: none; border-right: 3px solid #9333EA; }
        .explain-panel { border-left: none; border-right: 2px solid #4F46E5; }
        """

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap');

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
    --accent-purple: #9333EA;
    --accent-indigo: #4F46E5;
    --text-primary: {text_primary};
    --text-secondary: {text_secondary};
}}

html {{ font-size: 16px; -webkit-font-smoothing: antialiased; }}
body, .stApp, [data-testid="stAppViewContainer"] {{
    font-family: {"'IBM Plex Sans Arabic', 'Inter', sans-serif" if lang == "ar" else "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"} !important;
    background: {bg_base} !important;
    color: {text_primary} !important;
    line-height: 1.5 !important;
}}
[data-testid="stAppViewContainer"] > section {{ background: transparent !important; }}
[data-testid="stAppViewContainer"] {{ overflow-x: hidden !important; }}
.block-container p, .block-container li {{ color: {text_primary} !important; font-size: 0.9375rem !important; line-height: 1.55 !important; }}

/* App container: max-width, responsive padding, bottom space for fixed chat bar */
.block-container {{
    max-width: 1400px !important;
    margin: 0 auto !important;
    padding: 40px 24px 100px !important;
}}
@media (max-width: 1023px) {{ .block-container {{ padding: 24px 16px 100px !important; }} }}
@media (max-width: 768px) {{ .block-container {{ padding: 20px 12px 90px !important; }} }}

/* Variant: sticky navbar – Data Soul Studio, compact controls */
.navbar {{
    position: sticky;
    top: 0;
    z-index: 100;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 32px;
    background: {glass_panel};
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid {border_subtle};
}}
.nav-logo {{ font-weight: 600; font-size: 1.125rem; color: {text_primary} !important; letter-spacing: -0.02em; }}
.nav-logo span {{ font-weight: 400; opacity: 0.6; margin-left: 6px; }}
.nav-controls {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}
@media (max-width: 768px) {{ .navbar {{ padding: 12px 16px; }} .nav-logo {{ font-size: 1rem; }} }}
.nav-tag {{ padding: 4px 10px; background: rgba(255,255,255,0.05); border: 1px solid {border_subtle}; border-radius: 8px; font-size: 0.75rem; color: {text_secondary}; }}
.nav-tag.highlight {{ border-color: #9333EA; color: {text_primary}; }}
.lang-switcher {{
    display: inline-flex;
    background: {"rgba(255,255,255,0.08)" if is_dark else "rgba(0,0,0,0.05)"};
    border: 1px solid {border_subtle};
    border-radius: 10px;
    padding: 3px;
    gap: 2px;
}}
.lang-btn {{
    padding: 5px 12px;
    font-size: 0.75rem;
    font-weight: 600;
    border: none;
    background: transparent;
    color: {text_secondary};
    border-radius: 7px;
    cursor: pointer;
    text-decoration: none;
    letter-spacing: 0.03em;
}}
.lang-btn:hover {{ color: {text_primary}; }}
.lang-btn.active {{ background: #9333EA; color: #fff; }}
.theme-option {{
    padding: 6px 12px;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 7px;
    text-decoration: none;
    color: {text_secondary} !important;
}}
.theme-option.active {{ background: #9333EA; color: #fff !important; }}
.theme-switch-pill {{
    display: inline-flex;
    border-radius: 10px;
    background: {"rgba(255,255,255,0.08)" if is_dark else "rgba(0,0,0,0.05)"};
    border: 1px solid {border_subtle};
    padding: 3px;
    gap: 2px;
}}
.lang-menu {{ display: none; }}
.lang-dropdown {{ display: none; }}
.lang-trigger {{ display: none; }}

/* Subtle background texture */
.stApp::before {{
    content: "";
    position: fixed;
    inset: -100px;
    pointer-events: none;
    z-index: 0;
    background-image: radial-gradient(1px 1px at 40px 60px, rgba(255,255,255,{"0.12" if is_dark else "0.06"}) 100%, transparent);
    background-size: 120px 120px;
}}
.star-layer-3, .star-layer-4 {{ display: none; }}
[data-testid="stAppViewContainer"] {{ position: relative; z-index: 1; }}

/* Soft ambient glow (dark mode only) */
.light-flare-1 {{
    position: fixed;
    top: -30vh; left: 50%;
    transform: translateX(-50%);
    width: 60vw; height: 80vh;
    background: radial-gradient(ellipse at center, rgba(79, 70, 229, 0.12) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
    filter: blur(80px);
}}
.light-flare-2 {{
    position: fixed;
    top: 40vh; left: 50%;
    transform: translateX(-50%);
    width: 50vw; height: 40vh;
    background: radial-gradient(ellipse at center, rgba(147, 51, 234, 0.08) 0%, transparent 65%);
    pointer-events: none;
    z-index: 0;
    filter: blur(70px);
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
/* Variant: hero – 80px orb, title, subtitle */
.hero {{
    text-align: center;
    margin-bottom: 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
}}
.hero-orb {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #ffffff 0%, #A855F7 40%, #4F46E5 100%);
    box-shadow: 0 0 40px rgba(168, 85, 247, 0.4);
}}
.hero h1 {{ font-size: 1.875rem; font-weight: 600; color: {text_primary} !important; margin: 0; letter-spacing: -0.02em; }}
.hero-desc, .hero p {{ color: {text_secondary} !important; font-size: 0.9rem; max-width: 520px; line-height: 1.5; margin: 0; }}
@media (max-width: 768px) {{ .hero h1 {{ font-size: 1.375rem; }} .hero-orb {{ width: 52px; height: 52px; }} .hero-desc {{ font-size: 0.8125rem; }} }}

/* Main content shell: responsive – 3-col only when enough width, else stack (no overflow) */
.grid-main-marker + [data-testid="stHorizontalBlock"] {{
    display: grid !important;
    gap: 24px !important;
    align-items: start !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
}}
.grid-main-marker + [data-testid="stHorizontalBlock"] > div {{
    min-width: 0 !important;
    max-width: 100% !important;
    overflow: hidden !important;
}}
/* >= 1280px: 3 columns; rails use minmax(0, 280px) so they can shrink if needed */
@media (min-width: 1280px) {{
    .grid-main-marker + [data-testid="stHorizontalBlock"] {{
        grid-template-columns: minmax(0, 280px) minmax(320px, 1fr) minmax(0, 280px) !important;
    }}
}}
/* < 1280px: single column – no collision, no crushed center */
@media (max-width: 1279px) {{
    .grid-main-marker + [data-testid="stHorizontalBlock"] {{
        grid-template-columns: 1fr !important;
    }}
}}

/* Section titles */
.section-title {{
    font-size: 0.8rem;
    font-weight: 600;
    margin: 0 0 14px 0;
    color: {text_secondary} !important;
    letter-spacing: 0.03em;
}}

/* Stats row & KPI cards – clean grid */
.stats-row {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px;
    margin-bottom: 16px;
}}
.stats-row .kpi-card {{
    background: rgba(255, 255, 255, {"0.04" if is_dark else "0.5"});
    border: 1px solid {border_subtle};
    border-radius: 12px;
    padding: 14px 16px;
}}
.stats-row .kpi-label {{ font-size: 0.75rem; color: {text_secondary}; margin-bottom: 4px; }}
.stats-row .kpi-value {{ font-size: 1.2rem; font-weight: 600; margin-top: 0; color: {text_primary} !important; }}

/* Health score bar */
.health-score {{
    height: 6px;
    background: rgba(255, 255, 255, {"0.12" if is_dark else "0.2"});
    border-radius: 4px;
    margin: 10px 0;
    overflow: hidden;
}}
.health-fill {{
    height: 100%;
    background: linear-gradient(90deg, #059669, #10B981);
    border-radius: 4px;
}}

/* Tags – compact, readable */
.tag {{
    padding: 6px 12px;
    background: rgba(255, 255, 255, {"0.06" if is_dark else "0.08"});
    border: 1px solid {border_subtle};
    border-radius: 8px;
    font-size: 0.8125rem;
    color: {text_secondary};
}}
.tag.highlight {{ border-color: rgba(147, 51, 234, 0.4); color: {text_primary}; background: rgba(147, 51, 234, 0.08); }}
.tag-grid {{ display: flex; flex-wrap: wrap; gap: 8px; }}

/* Variant: insight-grid, insight-card – responsive */
.insight-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-top: 24px;
}}
@media (max-width: 900px) {{ .insight-grid {{ grid-template-columns: 1fr; }} }}
.insight-card {{
    padding: 18px 20px;
    border-radius: 14px;
    background: rgba(255,255,255,{"0.04" if is_dark else "0.6"});
    border: 1px solid {border_subtle};
}}
.insight-card.priority {{ border-left: 3px solid #9333EA; }}
.insight-card .kpi-label {{ font-size: 0.7rem; margin-bottom: 6px; font-weight: 600; }}
.insight-card div[style*="margin-top: 8px"] {{ font-size: 0.9rem !important; line-height: 1.5 !important; color: {text_primary} !important; }}

/* Variant: chart-area, chart-frame, chart-controls, explain-panel */
.chart-area {{
    margin-top: 24px;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 16px;
    border: 1px solid {border_subtle};
    padding: 24px;
}}
.chart-frame {{ min-height: 300px; border-radius: 12px; }}
.chart-controls {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }}
@media (max-width: 640px) {{ .chart-controls {{ grid-template-columns: 1fr 1fr; }} }}
.select-box {{
    background: rgba(255,255,255,0.05);
    border: 1px solid {border_subtle};
    color: {text_primary};
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 0.8rem;
}}
.explain-panel {{
    margin-top: 14px;
    padding: 14px 16px;
    background: rgba(79, 70, 229, {"0.08" if is_dark else "0.06"});
    border-radius: 12px;
    font-size: 0.875rem;
    line-height: 1.55;
    border-left: 3px solid #4F46E5;
    color: {text_primary} !important;
}}
.explain-panel strong {{ color: {text_primary} !important; margin-right: 6px; }}

/* Sidebar list & history items */
.sidebar-list {{ display: flex; flex-direction: column; gap: 10px; }}
.history-item {{
    padding: 12px 14px;
    border-radius: 10px;
    background: rgba(255,255,255,{"0.03" if is_dark else "0.05"});
    border: 1px solid {border_subtle};
    font-size: 0.8125rem;
    line-height: 1.45;
    color: {text_primary} !important;
}}
.history-item div[style*="opacity"] {{ color: {text_secondary} !important; }}

/* Variant: mode-selector, mode-btn */
.mode-selector {{ display: flex; gap: 4px; background: rgba(255,255,255,0.05); padding: 4px; border-radius: 12px; margin-bottom: 20px; }}
.mode-btn {{ flex: 1; padding: 6px; font-size: 0.7rem; border: none; background: transparent; color: {text_secondary}; border-radius: 8px; cursor: pointer; }}
.mode-btn.active {{ background: #9333EA; color: white; }}

/* Variant: suggested chips */
.suggested-chips {{ display: flex; gap: 10px; margin-top: 12px; flex-wrap: wrap; }}
.chip {{
    padding: 8px 16px;
    background: rgba(147, 51, 234, 0.1);
    border: 1px solid rgba(147, 51, 234, 0.2);
    border-radius: 20px;
    font-size: 0.8rem;
}}
/* Right rail suggested-question buttons as chips */
.grid-main-marker + [data-testid="stHorizontalBlock"] > div:last-child [data-testid="stButton"] button {{
    padding: 8px 14px !important;
    font-size: 0.8125rem !important;
    border-radius: 999px !important;
    background: rgba(147, 51, 234, 0.12) !important;
    border: 1px solid rgba(147, 51, 234, 0.25) !important;
    color: {text_primary} !important;
}}
.grid-main-marker + [data-testid="stHorizontalBlock"] > div:last-child [data-testid="stButton"] button:hover {{
    background: rgba(147, 51, 234, 0.2) !important;
}}

/* Variant: export-row, btn-ghost */
.export-row {{ display: flex; justify-content: space-between; align-items: center; margin-top: 24px; padding-top: 20px; border-top: 1px solid {border_subtle}; margin-bottom: 0 !important; }}
.export-row + [data-testid="stHorizontalBlock"] {{ margin-top: 6px !important; }}
.btn-ghost {{ padding: 8px 16px; background: rgba(255,255,255,0.05); border: 1px solid {border_subtle}; color: {text_primary}; border-radius: 10px; font-size: 0.85rem; cursor: pointer; }}
/* Download buttons */
.block-container [data-testid="stDownloadButton"] button {{
    padding: 10px 20px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    border-radius: 10px !important;
    background: rgba(255,255,255,{"0.08" if is_dark else "0.12"}) !important;
    border: 1px solid {border_subtle} !important;
    color: {text_primary} !important;
}}
.block-container [data-testid="stDownloadButton"] button:hover {{
    background: rgba(255,255,255,{"0.12" if is_dark else "0.18"}) !important;
}}

/* Glass panels – clean cards */
.glass-panel {{
    background: {glass_panel};
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid {border_subtle};
    border-radius: 16px;
    box-shadow: {shadow_glass};
    padding: 24px;
    min-width: 0;
    overflow: hidden;
}}
@media (max-width: 768px) {{ .glass-panel {{ padding: 18px !important; border-radius: 14px; }} }}


/* Design dropzone */
.dropzone, .dropzone-outer {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
    border: 1px dashed {border_subtle};
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.02);
    transition: all 0.3s ease;
    text-align: center;
}}
.dropzone:hover, .dropzone-outer:hover {{
    border-color: #9333EA;
    background: rgba(147, 51, 234, 0.05);
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
/* Data Source card – same as other panels */
.block-container > div > [data-testid="stVerticalBlock"]:has([data-testid="stFileUploader"]) {{
    background: {glass_panel} !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid {border_subtle};
    border-radius: 16px;
    box-shadow: {shadow_glass};
    padding: 24px !important;
    margin-bottom: 16px !important;
}}
[data-testid="stFileUploader"] {{
    background: transparent !important; border: none !important; padding: 0 !important;
    width: 100% !important; max-width: 100% !important; box-sizing: border-box !important;
}}
[data-testid="stFileUploader"] section {{ max-width: 100% !important; border: none !important; }}
[data-testid="stFileUploader"] label {{ color: {text_primary} !important; font-size: 0.9rem !important; font-weight: 500 !important; }}
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {{
    border: 1px dashed {border_subtle} !important; border-radius: 12px !important;
    background: rgba(255,255,255,{"0.03" if is_dark else "0.05"}) !important;
}}

/* Design dashboard-grid: balanced row, align top */
.dashboard-grid {{ display: grid; grid-template-columns: 1fr 2fr; gap: 24px; align-items: start; }}
.overview-card {{ display: flex; flex-direction: column; gap: 12px; }}
.dashboard-grid .kpi-card {{ min-height: 0; }}
.dashboard-grid .kpi-value {{ margin-top: 4px; }}
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

/* Table – readable, scannable */
.table-scroll-viewport {{
    width: 100%;
    max-height: 360px;
    overflow: auto;
    border-radius: 12px;
    border: 1px solid {border_subtle};
}}
.table-scroll-viewport table {{ width: 100%; border-collapse: collapse; font-size: 0.875rem; }}
.table-scroll-viewport th {{
    position: sticky; top: 0; z-index: 1;
    background: {th_bg} !important;
    color: {text_secondary} !important;
    font-weight: 600;
    padding: 12px 14px;
    border-bottom: 1px solid {border_subtle};
    text-align: left;
}}
.table-scroll-viewport td {{
    padding: 10px 14px;
    border-bottom: 1px solid {td_border};
    color: {text_primary} !important;
    font-size: 0.8125rem !important;
}}
.table-scroll-viewport tbody tr:hover td {{ background: rgba(255,255,255,{"0.03" if is_dark else "0.05"}) !important; }}

/* Buttons */
.cta-container {{ display: flex; justify-content: center; margin: 16px 0; }}
.stButton > button {{
    background: linear-gradient(135deg, #4F46E5, #7C3AED) !important;
    color: #fff !important;
    border: none !important;
    padding: 10px 22px !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    border-radius: 10px !important;
}}
.stButton > button:hover {{ opacity: 0.92 !important; }}

/* Design analysis-section */
.analysis-section {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }}

/* Charts: style the column that CONTAINS the Plotly chart as the card (chart renders inside) */
.block-container [data-testid="column"]:has([data-testid="stPlotlyChart"]) {{
    background: {glass_panel} !important;
    backdrop-filter: blur(32px);
    -webkit-backdrop-filter: blur(32px);
    border: 1px solid {border_card};
    border-radius: 16px;
    padding: 24px !important;
    min-height: 320px;
}}
.chart-card-title {{ font-weight: 500; font-size: 0.95rem; color: {text_primary} !important; margin-bottom: 16px; }}
/* Chart Studio: style the block that contains the Plotly chart so chart renders inside a card */
[data-testid="stVerticalBlock"]:has(> [data-testid="stPlotlyChart"]) {{
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid {border_subtle};
    border-radius: 16px;
    padding: 24px !important;
}}
.chart-placeholder {{
    min-height: 260px;
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

/* Chat section – readable messages */
.chat-section-title {{
    font-size: 0.8125rem;
    font-weight: 600;
    color: {text_secondary} !important;
    margin-bottom: 12px;
    margin-top: 32px;
}}
[data-testid="stChatMessage"] {{
    padding: 0 !important;
    margin-bottom: 12px !important;
    background: transparent !important;
}}
[data-testid="stChatMessage"] > div {{
    background: {glass_panel} !important;
    border: 1px solid {border_subtle} !important;
    border-radius: 14px !important;
    padding: 14px 18px !important;
    max-width: 88%;
}}
[data-testid="stChatMessage"]:nth-of-type(odd) > div {{
    margin-left: auto !important;
    margin-right: 0 !important;
    background: rgba(79, 70, 229, 0.12) !important;
    border-color: rgba(147, 51, 234, 0.2) !important;
}}
[data-testid="stChatMessage"]:nth-of-type(even) > div {{ margin-right: auto !important; margin-left: 0 !important; }}
[data-testid="stChatMessage"] p {{
    color: {text_primary} !important;
    font-size: 0.9375rem !important;
    line-height: 1.6 !important;
    margin: 0 !important;
}}

/* Suggested questions label */
.chat-suggested-label {{
    font-size: 0.8125rem;
    font-weight: 500;
    color: {text_secondary} !important;
    margin-bottom: 8px;
}}
/* Suggested chips only: innermost block that contains chat input (exclude CTA and other buttons) */
.block-container [data-testid="stVerticalBlock"]:has([data-testid="stChatInput"]):not([data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"]:has([data-testid="stChatInput"])) [data-testid="stButton"] button {{
    background: rgba(255,255,255,{"0.06" if is_dark else "0.12"}) !important;
    color: {text_secondary} !important;
    border: 1px solid {border_subtle} !important;
    padding: 8px 14px !important;
    font-size: 0.8125rem !important;
    font-weight: 500 !important;
    border-radius: 20px !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
}}
.block-container [data-testid="stVerticalBlock"]:has([data-testid="stChatInput"]):not([data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"]:has([data-testid="stChatInput"])) [data-testid="stButton"] button:hover {{
    background: rgba(255,255,255,{"0.1" if is_dark else "0.18"}) !important;
    color: {text_primary} !important;
    border-color: {border_highlight} !important;
}}

/* Floating chat input – one clean bar */
[data-testid="stChatInput"] {{
    position: fixed !important;
    bottom: 20px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: min(100% - 24px, 640px) !important;
    margin: 0 !important;
    background: linear-gradient(135deg, #5B42F3, #7C3AED) !important;
    border: none !important;
    border-radius: 24px !important;
    padding: 12px 20px !important;
    min-height: 50px !important;
    box-shadow: 0 8px 32px rgba(91, 66, 243, 0.35) !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    z-index: 1000 !important;
}}
[data-testid="stChatInput"] > div, [data-testid="stChatInput"] input {{
    flex: 1 !important; min-width: 0 !important;
    background: transparent !important; border: none !important;
}}
[data-testid="stChatInput"] input {{
    color: #fff !important; font-size: 0.9375rem !important;
    padding: 6px 8px !important;
}}
[data-testid="stChatInput"] input::placeholder {{ color: rgba(255,255,255,0.8) !important; }}
[data-testid="stChatInput"] button {{ flex-shrink: 0 !important; background: transparent !important; border: none !important; color: #fff !important; }}
@media (max-width: 768px) {{ [data-testid="stChatInput"] {{ bottom: 12px !important; padding: 10px 16px !important; }} }}

.summary-block {{ margin-bottom: 20px; }}
.summary-block h4 {{ font-size: 0.9375rem; font-weight: 600; color: {text_primary}; margin-bottom: 10px; }}
.summary-block p, .summary-block ul {{ color: {text_secondary}; font-size: 0.9375rem; line-height: 1.6; }}

/* All form widgets – readable */
.stSelectbox > div > div {{
    background: rgba(255,255,255,{"0.06" if is_dark else "0.1"}) !important;
    border: 1px solid {border_subtle} !important;
    color: {text_primary} !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
}}
.stSelectbox label {{ color: {text_secondary} !important; font-size: 0.8125rem !important; }}
[data-testid="stRadio"] > div {{ gap: 8px !important; }}
[data-testid="stRadio"] label {{ color: {text_primary} !important; font-size: 0.875rem !important; }}
/* Ensure all Streamlit text is readable */
[data-testid="stMarkdown"] p, [data-testid="stMarkdown"] li {{ color: {text_primary} !important; font-size: 0.9375rem !important; line-height: 1.55 !important; }}

#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
[data-testid="stSidebar"] {{ display: none !important; }}
{rtl_extra}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Render
# -----------------------------
# Sync lang/theme from query params (navbar links)
qp = st.query_params
changed = False
if "lang" in qp and qp["lang"] in ("en", "ar"):
    st.session_state.lang = qp["lang"]
    changed = True
if "theme" in qp and qp["theme"] in ("dark", "light"):
    st.session_state.theme = qp["theme"]
    changed = True
if changed:
    st.query_params.clear()
    st.rerun()

inject_css(st.session_state.theme, st.session_state.lang)

theme = st.session_state.theme
lang = st.session_state.lang
nav_lang_label = "English" if lang == "en" else "العربية"
nav_theme_dark_active = " active" if theme == "dark" else ""
nav_theme_light_active = " active" if theme == "light" else ""

# Navbar (sticky, design-fidelity: VARAIANT + lang links + theme pill)
st.markdown(f"""
<nav class="navbar">
    <div class="nav-logo">Data Soul <span>{t("studio")}</span></div>
    <div class="nav-controls">
        <div class="nav-tag highlight">v2.4 Pro</div>
        <div class="lang-switcher">
            <a href="?lang=en" class="lang-btn{" active" if lang == "en" else ""}">EN</a>
            <a href="?lang=ar" class="lang-btn{" active" if lang == "ar" else ""}">AR</a>
        </div>
        <div class="theme-switch-pill">
            <a href="?theme=dark" class="theme-option{nav_theme_dark_active}">Dark</a>
            <a href="?theme=light" class="theme-option{nav_theme_light_active}">Light</a>
        </div>
    </div>
</nav>
""", unsafe_allow_html=True)

# Star layers (both themes) + light flares (dark only)
st.markdown('<div class="star-layer-3"></div><div class="star-layer-4"></div>', unsafe_allow_html=True)
if st.session_state.theme == "dark":
    st.markdown('<div class="light-flare-1"></div><div class="light-flare-2"></div>', unsafe_allow_html=True)

# Data Source: one container = one card. Title + uploader render INSIDE the same block.
with st.container():
    st.markdown(f'<h2 class="section-title">{t("data_source")}</h2>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        t("drag_drop") + " — " + t("supports"),
        type=["csv", "xlsx"],
        label_visibility="collapsed",
        key="main_uploader"
    )

if uploaded_file is None:
    if st.session_state.last_uploaded_name is not None:
        reset_app_state()
    st.stop()

# Variant: hero with filename (after we have a file)
hero_sub = "Deep semantic profiling and automated visualization for " + html.escape(uploaded_file.name)
st.markdown(f"""
<div class="hero">
    <div class="hero-orb"></div>
    <h1>Data Soul</h1>
    <p class="hero-desc">{hero_sub}</p>
</div>
""", unsafe_allow_html=True)

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
    profile = profile_dataframe(df)
    dup_count = profile["duplicate_rows"]
    missing_note = str(profile["missing_total"]) if profile["missing_total"] > 0 else "—"

    # Variant: three-column grid-main (320 | 1fr | 320)
    readiness = profile.get("readiness_pct", 82)
    null_pct_str = f"{sum(profile['missing_pct'].values()) / len(profile['missing_pct']):.1f}%" if profile["missing_pct"] else "0%"
    num_count = sum(1 for v in profile["column_types"].values() if v == "numeric")
    cat_count = sum(1 for v in profile["column_types"].values() if v == "categorical")
    dt_count = sum(1 for v in profile["column_types"].values() if v == "datetime")
    rec_measures = profile.get("recommended_measures", [])[:3]
    rec_tags = "".join(f'<span class="tag highlight">{m}</span>' for m in rec_measures) or '<span class="tag">—</span>'
    type_tags = f'<span class="tag"># Numeric ({num_count})</span><span class="tag">A Categorical ({cat_count})</span><span class="tag">📅 Datetime ({dt_count})</span>'
    health_tags = "".join(f'<div class="tag">{html.escape(s)}</div>' for s in profile.get("quality_signals", ["—"])[:2])
    st.markdown('<div class="grid-main-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    left_rail, main_rail, right_rail = st.columns([1, 2.5, 1])

    with left_rail:
        st.markdown(f"""
        <div class="glass-panel">
            <h2 class="section-title">{t("data_health")}</h2>
            <div class="kpi-label">{t("readiness")}</div>
            <div class="health-score"><div class="health-fill" style="width: {readiness}%;"></div></div>
            <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-bottom: 12px;">
                <div class="kpi-card"><div class="kpi-label">{t("null_pct")}</div><div class="kpi-value" style="color: #F87171;">{null_pct_str}</div></div>
                <div class="kpi-card"><div class="kpi-label">{t("duplicates")}</div><div class="kpi-value">{dup_count}</div></div>
            </div>
            <div class="sidebar-list">{health_tags}</div>
        </div>
        <div class="glass-panel">
            <h2 class="section-title">{t("dataset_profiling")}</h2>
            <div class="tag-grid">{type_tags}</div>
            <div class="kpi-label" style="margin-top: 8px;">{t("rec_measures")}</div>
            <div class="tag-grid">{rec_tags}</div>
        </div>
        <div class="glass-panel">
            <h2 class="section-title">{t("business_lens")}</h2>
        </div>
        """, unsafe_allow_html=True)
        lens_options = [t("finance_lens"), t("ops_lens"), t("sales_lens")]
        current_lens = st.session_state.get("business_lens")
        lens_index = lens_options.index(current_lens) if current_lens in lens_options else 0
        st.selectbox(
            "Lens", options=lens_options, index=lens_index, key="business_lens", label_visibility="collapsed"
        )

    with main_rail:
        # Quality & Shape Metrics (Variant)
        usable = profile.get("usable_columns", n_cols)
        integrity = profile.get("integrity_score", 94)
        st.markdown(f"""
        <div class="glass-panel">
            <h2 class="section-title">{t("quality_metrics")}</h2>
            <div class="stats-row">
                <div class="kpi-card"><div class="kpi-label">{t("integrity")}</div><div class="kpi-value">{integrity}/100</div></div>
                <div class="kpi-card"><div class="kpi-label">{t("usable_cols")}</div><div class="kpi-value">{usable} / {n_cols}</div></div>
                <div class="kpi-card"><div class="kpi-label">{t("missing_cells")}</div><div class="kpi-value">{profile['missing_total']:,}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(t("generate_summary_short"), key="cta_gen"):
            with st.spinner(t("analyzing")):
                st.session_state.analysis_result = ask_agent_for_analysis(df, profile)
            st.rerun()
        result = st.session_state.analysis_result

        if result is not None:
            summary = result["summary"]
            charts = result.get("charts", [])
            def esc(s):
                return html.escape(str(s)) if s else ""
            top_finding = esc(summary.get("top_finding") or summary.get("key_insights", [None])[0] if summary.get("key_insights") else summary.get("overview"))
            biggest_risk = esc(summary.get("biggest_risk") or summary.get("recommendations", [None])[0] if summary.get("recommendations") else "")
            notable_trend = esc(summary.get("notable_trend") or (summary.get("key_insights", []) or [None])[1] if len(summary.get("key_insights", [])) > 1 else summary.get("overview"))
            st.markdown(f"""
            <div class="insight-grid">
                <div class="insight-card priority"><div class="kpi-label" style="color: var(--accent-purple);">{t("top_finding")}</div><div style="font-size: 0.9rem; margin-top: 8px;">{top_finding}</div></div>
                <div class="insight-card"><div class="kpi-label">{t("biggest_risk")}</div><div style="font-size: 0.9rem; margin-top: 8px;">{biggest_risk or "—"}</div></div>
                <div class="insight-card"><div class="kpi-label">{t("notable_trend")}</div><div style="font-size: 0.9rem; margin-top: 8px;">{notable_trend}</div></div>
            </div>
            """, unsafe_allow_html=True)

        # Chart Studio (always; use result for explain if available)
        col_types = profile.get("column_types", {})
        cat_cols = [c for c, t in col_types.items() if t == "categorical"]
        num_cols = [c for c, t in col_types.items() if t == "numeric"]
        if not cat_cols:
            cat_cols = [c for c in df.columns if df[c].dtype == "object" or df[c].nunique() < 50][:8]
        if not num_cols:
            num_cols = [c for c in df.columns if df[c].dtype in ("int64", "float64")][:8]
        x_opts = cat_cols or list(df.columns)[:5]
        y_opts = num_cols or list(df.columns)[:5]
        st.markdown(f'<h2 class="section-title">{t("chart_studio")}</h2>', unsafe_allow_html=True)
        mode_sel = st.radio("Mode", [t("exec"), t("analyst"), t("story")], horizontal=True, key="analyst_mode", label_visibility="collapsed")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            chart_type = st.selectbox("Type", ["Bar Chart", "Line Chart", "Pie Chart"], key="chart_type")
        with c2:
            chart_x = st.selectbox("X", x_opts, key="chart_x")
        with c3:
            chart_y = st.selectbox("Y", y_opts, key="chart_y")
        with c4:
            st.markdown("<br>", unsafe_allow_html=True)
            regen = st.button(t("regen"), key="chart_regen")
        type_map = {"bar chart": "bar", "line chart": "line", "pie chart": "pie"}
        chart_spec = {"chart_type": type_map.get(chart_type.lower(), "bar"), "x_column": chart_x, "y_column": chart_y, "title": f"{chart_y} by {chart_x}"}
        fig = render_chart_fig(df, chart_spec, st.session_state.theme == "dark")
        st.markdown('<div class="chart-area">', unsafe_allow_html=True)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True, key="chart_studio_main")
        else:
            st.markdown(f'<div class="chart-frame" style="height:300px;display:flex;align-items:center;justify-content:center;color:var(--text-secondary);">{t("chart_not_available")}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        explain_text = ""
        if result and result.get("summary"):
            explain_text = html.escape(str(result["summary"].get("overview", ""))[:300])
        st.markdown(f'<div class="explain-panel"><strong>{t("ai_insight")}</strong> {explain_text or "—"}</div>', unsafe_allow_html=True)

        # Data Preview (inside main_rail, fixed-height scroll)
        preview_df = df.head(50)
        thead = "".join(f"<th>{html.escape(str(c))}</th>" for c in preview_df.columns)
        trows = "".join("<tr>" + "".join(f"<td>{html.escape(str(row[c]))}</td>" for c in preview_df.columns) + "</tr>" for _, row in preview_df.iterrows())
        st.markdown(f"""
        <div class="glass-panel">
            <h2 class="section-title">{t("data_preview")}</h2>
            <div class="table-scroll-viewport">
                <table><thead><tr>{thead}</tr></thead><tbody>{trows}</tbody></table>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Export row
        st.markdown(f"""
        <div class="export-row">
            <div class="tag">{t("last_sync")}</div>
            <div style="display: flex; gap: 12px;"></div>
        </div>
        """, unsafe_allow_html=True)
        e1, e2, _ = st.columns(3)
        with e1:
            st.download_button(t("export_csv"), df.to_csv(index=False).encode("utf-8"), file_name=uploaded_file.name or "data.csv", mime="text/csv", key="dl_csv")
        with e2:
            rep = (result.get("summary", {}) if result else {}) or {}
            rep_text = f"# Executive Report\n\n{rep.get('overview', '')}\n\n## Key insights\n" + "\n".join(f"- {x}" for x in rep.get("key_insights", []))
            st.download_button(t("gen_report"), rep_text.encode("utf-8"), file_name="executive_report.md", mime="text/markdown", key="dl_report")

    with right_rail:
        st.markdown(f'<div class="glass-panel"><h2 class="section-title">{t("session_memory")}</h2><div class="sidebar-list">', unsafe_allow_html=True)
        for msg in st.session_state.chat_history[-6:]:
            who = "user" if msg["role"] == "user" else "assistant"
            snip = (msg["content"][:60] + "…") if len(msg["content"]) > 60 else msg["content"]
            st.markdown(f'<div class="history-item"><div style="opacity:0.6;font-size:0.7rem;">{who}</div>{html.escape(snip)}</div>', unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
        cat_cols_r = [c for c, t in profile.get("column_types", {}).items() if t == "categorical"] or list(df.columns)[:3]
        st.markdown(f'<div class="glass-panel"><h2 class="section-title">{t("segment_compare")}</h2><div class="kpi-label">{t("primary_segment")}</div>', unsafe_allow_html=True)
        seg_primary = st.selectbox("Primary", options=cat_cols_r, key="seg_primary", label_visibility="collapsed")
        st.markdown(f'<div class="kpi-label">{t("compare_against")}</div>', unsafe_allow_html=True)
        seg_compare = st.selectbox("Compare", options=["Global Average"] + cat_cols_r, key="seg_compare", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(f'<div class="glass-panel"><h2 class="section-title">{t("suggested_q")}</h2><div class="suggested-chips">', unsafe_allow_html=True)
        for i, q in enumerate([t("q_top_revenue"), t("q_region_growth"), t("q_anomalies")]):
            if st.button(q, key=f"right_sug_{i}"):
                st.session_state.pending_question = q
                st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)

    # Chat: process suggested-question click first
    if st.session_state.pending_question:
        q = st.session_state.pending_question
        st.session_state.pending_question = None
        st.session_state.chat_history.append({"role": "user", "content": q})
        with st.spinner("..."):
            answer = ask_agent_question(df, st.session_state.analysis_result or {}, q)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    # AI Assistant section: one container for hierarchy (title → conversation → chips → command bar)
    with st.container():
        st.markdown(f'<h2 class="chat-section-title">{t("ask_questions")}</h2>', unsafe_allow_html=True)

        # Conversation history: premium message bubbles
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Suggested questions: compact chips (low visual weight)
        st.markdown(f'<div class="chat-suggested-label">{t("suggested_questions")}</div>', unsafe_allow_html=True)
        suggested_qs = [t("q_top_revenue"), t("q_region_growth"), t("q_trends"), t("q_anomalies"), t("q_recommend")]
        sug_cols = st.columns(5)
        for i, q in enumerate(suggested_qs):
            with sug_cols[i % 5]:
                if st.button(q, key=f"sug_{i}"):
                    st.session_state.pending_question = q
                    st.rerun()

        # Integrated command bar (anchored below chips)
        user_question = st.chat_input(t("ask_ai_placeholder"))
        if user_question:
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.write(user_question)
            with st.chat_message("assistant"):
                answer = ask_agent_question(df, st.session_state.analysis_result or {}, user_question)
                st.write(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

except Exception as e:
    st.error(str(e))
