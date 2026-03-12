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


def parse_analysis_json(text):
    """Extract and parse JSON from model output; return None or fallback on failure."""
    text = (text or "").strip()
    if not text:
        return None
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
    return {
        "summary": {"overview": "Analysis could not be parsed.", "key_insights": [], "recommendations": [], "final_summary": ""},
        "charts": [],
    }


def profile_dataframe(df):
    """Basic profile: missing counts, duplicates, column types, readiness."""
    profile = {
        "missing_pct": {},
        "missing_total": 0,
        "duplicate_rows": int(df.duplicated().sum()),
        "total_rows": len(df),
        "column_types": {},
    }
    for col in df.columns:
        null_count = df[col].isna().sum()
        pct = round(100 * null_count / len(df), 1) if len(df) else 0
        profile["missing_pct"][col] = pct
        profile["missing_total"] += null_count
        dtype = str(df[col].dtype)
        if "int" in dtype or "float" in dtype:
            profile["column_types"][col] = "numeric"
        elif "datetime" in dtype:
            profile["column_types"][col] = "datetime"
        else:
            profile["column_types"][col] = "categorical"
    avg_null = sum(profile["missing_pct"].values()) / len(profile["missing_pct"]) if profile["missing_pct"] else 0
    profile["readiness_pct"] = max(0, min(100, round(100 - avg_null)))
    return profile


def ask_agent_for_analysis(df):
    columns = list(df.columns)
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
    sample_rows = df.head(10).to_dict(orient="records")
    for row in sample_rows:
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
    prompt = f"""
You are a professional data analysis AI agent.
Analyze the uploaded dataset and return ONLY valid JSON.
Dataset columns: {columns}
Dataset types: {dtypes}
Sample rows: {json.dumps(sample_rows, default=str)}
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
    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        raw = (response.output_text or "").strip()
        result = parse_analysis_json(raw)
        if not result:
            result = {"summary": {"overview": "Analysis unavailable.", "key_insights": [], "recommendations": [], "final_summary": ""}, "charts": []}
        valid_cols = set(df.columns)
        valid_charts = [ch for ch in result.get("charts", []) if ch.get("x_column") in valid_cols and (ch.get("y_column") in valid_cols or ch.get("aggregation") == "count")]
        result["charts"] = valid_charts if valid_charts else result.get("charts", [])[:2]
        return result
    except Exception as e:
        return {
            "summary": {"overview": f"Analysis failed: {str(e)[:150]}.", "key_insights": [], "recommendations": [], "final_summary": ""},
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
# Minimal UI (Streamlit-native, no layout hacks)
# -----------------------------
def apply_minimal_css():
    st.markdown("""
    <style>
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stSidebar"] { display: none !important; }
    .block-container { max-width: 1000px; padding-top: 1.5rem; padding-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)


# -----------------------------
# Render
# -----------------------------
apply_minimal_css()

# 1. Header
st.title(t("app_title"))
st.caption(t("badge"))

# 2. Upload block
st.subheader(t("data_source"))
uploaded_file = st.file_uploader(
    t("drag_drop") + " — " + t("supports"),
    type=["csv", "xlsx"],
    key="main_uploader",
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

# 3. KPI row
st.subheader(t("dataset_overview"))
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric(t("total_rows"), f"{n_rows:,}")
with k2:
    st.metric(t("total_columns"), n_cols)
with k3:
    st.metric(t("duplicates"), profile["duplicate_rows"])
with k4:
    st.metric(t("missing_vals"), profile["missing_total"])
with k5:
    st.metric("Readiness", f"{profile['readiness_pct']}%")
st.caption(f"{uploaded_file.name} · {size_mb:.2f} MB · {t('data_type')}: {infer_data_types(df)}")

# Generate summary (above tabs so it's always visible)
if st.button(t("generate_summary_short"), key="cta_gen"):
    with st.spinner(t("analyzing")):
        st.session_state.analysis_result = ask_agent_for_analysis(df)
    st.rerun()

# 4. Main tabbed workspace
tab_overview, tab_health, tab_insights, tab_charts, tab_ai = st.tabs([
    "Overview",
    "Data Health",
    "Insights",
    "Charts",
    "Ask AI",
])

with tab_overview:
    st.write("**File:**", uploaded_file.name, "·", f"{size_mb:.2f} MB")
    if result and result.get("summary", {}).get("overview"):
        st.write("**Overview:**", result["summary"]["overview"])
    st.caption(t("data_preview"))
    st.dataframe(df.head(100), height=320, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Export CSV", df.to_csv(index=False).encode("utf-8"), file_name=uploaded_file.name or "data.csv", mime="text/csv", key="dl_csv")
    with c2:
        rep = (result.get("summary", {}) if result else {}) or {}
        rep_text = (rep.get("overview") or "") + "\n\n## Key insights\n" + "\n".join(f"- {x}" for x in (rep.get("key_insights") or []))
        st.download_button("Executive report", rep_text.encode("utf-8"), file_name="executive_report.md", mime="text/markdown", key="dl_report")

with tab_health:
    st.metric("Duplicate rows", profile["duplicate_rows"])
    st.metric("Missing cells", profile["missing_total"])
    st.metric("Readiness", f"{profile['readiness_pct']}%")
    st.caption("Column types")
    for col, ctype in list(profile["column_types"].items())[:20]:
        st.text(f"{col}: {ctype}")
    if len(profile["column_types"]) > 20:
        st.caption(f"... and {len(profile['column_types']) - 20} more columns")

with tab_insights:
    if result is None:
        st.info("Generate summary above to see insights.")
    else:
        summary = result.get("summary") or {}
        st.write("**" + t("overview") + "**")
        st.write(summary.get("overview") or "—")
        st.write("**" + t("key_insights") + "**")
        for item in summary.get("key_insights") or []:
            st.write("-", item)
        st.write("**" + t("recommendations") + "**")
        for item in summary.get("recommendations") or []:
            st.write("-", item)
        st.write("**" + t("final_summary") + "**")
        st.write(summary.get("final_summary") or "—")

with tab_charts:
    if result is None:
        st.info("Generate summary above to see charts.")
    else:
        charts = result.get("charts") or []
        if not charts:
            st.caption(t("chart_not_available"))
        for i, ch in enumerate(charts):
            fig = render_chart_fig(df, ch, st.session_state.theme == "dark")
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{i}")
            else:
                st.caption(t("chart_not_available"))

with tab_ai:
    st.caption(t("ask_questions"))
    # Suggested questions
    suggested_qs = [
        "Top 5 rows by revenue",
        "Which region has the most growth?",
        "What are the main trends?",
        "Any anomalies or outliers?",
        "What do you recommend?",
    ]
    if st.session_state.pending_question:
        q = st.session_state.pending_question
        st.session_state.pending_question = None
        st.session_state.chat_history.append({"role": "user", "content": q})
        with st.spinner("..."):
            answer = ask_agent_question(df, result or {}, q)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()
    for i, q in enumerate(suggested_qs):
        if st.button(q, key=f"sug_{i}"):
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
