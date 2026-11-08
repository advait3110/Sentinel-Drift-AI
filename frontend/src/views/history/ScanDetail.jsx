// src/views/history/ScanDetail.jsx
import React, { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { CAlert, CButton, CSpinner } from '@coreui/react'
import CIcon from '@coreui/icons-react'
import { cilTrash } from '@coreui/icons'

import { deleteScan, getScan } from '../../api/client'
import ConfirmDeleteModal from '../../components/ConfirmDeleteModal'
import ScanResultView from '../scan/ScanResultView'

const ScanDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  // Remember which id the result belongs to, so a new id shows the spinner
  // without resetting state inside the effect.
  const [result, setResult] = useState({ id: null, scan: null, error: '' })
  const [confirming, setConfirming] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')

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

  const confirmDelete = async () => {
    setDeleting(true)
    setDeleteError('')
    try {
      await deleteScan(id)
      navigate('/scans', { replace: true })
    } catch (err) {
      setDeleteError(err.message)
      setDeleting(false)
    }
  }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <Link to="/scans">← Back to scan history</Link>
        {current?.scan && (
          <CButton
            color="danger"
            variant="outline"
            size="sm"
            onClick={() => {
              setDeleteError('')
              setConfirming(true)
            }}
          >
            <CIcon icon={cilTrash} className="me-1" />
            Delete scan
          </CButton>
        )}
      </div>
      {!current && (
        <div className="text-center py-5">
          <CSpinner />
        </div>
      )}
      {current?.error && <CAlert color="danger">{current.error}</CAlert>}
      {current?.scan && <ScanResultView scan={current.scan} />}

      <ConfirmDeleteModal
        scan={confirming ? current?.scan : null}
        deleting={deleting}
        error={deleteError}
        onCancel={() => !deleting && setConfirming(false)}
        onConfirm={confirmDelete}
      />
    </>
  )
}

export default ScanDetail