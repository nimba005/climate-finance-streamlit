# backend.py
import fitz  # PyMuPDF (better than PyPDF2 for large PDFs)
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# ---- CMAT Indicators Definition ----
CMAT_INDICATORS = {
    "Finance": [
        "Total Budget",
        "Public",
        "Adaptation",
        "Mitigation"
    ],
    "Sectors": [
        "Energy",
        "Agriculture",
        "Health",
        "Transport",
        "Water"
    ],
}

# ---- Country-Specific Thresholds ----
COUNTRY_THRESHOLDS = {
    "Zambia": {
        "Public": 50.0,       # 50% of total budget
        "Adaptation": 5.0,    # 5% of total budget
        "Mitigation": 5.0,    # 5% of total budget
    },
    "Kenya": {
        "Public": 45.0,
        "Adaptation": 7.0,
        "Mitigation": 6.0,
    },
    "Uganda": {
        "Public": 40.0,
        "Adaptation": 6.0,
        "Mitigation": 4.0,
    },
}

DEFAULT_THRESHOLDS = {
    "Public": 50.0,
    "Adaptation": 5.0,
    "Mitigation": 5.0,
}

# ---- PDF Extraction ----
def extract_text_from_pdf(uploaded_file, max_pages=None):
    text = []
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page_num, page in enumerate(doc):
            if max_pages and page_num >= max_pages:
                break
            text.append(page.get_text("text") or "")
    return "\n".join(text)

# ---- Extract Numeric Values ----
def extract_numbers_from_text(text, keywords=None):
    results = {}
    if not text:
        return results

    if not keywords:
        keywords = ["total budget", "public", "adaptation", "mitigation"]

    clean_text = text.lower()
    for key in keywords:
        pattern = rf"{key}[^0-9]*([\d,\.]+)"
        match = re.search(pattern, clean_text)
        if match:
            num_str = match.group(1).replace(",", "")
            try:
                results[key] = float(num_str)
            except ValueError:
                results[key] = None
    return results

# ---- Map Extracted Values to Survey Defaults ----
def prepare_survey_defaults(extracted_numbers):
    return {
        "total_budget": extracted_numbers.get("total budget", None),
        "public": extracted_numbers.get("public", None),
        "adaptation": extracted_numbers.get("adaptation", None),
        "mitigation": extracted_numbers.get("mitigation", None),
    }

# ---- Percentage Calculations ----
def calc_percentages(total_budget: float, public: float, adaptation: float, mitigation: float):
    total_budget = float(total_budget or 0)
    public = float(public or 0)
    adaptation = float(adaptation or 0)
    mitigation = float(mitigation or 0)

    if total_budget <= 0:
        return [0.0, 0.0, 0.0]

    vals = [public, adaptation, mitigation]
    return [(v / total_budget) * 100 for v in vals]

# ---- Simple Bar Chart ----
def bar_chart(data_dict, title):
    df = pd.DataFrame({"Indicator": list(data_dict.keys()), "Value": list(data_dict.values())})
    fig = px.bar(df, x="Indicator", y="Value", text="Value", title=title, template="plotly_white")
    fig.update_traces(texttemplate="%{text}", textposition="outside")
    fig.update_layout(margin=dict(t=60, r=20, l=20, b=40))
    return fig

# ---- Radar Chart ----
def radar_chart(data_dict, title):
    indicators = list(data_dict.keys())
    values = list(data_dict.values())

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values, theta=indicators, fill="toself", name="Indicators"))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=False,
        title=title,
        template="plotly_white"
    )
    return fig

# ---- Bar Chart with Country Targets ----
def bar_percent_chart(labels, percentages, title, country="Default"):
    thresholds = COUNTRY_THRESHOLDS.get(country, DEFAULT_THRESHOLDS)

    df = pd.DataFrame({"Indicator": labels, "Percent": [round(p, 2) for p in percentages]})

    colors = []
    for label, val in zip(df["Indicator"], df["Percent"]):
        threshold = thresholds.get(label, None)
        if threshold is not None:
            colors.append("green" if val >= threshold else "red")
        else:
            colors.append("gray")

    top = max([0] + percentages)
    max_y = 100 if top <= 100 else min(120, top + 10)

    fig = px.bar(df, x="Indicator", y="Percent", text="Percent", color=colors, color_discrete_map="identity")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        title=title,
        yaxis_title="Percentage of Total Budget (%)",
        xaxis_title="",
        template="plotly_white",
        margin=dict(t=60, r=20, l=20, b=40),
        showlegend=False
    )
    fig.update_yaxes(range=[0, max_y])
    return fig
