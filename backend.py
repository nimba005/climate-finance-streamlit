from PyPDF2 import PdfReader
import pandas as pd
import plotly.express as px

# ---- PDF Extraction ----
def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

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

# ---- Chart Function ----
def bar_percent_chart(labels, percentages, title):
    df = pd.DataFrame({"Indicator": labels, "Percent": [round(p, 2) for p in percentages]})
    top = max([0] + percentages)
    max_y = 100 if top <= 100 else min(120, top + 10)
    fig = px.bar(
        df,
        x="Indicator",
        y="Percent",
        text="Percent",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        title=title,
        yaxis_title="Percentage of Total Budget (%)",
        xaxis_title="",
        template="plotly_white",
        margin=dict(t=60, r=20, l=20, b=40),
    )
    fig.update_yaxes(range=[0, max_y])
    return fig
