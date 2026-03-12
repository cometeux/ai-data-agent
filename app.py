# -*- coding: utf-8 -*-
import html
import json
import pandas as pd
import streamlit as st
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
# -----------------------------
# Helpers (Streamlit-specific + imports from app_helpers)
# -----------------------------
from app_helpers import (
    load_data,
    file_size_mb,
    infer_data_types,
    profile_dataframe,
    parse_analysis_json,
    prepare_chart_data,
    render_chart_fig,
)


def reset_app_state():
    st.session_state.analysis_result = None
    st.session_state.chat_history = []
    st.session_state.last_uploaded_name = None


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


# -----------------------------
# Dashboard UI – compact three-rail layout, accents
# -----------------------------
def apply_dashboard_css():
    st.markdown("""
    <style>
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stSidebar"] { display: none !important; }
    .block-container { max-width: 1400px; padding: 1rem 1.25rem 1.5rem; }
    [data-testid="stVerticalBlock"] > div { gap: 0.5rem; }
    /* Compact header */
    h1 { font-size: 1.35rem !important; margin-bottom: 0.15rem !important; }
    [data-testid="stMarkdown"] p { margin-bottom: 0.25rem !important; font-size: 0.875rem !important; }
    /* Accent: primary buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: #fff !important; border: none !important;
        font-weight: 600 !important; border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.35);
    }
    .stButton > button:hover { box-shadow: 0 4px 12px rgba(139, 92, 246, 0.45); filter: brightness(1.05); }
    /* Metric cards: compact, subtle border */
    [data-testid="stMetric"] { padding: 0.5rem 0.75rem; background: rgba(30, 27, 75, 0.4); border-radius: 8px; border: 1px solid rgba(139, 92, 246, 0.15); }
    [data-testid="stMetric"] label { color: #a5b4fc !important; font-size: 0.75rem !important; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] { color: #e0e7ff !important; font-size: 1.1rem !important; }
    /* Expanders: tighter */
    .streamlit-expanderHeader { padding: 0.4rem 0.6rem !important; font-size: 0.9rem !important; }
    .streamlit-expanderContent { padding: 0.5rem 0.75rem !important; }
    /* Chat messages */
    [data-testid="stChatMessage"] { padding: 0.5rem 0.75rem !important; }
    /* Suggested question chips: accent when possible */
    div[data-testid="column"] button { border-radius: 6px !important; }
    /* Dark base for dashboard feel */
    [data-testid="stAppViewContainer"] { background: linear-gradient(180deg, #0f0f14 0%, #12121a 100%) !important; }
    .stPlotlyChart { border-radius: 8px; overflow: hidden; border: 1px solid rgba(139, 92, 246, 0.12); }
    /* Keep upload/input areas readable on dark */
    [data-testid="stFileUploader"] { border-radius: 8px; }
    [data-testid="stChatInput"] textarea { border-radius: 8px; border: 1px solid rgba(139, 92, 246, 0.25); }
    </style>
    """, unsafe_allow_html=True)


# -----------------------------
# Render – dashboard layout
# -----------------------------
apply_dashboard_css()

# Compact top line: title + badge
st.markdown(f'<p style="margin:0; font-size:0.8rem; color:#818cf8;">{t("badge")}</p>', unsafe_allow_html=True)
st.title(t("app_title"))

# --- Upload (full width so we can branch before rails) ---
uploaded_file = st.file_uploader(
    t("drag_drop") + " — " + t("supports"),
    type=["csv", "xlsx"],
    key="main_uploader",
    label_visibility="collapsed"
)

if uploaded_file is None:
    if st.session_state.last_uploaded_name is not None:
        reset_app_state()
    st.info(t("hero_desc"))
    st.stop()

if st.session_state.last_uploaded_name != uploaded_file.name:
    st.session_state.analysis_result = None
    st.session_state.chat_history = []
    st.session_state.last_uploaded_name = uploaded_file.name

try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(str(e))
    st.stop()

profile = profile_dataframe(df)
size_mb = file_size_mb(uploaded_file)
n_rows, n_cols = df.shape
result = st.session_state.analysis_result

# ----- Three-rail dashboard -----
left_rail, center_rail, right_rail = st.columns([1, 2.6, 1])

# --- LEFT: Upload context, actions, export ---
with left_rail:
    st.caption(t("data_source"))
    st.caption(f"**{uploaded_file.name}** · {size_mb:.2f} MB")
    if st.button(t("generate_summary_short"), key="cta_gen", use_container_width=True):
        with st.spinner(t("analyzing")):
            st.session_state.analysis_result = ask_agent_for_analysis(df, profile)
        st.rerun()
    st.caption("Export")
    st.download_button(
        t("export_csv"),
        df.to_csv(index=False).encode("utf-8"),
        file_name=uploaded_file.name or "data.csv",
        mime="text/csv",
        key="dl_csv",
        use_container_width=True
    )
    rep = (result.get("summary", {}) if result else {}) or {}
    rep_text = (
        "# Executive Report\n\n" + (rep.get("overview") or "")
        + "\n\n## Key insights\n" + "\n".join(f"- {x}" for x in (rep.get("key_insights") or []))
    )
    st.download_button(
        t("gen_report"),
        rep_text.encode("utf-8"),
        file_name="executive_report.md",
        mime="text/markdown",
        key="dl_report",
        use_container_width=True
    )

# --- CENTER: Metrics, summary, charts, preview ---
with center_rail:
    st.caption(t("dataset_overview"))
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.metric(t("total_rows"), f"{n_rows:,}")
    with r2:
        st.metric(t("total_columns"), n_cols)
    with r3:
        st.metric(t("duplicates"), profile["duplicate_rows"])
    with r4:
        st.metric(t("missing_vals"), profile["missing_total"])

    if result is not None:
        st.caption(t("analysis_summary"))
        summary = result.get("summary") or {}
        with st.expander(t("overview"), expanded=True):
            st.write(summary.get("overview") or "—")
        with st.expander(t("key_insights")):
            for item in summary.get("key_insights") or []:
                st.write(f"- {item}")
        with st.expander(t("recommendations")):
            for item in summary.get("recommendations") or []:
                st.write(f"- {item}")
        with st.expander(t("final_summary")):
            st.write(summary.get("final_summary") or summary.get("overview") or "—")

        charts = result.get("charts") or []
        if charts:
            st.caption(t("visualizations"))
            for i, ch in enumerate(charts):
                fig = render_chart_fig(df, ch, is_dark=(st.session_state.get("theme", "light") == "dark"))
                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{i}")
                else:
                    st.caption(t("chart_not_available"))

    st.caption(t("data_preview"))
    st.dataframe(df.head(100), height=280, use_container_width=True)

# --- RIGHT: AI assistant, suggested Qs, chat ---
with right_rail:
    st.caption(t("ask_questions"))
    if st.session_state.pending_question:
        q = st.session_state.pending_question
        st.session_state.pending_question = None
        st.session_state.chat_history.append({"role": "user", "content": q})
        with st.spinner("..."):
            answer = ask_agent_question(df, result or {}, q)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    st.caption(t("suggested_questions"))
    suggested_qs = [t("q_top_revenue"), t("q_region_growth"), t("q_trends"), t("q_anomalies"), t("q_recommend")]
    for i, q in enumerate(suggested_qs):
        if st.button(q, key=f"sug_{i}", use_container_width=True):
            st.session_state.pending_question = q
            st.rerun()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_question = st.chat_input(t("ask_ai_placeholder"))
    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("assistant"):
            answer = ask_agent_question(df, result or {}, user_question)
            st.write(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()
