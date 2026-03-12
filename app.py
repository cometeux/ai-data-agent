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
if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = None
if "chart_explanations" not in st.session_state:
    st.session_state.chart_explanations = {}


# -----------------------------
# Helpers
# -----------------------------
def reset_app_state():
    st.session_state.analysis_result = None
    st.session_state.chat_history = []
    st.session_state.last_uploaded_name = None
    st.session_state.suggested_questions = None
    st.session_state.chart_explanations = {}


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
    """Smart profile: types, readiness score, health issues, recommended columns."""
    n = len(df)
    profile = {
        "missing_pct": {},
        "missing_total": 0,
        "duplicate_rows": int(df.duplicated().sum()),
        "total_rows": n,
        "total_columns": len(df.columns),
        "column_types": {},
        "unique_counts": {},
        "high_null_columns": [],
        "suspicious_columns": [],
        "mixed_type_warnings": [],
        "quality_recommendations": [],
        "recommended_measure_columns": [],
        "recommended_grouping_columns": [],
        "id_like_columns": [],
        "text_heavy_columns": [],
    }
    for col in df.columns:
        s = df[col]
        null_count = s.isna().sum()
        pct = round(100 * null_count / n, 1) if n else 0
        profile["missing_pct"][col] = pct
        profile["missing_total"] += null_count
        profile["unique_counts"][col] = int(s.nunique())
        dtype = str(s.dtype)
        if "int" in dtype or "float" in dtype:
            profile["column_types"][col] = "numeric"
        elif "datetime" in dtype:
            profile["column_types"][col] = "datetime"
        else:
            profile["column_types"][col] = "categorical"
        if pct > 20:
            profile["high_null_columns"].append((col, pct))
        if col.lower().endswith("id") or col.lower() == "id" or (profile["unique_counts"][col] == n and n > 10):
            profile["id_like_columns"].append(col)
        if dtype == "object" and s.notna().any():
            try:
                if s.dropna().astype(str).str.len().max() > 80:
                    profile["text_heavy_columns"].append(col)
            except Exception:
                pass
    profile["high_null_columns"].sort(key=lambda x: -x[1])
    num_cols = [c for c, t in profile["column_types"].items() if t == "numeric"]
    cat_cols = [c for c, t in profile["column_types"].items() if t == "categorical"]
    profile["recommended_measure_columns"] = num_cols[:15]
    profile["recommended_grouping_columns"] = [c for c in cat_cols if profile["unique_counts"].get(c, 0) <= 50 and c not in profile["id_like_columns"]][:15]
    if not profile["recommended_grouping_columns"] and cat_cols:
        profile["recommended_grouping_columns"] = cat_cols[:10]
    avg_null = sum(profile["missing_pct"].values()) / len(profile["missing_pct"]) if profile["missing_pct"] else 0
    dup_penalty = min(15, profile["duplicate_rows"] // 50)
    high_null_penalty = min(20, len(profile["high_null_columns"]) * 5)
    score = max(0, min(100, round(100 - avg_null - dup_penalty - high_null_penalty)))
    profile["readiness_pct"] = score
    factors = []
    if avg_null > 5:
        factors.append(f"Missing values ({avg_null:.0f}% of cells on average)")
    if profile["duplicate_rows"] > 0:
        factors.append(f"Duplicate rows ({profile['duplicate_rows']})")
    if profile["high_null_columns"]:
        factors.append(f"Columns with >20% nulls: {len(profile['high_null_columns'])}")
    profile["readiness_factors"] = factors
    profile["readiness_summary"] = "Data is suitable for analysis." if score >= 70 else "Data has quality issues; review before heavy analysis."
    for col, pct in profile["high_null_columns"][:5]:
        profile["quality_recommendations"].append(f"Column '{col}' has {pct}% missing values.")
    if profile["duplicate_rows"] > 0:
        profile["quality_recommendations"].append(f"Remove or review {profile['duplicate_rows']} duplicate rows.")
    if not profile["quality_recommendations"]:
        profile["quality_recommendations"].append("No major quality issues detected.")
    return profile


def _validate_chart(df, profile, ch):
    """Ensure chart uses valid columns and sensible type. Returns True if chart is valid."""
    valid = set(df.columns)
    x, y = ch.get("x_column"), ch.get("y_column")
    agg = ch.get("aggregation") or "sum"
    if not x or x not in valid:
        return False
    if agg == "count":
        return True
    if not y or y not in valid:
        return False
    ctypes = profile.get("column_types", {})
    xt, yt = ctypes.get(x), ctypes.get(y)
    chart_type = (ch.get("chart_type") or "bar").lower()
    if chart_type in ("bar", "line", "pie"):
        return yt == "numeric" and (xt == "categorical" or xt == "datetime" or profile["unique_counts"].get(x, 0) <= 100)
    if chart_type == "scatter":
        return xt == "numeric" and yt == "numeric"
    return True


def ask_agent_for_analysis(df, profile):
    columns = list(df.columns)
    measure_cols = profile.get("recommended_measure_columns", []) or [c for c, t in profile.get("column_types", {}).items() if t == "numeric"][:10]
    group_cols = profile.get("recommended_grouping_columns", []) or [c for c, t in profile.get("column_types", {}).items() if t == "categorical"][:10]
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
    sample_rows = df.head(12).to_dict(orient="records")
    for row in sample_rows:
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
    prompt = f"""You are a professional data analysis AI agent. Analyze this dataset and return ONLY valid JSON.

COLUMNS: {columns}
TYPES: {profile.get('column_types', {})}
MEASURE COLUMNS (use for y-axis): {measure_cols}
GROUPING COLUMNS (use for x-axis): {group_cols}
SAMPLE ROWS: {json.dumps(sample_rows, default=str)}
DATA QUALITY: {profile.get('missing_total')} missing cells, {profile.get('duplicate_rows')} duplicate rows.

Return this exact JSON structure (no markdown, no extra text):
{{
  "summary": {{
    "overview": "2-3 sentence overview of what the data contains and its main use",
    "top_finding": "Single most important finding in one sentence",
    "biggest_risk": "Main data or business risk suggested by the data",
    "biggest_opportunity": "Main opportunity suggested by the data",
    "notable_trend": "One notable trend or pattern",
    "data_quality_concern": "One sentence on data quality if relevant, else empty string",
    "recommended_next_step": "One concrete recommended next step for the user",
    "key_insights": ["insight 1", "insight 2", "insight 3"],
    "recommendations": ["recommendation 1", "recommendation 2"],
    "final_summary": "One sentence executive conclusion"
  }},
  "charts": [
    {{ "title": "Chart title", "chart_type": "bar", "x_column": "exact_column_from_list", "y_column": "exact_column_from_list", "aggregation": "sum", "explanation": "What this chart shows, why it matters, and what action it suggests in 1-2 sentences." }},
    {{ "title": "Chart title", "chart_type": "line or bar or pie", "x_column": "...", "y_column": "...", "aggregation": "mean or sum or count", "explanation": "Brief explanation." }}
  ]
}}
RULES: Use ONLY column names from COLUMNS. chart_type: bar, line, pie, scatter. For bar/line/pie use a grouping column for x_column and measure column for y_column. aggregation: sum, mean, count. Return at least 2 charts. Include an "explanation" for each chart."""
    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        raw = (response.output_text or "").strip()
        result = parse_analysis_json(raw)
        if not result:
            result = _default_analysis_result()
        summary = result.get("summary") or {}
        for key in ("top_finding", "biggest_risk", "biggest_opportunity", "notable_trend", "data_quality_concern", "recommended_next_step"):
            if key not in summary:
                summary[key] = ""
        result["summary"] = summary
        valid_charts = []
        for ch in result.get("charts", []):
            if _validate_chart(df, profile, ch):
                if "explanation" not in ch:
                    ch["explanation"] = "Chart of selected metrics."
                valid_charts.append(ch)
        result["charts"] = valid_charts[:6] if valid_charts else []
        return result
    except Exception as e:
        return {"summary": {**_default_analysis_result()["summary"], "overview": f"Analysis failed: {str(e)[:120]}."}, "charts": []}


def _default_analysis_result():
    return {
        "summary": {
            "overview": "Analysis unavailable.",
            "top_finding": "", "biggest_risk": "", "biggest_opportunity": "", "notable_trend": "",
            "data_quality_concern": "", "recommended_next_step": "",
            "key_insights": [], "recommendations": [], "final_summary": "",
        },
        "charts": [],
    }


def ask_agent_suggested_questions(df, profile):
    """Generate 5–6 short, dataset-specific suggested questions. File-aware and context-aware."""
    columns = list(df.columns)[:40]
    col_types = profile.get("column_types", {})
    measure = profile.get("recommended_measure_columns", [])[:8]
    group = profile.get("recommended_grouping_columns", [])[:8]
    readiness = profile.get("readiness_pct", 100)
    high_null = [c for c, _ in profile.get("high_null_columns", [])[:5]]
    dup_count = profile.get("duplicate_rows", 0)
    n_rows = profile.get("total_rows", len(df))

    quality_note = ""
    if readiness < 70 or high_null or dup_count > 0:
        quality_note = (
            " Data quality is a concern: "
            + (f"readiness score {readiness}%, " if readiness < 70 else "")
            + (f"columns with many nulls: {high_null}. " if high_null else "")
            + (f"{dup_count} duplicate rows. " if dup_count > 0 else "")
            + "Include at least one question about data quality, reliability, or what is safe to analyze."
        )

    prompt = f"""You are generating suggested follow-up questions for a user who just uploaded a dataset. The questions must be specific to THIS dataset, not generic.

DATASET CONTEXT:
- Columns: {columns}
- Column types: {col_types}
- Likely measure columns (for metrics/sums): {measure}
- Likely grouping/category columns: {group}
- Rows: {n_rows}
- Readiness score (0–100): {readiness}
- Columns with high null %: {high_null or 'none'}
- Duplicate rows: {dup_count}
{quality_note}

RULES:
- Generate exactly 5 or 6 short questions (each under 12 words).
- Base questions on actual column names and likely use cases (e.g. growth, top segments, comparisons, outliers, drivers, trends).
- If the data looks like sales/performance: ask about growth, top segments, changes, comparisons.
- If the data looks like surveys/students/people: ask about score drivers, relationships, outliers, segments.
- If data quality is low: include at least one question about cleaning, reliability, or safe analysis.
- Be specific (mention column or domain where helpful), not vague.
- Return ONLY a JSON array of question strings, e.g. ["Question one?", "Question two?"]. No other text."""

    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        raw = (response.output_text or "").strip()
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            out = json.loads(raw[start:end])
            if isinstance(out, list) and len(out) >= 3:
                return [str(q).strip()[:100] for q in out[:6]]
    except Exception:
        pass
    # Fallback only if API fails: still dataset-aware from columns
    fallback = []
    if measure and group:
        fallback = [
            f"Which {group[0]} has the highest {measure[0]}?",
            f"What are the main drivers of {measure[0] if measure else 'performance'}?",
            "Are there outliers or anomalies?",
            "What should I investigate next?",
        ]
    if readiness < 70 or high_null:
        fallback.append("How reliable is this data for analysis?")
    while len(fallback) < 5:
        fallback.append("What are the key patterns in this data?")
    return fallback[:6]


def ask_agent_chart_explanation(chart_spec, df):
    """Return 1-2 sentence explanation of what the chart shows and why it matters."""
    try:
        title = chart_spec.get("title", "Chart")
        x, y = chart_spec.get("x_column"), chart_spec.get("y_column")
        agg = chart_spec.get("aggregation", "sum")
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"Chart: {title}. X: {x}, Y: {y}, aggregation: {agg}. In 1-2 sentences, what does this chart show and why it matters. No preamble.",
        )
        return (response.output_text or "").strip()[:300]
    except Exception:
        return "This chart visualizes the selected dimensions and measures."


