# -*- coding: utf-8 -*-
import html
import json
import pandas as pd
import streamlit as st
import plotly.express as px
from openai import OpenAI

st.set_page_config(
    page_title="Datara",
    page_icon="🫆",
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
        "hero_title": "Is your data usable? What matters? What's next?",
        "hero_subtitle": "Upload your dataset to generate an instant executive summary and deep-dive analysis.",
        "hero_desc": "Upload your dataset, and I'll automatically generate insights, visual summaries, and actionable recommendations.",
        "ask_ai_title": "Ask AI",
        "suggested_label": "Suggested questions (from this dataset):",
        "chat_placeholder": "Ask anything about your data...",
        "tab_overview": "Overview",
        "tab_health": "Data Health",
        "tab_findings": "Top Findings",
        "tab_charts": "Charts",
        "generate_cta": "Generate Executive Summary",
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
        "hero_title": "هل بياناتك قابلة للاستخدام؟ ما المهم؟ وما التالي؟",
        "hero_subtitle": "ارفع مجموعة البيانات لتوليد ملخص تنفيذي فوري وتحليل معمق.",
        "hero_desc": "ارفع مجموعة البيانات وسأقوم تلقائياً بتوليد الرؤى والملخصات المرئية والتوصيات القابلة للتطبيق.",
        "ask_ai_title": "اسأل الذكاء الاصطناعي",
        "suggested_label": "أسئلة مقترحة (من هذه البيانات):",
        "chat_placeholder": "اسأل أي شيء عن بياناتك...",
        "tab_overview": "نظرة عامة",
        "tab_health": "صحة البيانات",
        "tab_findings": "أبرز النتائج",
        "tab_charts": "الرسوم البيانية",
        "generate_cta": "إنشاء الملخص التنفيذي",
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
if "data_formulas_result" not in st.session_state:
    st.session_state.data_formulas_result = None


# -----------------------------
# Helpers
# -----------------------------
def reset_app_state():
    st.session_state.analysis_result = None
    st.session_state.chat_history = []
    st.session_state.last_uploaded_name = None
    st.session_state.suggested_questions = None
    st.session_state.chart_explanations = {}
    st.session_state.data_formulas_result = None


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
RULES: Use ONLY column names from COLUMNS. chart_type: bar, line, pie, scatter. For bar/line/pie use a grouping column for x_column and measure column for y_column. aggregation: sum, mean, count. Return exactly 2 charts (no more). Include an "explanation" for each chart."""
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
        result["charts"] = valid_charts[:2] if valid_charts else []
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
- Optionally include one question about ready-to-paste formulas (Excel/Sheets) for cleaning or fixing the data.
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


def ask_agent_data_formulas(profile, df):
    """Return ready-to-paste formulas (Excel, Google Sheets, optionally pandas/SQL) for common data health fixes."""
    columns = list(df.columns)
    ctypes = profile.get("column_types") or {}
    sample = df.head(10).to_dict(orient="records")
    for row in sample:
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
    prompt = f"""You are a data quality assistant. Given this dataset profile, suggest ready-to-paste formulas for common fixes.

Dataset: {profile.get('total_rows')} rows, {profile.get('total_columns')} columns. Columns: {columns}.
Column types: {ctypes}. Missing cells: {profile.get('missing_total')}. Duplicate rows: {profile.get('duplicate_rows')}.
Sample (first 10 rows): {json.dumps(sample, default=str)}

Provide 3–6 ready-to-paste formulas. For EACH formula give:
1. **Type**: Excel, Google Sheets, and/or pandas (or SQL if relevant)
2. **Use case**: e.g. "Fill missing values", "Trim spaces", "Standardize text", "Extract part of string", "Bucket/categorize", "Detect duplicates", "Fix case", "Date cleanup", "Conditional replacement"
3. **Formula/code**: exact, copy-paste ready (use placeholders like A2 or column names from the list above)
4. **Brief explanation**: one line

Format clearly with headers and code blocks so the user can copy each formula directly. Prefer Excel and Google Sheets first; add pandas snippets where helpful. Be concise."""

    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        return (response.output_text or "").strip()
    except Exception as e:
        return f"Could not generate formulas: {str(e)[:150]}"


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

Answer in 2-4 short paragraphs. Be analytical and decision-oriented. Base answers only on the data and analysis above. If the data cannot answer the question, say so briefly.
When the user asks for help cleaning, fixing, or improving the data (e.g. fill missing values, trim spaces, standardize text, duplicates, dates), provide ready-to-paste formulas: give Excel and/or Google Sheets formulas and optionally pandas snippets in clear code blocks, with a one-line explanation for each. Use column names from the dataset when relevant."""
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


# Chart palette — 🫆 lilac / orchid / muted violet / deep plum (premium, soft)
DATARA_CHART_COLORS = ["#D4ABFE", "#B98AF9", "#A978F4", "#7E5AB6", "#6d28d9", "#2A1E3F"]


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
    template = "plotly_dark" if is_dark else "plotly_white"
    if chart_type == "bar":
        fig = px.bar(data, x=x_column, y=final_y, title=None, template=template, color_discrete_sequence=DATARA_CHART_COLORS)
    elif chart_type == "line":
        fig = px.line(data, x=x_column, y=final_y, title=None, template=template, color_discrete_sequence=DATARA_CHART_COLORS)
    elif chart_type == "pie":
        fig = px.pie(data, names=x_column, values=final_y, title=None, color_discrete_sequence=DATARA_CHART_COLORS)
    elif chart_type == "scatter":
        fig = px.scatter(data, x=x_column, y=final_y, title=None, template=template, color_discrete_sequence=DATARA_CHART_COLORS)
    else:
        return None
    if is_dark:
        fig.update_layout(
            paper_bgcolor="#161121",
            plot_bgcolor="#2A1E3F",
            font=dict(family="Inter, sans-serif", color="#ffffff", size=12),
            margin=dict(l=24, r=24, t=12, b=24),
            xaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.06)",
                zerolinecolor="rgba(255, 255, 255, 0.08)",
                tickfont=dict(color="#9B92AB", size=11),
                title_font=dict(color="#9B92AB", size=12),
            ),
            yaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.06)",
                zerolinecolor="rgba(255, 255, 255, 0.08)",
                tickfont=dict(color="#9B92AB", size=11),
                title_font=dict(color="#9B92AB", size=12),
            ),
            colorway=DATARA_CHART_COLORS,
            legend=dict(bgcolor="rgba(42, 30, 63, 0.95)", font=dict(color="#9B92AB", size=11), bordercolor="rgba(212, 171, 254, 0.14)"),
            hoverlabel=dict(bgcolor="#2A1E3F", font=dict(color="#ffffff", size=12), bordercolor="rgba(212, 171, 254, 0.2)"),
            modebar=dict(bgcolor="rgba(42, 30, 63, 0.9)", color="#9B92AB", activecolor="#A978F4"),
        )
        if chart_type == "pie":
            fig.update_traces(marker=dict(colors=DATARA_CHART_COLORS))
        else:
            fig.update_traces(marker=dict(color=DATARA_CHART_COLORS[0]), selector=dict(type="bar"))
            fig.update_traces(line=dict(color=DATARA_CHART_COLORS[0]), selector=dict(type="scatter", mode="lines"))
            # Scatter points use color_discrete_sequence from px.scatter
    else:
        fig.update_layout(
            paper_bgcolor="rgba(255,255,255,0.6)",
            plot_bgcolor="rgba(248,250,252,0.8)",
            font=dict(color="#0f172a", size=12),
            margin=dict(l=24, r=24, t=12, b=24),
            xaxis=dict(gridcolor="rgba(15,23,42,0.08)", zerolinecolor="rgba(15,23,42,0.1)"),
            yaxis=dict(gridcolor="rgba(15,23,42,0.08)", zerolinecolor="rgba(15,23,42,0.1)"),
            colorway=DATARA_CHART_COLORS,
        )
    return fig


