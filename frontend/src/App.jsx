import { useEffect, useState } from "react"
import {
  getStats,
  getRoles,
  getRoleDetails
} from "./services/api"
import "./App.css"

function App() {
  const [page, setPage] = useState("Dashboard")

  const pages = [
    "Dashboard",
    "Career Explorer",
    "Skill Intelligence",
    "Location Intelligence",
    "Career Ranking"
  ]

  return (
    <div className="app">
      <header className="topbar">
        <h1>Job Market Intelligence</h1>
      </header>

      <div className="layout">
        <aside className="sidebar">
          <nav>
            {pages.map((item) => (
              <button
                key={item}
                className={page === item ? "active" : ""}
                onClick={() => setPage(item)}
              >
                {item}
              </button>
            ))}
          </nav>
        </aside>

        <main className="content">
          {page === "Dashboard" && <Dashboard />}
          {page === "Career Explorer" && <CareerExplorer />}
          {page === "Skill Intelligence" && <SkillIntelligence />}
          {page === "Location Intelligence" && <LocationIntelligence />}
          {page === "Career Ranking" && <CareerRanking />}
        </main>
      </div>
    </div>
  )
}

function Dashboard() {
  const [stats, setStats] = useState({
    total_jobs: 0,
    job_roles: 0,
    skills: 0
  })

  useEffect(() => {
    getStats()
      .then((data) => setStats(data))
      .catch((error) =>
        console.error("Failed to load stats:", error)
      )
  }, [])

  return (
    <>
      <h2>Job Market Overview</h2>

      <p className="subtitle">
        Explore jobs, skills, salaries, and career opportunities.
      </p>

      <div className="stats">
        <div className="card">
          <span>Total Jobs</span>
          <strong>{stats.total_jobs}</strong>
        </div>

        <div className="card">
          <span>Job Roles</span>
          <strong>{stats.job_roles}</strong>
        </div>

        <div className="card">
          <span>Skills</span>
          <strong>{stats.skills}</strong>
        </div>
      </div>

      <div className="section">
        <h3>Market Analysis</h3>
        <p>Charts and analysis will appear here.</p>
      </div>
    </>
  )
}

