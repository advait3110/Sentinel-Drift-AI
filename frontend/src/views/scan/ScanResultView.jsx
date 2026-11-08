// src/views/scan/ScanResultView.jsx
// Shows one stored scan: score, severity breakdown, AI summary, findings.
import React from 'react'
import PropTypes from 'prop-types'
import { CBadge, CCard, CCardBody, CCardHeader, CCol, CRow } from '@coreui/react'

import FindingsTable from './FindingsTable'
import StatCard from '../../components/StatCard'
import {
  RISK_LEVEL_COLOR,
  SEVERITIES,
  SEVERITY_COLOR,
  capitalize,
  formatDate,
} from '../../utils/severity'

const ScanResultView = ({ scan }) => {
  const counts = scan.severity_counts || {}
  const levelColor = RISK_LEVEL_COLOR[scan.risk_level] || 'secondary'
  const urgent = (counts.critical || 0) + (counts.high || 0)
  const explanation = scan.risk?.explanation || []

  return (
    <>
      <p className="text-body-secondary mb-3">
        <strong>{scan.filename}</strong> · scanned {formatDate(scan.created_at)}
      </p>

      <CRow className="g-3 mb-4">
        <CCol sm={6} xl={3}>
          <StatCard label="Risk score" value={`${scan.risk_score} / 100`} color={levelColor}>
            <CBadge color={levelColor}>{scan.risk_level}</CBadge>
          </StatCard>
        </CCol>
        <CCol sm={6} xl={3}>
          <StatCard label="Findings" value={scan.findings_count} color="primary" />
        </CCol>
        <CCol sm={6} xl={3}>
          <StatCard label="Critical + High" value={urgent} color={urgent ? 'danger' : 'success'} />
        </CCol>
        <CCol sm={6} xl={3}>
          <StatCard label="Resources scanned" value={scan.resources_scanned} color="info" />
        </CCol>
      </CRow>

      <CRow className="g-3 mb-4">
        <CCol lg={5}>
          <CCard className="h-100">
            <CCardHeader>Why this score</CCardHeader>
            <CCardBody>
              <div className="d-flex flex-wrap gap-2 mb-3">
                {SEVERITIES.map((s) => (
                  <CBadge key={s} color={SEVERITY_COLOR[s]}>
                    {capitalize(s)}: {counts[s] || 0}
                  </CBadge>
                ))}
              </div>
              <ul className="mb-0 small">
                {explanation.map((line) => (
                  <li key={line}>{line}</li>
                ))}
              </ul>
            </CCardBody>
          </CCard>
        </CCol>
        <CCol lg={7}>
          <CCard className="h-100">
            <CCardHeader>AI summary</CCardHeader>
            <CCardBody>
              {scan.ai_summary ? (
                <div style={{ whiteSpace: 'pre-wrap' }}>{scan.ai_summary}</div>
              ) : (
                <p className="text-body-secondary mb-0">
                  No AI summary for this scan. Either there were no findings, or GEMINI_API_KEY is
                  not set on the backend.
                </p>
              )}
              <p className="small text-body-secondary mt-3 mb-0">
                Severity and score come from the rule engine. The AI only explains them.
              </p>
            </CCardBody>
          </CCard>
        </CCol>
      </CRow>

      <CCard className="mb-4">
        <CCardHeader>Findings</CCardHeader>
        <CCardBody>
          <FindingsTable findings={scan.findings || []} />
        </CCardBody>
      </CCard>
    </>
  )
}

ScanResultView.propTypes = {
  scan: PropTypes.object.isRequired,
}

export default ScanResultView
