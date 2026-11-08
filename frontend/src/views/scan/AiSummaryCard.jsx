// src/views/scan/AiSummaryCard.jsx
// Shows the AI summary, or why it is missing, with a button to generate it.
import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { CAlert, CButton, CCard, CCardBody, CCardHeader, CSpinner } from '@coreui/react'
import CIcon from '@coreui/icons-react'
import { cilReload } from '@coreui/icons'

import { regenerateSummary } from '../../api/client'

const AiSummaryCard = ({ scan }) => {
  const [summary, setSummary] = useState(scan.ai_summary || '')
  const [reason, setReason] = useState(scan.ai_error || '')
  const [generating, setGenerating] = useState(false)

  const hasFindings = (scan.findings_count || 0) > 0

  const generate = async () => {
    setGenerating(true)
    setReason('')
    try {
      const updated = await regenerateSummary(scan.id)
      setSummary(updated.ai_summary || '')
      setReason(updated.ai_summary ? '' : updated.ai_error || 'No summary was returned.')
    } catch (err) {
      setReason(err.message)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <CCard className="h-100">
      <CCardHeader className="d-flex justify-content-between align-items-center">
        <span>AI summary</span>
        {hasFindings && summary && !generating && (
          <CButton
            size="sm"
            color="secondary"
            variant="ghost"
            onClick={generate}
            title="Regenerate"
          >
            <CIcon icon={cilReload} />
          </CButton>
        )}
      </CCardHeader>
      <CCardBody>
        {generating ? (
          <div className="d-flex align-items-center text-body-secondary">
            <CSpinner size="sm" className="me-2" />
            Generating summary… this can take up to a minute.
          </div>
        ) : summary ? (
          <div style={{ whiteSpace: 'pre-wrap' }}>{summary}</div>
        ) : !hasFindings ? (
          <p className="text-body-secondary mb-0">No findings, so there is nothing to summarize.</p>
        ) : (
          <>
            {reason ? (
              <CAlert color="warning" className="small">
                <strong>No AI summary:</strong> {reason}
              </CAlert>
            ) : (
              <p className="text-body-secondary">This scan has no AI summary yet.</p>
            )}
            <CButton color="primary" onClick={generate}>
              Generate AI summary
            </CButton>
          </>
        )}
        <p className="small text-body-secondary mt-3 mb-0">
          Severity and score come from the rule engine. The AI only explains them.
        </p>
      </CCardBody>
    </CCard>
  )
}

AiSummaryCard.propTypes = {
  scan: PropTypes.object.isRequired,
}

export default AiSummaryCard