def ask_agent_question(df, analysis_result, user_question, profile=None):
    columns = list(df.columns)
    sample = df.head(15).to_dict(orient="records")
    for row in sample:
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
    profile_summary = ""
    if profile:
        profile_summary = f"Data profile: {profile.get('total_rows')} rows, {profile.get('total_columns', len(columns))} columns; missing cells: {profile.get('missing_total')}; duplicate rows: {profile.get('duplicate_rows')}; readiness: {profile.get('readiness_pct')}%. Column types: {profile.get('column_types', {})}."
    prompt = f"""You are an analytical data assistant. Be specific and data-grounded. Use numbers and column names when relevant.

{profile_summary}
Dataset columns: {columns}
Sample rows (first 15): {json.dumps(sample, default=str)}
Existing analysis summary (if any): {json.dumps(analysis_result.get("summary", {}) if isinstance(analysis_result, dict) else {}, ensure_ascii=False)}

User question: {user_question}

Answer in 2-4 short paragraphs. Be analytical and decision-oriented. Base answers only on the data and analysis above. If the data cannot answer the question, say so briefly."""
    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        return (response.output_text or "").strip()
    except Exception as e:
        return f"Sorry, I couldn't process that: {str(e)[:100]}."


def prepare_chart_data(df, x_column, y_column, aggregation):
    data = df.copy()
    if aggregation == "count" or not y_column:
        data = data.groupby(x_column, as_index=False).size()
        data.columns = [x_column, "count"]
        return data, "count"
    if aggregation == "sum":
        data = data.groupby(x_column, as_index=False)[y_column].sum()
    elif aggregation == "mean":
        data = data.groupby(x_column, as_index=False)[y_column].mean()
    else:
        data = data.groupby(x_column, as_index=False)[y_column].sum()
    return data, y_column


