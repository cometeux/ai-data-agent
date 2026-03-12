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
        "mode_executive": "Executive",
        "mode_analyst": "Analyst",
        "mode_label": "Insight style",
        "tab_comparison": "Compare",
        "comparison_title": "Comparison",
        "comparison_metric": "Metric",
        "comparison_group": "Group by",
        "compare_vs_global": "vs global average",
        "compare_vs_group": "vs another group",
        "run_comparison": "Run comparison",
        "comparison_not_supported": "This dataset doesn't support comparison yet.",
        "suitability_title": "Use-case suitability",
        "suitability_good_for": "Good for",
        "fix_recipes_title": "Fix recipes",
        "issue": "Issue",
        "impact": "Impact",
        "fix": "Suggested fix",
        "formula_excel": "Excel",
        "formula_pandas": "pandas",
        "formula_sql": "SQL",
        "chart_what": "What this shows",
        "chart_takeaway": "Key takeaway",
        "chart_caveat": "Caveat",
        "chart_next_q": "Suggested next question",
        "copy": "Copy",
        "shorten": "Shorten",
        "bullets": "Bullets",
        "action_items": "Action items",
        "generate_code": "Generate formula/code",
        "next_best_title": "Suggested next steps",
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
        "mode_executive": "تنفيذي",
        "mode_analyst": "محلل",
        "mode_label": "أسلوب الرؤى",
        "tab_comparison": "مقارنة",
        "comparison_title": "المقارنة",
        "comparison_metric": "المقياس",
        "comparison_group": "التجميع حسب",
        "compare_vs_global": "مقارنة بالمتوسط العام",
        "compare_vs_group": "مقارنة بمجموعة أخرى",
        "run_comparison": "تشغيل المقارنة",
        "comparison_not_supported": "هذه البيانات لا تدعم المقارنة بعد.",
        "suitability_title": "ملاءمة الاستخدام",
        "suitability_good_for": "مناسب لـ",
        "fix_recipes_title": "وصفات الإصلاح",
        "issue": "المشكلة",
        "impact": "التأثير",
        "fix": "الإصلاح المقترح",
        "formula_excel": "Excel",
        "formula_pandas": "pandas",
        "formula_sql": "SQL",
        "chart_what": "ما يوضحه الرسم",
        "chart_takeaway": "الاستنتاج الرئيسي",
        "chart_caveat": "تحذير",
        "chart_next_q": "السؤال التالي المقترح",
        "copy": "نسخ",
        "shorten": "اختصار",
        "bullets": "نقاط",
        "action_items": "بنود إجراءات",
        "generate_code": "إنشاء صيغة/كود",
        "next_best_title": "الخطوات التالية المقترحة",
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
if "insight_mode" not in st.session_state:
    st.session_state.insight_mode = "executive"
if "insight_mode_radio" not in st.session_state:
    st.session_state.insight_mode_radio = "executive"  # executive | analyst
if "use_case_suitability" not in st.session_state:
    st.session_state.use_case_suitability = None
if "health_fix_recipes" not in st.session_state:
    st.session_state.health_fix_recipes = None
if "derived_column_suggestions" not in st.session_state:
    st.session_state.derived_column_suggestions = None
if "next_best_suggestions" not in st.session_state:
    st.session_state.next_best_suggestions = None
if "chart_explanation_detail" not in st.session_state:
    st.session_state.chart_explanation_detail = {}
if "comparison_result" not in st.session_state:
    st.session_state.comparison_result = None
if "response_transforms" not in st.session_state:
    st.session_state.response_transforms = {}  # f"{msg_idx}_{action}" -> transformed text
if "pending_transform" not in st.session_state:
    st.session_state.pending_transform = None  # (msg_idx, action) or None

# Apply theme/lang from URL (custom segment controls use ?theme= & ?lang=)
if "theme" in st.query_params:
    v = st.query_params.get("theme")
    if v in ("dark", "light") and st.session_state.theme != v:
        st.session_state.theme = v
        st.rerun()
if "lang" in st.query_params:
    v = st.query_params.get("lang")
    if v in ("en", "ar") and st.session_state.lang != v:
        st.session_state.lang = v
        st.rerun()

# -----------------------------
# Theme tokens (single source of truth; apply_css injects :root from these)
# -----------------------------
THEME_DARK = {
    "bg_base": "#06040A",
    "bg_panel": "#161121",
    "bg_surface": "#2A1E3F",
    "accent_primary": "#D4ABFE",
    "accent_secondary": "#B98AF9",
    "accent_glow": "#A978F4",
    "muted_violet": "#7E5AB6",
    "deep_plum": "#2A1E3F",
    "border_violet": "rgba(212, 171, 254, 0.14)",
    "border_dim": "rgba(212, 171, 254, 0.1)",
    "border_medium": "rgba(212, 171, 254, 0.18)",
    "border_bright": "rgba(212, 171, 254, 0.26)",
    "text_primary": "#ffffff",
    "text_secondary": "#9B92AB",
    "text_muted": "#6e6580",
    "gradient_start": "#2A1E3F",
    "gradient_end": "#06040A",
    "hero_shadow": "0 2px 10px rgba(0,0,0,0.5)",
}
THEME_LIGHT = {
    "bg_base": "#f5f3f8",
    "bg_panel": "#ffffff",
    "bg_surface": "#ebe8f2",
    "accent_primary": "#8B5CF6",
    "accent_secondary": "#7C3AED",
    "accent_glow": "#6D28D9",
    "muted_violet": "#7E5AB6",
    "deep_plum": "#e5e0ef",
    "border_violet": "rgba(126, 90, 182, 0.2)",
    "border_dim": "rgba(126, 90, 182, 0.2)",
    "border_medium": "rgba(126, 90, 182, 0.3)",
    "border_bright": "rgba(126, 90, 182, 0.4)",
    "text_primary": "#1a1525",
    "text_secondary": "#4a4358",
    "text_muted": "#6e6580",
    "gradient_start": "#e5e0ef",
    "gradient_end": "#f5f3f8",
    "hero_shadow": "none",
}


