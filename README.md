# Datara — Bilingual Analytics Exploration

A Streamlit exploration of an English/Arabic data-analysis workspace, with dataset profiling, charts, and AI-assisted questions.

> **Provenance:** this repository is a fork of [InnovationSJ/ai-data-agent](https://github.com/InnovationSJ/ai-data-agent). The fork relationship is intentional. Upstream code remains credited to its original authors; this repository is not presented as wholly original work.

## Explore

- CSV/Excel upload and dataset preview
- Data-health and executive-summary views
- English/Arabic interface copy
- Plotly visualizations and AI-assisted follow-up questions

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml` locally:

```toml
OPENAI_API_KEY = "your-key-here"
```

Run `streamlit run app.py`. Never commit real credentials. The current app initializes its API client at startup, so configure the key before launching.

## Reading the code

| File | Purpose |
|---|---|
| `app.py` | Application, translations and interaction flow |
| `app_helpers.py` | Data/chart helper functions |
| `theme.py` | Styling |
| `requirements.txt` | Dependencies |

## Scope and limitations

This is an exploration, not evidence of production deployment or model training. AI requests send dataset information to an external model provider; use synthetic or non-sensitive data. Check the implementation and upstream diff before attributing specific features or assessing individual contributions.

A separate workspace prototype is documented in [data-ai-agent](https://github.com/cometeux/data-ai-agent).
