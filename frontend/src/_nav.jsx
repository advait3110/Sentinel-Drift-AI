/**
 * Sidebar navigation.
 */
import React from 'react'
import CIcon from '@coreui/icons-react'
import { cilCloudUpload, cilHistory, cilSpeedometer } from '@coreui/icons'
import { CNavItem, CNavTitle } from '@coreui/react'

const _nav = [
  {
    component: CNavItem,
    name: 'Dashboard',
    to: '/dashboard',
    icon: <CIcon icon={cilSpeedometer} customClassName="nav-icon" />,
  },
  {
    component: CNavTitle,
    name: 'Scanning',
  },
  {
    component: CNavItem,
    name: 'Upload & Scan',
    to: '/scan',
    icon: <CIcon icon={cilCloudUpload} customClassName="nav-icon" />,
  },
  {
    component: CNavItem,
    name: 'Scan History',
    to: '/scans',
    icon: <CIcon icon={cilHistory} customClassName="nav-icon" />,
  },
]

export default _nav