# -----------------------------
# Ask AI response panel (full-width, scrollable body only — no chat_message wrapper)
# -----------------------------
def _datara_ask_ai_response_panel(content):
    """Full-width response panel: single column, normal reading layout, internal scroll. Plain text."""
    body_escaped = html.escape(content).replace("\n", "<br>")
    return (
        f'<div class="datara-ask-ai-response">'
        f'<div class="datara-ask-ai-response-body">{body_escaped}</div>'
        f'</div>'
    )


# -----------------------------
# Finding card icons (SVG, theme-muted)
# -----------------------------
FINDING_ICONS = {
    "Top Finding": '<span class="datara-finding-icon"><svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z"/><path d="M5 21h14"/></svg></span>',
    "Biggest Risk": '<span class="datara-finding-icon"><svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg></span>',
    "Biggest Opportunity": '<span class="datara-finding-icon"><svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17l9.2-9.2M17 17V7H7"/></svg></span>',
    "Recommended Next Step": '<span class="datara-finding-icon"><svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg></span>',
}


# -----------------------------
# Datara UI — design-system fidelity (Inter, JetBrains Mono, #0a0812, #a78bfa)
# -----------------------------
def apply_css():
    # Single HTML block starting with < so Streamlit doesn't render as code
    st.markdown("""<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* === Datara theme tokens: dark = :root; light = body.datara-theme-light overrides === */
    :root {
        /* Dark theme (default) — lilac–orchid–violet */
        --bg-base: #06040A;
        --bg-panel: #161121;
        --bg-surface: #2A1E3F;
        --accent-primary: #D4ABFE;
        --accent-secondary: #B98AF9;
        --accent-glow: #A978F4;
        --muted-violet: #7E5AB6;
        --deep-plum: #2A1E3F;
        --border-violet: rgba(212, 171, 254, 0.14);
        --border-dim: rgba(212, 171, 254, 0.1);
        --border-medium: rgba(212, 171, 254, 0.18);
        --border-bright: rgba(212, 171, 254, 0.26);
        --text-primary: #ffffff;
        --text-secondary: #9B92AB;
        --text-muted: #6e6580;
        --font-sans: 'Inter', -apple-system, sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
        --radius-sm: 12px;
        --radius-md: 18px;
        --radius-lg: 24px;
    }
    * { box-sizing: border-box; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stSidebar"] { display: none !important; }

    /* === HARD OVERRIDE: remove all Streamlit default accents (red/blue), force Datara === */
    [data-baseweb="radio"] [role="radio"],
    [data-baseweb="radio"] circle,
    .stRadio > div [role="radiogroup"] *,
    [data-baseweb="button"]:focus,
    [data-baseweb="button"]:focus-visible,
    [data-baseweb="input"]:focus,
    [data-baseweb="textarea"]:focus,
    [data-baseweb="select"]:focus,
    [data-baseweb="select"]:focus-within,
    [data-baseweb="slider"]:focus,
    [data-baseweb="checkbox"]:focus { outline: none !important; border-color: var(--accent-primary) !important; box-shadow: none !important; }
    [data-baseweb="radio"] [aria-checked="true"] { background: var(--accent-primary) !important; border-color: var(--accent-primary) !important; }
    [data-baseweb="radio"] [aria-checked="true"] circle { fill: var(--accent-primary) !important; }
    a:focus, a:focus-visible { outline: none !important; color: var(--accent-primary) !important; }
    [data-baseweb="tag"] { background: var(--bg-panel) !important; border-color: var(--border-dim) !important; color: var(--text-secondary) !important; }
    .stRadio, .stRadio * { box-shadow: none !important; }
    [data-testid="stRadio"] label { background: transparent !important; border: none !important; }

    /* === Streamlit theme overrides: Datara accent only === */
    input:focus, input:focus-visible, textarea:focus, textarea:focus-visible,
    [data-testid="stChatInput"] textarea:focus,
    [data-testid="stChatInput"] textarea:focus-visible,
    [data-testid="stFileUploader"]:focus-within,
    .stButton > button:focus, .stButton > button:focus-visible,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextInput"] input:focus-visible,
    select:focus, [data-baseweb="select"]:focus-within {
        outline: none !important;
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 1px var(--accent-primary), 0 0 0 3px rgba(169, 120, 244, 0.12) !important;
    }
    .stButton > button:focus, .stButton > button:focus-visible {
        box-shadow: 0 4px 20px rgba(212, 171, 254, 0.3), 0 0 0 2px rgba(169, 120, 244, 0.2) !important;
    }
    [data-testid="stProgress"] > div,
    [data-testid="stProgress"] [role="progressbar"],
    div[data-testid="stProgress"] > div > div,
    [data-testid="stProgress"] div[style*="width"] {
        background: var(--accent-primary) !important;
        background-color: var(--accent-primary) !important;
    }
    [data-testid="stProgress"] {
        background: var(--deep-plum) !important;
        border-radius: var(--radius-sm) !important;
    }
    [data-testid="stFileUploader"] [role="progressbar"],
    [data-testid="stFileUploader"] progress,
    [data-testid="stFileUploader"] [data-testid="stProgress"] > div > div,
    [data-testid="stFileUploader"] [data-testid="stProgress"] div[style*="width"] {
        background: var(--accent-secondary) !important;
        background-color: var(--accent-secondary) !important;
    }
    [data-testid="stFileUploader"] [data-testid="stProgress"],
    [data-testid="stFileUploader"] [data-testid="stProgress"] > div {
        background: var(--deep-plum) !important;
    }
    /* Remove every remaining red/coral accent leak — Datara only */
    *:focus-visible { outline-color: var(--accent-primary) !important; }
    [data-baseweb] *:focus, [data-baseweb] *:focus-visible {
        outline: none !important;
        box-shadow: 0 0 0 2px var(--accent-primary) !important;
    }
    [data-baseweb="slider"] path[fill],
    [data-baseweb="slider"] [role="slider"] {
        fill: var(--accent-primary) !important;
        background: var(--accent-primary) !important;
    }
    [data-baseweb="checkbox"] [role="checkbox"] {
        border-color: var(--border-medium) !important;
        background: var(--bg-panel) !important;
    }
    [data-baseweb="checkbox"] [role="checkbox"][aria-checked="true"] {
        background: var(--accent-primary) !important;
        border-color: var(--accent-primary) !important;
    }
    /* Plotly container — no red from toolbar/controls */
    .js-plotly-plot .modebar .modebar-group a path { fill: var(--text-muted) !important; }
    .js-plotly-plot .modebar .modebar-group a:hover path { fill: var(--accent-primary) !important; }

    [data-testid="stAppViewContainer"] {
        background: var(--bg-base) !important;
        background-image: radial-gradient(ellipse at 50% 30%, var(--deep-plum) 0%, var(--bg-base) 70%) !important;
    }
    .block-container { max-width: 1200px; padding: 48px 32px 64px; }
    .stApp, .stApp .main { background: transparent !important; }
    .stApp .main .block-container { color: var(--text-secondary); font-family: var(--font-sans); }

    .stApp h1 {
        font-family: var(--font-sans); font-size: 28px !important; font-weight: 600 !important;
        color: var(--text-primary) !important; letter-spacing: -0.5px; margin-bottom: 8px !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }
    .stApp [data-testid="stMarkdown"] p { color: var(--text-secondary) !important; font-size: 15px; }
    .stApp .stCaption { color: var(--text-muted) !important; font-size: 13px !important; }
    .stApp h2, .stApp h3 {
        font-family: var(--font-sans); font-size: 15px !important; font-weight: 500 !important;
        color: var(--text-secondary) !important;
    }

    /* Upload zone — panel, subtle hover only (no harsh border/outline) */
    [data-testid="stFileUploader"] { margin: 0.5rem 0 !important; }
    [data-testid="stFileUploader"] section {
        background: var(--bg-panel) !important;
        border: 1px solid var(--border-dim) !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3) !important;
        border-radius: var(--radius-lg) !important;
        padding: 32px !important;
        transition: background 0.2s ease, box-shadow 0.2s ease !important;
    }
    [data-testid="stFileUploader"] section:hover {
        background: rgba(255, 255, 255, 0.02) !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.25), 0 0 0 1px rgba(212, 171, 254, 0.06) !important;
    }
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] {
        font-size: 15px !important; font-weight: 500 !important; color: var(--text-primary) !important;
    }
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] + span {
        font-size: 13px !important; color: var(--text-muted) !important;
    }

    /* KPI cards — design: 24px padding, 32px value, 14px label; support metric-container and stMetric */
    [data-testid="stMetric"],
    [data-testid="metric-container"] {
        background: var(--bg-panel) !important;
        border: 1px solid var(--border-dim) !important;
        box-shadow: inset 0 1px 2px rgba(255,255,255,0.05) !important;
        border-radius: var(--radius-lg) !important;
        padding: 24px !important;
        gap: 12px;
    }
    [data-testid="stMetric"] label,
    [data-testid="stMetricLabel"],
    [data-testid="metric-container"] label {
        font-size: 14px !important; font-weight: 500 !important;
        color: var(--text-muted) !important;
        display: block !important;
    }
    [data-testid="stMetricValue"] {
        font-family: var(--font-sans) !important;
        font-size: 32px !important; font-weight: 700 !important;
        color: var(--text-primary) !important;
        letter-spacing: -1px;
    }
    /* Missing Values (3rd KPI) — accent in design */
    [data-testid="stMetric"]:nth-of-type(3) [data-testid="stMetricValue"],
    [data-testid="metric-container"]:nth-of-type(3) [data-testid="stMetricValue"] {
        color: var(--accent-primary) !important;
    }

    /* Primary button — Datara accent, dark text, no red focus */
    .stButton > button {
        font-family: var(--font-sans) !important;
        background: var(--accent-primary) !important;
        color: #161121 !important;
        border: none !important;
        border-radius: 999px !important;
        font-size: 15px !important; font-weight: 600 !important;
        padding: 16px !important;
        width: 100%; max-width: 360px;
        box-shadow: 0 4px 20px rgba(169, 120, 244, 0.28) !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 25px rgba(169, 120, 244, 0.35) !important;
    }

    /* Expander — Datara: same panel language, subtle border */
    .stExpander {
        background: transparent !important;
        border: none !important;
        margin: 8px 0 !important;
    }
    .streamlit-expanderHeader {
        background: transparent !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: var(--text-muted) !important;
        padding: 12px 0 !important;
        font-family: var(--font-sans) !important;
    }
    .streamlit-expanderContent {
        border-top: 1px solid var(--border-dim) !important;
        color: var(--text-secondary) !important;
        font-size: 14px !important;
        padding: 12px 0 4px 0 !important;
        font-family: var(--font-sans) !important;
    }
    .streamlit-expanderContent [data-testid="stMarkdown"] { margin-bottom: 0.5em !important; }

    /* Tabs — Datara: minimal underline, muted inactive, bright active, premium rhythm */
    [data-testid="stTabs"] { margin-top: 24px; }
    [data-testid="stTabs"] [role="tablist"] {
        border-bottom: 1px solid var(--border-dim) !important;
        gap: 28px !important;
        padding-bottom: 0 !important;
        min-height: 44px !important;
        align-items: flex-end !important;
    }
    [data-testid="stTabs"] [role="tab"] {
        font-family: var(--font-sans) !important;
        padding: 10px 0 14px 0 !important;
        color: var(--text-muted) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        letter-spacing: 0.01em !important;
        background: none !important;
        border: none !important;
        border-radius: 0 !important;
        border-bottom: 2px solid transparent !important;
        margin-bottom: -1px !important;
        transition: color 0.2s ease, border-color 0.2s ease !important;
    }
    [data-testid="stTabs"] [role="tab"]:hover {
        color: var(--text-secondary) !important;
    }
    /* Active tab: Datara accent only — no default red/coral */
    [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background: var(--accent-primary) !important;
        background-color: var(--accent-primary) !important;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: var(--text-primary) !important;
        border-bottom: 2px solid var(--accent-primary) !important;
        border-bottom-color: var(--accent-primary) !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"]::before,
    [data-testid="stTabs"] [role="tab"][aria-selected="true"]::after {
        display: none !important;
        background: transparent !important;
        border: none !important;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] span,
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] div {
        color: var(--text-primary) !important;
    }

    /* Table / dataframe — Datara: dark premium surface, header, rows, separators */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border-medium) !important;
        border-radius: var(--radius-lg) !important;
        background: var(--bg-panel) !important;
        overflow: hidden !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.2) !important;
    }
    [data-testid="stDataFrame"] table {
        width: 100% !important;
        border-collapse: collapse !important;
        font-family: var(--font-sans) !important;
    }
    [data-testid="stDataFrame"] thead tr {
        background: var(--bg-surface) !important;
        border-bottom: 1px solid var(--border-medium) !important;
    }
    [data-testid="stDataFrame"] thead th {
        color: var(--text-muted) !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        padding: 12px 16px !important;
        text-align: left !important;
        border: none !important;
    }
    [data-testid="stDataFrame"] tbody tr {
        border-bottom: 1px solid var(--border-dim) !important;
        transition: background 0.15s ease !important;
    }
    [data-testid="stDataFrame"] tbody tr:hover {
        background: rgba(245, 240, 255, 0.04) !important;
    }
    [data-testid="stDataFrame"] tbody tr:nth-child(even) {
        background: rgba(0, 0, 0, 0.08) !important;
    }
    [data-testid="stDataFrame"] tbody tr:nth-child(even):hover {
        background: rgba(245, 240, 255, 0.05) !important;
    }
    [data-testid="stDataFrame"] tbody td {
        color: var(--text-secondary) !important;
        font-size: 14px !important;
        padding: 10px 16px !important;
        border: none !important;
    }

    /* Chart container — Datara panel so chart sits in same design system */
    [data-testid="stPlotlyChart"] {
        background: var(--bg-panel) !important;
        border: 1px solid var(--border-dim) !important;
        border-radius: var(--radius-lg) !important;
        padding: 20px !important;
        overflow: hidden !important;
        box-shadow: inset 0 1px 2px rgba(255,255,255,0.02) !important;
    }
    [data-testid="stPlotlyChart"] > div {
        border-radius: var(--radius-md) !important;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        background: var(--bg-panel) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: var(--radius-lg) !important;
    }
    [data-testid="stAlert"] [data-testid="stMarkdown"] { color: var(--text-secondary) !important; }

    /* Ask AI section — divider and heading (clean spacing) */
    .datara-ask-ai-divider {
        margin: 32px 0 0 0 !important;
        padding: 0 !important;
        border: none !important;
        border-top: 1px solid var(--border-dim) !important;
    }
    .stApp h2 { font-family: var(--font-sans) !important; font-size: 18px !important; font-weight: 600 !important; color: var(--text-primary) !important; }

    /* Ask AI — suggested questions label (muted, no highlight) */
    .datara-ask-ai-suggested-label {
        font-size: 13px !important;
        color: var(--text-muted) !important;
        margin: 0 0 10px 0 !important;
        font-weight: 400 !important;
    }
    /* Ask AI — suggested chips: very muted, calm, secondary (no loud fill) */
    .block-container [data-testid="column"] { min-width: 0 !important; }
    .block-container > *:has(.datara-ask-ai-suggested-label) + * .stButton > button {
        font-family: var(--font-sans) !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        color: var(--text-muted) !important;
        background: rgba(80, 60, 100, 0.18) !important;
        border: 1px solid rgba(212, 171, 254, 0.08) !important;
        border-radius: var(--radius-lg) !important;
        padding: 8px 12px !important;
        box-shadow: none !important;
        white-space: normal !important;
        overflow-wrap: break-word !important;
        word-wrap: break-word !important;
        max-width: 100% !important;
        text-align: left !important;
    }
    .block-container > *:has(.datara-ask-ai-suggested-label) + * .stButton > button:hover {
        background: rgba(80, 60, 100, 0.25) !important;
        border-color: rgba(212, 171, 254, 0.12) !important;
    }

    /* Ask AI — response panel (full width, column layout, normal paragraphs, internal scroll) */
    .datara-ask-ai-response {
        display: block !important;
        width: 100% !important;
        max-width: 100% !important;
        margin-bottom: 16px !important;
        background: var(--bg-panel) !important;
        border: 1px solid var(--border-dim) !important;
        border-radius: var(--radius-lg) !important;
        overflow: hidden !important;
    }
    .datara-ask-ai-response-body {
        display: block !important;
        width: 100% !important;
        max-width: none !important;
        max-height: 50vh !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
        color: var(--text-secondary) !important;
        padding: 20px 24px !important;
        box-sizing: border-box !important;
    }
    .datara-ask-ai-response-body br { margin: 0.4em 0 !important; }

    /* Ask AI — chat input: full width, floating, Datara theme; send button = accent, NO red */
    [data-testid="stChatInput"] {
        background: var(--bg-panel) !important;
        border: 1px solid var(--border-dim) !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.2) !important;
        border-radius: 999px !important;
        padding: 12px 20px 12px 24px !important;
        margin-top: 16px !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: var(--border-medium) !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.2), 0 0 0 1px var(--border-medium) !important;
    }
    [data-testid="stChatInput"] textarea {
        color: var(--text-primary) !important;
        font-size: 15px !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: var(--text-muted) !important;
    }
    [data-testid="stChatInput"] button,
    [data-testid="stChatInput"] [data-testid="stChatInputSubmitButton"] {
        background: var(--accent-primary) !important;
        color: #161121 !important;
        border: none !important;
    }
    [data-testid="stChatInput"] button:hover,
    [data-testid="stChatInput"] [data-testid="stChatInputSubmitButton"]:hover {
        background: var(--accent-secondary) !important;
        color: #161121 !important;
    }

    /* Ask AI — message icons: Datara plum/lilac only (no red/warm/alert) */
    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"],
    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] > div,
    [data-testid="stChatMessage"] > div > div:first-child,
    [data-testid="stChatMessage"] > div > div:first-child > div {
        background: #1e1829 !important;
        background-color: #1e1829 !important;
        border: 1px solid rgba(212, 171, 254, 0.1) !important;
        border-radius: var(--radius-sm) !important;
        color: #8b7a9e !important;
        box-shadow: none !important;
    }
    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] *,
    [data-testid="stChatMessage"] > div > div:first-child * {
        color: #8b7a9e !important;
    }
    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] img,
    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] svg,
    [data-testid="stChatMessage"] > div > div:first-child img,
    [data-testid="stChatMessage"] > div > div:first-child svg {
        filter: brightness(1.15) saturate(0.4) hue-rotate(260deg) !important;
    }
    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] path,
    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] circle,
    [data-testid="stChatMessage"] > div > div:first-child path,
    [data-testid="stChatMessage"] > div > div:first-child circle {
        fill: #8b7a9e !important;
        stroke: #8b7a9e !important;
    }

    /* Tab-inner buttons — pill secondary */
    [data-testid="stTabs"] .stButton > button {
        max-width: none; width: auto;
        font-size: 12px !important; padding: 10px 16px !important;
        background: var(--bg-panel) !important;
        color: var(--text-muted) !important;
        border: 1px solid var(--border-dim) !important;
        border-radius: 999px !important;
        box-shadow: none !important;
        transform: none !important;
    }
    [data-testid="stTabs"] .stButton > button:hover {
        border-color: var(--accent-primary) !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stDownloadButton"] button {
        background: rgba(245, 240, 255, 0.08) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: 999px !important;
        font-size: 13px !important;
    }
    [data-testid="stDownloadButton"] button:hover {
        background: rgba(245, 240, 255, 0.15) !important;
        border-color: var(--border-bright) !important;
    }

    /* Global readability — content panels and long-form text */
    .datara-content-panel {
        font-family: var(--font-sans);
        background: var(--bg-panel);
        border: 1px solid var(--border-dim);
        border-radius: var(--radius-lg);
        padding: 22px 26px;
        margin-bottom: 20px;
        max-width: 72ch;
        box-shadow: inset 0 1px 2px rgba(255,255,255,0.03);
    }
    .datara-content-panel .datara-panel-title {
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
        margin-bottom: 12px;
    }
    .datara-content-panel .datara-panel-body {
        font-size: 15px;
        line-height: 1.6;
        color: var(--text-secondary);
    }
    .datara-content-panel .datara-panel-body br { margin: 0.4em 0; }
    .datara-explanation-box {
        font-family: var(--font-sans);
        background: var(--bg-panel);
        border: 1px solid var(--border-dim);
        border-radius: var(--radius-md);
        padding: 14px 18px;
        margin-top: 12px;
        font-size: 14px;
        line-height: 1.55;
        color: var(--text-secondary);
    }
    /* Findings — proper spacing rhythm, breathable and polished */
    .datara-finding-card {
        font-family: var(--font-sans);
        background: var(--bg-panel);
        border: 1px solid var(--border-dim);
        border-radius: var(--radius-lg);
        padding: 30px 34px;
        margin-bottom: 32px;
        box-shadow: inset 0 1px 2px rgba(255,255,255,0.03);
    }
    .datara-finding-card:first-of-type { margin-top: 24px; }
    .datara-finding-card:last-child { margin-bottom: 0; }
    .datara-finding-label {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-muted);
        margin-bottom: 18px;
        padding-bottom: 18px;
        border-bottom: 1px solid var(--border-dim);
    }
    .datara-finding-label .datara-finding-icon {
        flex-shrink: 0;
        width: 18px;
        height: 18px;
        opacity: 0.9;
        color: var(--text-muted);
    }
    .datara-finding-label .datara-finding-icon svg {
        width: 100%;
        height: 100%;
    }
    .datara-finding-value {
        font-size: 15px;
        line-height: 1.58;
        color: var(--text-secondary);
        margin-top: 8px;
    }
    .datara-finding-value br { margin: 0.5em 0; }

    /* Tab content — consistent vertical rhythm */
    [data-testid="stTabs"] [data-testid="stVerticalBlock"] {
        padding-top: 20px !important;
    }
    [data-testid="stTabs"] [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        margin-top: 16px !important;
    }

    /* In-theme upload prompt — matches panel/cards, no default Streamlit info look */
    .datara-upload-prompt {
        font-family: var(--font-sans);
        font-size: 14px;
        color: var(--text-muted);
        background: var(--bg-panel);
        border: 1px solid var(--border-dim);
        border-radius: var(--radius-lg);
        padding: 20px 24px;
        margin: 16px 0 0 0;
        box-shadow: inset 0 1px 2px rgba(255,255,255,0.03);
    }

    /* Light theme — full app restyle, premium soft surfaces */
    body.datara-theme-light {
        --bg-base: #f5f3f8;
        --bg-panel: #ffffff;
        --bg-surface: #ebe8f2;
        --text-primary: #1a1525;
        --text-secondary: #4a4358;
        --text-muted: #6e6580;
        --border-dim: rgba(126, 90, 182, 0.18);
        --border-medium: rgba(126, 90, 182, 0.28);
        --border-bright: rgba(126, 90, 182, 0.4);
        --deep-plum: #e5e0ef;
    }
    body.datara-theme-light [data-testid="stAppViewContainer"] {
        background: #f5f3f8 !important;
        background-image: radial-gradient(ellipse at 50% 30%, #e5e0ef 0%, #f5f3f8 70%) !important;
    }
    body.datara-theme-light .stApp .main .block-container,
    body.datara-theme-light [data-testid="stMarkdown"] p { color: #4a4358 !important; }
    body.datara-theme-light .stApp h1 { color: #1a1525 !important; text-shadow: none !important; }
    body.datara-theme-light .stApp .stCaption { color: #6e6580 !important; }
    body.datara-theme-light .stApp h2, body.datara-theme-light .stApp h3 { color: #1a1525 !important; }
    body.datara-theme-light [data-testid="stFileUploader"] section {
        background: #ffffff !important;
        border-color: rgba(126, 90, 182, 0.2) !important;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.04) !important;
    }
    body.datara-theme-light [data-testid="stFileUploader"] section:hover {
        background: #faf9fc !important;
        border-color: rgba(126, 90, 182, 0.28) !important;
    }
    body.datara-theme-light .datara-upload-prompt {
        background: #ffffff !important;
        border-color: rgba(126, 90, 182, 0.2) !important;
        color: #6e6580 !important;
    }
    body.datara-theme-light [data-testid="stMetric"] [data-testid="stMetricValue"],
    body.datara-theme-light [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #1a1525 !important; }
    body.datara-theme-light [data-testid="stMetric"] label { color: #6e6580 !important; }
    body.datara-theme-light .stButton > button {
        background: var(--accent-primary) !important;
        color: #161121 !important;
        box-shadow: 0 2px 12px rgba(169, 120, 244, 0.25) !important;
    }
    body.datara-theme-light .datara-content-panel,
    body.datara-theme-light .datara-explanation-box {
        background: #ffffff !important;
        border-color: rgba(126, 90, 182, 0.2) !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    }
    body.datara-theme-light .datara-content-panel .datara-panel-title,
    body.datara-theme-light .datara-finding-label { color: #6e6580 !important; }
    body.datara-theme-light .datara-content-panel .datara-panel-body,
    body.datara-theme-light .datara-finding-value { color: #4a4358 !important; }
    body.datara-theme-light .datara-finding-card {
        background: #ffffff !important;
        border-color: rgba(126, 90, 182, 0.2) !important;
    }
    body.datara-theme-light [data-testid="stTabs"] .stButton > button {
        background: #ffffff !important;
        color: #6e6580 !important;
        border-color: rgba(126, 90, 182, 0.2) !important;
    }
    body.datara-theme-light [data-testid="stTabs"] .stButton > button:hover {
        border-color: var(--accent-primary) !important;
        color: #1a1525 !important;
    }
    body.datara-theme-light .datara-ask-ai-response,
    body.datara-theme-light [data-testid="stChatMessage"] {
        background: #ffffff !important;
        border-color: rgba(126, 90, 182, 0.2) !important;
    }
    body.datara-theme-light .datara-ask-ai-response-body { color: #4a4358 !important; }
    body.datara-theme-light [data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"],
    body.datara-theme-light [data-testid="stChatMessage"] > div > div:first-child {
        background: #ebe8f2 !important;
        border-color: rgba(126, 90, 182, 0.2) !important;
        color: #6e6580 !important;
    }
    body.datara-theme-light [data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] path,
    body.datara-theme-light [data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] circle,
    body.datara-theme-light [data-testid="stChatMessage"] > div > div:first-child path,
    body.datara-theme-light [data-testid="stChatMessage"] > div > div:first-child circle {
        fill: #6e6580 !important;
        stroke: #6e6580 !important;
    }
    body.datara-theme-light [data-testid="stChatInput"] {
        background: #ffffff !important;
        border-color: rgba(126, 90, 182, 0.25) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    }
    body.datara-theme-light [data-testid="stChatInput"] textarea { color: #1a1525 !important; }
    body.datara-theme-light .block-container > *:has(.datara-ask-ai-suggested-label) + * .stButton > button {
        background: rgba(126, 90, 182, 0.12) !important;
        color: #6e6580 !important;
        border-color: rgba(126, 90, 182, 0.2) !important;
    }
    body.datara-theme-light .block-container > *:has(.datara-ask-ai-suggested-label) + * .stButton > button:hover {
        background: rgba(126, 90, 182, 0.18) !important;
        border-color: rgba(126, 90, 182, 0.3) !important;
    }
    body.datara-theme-light .datara-header-brand { color: #1a1525 !important; }
    /* Header segment controls in light mode */
    body.datara-theme-light #datara-header-lang + * [data-testid="stHorizontalBlock"],
    body.datara-theme-light #datara-header-lang ~ * [data-testid="stHorizontalBlock"],
    body.datara-theme-light #datara-header-theme + * [data-testid="stHorizontalBlock"],
    body.datara-theme-light #datara-header-theme ~ * [data-testid="stHorizontalBlock"] {
        background: #f5f3f8 !important; border-color: rgba(126, 90, 182, 0.2) !important;
    }
    body.datara-theme-light #datara-header-lang + * [data-testid="stHorizontalBlock"] [data-testid="column"] button,
    body.datara-theme-light #datara-header-lang ~ * [data-testid="stHorizontalBlock"] [data-testid="column"] button,
    body.datara-theme-light #datara-header-theme + * [data-testid="stHorizontalBlock"] [data-testid="column"] button,
    body.datara-theme-light #datara-header-theme ~ * [data-testid="stHorizontalBlock"] [data-testid="column"] button {
        color: #6e6580 !important;
    }
    body.datara-theme-light:not(.datara-lang-ar) #datara-header-lang ~ * [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button,
    body.datara-theme-light.datara-lang-ar #datara-header-lang ~ * [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button,
    body.datara-theme-light #datara-header-theme ~ * [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button {
        color: #161121 !important;
    }
    body.datara-theme-light .streamlit-expanderHeader,
    body.datara-theme-light [data-testid="stExpander"] summary { color: #4a4358 !important; }
    body.datara-theme-light [data-testid="stAlert"] { background: #faf9fc !important; border-color: rgba(126, 90, 182, 0.25) !important; }

    /* RTL + Noto Sans Arabic for Arabic */
    body.datara-lang-ar [data-testid="stAppViewContainer"],
    body.datara-lang-ar .block-container,
    body.datara-lang-ar .stApp,
    body.datara-lang-ar [data-testid="stMarkdown"],
    body.datara-lang-ar .stCaption,
    body.datara-lang-ar h1, body.datara-lang-ar h2, body.datara-lang-ar h3,
    body.datara-lang-ar .datara-header-brand,
    body.datara-lang-ar .stButton button,
    body.datara-lang-ar .datara-content-panel,
    body.datara-lang-ar .datara-finding-card,
    body.datara-lang-ar .datara-ask-ai-response-body {
        font-family: "Noto Sans Arabic", var(--font-sans) !important;
    }
    body.datara-lang-ar [data-testid="stAppViewContainer"],
    body.datara-lang-ar .block-container {
        direction: rtl;
        text-align: right;
    }
    body.datara-lang-ar .block-container [data-testid="column"] {
        direction: rtl;
    }

    </style>
    <script>
    document.body.addEventListener("click", function(e) {
        var btn = e.target.closest(".datara-copy-btn");
        if (btn && btn.getAttribute("data-copy") !== null) {
            var text = btn.getAttribute("data-copy");
            try {
                navigator.clipboard.writeText(text);
                btn.textContent = "Copied!";
                setTimeout(function() { btn.textContent = "Copy"; }, 1400);
            } catch (err) {}
        }
    });
    </script>
    """, unsafe_allow_html=True)


