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

Dataset columns:
{columns}

Dataset types:
{dtypes}

Sample rows:
{sample_rows}

Return JSON in exactly this structure:
{{
  "summary": {{
    "overview": "brief overview of the dataset",
    "key_insights": [
      "insight 1",
      "insight 2",
      "insight 3"
    ],
    "recommendations": [
      "recommendation 1",
      "recommendation 2"
    ],
    "final_summary": "clear professional final summary"
  }},
  "charts": [
    {{
      "title": "chart title",
      "chart_type": "bar",
      "x_column": "exact column name",
      "y_column": "exact column name",
      "aggregation": "sum"
    }},
    {{
      "title": "chart title",
      "chart_type": "line",
      "x_column": "exact column name",
      "y_column": "exact column name",
      "aggregation": "mean"
    }}
  ]
}}

Rules:
- Return at least 2 charts
- chart_type must be one of: bar, line, pie, scatter
- aggregation must be one of: sum, mean, count, none
- use exact dataset column names
- choose useful charts for understanding the data
- keep the summary concise and practical
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return json.loads(response.output_text)


def ask_agent_question(df, analysis_result, user_question):
    columns = list(df.columns)
    sample_rows = df.head(10).to_dict(orient="records")
    prompt = f"""
You are a helpful data analysis AI agent.

Dataset columns:
{columns}

Sample rows:
{sample_rows}

Existing analysis summary:
{json.dumps(analysis_result, ensure_ascii=False)}

User follow-up question:
{user_question}

Answer the user's question clearly and directly based only on the uploaded data and existing analysis.
"""
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
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
    chart_type = chart["chart_type"]
    x_column = chart["x_column"]
    y_column = chart["y_column"]
    aggregation = chart.get("aggregation", "sum")
    title = chart["title"]
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
            paper_bgcolor="rgba(18,18,22,0.4)",
            plot_bgcolor="rgba(18,18,22,0.2)",
            font=dict(color="#F3F4F6", size=12),
            margin=dict(l=20, r=20, t=10, b=20),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.06)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.06)")
        )
    else:
        fig.update_layout(
            paper_bgcolor="rgba(255,255,255,0.5)",
            plot_bgcolor="rgba(255,255,255,0.3)",
            font=dict(color="#111827", size=12),
            margin=dict(l=20, r=20, t=10, b=20)
        )
    return fig


# -----------------------------
# Reference-matching CSS (dark + light)
# -----------------------------
def inject_css(theme):
    is_dark = theme == "dark"
    if is_dark:
        bg_base = "#060608"
        text_primary = "#F3F4F6"
        text_secondary = "#9CA3AF"
        glass_panel = "rgba(18, 18, 22, 0.6)"
        border_subtle = "rgba(255, 255, 255, 0.06)"
        border_highlight = "rgba(255, 255, 255, 0.12)"
        border_card = "rgba(255, 255, 255, 0.08)"
        th_bg = "rgba(255, 255, 255, 0.02)"
        td_border = "rgba(255, 255, 255, 0.03)"
        dot_bg = "1px 1px at 10% 10%, rgba(255,255,255,0.6) 100%, transparent"
    else:
        bg_base = "#f8fafc"
        text_primary = "#111827"
        text_secondary = "#6b7280"
        glass_panel = "rgba(255, 255, 255, 0.75)"
        border_subtle = "rgba(0, 0, 0, 0.08)"
        border_highlight = "rgba(0, 0, 0, 0.12)"
        border_card = "rgba(0, 0, 0, 0.08)"
        th_bg = "rgba(0, 0, 0, 0.03)"
        td_border = "rgba(0, 0, 0, 0.05)"
        dot_bg = "1px 1px at 10% 10%, rgba(0,0,0,0.08) 100%, transparent"

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {{ box-sizing: border-box; }}
html, body, .stApp, [data-testid="stAppViewContainer"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: {bg_base} !important;
    color: {text_primary} !important;
}}
[data-testid="stAppViewContainer"] > section {{ background: transparent !important; }}

.block-container {{
    max-width: 1100px !important;
    margin: 0 auto !important;
    padding: 60px 24px 120px !important;
}}

