/**
 * Application routes (rendered inside the main layout).
 */
import React from 'react'

const Dashboard = React.lazy(() => import('./views/dashboard/Dashboard'))
const UploadScan = React.lazy(() => import('./views/scan/UploadScan'))
const ScanHistory = React.lazy(() => import('./views/history/ScanHistory'))
const ScanDetail = React.lazy(() => import('./views/history/ScanDetail'))

export const routes = [
  { path: '/', exact: true, name: 'Home' },
  { path: '/dashboard', name: 'Dashboard', element: Dashboard },
  { path: '/scan', name: 'Upload & Scan', element: UploadScan },
  { path: '/scans', name: 'Scan History', element: ScanHistory, exact: true },
  { path: '/scans/:id', name: 'Scan Details', element: ScanDetail },
]

export default routes
