// Shown inside the layout for unknown routes.
import React from 'react'
import { useNavigate } from 'react-router-dom'
import { CButton, CCard, CCardBody } from '@coreui/react'

const NotFound = () => {
  const navigate = useNavigate()
  return (
    <CCard>
      <CCardBody className="text-center py-5">
        <h1 className="display-5 fw-bold">404</h1>
        <p className="text-body-secondary">This page doesn&apos;t exist.</p>
        <CButton color="primary" onClick={() => navigate('/dashboard')}>
          Go to dashboard
        </CButton>
      </CCardBody>
    </CCard>
  )
}

export default NotFound