function CareerExplorer() {
  const [roles, setRoles] = useState([])
  const [search, setSearch] = useState("")
  const [selectedRole, setSelectedRole] = useState(null)
  const [roleDetails, setRoleDetails] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    getRoles()
      .then((data) => setRoles(data))
      .catch((error) =>
        console.error("Failed to load roles:", error)
      )
  }, [])

  const handleRoleClick = async (role) => {
    setSelectedRole(role)
    setRoleDetails(null)
    setError("")
    setLoading(true)

    try {
      const data = await getRoleDetails(role)

      if (data.error) {
        setError(data.error)
      } else {
        setRoleDetails(data)
      }
    } catch (error) {
      console.error("Failed to load role details:", error)

      setError(
        error.response?.data?.detail ||
        error.message ||
        "Failed to load role details."
      )
    } finally {
      setLoading(false)
    }
  }

  if (selectedRole) {
    return (
      <>
        <button
          className="back-button"
          onClick={() => {
            setSelectedRole(null)
            setRoleDetails(null)
            setError("")
          }}
        >
          ← Back to Career Explorer
        </button>

        <h2>{selectedRole}</h2>

        {loading && (
          <p className="loading">
            Loading role details...
          </p>
        )}

        {error && !loading && (
          <div className="detail-section">
            <h3>Unable to load role details</h3>
            <p>
              <strong>Error:</strong> {error}
            </p>
            <p>
              The role exists in Career Explorer, but detailed
              information could not be retrieved from the backend.
            </p>
          </div>
        )}

        {roleDetails &&
          !roleDetails.error &&
          !loading && (
            <>
              <p className="subtitle">
                Detailed career intelligence for this role.
              </p>

              <div className="stats">
                <div className="card">
                  <span>Job Demand</span>
                  <strong>{roleDetails.job_count}</strong>
                </div>

                <div className="card">
                  <span>Average Salary</span>
                  <strong>
                    ₹{roleDetails.avg_salary_lpa} LPA
                  </strong>
                </div>

                <div className="card">
                  <span>Median Salary</span>
                  <strong>
                    ₹{roleDetails.median_salary_lpa} LPA
                  </strong>
                </div>
              </div>

              <div className="detail-grid">
                <div className="detail-section">
                  <h3>Career Scores</h3>

                  <p>
                    Demand Score:{" "}
                    <strong>
                      {Number(roleDetails.demand_score).toFixed(1)}
                    </strong>
                  </p>

                  <p>
                    Salary Score:{" "}
                    <strong>
                      {Number(roleDetails.salary_score).toFixed(1)}
                    </strong>
                  </p>

                  <p>
                    Opportunity Score:{" "}
                    <strong>
                      {Number(
                        roleDetails.opportunity_score
                      ).toFixed(1)}
                    </strong>
                  </p>
                </div>

                <div className="detail-section">
                  <h3>Demand</h3>

                  <p>
                    Demand Percentage:{" "}
                    <strong>
                      {roleDetails.demand_percent}%
                    </strong>
                  </p>

                  <p>
                    Jobs with salary data:{" "}
                    <strong>
                      {roleDetails.salary_job_count}
                    </strong>
                  </p>
                </div>
              </div>

              <div className="detail-section">
                <h3>Top Skills</h3>

                {roleDetails.top_skills &&
                roleDetails.top_skills.length > 0 ? (
                  roleDetails.top_skills.map((skill) => (
                    <div
                      className="skill-row"
                      key={skill.skill_name}
                    >
                      <span>{skill.skill_name}</span>
                      <strong>{skill.skill_percent}%</strong>
                    </div>
                  ))
                ) : (
                  <p>No skill information available.</p>
                )}
              </div>

              <div className="detail-section">
                <h3>Top Locations</h3>

                {roleDetails.top_locations &&
                roleDetails.top_locations.length > 0 ? (
                  roleDetails.top_locations.map((location) => (
                    <div
                      className="skill-row"
                      key={location.city}
                    >
                      <span>{location.city}</span>
                      <strong>
                        {location.job_count} jobs
                      </strong>
                    </div>
                  ))
                ) : (
                  <p>
                    No location information available.
                  </p>
                )}
              </div>
            </>
          )}
      </>
    )
  }

  const filteredRoles = roles
    .filter((item) =>
      item.role
        .toLowerCase()
        .includes(search.toLowerCase())
    )
    .slice(0, 20)

  return (
    <>
      <h2>Career Explorer</h2>

      <p className="subtitle">
        Explore career roles and job demand.
      </p>

      <input
        className="search-box"
        type="text"
        placeholder="Search for a role..."
        value={search}
        onChange={(event) => setSearch(event.target.value)}
      />

      <p className="result-count">
        Showing {filteredRoles.length} roles
      </p>

      <div className="role-list">
        {filteredRoles.map((item) => (
          <div
            className="role-card"
            key={item.role}
            onClick={() => handleRoleClick(item.role)}
          >
            <span>{item.role}</span>
            <strong>{item.job_count} jobs</strong>
            <small>Click to view details →</small>
          </div>
        ))}
      </div>
    </>
  )
}

function SkillIntelligence() {
  return (
    <>
      <h2>Skill Intelligence</h2>

      <p className="subtitle">
        Analyze the skills currently demanded by the job market.
      </p>
    </>
  )
}

function LocationIntelligence() {
  return (
    <>
      <h2>Location Intelligence</h2>

      <p className="subtitle">
        Explore job demand and salary information by city.
      </p>
    </>
  )
}

function CareerRanking() {
  return (
    <>
      <h2>Career Ranking</h2>

      <p className="subtitle">
        Compare career roles using job demand and salary metrics.
      </p>
    </>
  )
}

export default App