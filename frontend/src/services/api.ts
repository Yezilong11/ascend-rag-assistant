import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export const skillTreeApiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/skill-tree`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const ragApiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/rag`,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const rssApiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/rss`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const multimodalApiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/multimodal`,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
})

skillTreeApiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.response?.data?.message || '请求失败'
    return Promise.reject(new Error(message))
  },
)

ragApiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.response?.data?.message || '请求失败'
    return Promise.reject(new Error(message))
  },
)

rssApiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.response?.data?.message || '请求失败'
    return Promise.reject(new Error(message))
  },
)

multimodalApiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.response?.data?.message || '请求失败'
    return Promise.reject(new Error(message))
  },
)
