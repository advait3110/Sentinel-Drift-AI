import React from 'react'
import { CButton, CCol, CContainer, CRow } from '@coreui/react'

const Page404 = () => (
  <div className="bg-body-tertiary min-vh-100 d-flex flex-row align-items-center">
    <CContainer>
      <CRow className="justify-content-center">
        <CCol md={6} className="text-center">
          <h1 className="display-3">404</h1>
          <h4>Page not found</h4>
          <p className="text-body-secondary">The page you are looking for doesn&apos;t exist.</p>
          <CButton color="primary" href="#/dashboard">
            Go to dashboard
          </CButton>
        </CCol>
      </CRow>
    </CContainer>
  </div>
)

export default Page404