# -----------------------------
# Helpers
# -----------------------------
def reset_app_state():
    st.session_state.analysis_result = None
    st.session_state.chat_history = []
    st.session_state.last_uploaded_name = None
    st.session_state.suggested_questions = None
    st.session_state.chart_explanations = {}
    st.session_state.chart_explanation_detail = {}
    st.session_state.data_formulas_result = None
    st.session_state.use_case_suitability = None
    st.session_state.health_fix_recipes = None
    st.session_state.derived_column_suggestions = None
    st.session_state.next_best_suggestions = None
    st.session_state.comparison_result = None
    st.session_state.response_transforms = {}
    st.session_state.pending_transform = None


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


def ask_agent_for_analysis(df, profile, mode="executive"):
    """mode: 'executive' = concise, business-oriented, action-oriented; 'analyst' = detailed, caveats, method hints."""
    columns = list(df.columns)
    measure_cols = profile.get("recommended_measure_columns", []) or [c for c, t in profile.get("column_types", {}).items() if t == "numeric"][:10]
    group_cols = profile.get("recommended_grouping_columns", []) or [c for c, t in profile.get("column_types", {}).items() if t == "categorical"][:10]
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
    sample_rows = df.head(12).to_dict(orient="records")
    for row in sample_rows:
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
    mode_instruction = (
        "Tone: EXECUTIVE — concise, business-oriented, decision-friendly. No technical jargon. Focus on so-what and next action."
        if mode == "executive"
        else "Tone: ANALYST — more detailed, include assumptions and caveats, mention method/logic where relevant. Analytical depth welcome."
    )
    prompt = f"""You are a professional data analysis AI agent. Analyze this dataset and return ONLY valid JSON. {mode_instruction}

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
    """Generate 6–9 dataset-aware suggested questions across comparison, trend, anomaly, driver, cleaning, segmentation.
    Only includes questions the dataset structure supports. Returns a flat list of short, human questions."""
    columns = list(df.columns)[:40]
    col_types = profile.get("column_types", {})
    measure = profile.get("recommended_measure_columns", [])[:8]
    group = profile.get("recommended_grouping_columns", [])[:8]
    dt_cols = [c for c, t in col_types.items() if t == "datetime"]
    readiness = profile.get("readiness_pct", 100)
    high_null = [c for c, _ in profile.get("high_null_columns", [])[:5]]
    dup_count = profile.get("duplicate_rows", 0)
    n_rows = profile.get("total_rows", len(df))
    unique_counts = profile.get("unique_counts", {})

    quality_note = ""
    if readiness < 70 or high_null or dup_count > 0:
        quality_note = (
            " Data quality is a concern: readiness " + str(readiness) + "%, high-null columns: " + str(high_null or "none")
            + ", duplicate rows: " + str(dup_count) + ". Include 1–2 questions about data quality, cleaning, or reliability."
        )

    prompt = f"""You are generating suggested follow-up questions for a user who just uploaded a dataset. Questions must be specific to THIS dataset and only ask about what the data can support.

DATASET:
- Columns: {columns}
- Column types: {col_types}
- Numeric/measure columns (for metrics): {measure}
- Categorical/grouping columns: {group}
- Datetime columns (if any): {dt_cols}
- Rows: {n_rows}
- Readiness: {readiness}%
- High-null columns: {high_null or 'none'}
- Duplicate rows: {dup_count}
- Unique counts per column (sample): {dict(list(unique_counts.items())[:15])}
{quality_note}

CATEGORIES to draw from (only include questions the data supports):
- Comparison: e.g. compare one category vs another, one segment vs global average, one group vs rest (need at least one group column and one measure or count).
- Trend: e.g. over time, by period (need datetime or ordered group).
- Anomaly: e.g. outliers, unusual values (need numeric or counts).
- Driver: e.g. what drives X, main factors (need measure + groups).
- Cleaning: e.g. fix missing values, standardize categories, remove duplicates (especially if high null or duplicates).
- Segmentation: e.g. which segments perform best, break down by (need group + measure).

RULES:
- Generate 6–9 short questions (each under 12 words). Use actual column names where it helps.
- Do NOT suggest comparison/trend/segmentation if there are no suitable measure and group columns.
- Do NOT suggest trend questions if there are no datetime columns and no clear time-like dimension.
- If data is messy, include at least one cleaning/formula question.
- Return ONLY a JSON array of question strings, e.g. ["Q1?", "Q2?"]. No other text."""

    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        raw = (response.output_text or "").strip()
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            out = json.loads(raw[start:end])
            if isinstance(out, list) and len(out) >= 3:
                return [str(q).strip()[:100] for q in out[:9]]
    except Exception:
        pass
    # Fallback: dataset-aware from columns
    fallback = []
    if measure and group:
        fallback = [
            f"Which {group[0]} has the highest {measure[0]}?",
            f"What are the main drivers of {measure[0]}?",
            "Are there outliers or anomalies?",
            "What should I investigate next?",
        ]
    if dt_cols:
        fallback.append(f"How does the main metric change over time ({dt_cols[0]})?")
    if readiness < 70 or high_null or dup_count > 0:
        fallback.append("How can I clean or fix this data?")
    while len(fallback) < 6:
        fallback.append("What are the key patterns in this data?")
    return fallback[:9]


def ask_agent_derived_column_suggestions(profile, df):
    """Suggest useful derived columns: date parts, bands, tiers, normalized categories, etc."""
    columns = list(df.columns)[:30]
    ctypes = profile.get("column_types", {})
    dt_cols = [c for c, t in ctypes.items() if t == "datetime"]
    num_cols = [c for c, t in ctypes.items() if t == "numeric"]
    cat_cols = [c for c, t in ctypes.items() if t == "categorical"]
    prompt = f"""Suggest 3-6 useful derived columns the user could add. Dataset columns: {columns}. Types: {ctypes}. Datetime: {dt_cols}. Numeric: {num_cols}. Categorical: {cat_cols}.