/* Subtle dot grid (dark) / light grid */
.stApp::before {{
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 0;
    background-image: radial-gradient({dot_bg}),
        radial-gradient(1.5px 1.5px at 80% 20%, rgba(0,0,0,0.06) 100%, transparent),
        radial-gradient(1px 1px at 30% 60%, rgba(0,0,0,0.05) 100%, transparent);
    background-size: 150px 150px;
    background-attachment: fixed;
    opacity: {0.15 if is_dark else 0.5};
}}
[data-testid="stAppViewContainer"] {{ position: relative; z-index: 1; }}

/* Light flares (dark only) */
.light-flare-1 {{
    position: fixed;
    top: -10vh; left: 50%;
    transform: translateX(-50%);
    width: 30vw; height: 90vh;
    background: radial-gradient(ellipse 50% 100% at top center, rgba(79, 70, 229, 0.25) 0%, transparent 100%);
    pointer-events: none;
    z-index: 0;
    filter: blur(50px);
}}
.light-flare-2 {{
    position: fixed;
    top: -5vh; left: 50%;
    transform: translateX(-50%);
    width: 8vw; height: 70vh;
    background: radial-gradient(ellipse 50% 100% at top center, rgba(147, 51, 234, 0.4) 0%, transparent 100%);
    pointer-events: none;
    z-index: 0;
    filter: blur(30px);
}}

.glass-panel {{
    background: {glass_panel};
    backdrop-filter: blur(32px);
    -webkit-backdrop-filter: blur(32px);
    border: 1px solid {border_subtle};
    border-top: 1px solid {border_highlight};
    border-radius: 24px;
    box-shadow: 0 24px 48px rgba(0, 0, 0, 0.15);
    padding: 32px;
}}

.hero {{ text-align: center; margin-bottom: 16px; display: flex; flex-direction: column; align-items: center; gap: 16px; }}
.hero-orb {{
    width: 64px; height: 64px;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #ffffff 0%, #A855F7 40%, #4F46E5 100%);
    box-shadow: 0 0 30px rgba(168, 85, 247, 0.5), inset 0 -4px 12px rgba(0,0,0,0.2);
}}
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    font-size: 0.85rem;
    font-weight: 500;
    color: #E0E7FF;
}}
.hero h1 {{ font-size: 2.5rem; font-weight: 500; letter-spacing: -0.02em; color: {text_primary} !important; }}
.hero-desc {{ color: {text_secondary} !important; font-size: 1.05rem; max-width: 500px; }}

.section-title {{
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 16px;
    color: {text_secondary} !important;
}}

/* Dropzone styling */
[data-testid="stFileUploader"] {{
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px dashed rgba(255,255,255,0.15) !important;
    border-radius: 16px !important;
    padding: 24px !important;
}}
[data-testid="stFileUploader"]:hover {{ border-color: rgba(168, 85, 247, 0.5) !important; }}
[data-testid="stFileUploader"] label {{ color: {text_primary} !important; }}

.dashboard-grid {{ display: grid; grid-template-columns: 1fr 2fr; gap: 24px; }}
@media (max-width: 900px) {{ .dashboard-grid {{ grid-template-columns: 1fr; }} }}

