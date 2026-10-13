import axios from "axios"

const API = axios.create({
  baseURL: "http://127.0.0.1:8000"
})

export const getStats = async () => {
  const response = await API.get("/api/stats")
  return response.data
}

export const getRoles = async () => {
  const response = await API.get("/api/roles")
  return response.data
}

export const getRoleDetails = async (role) => {
  const response = await API.get(
    `/api/roles/${encodeURIComponent(role)}`
  )

  return response.data
}
export const getSkills = async () => {
  const response = await API.get("/api/skills")
  return response.data
}

export const getSkillDetails = async (skill) => {
  const response = await API.get(
    `/api/skills/${encodeURIComponent(skill)}`
  )

  return response.data
}
export const getLocations = async () => {
  const response = await API.get("/api/locations")
  return response.data
}

export const getRankings = async () => {
  const response = await API.get("/api/rankings")
  return response.data
}