Return ONLY a JSON array of objects: {{"suggestion": "short name or formula idea", "rationale": "one line why"}}. E.g. date parts, age bands, revenue tiers, normalized categories, engagement levels. Use actual column names. No other text."""
    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        raw = (response.output_text or "").strip()
        start, end = raw.find("["), raw.rfind("]") + 1
        if start >= 0 and end > start:
            out = json.loads(raw[start:end])
            if isinstance(out, list):
                return [{"suggestion": str(r.get("suggestion", "")), "rationale": str(r.get("rationale", ""))[:100]} for r in out[:6]]
    except Exception:
        pass
    return []


def ask_agent_next_best_suggestions(profile, result, df):
    """Return 3-4 suggested next analysis steps as short strings (e.g. 'Compare sales by region', 'Explain the first chart')."""
    summary = (result or {}).get("summary") or {}
    charts = (result or {}).get("charts") or []
    measure = profile.get("recommended_measure_columns", [])[:5]
    group = profile.get("recommended_grouping_columns", [])[:5]
    prompt = f"""Given this analysis state, suggest 3-4 concrete next steps the user could take. Return ONLY a JSON array of short strings (each under 10 words).
Summary keys: {list(summary.keys())}. Number of charts: {len(charts)}. Measure columns: {measure}. Group columns: {group}.
Examples: "Compare X by Y", "Explain the first chart", "Generate cleaning formulas", "Inspect outliers in Z". Use actual column names. Return ONLY the array."""
    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        raw = (response.output_text or "").strip()
        start, end = raw.find("["), raw.rfind("]") + 1
        if start >= 0 and end > start:
            out = json.loads(raw[start:end])
            if isinstance(out, list):
                return [str(x).strip()[:80] for x in out[:4]]
    except Exception:
        pass
    return ["Compare segments", "Explain a chart", "Generate formulas"][:3]


def ask_agent_use_case_suitability(profile, df):
    """Return list of { use_case, score, rationale } for what this dataset is good for."""
    columns = list(df.columns)
    ctypes = profile.get("column_types", {})
    measure = profile.get("recommended_measure_columns", [])[:8]
    group = profile.get("recommended_grouping_columns", [])[:8]
    dt_cols = [c for c, t in ctypes.items() if t == "datetime"]
    n = profile.get("total_rows", len(df))
    prompt = f"""For this dataset, assess suitability for common use cases. Return ONLY a JSON array of objects with keys: "use_case", "score" (1-5 or "high"/"medium"/"low"), "rationale" (one short sentence).
Dataset: {n} rows, columns: {columns}, types: {ctypes}, measure columns: {measure}, grouping: {group}, datetime: {dt_cols}.
Use cases to consider: descriptive analysis, comparison analysis, trend analysis, segmentation, forecasting, ML preparation. Only include use cases that make sense; score honestly. Return ONLY the JSON array."""

    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        raw = (response.output_text or "").strip()
        start, end = raw.find("["), raw.rfind("]") + 1
        if start >= 0 and end > start:
            out = json.loads(raw[start:end])
            if isinstance(out, list):
                return [{"use_case": str(r.get("use_case", "")), "score": str(r.get("score", "")), "rationale": str(r.get("rationale", ""))[:120]} for r in out[:8]]
    except Exception:
        pass
    return []


def ask_agent_health_fix_recipes(profile, df):
    """Return structured fix recipes: for each important issue, issue title, impact, why it matters, suggested fix, and optional Excel/pandas/SQL."""
    columns = list(df.columns)
    ctypes = profile.get("column_types") or {}
    sample = df.head(8).to_dict(orient="records")
    for row in sample:
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
    high_null = profile.get("high_null_columns", [])[:5]
    dup = profile.get("duplicate_rows", 0)
    prompt = f"""You are a data quality assistant. For this dataset, produce 2-5 fix "recipes". For each recipe return ONLY valid JSON in this exact structure (array of objects):
