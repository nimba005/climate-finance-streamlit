import streamlit as st
from PyPDF2 import PdfReader
import plotly.express as px
import pandas as pd

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="🌍 Climate Finance Tool",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- Custom Theme & Styles ----------------
st.markdown(
    """
    <style>
    /* Main background */
    .stApp {
        background-color: #f9fafa;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1b4332;
        color: white;
    }
    section[data-testid="stSidebar"] .st-radio label {
        color: white !important;
        font-weight: 600;
    }

    /* Titles */
    h1, h2, h3 {
        color: #1b4332;
    }

    /* Buttons */
    div.stButton > button {
        background-color: #2d6a4f;
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.6em 1.2em;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #40916c;
        color: white;
    }

    /* Inputs */
    .stTextInput input, .stTextArea textarea {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Sidebar Navigation ----------------
st.sidebar.title("🌍 Climate Finance Tool")
menu = st.sidebar.radio("Navigate", ["🏠 Home", "📑 Upload Document", "📝 Take Survey", "🔐 Login"])

# ---------------- Helpers ----------------
def calc_percentages(total_budget: float, public: float, adaptation: float, mitigation: float):
    total_budget = float(total_budget or 0)
    public = float(public or 0)
    adaptation = float(adaptation or 0)
    mitigation = float(mitigation or 0)

    # Avoid div-by-zero
    if total_budget <= 0:
        return [0.0, 0.0, 0.0]

    vals = [public, adaptation, mitigation]
    return [(v / total_budget) * 100 for v in vals]

def bar_percent_chart(labels, percentages, title):
    df = pd.DataFrame({"Indicator": labels, "Percent": [round(p, 2) for p in percentages]})
    top = max([0] + percentages)
    max_y = 100 if top <= 100 else min(120, top + 10)  # cap a bit above top if >100
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
        uniformtext_minsize=10,
        uniformtext_mode="hide",
        margin=dict(t=60, r=20, l=20, b=40),
    )
    fig.update_yaxes(range=[0, max_y])
    return fig

# ---------------- Home Page ----------------
if menu == "🏠 Home":
    st.title("🌍 Climate Finance Indicator Tool")
    st.markdown(
        """
        Welcome to the **Climate Finance Indicator Tool**.  
        Use this tool to:
        - 📑 Upload and analyze budget documents (PDF)  
        - 📝 Take a survey to manually input budget values  
        - 📊 Visualize extracted indicators in charts  
        - 🔐 Login for secure access (future integration)  
        """
    )
    st.image(
        "https://images.unsplash.com/photo-1502786129293-79981df4e689",
        caption="Climate Action",
        use_container_width=True
    )

# ---------------- Upload Document Page ----------------
elif menu == "📑 Upload Document":
    st.header("📑 Upload a Budget Document")

    uploaded_file = st.file_uploader(
        "Upload a budget document (PDF, max 5MB)",
        type=["pdf"],
        key="pdf_file"
    )

    if uploaded_file:
        if uploaded_file.size > 5 * 1024 * 1024:  # 5MB size limit
            st.error("⚠️ File size exceeds 5MB. Please upload a smaller document.")
        else:
            # Read PDF text
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            st.success("✅ Document uploaded successfully")

            # -------- Auto-filled placeholders (replace with your extractor when ready) --------
            # These are pre-filled so the user can immediately calculate or edit if needed.
            st.subheader("📑 Extracted Values (from PDF)")
            col1, col2 = st.columns(2)
            with col1:
                total_budget_input = st.text_input(
                    "Total national budget",
                    value="1000000",  # auto-filled placeholder
                    key="pdf_total_budget"
                )
                public_invest_input = st.text_input(
                    "Public climate investment (total)",
                    value="200000",  # auto-filled placeholder
                    key="pdf_public_invest"
                )
            with col2:
                adapt_budget_input = st.text_input(
                    "Adaptation budget",
                    value="120000",  # auto-filled placeholder
                    key="pdf_adaptation"
                )
                mitig_budget_input = st.text_input(
                    "Mitigation budget",
                    value="80000",  # auto-filled placeholder
                    key="pdf_mitigation"
                )

            # -------- Chart visualization (Plotly) --------
            st.subheader("📊 Visualization of Indicators")
            labels = ["Public Investment", "Adaptation", "Mitigation"]

            percentages = calc_percentages(
                total_budget_input, public_invest_input, adapt_budget_input, mitig_budget_input
            )
            fig = bar_percent_chart(labels, percentages, "Climate Finance Indicators")
            st.plotly_chart(fig, use_container_width=True)

# ---------------- Take Survey Page ----------------
elif menu == "📝 Take Survey":
    st.header("📝 Survey / Manual Input")

    col1, col2 = st.columns(2)
    with col1:
        survey_total_budget = st.text_input("Total national budget", value="", key="survey_total_budget")
        survey_public_invest = st.text_input("Public climate investment (total)", value="", key="survey_public_invest")
    with col2:
        survey_adapt_budget = st.text_input("Adaptation budget", value="", key="survey_adaptation")
        survey_mitig_budget = st.text_input("Mitigation budget", value="", key="survey_mitigation")

    st.subheader("⚙️ Settings")
    currency = st.text_input("Currency (e.g. KES, USD, EUR)", value="KES", key="extra_currency")
    notes = st.text_area("Additional Notes", key="extra_notes")

    # Live chart preview as they type (nice UX)
    st.subheader("📊 Live Preview")
    survey_percentages = calc_percentages(
        survey_total_budget, survey_public_invest, survey_adapt_budget, survey_mitig_budget
    )
    fig_survey = bar_percent_chart(
        ["Public Investment", "Adaptation", "Mitigation"],
        survey_percentages,
        "Climate Finance Indicators (Survey)"
    )
    st.plotly_chart(fig_survey, use_container_width=True)

# ---------------- Login Page ----------------
elif menu == "🔐 Login":
    st.header("🔐 Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        if username == "admin" and password == "admin":  # Placeholder logic
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid username or password")
