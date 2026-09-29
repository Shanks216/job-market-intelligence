import streamlit as st
import pandas as pd
import ast
import os
import re
st.set_page_config(
    page_title="Job Market Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("""
<style>
.block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}
[data-testid="stMetric"] {
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 12px;
    padding: 12px 15px;
}
</style>
""", unsafe_allow_html=True)
def clean_columns(df):
    df = df.copy()
    df.columns=(
        df.columns
        .astype(str)
        .str.strip()
        .str.replace("\ufeff","",regex=False)
    )
    return df
def load_csv(path):
    return clean_columns(pd.read_csv(path))
def num(value, default=0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default
def integer(value):
    return f"{int(num(value)):,}"
def money_lpa(value):
    return f"₹{num(value):.2f} LPA"
def parse_list(value):
    if isinstance(value, list):
        return value
    if value is None:
        return []
    try:
        if pd.isna(value):
            return []
    except (TypeError, ValueError):
        return []
    if isinstance(value, str):
        try:
            result = ast.literal_eval(value)
            if isinstance(result, list):
                return result
        except (ValueError, SyntaxError):
            pass
    return []
@st.cache_data
def load_data():
    files = {
        "role_intelligence": "data/role_intelligence.csv",
        "role_ranking": "data/role_ranking.csv",
        "skill_demand": "data/skill_demand.csv",
        "city_intelligence": "data/city_intelligence.csv",
        "skill_pairs": "data/skill_pairs.csv",
        "role_city_counts": "data/role_city_counts.csv",
        "cleaned_jobs": "data/cleaned_jobs.csv",
    }
    return {name: load_csv(path) for name, path in files.items()}
data = load_data()
role_intelligence = data["role_intelligence"]
role_ranking = data["role_ranking"]
skill_demand = data["skill_demand"]
city_intelligence = data["city_intelligence"]
skill_pairs = data["skill_pairs"]
role_city_counts = data["role_city_counts"]
required_role_columns = [
    "role",
    "job_count",
    "demand_percent",
    "salary_job_count",
    "avg_salary_lpa",
    "median_salary_lpa",
    "top_skills",
]
if not all(column in role_intelligence.columns for column in required_role_columns):
    st.error("role_intelligence.csv is missing required columns.")
    st.stop()
total_jobs = int(
    pd.to_numeric(
        role_intelligence["job_count"],
        errors="coerce"
    )
    .fillna(0)
    .sum()
)
total_roles = role_intelligence[
    "role"
].nunique()
total_skills = (
    skill_demand[
        "skill_name"
    ].nunique()
    if "skill_name" in skill_demand.columns
    else 0
)
city_column = "city_clean" if "city_clean" in city_intelligence.columns else "city"
total_cities = (
    city_intelligence[
        city_column
    ].nunique()
    if city_column
    else 0
)
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "Market Overview",
        "Career Explorer",
        "Skill Intelligence",
        "Location Intelligence",
        "Career Ranking",
    ]
)
st.sidebar.divider()
st.sidebar.caption(
    "📊 Job Market Intelligence"
)
st.sidebar.caption(
    "Indian job-market analytics"
)
if page == "Market Overview":
    st.title(
        "📊 Job Market Intelligence"
    )
    st.caption(
        "Demand, salaries, skills and career "
        "opportunities across the analyzed "
        "Indian job market."
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "💼 Job Postings",
        integer(total_jobs)
    )
    c2.metric(
        "🎯 Career Roles",
        integer(total_roles)
    )
    c3.metric(
        "🛠️ Skills",
        integer(total_skills)
    )
    c4.metric(
        "📍 Cities",
        integer(total_cities)
    )
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(
            "🔥 Top Roles by Demand"
        )
        top_roles = (
            role_intelligence
            .sort_values(
                "job_count",
                ascending=False
            )
            .head(10)
        )
        st.bar_chart(
            top_roles[
                [
                    "role",
                    "job_count"
                ]
            ].set_index("role")
        )
    with col2:
        st.subheader(
            "🛠️ Most In-Demand Skills"
        )
        if (
            not skill_demand.empty
            and "job_count"
            in skill_demand.columns
        ):
            top_skills = (
                skill_demand
                .sort_values(
                    "job_count",
                    ascending=False
                )
                .head(10)
            )
            st.bar_chart(
                top_skills[
                    [
                        "skill_name",
                        "job_count"
                    ]
                ].set_index(
                    "skill_name"
                )
            )
        else:
            st.info(
                "Skill-demand data unavailable."
            )
    st.divider()
    st.subheader(
        "💰 Demand vs Median Salary"
    )
    scatter = role_intelligence[
        [
            "role",
            "demand_percent",
            "median_salary_lpa"
        ]
    ].copy()
    scatter[
        "demand_percent"
    ] = pd.to_numeric(
        scatter["demand_percent"],
        errors="coerce"
    )
    scatter[
        "median_salary_lpa"
    ] = pd.to_numeric(
        scatter["median_salary_lpa"],
        errors="coerce"
    )
    scatter = scatter.dropna()
    if not scatter.empty:
        st.scatter_chart(
            scatter,
            x="demand_percent",
            y="median_salary_lpa"
        )
    st.divider()
    st.subheader(
        "🏆 Top Career Opportunities"
    )
    score_col = "opportunity_score"
    if score_col:
        top = (
            role_ranking
            .sort_values(
                score_col,
                ascending=False
            )
            .head(10)
        )
        display_columns = [
            c for c in [
                "role",
                "job_count",
                "demand_percent",
                "avg_salary_lpa",
                "median_salary_lpa",
                "salary_score",
                "demand_score",
                score_col
            ]
            if c in top.columns
        ]
        st.dataframe(
            top[display_columns],
            use_container_width=True,
            hide_index=True
        )
elif page == "Career Explorer":
    st.title(
        "💼 Career Explorer"
    )
    st.caption(
        "Explore demand, salary, skills and "
        "locations for a role."
    )
    roles = sorted(
        role_intelligence[
            "role"
        ]
        .dropna()
        .astype(str)
        .unique()
    )
    selected_role = st.selectbox(
        "🎯 Select a career role",
        roles
    )
    role_rows = role_intelligence[
        role_intelligence["role"]
        == selected_role
    ]
    if role_rows.empty:
        st.error(
            "No data found for this role."
        )
        st.stop()
    role = role_rows.iloc[0]
    st.divider()
    st.subheader(
        f"💼 {selected_role}"
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "💼 Job Postings",
        integer(role["job_count"])
    )
    c2.metric(
        "📊 Demand Share",
        f"{num(role['demand_percent']):.2f}%"
    )
    c3.metric(
        "💰 Median Salary",
        money_lpa(
            role["median_salary_lpa"]
        )
    )
    c4.metric(
        "📄 Salary Sample",
        integer(
            role["salary_job_count"]
        )
    )
    st.divider()
    st.subheader(
        f"🔥 Top Skills for {selected_role}"
    )
    skills = parse_list(
        role["top_skills"]
    )
    if skills:
        skill_df = pd.DataFrame(
            skills
        )
        if {
            "skill_name",
            "skill_percent"
        }.issubset(
            skill_df.columns
        ):
            skill_df[
                "skill_percent"
            ] = pd.to_numeric(
                skill_df[
                    "skill_percent"
                ],
                errors="coerce"
            )
            skill_df = (
                skill_df
                .dropna()
                .head(10)
            )
            col1, col2 = st.columns(
                [1.5, 1]
            )
            with col1:
                st.bar_chart(
                    skill_df[
                        [
                            "skill_name",
                            "skill_percent"
                        ]
                    ].set_index(
                        "skill_name"
                    )
                )
            with col2:
                display = skill_df.copy()
                display[
                    "skill_percent"
                ] = display[
                    "skill_percent"
                ].round(2)
                display.columns = [
                    "Skill",
                    "Job %"
                ]
                st.dataframe(
                    display,
                    use_container_width=True,
                    hide_index=True
                )
    else:
        st.info(
            "No skill information available."
        )
    st.divider()
    st.subheader(
        f"📍 Best Locations for {selected_role}"
    )
    if not role_city_counts.empty:
        cities = role_city_counts[
            role_city_counts["role"]
            == selected_role
        ].copy()
        if not cities.empty:
            cities = (
                cities
                .sort_values(
                    "job_count",
                    ascending=False
                )
                .head(10)
            )
            col1, col2 = st.columns(
                [1.5, 1]
            )
            with col1:
                st.bar_chart(
                    cities[
                        [
                            "city",
                            "job_count"
                        ]
                    ].set_index(
                        "city"
                    )
                )
            with col2:
                display = cities[
                    [
                        "city",
                        "job_count"
                    ]
                ].copy()
                display.columns = [
                    "City",
                    "Jobs"
                ]
                st.dataframe(
                    display,
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info(
                f"No city data available "
                f"for {selected_role}."
            )
    else:
        st.warning(
            "Role-city data is unavailable."
        )
    st.divider()
    st.subheader(
        "📈 Salary Positioning"
    )
    avg_salary = num(
        role["avg_salary_lpa"]
    )
    median_salary = num(
        role["median_salary_lpa"]
    )
    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Average Salary",
        money_lpa(avg_salary)
    )
    c2.metric(
        "Median Salary",
        money_lpa(median_salary)
    )
    c3.metric(
        "Average − Median",
        f"₹{avg_salary - median_salary:.2f} LPA"
    )
    st.divider()
    st.subheader(
        "📌 Career Summary"
    )
    st.markdown(
        f"""