# -----------------------------
# Render
# -----------------------------
apply_css()

# Theme + language: inject config and run script immediately + on load (so light mode applies)
_theme = st.session_state.get("theme", "dark")
_lang = st.session_state.get("lang", "en")
st.markdown(
    f'<div id="datara-config" data-theme="{_theme}" data-lang="{_lang}"></div>'
    r'<script>(function(){var run=function(){var c=document.getElementById("datara-config");if(c){var t=c.getAttribute("data-theme"),l=c.getAttribute("data-lang");'
    r'document.body.classList.toggle("datara-theme-light",t==="light");document.body.classList.toggle("datara-lang-ar",l==="ar");}};'
    r'run();document.addEventListener("DOMContentLoaded",run);})();</script>',
    unsafe_allow_html=True,
)

# Header: brand | custom language switcher | custom theme switcher (no Streamlit radio)
_h1, _h2, _h3 = st.columns([2, 1, 1])
with _h1:
    st.markdown('<span class="datara-header-brand">Datara</span>', unsafe_allow_html=True)
with _h2:
    st.markdown('<div id="datara-header-lang" class="datara-seg-marker"></div>', unsafe_allow_html=True)
    _la, _lb = st.columns(2)
    with _la:
        if st.button(t("lang_en"), key="btn_lang_en"):
            st.session_state.lang = "en"
            st.rerun()
    with _lb:
        if st.button(t("lang_ar"), key="btn_lang_ar"):
            st.session_state.lang = "ar"
            st.rerun()
