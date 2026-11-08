/**
 * Small metric card used on the dashboard and scan result pages.
 */
import React from 'react'
import PropTypes from 'prop-types'
import { CCard, CCardBody } from '@coreui/react'

const StatCard = ({ label, value, color = 'primary', children }) => (
  <CCard className={`h-100 border-top-${color} border-top-3`}>
    <CCardBody>
      <div className="text-body-secondary small text-uppercase fw-semibold">{label}</div>
      <div className="fs-2 fw-bold">{value}</div>
      {children}
    </CCardBody>
  </CCard>
)

StatCard.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.node.isRequired,
  color: PropTypes.string,
  children: PropTypes.node,
}

export default StatCard
