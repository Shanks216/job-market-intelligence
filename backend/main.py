from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import ast
import pandas as pd
app = FastAPI(title="Job Market Intelligence API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

df = pd.read_csv(DATA_DIR / "cleaned_jobs.csv")
role_intelligence_df = pd.read_csv(DATA_DIR / "role_intelligence.csv")
role_city_df = pd.read_csv(DATA_DIR / "role_city_counts.csv")
skill_demand_df = pd.read_csv(DATA_DIR / "skill_demand.csv")
skill_pairs_df = pd.read_csv(DATA_DIR / "skill_pairs.csv")
city_intelligence_df = pd.read_csv(DATA_DIR / "city_intelligence.csv")
role_ranking_df = pd.read_csv(DATA_DIR / "role_ranking.csv")
@app.get("/")
def home():
    return {
        "message": "Job Market Intelligence API is running"
    }

@app.get("/api/stats")
def get_stats():
    total_jobs = len(df)
    job_roles = df["normalized_title"].nunique()
    skills = set()

    for value in df["tags_and_skills"].dropna():
        for skill in str(value).split(","):
            skill = skill.strip()
            if skill:
                skills.add(skill)

    return {
        "total_jobs": total_jobs,
        "job_roles": job_roles,
        "skills": len(skills)
    }

@app.get("/api/roles")
def get_roles():
    roles = (
        role_intelligence_df[
            ["role", "job_count"]
        ]
        .dropna()
        .sort_values("job_count", ascending=False)
    )

    return roles.to_dict(orient="records")

@app.get("/api/rankings")
def get_rankings():
    result = role_ranking_df.sort_values(
        by="opportunity_score",
        ascending=False
    )

    return result.to_dict(orient="records")

def parse_top_skills(value):
    if not isinstance(value, str):
        return []

    try:
        skills = ast.literal_eval(value)

        if isinstance(skills, list):
            return skills

    except (ValueError, SyntaxError):
        pass

    return []
@app.get("/api/roles/{role_name:path}")
def get_role_details(role_name: str):
    requested_role = (
        role_name
        .strip()
        .lower()
        .replace(" ", "")
    )

    matches = role_intelligence_df[
        role_intelligence_df["role"]
        .astype(str)
        .str.lower()
        .str.replace(" ", "", regex=False)
        == requested_role
    ]

    if matches.empty:
        return {"error": "Role not found"}

    role = matches.iloc[0]

    cities = role_city_df[
        role_city_df["role"]
        .astype(str)
        .str.lower()
        .str.replace(" ", "", regex=False)
        == requested_role
    ].copy()

    cities["job_count"] = pd.to_numeric(
        cities["job_count"],
        errors="coerce"
    ).fillna(0)

    cities = (
        cities
        .sort_values("job_count", ascending=False)
        .head(10)
    )

    top_locations = [
        {
            "city": str(row["city"]),
            "job_count": int(row["job_count"])
        }
        for _, row in cities.iterrows()
    ]

    return {
        "role": str(role["role"]),
        "job_count": int(role["job_count"]),
        "demand_percent": float(role["demand_percent"]),
        "salary_job_count": int(role["salary_job_count"]),
        "avg_salary_lpa": float(role["avg_salary_lpa"]),
        "median_salary_lpa": float(role["median_salary_lpa"]),
        "top_skills": parse_top_skills(role["top_skills"]),
        "salary_score": float(role["salary_score"]),
        "demand_score": float(role["demand_score"]),
        "opportunity_score": float(role["opportunity_score"]),
        "top_locations": top_locations
    }
@app.get("/api/skills")
def get_skills():
    skills = (
        skill_demand_df[
            ["skill_name", "job_count", "demand_percent"]
        ]
        .dropna()
        .sort_values("job_count", ascending=False)
        .head(100)
    )

    return skills.to_dict(orient="records")


@app.get("/api/skills/{skill_name:path}")
def get_skill_details(skill_name: str):
    requested_skill = (
        skill_name
        .strip()
        .lower()
        .replace(" ", "")
    )

    matches = skill_demand_df[
        skill_demand_df["skill_name"]
        .astype(str)
        .str.lower()
        .str.replace(" ", "", regex=False)
        == requested_skill
    ]

    if matches.empty:
        return {"error": "Skill not found"}

    skill = matches.iloc[0]

    pairs = skill_pairs_df[
        (
            skill_pairs_df["skill_1"]
            .astype(str)
            .str.lower()
            .str.replace(" ", "", regex=False)
            == requested_skill
        )
        |
        (
            skill_pairs_df["skill_2"]
            .astype(str)
            .str.lower()
            .str.replace(" ", "", regex=False)
            == requested_skill
        )
    ].copy()

    related_skills = []

    for _, row in pairs.iterrows():
        skill_1 = str(row["skill_1"])
        skill_2 = str(row["skill_2"])

        if (
            skill_1.lower().replace(" ", "")
            == requested_skill
        ):
            related_skill = skill_2
        else:
            related_skill = skill_1

        related_skills.append({
            "skill": related_skill,
            "job_count": int(row["job_count"]),
            "avg_salary_lpa": float(row["avg_salary_lpa"]),
            "median_salary_lpa": float(
                row["median_salary_lpa"]
            )
        })

    related_skills = sorted(
        related_skills,
        key=lambda x: x["job_count"],
        reverse=True
    )[:10]

    return {
        "skill_name": str(skill["skill_name"]),
        "job_count": int(skill["job_count"]),
        "demand_percent": float(skill["demand_percent"]),
        "related_skills": related_skills
    }
@app.get("/api/locations")
def get_locations():
    result = city_intelligence_df.copy()
    result = result.sort_values(
        by="job_count",
        ascending=False
    )
    return result.head(100).to_dict(
        orient="records"
    )
