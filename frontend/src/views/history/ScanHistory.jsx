// src/views/history/ScanHistory.jsx
import React, { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  CAlert,
  CBadge,
  CButton,
  CCard,
  CCardBody,
  CCardHeader,
  CSpinner,
  CTable,
  CTableBody,
  CTableDataCell,
  CTableHead,
  CTableHeaderCell,
  CTableRow,
} from '@coreui/react'

import { listScans } from '../../api/client'
import { RISK_LEVEL_COLOR, formatDate } from '../../utils/severity'

const ScanHistory = () => {
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const fetchScans = useCallback(
    () =>
      listScans(100)
        .then((data) => {
          setScans(data)
          setError('')
        })
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false)),
    [],
  )

  useEffect(() => {
    fetchScans()
  }, [fetchScans])

  const refresh = () => {
    setLoading(true)
    fetchScans()
  }

  return (
    <CCard className="mb-4">
      <CCardHeader className="d-flex justify-content-between align-items-center">
        <span>Scan history</span>
        <CButton size="sm" color="secondary" variant="outline" onClick={refresh} disabled={loading}>
          Refresh
        </CButton>
      </CCardHeader>
      <CCardBody>
        {error && <CAlert color="danger">{error}</CAlert>}
        {loading ? (
          <div className="text-center py-4">
            <CSpinner />
          </div>
        ) : scans.length === 0 ? (
          !error && (
            <p className="mb-0">
              No scans yet. <Link to="/scan">Run your first scan</Link>.
            </p>
          )
        ) : (
          <CTable hover responsive align="middle" className="mb-0">
            <CTableHead>
              <CTableRow>
                <CTableHeaderCell>Date</CTableHeaderCell>
                <CTableHeaderCell>File</CTableHeaderCell>
                <CTableHeaderCell>Score</CTableHeaderCell>
                <CTableHeaderCell>Risk level</CTableHeaderCell>
                <CTableHeaderCell>Findings</CTableHeaderCell>
                <CTableHeaderCell>Critical</CTableHeaderCell>
                <CTableHeaderCell>High</CTableHeaderCell>
              </CTableRow>
            </CTableHead>
            <CTableBody>
              {scans.map((s) => (
                <CTableRow
                  key={s.id}
                  role="button"
                  tabIndex={0}
                  onClick={() => navigate(`/scans/${s.id}`)}
                  onKeyDown={(e) => e.key === 'Enter' && navigate(`/scans/${s.id}`)}
                >
                  <CTableDataCell>{formatDate(s.created_at)}</CTableDataCell>
                  <CTableDataCell>{s.filename}</CTableDataCell>
                  <CTableDataCell className="fw-semibold">{s.risk_score}</CTableDataCell>
                  <CTableDataCell>
                    <CBadge color={RISK_LEVEL_COLOR[s.risk_level] || 'secondary'}>
                      {s.risk_level}
                    </CBadge>
                  </CTableDataCell>
                  <CTableDataCell>{s.findings_count}</CTableDataCell>
                  <CTableDataCell>{s.severity_counts?.critical || 0}</CTableDataCell>
                  <CTableDataCell>{s.severity_counts?.high || 0}</CTableDataCell>
                </CTableRow>
              ))}
            </CTableBody>
          </CTable>
        )}
      </CCardBody>
    </CCard>
  )
}

export default ScanHistory
