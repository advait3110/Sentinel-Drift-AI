// src/utils/severity.js

export const SEVERITIES = ['critical', 'high', 'medium', 'low', 'info']

// CoreUI color names for CBadge / CCard / CAlert
export const SEVERITY_COLOR = {
  critical: 'danger',
  high: 'warning',
  medium: 'primary',
  low: 'info',
  info: 'secondary',
}

export const RISK_LEVEL_COLOR = {
  Excellent: 'success',
  Good: 'success',
  Moderate: 'warning',
  'High Risk': 'danger',
  Critical: 'danger',
}

export const FINDING_TYPE_LABEL = {
  misconfiguration: 'Misconfiguration',
  drift: 'Drift',
  missing_control: 'Missing control',
}

export function formatValue(value) {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

export function formatDate(iso) {
  if (!iso) return '—'
  const date = new Date(iso)
  return Number.isNaN(date.getTime()) ? iso : date.toLocaleString()
}

// Compact date for chart axes, e.g. "Nov 6, 05:28 PM"
export function formatShortDate(iso) {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso || ''
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function capitalize(text) {
  return text ? text.charAt(0).toUpperCase() + text.slice(1) : ''
}
