# app.py
import streamlit as st
import os, json
from backend import (
    CMAT_INDICATORS,
    extract_text_from_pdf,
    extract_numbers_from_text,
    bar_chart,
    radar_chart,
    extract_agriculture_budget,
    agriculture_bar_chart,
    extract_climate_programmes,
    climate_bar_chart,
    extract_total_budget,
    climate_multi_year_chart,
    climate_2024_vs_total_chart
)

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="🌍 CMAT Tool",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

USER_FILE = "users.json"

def load_users():
    return json.load(open(USER_FILE)) if os.path.exists(USER_FILE) else {}

def save_users(users):
    json.dump(users, open(USER_FILE, "w"))

if "users" not in st.session_state:
    st.session_state.users = load_users() or {"admin": "admin"}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ---------------- Sidebar ----------------
st.sidebar.title("🌍 CMAT Tool")
menu = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "📑 Upload Document", "📝 Indicators Survey", "🔐 Login"]
)

page_titles = {
    "🏠 Home": "Home",
    "📑 Upload Document": "Upload Document",
    "📝 Indicators Survey": "Survey",
    "🔐 Login": "Login / Sign Up"
}
current_page = page_titles.get(menu, "")

st.markdown(f"""
<div class="top-header">
    <div class="header-left">
        <h2>🌍 Climate Monitoring & Accountability Tool (CMAT)</h2>
        <p>AI-enabled oversight tool for Zambia’s National Assembly</p>
        <h4>Current Page: {current_page}</h4>
    </div>
    <div class="header-right">
        {"Logged in as: <strong>" + st.session_state.current_user + "</strong>" if st.session_state.logged_in else "Not logged in"}
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- Home ----------------
if menu == "🏠 Home":
    st.subheader("Welcome to CMAT")
    st.markdown("""
        This tool supports parliamentary oversight of climate action by monitoring key indicators under the 
        **Green Economy and Climate Change Programme**.
        """)
    st.image("https://images.unsplash.com/photo-1502786129293-79981df4e689", width=500)
    
    # 🎞 Dummy project images for slideshow
    projects = [
        {
            "title": "Chisamba Solar Power Plant (100 MW)",
            "desc": "Commissioned June 2025; helps diversify Zambia’s energy mix away from hydropower.",
            "img": "https://images.unsplash.com/photo-1509395062183-67c5ad6faff9?w=800&q=60"
        },
        {
            "title": "Itimpi Solar Power Station (60 MW)",
            "desc": "Kitwe-based solar farm addressing electricity shortages, commissioned April 2024.",
            "img": "https://images.unsplash.com/photo-1603565816030-d87e5069a0c1?w=800&q=60"
        },
        {
            "title": "Zambia Riverside Solar Power Station (34 MW)",
            "desc": "Expanded solar farm in Kitwe operational since February 2023.",
            "img": "https://images.unsplash.com/photo-1584277261381-5d7f5d4b5c2d?w=800&q=60"
        },
        {
            "title": "Growing Greener Project (Simalaha Conservancy)",
            "desc": "Community-led project building resilience, combating desertification and boosting biodiversity.",
            "img": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=800&q=60"
        },
        {
            "title": "Strengthening Climate Resilience in the Barotse Sub-basin",
            "desc": "CIF/World Bank-supported effort (2013–2022) to enhance local adaptation capacity.",
            "img": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=800&q=60"
        },
        {
            "title": "Early Warning Systems Project",
            "desc": "UNDP-GEF initiative building Zambia’s hydro-meteorological monitoring infrastructure.",
            "img": "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=800&q=60"
        },
        {
            "title": "National Adaptation Programme of Action (NAPA)",
            "desc": "Targeted adaptation interventions prioritizing vulnerable sectors.",
            "img": "https://images.unsplash.com/photo-1549887534-3db1bd59dcca?w=800&q=60"
        },
        {
            "title": "NDC Implementation Framework",
            "desc": "₮17.2 B Blueprint (2023–2030) aligning mitigation/adaptation with national development goals.",
            "img": "https://images.unsplash.com/photo-1523978591478-c753949ff840?w=800&q=60"
        },
    ]

    st.subheader("🏷 Featured National Climate Projects")

    # Slideshow navigation (using session_state index)
    if "slide_index" not in st.session_state:
        st.session_state.slide_index = 0

    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        if st.button("⬅️ Prev"):
            st.session_state.slide_index = (st.session_state.slide_index - 1) % len(projects)

    with col3:
        if st.button("Next ➡️"):
            st.session_state.slide_index = (st.session_state.slide_index + 1) % len(projects)

    project = projects[st.session_state.slide_index]
    with col2:
        st.image(project["img"], caption=project["title"], use_container_width=True)
        st.markdown(f"**{project['title']}** – {project['desc']}")

# ---------------- Upload Document ----------------
elif menu == "📑 Upload Document":
    if not st.session_state.logged_in:
        st.warning("🔐 Please login to access this page.")
        st.stop()

    st.header("📑 Upload a Budget or Climate Policy Document")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file:
        text = extract_text_from_pdf(uploaded_file, max_pages=10)
        st.success("✅ Document uploaded and processed")
        
        with st.expander("📑 Extracted Text Preview"):
            st.text_area("Extracted Text", text[:3000], height=200)

        # ---- Climate Programmes Analysis ----
        st.subheader("🌍 Climate Programmes (2023 vs 2024)")
        climate_df = extract_climate_programmes(text)
        total_budget = extract_total_budget(text)

        if climate_df is not None:
            st.dataframe(climate_df, use_container_width=True)

            if total_budget:
                st.write(f"**Total 2024 Budget (all programmes):** {total_budget:,.0f} ZMW")

            # 1️⃣ Climate 2022 vs 2023 vs 2024 grouped bars + avg line
            st.plotly_chart(climate_multi_year_chart(climate_df, total_budget=total_budget), use_container_width=True)

            # 2️⃣ Climate 2024 vs total budget
            st.plotly_chart(climate_2024_vs_total_chart(climate_df, total_budget=total_budget), use_container_width=True)

        else:
            st.info("No climate programme data detected (codes 07, 17, 18, 41, 61).")

        # ---- Agriculture Analysis ----
        st.subheader("🌾 Agriculture Budget Analysis")
        df, totals = extract_agriculture_budget(text)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            st.write("**Agriculture Totals:**", totals)
            st.plotly_chart(agriculture_bar_chart(df, totals, year=2024), use_container_width=True)
        else:
            st.info("No agriculture budget data detected.")

        # 🔎 Auto-extract figures
        st.subheader("📊 Auto-Extracted Key Figures")
        extracted = extract_numbers_from_text(
            text,
            keywords=[
                "total public investment in climate initiatives",
                "percentage of national budget allocated to climate adaptation",
                "private sector investment mobilized",
                "energy",
                "agriculture",
                "health",
                "transport",
                "water"
            ]
        )

        if extracted:
            st.write("Extracted Values:", extracted)

            numeric_results = {}
            if "total public investment in climate initiatives" in extracted:
                numeric_results["Total Budget"] = extracted["total public investment in climate initiatives"]
            if "percentage of national budget allocated to climate adaptation" in extracted:
                numeric_results["Adaptation"] = extracted["percentage of national budget allocated to climate adaptation"]
            if "private sector investment mobilized" in extracted:
                numeric_results["Public"] = extracted["private sector investment mobilized"]

            if numeric_results:
                st.plotly_chart(bar_chart(numeric_results, "Budget Indicators"), use_container_width=True)
                st.plotly_chart(radar_chart(numeric_results, "Composite View (Radar)"), use_container_width=True)
            else:
                st.info("No numeric results mapped to indicators yet.")
        else:
            st.warning("⚠️ No key figures could be extracted. Please check document formatting.")

# ---------------- Indicators Survey ----------------
elif menu == "📝 Indicators Survey":
    if not st.session_state.logged_in:
        st.warning("🔐 Please login to access this page.")
        st.stop()

    st.header("📝 CMAT Indicators Input")
    results = {}

    for category, indicators in CMAT_INDICATORS.items():
        with st.expander(f"📊 {category} Indicators"):
            for ind in indicators:
                val = st.text_input(ind, key=f"{category}_{ind}")
                try:
                    results[ind] = float(val) if val else 0
                except:
                    results[ind] = val

    st.subheader("📊 Visualizations")
    numeric_results = {k: v for k, v in results.items() if isinstance(v, (int, float))}
    if numeric_results:
        st.plotly_chart(bar_chart(numeric_results, "Indicator Values"), use_container_width=True)
        st.plotly_chart(radar_chart(numeric_results, "Composite View (Radar)"), use_container_width=True)
    else:
        st.info("Enter numeric values to generate visualizations.")

# ---------------- Login ----------------
elif menu == "🔐 Login":
    st.header("🔐 Login / Sign Up")
    if st.session_state.logged_in:
        st.success(f"✅ Welcome, {st.session_state.current_user}!")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()
    else:
        option = st.radio("Select Option", ["Login", "Sign Up"])
        if option == "Login":
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Login"):
                if u in st.session_state.users and st.session_state.users[u] == p:
                    st.session_state.logged_in, st.session_state.current_user = True, u
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        else:
            u = st.text_input("Choose Username")
            p = st.text_input("Choose Password", type="password")
            if st.button("Sign Up"):
                if u in st.session_state.users:
                    st.error("⚠️ Username exists")
                else:
                    st.session_state.users[u] = p
                    save_users(st.session_state.users)
                    st.success(f"✅ Account created for {u}. Please login.")

# ---------------- Footer ----------------
st.markdown("""
<div class="footer">
    <p>🌍 Climate Monitoring & Accountability Tool (CMAT) — Supporting Zambia’s Climate Action Oversight</p>
    <p>© 2025 CMAT | Built with ❤️ AGNES</p>
</div>
""", unsafe_allow_html=True)