with _h3:
    st.markdown('<div id="datara-header-theme" class="datara-seg-marker"></div>', unsafe_allow_html=True)
    _ta, _tb = st.columns(2)
    with _ta:
        if st.button(t("theme_dark"), key="btn_theme_dark"):
            st.session_state.theme = "dark"
            st.rerun()
    with _tb:
        if st.button(t("theme_light"), key="btn_theme_light"):
            st.session_state.theme = "light"
            st.rerun()

# Custom segmented control CSS: pill container + active state from body class (no Streamlit radio)
st.markdown("""
<style>
.datara-header-brand { font-family: var(--font-sans); font-size: 18px; font-weight: 600; color: var(--text-primary); }
.datara-seg-marker { display: none !important; }
/* Lang segment: container = one pill */
/* Lang segment: pill container (next sibling or descendant of next sibling) */
#datara-header-lang + * [data-testid="stHorizontalBlock"],
#datara-header-lang ~ * [data-testid="stHorizontalBlock"] {
    display: inline-flex !important; gap: 0 !important;
    background: var(--bg-panel) !important; border: 1px solid var(--border-dim) !important;
    border-radius: 999px !important; padding: 3px !important;
}
#datara-header-lang + * [data-testid="stHorizontalBlock"] [data-testid="column"],
#datara-header-lang ~ * [data-testid="stHorizontalBlock"] [data-testid="column"] { min-width: 0 !important; flex: 1 1 0 !important; }
#datara-header-lang + * [data-testid="stHorizontalBlock"] [data-testid="column"] .stButton,
#datara-header-lang ~ * [data-testid="stHorizontalBlock"] [data-testid="column"] .stButton { width: 100% !important; }
#datara-header-lang + * [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button,
#datara-header-lang ~ * [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button {
    border-radius: 999px 0 0 999px !important; border: none !important;
    background: transparent !important; color: var(--text-muted) !important;
    font-size: 12px !important; font-weight: 500 !important; padding: 6px 14px !important;
    box-shadow: none !important; width: 100% !important;
}
#datara-header-lang + * [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button,
#datara-header-lang ~ * [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button {
    border-radius: 0 999px 999px 0 !important; border: none !important;
    background: transparent !important; color: var(--text-muted) !important;
    font-size: 12px !important; font-weight: 500 !important; padding: 6px 14px !important;
    box-shadow: none !important; width: 100% !important;
}
body:not(.datara-lang-ar) #datara-header-lang + * [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button,
body:not(.datara-lang-ar) #datara-header-lang ~ * [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button {
    background: var(--accent-primary) !important; color: #161121 !important;
}
body.datara-lang-ar #datara-header-lang + * [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button,
body.datara-lang-ar #datara-header-lang ~ * [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button {
    background: var(--accent-primary) !important; color: #161121 !important;
}
/* Theme segment */
#datara-header-theme + * [data-testid="stHorizontalBlock"],
#datara-header-theme ~ * [data-testid="stHorizontalBlock"] {
    display: inline-flex !important; gap: 0 !important;
    background: var(--bg-panel) !important; border: 1px solid var(--border-dim) !important;
    border-radius: 999px !important; padding: 3px !important; margin-left: 8px !important;
}
#datara-header-theme + * [data-testid="stHorizontalBlock"] [data-testid="column"],
#datara-header-theme ~ * [data-testid="stHorizontalBlock"] [data-testid="column"] { min-width: 0 !important; flex: 1 1 0 !important; }
#datara-header-theme + * [data-testid="stHorizontalBlock"] [data-testid="column"] .stButton,
#datara-header-theme ~ * [data-testid="stHorizontalBlock"] [data-testid="column"] .stButton { width: 100% !important; }
#datara-header-theme + * [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button,
#datara-header-theme + * [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button,
#datara-header-theme ~ * [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button,
#datara-header-theme ~ * [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button {
    border: none !important; background: transparent !important; color: var(--text-muted) !important;
    font-size: 12px !important; font-weight: 500 !important; padding: 6px 14px !important;
    box-shadow: none !important; width: 100% !important;
}
#datara-header-theme + * [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button,
#datara-header-theme ~ * [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button { border-radius: 999px 0 0 999px !important; }
#datara-header-theme + * [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button,
#datara-header-theme ~ * [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button { border-radius: 0 999px 999px 0 !important; }
body:not(.datara-theme-light) #datara-header-theme + * [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button,
body:not(.datara-theme-light) #datara-header-theme ~ * [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button {
    background: var(--accent-primary) !important; color: #161121 !important;
}
body.datara-theme-light #datara-header-theme + * [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button,
body.datara-theme-light #datara-header-theme ~ * [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button {
    background: var(--accent-primary) !important; color: #161121 !important;
}
</style>
""", unsafe_allow_html=True)