**{selected_role}** has **{integer(role["job_count"])}**
job postings, representing
**{num(role["demand_percent"]):.2f}%**
of analyzed role demand.
The median advertised salary is
**{money_lpa(median_salary)}**.
The skill and location sections above highlight
the strongest preparation areas and cities for
this career.
"""
    )
elif page == "Skill Intelligence":
    st.title(
        "🛠️ Skill Intelligence"
    )
    st.caption(
        "Explore skill demand, salary signals "
        "and skill combinations."
    )
    if skill_demand.empty:
        st.error(
            "skill_demand.csv could not be loaded."
        )
        st.stop()
    st.subheader(
        "🔥 Most In-Demand Skills"
    )
    maximum = min(
        30,
        max(
            5,
            len(skill_demand)
        )
    )
    default_value = min(
        15,
        len(skill_demand)
    )
    top_n = st.slider(
        "Skills to display",
        min_value=5,
        max_value=maximum,
        value=default_value
    )
    top_skills = (
        skill_demand
        .sort_values(
            "job_count",
            ascending=False
        )
        .head(top_n)
    )
    st.bar_chart(
        top_skills[
            [
                "skill_name",
                "job_count"
            ]
        ].set_index(
            "skill_name"
        )
    )
    st.divider()
    st.subheader(
        "🔎 Skill Explorer"
    )
    skill_names = sorted(
        skill_demand[
            "skill_name"
        ]
        .dropna()
        .astype(str)
        .unique()
    )
    selected_skill = st.selectbox(
        "Select a skill",
        skill_names
    )
    skill_row = skill_demand[
        skill_demand["skill_name"]
        == selected_skill
    ]
    if not skill_row.empty:
        row = skill_row.iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric(
            "💼 Job Count",
            integer(
                row["job_count"]
            )
        )
        demand_share = num(row["demand_percent"])
        c2.metric(
            "📊 Skill Demand Share",
            f"{demand_share:.2f}%"
        )
        if "median_salary" in skill_demand.columns:
            salary_lpa = (
                num(
                    row["median_salary"]
                ) / 100000
            )
            c3.metric(
                "💰 Median Salary",
                money_lpa(salary_lpa)
            )
    st.divider()
    st.subheader(
        "🔗 Valuable Skill Combinations"
    )
    if not skill_pairs.empty:
        st.dataframe(
            skill_pairs.head(20),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(
            "skill_pairs.csv is unavailable."
        )
elif page == "Location Intelligence":
    st.title(
        "📍 Location Intelligence"
    )
    st.caption(
        "Compare job demand and salary "
        "patterns across cities."
    )
    if city_intelligence.empty:
        st.error(
            "city_intelligence.csv could not "
            "be loaded."
        )
        st.stop()
    city_col = "city_clean" if "city_clean" in city_intelligence.columns else "city"
    if not city_col:
        st.error(
            "Could not identify the city column."
        )
        st.write(
            "Available columns:",
            list(
                city_intelligence.columns
            )
        )
        st.stop()
    count_col = "job_count"
    avg_col = "avg_salary_lpa"
    median_col = "median_salary_lpa"
    cities = sorted(
        city_intelligence[
            city_col
        ]
        .dropna()
        .astype(str)
        .unique()
    )
    selected_city = st.selectbox(
        "📍 Select a city",
        cities
    )
    city_rows = city_intelligence[
        city_intelligence[
            city_col
        ].astype(str)
        == selected_city
    ]
    if not city_rows.empty:
        row = city_rows.iloc[0]
        c1, c2, c3 = st.columns(3)
        if count_col:
            c1.metric(
                "💼 Jobs",
                integer(
                    row[count_col]
                )
            )
        if avg_col:
            avg = num(
                row[avg_col]
            )
            c2.metric(
                "💰 Average Salary",
                money_lpa(avg)
            )
        if median_col:
            median = num(
                row[median_col]
            )
            c3.metric(
                "📊 Median Salary",
                money_lpa(median)
            )
    st.divider()
    st.subheader(
        "🏙️ Cities by Job Demand"
    )
    if count_col:
        top_cities = (
            city_intelligence
            .sort_values(
                count_col,
                ascending=False
            )
            .head(15)
        )
        st.bar_chart(
            top_cities[
                [
                    city_col,
                    count_col
                ]
            ].set_index(
                city_col
            )
        )
    else:
        st.info(
            "Job-count column unavailable."
        )
    st.divider()
    st.subheader(
        "💰 City Salary Comparison"
    )
    columns = [
        c for c in [
            city_col,
            "job_count",
            "avg_salary_lpa",
            "median_salary_lpa",
            "demand_percent"
        ]
        if c in city_intelligence.columns
    ]
    if columns:
        table = (
            city_intelligence[
                columns
            ]
            .sort_values(
                "job_count",
                ascending=False
            )
            .head(30)
        )
        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True
        )
elif page == "Career Ranking":
    st.title("🏆 Career Ranking")
    st.caption(
        "Compare career roles using job demand and salary metrics."
    )
    if role_ranking.empty:
        st.error("role_ranking.csv could not be loaded.")
        st.stop()
    score_col = "opportunity_score"
    if score_col not in role_ranking.columns:
        st.error("Opportunity score data is unavailable.")
        st.stop()
    ranking = (
        role_ranking
        .sort_values(
            score_col,
            ascending=False
        )
        .copy()
    )
    st.subheader("📊 Opportunity Score")
    st.bar_chart(
        ranking.head(15)[
            [
                "role",
                score_col
            ]
        ].set_index("role")
    )
    st.divider()
    st.subheader("📋 Career Ranking")
    columns = [
        c for c in [
            "role",
            "job_count",
            "demand_percent",
            "avg_salary_lpa",
            "median_salary_lpa",
            score_col
        ]
        if c in ranking.columns
    ]
    st.dataframe(
        ranking[columns],
        use_container_width=True,
        hide_index=True
    )
    st.divider()
    st.subheader("⚖️ Compare Careers")
    available_roles = sorted(
        role_ranking["role"]
        .dropna()
        .astype(str)
        .unique()
    )
    compare = st.multiselect(
        "Select up to 5 roles",
        available_roles,
        max_selections=5
    )
    if compare:
        comparison = role_ranking[
            role_ranking["role"].isin(compare)
        ].copy()
        columns = [
            c for c in [
                "role",
                "job_count",
                "demand_percent",
                "avg_salary_lpa",
                "median_salary_lpa",
                "opportunity_score"
            ]
            if c in comparison.columns
        ]
        st.dataframe(
            comparison[columns],
            use_container_width=True,
            hide_index=True
        )
st.sidebar.divider()
st.sidebar.caption(
    "Python • Pandas • Streamlit"
)
