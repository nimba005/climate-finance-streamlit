import streamlit as st
import os
import json
from backend import calc_percentages, bar_percent_chart, extract_text_from_pdf

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="🌍 Climate Finance Tool",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- Custom Theme & Styles ----------------
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------- Helper Functions ----------------
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# ---------------- Session Setup ----------------
if "users" not in st.session_state:
    st.session_state.users = load_users()
    if not st.session_state.users:
        st.session_state.users = {"admin": "admin"}  # default

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ---------------- Sidebar Navigation ----------------
st.sidebar.title("🌍 Climate Finance Tool")
menu = st.sidebar.radio("Navigate", ["🏠 Home", "📑 Upload Document", "📝 Take Survey", "🔐 Login"])

# ---------------- Persistent Top Header (Dynamic Page Title) ----------------
page_titles = {
    "🏠 Home": "Home",
    "📑 Upload Document": "Upload Document",
    "📝 Take Survey": "Survey",
    "🔐 Login": "Login / Sign Up"
}
current_page = page_titles.get(menu, "")

st.markdown(f"""
<div class="top-header">
    <div class="header-left">
        <h2>🌍 Climate Monitoring & Accountability Tool (CMAT)</h2>
        <p>AI-enabled web tool for parliamentary oversight of climate action and individual country monitoring</p>
        <h4>Current Page: {current_page}</h4>
    </div>
    <div class="header-right">
        {"Logged in as: <strong>" + st.session_state.current_user + "</strong>" if st.session_state.logged_in else "Not logged in"}
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- Home Page ----------------
if menu == "🏠 Home":
    st.subheader("Welcome to the Climate Finance Indicator Tool")
    st.markdown(
        """
        Use this tool to:
        - 📑 Upload and analyze budget documents (PDF)  
        - 📝 Take a survey to manually input budget values  
        - 📊 Visualize extracted indicators in charts  
        - 🔐 Login for secure access  
        """
    )
    st.image(
        "https://images.unsplash.com/photo-1502786129293-79981df4e689",
        caption="Climate Action",
        use_container_width=True
    )

# ---------------- Upload Document Page ----------------
elif menu == "📑 Upload Document":
    if not st.session_state.logged_in:
        st.warning("🔐 Please login to access this page.")
        st.stop()

    st.header("📑 Upload a Budget Document")

    uploaded_file = st.file_uploader(
        "Upload a budget document (PDF, max 5MB)",
        type=["pdf"],
        key="pdf_file"
    )

    if uploaded_file:
        if uploaded_file.size > 5 * 1024 * 1024:
            st.error("⚠️ File size exceeds 5MB. Please upload a smaller document.")
        else:
            text = extract_text_from_pdf(uploaded_file)
            st.success("✅ Document uploaded successfully")

            st.subheader("📑 Extracted Values (from PDF)")
            col1, col2 = st.columns(2)
            with col1:
                total_budget_input = st.text_input("Total national budget", value="1000000", key="pdf_total_budget")
                public_invest_input = st.text_input("Public climate investment (total)", value="200000", key="pdf_public_invest")
            with col2:
                adapt_budget_input = st.text_input("Adaptation budget", value="120000", key="pdf_adaptation")
                mitig_budget_input = st.text_input("Mitigation budget", value="80000", key="pdf_mitigation")

            st.subheader("📊 Visualization of Indicators")
            labels = ["Public Investment", "Adaptation", "Mitigation"]
            percentages = calc_percentages(total_budget_input, public_invest_input, adapt_budget_input, mitig_budget_input)
            fig = bar_percent_chart(labels, percentages, "Climate Finance Indicators")
            st.plotly_chart(fig, use_container_width=True)

# ---------------- Take Survey Page ----------------
elif menu == "📝 Take Survey":
    if not st.session_state.logged_in:
        st.warning("🔐 Please login to access this page.")
        st.stop()

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

    st.subheader("📊 Live Preview")
    survey_percentages = calc_percentages(survey_total_budget, survey_public_invest, survey_adapt_budget, survey_mitig_budget)
    fig_survey = bar_percent_chart(["Public Investment", "Adaptation", "Mitigation"], survey_percentages, "Climate Finance Indicators (Survey)")
    st.plotly_chart(fig_survey, use_container_width=True)

# ---------------- Login / Sign Up Page ----------------
elif menu == "🔐 Login":
    st.header("🔐 Login / Sign Up")

    if st.session_state.logged_in:
        st.success(f"✅ Welcome, {st.session_state.current_user}!")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.info("You have been logged out.")
            st.experimental_rerun()
    else:
        option = st.radio("Select Option", ["Login", "Sign Up"], key="auth_option")

        if option == "Login":
            st.subheader("Login to Your Account")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")

            if st.button("Login"):
                if username in st.session_state.users and st.session_state.users[username] == password:
                    st.success(f"✅ Welcome back, {username}!")
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.experimental_rerun()
                else:
                    st.error("❌ Invalid username or password")

        elif option == "Sign Up":
            st.subheader("Create a New Account")
            new_username = st.text_input("Choose a Username", key="signup_user")
            new_password = st.text_input("Choose a Password", type="password", key="signup_pass")

            if st.button("Sign Up"):
                if new_username in st.session_state.users:
                    st.error("⚠️ Username already exists. Please choose another one.")
                elif new_username.strip() == "" or new_password.strip() == "":
                    st.error("⚠️ Username and Password cannot be empty.")
                else:
                    st.session_state.users[new_username] = new_password
                    save_users(st.session_state.users)
                    st.success(f"✅ Account created for {new_username}! Please log in.")

# ---------------- Footer ----------------
st.markdown("""
<div class="footer">
    <hr>
    <p>GGA Indicators Engine: <a href="#" target="_blank">Link</a></p>
    <p>Semi-automated engine that ranks candidate indicators for the Global Goal on Adaptation (UAE-Belém WP)</p>
</div>
""", unsafe_allow_html=True)
