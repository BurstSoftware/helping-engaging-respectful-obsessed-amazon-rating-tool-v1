import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
import json

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
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ====================== SESSION STATE ======================
if "assessments" not in st.session_state:
    st.session_state.assessments = []

if "current_scores" not in st.session_state:
    st.session_state.current_scores = {"Helpful": 3, "Engaged": 3, "Respectful": 3, "Obsessed": 3}

# ====================== SIDEBAR ======================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", width=150)
    st.title("Ordinal Tool")
    st.caption("**HELPFUL • ENGAGED • RESPECTFUL • OBSESSED**")
    
    st.divider()
    role = st.radio("Your Role", ["Operations Manager", "Area Manager", "Process Assistant"], horizontal=True)
    assessor = st.text_input("Assessor Name", value="Alex Rivera")
    
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
            "Area / Process",
            ["Pick - North Wing", "Pack - Downstream", "Receive / Stow", "Sort Center - IB",
             "Problem Solve", "Ship Dock", "Returns", "Other"]
        )
        shift = st.selectbox("Shift", ["Morning", "Mid", "Nights"])
        assessment_date = st.date_input("Assessment Date", value=date.today())
        
        st.divider()
        st.info("**Pro Tip**: Be specific with examples (UPH, safety, defects, teamwork)")

    with col_main:
        st.subheader("Rate on the 4 Pillars")

        dimensions = {
            "Helpful": {
                "emoji": "🤝",
                "color": "#3b82f6",
                "desc": "Supports teammates & customers beyond standard duties"
            },
            "Engaged": {
                "emoji": "⚡",
                "color": "#10b981",
                "desc": "Actively participates with focus and energy"
            },
            "Respectful": {
                "emoji": "🙌",
                "color": "#8b5cf6",
                "desc": "Treats everyone with dignity & promotes inclusion"
            },
            "Obsessed": {
                "emoji": "🔥",
                "color": "#ef4444",
                "desc": "Driven by customer obsession & operational excellence"
            }
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
                
                comment = st.text_area(
                    "Specific examples from this shift",
                    placeholder="e.g. Covered a new hire during peak, chased a packaging defect to root cause...",
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
                        "assessor": assessor,
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
                    
                    st.success(f"✅ Assessment for **{associate}** saved!")
                    
                    # Show radar immediately
                    fig = go.Figure()
                    categories = list(assessment["scores"].keys())
                    values = list(assessment["scores"].values())
                    values += values[:1]  # close the polygon
                    
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories + [categories[0]],
                        fill='toself',
                        name='Score',
                        line_color='#FF9900',
                        fillcolor='rgba(255, 153, 0, 0.3)'
                    ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 5]),
                            bgcolor="#f8f9fa"
                        ),
                        showlegend=False,
                        height=500,
                        title="Ordinal Radar Summary"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Download buttons
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
            df[["date", "associate", "area", "average", "role"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "average": st.column_config.NumberColumn("Avg Score", format="%.1f")
            }
        )
        
        st.subheader("Assessment Details")
        for i, ass in enumerate(st.session_state.assessments):
            with st.expander(f"📅 {ass['date']} — {ass['associate']} ({ass['average']})"):
                cols = st.columns(4)
                for j, (dim, score) in enumerate(ass["scores"].items()):
                    with cols[j]:
                        st.metric(dim, score)
                st.write("**Overall Comment:**")
                st.write(ass.get("overall", ""))

# ====================== TAB 3: HOW IT WORKS ======================
with tab3:
    st.markdown("""
    ### How the Qualitative Ordinal Tool Works

    1. **Select Associate** — Enter name/ID, area, shift
    2. **Rate on 4 Pillars** — Use the 1–5 ordinal scale with real operational examples
    3. **Add Context** — Specific, behavior-based feedback is most valuable
    4. **Save & Review** — Instant radar chart + downloadable report

    **Purpose**: Provide consistent, fair, and development-focused feedback aligned with Amazon Leadership Principles.
    """)
    
    st.caption("This tool stores data only in your browser session. For team-wide use, connect it to a database or Google Sheets.")

# ====================== FOOTER ======================
st.caption("Amazon Operations Qualitative Ordinal Tool • Built with ❤️ for Ops Leaders")
