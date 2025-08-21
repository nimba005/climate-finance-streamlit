# app.py
import io
import re
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PyPDF2 import PdfReader

st.set_page_config(page_title="Climate Finance Indicator Tool", layout="wide")

# ---------------------------
# Helpers: parsing & cleaning
# ---------------------------
def parse_number(s):
    """Parse a string like 'KES 12 billion' or '12,000,000' -> float (absolute amount)."""
    if s is None:
        return None
    s = str(s).strip()
    if s == "":
        return None

    # find numeric with possible unit word
    s = s.replace("\u00A0", " ")  # non-breaking space
    s = s.replace(",", "")
    # e.g. '12.5 billion', 'KES 12 billion', '12 000 000'
    m = re.search(r'([+-]?\d+(?:\.\d+)?)\s*(billion|bn|million|m|thousand|k)?', s, re.I)
    if not m:
        # fallback: extract any digits
        m2 = re.search(r'([0-9]+(?:\.[0-9]+)?)', s)
        if not m2:
            return None
        return float(m2.group(1))
    num = float(m.group(1))
    unit = m.group(2)
    if unit:
        unit = unit.lower()
        if "b" in unit:
            num *= 1_000_000_000
        elif "m" in unit and "mil" in unit or unit == "million" or unit == "m":
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

def find_values_in_text(text):
    """Try to find amounts for key indicators using keyword-near-number heuristics."""
    patterns = {
        "total_budget": r'(?:total national budget|total budget|national budget)[\s\S]{0,120}?([\-–\d\.,\s]*\d+(?:\.\d+)?(?:\s*(?:billion|million|bn|m|k|thousand))?)',
        "public_investment": r'(?:public (?:investment|expenditure|spend).*climate|public investment in climate|public climate investment)[\s\S]{0,120}?([\-–\d\.,\s]*\d+(?:\.\d+)?(?:\s*(?:billion|million|bn|m|k|thousand))?)',
        "adaptation_budget": r'(?:climate adaptation budget|adaptation budget|budget for adaptation|adaptation allocation)[\s\S]{0,120}?([\-–\d\.,\s]*\d+(?:\.\d+)?(?:\s*(?:billion|million|bn|m|k|thousand))?)',
        "previous_adaptation": r'(?:previous year|previous|in \d{4})[\s\S]{0,80}?(?:adaptation budget|adaptation)[\s\S]{0,40}?([\-–\d\.,\s]*\d+(?:\.\d+)?(?:\s*(?:billion|million|bn|m|k|thousand))?)',
        "private_investment": r'(?:private sector (?:investment|contributed|mobilized)|private investment)[\s\S]{0,120}?([\-–\d\.,\s]*\d+(?:\.\d+)?(?:\s*(?:billion|million|bn|m|k|thousand))?)'
    }

    found = {}
    for key, pat in patterns.items():
        m = re.search(pat, text, re.I)
        if m:
            raw = m.group(1).strip()
            val = parse_number(raw)
            found[key] = {"raw": raw, "value": val}
        else:
            found[key] = {"raw": None, "value": None}

    # try to detect currency
    cur_m = re.search(r'\b(KES|KSh|USD|EUR|GBP|KES\b)\b', text, re.I)
    found["currency"] = cur_m.group(1) if cur_m else None

    return found

# ---------------------------
# Calculation logic
# ---------------------------
def calculate_indicators(
    *,
    total_budget,
    public_investment,
    adaptation_budget,
    previous_adaptation_budget,
    private_investment,
    sector_breakdown_dict=None
):
    # Ensure floats
    total_budget = float(total_budget) if total_budget not in (None, "", 0) else None
    public_investment = float(public_investment) if public_investment not in (None, "") else 0.0
    adaptation_budget = float(adaptation_budget) if adaptation_budget not in (None, "") else 0.0
    previous_adaptation_budget = float(previous_adaptation_budget) if previous_adaptation_budget not in (None, "") else None
    private_investment = float(private_investment) if private_investment not in (None, "") else 0.0

    # Indicators
    pct_adaptation_of_budget = None
    if total_budget and total_budget > 0:
        pct_adaptation_of_budget = (adaptation_budget / total_budget) * 100

    yoy_adaptation_increase_pct = None
    if previous_adaptation_budget and previous_adaptation_budget > 0:
        yoy_adaptation_increase_pct = ((adaptation_budget - previous_adaptation_budget) / previous_adaptation_budget) * 100

    total_climate_investment = public_investment + private_investment

    # Sector breakdown proportions (percent of total climate investment)
    sector_percent = {}
    if sector_breakdown_dict:
        total_sector = sum([v for v in sector_breakdown_dict.values() if v is not None])
        for k, v in sector_breakdown_dict.items():
            if total_sector and total_sector > 0:
                sector_percent[k] = (v / total_sector) * 100
            else:
                sector_percent[k] = None

    return {
        "total_public_investment": public_investment,
        "pct_adaptation_of_budget": pct_adaptation_of_budget,
        "yoy_adaptation_increase_pct": yoy_adaptation_increase_pct,
        "private_sector_investment": private_investment,
        "total_climate_investment": total_climate_investment,
        "sector_percent": sector_percent
    }

