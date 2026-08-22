import streamlit as st
import pandas as pd
import ast
import os
import re


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Job Market Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# STYLE
# ============================================================

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


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_columns(df):
    df = df.copy()

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace("\ufeff", "", regex=False)
    )

    return df


def read_csv_safe(path):
    if not os.path.exists(path):
        return pd.DataFrame()

    if os.path.getsize(path) == 0:
        return pd.DataFrame()

    try:
        return clean_columns(pd.read_csv(path))
    except Exception as e:
        st.warning(f"Could not read {path}: {e}")
        return pd.DataFrame()


def first_col(df, possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    return None


def num(value, default=0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
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
    except Exception:
        pass

    if isinstance(value, str):
        try:
            result = ast.literal_eval(value)

            if isinstance(result, list):
                return result

        except Exception:
            pass

    return []


def normalize_text(value):
    if pd.isna(value):
        return ""

    text = str(value).lower()
    text = re.sub(r"[^a-z0-9+# ]+", " ", text)

    return re.sub(r"\s+", " ", text).strip()


# ============================================================
# ROLE INFERENCE
# ============================================================

def infer_role(title):

    text = normalize_text(title)

    rules = [
        (
            "Data Scientist",
            [
                "data scientist",
                "machine learning scientist"
            ]
        ),

        (
            "Data Engineer",
            [
                "data engineer",
                "big data engineer",
                "etl developer"
            ]
        ),

        (
            "Data Analyst",
            [
                "data analyst"
            ]
        ),

        (
            "Cloud Engineer",
            [
                "cloud engineer",
                "cloud architect"
            ]
        ),

        (
            "DevOps Engineer",
            [
                "devops",
                "dev ops",
                "site reliability engineer",
                "sre"
            ]
        ),

        (
            "QA / Testing",
            [
                "qa",
                "quality assurance",
                "tester",
                "test engineer",
                "testing"
            ]
        ),

        (
            "Project Manager",
            [
                "project manager",
                "program manager"
            ]
        ),

        (
            "Business Analyst",
            [
                "business analyst"
            ]
        ),

        (
            "Java Developer",
            [
                "java developer",
                "java engineer"
            ]
        ),

        (
            "Python Developer",
            [
                "python developer",
                "python engineer"
            ]
        ),

        (
            "Frontend Developer",
            [
                "frontend developer",
                "front end developer",
                "ui developer"
            ]
        ),

        (
            "Backend Developer",
            [
                "backend developer",
                "back end developer"
            ]
        ),

        (
            "Full Stack Developer",
            [
                "full stack developer",
                "fullstack developer"
            ]
        ),

        (
            "Software Engineer",
            [
                "software engineer"
            ]
        ),

        (
            "Software Developer",
            [
                "software developer",
                "application developer"
            ]
        ),
    ]

    for role, keywords in rules:

        for keyword in keywords:

            if keyword in text:
                return role

    return None


# ============================================================
# ROLE-CITY DATA
# ============================================================

def prepare_role_city(df):

    if df.empty:
        return pd.DataFrame(
            columns=["role", "city", "job_count"]
        )

    role_col = first_col(
        df,
        [
            "role",
            "normalized_role",
            "job_role"
        ]
    )

    city_col = first_col(
        df,
        [
            "city_clean",
            "city",
            "location",
            "location_clean"
        ]
    )

    count_col = first_col(
        df,
        [
            "job_count",
            "count",
            "jobs"
        ]
    )

    if not role_col or not city_col or not count_col:

        return pd.DataFrame(
            columns=["role", "city", "job_count"]
        )

    result = df[
        [
            role_col,
            city_col,
            count_col
        ]
    ].copy()

    result.columns = [
        "role",
        "city",
        "job_count"
    ]

    result["job_count"] = pd.to_numeric(
        result["job_count"],
        errors="coerce"
    ).fillna(0)

    return result.dropna(
        subset=["role", "city"]
    )


def derive_role_city(jobs):

    if jobs.empty:
        return pd.DataFrame(
            columns=["role", "city", "job_count"]
        )

    title_col = first_col(
        jobs,
        [
            "normalized_title",
            "title",
            "job_title"
        ]
    )

    city_col = first_col(
        jobs,
        [
            "city_clean",
            "city",
            "location"
        ]
    )

    if not title_col or not city_col:

        return pd.DataFrame(
            columns=["role", "city", "job_count"]
        )

    temp = jobs[
        [
            title_col,
            city_col
        ]
    ].copy()

    temp["role"] = temp[
        title_col
    ].map(infer_role)

    temp["city"] = (
        temp[city_col]
        .astype(str)
        .str.strip()
    )

    temp = temp[
        temp["role"].notna()
        &
        temp["city"].notna()
        &
        (temp["city"] != "")
        &
        (temp["city"].str.lower() != "nan")
    ]

    return (
        temp
        .groupby(
            ["role", "city"],
            as_index=False
        )
        .size()
        .rename(
            columns={
                "size": "job_count"
            }
        )
    )


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    files = {
        "role_intelligence":
            "data/role_intelligence.csv",

        "role_ranking":
            "data/role_ranking.csv",

        "skill_demand":
            "data/skill_demand.csv",

        "city_intelligence":
            "data/city_intelligence.csv",

        "skill_pairs":
            "data/skill_pairs.csv",

        "role_city_counts":
            "data/role_city_counts.csv",

        "cleaned_jobs":
            "data/cleaned_jobs.csv",
    }

    data = {}

    for name, path in files.items():
        data[name] = read_csv_safe(path)

    role_city = prepare_role_city(
        data["role_city_counts"]
    )

    # If role_city_counts.csv is empty,
    # derive it from cleaned_jobs.csv.
    if role_city.empty:
        role_city = derive_role_city(
            data["cleaned_jobs"]
        )

    data["role_city_counts"] = role_city

    return data


data = load_data()

role_intelligence = data[
    "role_intelligence"
]

role_ranking = data[
    "role_ranking"
]

skill_demand = data[
    "skill_demand"
]

city_intelligence = data[
    "city_intelligence"
]

skill_pairs = data[
    "skill_pairs"
]

role_city_counts = data[
    "role_city_counts"
]


# ============================================================
# VALIDATE ROLE DATA
# ============================================================

required_role_columns = [
    "role",
    "job_count",
    "demand_percent",
    "salary_job_count",
    "avg_salary_lpa",
    "median_salary_lpa",
    "top_skills",
]

missing_columns = [
    column
    for column in required_role_columns
    if column not in role_intelligence.columns
]

if missing_columns:

    st.error(
        "role_intelligence.csv is missing: "
        + ", ".join(missing_columns)
    )

    st.stop()


# ============================================================
# GLOBAL STATISTICS
# ============================================================

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

city_column = first_col(
    city_intelligence,
    [
        "city_clean",
        "city",
        "location"
    ]
)

total_cities = (
    city_intelligence[
        city_column
    ].nunique()
    if city_column
    else 0
)


# ============================================================
# SIDEBAR
# ============================================================

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


# ============================================================
# 1. MARKET OVERVIEW
# ============================================================

if page == "Market Overview":

    st.title(
        "📊 Job Market Intelligence"
    )

    st.caption(
        "Demand, salaries, skills and career "
        "opportunities across the analyzed "
        "Indian job market."
    )

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # TOP ROLES + TOP SKILLS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # DEMAND VS SALARY
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # TOP OPPORTUNITIES
    # --------------------------------------------------------

    st.subheader(
        "🏆 Top Career Opportunities"
    )

    score_col = first_col(
        role_ranking,
        [
            "opportunity_score",
            "score"
        ]
    )

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


# ============================================================
# 2. CAREER EXPLORER
# ============================================================

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

    # --------------------------------------------------------
    # TOP SKILLS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # BEST LOCATIONS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # SALARY
    # --------------------------------------------------------

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


# ============================================================
# 3. SKILL INTELLIGENCE
# ============================================================

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

    # --------------------------------------------------------
    # TOP SKILLS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # SKILL EXPLORER
    # --------------------------------------------------------

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

        # Derive demand share
        # from job_count because your
        # skill_demand.csv does not
        # contain demand_percent.

        skill_total = pd.to_numeric(
            skill_demand["job_count"],
            errors="coerce"
        ).fillna(0).sum()

        demand_share = (
            num(row["job_count"])
            / max(skill_total, 1)
            * 100
        )

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

    # ========================================================
    # HIGH DEMAND + HIGH SALARY
    # ========================================================

    st.subheader(
        "💎 High-Demand + High-Salary Skills"
    )

    # --------------------------------------------------------
    # YOUR ACTUAL CSV SCHEMA IS:
    #
    # skill_name
    # job_count
    # avg_salary
    # median_salary
    #
    # There is NO demand_percent column.
    #
    # Therefore we calculate demand percentage
    # ourselves from job_count.
    # --------------------------------------------------------

    if (
        not skill_demand.empty
        and "skill_name"
        in skill_demand.columns
        and "job_count"
        in skill_demand.columns
        and "median_salary"
        in skill_demand.columns
    ):

        market = skill_demand.copy()

        market[
            "job_count"
        ] = pd.to_numeric(
            market["job_count"],
            errors="coerce"
        )

        market[
            "median_salary"
        ] = pd.to_numeric(
            market["median_salary"],
            errors="coerce"
        )

        market = market.dropna(
            subset=[
                "skill_name",
                "job_count",
                "median_salary"
            ]
        )

        # ----------------------------------------------------
        # DEMAND %
        # ----------------------------------------------------

        total_skill_jobs = (
            market["job_count"].sum()
        )

        if total_skill_jobs > 0:

            market[
                "demand_percent"
            ] = (
                market["job_count"]
                / total_skill_jobs
                * 100
            )

        else:

            market[
                "demand_percent"
            ] = 0

        # ----------------------------------------------------
        # SALARY → LPA
        # ----------------------------------------------------

        market[
            "median_salary_lpa"
        ] = (
            market["median_salary"]
            / 100000
        )

        # ----------------------------------------------------
        # THRESHOLDS
        # ----------------------------------------------------

        demand_threshold = (
            market[
                "demand_percent"
            ].median()
        )

        salary_threshold = (
            market[
                "median_salary_lpa"
            ].median()
        )

        # ----------------------------------------------------
        # SWEET SPOT
        # ----------------------------------------------------

        sweet_spot = market[
            (
                market["demand_percent"]
                >= demand_threshold
            )
            &
            (
                market["median_salary_lpa"]
                >= salary_threshold
            )
        ].copy()

        sweet_spot = (
            sweet_spot
            .sort_values(
                [
                    "median_salary_lpa",
                    "demand_percent"
                ],
                ascending=False
            )
            .head(15)
        )

        # ----------------------------------------------------
        # DISPLAY TABLE
        # ----------------------------------------------------

        display = sweet_spot[
            [
                "skill_name",
                "job_count",
                "demand_percent",
                "median_salary_lpa"
            ]
        ].copy()

        display.columns = [
            "Skill",
            "Job Count",
            "Demand %",
            "Median Salary (LPA)"
        ]

        display[
            "Demand %"
        ] = display[
            "Demand %"
        ].round(2)

        display[
            "Median Salary (LPA)"
        ] = display[
            "Median Salary (LPA)"
        ].round(2)

        if display.empty:

            st.info(
                "No skills currently fall into "
                "both the high-demand and "
                "high-salary groups."
            )

        else:

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True
            )

        st.caption(
            f"High demand = above "
            f"{demand_threshold:.2f}% "
            f"skill-share. "
            f"High salary = above "
            f"₹{salary_threshold:.2f} LPA median."
        )

    else:

        st.error(
            "skill_demand.csv does not have "
            "the expected columns."
        )

        st.write(
            "Columns actually loaded:"
        )

        st.code(
            str(
                skill_demand.columns.tolist()
            )
        )

    st.divider()

    # --------------------------------------------------------
    # SKILL PAIRS
    # --------------------------------------------------------

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


# ============================================================
# 4. LOCATION INTELLIGENCE
# ============================================================

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

    city_col = first_col(
        city_intelligence,
        [
            "city_clean",
            "city",
            "location"
        ]
    )

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

    count_col = first_col(
        city_intelligence,
        [
            "job_count",
            "count",
            "jobs"
        ]
    )

    avg_col = first_col(
        city_intelligence,
        [
            "avg_salary_lpa",
            "avg_salary"
        ]
    )

    median_col = first_col(
        city_intelligence,
        [
            "median_salary_lpa",
            "median_salary"
        ]
    )

    # --------------------------------------------------------
    # CITY SELECTOR
    # --------------------------------------------------------

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

            if avg_col == "avg_salary":
                avg /= 100000

            c2.metric(
                "💰 Average Salary",
                money_lpa(avg)
            )

        if median_col:

            median = num(
                row[median_col]
            )

            if median_col == "median_salary":
                median /= 100000

            c3.metric(
                "📊 Median Salary",
                money_lpa(median)
            )

    st.divider()

    # --------------------------------------------------------
    # CITY DEMAND
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CITY TABLE
    # --------------------------------------------------------

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


# ============================================================
# 5. CAREER RANKING
# ============================================================

elif page == "Career Ranking":

    st.title(
        "🏆 Career Opportunity Ranking"
    )

    st.caption(
        "Compare careers using demand, "
        "salary and opportunity scores."
    )

    if role_ranking.empty:

        st.error(
            "role_ranking.csv could not "
            "be loaded."
        )

        st.stop()

    score_col = first_col(
        role_ranking,
        [
            "opportunity_score",
            "score"
        ]
    )

    if not score_col:

        st.error(
            "No opportunity-score column "
            "was found."
        )

        st.write(
            "Available columns:",
            list(
                role_ranking.columns
            )
        )

        st.stop()

    ranking = (
        role_ranking
        .sort_values(
            score_col,
            ascending=False
        )
        .copy()
    )

    # --------------------------------------------------------
    # BEST ROLE
    # --------------------------------------------------------

    best = ranking.iloc[0]

    st.success(
        f"""
🥇 **Top Career Opportunity:
{best['role']}**

Opportunity Score:
**{num(best[score_col]):.2f}**
"""
    )

    st.divider()

    # --------------------------------------------------------
    # SCORE CHART
    # --------------------------------------------------------

    st.subheader(
        "📊 Opportunity Score"
    )

    st.bar_chart(
        ranking.head(15)[
            [
                "role",
                score_col
            ]
        ].set_index(
            "role"
        )
    )

    st.divider()

    # --------------------------------------------------------
    # FULL RANKING
    # --------------------------------------------------------

    st.subheader(
        "📋 Complete Career Ranking"
    )

    st.dataframe(
        ranking,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # --------------------------------------------------------
    # CAREER COMPARISON
    # --------------------------------------------------------

    st.subheader(
        "⚖️ Compare Careers"
    )

    available_roles = sorted(
        role_ranking[
            "role"
        ]
        .dropna()
        .astype(str)
        .unique()
    )

    default_roles = (
        available_roles[:3]
    )

    compare = st.multiselect(
        "Select up to 5 roles",
        available_roles,
        default=default_roles,
        max_selections=5
    )

    if compare:

        comparison = role_ranking[
            role_ranking[
                "role"
            ].isin(compare)
        ].copy()

        columns = [
            c for c in [
                "role",
                "job_count",
                "demand_percent",
                "avg_salary_lpa",
                "median_salary_lpa",
                "salary_score",
                "demand_score",
                "opportunity_score"
            ]
            if c in comparison.columns
        ]

        st.dataframe(
            comparison[
                columns
            ],
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "Python • Pandas • Streamlit"
)