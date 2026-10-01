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
role_intelligence_df = pd.read_csv(
    DATA_DIR / "role_intelligence.csv"
)
role_city_df = pd.read_csv(
    DATA_DIR / "role_city_counts.csv"
)
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