# ---------------------------
# UI
# ---------------------------
st.title("🌍 Climate Finance Indicator Tool (Single-file)")

st.markdown("""
Upload a **CSV / Excel** (preferred) or **PDF** budget document, or use the **Survey** tab to enter numbers manually.
The app computes:
1. Total public investment in climate initiatives  
2. % of national budget allocated to climate adaptation  
3. Year-on-year increase for climate adaptation budget  
4. Private sector investment mobilized  
5. Funding allocation by sector  
""")

tab1, tab2 = st.tabs(["Upload Document", "Survey / Manual Input"])

# -------- Upload Document Tab --------
with tab1:
    st.header("Upload a document")
    st.markdown("Supported: CSV, XLSX, PDF. If you upload a **CSV/XLSX**, it should contain columns (case-insensitive): "
                "`Year`, `Total_Budget`, `Public_Climate_Investment`, `Climate_Adaptation_Budget`, `Previous_Year_Adaptation_Budget`, `Private_Sector_Investment`."
                " For sector breakdown, upload a separate CSV with `Sector,Amount` or paste in the Sector input below.")

    uploaded_file = st.file_uploader("Upload CSV / XLSX / PDF", type=["csv", "xlsx", "pdf"])

    # optional sector breakdown file
    sector_file = st.file_uploader("Optional: Upload sector breakdown CSV (Sector,Amount)", type=["csv"])

    extracted_values = {}
    budget_df = None

    if uploaded_file:
        fname = uploaded_file.name.lower()
        if fname.endswith(".csv"):
            budget_df = pd.read_csv(uploaded_file)
        elif fname.endswith(".xlsx") or fname.endswith(".xls"):
            budget_df = pd.read_excel(uploaded_file)
        elif fname.endswith(".pdf"):
            # try to extract text heuristically
            raw_bytes = uploaded_file.read()
            text = extract_text_from_pdf(io.BytesIO(raw_bytes))
            st.subheader("Extracted text (first 2000 chars)")
            st.text(text[:2000])
            extracted_values = find_values_in_text(text)

            st.markdown("Detected values (you can edit them):")
            # provide editable fields prefilled with detected values
            currency_detected = extracted_values.get("currency") or ""
            col1, col2 = st.columns(2)
            with col1:
                total_budget_input = st.text_input(
                    "Total national budget",
                    value=str(extracted_values.get("total_budget", {}).get("raw") or "")
                )
                public_invest_input = st.text_input(
                    "Public climate investment (total)",
                    value=str(extracted_values.get("public_investment", {}).get("raw") or "")
                )
                adaptation_input = st.text_input(
                    "Climate adaptation budget (current)",
                    value=str(extracted_values.get("adaptation_budget", {}).get("raw") or "")
                )
            with col2:
                prev_adapt_input = st.text_input(
                    "Previous year adaptation budget",
                    value=str(extracted_values.get("previous_adaptation", {}).get("raw") or "")
                )
                private_input = st.text_input(
                    "Private sector investment mobilized",
                    value=str(extracted_values.get("private_investment", {}).get("raw") or "")
                )
                currency_input = st.text_input("Currency (detected)", value=currency_detected)

            # parse numbers when user clicks calculate
            if st.button("Calculate from PDF inputs"):
                tb = parse_number(total_budget_input)
                pub = parse_number(public_invest_input)
                adapt = parse_number(adaptation_input)
                prev = parse_number(prev_adapt_input)
                priv = parse_number(private_input)

                # sector file parsing (if uploaded)
                sector_dict = {}
                if sector_file:
                    dfsec = pd.read_csv(sector_file)
                    for _, r in dfsec.iterrows():
                        k = str(r.iloc[0])
                        v = parse_number(r.iloc[1])
                        sector_dict[k] = v or 0.0

                results = calculate_indicators(
                    total_budget=tb,
                    public_investment=pub,
                    adaptation_budget=adapt,
                    previous_adaptation_budget=prev,
                    private_investment=priv,
                    sector_breakdown_dict=sector_dict if sector_dict else None
                )

                st.subheader("Results")
                st.write(results)
                # show charts
                fig1, ax1 = plt.subplots()
                ax1.bar(['Public', 'Private'], [results['total_public_investment'] or 0, results['private_sector_investment'] or 0])
                ax1.set_ylabel('Amount')
                st.pyplot(fig1)

                if results['sector_percent']:
                    fig2, ax2 = plt.subplots()
                    labels = list(results['sector_percent'].keys())
                    sizes = [v for v in results['sector_percent'].values()]
                    ax2.pie(sizes, labels=labels, autopct='%1.1f%%')
                    st.pyplot(fig2)

        # If we have a dataframe from CSV/XLSX, show it and compute
        if budget_df is not None:
            st.subheader("Uploaded table (preview)")
            st.dataframe(budget_df.head())

            # Normalise column names to lowercase without spaces
            dfc = budget_df.copy()
            dfc.columns = [str(c).strip().lower().replace(" ", "_") for c in dfc.columns]

            # Accept multiple rows (years). Required columns mapping:
            mapping = {
                "year": ["year"],
                "total_budget": ["total_budget", "total_national_budget", "total budget"],
                "public_investment": ["public_climate_investment", "public_investment_climate", "public_climate_investment_total", "public_investment"],
                "adaptation_budget": ["climate_adaptation_budget", "adaptation_budget", "adaptation"],
                "previous_adaptation": ["previous_year_adaptation_budget", "previous_adaptation_budget", "prev_adaptation", "previous_adaptation"],
                "private_investment": ["private_sector_investment", "private_investment", "private"]
            }

            # helper to get first matching col
            def pick_col(keys):
                for k in keys:
                    if k in dfc.columns:
                        return k
                return None

            cols_found = {name: pick_col(cands) for name, cands in mapping.items()}

            if cols_found["total_budget"] is None:
                st.error("CSV/XLSX must contain a 'Total_Budget' (or similar) column.")
            else:
                # Build results per-row
                rows = []
                for idx, r in dfc.iterrows():
                    year = r.get(cols_found["year"]) if cols_found["year"] else None
                    total_budget_val = parse_number(r.get(cols_found["total_budget"]))
                    pub_val = parse_number(r.get(cols_found["public_investment"])) if cols_found["public_investment"] else 0.0
                    adapt_val = parse_number(r.get(cols_found["adaptation_budget"])) if cols_found["adaptation_budget"] else 0.0
                    prev_val = parse_number(r.get(cols_found["previous_adaptation"])) if cols_found["previous_adaptation"] else None
                    priv_val = parse_number(r.get(cols_found["private_investment"])) if cols_found["private_investment"] else 0.0

                    res = calculate_indicators(
                        total_budget=total_budget_val,
                        public_investment=pub_val,
                        adaptation_budget=adapt_val,
                        previous_adaptation_budget=prev_val,
                        private_investment=priv_val,
                        sector_breakdown_dict=None
                    )
                    rows.append({
                        "year": year,
                        "total_budget": total_budget_val,
                        "public_investment": pub_val,
                        "adaptation_budget": adapt_val,
                        "previous_adaptation_budget": prev_val,
                        "private_investment": priv_val,
                        "pct_adaptation_of_budget": res["pct_adaptation_of_budget"],
                        "yoy_adaptation_increase_pct": res["yoy_adaptation_increase_pct"],
                        "total_climate_investment": res["total_climate_investment"]
                    })

                results_df = pd.DataFrame(rows)
                st.subheader("Computed Indicators (per row)")
                st.dataframe(results_df)

                # Plot: % adaptation across years if year present
                if "year" in results_df.columns and results_df["year"].notnull().any():
                    fig3, ax3 = plt.subplots()
                    plot_df = results_df.dropna(subset=["pct_adaptation_of_budget"])
                    if not plot_df.empty:
                        ax3.plot(plot_df["year"].astype(str), plot_df["pct_adaptation_of_budget"], marker='o')
                        ax3.set_title("% of National Budget Allocated to Climate Adaptation")
                        ax3.set_ylabel("%")
                        ax3.set_xlabel("Year")
                        st.pyplot(fig3)

                # Bar: public vs private for latest year (last row)
                last = results_df.iloc[-1]
                fig4, ax4 = plt.subplots()
                ax4.bar(["Public", "Private"], [last["public_investment"] or 0, last["private_investment"] or 0])
                ax4.set_ylabel("Amount")
                ax4.set_title(f"Public vs Private (Year: {last['year']})")
                st.pyplot(fig4)

                # allow download
                csv_out = results_df.to_csv(index=False)
                st.download_button("Download results as CSV", csv_out, file_name="climate_indicators_results.csv", mime="text/csv")