# 1. Hero (translated)
st.title(t("hero_title"))
st.caption(t("hero_subtitle"))

# 2. Upload zone
uploaded_file = st.file_uploader(
    t("drag_drop") + " — " + t("browse_files"),
    type=["csv", "xlsx"],
    key="main_uploader",
)

if uploaded_file is None:
    if st.session_state.last_uploaded_name is not None:
        reset_app_state()
    st.markdown(
        f'<p class="datara-upload-prompt">{html.escape(t("hero_subtitle"))}</p>',
        unsafe_allow_html=True,
    )
    st.stop()

if st.session_state.last_uploaded_name != uploaded_file.name:
    st.session_state.analysis_result = None
    st.session_state.chat_history = []
    st.session_state.last_uploaded_name = uploaded_file.name
    st.session_state.suggested_questions = None
    st.session_state.chart_explanations = {}
    st.session_state.data_formulas_result = None

try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(str(e))
    st.stop()

profile = profile_dataframe(df)
size_mb = file_size_mb(uploaded_file)
n_rows, n_cols = df.shape
result = st.session_state.analysis_result

# File row + metadata
st.write("**File:**", uploaded_file.name, "·", f"{size_mb:.2f} MB", "·", infer_data_types(df))
if profile.get("readiness_summary"):
    st.caption(profile["readiness_summary"])

