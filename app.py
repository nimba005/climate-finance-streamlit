# app.py
import io
import re
import streamlit as st
import matplotlib.pyplot as plt
from PyPDF2 import PdfReader

st.set_page_config(page_title="Climate Finance Indicator Tool", layout="wide")

# ---------------------------
# Helpers
# ---------------------------
def parse_number(s):
    """Parse a string like 'KES 12 billion' or '12,000,000' -> float (absolute amount)."""
    if s is None or s == "":
        return None
    s = str(s).replace(",", "").strip()
    m = re.search(r'([+-]?\d+(?:\.\d+)?)\s*(billion|bn|million|m|thousand|k)?', s, re.I)
    if not m:
        return None
    num = float(m.group(1))
    unit = m.group(2)
    if unit:
        unit = unit.lower()
        if "b" in unit:
            num *= 1_000_000_000
        elif "m" in unit:
            num *= 1_000_000
        elif unit in ("k", "thousand"):
            num *= 1_000
    return num

def extract_text_from_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = []
        for p in reader.pages:
            txt = p.extract_text()
            if txt:
                text.append(txt)
        return "\n".join(text)
    except Exception as e:
        st.error(f"PDF parsing failed: {e}")
        return ""

def extract_values_from_text(text):
    """Search for numbers near key terms."""
    patterns = {
        "total_budget": r"(?:total national budget|total budget|national budget)[\s\S]{0,50}?([\d,\.]+\s*(?:billion|million|m|k|thousand)?)",
        "public_investment": r"(?:public climate investment|public investment)[\s\S]{0,50}?([\d,\.]+\s*(?:billion|million|m|k|thousand)?)",
        "adaptation_budget": r"(?:climate adaptation budget|adaptation budget)[\s\S]{0,50}?([\d,\.]+\s*(?:billion|million|m|k|thousand)?)",
        "private_investment": r"(?:private sector investment|private investment)[\s\S]{0,50}?([\d,\.]+\s*(?:billion|million|m|k|thousand)?)"
    }
    extracted = {}
    for key, pat in patterns.items():
        m = re.search(pat, text, re.I)
        if m:
            extracted[key] = m.group(1)
        else:
            extracted[key] = ""
    return extracted

def calculate_indicators(total_budget, public_investment, adaptation_budget, private_investment):
    """Return indicator values"""
    total_budget = float(total_budget) if total_budget not in (None, "", 0) else None
    public_investment = float(public_investment) if public_investment not in (None, "") else 0.0
    adaptation_budget = float(adaptation_budget) if adaptation_budget not in (None, "") else 0.0
    private_investment = float(private_investment) if private_investment not in (None, "") else 0.0

    pct_adaptation_of_budget = (adaptation_budget / total_budget * 100) if total_budget else None
    total_climate_investment = public_investment + private_investment
    pct_public = (public_investment / total_climate_investment * 100) if total_climate_investment else None
    pct_private = (private_investment / total_climate_investment * 100) if total_climate_investment else None

    return {
        "total_budget": total_budget,
        "public_investment": public_investment,
        "adaptation_budget": adaptation_budget,
        "private_investment": private_investment,
        "pct_adaptation_of_budget": pct_adaptation_of_budget,
        "total_climate_investment": total_climate_investment,
        "pct_public": pct_public,
        "pct_private": pct_private
    }

# ---------------------------
# UI
# ---------------------------
st.title("🌍 Climate Finance Indicator Tool")
tab1, tab2 = st.tabs(["Upload Document", "Survey / Manual Input"])

# -------- Upload Document Tab --------
with tab1:
    st.header("Upload a budget document")
    uploaded_file = st.file_uploader("Upload PDF (max 5MB)", type=["pdf"], key="pdf_file")

    if uploaded_file:
        if uploaded_file.size > 5 * 1024 * 1024:
            st.error("⚠️ File size exceeds 5MB. Please upload a smaller document.")
        else:
            text = extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
            st.subheader("Extracted Text Preview (first 1000 chars)")
            st.text(text[:1000])

            # Extract numbers from PDF text automatically
            extracted_values = extract_values_from_text(text)

            total_budget_input = st.text_input(
                "Total national budget",
                value=extracted_values.get("total_budget", ""),
                key="pdf_total_budget"
            )
            public_invest_input = st.text_input(
                "Public climate investment",
                value=extracted_values.get("public_investment", ""),
                key="pdf_public_invest"
            )
            adaptation_input = st.text_input(
                "Adaptation budget",
                value=extracted_values.get("adaptation_budget", ""),
                key="pdf_adaptation"
            )
            private_input = st.text_input(
                "Private sector investment",
                value=extracted_values.get("private_investment", ""),
                key="pdf_private_invest"
            )

            if st.button("Calculate Indicators from Document", key="calc_pdf"):
                tb = parse_number(total_budget_input)
                pub = parse_number(public_invest_input)
                adapt = parse_number(adaptation_input)
                priv = parse_number(private_input)

                results = calculate_indicators(tb, pub, adapt, priv)

                st.subheader("📊 Results")
                st.write(results)

                # Plot chart
                fig, ax = plt.subplots()
                labels = ['Public', 'Private', 'Adaptation of Budget']
                values = [
                    results['pct_public'] or 0,
                    results['pct_private'] or 0,
                    results['pct_adaptation_of_budget'] or 0
                ]
                ax.bar(labels, values, color=['skyblue', 'orange', 'green'])
                ax.set_ylabel("Percentage (%)")
                ax.set_title("Climate Finance Indicators in Percentage")
                st.pyplot(fig)

# -------- Survey / Manual Input Tab --------
with tab2:
    st.header("Survey / Manual Input")

    total_budget_in = st.text_input("Total national budget", key="survey_total_budget")
    public_invest_in = st.text_input("Public climate investment", key="survey_public_invest")
    adaptation_in = st.text_input("Adaptation budget", key="survey_adaptation")
    private_invest_in = st.text_input("Private sector investment", key="survey_private_invest")

    if st.button("Calculate Indicators from Survey", key="calc_survey"):
        tb = parse_number(total_budget_in)
        pub = parse_number(public_invest_in)
        adapt = parse_number(adaptation_in)
        priv = parse_number(private_invest_in)

        results = calculate_indicators(tb, pub, adapt, priv)

        st.subheader("📊 Results")
        st.write(results)

        fig, ax = plt.subplots()
        labels = ['Public', 'Private', 'Adaptation of Budget']
        values = [
            results['pct_public'] or 0,
            results['pct_private'] or 0,
            results['pct_adaptation_of_budget'] or 0
        ]
        ax.bar(labels, values, color=['skyblue', 'orange', 'green'])
        ax.set_ylabel("Percentage (%)")
        ax.set_title("Climate Finance Indicators in Percentage")
        st.pyplot(fig)
