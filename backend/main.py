from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
app = FastAPI(title="Job Market Intelligence API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

df = pd.read_csv("../data/cleaned_jobs.csv")

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
        df["normalized_title"]
        .dropna()
        .value_counts()
        .reset_index()
    )

    roles.columns = ["role", "job_count"]

    return roles.to_dict(orient="records")