// src/api/client.js
// Single place for all calls to the FastAPI backend.

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_URL}${path}`, options)
  } catch {
    throw new Error(`Cannot reach the backend at ${API_URL}. Is uvicorn running?`)
  }

  const text = await response.text()
  let body = null
  if (text) {
    try {
      body = JSON.parse(text)
    } catch {
      body = text
    }
  }

  if (!response.ok) {
    const detail = body && typeof body === 'object' ? body.detail : body
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg).join('; ')
      : detail || `Request failed (${response.status})`
    throw new Error(message)
  }
  return body
}

export function getHealth() {
  return request('/health')
}

export function uploadScan(file) {
  const form = new FormData()
  form.append('file', file)
  return request('/api/scans', { method: 'POST', body: form })
}

export function listScans(limit = 50) {
  return request(`/api/scans?limit=${limit}`)
}

export function getScan(id) {
  return request(`/api/scans/${encodeURIComponent(id)}`)
}
