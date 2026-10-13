import { useEffect, useState } from "react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts"
import {
  getStats,
  getRoles,
  getRoleDetails,
  getSkills,
  getSkillDetails,
  getLocations,
  getRankings
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
  const [rankings, setRankings] = useState([])
  const [skills, setSkills] = useState([])
  const [locations, setLocations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    Promise.all([
      getStats(),
      getRankings(),
      getSkills(),
      getLocations()
    ])
      .then(([statsData, rankingData, skillData, locationData]) => {
        setStats(statsData)
        setRankings(rankingData)
        setSkills(skillData)
        setLocations(locationData)
      })
      .catch((err) => {
        console.error("Failed to load dashboard insights:", err)
        setError("Some dashboard insights could not be loaded.")
      })
      .finally(() => setLoading(false))
  }, [])

  const topCareers = [...rankings]
    .sort((a, b) => b.opportunity_score - a.opportunity_score)
    .slice(0, 5)

  const topSkills = [...skills]
    .sort((a, b) => b.job_count - a.job_count)
    .slice(0, 5)

  const topCities = [...locations]
    .sort((a, b) => b.job_count - a.job_count)
    .slice(0, 5)

  const remoteJobs =
    locations.find(
      (city) => city.city_clean.toLowerCase() === "remote"
    )?.job_count || 0

  const highestSalaryCity = [...locations]
    .filter((city) => Number(city.median_salary_lpa) > 0)
    .sort((a, b) => b.median_salary_lpa - a.median_salary_lpa)[0]

  if (loading) {
    return (
      <>
        <h2>Job Market Overview</h2>
        <p className="subtitle">Loading market insights...</p>
      </>
    )
  }

  return (
    <>
      <h2>Job Market Overview</h2>
      <p className="subtitle">
        Explore jobs, skills, salaries, and career opportunities.
      </p>

      <div className="stats">
        <div className="card">
          <span>Total Jobs</span>
          <strong>{stats.total_jobs.toLocaleString()}</strong>
        </div>
        <div className="card">
          <span>Job Roles</span>
          <strong>{stats.job_roles.toLocaleString()}</strong>
        </div>
        <div className="card">
          <span>Skills</span>
          <strong>{stats.skills.toLocaleString()}</strong>
        </div>
      </div>

      {error && (
        <div className="section">
          <p>{error} Check that all backend endpoints are running.</p>
        </div>
      )}

      <div className="section">
        <h3>Market Insights</h3>
        <p>
          Your dataset contains {stats.total_jobs.toLocaleString()} job
          postings. Explore the strongest career opportunities, most
          requested skills, and leading hiring locations below.
        </p>
      </div>

      <div className="detail-grid">
        <div className="detail-section">
          <h3>Top Career Opportunities</h3>
          {topCareers.map((career, index) => (
            <div className="skill-row" key={career.role}>
              <strong>#{index + 1}</strong>
              <span>{career.role}</span>
              <strong>
                {Number(career.opportunity_score).toFixed(1)}
              </strong>
            </div>
          ))}
          {topCareers.length === 0 && <p>No career rankings available.</p>}
        </div>

        <div className="detail-section">
          <h3>Most In-Demand Skills</h3>
          {topSkills.map((skill, index) => (
            <div className="skill-row" key={skill.skill_name}>
              <strong>#{index + 1}</strong>
              <span>{skill.skill_name}</span>
              <strong>{skill.job_count.toLocaleString()} jobs</strong>
            </div>
          ))}
          {topSkills.length === 0 && <p>No skill data available.</p>}
        </div>
      </div>

      <div className="detail-section">
        <h3>Hiring Market Snapshot</h3>
        <div className="stats-grid">
          <div className="stat-card">
            <span>Leading Hiring City</span>
            <p>{topCities[0]?.city_clean || "N/A"}</p>
            <span>
              {topCities[0]?.job_count.toLocaleString() || 0} jobs
            </span>
          </div>

          <div className="stat-card">
            <span>Remote Opportunities</span>
            <p>{remoteJobs.toLocaleString()}</p>
            <span>Jobs tagged as Remote</span>
          </div>

          <div className="stat-card">
            <span>Highest Median Salary</span>
            <p>
              {highestSalaryCity
                ? `${Number(highestSalaryCity.median_salary_lpa).toFixed(2)} LPA`
                : "N/A"}
            </p>
            <span>{highestSalaryCity?.city_clean || "No data"}</span>
          </div>
        </div>
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
          <p className="loading">Loading role details...</p>
        )}

        {error && !loading && (
          <div className="detail-section">
            <h3>Unable to load role details</h3>
            <p><strong>Error:</strong> {error}</p>
          </div>
        )}

        {roleDetails && !roleDetails.error && !loading && (
          <>
            <p className="subtitle">
              Detailed career intelligence for this role.
            </p>

            <div className="stats">
              <div className="card">
                <span>Job Demand</span>
                <strong>
                  {roleDetails.job_count.toLocaleString()}
                </strong>
              </div>

              <div className="card">
                <span>Average Salary</span>
                <strong>
                  ₹{Number(roleDetails.avg_salary_lpa).toFixed(2)} LPA
                </strong>
              </div>

              <div className="card">
                <span>Median Salary</span>
                <strong>
                  ₹{Number(roleDetails.median_salary_lpa).toFixed(2)} LPA
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
                    {Number(roleDetails.opportunity_score).toFixed(1)}
                  </strong>
                </p>
              </div>

              <div className="detail-section">
                <h3>Demand</h3>

                <p>
                  Demand Percentage:{" "}
                  <strong>{roleDetails.demand_percent}%</strong>
                </p>

                <p>
                  Jobs with salary data:{" "}
                  <strong>{roleDetails.salary_job_count}</strong>
                </p>
              </div>
            </div>

            <div className="detail-section">
              <h3>Top Skills</h3>

              {roleDetails.top_skills?.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart
                    data={roleDetails.top_skills}
                    layout="vertical"
                    margin={{
                      top: 10,
                      right: 30,
                      left: 30,
                      bottom: 10
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" unit="%" />
                    <YAxis
                      type="category"
                      dataKey="skill_name"
                      width={130}
                    />
                    <Tooltip />
                    <Bar
                      dataKey="skill_percent"
                      name="Skill Demand"
                      fill="#4f46e5"
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p>No skill information available.</p>
              )}
            </div>

            <div className="detail-section">
              <h3>Top Locations</h3>

              {roleDetails.top_locations?.length > 0 ? (
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart
                    data={roleDetails.top_locations}
                    layout="vertical"
                    margin={{
                      top: 10,
                      right: 30,
                      left: 30,
                      bottom: 10
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      type="number"
                      allowDecimals={false}
                    />
                    <YAxis
                      type="category"
                      dataKey="city"
                      width={120}
                    />
                    <Tooltip />
                    <Bar
                      dataKey="job_count"
                      name="Jobs"
                      fill="#4f46e5"
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p>No location information available.</p>
              )}
            </div>
          </>
        )}
      </>
    )
  }

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
          <div
            className="role-card"
            key={item.role}
            onClick={() => handleRoleClick(item.role)}
          >
            <span>{item.role}</span>
            <strong>{item.job_count.toLocaleString()} jobs</strong>
            <small>Click to view details →</small>
          </div>
        ))}
      </div>
    </>
  )
}

