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