# Pure data/chart helpers – no Streamlit. Used by app.py and test_app.py.
import json
import pandas as pd
import plotly.express as px


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
    avg_null = sum(profile["missing_pct"].values()) / len(profile["missing_pct"]) if profile["missing_pct"] else 0
    dup_penalty = min(10, profile["duplicate_rows"] // 100)
    profile["readiness_pct"] = max(0, min(100, round(100 - avg_null - dup_penalty)))
    usable = sum(1 for c, p in profile["missing_pct"].items() if p < 50)
    profile["usable_columns"] = usable
    profile["integrity_score"] = round(100 * usable / len(df.columns)) if len(df.columns) else 0
    profile["recommended_measures"] = [c for c, t in profile["column_types"].items() if t == "numeric"][:5]
    return profile


def parse_analysis_json(text):
    """Extract and parse JSON from model output with fallbacks."""
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
        "summary": {
            "overview": "Analysis could not be parsed. Please try again.",
            "key_insights": [],
            "recommendations": [],
            "final_summary": "",
        },
        "charts": [],
    }


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


DATARA_CHART_COLORS = ["#D4ABFE", "#a78bfa", "#8b5cf6", "#c084fc", "#7c3aed", "#6d28d9"]


def render_chart_fig(df, chart, is_dark):
    chart_type = chart.get("chart_type", "bar")
    x_column = chart.get("x_column")
    y_column = chart.get("y_column")
    aggregation = chart.get("aggregation", "sum")
    if not x_column:
        return None
    if x_column not in df.columns:
        return None
    if aggregation != "count" and (not y_column or y_column not in df.columns):
        return None
    data, final_y = prepare_chart_data(df, x_column, y_column, aggregation)
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
            plot_bgcolor="#221b32",
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
            legend=dict(bgcolor="rgba(22, 17, 33, 0.9)", font=dict(color="#9B92AB", size=11), bordercolor="rgba(255,255,255,0.08)"),
            hoverlabel=dict(bgcolor="#221b32", font=dict(color="#ffffff", size=12), bordercolor="rgba(212, 171, 254, 0.3)"),
            modebar=dict(bgcolor="rgba(22, 17, 33, 0.8)", color="#9B92AB", activecolor="#D4ABFE"),
        )
        if chart_type == "pie":
            fig.update_traces(marker=dict(colors=DATARA_CHART_COLORS))
        else:
            fig.update_traces(marker=dict(color=DATARA_CHART_COLORS[0]), selector=dict(type="bar"))
            fig.update_traces(line=dict(color=DATARA_CHART_COLORS[0]), selector=dict(type="scatter", mode="lines"))
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
