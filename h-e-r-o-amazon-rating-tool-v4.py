import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

# ========================= CONFIG =========================
st.set_page_config(
    page_title="Amazon Ops Ordinal Tool",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (Amazon look & feel)
st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    .stButton>button {
        background-color: #FF9900;
        color: white;
        border-radius: 20px;
        height: 3em;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #FFBB33;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ====================== SESSION STATE ======================
if "assessments" not in st.session_state:
    st.session_state.assessments = []

if "current_scores" not in st.session_state:
    st.session_state.current_scores = {"Helpful": 3, "Engaged": 3, "Respectful": 3, "Obsessed": 3}

# ====================== TEAM MEMBERS ======================
ASSESSORS = {
    "Artur": "Operations Manager",
    "Emilio": "Operations Manager",
    "Ashley": "Process Assistant",
    "Mike": "Process Assistant",
    "Ken": "Process Assistant",
    "Dan": "Process Assistant",
    "Elizet": "Process Assistant",
    "David": "Process Assistant"
}

# ====================== SIDEBAR ======================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", width=150)
    st.title("Ordinal Tool")
    st.caption("**HELPFUL • ENGAGED • RESPECTFUL • OBSESSED**")
    
    st.divider()
    
    # Assessor Selection (Alex Rivera removed)
    assessor_name = st.selectbox(
        "Assessor Name",
        options=list(ASSESSORS.keys()),
        index=0  # Default to Artur
    )
    
    # Auto-display role
    role = ASSESSORS[assessor_name]
    st.info(f"**Role**: {role}")
    
    st.divider()
    st.caption("Built for Amazon Operations Leaders")

# ====================== TABS ======================
tab1, tab2, tab3 = st.tabs(["📋 New Assessment", "📊 History", "ℹ️ How It Works"])

# ====================== TAB 1: NEW ASSESSMENT ======================
with tab1:
    col_meta, col_main = st.columns([1, 2])
    
    with col_meta:
        st.subheader("Assessment Details")
        associate = st.text_input("Associate Name / ID", placeholder="Maria Lopez • A874392")
        
        area = st.selectbox(
            "Building & Area / Process",
            [
                "QMN7 - Pick", "QMN7 - Pack", "QMN7 - Stow", "QMN7 - Receive",
                "QMN7 - Ship Dock", "QMN7 - Problem Solve", "QMN7 - Sortation", "QMN7 - Other",
                "WMN7 - Inbound", "WMN7 - Outbound", "WMN7 - Pick", "WMN7 - Pack",
                "WMN7 - Stow", "WMN7 - Returns", "WMN7 - Other",
                "Other Building / Process"
            ]
        )
        
        shift = st.selectbox("Shift", ["Morning", "Mid", "Nights"])
        assessment_date = st.date_input("Assessment Date", value=date.today())
        
        st.divider()
        st.info("**Pro Tip**: Be specific with examples (UPH, safety, defects, teamwork)")

    with col_main:
        st.subheader("Rate on the 4 Pillars")

        dimensions = {
            "Helpful": {"emoji": "🤝", "desc": "Supports teammates & customers beyond standard duties"},
            "Engaged": {"emoji": "⚡", "desc": "Actively participates with focus and energy"},
            "Respectful": {"emoji": "🙌", "desc": "Treats everyone with dignity & promotes inclusion"},
            "Obsessed": {"emoji": "🔥", "desc": "Driven by customer obsession & operational excellence"}
        }

        for dim, info in dimensions.items():
            with st.expander(f"{info['emoji']} **{dim}** — {info['desc']}", expanded=True):
                score = st.select_slider(
                    f"Score for {dim}",
                    options=[1, 2, 3, 4, 5],
                    value=st.session_state.current_scores[dim],
                    key=f"slider_{dim}",
                    format_func=lambda x: {
                        1: "1 — Rarely demonstrates",
                        2: "2 — Occasionally helps when asked",
                        3: "3 — Consistently assists",
                        4: "4 — Proactively mentors",
                        5: "5 — Role model / Culture builder"
                    }[x]
                )
                st.session_state.current_scores[dim] = score
                
                st.text_area(
                    "Specific examples from this shift",
                    placeholder="e.g. Covered a new hire during peak, chased a packaging defect...",
                    height=80,
                    key=f"comment_{dim}"
                )

        overall_comment = st.text_area("Overall Comments & Development Plan", height=120)

        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("Submit Assessment", type="primary", use_container_width=True):
                if not associate:
                    st.error("Please enter Associate Name / ID")
                else:
                    assessment = {
                        "date": assessment_date.strftime("%Y-%m-%d"),
                        "assessor": assessor_name,
                        "role": role,
                        "associate": associate,
                        "area": area,
                        "shift": shift,
                        "scores": {dim: st.session_state.current_scores[dim] for dim in dimensions},
                        "average": round(sum(st.session_state.current_scores.values()) / 4, 1),
                        "comments": {
                            dim: st.session_state.get(f"comment_{dim}", "") for dim in dimensions
                        },
                        "overall": overall_comment
                    }
                    
                    st.session_state.assessments.insert(0, assessment)
                    st.success(f"✅ Assessment for **{associate}** saved by {assessor_name}!")
                    
                    # Radar Chart
                    fig = go.Figure()
                    categories = list(assessment["scores"].keys())
                    values = list(assessment["scores"].values()) + [list(assessment["scores"].values())[0]]
                    
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories + [categories[0]],
                        fill='toself',
                        line_color='#FF9900',
                        fillcolor='rgba(255, 153, 0, 0.3)'
                    ))
                    
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                        showlegend=False,
                        height=500,
                        title="Ordinal Radar Summary"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Download
                    csv = pd.DataFrame({
                        "Dimension": list(assessment["scores"].keys()),
                        "Score": list(assessment["scores"].values()),
                        "Comment": [assessment["comments"][d] for d in dimensions]
                    }).to_csv(index=False)
                    
                    st.download_button(
                        "📥 Download Full Report (CSV)",
                        csv,
                        f"Amazon_Ops_{associate.replace(' ', '_')}_{assessment_date}.csv",
                        "text/csv"
                    )

        with col_btn2:
            if st.button("Clear Form", use_container_width=True):
                for dim in dimensions:
                    st.session_state.current_scores[dim] = 3
                st.rerun()

# ====================== TAB 2: HISTORY ======================
with tab2:
    if not st.session_state.assessments:
        st.info("No assessments yet. Create your first one in the **New Assessment** tab.")
    else:
        df = pd.DataFrame(st.session_state.assessments)
        st.dataframe(
            df[["date", "assessor", "role", "associate", "area", "average"]],
            use_container_width=True,
            hide_index=True,
            column_config={"average": st.column_config.NumberColumn("Avg Score", format="%.1f")}
        )

# ====================== TAB 3: HOW IT WORKS ======================
with tab3:
    st.markdown("""
    ### How the Qualitative Ordinal Tool Works

    1. **Select Assessor** — Choose from your team  
    2. **Select Associate** — Enter name/ID, building & area, shift  
    3. **Rate on 4 Pillars** — Use the 1–5 ordinal scale  
    4. **Save & Review** — Instant radar + downloadable report
    """)

# ====================== FOOTER ======================
st.caption("Amazon Operations Qualitative Ordinal Tool • Built with ❤️ for Ops Leaders")