# -------- Survey / Manual Input Tab --------
with tab2:
    st.header("Survey / Manual Input")
    st.markdown("If you don't have a document, enter values below. You can also paste sector breakdown CSV lines (Sector,Amount).")
    col1, col2 = st.columns(2)

    with col1:
        year = st.text_input("Year", value=str(pd.Timestamp.now().year))
        currency = st.text_input("Currency (e.g., KES, USD)", value="KES")
        total_budget_in = st.text_input("Total national budget (e.g., 400000000000 or '400 billion')", "")
        public_invest_in = st.text_input("Public climate investment (total)", "")
        adaptation_in = st.text_input("Climate adaptation budget (current year)", "")
    with col2:
        prev_adapt_in = st.text_input("Previous year adaptation budget", "")
        private_invest_in = st.text_input("Private sector investment mobilized", "")
        sector_text = st.text_area("Sector breakdown (paste CSV lines: Sector,Amount). Example:\nAgriculture,50000000\nWater,30000000", height=150)

    if st.button("Calculate from survey"):
        tb = parse_number(total_budget_in)
        pub = parse_number(public_invest_in)
        adapt = parse_number(adaptation_in)
        prev = parse_number(prev_adapt_in)
        priv = parse_number(private_invest_in)

        # parse sector_text
        sector_dict = {}
        if sector_text:
            for line in sector_text.splitlines():
                if not line.strip(): 
                    continue
                parts = line.split(",")
                if len(parts) >= 2:
                    k = parts[0].strip()
                    v = parse_number(parts[1].strip())
                    if v is None:
                        v = 0.0
                    sector_dict[k] = v

        results = calculate_indicators(
            total_budget=tb,
            public_investment=pub,
            adaptation_budget=adapt,
            previous_adaptation_budget=prev,
            private_investment=priv,
            sector_breakdown_dict=sector_dict if sector_dict else None
        )

        st.subheader("Results")
        st.write(results)

        # charts
        fig5, ax5 = plt.subplots()
        ax5.bar(['Public', 'Private'], [results['total_public_investment'] or 0, results['private_sector_investment'] or 0])
        ax5.set_ylabel('Amount')
        st.pyplot(fig5)

        if results['sector_percent']:
            fig6, ax6 = plt.subplots()
            labels = list(results['sector_percent'].keys())
            sizes = [v for v in results['sector_percent'].values()]
            ax6.pie(sizes, labels=labels, autopct='%1.1f%%')
            st.pyplot(fig6)

        # allow CSV download of a small summary
        summary = {
            "year": [year],
            "currency": [currency],
            "total_budget": [tb],
            "public_investment": [pub],
            "adaptation_budget": [adapt],
            "previous_adaptation_budget": [prev],
            "private_investment": [priv],
            "pct_adaptation_of_budget": [results['pct_adaptation_of_budget']],
            "yoy_adaptation_increase_pct": [results['yoy_adaptation_increase_pct']],
            "total_climate_investment": [results['total_climate_investment']]
        }
        df_summary = pd.DataFrame(summary)
        st.download_button("Download summary CSV", df_summary.to_csv(index=False), file_name="survey_summary.csv", mime="text/csv")