# Generate file-aware suggested questions once per file (when None)
if st.session_state.suggested_questions is None:
    with st.spinner("Preparing suggested questions..."):
        st.session_state.suggested_questions = ask_agent_suggested_questions(df, profile)
    st.rerun()

# 3. KPI Strip (translated)
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric(t("total_rows"), f"{n_rows:,}")
with k2:
    st.metric(t("total_columns"), n_cols)
with k3:
    st.metric("Missing Values", profile["missing_total"])
with k4:
    st.metric("Duplicates", profile["duplicate_rows"])
with k5:
    st.metric("Readiness %", f"{profile['readiness_pct']}%")

# Generate summary + readiness expander
if st.button(t("generate_cta"), key="cta_gen"):
    with st.spinner("Analyzing..."):
        st.session_state.analysis_result = ask_agent_for_analysis(df, profile)
    st.rerun()
if profile.get("readiness_factors"):
    with st.expander("What affects the readiness score?"):
        for f in profile["readiness_factors"]:
            st.write("-", str(f) if f is not None else "—")

# 4. Main Tabbed Workspace (translated labels)
tab_overview, tab_health, tab_findings, tab_charts = st.tabs([
    t("tab_overview"),
    t("tab_health"),
    t("tab_findings"),
    t("tab_charts"),
])

