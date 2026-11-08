// src/config.js
// App-wide constants. Keep upload limits in sync with backend/app/core/config.py.

export const APP_NAME = 'Sentinel Drift AI'
export const APP_VERSION = '0.1.0'

export const THEME_STORAGE_KEY = 'sentinel-drift-theme'

export const MAX_UPLOAD_BYTES = 1_000_000 // 1 MB
export const ALLOWED_EXTENSIONS = ['.json', '.yaml', '.yml']

// How often the header re-checks that the backend is reachable.
export const HEALTH_POLL_MS = 30_000
