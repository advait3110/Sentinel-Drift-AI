import React from 'react'
import { CButton, CCol, CContainer, CRow } from '@coreui/react'

const Page500 = () => (
  <div className="bg-body-tertiary min-vh-100 d-flex flex-row align-items-center">
    <CContainer>
      <CRow className="justify-content-center">
        <CCol md={6} className="text-center">
          <h1 className="display-3">500</h1>
          <h4>Something went wrong</h4>
          <p className="text-body-secondary">An unexpected error occurred. Please try again.</p>
          <CButton color="primary" href="#/dashboard">
            Go to dashboard
          </CButton>
        </CCol>
      </CRow>
    </CContainer>
  </div>
)

export default Page500
