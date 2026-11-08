// src/views/scan/FindingsTable.jsx
import React, { useMemo, useState } from 'react'
import PropTypes from 'prop-types'
import {
  CBadge,
  CCol,
  CFormInput,
  CFormSelect,
  CRow,
  CTable,
  CTableBody,
  CTableDataCell,
  CTableHead,
  CTableHeaderCell,
  CTableRow,
} from '@coreui/react'

import {
  FINDING_TYPE_LABEL,
  SEVERITIES,
  SEVERITY_COLOR,
  capitalize,
  formatValue,
} from '../../utils/severity'

const FindingsTable = ({ findings }) => {
  const [severity, setSeverity] = useState('all')
  const [type, setType] = useState('all')
  const [search, setSearch] = useState('')

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return findings.filter((f) => {
      if (severity !== 'all' && f.severity !== severity) return false
      if (type !== 'all' && f.finding_type !== type) return false
      if (!q) return true
      return [f.title, f.path, f.resource_id, f.rule_id]
        .filter(Boolean)
        .some((v) => String(v).toLowerCase().includes(q))
    })
  }, [findings, severity, type, search])

  if (!findings.length) {
    return (
      <p className="text-body-secondary mb-0">
        No findings. Everything matches the rules and baseline.
      </p>
    )
  }

  return (
    <>
      <CRow className="g-2 mb-3">
        <CCol md={3}>
          <CFormSelect
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
            aria-label="Severity"
          >
            <option value="all">All severities</option>
            {SEVERITIES.map((s) => (
              <option key={s} value={s}>
                {capitalize(s)}
              </option>
            ))}
          </CFormSelect>
        </CCol>
        <CCol md={3}>
          <CFormSelect
            value={type}
            onChange={(e) => setType(e.target.value)}
            aria-label="Finding type"
          >
            <option value="all">All types</option>
            {Object.entries(FINDING_TYPE_LABEL).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </CFormSelect>
        </CCol>
        <CCol md={6}>
          <CFormInput
            placeholder="Search issue, control, resource or rule ID"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </CCol>
      </CRow>

      <p className="small text-body-secondary">
        Showing {filtered.length} of {findings.length} findings
      </p>

      <CTable hover responsive align="middle" className="mb-0">
        <CTableHead>
          <CTableRow>
            <CTableHeaderCell>Severity</CTableHeaderCell>
            <CTableHeaderCell>Issue</CTableHeaderCell>
            <CTableHeaderCell>Resource</CTableHeaderCell>
            <CTableHeaderCell>Control</CTableHeaderCell>
            <CTableHeaderCell>Expected</CTableHeaderCell>
            <CTableHeaderCell>Actual</CTableHeaderCell>
            <CTableHeaderCell>Fix</CTableHeaderCell>
          </CTableRow>
        </CTableHead>
        <CTableBody>
          {filtered.map((f, i) => (
            <CTableRow key={`${f.resource_id}-${f.path}-${f.rule_id || ''}-${i}`}>
              <CTableDataCell>
                <CBadge color={SEVERITY_COLOR[f.severity] || 'secondary'}>
                  {capitalize(f.severity)}
                </CBadge>
              </CTableDataCell>
              <CTableDataCell>
                <div className="fw-semibold">{f.title}</div>
                <div className="small text-body-secondary">
                  {FINDING_TYPE_LABEL[f.finding_type] || f.finding_type}
                  {f.rule_id ? ` · ${f.rule_id}` : ''}
                </div>
              </CTableDataCell>
              <CTableDataCell>
                <div>{f.resource_id}</div>
                <div className="small text-body-secondary">{f.resource_type}</div>
              </CTableDataCell>
              <CTableDataCell className="text-nowrap">
                <code>{f.path}</code>
              </CTableDataCell>
              <CTableDataCell>
                <code>{formatValue(f.expected)}</code>
              </CTableDataCell>
              <CTableDataCell>
                <code>{formatValue(f.actual)}</code>
              </CTableDataCell>
              <CTableDataCell className="small" style={{ minWidth: 220 }}>
                {f.remediation || '—'}
              </CTableDataCell>
            </CTableRow>
          ))}
        </CTableBody>
      </CTable>
    </>
  )
}

FindingsTable.propTypes = {
  findings: PropTypes.arrayOf(PropTypes.object).isRequired,
}

export default FindingsTable
