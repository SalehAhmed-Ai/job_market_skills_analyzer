"""
app.py

Optional Streamlit dashboard for the Job Market Skills Analyzer project.
Reads the cleaned dataset and presents an interactive summary with
filters, KPI cards, and charts. Does not perform any scraping or
re-cleaning of the data.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(
    page_title="Job Market Skills Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling Injection (Supports dark and light themes dynamically)
st.markdown("""
<style>
    /* Global style overrides */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    
    /* Styled tab headers */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 2px solid rgba(128,128,128,0.2);
        padding-bottom: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.15);
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        font-weight: 600 !important;
        color: var(--text-color) !important;
        opacity: 0.75;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        opacity: 1;
        background-color: rgba(99, 102, 241, 0.05);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4F46E5 !important;
        color: white !important;
        border-color: #4F46E5 !important;
        opacity: 1;
    }
    
    /* Container style */
    .card-container {
        border-radius: 12px;
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 1px solid rgba(128, 128, 128, 0.15);
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }
</style>
""", unsafe_allow_html=True)

# Helper function to render modern metric cards
def render_metric_card(title, value, subtitle="", icon="📊", gradient="linear-gradient(135deg, #6366F1, #4F46E5)"):
    st.markdown(f"""
    <div style="
        background: {gradient};
        color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    ">
        <div style="font-size: 11px; font-weight: 600; opacity: 0.85; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; font-family: 'Inter', sans-serif;">{title}</div>
        <div style="font-size: 26px; font-weight: 800; margin-bottom: 4px; font-family: 'Inter', sans-serif; line-height: 1.2;">{value}</div>
        {f'<div style="font-size: 11px; opacity: 0.8; font-weight: 500; font-family: \'Inter\', sans-serif;">{subtitle}</div>' if subtitle else ''}
        <div style="position: absolute; right: 15px; bottom: 8px; font-size: 40px; opacity: 0.18; pointer-events: none; user-select: none;">{icon}</div>
    </div>
    """, unsafe_allow_html=True)

DATA_PATH = "data/cleaned/job_postings_cleaned.csv"

SKILL_COLUMNS = [
    "Python", "SQL", "Excel", "Power_Bi", "Tableau", "Pandas", "Numpy",
    "Machine_Learning", "Git", "AWS", "Azure", "R", "Java", "SAS",
    "Spark", "Etl", "Statistics", "Powerpoint", "Word", "Outlook"
]

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        return pd.DataFrame()

# Load dataset with visual spinner
with st.spinner("Loading job postings data..."):
    df = load_data(DATA_PATH)

# Beautiful Gradient Header Banner
st.markdown("""
<div style="background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%); padding: 25px; border-radius: 12px; margin-bottom: 25px; text-align: center; color: white; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
    <h1 style="margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -0.5px; font-family: 'Inter', sans-serif; color: white;">📊 Job Market Skills Analyzer</h1>
    <p style="margin: 5px 0 0 0; font-size: 16px; opacity: 0.95; font-weight: 400; font-family: 'Inter', sans-serif; color: white;">Interactive Dashboard of Skills, Salaries, and Trends in Data Analytics</p>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.error(
        "❌ Cleaned dataset not found. Please run `job_market_analysis.ipynb` "
        "first to generate `data/cleaned/job_postings_cleaned.csv`."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar Filters & Control Panel
# ---------------------------------------------------------------------------
st.sidebar.header("🎛️ Control Panel")
st.sidebar.write("Configure metrics and filters below:")

# Set up default arrays and check session states
all_roles = sorted(df["main_role"].dropna().unique())
all_work_modes = sorted(df["work_mode_from_text"].dropna().unique())
all_seniorities = sorted(df["seniority_level"].dropna().unique())
all_experiences = sorted(df["experience_level"].dropna().unique())

if "roles_sel" not in st.session_state:
    st.session_state.roles_sel = all_roles
if "work_modes_sel" not in st.session_state:
    st.session_state.work_modes_sel = all_work_modes
if "seniority_sel" not in st.session_state:
    st.session_state.seniority_sel = all_seniorities
if "experience_sel" not in st.session_state:
    st.session_state.experience_sel = all_experiences
if "salary_only_sel" not in st.session_state:
    st.session_state.salary_only_sel = False

# Sidebar widgets
roles = st.sidebar.multiselect("Main Role", options=all_roles, key="roles_sel")
work_modes = st.sidebar.multiselect("Work Mode", options=all_work_modes, key="work_modes_sel")
seniority = st.sidebar.multiselect("Seniority Level", options=all_seniorities, key="seniority_sel")
experience = st.sidebar.multiselect("Experience Level", options=all_experiences, key="experience_sel")
salary_only = st.sidebar.checkbox("Disclosed Salary Only", key="salary_only_sel")

# Reset button in sidebar
if st.sidebar.button("🔄 Reset Filters", use_container_width=True):
    st.session_state.roles_sel = all_roles
    st.session_state.work_modes_sel = all_work_modes
    st.session_state.seniority_sel = all_seniorities
    st.session_state.experience_sel = all_experiences
    st.session_state.salary_only_sel = False
    st.rerun()

# Apply Filters
filtered_df = df[
    df["main_role"].isin(roles) & 
    df["work_mode_from_text"].isin(work_modes) &
    df["seniority_level"].isin(seniority) &
    df["experience_level"].isin(experience)
]

if salary_only:
    filtered_df = filtered_df[filtered_df["has_salary"] == True]

if filtered_df.empty:
    st.warning("⚠️ No postings match the selected filters. Please adjust your filters or click 'Reset Filters' in the sidebar.")
    st.stop()

# Sidebar Metadata Expanders
st.sidebar.markdown("---")
with st.sidebar.expander("ℹ️ About the Dataset", expanded=False):
    st.markdown("""
    **Job Market Skills Analyzer**
    
    - **Source:** Kaggle - Data Analyst Job Postings
    - **Total Records:** 977 postings (after cleaning and sampling)
    - **Methodology:** Regular expressions were utilized to extract skills, experience levels, and work modes from free-text descriptions.
    
    *For full cleaning workflows, please refer to `job_market_analysis.ipynb`.*
    """)

# ---------------------------------------------------------------------------
# Main Tabs Navigation
# ---------------------------------------------------------------------------
tab_overview, tab_salary, tab_requirements, tab_explorer = st.tabs([
    "📊 Market Overview", 
    "💰 Salary Insights", 
    "🎓 Requirements & Trends", 
    "🔍 Job Explorer"
])

# ---------------------------------------------------------------------------
# Tab 1: Market Overview & Skills
# ---------------------------------------------------------------------------
with tab_overview:
    # 1. Metric Calculations
    total_postings = len(filtered_df)
    existing_skill_cols = [c for c in SKILL_COLUMNS if c in filtered_df.columns]
    skill_totals = filtered_df[existing_skill_cols].sum().sort_values(ascending=False)
    top_skill = skill_totals.index[0] if not skill_totals.empty else "N/A"
    top_skill_count = skill_totals.values[0] if not skill_totals.empty else 0
    top_skill_pct = (top_skill_count / total_postings) * 100 if total_postings > 0 else 0
    
    avg_skill_count = filtered_df["skill_count"].mean() if "skill_count" in filtered_df else 0
    remote_pct = (filtered_df["work_mode_from_text"] == "Remote").mean() * 100
    
    # 2. Render Cards Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card(
            title="Total Postings",
            value=f"{total_postings}",
            subtitle=f"Filtered from {len(df)} postings",
            icon="📋",
            gradient="linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)"
        )
    with col2:
        render_metric_card(
            title="Top Technical Skill",
            value=f"{top_skill.replace('_', ' ')}",
            subtitle=f"Found in {top_skill_pct:.1f}% of roles",
            icon="🛠️",
            gradient="linear-gradient(135deg, #10b981 0%, #059669 100%)"
        )
    with col3:
        render_metric_card(
            title="Avg Skill Count",
            value=f"{avg_skill_count:.1f}",
            subtitle="Skills identified per job description",
            icon="🧠",
            gradient="linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)"
        )
    with col4:
        render_metric_card(
            title="Remote Share",
            value=f"{remote_pct:.0f}%",
            subtitle=f"{filtered_df['work_mode_from_text'].eq('Remote').sum()} remote roles in selection",
            icon="🌐",
            gradient="linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3. Two-Column Chart Layout
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        role_counts = filtered_df["main_role"].value_counts().head(10)
        fig_roles = px.bar(
            x=role_counts.values, y=[r.replace('_', ' ') for r in role_counts.index], orientation="h",
            labels={"x": "Number of Postings", "y": "Main Role"},
            title="🔥 Most Common Job Roles in Selected Sample"
        )
        fig_roles.update_traces(
            marker_color='#6366F1',
            hovertemplate="<b>%{y}</b><br>Postings: %{x}<extra></extra>"
        )
        fig_roles.update_layout(
            yaxis=dict(categoryorder="total ascending"),
            margin=dict(l=10, r=10, t=45, b=10),
            xaxis_title="Number of Postings",
            yaxis_title=None,
            title_font=dict(size=16, family="Inter, sans-serif")
        )
        st.plotly_chart(fig_roles, use_container_width=True)
        
    with chart_col2:
        # Convert to percentage
        skill_percentages = (skill_totals / total_postings * 100).head(15)
        fig_skills = px.bar(
            x=skill_percentages.values, y=[s.replace('_', ' ') for s in skill_percentages.index], orientation="h",
            labels={"x": "% of Postings", "y": "Skill"},
            title="🛠️ Top 15 Requested Technical Skills (% of Postings)"
        )
        fig_skills.update_traces(
            marker_color='#10B981',
            hovertemplate="<b>%{y}</b><br>Prevalence: %{x:.1f}%<extra></extra>"
        )
        fig_skills.update_layout(
            yaxis=dict(categoryorder="total ascending"),
            margin=dict(l=10, r=10, t=45, b=10),
            xaxis_title="% of Postings with Skill",
            yaxis_title=None,
            title_font=dict(size=16, family="Inter, sans-serif")
        )
        st.plotly_chart(fig_skills, use_container_width=True)
        
    # -----------------------------------------------------------------------
    # Additional Distributions and Comparisons (Replacing Heatmap)
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📊 Work Mode & Seniority Distributions")
    
    col_wm_sen1, col_wm_sen2 = st.columns(2)
    with col_wm_sen1:
        # --- Chart 3: Work mode distribution ---
        known_wm_df = filtered_df[filtered_df["work_mode_from_text"] != "Unknown"]
        if not known_wm_df.empty:
            wm_counts = known_wm_df["work_mode_from_text"].value_counts()
            fig_wm = px.bar(
                x=wm_counts.index, y=wm_counts.values,
                title=f"Work Mode Distribution (Among {len(known_wm_df)} Postings with Explicit Mode)"
            )
            fig_wm.update_traces(marker_color='#7c3aed', hovertemplate="<b>%{x}</b><br>Postings: %{y}<extra></extra>")
            fig_wm.update_layout(
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis_title="Work Mode",
                yaxis_title="Number of Postings",
                title_font=dict(size=14, family="Inter, sans-serif")
            )
            st.plotly_chart(fig_wm, use_container_width=True)
        else:
            st.info("No explicit work mode details found in selected data.")
            
    with col_wm_sen2:
        # --- Chart 4: Seniority level distribution ---
        known_sen_df = filtered_df[filtered_df["seniority_level"] != "Not Specified"]
        if not known_sen_df.empty:
            sen_counts = known_sen_df["seniority_level"].value_counts()
            fig_sen = px.bar(
                x=sen_counts.index, y=sen_counts.values,
                title=f"Seniority Level Distribution (Among {len(known_sen_df)} Postings with Explicit Level)"
            )
            fig_sen.update_traces(marker_color='#f59e0b', hovertemplate="<b>%{x}</b><br>Postings: %{y}<extra></extra>")
            fig_sen.update_layout(
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis_title="Seniority Level",
                yaxis_title="Number of Postings",
                title_font=dict(size=14, family="Inter, sans-serif")
            )
            st.plotly_chart(fig_sen, use_container_width=True)
        else:
            st.info("No explicit seniority level details found in selected data.")

    st.markdown("---")
    st.markdown("### 💰 Salary Distributions & Skill Comparisons")
    
    col_sal_comp1, col_sal_comp2 = st.columns(2)
    with col_sal_comp1:
        # --- Chart 5: Salary distribution (only on postings with disclosed salary) ---
        sal_data = filtered_df[filtered_df["has_salary"] == True]
        if not sal_data.empty:
            fig_sal_dist = px.histogram(
                sal_data, x="salary_standardized", nbins=20,
                title=f"Salary Distribution (Standardized Annual - {len(sal_data)} postings)"
            )
            fig_sal_dist.update_traces(
                marker=dict(color='#0891b2', line=dict(color='white', width=1.5)),
                hovertemplate="Salary Range: %{x}<br>Postings: %{y}<extra></extra>"
            )
            fig_sal_dist.update_layout(
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis_title="Standardized Annual Salary ($)",
                yaxis_title="Number of Postings",
                title_font=dict(size=14, family="Inter, sans-serif")
            )
            st.plotly_chart(fig_sal_dist, use_container_width=True)
        else:
            st.info("No disclosed salary data available in selected data.")
            
    with col_sal_comp2:
        # --- 8.6 Skills vs Salary Comparison ---
        sal_compare_df = filtered_df[filtered_df["has_salary"] == True]
        if not sal_compare_df.empty:
            skills_to_compare = ["Python", "SQL", "Machine_Learning", "Power_Bi", "Tableau"]
            salary_by_skill = {}
            for skill in skills_to_compare:
                if skill in sal_compare_df.columns:
                    has_skill = sal_compare_df[sal_compare_df[skill] == 1]["salary_standardized"]
                    no_skill = sal_compare_df[sal_compare_df[skill] == 0]["salary_standardized"]
                    
                    has_val = has_skill.mean() if len(has_skill) > 0 else np.nan
                    no_val = no_skill.mean() if len(no_skill) > 0 else np.nan
                    
                    salary_by_skill[skill.replace('_', ' ')] = {
                        "Has Skill": has_val,
                        "No Skill": no_val
                    }
            
            if salary_by_skill:
                salary_skill_df = pd.DataFrame(salary_by_skill).T.reset_index().rename(columns={"index": "Skill"})
                salary_skill_df_melted = pd.melt(
                    salary_skill_df, id_vars="Skill",
                    value_vars=["Has Skill", "No Skill"],
                    var_name="Requirement", value_name="Average Salary ($)"
                )
                
                fig_sal_skill = px.bar(
                    salary_skill_df_melted, x="Skill", y="Average Salary ($)", color="Requirement",
                    barmode="group",
                    color_discrete_map={"Has Skill": "#16a34a", "No Skill": "#d1d5db"},
                    title="Average Salary by Skill Requirement"
                )
                fig_sal_skill.update_layout(
                    margin=dict(l=10, r=10, t=40, b=10),
                    xaxis_title="Skill",
                    yaxis_title="Average Salary ($)",
                    title_font=dict(size=14, family="Inter, sans-serif")
                )
                st.plotly_chart(fig_sal_skill, use_container_width=True)
            else:
                st.info("No skill-salary comparison data could be computed.")
        else:
            st.info("No disclosed salary data available to compare skill requirements.")

# ---------------------------------------------------------------------------
# Tab 2: Salary Insights
# ---------------------------------------------------------------------------
with tab_salary:
    salary_available = filtered_df[filtered_df["has_salary"] == True]
    
    if salary_available.empty:
        st.info(
            "ℹ️ No disclosed salary data is available for the current filter configuration. "
            "Please broaden your filters or clear the 'Disclosed Salary Only' checkbox in the sidebar."
        )
    else:
        # 1. Salary KPIs
        median_sal = salary_available["salary_standardized"].median()
        max_sal = salary_available["salary_standardized"].max()
        avg_sal = salary_available["salary_standardized"].mean()
        sal_disclosure_rate = (len(salary_available) / total_postings) * 100
        
        col_sal1, col_sal2, col_sal3, col_sal4 = st.columns(4)
        with col_sal1:
            render_metric_card(
                title="Median Salary",
                value=f"${median_sal:,.0f}",
                subtitle="Annual standardized salary",
                icon="💰",
                gradient="linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)"
            )
        with col_sal2:
            render_metric_card(
                title="Average Salary",
                value=f"${avg_sal:,.0f}",
                subtitle="Annual standardized salary",
                icon="📈",
                gradient="linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)"
            )
        with col_sal3:
            render_metric_card(
                title="Maximum Salary",
                value=f"${max_sal:,.0f}",
                subtitle="Annual standardized salary",
                icon="🏆",
                gradient="linear-gradient(135deg, #10b981 0%, #047857 100%)"
            )
        with col_sal4:
            render_metric_card(
                title="Salary Disclosure",
                value=f"{sal_disclosure_rate:.1f}%",
                subtitle=f"{len(salary_available)} of {total_postings} postings",
                icon="📊",
                gradient="linear-gradient(135deg, #f59e0b 0%, #b45309 100%)"
            )
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. Distribution and Ranges layout
        col_sal_charts1, col_sal_charts2 = st.columns(2)
        
        with col_sal_charts1:
            fig_sal_dist = px.histogram(
                salary_available, x="salary_standardized",
                nbins=15, marginal="box",
                labels={"salary_standardized": "Standardized Salary ($)"},
                title="📊 Distribution of Disclosed Standardized Salaries"
            )
            fig_sal_dist.update_traces(
                marker=dict(color='#6366f1', line=dict(color='white', width=1.5)),
                opacity=0.85,
                hovertemplate="Salary Range: %{x}<br>Count: %{y}<extra></extra>"
            )
            fig_sal_dist.update_layout(
                xaxis_title="Standardized Annual Salary ($)",
                yaxis_title="Number of Postings",
                margin=dict(l=10, r=10, t=40, b=10),
                title_font=dict(size=16, family="Inter, sans-serif")
            )
            st.plotly_chart(fig_sal_dist, use_container_width=True)
            
        with col_sal_charts2:
            fig_sal_by_role = px.box(
                salary_available, x="main_role", y="salary_standardized",
                color="main_role",
                title="💼 Annual Salary Ranges by Main Job Role"
            )
            fig_sal_by_role.update_layout(
                xaxis_title=None,
                yaxis_title="Standardized Annual Salary ($)",
                showlegend=False,
                margin=dict(l=10, r=10, t=40, b=10),
                title_font=dict(size=16, family="Inter, sans-serif")
            )
            st.plotly_chart(fig_sal_by_role, use_container_width=True)
            
        st.markdown("---")
        
        # 3. Salary Premium Calculation
        st.markdown("### 💰 Skill Salary Premium (Median)")
        st.markdown("Calculates the premium difference in **median annual salary** for job postings that *require* a technical skill versus those that *do not* (restricted to the top 10 most common skills).")
        
        top_skills_premium = skill_totals.head(10).index.tolist()
        premium_list = []
        for skill in top_skills_premium:
            with_skill_sal = salary_available[salary_available[skill] == 1]["salary_standardized"]
            without_skill_sal = salary_available[salary_available[skill] == 0]["salary_standardized"]
            if len(with_skill_sal) >= 3 and len(without_skill_sal) >= 3:
                med_with = with_skill_sal.median()
                med_without = without_skill_sal.median()
                premium = med_with - med_without
                premium_list.append({
                    "Skill": skill.replace('_', ' '),
                    "Median Salary (With)": med_with,
                    "Median Salary (Without)": med_without,
                    "Salary Premium ($)": premium,
                    "Jobs With": len(with_skill_sal),
                    "Jobs Without": len(without_skill_sal)
                })
                
        if premium_list:
            premium_df = pd.DataFrame(premium_list).sort_values(by="Salary Premium ($)", ascending=False)
            
            fig_prem = px.bar(
                premium_df, x="Salary Premium ($)", y="Skill", orientation="h",
                color="Salary Premium ($)",
                color_continuous_scale="RdYlGn",
                labels={"Salary Premium ($)": "Median Salary Difference ($)", "Skill": "Technical Skill"},
                title="Salary Premium for In-Demand Technical Skills",
                hover_data=["Median Salary (With)", "Median Salary (Without)", "Jobs With", "Jobs Without"]
            )
            fig_prem.update_layout(
                margin=dict(l=10, r=10, t=40, b=10),
                yaxis=dict(categoryorder="total ascending"),
                title_font=dict(size=16, family="Inter, sans-serif")
            )
            st.plotly_chart(fig_prem, use_container_width=True)
        else:
            st.info("Insufficient salary data points in selection to compute skill salary premiums (at least 3 sample postings with and without the skill required are needed).")

# ---------------------------------------------------------------------------
# Tab 3: Requirements & Trends
# ---------------------------------------------------------------------------
with tab_requirements:
    # 1. Experience & Trends KPIs
    avg_exp = filtered_df["min_experience"].mean() if "min_experience" in filtered_df else np.nan
    remote_pct = (filtered_df["work_mode_from_text"] == "Remote").mean() * 100
    seniority_spec = (filtered_df["seniority_level"] != "Not Specified").mean() * 100
    
    col_req1, col_req2, col_req3 = st.columns(3)
    with col_req1:
        render_metric_card(
            title="Avg Experience Required",
            value=f"{avg_exp:.1f} Yrs" if pd.notna(avg_exp) else "N/A",
            subtitle="Minimum required years of experience",
            icon="🎓",
            gradient="linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)"
        )
    with col_req2:
        render_metric_card(
            title="Flexible Work Share",
            value=f"{remote_pct:.1f}%",
            subtitle="Classified as Remote work mode",
            icon="🌐",
            gradient="linear-gradient(135deg, #10b981 0%, #047857 100%)"
        )
    with col_req3:
        render_metric_card(
            title="Seniority Specification",
            value=f"{seniority_spec:.1f}%",
            subtitle="Seniority level declared in job title",
            icon="🏆",
            gradient="linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)"
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Charts Layout
    col_req_charts1, col_req_charts2 = st.columns(2)
    
    with col_req_charts1:
        exp_available = filtered_df[filtered_df["min_experience"].notna()]
        if not exp_available.empty:
            fig_exp_dist = px.histogram(
                exp_available, x="min_experience",
                nbins=8,
                title="🎓 Distribution of Minimum Years of Experience Required"
            )
            fig_exp_dist.update_traces(
                marker_color='#8b5cf6',
                opacity=0.85,
                hovertemplate="Required Experience: %{x} yrs<br>Jobs count: %{y}<extra></extra>"
            )
            fig_exp_dist.update_layout(
                xaxis_title="Required Minimum Years of Experience",
                yaxis_title="Number of Postings",
                margin=dict(l=10, r=10, t=40, b=10),
                title_font=dict(size=16, family="Inter, sans-serif")
            )
            st.plotly_chart(fig_exp_dist, use_container_width=True)
        else:
            st.info("No postings with valid experience information match the selected filters.")
            
    with col_req_charts2:
        # Stacked bar chart: Work Mode by Seniority Level
        work_seniority = filtered_df.groupby(["seniority_level", "work_mode_from_text"]).size().reset_index(name="count")
        fig_ws = px.bar(
            work_seniority, x="seniority_level", y="count", color="work_mode_from_text",
            title="🌐 Work Mode Distribution by Seniority Level",
            labels={"count": "Number of Postings", "seniority_level": "Seniority Level", "work_mode_from_text": "Work Mode"},
            barmode="stack",
            color_discrete_map={"Remote": "#10b981", "Hybrid": "#3b82f6", "On-site": "#ec4899", "Unknown": "#94a3b8"}
        )
        fig_ws.update_layout(
            xaxis_title="Seniority Level",
            yaxis_title="Number of Postings",
            margin=dict(l=10, r=10, t=40, b=10),
            title_font=dict(size=16, family="Inter, sans-serif")
        )
        st.plotly_chart(fig_ws, use_container_width=True)
        
    st.markdown("---")
    
    # 3. Experience vs Salary Relationship
    st.markdown("### 📈 Relationship between Experience and Salary")
    scatter_data = filtered_df[filtered_df["min_experience"].notna() & filtered_df["salary_standardized"].notna() & (filtered_df["has_salary"] == True)]
    if not scatter_data.empty:
        fig_scatter = px.scatter(
            scatter_data, x="min_experience", y="salary_standardized",
            color="experience_level",
            hover_data=["job_title", "company"],
            title="🎓 Required Experience vs. Standardized Annual Salary",
            labels={"min_experience": "Required Experience (Years)", "salary_standardized": "Standardized Salary ($)", "experience_level": "Experience Category"}
        )
        # Fit trend line using NumPy safely
        try:
            x_vals = scatter_data["min_experience"].values
            y_vals = scatter_data["salary_standardized"].values
            if len(x_vals) > 1:
                slope, intercept = np.polyfit(x_vals, y_vals, 1)
                x_line = np.array([x_vals.min(), x_vals.max()])
                y_line = slope * x_line + intercept
                
                fig_scatter.add_trace(go.Scatter(
                    x=x_line, y=y_line, mode="lines",
                    name="Trendline",
                    line=dict(color="#EF4444", dash="dash", width=2)
                ))
        except Exception:
            pass
            
        fig_scatter.update_layout(
            xaxis_title="Required Years of Experience",
            yaxis_title="Standardized Annual Salary ($)",
            margin=dict(l=10, r=10, t=40, b=10),
            title_font=dict(size=16, family="Inter, sans-serif")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No postings containing both disclosed salary and experience requirements match the selected filters.")

# ---------------------------------------------------------------------------
# Tab 4: Job Explorer
# ---------------------------------------------------------------------------
with tab_explorer:
    st.markdown("### 🔍 Interactive Job Posting Explorer")
    st.markdown("Search and browse through individual job postings matching your current filter criteria. Use the search bar to filter by text, select a job, and view the complete raw description below.")
    
    search_query = st.text_input(
        "🔍 Search job title, company name, location, or description:",
        placeholder="e.g. SQL, healthcare, Chase, Chicago..."
    )
    
    # Filter Explorer dataset
    explorer_df = filtered_df.copy()
    if search_query:
        q = search_query.lower()
        explorer_df = explorer_df[
            explorer_df["job_title"].str.lower().str.contains(q, na=False) |
            explorer_df["company"].str.lower().str.contains(q, na=False) |
            explorer_df["job_description"].str.lower().str.contains(q, na=False) |
            explorer_df["location"].str.lower().str.contains(q, na=False)
        ]
        
    st.write(f"Displaying **{len(explorer_df)}** matching jobs out of **{len(filtered_df)}** filtered postings.")
    
    if not explorer_df.empty:
        # 1. Format table for display
        display_df = explorer_df[[
            "job_title", "company", "location", "work_mode_from_text", "salary", "skill_count", "seniority_level"
        ]].copy()
        display_df.columns = [
            "Job Title", "Company", "Location", "Work Mode", "Salary Disclosed", "Skills Count", "Seniority"
        ]
        st.dataframe(display_df, use_container_width=True, height=280)
        
        # 2. Select Job to view details
        job_options = []
        for idx, row in explorer_df.iterrows():
            job_options.append(f"{row['job_title']} at {row['company']} (ID: {row['index']})")
            
        selected_option = st.selectbox(
            "👉 Select a job posting to inspect in detail:", 
            options=job_options
        )
        
        if selected_option:
            selected_id = int(selected_option.split(" (ID: ")[-1][:-1])
            selected_job = explorer_df[explorer_df["index"] == selected_id].iloc[0]
            
            st.markdown("---")
            st.markdown(f"### {selected_job['job_title']}")
            
            # Details columns
            col_det1, col_det2 = st.columns([1, 2])
            with col_det1:
                st.markdown(f"""
                <div style="background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.2); padding: 15px; border-radius: 8px; font-family: 'Inter', sans-serif;">
                    <h4 style="margin-top: 0; margin-bottom: 12px; border-bottom: 1px solid rgba(128,128,128,0.15); padding-bottom: 4px;">Job Metadata</h4>
                    <p style="margin: 4px 0;"><b>🏢 Company:</b> {selected_job['company']}</p>
                    <p style="margin: 4px 0;"><b>📍 Location:</b> {selected_job['location']}</p>
                    <p style="margin: 4px 0;"><b>🌐 Work Mode:</b> {selected_job['work_mode_from_text']}</p>
                    <p style="margin: 4px 0;"><b>⏱️ Type:</b> {selected_job['employment_type'] if pd.notna(selected_job['employment_type']) else 'Not Specified'}</p>
                    <p style="margin: 4px 0;"><b>💰 Salary:</b> {selected_job['salary'] if pd.notna(selected_job['salary']) else 'Not Disclosed'}</p>
                    <p style="margin: 4px 0;"><b>🎓 Experience:</b> {selected_job['min_experience'] if pd.notna(selected_job['min_experience']) else 'Not Specified'} years min</p>
                    <p style="margin: 4px 0;"><b>📈 Seniority:</b> {selected_job['seniority_level']}</p>
                    <p style="margin: 4px 0;"><b>📅 Posted:</b> {selected_job['posted_date'] if pd.notna(selected_job['posted_date']) else 'Not Specified'}</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col_det2:
                st.markdown("#### 🛠️ Detected Technical Skills")
                
                # Filter skills detected in this job
                skills_present = [s for s in SKILL_COLUMNS if selected_job.get(s.replace(' ', '_'), 0) == 1]
                
                if skills_present:
                    badges_html = ""
                    for s in skills_present:
                        badges_html += f'<span style="display: inline-block; background-color: rgba(99, 102, 241, 0.1); color: #4F46E5; border: 1px solid rgba(99, 102, 241, 0.25); padding: 4px 10px; border-radius: 9999px; font-size: 13px; font-weight: 600; margin: 3px; font-family: Inter, sans-serif;">{s.replace("_", " ")}</span>'
                    st.markdown(badges_html, unsafe_allow_html=True)
                else:
                    st.info("No controlled skills from list were detected in the description.")
                    
                st.markdown("<br><b>🔗 Source Posting Platform:</b>", unsafe_allow_html=True)
                st.write(selected_job["source"])
                
            st.markdown("<br>#### 📄 Full Description Text", unsafe_allow_html=True)
            with st.expander("Expand to read full description text", expanded=True):
                st.markdown(selected_job["job_description"])
    else:
        st.info("No matching job postings found. Try adjusting your search query.")

# Footer caption
st.markdown("---")
st.caption(
    "Data source: Kaggle - Data Analyst Job Postings dataset "
    "(random sample, see data/source_notes.md for details)."
)
