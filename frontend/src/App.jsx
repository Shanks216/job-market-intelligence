import { useEffect, useState } from "react"
import { getStats, getRoles } from "./services/api"
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
      .catch((error) => console.error("Failed to load stats:", error))
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
  useEffect(() => {
    getRoles()
      .then((data) => setRoles(data))
      .catch((error) => console.error("Failed to load roles:", error))
  }, [])
  const filteredRoles = roles
    .filter((item) =>
      item.role.toLowerCase().includes(search.toLowerCase())
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
          <div className="role-card" key={item.role}>
            <span>{item.role}</span>
            <strong>{item.job_count} jobs</strong>
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