.ref-list-item {{
    display: flex;
    align-items: center;
    padding: 12px 8px;
    background: transparent;
    border-radius: 10px;
    gap: 16px;
}}
.ref-list-item:hover {{ background: rgba(255, 255, 255, 0.03); }}
.ref-icon-box {{
    width: 36px; height: 36px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid {border_card};
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.ref-text-box {{ flex: 1; }}
.ref-title {{ font-size: 0.95rem; font-weight: 500; color: {text_primary} !important; }}
.ref-subtitle {{ font-size: 0.8rem; color: {text_secondary} !important; }}

.kpi-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
.kpi-card {{
    background: transparent;
    border-radius: 16px;
    border: 1px solid {border_card};
    padding: 20px;
}}
.kpi-label {{
    color: {text_secondary} !important;
    font-size: 0.85rem;
    margin-bottom: 12px;
}}
.kpi-value {{ font-size: 1.75rem; font-weight: 500; letter-spacing: -0.02em; color: {text_primary} !important; }}

/* Table */
.table-wrap {{
    width: 100%;
    overflow-x: auto;
    border-radius: 16px;
    border: 1px solid {border_card};
}}
.table-wrap table {{ width: 100%; border-collapse: collapse; text-align: left; }}
.table-wrap th {{
    color: {text_secondary} !important;
    font-weight: 500;
    border-bottom: 1px solid {border_card};
    background: {th_bg} !important;
    padding: 16px 20px;
    font-size: 0.9rem;
}}
.table-wrap td {{
    border-bottom: 1px solid {td_border};
    color: {text_primary} !important;
    padding: 16px 20px;
    font-size: 0.9rem;
}}
.table-wrap tr:last-child td {{ border-bottom: none; }}

.cta-container {{ display: flex; justify-content: center; margin: 16px 0; }}
.stButton > button {{
    background: linear-gradient(90deg, #4F46E5, #9333EA) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    padding: 16px 40px !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 32px rgba(147, 51, 234, 0.4) !important;
}}
.stButton > button:hover {{
    box-shadow: 0 12px 40px rgba(147, 51, 234, 0.6) !important;
}}

.analysis-section {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }}
@media (max-width: 900px) {{ .analysis-section {{ grid-template-columns: 1fr; }} }}

.charts-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }}
@media (max-width: 900px) {{ .charts-grid {{ grid-template-columns: 1fr; }} }}
.chart-card {{
    background: transparent;
    border-radius: 16px;
    border: 1px solid {border_card};
    padding: 24px;
    min-height: 300px;
}}
.chart-title {{ font-weight: 500; font-size: 0.95rem; color: {text_primary} !important; margin-bottom: 16px; }}