[{{"issue": "short title", "impact": "one line impact", "why_it_matters": "one line", "suggested_fix": "one line what to do", "excel_formula": "optional copy-paste formula or empty string", "pandas_code": "optional one block or empty", "sql": "optional or empty"}}]
Dataset: {profile.get('total_rows')} rows, columns: {columns}. Types: {ctypes}. High-null columns: {high_null}. Duplicate rows: {dup}.
Sample: {json.dumps(sample, default=str)}
Only include recipes the data actually needs (e.g. missing values, duplicates, inconsistent casing, date formatting, mixed types). Use real column names. Return ONLY the JSON array, no other text."""

    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        raw = (response.output_text or "").strip()
        start, end = raw.find("["), raw.rfind("]") + 1
        if start >= 0 and end > start:
            out = json.loads(raw[start:end])
            if isinstance(out, list):
                return [{"issue": str(r.get("issue", "")), "impact": str(r.get("impact", "")), "why_it_matters": str(r.get("why_it_matters", "")), "suggested_fix": str(r.get("suggested_fix", "")), "excel_formula": str(r.get("excel_formula", "") or ""), "pandas_code": str(r.get("pandas_code", "") or ""), "sql": str(r.get("sql", "") or "")} for r in out[:6]]
    except Exception:
        pass
    return []


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


def ask_agent_chart_explanation(chart_spec, df, mode="executive", structured=False):
    """Return explanation of the chart. If structured=True, return dict with what, takeaway, caveat, next_q.
    Otherwise return a single string (backward compatible)."""
    try:
        title = chart_spec.get("title", "Chart")
        x, y = chart_spec.get("x_column"), chart_spec.get("y_column")
        agg = chart_spec.get("aggregation", "sum")
        style = "Executive: concise, one key takeaway." if mode == "executive" else "Analyst: include caveats and suggested next question."
        if structured:
            prompt = f"""Chart: {title}. X: {x}, Y: {y}, aggregation: {agg}. {style}
Return ONLY valid JSON with exactly these keys (short strings):
"what": 1 sentence on what this chart shows.
"takeaway": 1 sentence key takeaway.
"caveat": 1 sentence warning or limitation if any, else empty string.
"next_q": 1 suggested follow-up question the user could ask."""
            response = client.responses.create(model="gpt-4.1-mini", input=prompt)
            raw = (response.output_text or "").strip()
            start, end = raw.find("{"), raw.rfind("}") + 1
            if start >= 0 and end > start:
                d = json.loads(raw[start:end])
                return {
                    "what": str(d.get("what", "")).strip()[:200],
                    "takeaway": str(d.get("takeaway", "")).strip()[:200],
                    "caveat": str(d.get("caveat", "")).strip()[:200],
                    "next_q": str(d.get("next_q", "")).strip()[:150],
                }
        # Single string
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"Chart: {title}. X: {x}, Y: {y}, aggregation: {agg}. In 1-2 sentences, what does this chart show and why it matters. {style} No preamble.",
        )
        return (response.output_text or "").strip()[:300]
    except Exception:
        return "This chart visualizes the selected dimensions and measures." if not structured else {"what": "Chart of selected dimensions and measures.", "takeaway": "", "caveat": "", "next_q": ""}


def ask_agent_transform_response(content, action, profile=None, df=None):
    """Transform an AI response: shorten, bullets, action_items, technical, formula. Returns new text."""
    action_instructions = {
        "shorten": "Summarize this in 2-3 short sentences. Keep the main point.",
        "bullets": "Turn this into a concise bullet list. Keep key facts.",
        "action_items": "Turn this into a short list of clear action items (each starting with a verb).",
        "technical": "Add more technical detail, assumptions, and caveats. Keep it accurate.",
        "formula": "Based on this answer, provide ready-to-paste Excel formula and/or pandas code where relevant. Use column names from the dataset if provided.",
    }
    if action not in action_instructions:
        return content
    extra = ""
    if action == "formula" and profile and df is not None:
        cols = list(df.columns)[:20]
        extra = f" Dataset columns: {cols}. Column types: {profile.get('column_types', {})}."
    prompt = f"""Transform the following AI-generated answer as requested. Return ONLY the transformed text, no preamble.

Request: {action_instructions[action]}.{extra}

Original answer:
{content[:3000]}"""
    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        return (response.output_text or "").strip()[:4000]
    except Exception:
        return content


def ask_agent_question(df, analysis_result, user_question, profile=None, mode="executive"):
    columns = list(df.columns)
    sample = df.head(15).to_dict(orient="records")
    for row in sample:
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
    profile_summary = ""
    if profile:
        profile_summary = f"Data profile: {profile.get('total_rows')} rows, {profile.get('total_columns', len(columns))} columns; missing cells: {profile.get('missing_total')}; duplicate rows: {profile.get('duplicate_rows')}; readiness: {profile.get('readiness_pct')}%. Column types: {profile.get('column_types', {})}."
    tone = (
        "Answer in EXECUTIVE style: concise, business-oriented, action-oriented. 2-3 short paragraphs. No technical jargon; focus on so-what and next step."
        if mode == "executive"
        else "Answer in ANALYST style: more detailed, include assumptions and caveats, method hints where relevant. 3-4 paragraphs. Analytical depth OK."
    )
    prompt = f"""You are an analytical data assistant. Be specific and data-grounded. Use numbers and column names when relevant. {tone}

{profile_summary}
Dataset columns: {columns}
Sample rows (first 15): {json.dumps(sample, default=str)}
Existing analysis summary (if any): {json.dumps(analysis_result.get("summary", {}) if isinstance(analysis_result, dict) else {}, ensure_ascii=False)}

User question: {user_question}