with tab_overview:
    # Short dataset summary — in a readable content panel
    rep = (result.get("summary", {}) if result else {}) or {}
    overview_text = (rep.get("overview") or "").strip() if result else ""
    if not overview_text:
        overview_text = f"Dataset has {n_rows:,} rows and {n_cols} columns. Generate summary above for an AI overview."
    safe_overview = html.escape(overview_text).replace("\n", "<br>")
    st.markdown(
        f'<div class="datara-content-panel">'
        f'<div class="datara-panel-title">Summary</div>'
        f'<div class="datara-panel-body">{safe_overview}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    # Key insights (if present)
    key_insights = rep.get("key_insights") or []
    if key_insights:
        lines = "".join(f"<br>• {html.escape(str(x))}" for x in key_insights[:10])
        st.markdown(
            f'<div class="datara-content-panel">'
            f'<div class="datara-panel-title">Key insights</div>'
            f'<div class="datara-panel-body">{lines}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    # Recommendations (if present)
    recs_list = rep.get("recommendations") or []
    if recs_list:
        lines = "".join(f"<br>• {html.escape(str(x))}" for x in recs_list[:10])
        st.markdown(
            f'<div class="datara-content-panel">'
            f'<div class="datara-panel-title">Recommendations</div>'
            f'<div class="datara-panel-body">{lines}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    # Detected column types
    ctypes = profile.get("column_types") or {}
    if ctypes:
        num = [c for c, typ in ctypes.items() if typ == "numeric"]
        cat = [c for c, typ in ctypes.items() if typ == "categorical"]
        dt = [c for c, typ in ctypes.items() if typ == "datetime"]
        if num:
            st.caption("**Numeric (measures):** " + ", ".join(num[:15]) + (" …" if len(num) > 15 else ""))
        if cat:
            st.caption("**Categorical (groups):** " + ", ".join(cat[:15]) + (" …" if len(cat) > 15 else ""))
        if dt:
            st.caption("**Datetime:** " + ", ".join(dt))
    # Recommended measures / groups
    meas = profile.get("recommended_measure_columns") or []
    grp = profile.get("recommended_grouping_columns") or []
    if meas or grp:
        st.caption("**Recommended measures:** " + (", ".join(meas[:10]) if meas else "—") + " · **Recommended groups:** " + (", ".join(grp[:10]) if grp else "—"))
    st.caption("Data preview")
    st.dataframe(df.head(200), height=280, use_container_width=True)
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
    total_cells = (profile.get("total_rows") or 0) * max(len(profile.get("column_types") or {}), 1)
    missing_pct = (100 * profile["missing_total"] / total_cells) if total_cells else 0
    parts = []
    parts.append(f'<div class="datara-content-panel">')
    parts.append(f'<div class="datara-panel-title">Missing values</div>')
    parts.append(f'<div class="datara-panel-body">{profile["missing_total"]} cells ({missing_pct:.1f}% of all cells)</div>')
    parts.append(f'</div>')
    parts.append(f'<div class="datara-content-panel">')
    parts.append(f'<div class="datara-panel-title">Duplicate rows</div>')
    parts.append(f'<div class="datara-panel-body">{profile["duplicate_rows"]}</div>')
    parts.append(f'</div>')
    if profile.get("high_null_columns"):
        lines = "".join(f"<br>• {html.escape(col)}: {pct}% null" for col, pct in profile["high_null_columns"][:10])
        parts.append(f'<div class="datara-content-panel">')
        parts.append(f'<div class="datara-panel-title">Columns with highest null %</div>')
        parts.append(f'<div class="datara-panel-body">{lines}</div>')
        parts.append(f'</div>')
    if profile.get("text_heavy_columns"):
        txt = html.escape(", ".join(profile["text_heavy_columns"][:8]))
        parts.append(f'<div class="datara-content-panel"><div class="datara-panel-title">Text-heavy columns</div><div class="datara-panel-body">{txt}</div></div>')
    if profile.get("id_like_columns"):
        txt = html.escape(", ".join(profile["id_like_columns"][:8]))
        parts.append(f'<div class="datara-content-panel"><div class="datara-panel-title">ID-like columns</div><div class="datara-panel-body">{txt}</div></div>')
    recs = profile.get("quality_recommendations") or []
    if recs:
        lines = "".join(f"<br>• {html.escape(str(r))}" for r in recs)
        parts.append(f'<div class="datara-content-panel">')
        parts.append(f'<div class="datara-panel-title">Cleanup recommendations</div>')
        parts.append(f'<div class="datara-panel-body">{lines}</div>')
        parts.append(f'</div>')
    if not recs and profile["missing_total"] == 0 and profile["duplicate_rows"] == 0:
        parts.append(f'<div class="datara-content-panel"><div class="datara-panel-body">No major data health issues detected.</div></div>')
    st.markdown("".join(parts), unsafe_allow_html=True)

    # Ready-to-paste formulas (Excel, Google Sheets, pandas)
    st.markdown("---")
    st.caption("**Ready-to-paste formulas** — Get copy-paste formulas for common data fixes (Excel, Google Sheets, pandas).")
    if st.button("Generate formulas for this dataset", key="btn_data_formulas"):
        with st.spinner("Generating formulas..."):
            st.session_state.data_formulas_result = ask_agent_data_formulas(profile, df)
        st.rerun()
    if st.session_state.data_formulas_result:
        formula_text = st.session_state.data_formulas_result
        copy_attr = html.escape(formula_text).replace("\n", "&#10;").replace("\r", "")
        st.markdown("**Formulas**")
        st.markdown(formula_text)
        st.markdown(
            f'<button type="button" class="datara-copy-btn" data-copy="{copy_attr}">Copy all</button>',
            unsafe_allow_html=True,
        )

with tab_findings:
    if result is None:
        st.caption("Generate summary above to see findings.")
    else:
        summary = result.get("summary") or {}
        cards = [
            ("Top Finding", summary.get("top_finding")),
            ("Biggest Risk", summary.get("biggest_risk")),
            ("Biggest Opportunity", summary.get("biggest_opportunity")),
            ("Recommended Next Step", summary.get("recommended_next_step")),
        ]
        for label, value in cards:
            text = (value if isinstance(value, str) and value.strip() else "") or "—"
            safe_text = html.escape(text).replace("\n", "<br>")
            icon_html = FINDING_ICONS.get(label, "")
            st.markdown(
                f'<div class="datara-finding-card">'
                f'<div class="datara-finding-label">{icon_html}{html.escape(label)}</div>'
                f'<div class="datara-finding-value">{safe_text}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

with tab_charts:
    if result is None:
        st.caption("Generate summary above to see charts.")
    else:
        charts = (result.get("charts") or [])[:2]
        if not charts:
            st.caption("No charts generated. Try generating a summary.")
        for i, ch in enumerate(charts):
            with st.container():
                st.write("**" + (ch.get("title") or "Chart") + "**")
                fig = render_chart_fig(df, ch, st.session_state.theme == "dark")
                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{i}")
                else:
                    st.caption("Chart could not be rendered.")
                expl = ch.get("explanation") or st.session_state.chart_explanations.get(i)
                if expl:
                    safe_expl = html.escape(expl).replace("\n", "<br>")
                    st.markdown(f'<div class="datara-explanation-box">{safe_expl}</div>', unsafe_allow_html=True)
                else:
                    if st.button("Explain this chart", key=f"explain_{i}"):
                        with st.spinner("..."):
                            st.session_state.chart_explanations[i] = ask_agent_chart_explanation(ch, df)
                        st.rerun()
                    else:
                        st.caption("Click *Explain this chart* for a short explanation.")

# 5. Ask AI section — rebuilt: full-width panel, no broken chat_message layout
st.markdown('<hr class="datara-ask-ai-divider" />', unsafe_allow_html=True)
st.subheader(t("ask_ai_title"))

# Suggested questions label + chips (muted, stable, no icon/animation)
st.markdown(f'<p class="datara-ask-ai-suggested-label">{html.escape(t("suggested_label"))}</p>', unsafe_allow_html=True)
suggested_qs = st.session_state.suggested_questions or []
if suggested_qs:
    cols = st.columns(3)
    for i, q in enumerate(suggested_qs):
        with cols[i % 3]:
            if st.button(q[:60] + ("…" if len(q) > 60 else ""), key=f"sug_{i}"):
                st.session_state.pending_question = q
                st.rerun()

# Handle suggested-question click: run agent and append to history
if st.session_state.pending_question:
    q = st.session_state.pending_question
    st.session_state.pending_question = None
    st.session_state.chat_history.append({"role": "user", "content": q})
    with st.spinner("..."):
        answer = ask_agent_question(df, result or {}, q, profile)
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    st.rerun()

# Render history: user = chat_message (compact), assistant = full-width panel only
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        st.markdown(_datara_ask_ai_response_panel(msg["content"]), unsafe_allow_html=True)

# New question from input
user_question = st.chat_input(t("chat_placeholder"))
if user_question:
    st.session_state.chat_history.append({"role": "user", "content": user_question})
    with st.spinner("..."):
        answer = ask_agent_question(df, result or {}, user_question, profile)
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    st.rerun()
