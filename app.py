# app.py
import streamlit as st
import os, json
import base64
from backend import extract_combined_budget_info
from streamlit_autorefresh import st_autorefresh
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
    climate_2024_vs_total_chart,
    ai_extract_budget_info
)

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="🌍 CMAT Tool",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",  # hide sidebar since nav is on top
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

nav_options = {
    "🏠 Home": "home",
    "ℹ️ About": "about",
    "📑 Upload Doc": "upload",
    "📝 Survey": "survey",
    "🔐 Login": "login"
}


# Set default nav
if "nav" not in st.session_state:
    st.session_state.nav = "home"

# ---------------- Modern Top Navbar (Reworked) ----------------
logo_base64 = get_base64_image("images/gv_zambia.png")

# Use a custom div wrapper to target this specific nav bar with CSS
st.markdown('<div class="nav-bar sticky-nav">', unsafe_allow_html=True)

# Create columns: a wider one for the logo, and equal ones for the buttons.
cols = st.columns([2, 1, 1, 1, 1, 1])

# Render the logo in the first column
with cols[0]:
    st.markdown(
        f'<img src="data:image/png;base64,{logo_base64}" class="nav-logo-img">',
        unsafe_allow_html=True
    )

# Render navigation buttons in the remaining columns
for i, (label, key) in enumerate(nav_options.items()):
    with cols[i + 1]:
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.nav = key

st.markdown('</div>', unsafe_allow_html=True)



# Map session state nav to menu (keeps consistency with nav_options)
nav_map = {
    "home": "🏠 Home",
    "about": "ℹ️ About",
    "upload": "📑 Upload Doc",
    "survey": "📝 Survey",
    "login": "🔐 Login",
}



menu = nav_map.get(st.session_state.nav, "🏠 Home")


# ---------------- Header (No Background) ----------------
user_status = (
    f"Logged in as: <strong>{st.session_state.current_user}</strong>"
    if st.session_state.logged_in else "Not logged in"
)