Base answers only on the data and analysis above. If the data cannot answer the question, say so briefly.
When the user asks for help cleaning, fixing, or improving the data, provide ready-to-paste formulas: Excel and/or Google Sheets and optionally pandas in clear code blocks, with a one-line explanation. Use column names from the dataset when relevant."""
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


def run_comparison(df, profile, group_col, metric_col, aggregation="mean", target_group_value=None):
    """Compare groups: either each group vs global average, or one group vs another.
    Returns dict: compared_groups, metric, abs_diff, pct_diff, higher, explanation, chart_data; or None with 'error' key."""
    if group_col not in df.columns:
        return {"error": "Group column not found."}
    ctypes = profile.get("column_types", {})
    measure_cols = profile.get("recommended_measure_columns", []) or [c for c, t in ctypes.items() if t == "numeric"]
    group_cols = profile.get("recommended_grouping_columns", []) or [c for c, t in ctypes.items() if t == "categorical" if profile.get("unique_counts", {}).get(c, 0) <= 100]
    if not group_cols or group_col not in group_cols:
        if group_col not in df.columns:
            return {"error": "Choose a valid group column."}
    if metric_col and metric_col not in df.columns:
        return {"error": "Metric column not found."}
    if metric_col and metric_col not in measure_cols and ctypes.get(metric_col) != "numeric":
        pass  # still allow if numeric
    try:
        if metric_col and ctypes.get(metric_col) == "numeric":
            agg = aggregation if aggregation in ("mean", "sum") else "mean"
            global_val = df[metric_col].agg(agg)
            grp = df.groupby(group_col, as_index=True)[metric_col].agg(agg)
        else:
            metric_col = "count"
            aggregation = "count"
            grp = df.groupby(group_col, as_index=True).size()
            global_val = grp.mean()  # average count per group for comparison
        grp = grp.sort_values(ascending=False)
        groups = grp.index.tolist()
        values = grp.tolist()
        if target_group_value is not None:
            if target_group_value not in groups:
                return {"error": "Selected group not found."}
            a_val = grp.loc[target_group_value]
            other_vals = [grp.loc[g] for g in groups if g != target_group_value]
            other_avg = sum(other_vals) / len(other_vals) if other_vals else 0
            abs_d = a_val - other_avg
            pct_d = (100 * abs_d / other_avg) if other_avg else 0
            higher = target_group_value if abs_d > 0 else "other groups"
            compared = [str(target_group_value), "other groups average"]
        else:
            compared = [str(g) for g in groups[:2]] if len(groups) >= 2 else [str(groups[0]), "global"]
            a_val = values[0] if values else 0
            abs_d = a_val - global_val if isinstance(global_val, (int, float)) else 0
            pct_d = (100 * abs_d / global_val) if global_val else 0
            higher = groups[0] if abs_d > 0 else "global average"
        return {
            "compared_groups": compared,
            "metric": metric_col,
            "aggregation": aggregation,
            "values": values[:10],
            "groups": groups[:10],
            "global_val": global_val,
            "abs_diff": abs_d,
            "pct_diff": pct_d,
            "higher": higher,
            "chart_data": {"groups": groups[:15], "values": values[:15], "metric": metric_col},
        }
    except Exception as e:
        return {"error": str(e)[:200]}


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


def _datara_user_msg_html(content):
    """Single user message row (custom HTML) to avoid st.chat_message duplication and red styling."""
    body_escaped = html.escape(content).replace("\n", "<br>")
    return (
        f'<div class="datara-ask-ai-user-row">'
        f'<div class="datara-ask-ai-user-bubble">{body_escaped}</div>'
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
def _root_css(theme):
    """Build :root block from THEME_DARK or THEME_LIGHT so light mode is server-driven."""
    tokens = THEME_LIGHT if theme == "light" else THEME_DARK
    lines = [f"        --{k.replace('_', '-')}: {v};" for k, v in tokens.items()]
    lines.append("        --font-sans: 'Inter', -apple-system, sans-serif;")
    lines.append("        --font-mono: 'JetBrains Mono', monospace;")
    lines.append("        --radius-sm: 12px; --radius-md: 18px; --radius-lg: 24px;")
    return "    :root {\n" + "\n".join(lines) + "\n    }\n"


def apply_css():
    theme = st.session_state.get("theme", "dark")
    root_block = _root_css(theme)
    st.markdown("""<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* Datara theme: """ + theme + """ (tokens in :root) */