/* Chat console */
[data-testid="stChatInput"] {{
    background: linear-gradient(90deg, #5B42F3, #8B5CF6) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 16px !important;
    padding: 16px 24px !important;
    box-shadow: 0 8px 32px rgba(139, 92, 246, 0.5) !important;
}}
[data-testid="stChatInput"] input {{ color: #FFFFFF !important; }}
[data-testid="stChatInput"] input::placeholder {{ color: rgba(255,255,255,0.9) !important; }}
[data-testid="stChatMessage"] {{ color: {text_primary} !important; }}

/* Hide Streamlit branding */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Render
# -----------------------------
inject_css(st.session_state.theme)

# Theme toggle (top right, no sidebar)
_, col_theme = st.columns([5, 1])
with col_theme:
    st.radio("Theme", ["dark", "light"], key="theme", horizontal=True, label_visibility="collapsed")

# Light flares (dark only)
if st.session_state.theme == "dark":
    st.markdown('<div class="light-flare-1"></div><div class="light-flare-2"></div>', unsafe_allow_html=True)

# Hero
st.markdown("""
<div class="hero">
    <div class="hero-orb"></div>
    <div class="badge">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
        AI-Powered Analytics
    </div>
    <h1>Data Analysis AI Agent</h1>
    <p class="hero-desc">Upload your dataset, and I'll automatically generate insights, visual summaries, and actionable recommendations.</p>
</div>
""", unsafe_allow_html=True)

# Data Source glass panel
st.markdown('<div class="glass-panel"><h2 class="section-title">Data Source</h2>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Drag & drop your dataset — Supports CSV, XLSX up to 50MB",
    type=["csv", "xlsx"],
    label_visibility="collapsed"
)
st.markdown("</div>", unsafe_allow_html=True)

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

    # Dashboard grid: Overview (1fr) + Shape (2fr)
    st.markdown("""
    <div class="dashboard-grid">
        <div class="glass-panel overview-card">
            <h2 class="section-title">Dataset Overview</h2>
            <div class="ref-list-item">
                <div class="ref-icon-box">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                </div>
                <div class="ref-text-box">
                    <div class="ref-title">""" + uploaded_file.name + """</div>
                    <div class="ref-subtitle">""" + f"{size_mb} MB • {n_rows:,} rows" + """</div>
                </div>
            </div>
            <div class="ref-list-item">
                <div class="ref-icon-box" style="color: #A78BFA;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline></svg>
                </div>
                <div class="ref-text-box">
                    <div class="ref-title">Data Type</div>
                    <div class="ref-subtitle">""" + data_types_str + """</div>
                </div>
            </div>
        </div>
        <div class="glass-panel">
            <h2 class="section-title">Shape</h2>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">Total Rows</div>
                    <div class="kpi-value">""" + f"{n_rows:,}" + """</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Total Columns</div>
                    <div class="kpi-value">""" + str(n_cols) + """</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Preview Rows</div>
                    <div class="kpi-value">""" + str(preview_n) + """</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Data Preview (HTML table to match reference styling)
    preview_df = df.head(10)
    thead = "".join(f"<th>{c}</th>" for c in preview_df.columns)
    trows = ""
    for _, row in preview_df.iterrows():
        trows += "<tr>" + "".join(f"<td>{row[c]}</td>" for c in preview_df.columns) + "</tr>"
    st.markdown(f"""
    <div class="glass-panel">
        <h2 class="section-title">Data Preview</h2>
        <div class="table-wrap">
            <table class="dataframe">
                <thead><tr>{thead}</tr></thead>
                <tbody>{trows}</tbody>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA
    st.markdown('<div class="cta-container">', unsafe_allow_html=True)
    if st.button("Generate Summary and Charts"):
        with st.spinner("Analyzing data..."):
            st.session_state.analysis_result = ask_agent_for_analysis(df)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    result = st.session_state.analysis_result

    if result is not None:
        summary = result["summary"]
        charts = result.get("charts", [])

        # Analysis Summary panel (ref-list style)
        st.markdown("""
        <div class="glass-panel">
            <h2 class="section-title">Analysis Summary</h2>
            <div class="analysis-section">
                <div class="ref-list-item">
                    <div class="ref-icon-box" style="color: #34D399;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>
                    </div>
                    <div class="ref-text-box">
                        <div class="ref-title">Overview</div>
                        <div class="ref-subtitle">General trends and descriptive stats</div>
                    </div>
                </div>
                <div class="ref-list-item">
                    <div class="ref-icon-box" style="color: #FBBF24;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path></svg>
                    </div>
                    <div class="ref-text-box">
                        <div class="ref-title">Key Insights</div>
                        <div class="ref-subtitle">Anomalies, correlations, and highlights</div>
                    </div>
                </div>
                <div class="ref-list-item">
                    <div class="ref-icon-box" style="color: #60A5FA;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                    </div>
                    <div class="ref-text-box">
                        <div class="ref-title">Recommendations</div>
                        <div class="ref-subtitle">Actionable next steps based on data</div>
                    </div>
                </div>
                <div class="ref-list-item">
                    <div class="ref-icon-box" style="color: #F87171;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
                    </div>
                    <div class="ref-text-box">
                        <div class="ref-title">Final Summary</div>
                        <div class="ref-subtitle">Executive brief and conclusion</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Summary content (expandable-style blocks)
        st.markdown("#### Overview")
        st.write(summary["overview"])
        st.markdown("#### Key Insights")
        for item in summary["key_insights"]:
            st.markdown(f"- {item}")
        st.markdown("#### Recommendations")
        for item in summary["recommendations"]:
            st.markdown(f"- {item}")
        st.markdown("#### Final Summary")
        st.write(summary["final_summary"])

        # Visualizations
        st.markdown('<div class="glass-panel"><h2 class="section-title">Visualizations</h2><div class="charts-grid">', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, chart in enumerate(charts):
            with cols[i % 2]:
                st.markdown(f'<div class="chart-card"><div class="chart-title">{chart.get("title", "Chart")}</div>', unsafe_allow_html=True)
                fig = render_chart_fig(df, chart, st.session_state.theme == "dark")
                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.markdown('<div style="min-height:260px; border:1px dashed rgba(255,255,255,0.1); border-radius:8px; display:flex; align-items:center; justify-content:center; color:#9CA3AF;">Chart not available</div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    # Chat
    st.markdown("---")
    st.markdown("**Ask questions about your data**")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_question = st.chat_input("Ask AI to slice the data, find specific metrics, or generate new charts...")
    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.write(user_question)
        with st.chat_message("assistant"):
            answer = ask_agent_question(df, result if result else {}, user_question)
            st.write(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

except Exception as e:
    st.error(f"Error: {e}")