function SkillIntelligence() {
  const [skills, setSkills] = useState([])
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [selectedSkill, setSelectedSkill] = useState(null)
  const [skillDetails, setSkillDetails] = useState(null)
  const [detailsLoading, setDetailsLoading] = useState(false)
  const [detailsError, setDetailsError] = useState("")

  useEffect(() => {
    getSkills()
      .then((data) => setSkills(data))
      .catch((error) => {
        console.error("Failed to load skills:", error)
        setError("Unable to load skill data.")
      })
      .finally(() => setLoading(false))
  }, [])

  const filteredSkills = skills.filter((skill) =>
    skill.skill_name.toLowerCase().includes(search.toLowerCase())
  )

  const topSkills = [...filteredSkills]
    .sort((a, b) => b.job_count - a.job_count)
    .slice(0, 15)

  const handleSkillClick = async (skillName) => {
    setSelectedSkill(skillName)
    setSkillDetails(null)
    setDetailsError("")
    setDetailsLoading(true)

    try {
      const data = await getSkillDetails(skillName)

      if (data.error) {
        setDetailsError(data.error)
      } else {
        setSkillDetails(data)
      }
    } catch (error) {
      console.error("Failed to load skill details:", error)
      setDetailsError("Unable to load related skills.")
    } finally {
      setDetailsLoading(false)
    }
  }

  const clearSelection = () => {
    setSelectedSkill(null)
    setSkillDetails(null)
    setDetailsError("")
  }

  if (loading) {
    return (
      <>
        <h2>Skill Intelligence</h2>
        <p>Loading skills...</p>
      </>
    )
  }

  if (error) {
    return (
      <>
        <h2>Skill Intelligence</h2>
        <p>{error}</p>
      </>
    )
  }

  return (
    <>
      <h2>Skill Intelligence</h2>

      <p className="subtitle">
        Analyze skill demand and discover valuable technical skills.
      </p>

      <div className="stats">
        <div className="card">
          <span>Skills Available</span>
          <strong>{skills.length}</strong>
        </div>

        <div className="card">
          <span>Top Skill</span>
          <strong>{topSkills[0]?.skill_name || "N/A"}</strong>
        </div>

        <div className="card">
          <span>Top Skill Jobs</span>
          <strong>
            {topSkills[0]?.job_count.toLocaleString() || 0}
          </strong>
        </div>
      </div>

      <input
        className="search-box"
        type="text"
        placeholder="Search for a skill..."
        value={search}
        onChange={(event) => setSearch(event.target.value)}
      />

      <div className="detail-section">
        <h3>Top Skills by Job Demand</h3>

        {topSkills.length > 0 ? (
          <ResponsiveContainer width="100%" height={450}>
            <BarChart
              data={topSkills}
              layout="vertical"
              margin={{
                top: 10,
                right: 35,
                left: 30,
                bottom: 10
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" allowDecimals={false} />
              <YAxis
                type="category"
                dataKey="skill_name"
                width={120}
              />
              <Tooltip />
              <Bar
                dataKey="job_count"
                name="Job Postings"
                fill="#4f46e5"
                cursor="pointer"
                onClick={(data) => {
                  if (data?.skill_name) {
                    handleSkillClick(data.skill_name)
                  }
                }}
              />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p>No matching skills found.</p>
        )}
      </div>

      <div className="detail-section">
        <h3>Skill Demand Details</h3>

        <div className="skill-table">
          {filteredSkills.map((skill) => (
            <div
              className="skill-row clickable-skill"
              key={skill.skill_name}
              onClick={() => handleSkillClick(skill.skill_name)}
              role="button"
              tabIndex={0}
              onKeyDown={(event) => {
                if (
                  event.key === "Enter" ||
                  event.key === " "
                ) {
                  event.preventDefault()
                  handleSkillClick(skill.skill_name)
                }
              }}
            >
              <span>{skill.skill_name}</span>

              <strong>
                {skill.job_count.toLocaleString()} jobs
              </strong>

              <span>
                {Number(skill.demand_percent).toFixed(2)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {selectedSkill && (
        <div className="detail-section">
          <button
            className="back-button"
            onClick={clearSelection}
          >
            ← Clear Selection
          </button>

          <h3>{selectedSkill} — Related Skills</h3>

          {detailsLoading && <p>Loading related skills...</p>}
          {detailsError && <p>{detailsError}</p>}

          {skillDetails && !detailsLoading && (
            <>
              <p>
                Job postings:{" "}
                <strong>
                  {skillDetails.job_count.toLocaleString()}
                </strong>
              </p>

              <p>
                Demand:{" "}
                <strong>
                  {Number(skillDetails.demand_percent).toFixed(2)}%
                </strong>
              </p>

              {skillDetails.related_skills.length > 0 ? (
                skillDetails.related_skills.map((item) => (
                  <div className="skill-row" key={item.skill}>
                    <span>{item.skill}</span>

                    <strong>
                      {item.job_count.toLocaleString()} jobs
                    </strong>

                    <span>
                      Avg. ₹{Number(item.avg_salary_lpa).toFixed(2)} LPA
                    </span>

                    <span>
                      Median ₹
                      {Number(item.median_salary_lpa).toFixed(2)} LPA
                    </span>
                  </div>
                ))
              ) : (
                <p>
                  No related skill combinations found for{" "}
                  {selectedSkill}.
                </p>
              )}
            </>
          )}
        </div>
      )}
    </>
  )
}


function LocationIntelligence() {
  const [locations, setLocations] = useState([])
  const [selectedCity, setSelectedCity] = useState("")
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    getLocations()
      .then((data) => {
        setLocations(data)
        if (data.length > 0) {
          setSelectedCity(
            [...data].sort(
              (a, b) => b.job_count - a.job_count
            )[0].city_clean
          )
        }
      })
      .catch(() => {
        setError("Unable to load location data. Check the backend.")
      })
      .finally(() => setLoading(false))
  }, [])

  const filteredLocations = locations
    .filter((city) =>
      city.city_clean.toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) => b.job_count - a.job_count)

  const selectedLocation = locations.find(
    (city) => city.city_clean === selectedCity
  )

  const topCities = [...locations]
    .sort((a, b) => b.job_count - a.job_count)
    .slice(0, 10)

  if (loading) {
    return (
      <div>
        <h2>Location Intelligence</h2>
        <p className="subtitle">Loading location data...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <h2>Location Intelligence</h2>
        <p className="subtitle">{error}</p>
      </div>
    )
  }

  return (
    <>
      <h2>Location Intelligence</h2>
      <p className="subtitle">
        Explore job demand and salary information by city.
      </p>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Locations</h3>
          <p>{locations.length.toLocaleString()}</p>
        </div>

        <div className="stat-card">
          <h3>Top Hiring City</h3>
          <p>{topCities[0]?.city_clean || "N/A"}</p>
        </div>

        <div className="stat-card">
          <h3>Top City Job Count</h3>
          <p>
            {topCities[0]?.job_count.toLocaleString() || 0}
          </p>
        </div>

        <div className="stat-card">
          <h3>Remote Jobs</h3>
          <p>
            {locations.find(
              (city) => city.city_clean.toLowerCase() === "remote"
            )?.job_count.toLocaleString() || 0}
          </p>
        </div>
      </div>

      <div className="chart-card">
        <h3>Top 10 Locations by Job Demand</h3>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart
            data={topCities}
            layout="vertical"
            margin={{ left: 25, right: 25 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis
              dataKey="city_clean"
              type="category"
              width={110}
            />
            <Tooltip />
            <Bar
              dataKey="job_count"
              name="Job Postings"
              fill="#6366f1"
              radius={[0, 5, 5, 0]}
              onClick={(data) => {
                if (data?.city_clean) {
                  setSelectedCity(data.city_clean)
                }
              }}
              cursor="pointer"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-card">
        <h3>Compare Average and Median Salary</h3>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={topCities}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="city_clean"
              angle={-25}
              textAnchor="end"
              height={80}
              interval={0}
            />
            <YAxis />
            <Tooltip />
            <Bar
              dataKey="avg_salary_lpa"
              name="Average Salary (LPA)"
              fill="#6366f1"
            />
            <Bar
              dataKey="median_salary_lpa"
              name="Median Salary (LPA)"
              fill="#14b8a6"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-card">
        <h3>Explore a City</h3>

        <input
          type="text"
          placeholder="Search for a city..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />

        <div className="skill-table">
          {filteredLocations.map((city) => (
            <div
              key={city.city_clean}
              className="skill-row clickable-skill"
              role="button"
              tabIndex={0}
              onClick={() => setSelectedCity(city.city_clean)}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault()
                  setSelectedCity(city.city_clean)
                }
              }}
            >
              <span>{city.city_clean}</span>
              <strong>{city.job_count.toLocaleString()} jobs</strong>
              <span>{Number(city.median_salary_lpa).toFixed(2)} LPA median</span>
            </div>
          ))}
        </div>

        {selectedLocation && (
          <div className="detail-card">
            <h3>{selectedLocation.city_clean}</h3>
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Job Postings</h3>
                <p>{selectedLocation.job_count.toLocaleString()}</p>
              </div>
              <div className="stat-card">
                <h3>Average Salary</h3>
                <p>
                  {Number(selectedLocation.avg_salary_lpa).toFixed(2)} LPA
                </p>
              </div>
              <div className="stat-card">
                <h3>Median Salary</h3>
                <p>
                  {Number(selectedLocation.median_salary_lpa).toFixed(2)} LPA
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  )
}

function CareerRanking() {
  const [rankings, setRankings] = useState([])
  const [search, setSearch] = useState("")
  const [sortBy, setSortBy] = useState("opportunity_score")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    getRankings()
      .then((data) => setRankings(data))
      .catch((err) => {
        console.error("Failed to load rankings:", err)
        setError("Unable to load career rankings. Check the backend.")
      })
      .finally(() => setLoading(false))
  }, [])

  const filteredRankings = rankings
    .filter((item) =>
      item.role.toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) => b[sortBy] - a[sortBy])

  const topRankings = [...rankings]
    .sort((a, b) => b.opportunity_score - a.opportunity_score)
    .slice(0, 10)

  const topCareer = topRankings[0]

  if (loading) {
    return (
      <>
        <h2>Career Ranking</h2>
        <p className="subtitle">Loading career rankings...</p>
      </>
    )
  }

  if (error) {
    return (
      <>
        <h2>Career Ranking</h2>
        <p className="subtitle">{error}</p>
      </>
    )
  }

  return (
    <>
      <h2>Career Ranking</h2>

      <p className="subtitle">
        Compare career roles using job demand, salary, and opportunity scores.
      </p>

      <div className="stats">
        <div className="card">
          <span>Roles Ranked</span>
          <strong>{rankings.length}</strong>
        </div>

        <div className="card">
          <span>Top Career</span>
          <strong>{topCareer?.role || "N/A"}</strong>
        </div>

        <div className="card">
          <span>Top Opportunity Score</span>
          <strong>
            {Number(topCareer?.opportunity_score || 0).toFixed(1)}
          </strong>
        </div>
      </div>

      <div className="detail-section">
        <h3>Top 10 Careers by Opportunity Score</h3>

        <ResponsiveContainer width="100%" height={400}>
          <BarChart
            data={topRankings}
            layout="vertical"
            margin={{ top: 10, right: 30, left: 30, bottom: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[0, 100]} />
            <YAxis
              type="category"
              dataKey="role"
              width={140}
            />
            <Tooltip />
            <Bar
              dataKey="opportunity_score"
              name="Opportunity Score"
              fill="#4f46e5"
              radius={[0, 5, 5, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="detail-section">
        <h3>Career Rankings</h3>

        <input
          className="search-box"
          type="text"
          placeholder="Search career roles..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />

        <label htmlFor="ranking-sort">Rank by: </label>
        <select
          id="ranking-sort"
          value={sortBy}
          onChange={(event) => setSortBy(event.target.value)}
        >
          <option value="opportunity_score">Opportunity Score</option>
          <option value="demand_score">Demand Score</option>
          <option value="salary_score">Salary Score</option>
          <option value="job_count">Job Count</option>
          <option value="median_salary_lpa">Median Salary</option>
        </select>

        <p className="result-count">
          Showing {filteredRankings.length} career roles
        </p>

        <div className="skill-table">
          {filteredRankings.map((item, index) => (
            <div className="skill-row" key={item.role}>
              <strong>#{index + 1}</strong>
              <span>{item.role}</span>
              <span>{item.job_count.toLocaleString()} jobs</span>
              <span>
                {Number(item.median_salary_lpa).toFixed(2)} LPA median
              </span>
              <span>
                Score: {Number(item.opportunity_score).toFixed(1)}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="detail-section">
        <h3>Compare Career Metrics</h3>

        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={topRankings}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="role"
              angle={-25}
              textAnchor="end"
              height={100}
              interval={0}
            />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Bar dataKey="demand_score" name="Demand Score" fill="#4f46e5" />
            <Bar dataKey="salary_score" name="Salary Score" fill="#14b8a6" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  )
}


export default App