""" + root_block + """
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
        background-image: radial-gradient(ellipse at 50% 30%, var(--gradient-start) 0%, var(--gradient-end) 70%) !important;
    }
    .block-container { max-width: 1200px; padding: 48px 32px 64px; }
    .stApp, .stApp .main { background: transparent !important; }
    .stApp .main .block-container { color: var(--text-secondary); font-family: var(--font-sans); }

    .stApp h1 {
        font-family: var(--font-sans); font-size: 28px !important; font-weight: 600 !important;
        color: var(--text-primary) !important; letter-spacing: -0.5px; margin-bottom: 8px !important;
        text-shadow: var(--hero-shadow);
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
    .datara-mode-label { font-size: 13px !important; color: var(--text-muted) !important; font-weight: 500 !important; margin-right: 8px !important; }
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

    /* Ask AI — user message row (custom HTML; no st.chat_message, no red) */
    .datara-ask-ai-user-row {
        display: block !important;
        width: 100% !important;
        margin-bottom: 12px !important;
    }
    .datara-ask-ai-user-bubble {
        display: inline-block !important;
        max-width: 85% !important;
        padding: 12px 18px !important;
        background: var(--muted-violet) !important;
        border: 1px solid var(--border-violet) !important;
        border-radius: var(--radius-lg) !important;
        font-size: 15px !important;
        line-height: 1.5 !important;
        color: var(--text-primary) !important;
        box-shadow: none !important;
    }
    body.datara-lang-ar .datara-ask-ai-user-bubble { margin-right: 0 !important; margin-left: auto !important; }

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
    /* Kill ALL red/coral in chat and Ask AI area — Datara plum/lilac only */
    [data-testid="stChatMessage"],
    [data-testid="stChatMessage"] *,
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] *,
    .block-container > *:has(.datara-ask-ai-divider) ~ *,
    .block-container > *:has(.datara-ask-ai-suggested-label),
    .block-container > *:has(.datara-ask-ai-user-row),
    .block-container > *:has(.datara-ask-ai-response) {
        --primary: var(--accent-primary) !important;
        --background-color: var(--bg-panel) !important;
    }
    [data-testid="stChatMessage"] [style*="red"],
    [data-testid="stChatMessage"] [style*="coral"],
    [data-testid="stChatInput"] [style*="red"],
    [data-testid="stChatInput"] [style*="coral"] { background: var(--muted-violet) !important; color: var(--text-primary) !important; border-color: var(--border-violet) !important; }
    [data-testid="stChatInput"] button svg path,
    [data-testid="stChatInput"] [data-testid="stChatInputSubmitButton"] svg path { fill: #161121 !important; stroke: #161121 !important; }

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
    .datara-response-utils { margin-top: 8px !important; margin-bottom: 4px !important; }
    .datara-response-utils .datara-util-btn { font-size: 11px !important; padding: 4px 10px !important; }
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
    body.datara-lang-ar .datara-ask-ai-response-body,
    body.datara-lang-ar .datara-ask-ai-user-bubble {
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

# Lang: set body class for RTL + Noto Sans Arabic (theme is server-driven via :root)
_lang = st.session_state.get("lang", "en")
st.markdown(
    f'<div id="datara-lang-config" data-lang="{_lang}"></div>'
    r'<script>(function(){var c=document.getElementById("datara-lang-config");if(c&&c.getAttribute("data-lang")==="ar")document.body.classList.add("datara-lang-ar");else document.body.classList.remove("datara-lang-ar");})();</script>',
    unsafe_allow_html=True,
)

# Header: brand | custom segment controls (links; no Streamlit widgets)
_theme = st.session_state.get("theme", "dark")
_seg_lang = (
    f'<div class="datara-seg">'
    f'<a href="?lang=en" class="datara-seg-opt{" datara-seg-active" if st.session_state.lang == "en" else ""}">{html.escape(t("lang_en"))}</a>'
    f'<a href="?lang=ar" class="datara-seg-opt{" datara-seg-active" if st.session_state.lang == "ar" else ""}">{html.escape(t("lang_ar"))}</a>'
    f'</div>'
)
_seg_theme = (
    f'<div class="datara-seg">'
    f'<a href="?theme=dark" class="datara-seg-opt{" datara-seg-active" if st.session_state.theme == "dark" else ""}">{html.escape(t("theme_dark"))}</a>'
    f'<a href="?theme=light" class="datara-seg-opt{" datara-seg-active" if st.session_state.theme == "light" else ""}">{html.escape(t("theme_light"))}</a>'
    f'</div>'
)
_h1, _h2 = st.columns([2, 1])
with _h1:
    st.markdown('<span class="datara-header-brand">Datara</span>', unsafe_allow_html=True)
with _h2:
    st.markdown(
        f'<div class="datara-header-controls">{_seg_lang}{_seg_theme}</div>'
        '<style>'
        '.datara-header-brand{font-family:var(--font-sans);font-size:18px;font-weight:600;color:var(--text-primary);}'
        '.datara-header-controls{display:flex;align-items:center;gap:10px;flex-wrap:wrap;}'
        '.datara-seg{display:inline-flex;background:var(--bg-panel);border:1px solid var(--border-dim);border-radius:999px;padding:3px;}'
        '.datara-seg-opt{font-size:12px;font-weight:500;padding:6px 14px;border-radius:999px;color:var(--text-muted);text-decoration:none;transition:background .2s,color .2s;}'
        '.datara-seg-opt:first-child{border-radius:999px 0 0 999px;}'
        '.datara-seg-opt:last-child{border-radius:0 999px 999px 0;}'
        '.datara-seg-opt:hover{color:var(--text-primary);}'
        '.datara-seg-opt.datara-seg-active{background:var(--accent-primary);color:#161121;}'
        '</style>',
        unsafe_allow_html=True,
    )

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

# Insight style: Executive | Analyst (affects summary, findings, Ask AI, chart explanations)
mode_col, cta_col = st.columns([1, 1])
with mode_col:
    st.markdown(f'<span class="datara-mode-label">{html.escape(t("mode_label"))}</span>', unsafe_allow_html=True)
    st.radio(
        "insight_mode",
        options=["executive", "analyst"],
        format_func=lambda x: t("mode_executive") if x == "executive" else t("mode_analyst"),
        key="insight_mode_radio",
        horizontal=True,
        label_visibility="collapsed",
    )
with cta_col:
    if st.button(t("generate_cta"), key="cta_gen"):
        with st.spinner("Analyzing..."):
            st.session_state.analysis_result = ask_agent_for_analysis(df, profile, st.session_state.get("insight_mode_radio", "executive"))
        st.rerun()
if profile.get("readiness_factors"):
    with st.expander("What affects the readiness score?"):
        for f in profile["readiness_factors"]:
            st.write("-", str(f) if f is not None else "—")

# 4. Main Tabbed Workspace (translated labels)
tab_overview, tab_health, tab_findings, tab_charts, tab_comparison = st.tabs([
    t("tab_overview"),
    t("tab_health"),
    t("tab_findings"),
    t("tab_charts"),
    t("tab_comparison"),
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
    # Next best analysis suggestions (when we have results)
    if result and st.session_state.get("next_best_suggestions") is None and st.button(t("next_best_title"), key="btn_next_best"):
        with st.spinner("..."):
            st.session_state.next_best_suggestions = ask_agent_next_best_suggestions(profile, result, df)
        st.rerun()
    if st.session_state.get("next_best_suggestions"):
        st.markdown(f"**{t('next_best_title')}**")
        for nb_idx, nb in enumerate(st.session_state.next_best_suggestions):
            if st.button(nb[:50] + ("…" if len(nb) > 50 else ""), key=f"nextbest_{nb_idx}"):
                st.session_state.pending_question = nb
                st.rerun()

    # Use-case suitability (compact)
    if st.session_state.get("use_case_suitability") is None and st.button("Assess use-case suitability", key="btn_suitability"):
        with st.spinner("Assessing..."):
            st.session_state.use_case_suitability = ask_agent_use_case_suitability(profile, df)
        st.rerun()
    if st.session_state.get("use_case_suitability"):
        st.markdown(f'<div class="datara-panel-title">{t("suitability_title")}</div>', unsafe_allow_html=True)
        for u in st.session_state.use_case_suitability:
            uc = html.escape(u.get("use_case", ""))
            sc = html.escape(str(u.get("score", "")))
            rat = html.escape(u.get("rationale", ""))
            st.markdown(f'<div class="datara-content-panel"><div class="datara-panel-body"><strong>{uc}</strong> — {sc}<br>{rat}</div></div>', unsafe_allow_html=True)

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
    # Derived column suggestions
    if st.session_state.get("derived_column_suggestions") is None and st.button("Suggest derived columns", key="btn_derived"):
        with st.spinner("..."):
            st.session_state.derived_column_suggestions = ask_agent_derived_column_suggestions(profile, df)
        st.rerun()
    if st.session_state.get("derived_column_suggestions"):
        st.caption("**Suggested derived columns**")
        for d in st.session_state.derived_column_suggestions:
            st.caption(f"• {d.get('suggestion', '')} — {d.get('rationale', '')}")
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

    # Data health fix recipes (issue → impact → fix → optional formulas)
    st.markdown("---")
    st.markdown(f"**{t('fix_recipes_title')}** — Issue, impact, suggested fix, and optional Excel/pandas/SQL.")
    if st.button("Generate fix recipes", key="btn_fix_recipes"):
        with st.spinner("Generating fix recipes..."):
            st.session_state.health_fix_recipes = ask_agent_health_fix_recipes(profile, df)
        st.rerun()
    if st.session_state.get("health_fix_recipes"):
        for idx, r in enumerate(st.session_state.health_fix_recipes):
            issue = html.escape(r.get("issue", ""))
            impact = html.escape(r.get("impact", ""))
            why = html.escape(r.get("why_it_matters", ""))
            fix = html.escape(r.get("suggested_fix", ""))
            ex = (r.get("excel_formula") or "").strip()
            pd_code = (r.get("pandas_code") or "").strip()
            sql = (r.get("sql") or "").strip()
            st.markdown(
                f'<div class="datara-finding-card">'
                f'<div class="datara-panel-title">{issue}</div>'
                f'<div class="datara-panel-body">'
                f'<strong>{t("impact")}:</strong> {impact}<br>'
                f'<strong>Why it matters:</strong> {why}<br>'
                f'<strong>{t("fix")}:</strong> {fix}'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            if ex or pd_code or sql:
                with st.expander(f"{t('formula_excel')} / {t('formula_pandas')} / {t('formula_sql')}"):
                    if ex:
                        st.text(ex)
                    if pd_code:
                        st.code(pd_code, language="python")
                    if sql:
                        st.code(sql, language="sql")

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
                detail = st.session_state.chart_explanation_detail.get(i)
                expl = ch.get("explanation") or st.session_state.chart_explanations.get(i)
                if detail and isinstance(detail, dict):
                    what = html.escape(detail.get("what", ""))
                    takeaway = html.escape(detail.get("takeaway", ""))
                    caveat = html.escape(detail.get("caveat", ""))
                    next_q = html.escape(detail.get("next_q", ""))
                    parts_ex = [f"<strong>{t('chart_what')}</strong> {what}"]
                    if takeaway:
                        parts_ex.append(f"<strong>{t('chart_takeaway')}</strong> {takeaway}")
                    if caveat:
                        parts_ex.append(f"<strong>{t('chart_caveat')}</strong> {caveat}")
                    if next_q:
                        parts_ex.append(f"<strong>{t('chart_next_q')}</strong> {next_q}")
                    st.markdown(f'<div class="datara-explanation-box">{"<br>".join(parts_ex)}</div>', unsafe_allow_html=True)
                elif expl:
                    safe_expl = html.escape(expl if isinstance(expl, str) else "").replace("\n", "<br>")
                    st.markdown(f'<div class="datara-explanation-box">{safe_expl}</div>', unsafe_allow_html=True)
                else:
                    if st.button("Explain this chart", key=f"explain_{i}"):
                        with st.spinner("..."):
                            out = ask_agent_chart_explanation(ch, df, st.session_state.get("insight_mode_radio", "executive"), structured=True)
                            if isinstance(out, dict):
                                st.session_state.chart_explanation_detail[i] = out
                            else:
                                st.session_state.chart_explanations[i] = out
                        st.rerun()
                    else:
                        st.caption("Click *Explain this chart* for what it shows, key takeaway, caveat, and suggested next question.")

with tab_comparison:
    st.markdown(f'<div class="datara-panel-title">{html.escape(t("comparison_title"))}</div>', unsafe_allow_html=True)
    measure_cols = profile.get("recommended_measure_columns", []) or [c for c, t in (profile.get("column_types") or {}).items() if t == "numeric"]
    group_cols = profile.get("recommended_grouping_columns", []) or [c for c in (df.columns.tolist()) if (profile.get("unique_counts", {}).get(c, 999) <= 100) and c in (profile.get("column_types") or {})]
    if not measure_cols and not group_cols:
        st.caption(t("comparison_not_supported"))
    else:
        metric_options = ["count"] + measure_cols[:15]
        group_options = group_cols[:20] if group_cols else [c for c in df.columns if df[c].nunique() <= 100][:20]
        if not group_options:
            st.caption(t("comparison_not_supported"))
        else:
            comp_metric = st.selectbox(t("comparison_metric"), options=metric_options, key="comp_metric")
            comp_group = st.selectbox(t("comparison_group"), options=group_options, key="comp_group")
            comp_agg = "count"
            if comp_metric != "count":
                comp_agg = st.radio("Aggregation", options=["mean", "sum"], key="comp_agg", horizontal=True)
            run_comp = st.button(t("run_comparison"), key="run_comp")
            if run_comp:
                res = run_comparison(df, profile, comp_group, comp_metric if comp_metric != "count" else None, comp_agg, None)
                st.session_state.comparison_result = res
            if st.session_state.get("comparison_result"):
                res = st.session_state.comparison_result
                if res.get("error"):
                    st.warning(res["error"])
                else:
                    st.markdown(
                        f'<div class="datara-content-panel">'
                        f'<div class="datara-panel-title">Comparison result</div>'
                        f'<div class="datara-panel-body">'
                        f'<strong>{html.escape(str(res.get("compared_groups", [])[0]))}</strong> vs '
                        f'<strong>{html.escape(str(res.get("compared_groups", [])[1] if len(res.get("compared_groups", [])) > 1 else "global"))}</strong> '
                        f'({res.get("metric", "")} {res.get("aggregation", "")}). '
                        f'Absolute difference: {res.get("abs_diff", 0):.2f}. '
                        f'Percentage difference: {res.get("pct_diff", 0):.1f}%. '
                        f'Higher: {html.escape(str(res.get("higher", "")))}.'
                        f'</div></div>',
                        unsafe_allow_html=True,
                    )
                    cd = res.get("chart_data", {})
                    if cd and cd.get("groups") and cd.get("values"):
                        comp_df = pd.DataFrame({"group": cd["groups"], "value": cd["values"]})
                        fig = px.bar(comp_df, x="group", y="value", title="", color_discrete_sequence=DATARA_CHART_COLORS)
                        if st.session_state.get("theme", "dark") == "dark":
                            fig.update_layout(paper_bgcolor="#161121", plot_bgcolor="#2A1E3F", font=dict(color="#ffffff"))
                        st.plotly_chart(fig, use_container_width=True, key="comp_chart")

# 5. Ask AI section — full-width panel, response utilities
st.markdown('<hr class="datara-ask-ai-divider" />', unsafe_allow_html=True)
st.subheader(t("ask_ai_title"))

# Handle response transform (Shorten, Bullets, etc.) from previous run
if st.session_state.get("pending_transform"):
    pt = st.session_state.pending_transform
    st.session_state.pending_transform = None
    hist = st.session_state.chat_history
    if isinstance(pt, (list, tuple)) and len(pt) == 2 and pt[0] < len(hist) and hist[pt[0]].get("role") == "assistant":
        idx, action = pt[0], pt[1]
        content = hist[idx].get("content", "")
        result = ask_agent_transform_response(content, action, profile, df)
        st.session_state.response_transforms[f"{idx}_{action}"] = result
    st.rerun()

# Suggested questions label + chips (muted, stable)
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
        answer = ask_agent_question(df, result or {}, q, profile, st.session_state.get("insight_mode_radio", "executive"))
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    st.rerun()

# Render history: user = custom HTML row; assistant = full-width panel + response utilities
for idx, msg in enumerate(st.session_state.chat_history):
    if msg["role"] == "user":
        st.markdown(_datara_user_msg_html(msg["content"]), unsafe_allow_html=True)
    else:
        st.markdown(_datara_ask_ai_response_panel(msg["content"]), unsafe_allow_html=True)
        # Copy button (JS) + transform actions
        copy_attr = html.escape(msg.get("content", "")).replace("\n", "&#10;").replace("\r", "").replace('"', "&quot;")[:5000]
        st.markdown(f'<div class="datara-response-utils"><button type="button" class="datara-copy-btn datara-util-btn" data-copy="{copy_attr}">{t("copy")}</button></div>', unsafe_allow_html=True)
        u1, u2, u3, u4, u5 = st.columns(5)
        with u1:
            if st.button(t("shorten"), key=f"shorten_{idx}"):
                st.session_state.pending_transform = (idx, "shorten")
                st.rerun()
        with u2:
            if st.button(t("bullets"), key=f"bullets_{idx}"):
                st.session_state.pending_transform = (idx, "bullets")
                st.rerun()
        with u3:
            if st.button(t("action_items"), key=f"action_{idx}"):
                st.session_state.pending_transform = (idx, "action_items")
                st.rerun()
        with u4:
            if st.button("Technical", key=f"technical_{idx}"):
                st.session_state.pending_transform = (idx, "technical")
                st.rerun()
        with u5:
            if st.button(t("generate_code"), key=f"formula_{idx}"):
                st.session_state.pending_transform = (idx, "formula")
                st.rerun()
        for action, label in [("shorten", "Shortened"), ("bullets", "Bullets"), ("action_items", "Action items"), ("technical", "Technical"), ("formula", "Formula/code")]:
            trans = st.session_state.response_transforms.get(f"{idx}_{action}")
            if trans:
                with st.expander(label):
                    st.markdown(trans)

# New question from input
user_question = st.chat_input(t("chat_placeholder"))
if user_question:
    st.session_state.chat_history.append({"role": "user", "content": user_question})
    with st.spinner("..."):
        answer = ask_agent_question(df, result or {}, user_question, profile, st.session_state.get("insight_mode_radio", "executive"))
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    st.rerun()
