# backend.py
import fitz  # PyMuPDF (faster and better for large PDFs)
import pandas as pd
import plotly.express as px
import re

# ---- PDF Extraction (robust + scalable) ----
def extract_text_from_pdf(uploaded_file, max_pages=None):
    """
    Extract text from a PDF file using PyMuPDF.
    Handles very large files efficiently by streaming page by page.
    """
    text = []
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        total_pages = len(doc)
        for page_num, page in enumerate(doc):
            if max_pages and page_num >= max_pages:
                break
            page_text = page.get_text("text") or ""
            text.append(page_text)
    return "\n".join(text)

# ---- Extract Numeric Values (optional helper) ----
def extract_numbers_from_text(text, keywords=None):
    """
    Simple regex-based extractor for financial figures linked to keywords.
    Example: 'Total budget: 5,000,000 USD'
    """
    results = {}
    if not text:
        return results

    if not keywords:
        keywords = ["total budget", "public", "adaptation", "mitigation"]

    # Normalize text
    clean_text = text.lower()

    for key in keywords:
        # Find line with keyword
        pattern = rf"{key}[^0-9]*([\d,\.]+)"
        match = re.search(pattern, clean_text)
        if match:
            num_str = match.group(1).replace(",", "")
            try:
                results[key] = float(num_str)
            except ValueError:
                results[key] = None
    return results

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