def render_chart_fig(df, chart, is_dark):
    chart_type = (chart.get("chart_type") or "bar").lower()
    x_column = chart.get("x_column")
    y_column = chart.get("y_column")
    aggregation = chart.get("aggregation") or "sum"
    if not x_column or (x_column not in df.columns):
        return None
    if aggregation != "count" and (not y_column or y_column not in df.columns):
        return None
    data, final_y = prepare_chart_data(df, x_column, y_column or x_column, aggregation)
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
# Premium UI (compact, glass-like, indigo accents — Streamlit-safe CSS only)
# -----------------------------
def apply_minimal_css():
    st.markdown("""
    <style>
    /* Hide chrome */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stSidebar"] { display: none !important; }

    /* Compact container */
    .block-container {
        max-width: 980px;
        padding: 0.75rem 1.25rem 1.25rem;
    }

    /* Subtle dark gradient + soft indigo glow */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(165deg, #0f0f14 0%, #12121a 40%, #15152a 100%) !important;
    }
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top: -20%;
        left: 50%;
        transform: translateX(-50%);
        width: 80%;
        height: 50%;
        background: radial-gradient(ellipse, rgba(99, 102, 241, 0.08) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }
    .block-container { position: relative; z-index: 1; }

    /* Tighter typography and spacing */
    h1 { font-size: 1.5rem !important; margin-bottom: 0.1rem !important; }
    [data-testid="stMarkdown"] p { margin-bottom: 0.2rem !important; }
    [data-testid="stVerticalBlock"] > div { gap: 0.35rem !important; }

    /* Glass-like KPI cards */
    [data-testid="stMetric"] {
        background: rgba(30, 27, 75, 0.4);
        padding: 0.6rem 0.85rem;
        border-radius: 10px;
        border: 1px solid rgba(139, 92, 246, 0.15);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }
    [data-testid="stMetric"] label {
        color: #a5b4fc !important;
        font-size: 0.7rem !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #e0e7ff !important;
        font-size: 1.15rem !important;
        font-weight: 600;
    }

    /* Primary button: indigo/violet */
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: #fff !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 0 2px 10px rgba(79, 70, 229, 0.35);
    }
    .stButton > button:hover {
        box-shadow: 0 4px 14px rgba(124, 58, 237, 0.45);
        filter: brightness(1.05);
    }

    /* Tabs: modern, active accent */
    [data-testid="stTabs"] {
        margin-top: 0.5rem;
    }
    [data-testid="stTabs"] [role="tab"] {
        padding: 0.45rem 0.9rem !important;
        border-radius: 8px;
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.2) !important;
        color: #c7d2fe !important;
    }

    /* Upload area: contained feel */
    [data-testid="stFileUploader"] {
        border-radius: 10px;
        padding: 0.5rem;
        background: rgba(30, 27, 75, 0.25);
        border: 1px solid rgba(139, 92, 246, 0.12);
    }
    [data-testid="stFileUploader"] section {
        border-radius: 8px;
        border-color: rgba(139, 92, 246, 0.2) !important;
    }

    /* Expander: softer */
    .streamlit-expanderHeader {
        background: rgba(30, 27, 75, 0.2);
        border-radius: 8px;
        border: 1px solid rgba(139, 92, 246, 0.1);
    }

    /* Chat / AI section refinement */
    [data-testid="stChatInput"] {
        border-radius: 10px;
        border: 1px solid rgba(139, 92, 246, 0.2);
        background: rgba(30, 27, 75, 0.3) !important;
    }
    [data-testid="stChatMessage"] {
        background: rgba(30, 27, 75, 0.2) !important;
        border-radius: 10px;
        border: 1px solid rgba(139, 92, 246, 0.08);
        padding: 0.6rem 0.9rem !important;
    }

    /* Subheaders: compact, accent */
    h2, h3 { font-size: 0.95rem !important; margin-top: 0.4rem !important; margin-bottom: 0.3rem !important; color: #a5b4fc !important; }
    .stCaption { color: #94a3b8 !important; }

    /* Info/success boxes: subtle glass */
    [data-testid="stAlert"] {
        border-radius: 8px;
        border: 1px solid rgba(139, 92, 246, 0.15);
    }

    /* Dividers lighter */
    hr { border-color: rgba(139, 92, 246, 0.12) !important; margin: 0.4rem 0 !important; }

    /* Suggested questions: compact chip-style (Ask AI tab) */
    [role="tabpanel"]:nth-of-type(5) [data-testid="column"] .stButton > button {
        font-size: 0.8rem !important;
        padding: 0.35rem 0.65rem !important;
        border-radius: 999px !important;
        background: rgba(51, 65, 85, 0.5) !important;
        border: 1px solid rgba(148, 163, 184, 0.25) !important;
        color: #c7d2fe !important;
        font-weight: 500 !important;
    }
    [role="tabpanel"]:nth-of-type(5) [data-testid="column"] .stButton > button:hover {
        background: rgba(99, 102, 241, 0.25) !important;
        border-color: rgba(139, 92, 246, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)


# -----------------------------
# Render
# -----------------------------
apply_minimal_css()

# 1. Header (compact: title + badge)
col_title, col_badge = st.columns([3, 1])
with col_title:
    st.title(t("app_title"))
with col_badge:
    st.caption(t("badge"))
st.divider()

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
    st.session_state.suggested_questions = None
    st.session_state.chart_explanations = {}

try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(str(e))
    st.stop()

profile = profile_dataframe(df)
size_mb = file_size_mb(uploaded_file)
n_rows, n_cols = df.shape
result = st.session_state.analysis_result

# Generate file-aware suggested questions once per file (when None)
if st.session_state.suggested_questions is None:
    with st.spinner("Preparing suggested questions..."):
        st.session_state.suggested_questions = ask_agent_suggested_questions(df, profile)
    st.rerun()

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
st.caption(f"{uploaded_file.name} · {size_mb:.2f} MB · {t('data_type')}: {infer_data_types(df)}" + (f" · {profile.get('readiness_summary', '')}" if profile.get("readiness_summary") else ""))

# Generate summary + readiness expander (one row)
row_btn, row_exp = st.columns([1, 2])
with row_btn:
    if st.button(t("generate_summary_short"), key="cta_gen"):
        with st.spinner(t("analyzing")):
            st.session_state.analysis_result = ask_agent_for_analysis(df, profile)
        st.rerun()
with row_exp:
    if profile.get("readiness_factors"):
        with st.expander("What affects the readiness score"):
            for f in profile["readiness_factors"]:
                st.write("-", f)

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
        lines = [
            "# Executive Summary",
            "",
            "## Overview",
            rep.get("overview") or "—",
            "",
            "## Data Readiness",
            f"Score: {profile.get('readiness_pct', 0)}/100. {profile.get('readiness_summary', '')}",
            "",
            "## Top Finding",
            rep.get("top_finding") or "—",
            "",
            "## Biggest Risk",
            rep.get("biggest_risk") or "—",
            "",
            "## Biggest Opportunity",
            rep.get("biggest_opportunity") or "—",
            "",
            "## Notable Trend",
            rep.get("notable_trend") or "—",
            "",
            "## Data Quality Note",
            rep.get("data_quality_concern") or "—",
            "",
            "## Recommended Next Step",
            rep.get("recommended_next_step") or "—",
            "",
            "## Key Insights",
        ]
        lines.extend([f"- {x}" for x in (rep.get("key_insights") or [])])
        lines.extend(["", "## Recommendations", ""])
        lines.extend([f"- {x}" for x in (rep.get("recommendations") or [])])
        if result and result.get("charts"):
            lines.extend(["", "## Chart Explanations", ""])
            for ch in result["charts"]:
                lines.append(f"- **{ch.get('title', 'Chart')}:** " + (ch.get("explanation") or ""))
        rep_text = "\n".join(lines)
        st.download_button("Executive report", rep_text.encode("utf-8"), file_name="executive_report.md", mime="text/markdown", key="dl_report")

with tab_health:
    st.write("**Data Readiness Score:**", f"{profile['readiness_pct']}/100 —", profile.get("readiness_summary", ""))
    st.divider()
    h1, h2, h3 = st.columns(3)
    with h1:
        st.metric("Missing cells", profile["missing_total"])
        pct = (100 * profile["missing_total"] / (profile["total_rows"] * len(profile["column_types"]))) if profile.get("column_types") else 0
        st.caption(f"({pct:.1f}% of all cells)")
    with h2:
        st.metric("Duplicate rows", profile["duplicate_rows"])
    with h3:
        st.metric("Readiness", f"{profile['readiness_pct']}%")
    if profile.get("high_null_columns"):
        st.subheader("Columns with highest null %")
        for col, pct in profile["high_null_columns"][:10]:
            st.write(f"- **{col}**: {pct}% null")
    st.subheader("Quality recommendations")
    for rec in profile.get("quality_recommendations", []):
        st.write("-", rec)
    st.subheader("Column types (smart profiling)")
    num = [c for c, t in profile.get("column_types", {}).items() if t == "numeric"]
    cat = [c for c, t in profile.get("column_types", {}).items() if t == "categorical"]
    dt = [c for c, t in profile.get("column_types", {}).items() if t == "datetime"]
    if num:
        st.caption("Numeric (recommended for measures): " + ", ".join(num[:12]) + (" ..." if len(num) > 12 else ""))
    if cat:
        st.caption("Categorical (recommended for grouping): " + ", ".join(cat[:12]) + (" ..." if len(cat) > 12 else ""))
    if dt:
        st.caption("Datetime: " + ", ".join(dt))
    if profile.get("id_like_columns"):
        st.caption("ID-like columns: " + ", ".join(profile["id_like_columns"][:10]))
    if profile.get("text_heavy_columns"):
        st.caption("Text-heavy columns: " + ", ".join(profile["text_heavy_columns"][:5]))

with tab_insights:
    if result is None:
        st.info("Generate summary above to see insights.")
    else:
        summary = result.get("summary") or {}
        st.write("**" + t("overview") + "**")
        st.write(summary.get("overview") or "—")
        # Insight cards
        cards = [
            ("Top Finding", summary.get("top_finding")),
            ("Biggest Risk", summary.get("biggest_risk")),
            ("Biggest Opportunity", summary.get("biggest_opportunity")),
            ("Notable Trend", summary.get("notable_trend")),
            ("Data Quality Concern", summary.get("data_quality_concern")),
            ("Recommended Next Step", summary.get("recommended_next_step")),
        ]
        for label, value in cards:
            if value:
                with st.container():
                    st.write(f"**{label}**")
                    st.info(value) if label in ("Biggest Risk", "Data Quality Concern") else st.success(value) if label in ("Biggest Opportunity", "Recommended Next Step") else st.write(value)
        st.write("**" + t("key_insights") + "**")
        for item in summary.get("key_insights") or []:
            st.write("-", item)
        st.write("**" + t("recommendations") + "**")
        for item in summary.get("recommendations") or []:
            st.write("-", item)
        st.write("**" + t("final_summary") + "**")
        st.write(summary.get("final_summary") or "—")

with tab_charts:
    # Simple chart builder
    st.subheader("Build your own chart")
    measure_cols = profile.get("recommended_measure_columns") or [c for c, t in profile.get("column_types", {}).items() if t == "numeric"]
    group_cols = profile.get("recommended_grouping_columns") or [c for c, t in profile.get("column_types", {}).items() if t == "categorical"]
    if not group_cols:
        group_cols = list(df.columns)[:10]
    if not measure_cols:
        measure_cols = list(df.columns)[:10]
    cb1, cb2, cb3, cb4 = st.columns(4)
    with cb1:
        chart_type_build = st.selectbox("Chart type", ["bar", "line", "pie", "scatter"], key="cb_type")
    with cb2:
        x_build = st.selectbox("X (category)", group_cols, key="cb_x")
    with cb3:
        y_build = st.selectbox("Y (measure)", ["count"] + measure_cols, key="cb_y")
    with cb4:
        agg_build = st.selectbox("Aggregation", ["sum", "mean", "count"], key="cb_agg")
    use_count = y_build == "count"
    build_spec = {"chart_type": chart_type_build, "x_column": x_build, "y_column": x_build if use_count else y_build, "aggregation": "count" if use_count else agg_build, "title": f"Count by {x_build}" if use_count else f"{y_build} by {x_build}"}
    fig_build = render_chart_fig(df, build_spec, st.session_state.theme == "dark")
    if fig_build is not None:
        st.plotly_chart(fig_build, use_container_width=True, key="chart_builder")
    st.divider()
    st.subheader("AI-generated charts")
    if result is None:
        st.info("Generate summary above to see AI-recommended charts.")
    else:
        charts = result.get("charts") or []
        if not charts:
            st.caption(t("chart_not_available"))
        for i, ch in enumerate(charts):
            st.write("**" + (ch.get("title") or "Chart") + "**")
            fig = render_chart_fig(df, ch, st.session_state.theme == "dark")
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{i}")
            else:
                st.caption(t("chart_not_available"))
            expl = ch.get("explanation") or st.session_state.chart_explanations.get(i)
            if expl:
                st.caption("**Explain this chart:** " + expl)
            elif st.button("Explain this chart", key=f"explain_{i}"):
                with st.spinner("..."):
                    st.session_state.chart_explanations[i] = ask_agent_chart_explanation(ch, df)
                st.rerun()

with tab_ai:
    st.caption(t("ask_questions"))
    suggested_qs = st.session_state.suggested_questions or []
    st.caption("Suggested questions (click to ask):")
    # Compact chip-style grid (3 columns)
    n = len(suggested_qs)
    if n > 0:
        cols = st.columns(3)
        for i, q in enumerate(suggested_qs):
            with cols[i % 3]:
                if st.button(q, key=f"sug_{i}"):
                    st.session_state.pending_question = q
                    st.rerun()
    if st.session_state.pending_question:
        q = st.session_state.pending_question
        st.session_state.pending_question = None
        st.session_state.chat_history.append({"role": "user", "content": q})
        with st.spinner("..."):
            answer = ask_agent_question(df, result or {}, q, profile)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    user_question = st.chat_input(t("ask_ai_placeholder"))
    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("assistant"):
            answer = ask_agent_question(df, result or {}, user_question, profile)
            st.write(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()
