// src/views/history/ScanDetail.jsx
import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { CAlert, CSpinner } from '@coreui/react'

import { getScan } from '../../api/client'
import ScanResultView from '../scan/ScanResultView'

const ScanDetail = () => {
  const { id } = useParams()
  // Remember which id the result belongs to, so a new id shows the spinner
  // without resetting state inside the effect.
  const [result, setResult] = useState({ id: null, scan: null, error: '' })

  useEffect(() => {
    let cancelled = false
    getScan(id)
      .then((scan) => !cancelled && setResult({ id, scan, error: '' }))
      .catch((err) => !cancelled && setResult({ id, scan: null, error: err.message }))
    return () => {
      cancelled = true
    }
  }, [id])

  const current = result.id === id ? result : null

  return (
    <>
      <p>
        <Link to="/scans">← Back to scan history</Link>
      </p>
      {!current && (
        <div className="text-center py-5">
          <CSpinner />
        </div>
      )}
      {current?.error && <CAlert color="danger">{current.error}</CAlert>}
      {current?.scan && <ScanResultView scan={current.scan} />}
    </>
  )
}

export default ScanDetail
