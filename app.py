import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from openai import OpenAI

st.set_page_config(page_title="AI Data Analyst Agent", layout="wide")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("AI Data Analyst Agent")
st.write("Upload a CSV or Excel file and ask questions about your data.")

uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

user_question = st.text_input(
    "Ask a question about your data",
    placeholder="Example: Create a bar chart of total sales by month"
)

def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)

def ask_model(df, question):

    columns = list(df.columns)
    sample_rows = df.head(5).to_dict(orient="records")

    prompt = f"""
You are a helpful data analyst.

Columns:
{columns}

Sample rows:
{sample_rows}

User question:
{question}

Return ONLY JSON in this format:

{{
"answer": "short explanation",
"chart_needed": true,
"chart_type": "bar",
"x_column": "column name",
"y_column": "column name",
"aggregation": "sum"
}}

chart_type must be:
bar, line, pie, scatter
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return json.loads(response.output_text)

def create_chart(df, chart_type, x_column, y_column, aggregation):

    data = df.copy()

    if aggregation == "sum":
        data = data.groupby(x_column, as_index=False)[y_column].sum()

    if aggregation == "mean":
        data = data.groupby(x_column, as_index=False)[y_column].mean()

    fig, ax = plt.subplots()

    if chart_type == "bar":
        ax.bar(data[x_column], data[y_column])

    if chart_type == "line":
        ax.plot(data[x_column], data[y_column])

    if chart_type == "scatter":
        ax.scatter(data[x_column], data[y_column])

    if chart_type == "pie":
        ax.pie(data[y_column], labels=data[x_column], autopct="%1.1f%%")

    st.pyplot(fig)

if uploaded_file:

    df = load_data(uploaded_file)

    st.subheader("Data preview")
    st.dataframe(df.head())

    if st.button("Run Agent"):

        result = ask_model(df, user_question)

        st.subheader("AI Answer")
        st.write(result["answer"])

        if result["chart_needed"]:
            create_chart(
                df,
                result["chart_type"],
                result["x_column"],
                result["y_column"],
                result["aggregation"]
            )