st.markdown(
    f"""
    <div class="top-header" style="padding: 20px; background-color: #f9f9f9; border-bottom: 1px solid #ddd;">
        <div class="header-left">
            <h2>🌍 Climate Monitoring & Accountability Tool (CMAT)</h2>
            <p>AI-enabled oversight tool for Zambia’s National Assembly</p>
        </div>
        <div class="header-right" style="font-size:14px; color:#333;">
            {user_status}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------- Home ----------------
if menu == "🏠 Home":
    # 🏠 Intro Section
    st.markdown(
        """
        <div class="section intro-text">
            <h3>Welcome to CMAT</h3>
            <p>
                This tool supports parliamentary oversight of climate action by monitoring key indicators under the 
                <strong>Green Economy and Climate Change Programme</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------- About ----------------
elif menu == "ℹ️ About":
    st.header("ℹ️ About CMAT")
    st.markdown(
        """
        The **Climate Monitoring & Accountability Tool (CMAT)** is an AI-enabled platform 
        developed by the **National Assembly of Zambia (NAZ)** in collaboration with **AGNES**.  
        Its goal is to strengthen **parliamentary oversight** of climate action by tracking 
        budgets, programmes, and performance against Zambia’s climate goals.  

        ### 📜 Background & Context
        - Developed in line with **NAZ Standing Orders (2024)** and the **National Planning and Budgeting Act No. 1 of 2020**.  
        - Focuses on oversight of the **Ministry of Green Economy and Environment**, which leads Zambia’s climate policy.  
        - Supports alignment with **international commitments** (Paris Agreement, NDCs).  

        ### 🎯 Objectives
        1. Track climate-related laws, budgets, and strategies.  
        2. Strengthen transparency in climate finance.  
        3. Promote accountability in project implementation.  
        4. Enhance public engagement and awareness.  
        """
    )

    st.subheader("📊 Indicators for CMAT")
    st.markdown(
        """
        The CMAT uses indicators to track Zambia’s climate governance, 
        budget allocations, and policy outcomes. Indicators fall under 
        these categories:
        """
    )

    categories = {
        "Legislative": [
            "Number of Climate-Related Laws Enacted",
            "Quality of Climate Legislation",
            "Timeliness of Law Implementation"
        ],
        "Financial": [
            "Total Public Investment in Climate Initiatives",
            "Budget % Allocated to Climate Adaptation",
            "Private Sector Investment Mobilized"
        ],
        "Policy & Governance": [
            "Green Growth Guidelines",
            "Climate Coordination",
            "Public Engagement"
        ],
        "Capacity Building": [
            "Training Programmes Funded",
            "Awareness Campaigns Implemented"
        ],
        "Implementation": [
            "% of Budget Utilised",
            "Project Completion Rates",
            "Fund Disbursement Timeliness"
        ],
        "International Commitments": [
            "Alignment with Paris Agreement",
            "Progress Towards NDCs"
        ]
    }

    for category, inds in categories.items():
        with st.expander(f"📌 {category} Indicators"):
            for ind in inds:
                st.markdown(f"- {ind}")

    # 📂 Reports Section
    st.markdown(
        """
        <div class="section">
            <h3>📂 Reports & Resources</h3>
            <p>Here you will find key documents, data, and reports generated through CMAT.</p>

            ### 📑 Available Resources
            - 📘 National Climate Indicators Report (2025) *(Coming Soon)*
            - 📗 Annual Budget Oversight Report *(Draft in progress)*
            - 📄 Public Awareness Briefs *(2025)*

            ### 📥 Downloads
            *Currently under development – reports will be made available here.*
        </div>
        """,
        unsafe_allow_html=True
    )

    # 🎞 Project images for slideshow
    st.markdown(
        """
        <div class="section">
            <h3>🏷 Featured National Climate Projects</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    projects = [
        {
            "title": "Chisamba Solar Power Plant (100 MW)",
            "desc": "Commissioned June 2025; helps diversify Zambia’s energy mix away from hydropower.",
            "img": "images/chisamba.jpg"
        },
        {
            "title": "Itimpi Solar Power Station (60 MW)",
            "desc": "Kitwe-based solar farm addressing electricity shortages, commissioned April 2024.",
            "img": "images/itimpi.jpg"
        },
        {
            "title": "Zambia Riverside Solar Power Station (34 MW)",
            "desc": "Expanded solar farm in Kitwe operational since February 2023.",
            "img": "images/riverside.jpg"
        },
        {
            "title": "Growing Greener Project (Simalaha Conservancy)",
            "desc": "Community-led project building resilience, combating desertification and boosting biodiversity.",
            "img": "images/greener.jpg"
        },
        {
            "title": "Strengthening Climate Resilience in the Barotse Sub-basin",
            "desc": "CIF/World Bank-supported effort (2013–2022) to enhance local adaptation capacity.",
            "img": "images/barotse.jpg"
        },
        {
            "title": "Early Warning Systems Project",
            "desc": "UNDP-GEF initiative building Zambia’s hydro-meteorological monitoring infrastructure.",
            "img": "images/earlywarning.jpg"
        },
        {
            "title": "National Adaptation Programme of Action (NAPA)",
            "desc": "Targeted adaptation interventions prioritizing vulnerable sectors.",
            "img": "images/napa.jpg"
        },
        {
            "title": "NDC Implementation Framework",
            "desc": "₮17.2 B Blueprint (2023–2030) aligning mitigation/adaptation with national development goals.",
            "img": "images/ndc.jpg"
        }
    ]

    # Slideshow state
    if "slide_index" not in st.session_state:
        st.session_state.slide_index = 0
    
    if "refresh_count" not in st.session_state:
        st.session_state.refresh_count = 0

    # Auto-advance slideshow every 5s
    refresh_count = st_autorefresh(interval=5000, key="slideshow_refresher")

    if refresh_count > st.session_state.refresh_count:
        st.session_state.refresh_count = refresh_count
        st.session_state.slide_index = (st.session_state.slide_index + 1) % len(projects)

    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        if st.button("⬅️ Prev"):
            st.session_state.slide_index = (st.session_state.slide_index - 1) % len(projects)
            st.rerun()

    with col3:
        if st.button("Next ➡️"):
            st.session_state.slide_index = (st.session_state.slide_index + 1) % len(projects)
            st.rerun()

    project = projects[st.session_state.slide_index]

    with col2:
        st.markdown('<div class="project-card">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <img src="data:image/png;base64,{get_base64_image(project['img'])}" 
                 class="project-img" alt="{project['title']}"/>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div class="project-text">
                <h4>{project['title']}</h4>
                <p>{project['desc']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Dot indicators
        dots = ""
        for i in range(len(projects)):
            if i == st.session_state.slide_index:
                dots += "<span style='font-size:22px; color:#007BFF;'>●</span> "
            else:
                dots += "<span style='font-size:18px; color:gray;'>○</span> "
        st.markdown(
            f"<div style='text-align:center; margin-top:10px;'>{dots}</div>",
            unsafe_allow_html=True
        )

# ---------------- Upload Document ----------------
elif menu == "📑 Upload Doc":
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

        # ---- AI + Keyword-Based Budget Extraction (via backend) ----
        st.subheader("🤖 AI + Keyword-Enhanced Budget Figures")
        merged_results = extract_combined_budget_info(text)

        if merged_results:
            st.json(merged_results)
            st.plotly_chart(bar_chart(merged_results, "Merged Budget Indicators"), use_container_width=True)
            st.plotly_chart(radar_chart(merged_results, "Merged Composite View"), use_container_width=True)
            st.session_state.survey_defaults = merged_results
            st.info("📊 Survey defaults updated automatically from merged AI + keyword extraction ✅")
        else:
            st.warning("⚠️ Could not extract budget figures (AI + fallback both failed).")

        # ---- Climate Programmes Analysis ----
        st.subheader("🌍 Climate Programmes (2023 vs 2024)")
        climate_df = extract_climate_programmes(text)
        total_budget = extract_total_budget(text)

        if climate_df is not None:
            st.dataframe(climate_df, use_container_width=True)

            if total_budget:
                st.write(f"**Total 2024 Budget (all programmes):** {total_budget:,.0f} ZMW")

            st.plotly_chart(climate_multi_year_chart(climate_df, total_budget=total_budget), use_container_width=True)
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

# ---------------- Survey ----------------
elif menu == "📝 Survey":
    if not st.session_state.logged_in:
        st.warning("🔐 Please login to access this page.")
        st.stop()

    st.header("📝 CMAT Indicators Survey")
    st.write("Enter values manually for each indicator. If a document was uploaded, values are pre-filled.")

    manual_results = {}
    for category, indicators in CMAT_INDICATORS.items():
        with st.expander(f"📊 {category} Indicators"):
            for ind in indicators:
                # Fetch default if available (case-insensitive lookup)
                default_val = 0.0
                if "survey_defaults" in st.session_state:
                    for k, v in st.session_state.survey_defaults.items():
                        if k.lower() == ind.lower():
                            default_val = v
                            break

                val = st.number_input(
                    f"{ind}",
                    min_value=0.0,
                    step=1000.0,
                    value=float(default_val),
                    key=f"survey_{category}_{ind}"
                )
                manual_results[ind] = val

    # Process entered numbers
    st.subheader("📊 Survey Results")
    numeric_results = {k: v for k, v in manual_results.items() if isinstance(v, (int, float)) and v > 0}

    if numeric_results:
        st.success("✅ Indicators recorded successfully")
        st.plotly_chart(bar_chart(numeric_results, "Survey Budget Indicators"), use_container_width=True)
        st.plotly_chart(radar_chart(numeric_results, "Survey Composite View"), use_container_width=True)

        # Extra: calculate percentages if "Total Budget" is present
        if "Total Budget" in numeric_results:
            total_budget = numeric_results["Total Budget"]
            public = numeric_results.get("Public", 0)
            adaptation = numeric_results.get("Adaptation", 0)
            mitigation = numeric_results.get("Mitigation", 0)

            percentages = calc_percentages(total_budget, public, adaptation, mitigation)
            st.plotly_chart(
                bar_percent_chart(
                    ["Public", "Adaptation", "Mitigation"], 
                    percentages,
                    "Share of Total Budget (%)"
                ),
                use_container_width=True
            )
    else:
        st.info("Please enter numeric values above to see results.")




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
# We inject a custom CSS class to wrap the footer and apply styles
st.markdown("""
<div class="footer">
    <div class="footer-container">
""", unsafe_allow_html=True)

# Use Streamlit columns to structure the footer content
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <h4>About CMAT</h4>
        <p>🌍 Climate Monitoring & Accountability Tool (CMAT) supports Zambia’s climate action oversight by tracking projects, budgets, and impact.</p>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("<h4>Quick Links</h4>", unsafe_allow_html=True)
    
    # Use st.button to trigger navigation. Each button updates the session state.
    if st.button("Home", key="footer_home", use_container_width=True):
        st.session_state.nav = "home"
        st.rerun()
        
    if st.button("About", key="footer_about", use_container_width=True):
        st.session_state.nav = "about"
        st.rerun()
        
    if st.button("Upload Document", key="footer_upload", use_container_width=True):
        st.session_state.nav = "upload"
        st.rerun()
        
    if st.button("Login", key="footer_login", use_container_width=True):
        st.session_state.nav = "login"
        st.rerun()

with col3:
    st.markdown("""
        <h4>Contact</h4>
        <p>Email: info@parliament.gov.zm</p>
        <p>📍 Parliament road, Lusaka</p>
        <div class="social-icons">
            <a href="#"><img src="https://cdn-icons-png.flaticon.com/512/733/733547.png" alt="Facebook" width="20"/></a>
            <a href="#"><img src="https://cdn-icons-png.flaticon.com/512/733/733579.png" alt="Twitter" width="20"/></a>
            <a href="#"><img src="https://cdn-icons-png.flaticon.com/512/2111/2111463.png" alt="LinkedIn" width="20"/></a>
        </div>
    """, unsafe_allow_html=True)

# Close the footer containers and add the bottom bar
st.markdown("""
    </div>
    <div class="footer-bottom">
        <p>© 2025 CMAT | Built with ❤️ by AGNES</p>
    </div>
</div>
""", unsafe_allow_html=True)
