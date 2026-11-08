// src/views/dashboard/Dashboard.jsx
// Overview: latest posture, risk-score trend and recent scans.
import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  CAlert,
  CBadge,
  CButton,
  CCard,
  CCardBody,
  CCardHeader,
  CCol,
  CListGroup,
  CListGroupItem,
  CRow,
  CSpinner,
} from '@coreui/react'
import { CChartLine } from '@coreui/react-chartjs'

import { listScans } from '../../api/client'
import StatCard from '../../components/StatCard'
import { RISK_LEVEL_COLOR, formatDate, formatShortDate } from '../../utils/severity'

const Dashboard = () => {
  const [scans, setScans] = useState(null)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    listScans(30)
      .then(setScans)
      .catch((err) => {
        setError(err.message)
        setScans([])
      })
  }, [])

  if (scans === null) {
    return (
      <div className="text-center py-5">
        <CSpinner />
      </div>
    )
  }

  if (error) return <CAlert color="danger">{error}</CAlert>

  if (scans.length === 0) {
    return (
      <CCard>
        <CCardBody className="text-center py-5">
          <h4>No scans yet</h4>
          <p className="text-body-secondary">
            Upload a configuration to see your security posture here.
          </p>
          <CButton color="primary" onClick={() => navigate('/scan')}>
            Run your first scan
          </CButton>
        </CCardBody>
      </CCard>
    )
  }

  const latest = scans[0]
  const levelColor = RISK_LEVEL_COLOR[latest.risk_level] || 'secondary'
  const counts = latest.severity_counts || {}
  const urgent = (counts.critical || 0) + (counts.high || 0)
  const trend = [...scans].reverse() // oldest -> newest for the chart

  return (
    <>
      <CRow className="g-3 mb-4">
        <CCol sm={6} xl={3}>
          <StatCard
            label="Current risk score"
            value={`${latest.risk_score} / 100`}
            color={levelColor}
          >
            <CBadge color={levelColor}>{latest.risk_level}</CBadge>
          </StatCard>
        </CCol>
        <CCol sm={6} xl={3}>
          <StatCard
            label="Open findings (latest scan)"
            value={latest.findings_count}
            color="primary"
          />
        </CCol>
        <CCol sm={6} xl={3}>
          <StatCard label="Critical + High" value={urgent} color={urgent ? 'danger' : 'success'} />
        </CCol>
        <CCol sm={6} xl={3}>
          <StatCard
            label="Scans recorded"
            value={scans.length === 30 ? '30+' : scans.length}
            color="info"
          />
        </CCol>
      </CRow>

      <CRow className="g-3">
        <CCol lg={8}>
          <CCard className="h-100">
            <CCardHeader>Risk score trend</CCardHeader>
            <CCardBody>
              <CChartLine
                style={{ height: 300 }}
                data={{
                  labels: trend.map((s) => formatShortDate(s.created_at)),
                  datasets: [
                    {
                      label: 'Risk score',
                      data: trend.map((s) => s.risk_score),
                      borderColor: '#5856d6',
                      backgroundColor: 'rgba(88, 86, 214, 0.1)',
                      fill: true,
                      tension: 0.3,
                      pointRadius: 4,
                    },
                  ],
                }}
                options={{
                  maintainAspectRatio: false,
                  plugins: { legend: { display: false } },
                  scales: {
                    y: {
                      min: 0,
                      max: 100,
                      title: { display: true, text: 'Score (higher is safer)' },
                    },
                    x: { ticks: { maxTicksLimit: 6 } },
                  },
                }}
              />
            </CCardBody>
          </CCard>
        </CCol>
        <CCol lg={4}>
          <CCard className="h-100">
            <CCardHeader className="d-flex justify-content-between">
              <span>Recent scans</span>
              <Link to="/scans">View all</Link>
            </CCardHeader>
            <CListGroup flush>
              {scans.slice(0, 6).map((s) => (
                <CListGroupItem
                  key={s.id}
                  as="button"
                  className="d-flex justify-content-between align-items-center"
                  onClick={() => navigate(`/scans/${s.id}`)}
                >
                  <span>
                    <div className="fw-semibold">{s.filename}</div>
                    <div className="small text-body-secondary">{formatDate(s.created_at)}</div>
                  </span>
                  <CBadge color={RISK_LEVEL_COLOR[s.risk_level] || 'secondary'}>
                    {s.risk_score}
                  </CBadge>
                </CListGroupItem>
              ))}
            </CListGroup>
          </CCard>
        </CCol>
      </CRow>
    </>
  )
}

export default Dashboard
