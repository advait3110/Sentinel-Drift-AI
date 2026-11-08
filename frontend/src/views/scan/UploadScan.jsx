// src/views/scan/UploadScan.jsx
import React, { useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { CAlert, CButton, CCard, CCardBody, CCardHeader, CSpinner } from '@coreui/react'
import CIcon from '@coreui/icons-react'
import { cilCloudUpload, cilFile } from '@coreui/icons'

import { uploadScan } from '../../api/client'
import { ALLOWED_EXTENSIONS, MAX_UPLOAD_BYTES } from '../../config'
import ScanResultView from './ScanResultView'

function validateFile(file) {
  const name = file.name.toLowerCase()
  if (!ALLOWED_EXTENSIONS.some((ext) => name.endsWith(ext))) {
    return `Unsupported file type. Use ${ALLOWED_EXTENSIONS.join(', ')}.`
  }
  if (file.size === 0) return 'The file is empty.'
  if (file.size > MAX_UPLOAD_BYTES) {
    return `File is too large (${formatSize(file.size)}). Maximum is ${formatSize(MAX_UPLOAD_BYTES)}.`
  }
  return ''
}

function formatSize(bytes) {
  if (bytes < 1000) return `${bytes} B`
  if (bytes < 1_000_000) return `${(bytes / 1000).toFixed(1)} KB`
  return `${(bytes / 1_000_000).toFixed(1)} MB`
}

const UploadScan = () => {
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [scan, setScan] = useState(null)
  const inputRef = useRef(null)

  const selectFile = (selected) => {
    setScan(null)
    if (!selected) return
    const problem = validateFile(selected)
    setError(problem)
    setFile(problem ? null : selected)
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setDragging(false)
    if (!loading) selectFile(event.dataTransfer.files?.[0])
  }

  const openPicker = () => {
    if (!loading) inputRef.current?.click()
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!file) return
    setLoading(true)
    setError('')
    setScan(null)
    try {
      setScan(await uploadScan(file))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setFile(null)
    setScan(null)
    setError('')
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <>
      <CCard className="mb-4">
        <CCardHeader>Upload configuration</CCardHeader>
        <CCardBody>
          <p className="text-body-secondary">
            Upload a JSON or YAML configuration export. It is checked against the security rules and
            the approved baseline, scored, and saved to scan history.
          </p>

          <form onSubmit={handleSubmit}>
            <div
              className={`upload-dropzone ${dragging ? 'is-dragging' : ''} ${loading ? 'is-disabled' : ''}`}
              role="button"
              tabIndex={0}
              aria-label="Choose a configuration file"
              onClick={openPicker}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  openPicker()
                }
              }}
              onDragOver={(e) => {
                e.preventDefault()
                setDragging(true)
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
            >
              <input
                ref={inputRef}
                type="file"
                accept={ALLOWED_EXTENSIONS.join(',')}
                className="d-none"
                onChange={(e) => selectFile(e.target.files?.[0])}
              />
              {file ? (
                <>
                  <CIcon icon={cilFile} size="3xl" className="mb-2 text-primary" />
                  <div className="fw-semibold">{file.name}</div>
                  <div className="small text-body-secondary">
                    {formatSize(file.size)} · click to change
                  </div>
                </>
              ) : (
                <>
                  <CIcon icon={cilCloudUpload} size="3xl" className="mb-2 text-body-secondary" />
                  <div className="fw-semibold">Drop a file here or click to browse</div>
                  <div className="small text-body-secondary">
                    {ALLOWED_EXTENSIONS.join(', ')} · up to {formatSize(MAX_UPLOAD_BYTES)}
                  </div>
                </>
              )}
            </div>

            <div className="d-flex gap-2 mt-3">
              <CButton type="submit" color="primary" disabled={loading || !file}>
                {loading ? (
                  <>
                    <CSpinner size="sm" className="me-2" />
                    Scanning…
                  </>
                ) : (
                  'Run scan'
                )}
              </CButton>
              {(file || scan || error) && (
                <CButton color="secondary" variant="outline" onClick={reset} disabled={loading}>
                  Clear
                </CButton>
              )}
            </div>
          </form>

          {error && (
            <CAlert color="danger" className="mt-3 mb-0">
              {error}
            </CAlert>
          )}
        </CCardBody>
      </CCard>

      {scan && (
        <>
          <CAlert color="success" className="d-flex justify-content-between align-items-center">
            <span>Scan saved to history.</span>
            <Link to={`/scans/${scan.id}`}>Open scan</Link>
          </CAlert>
          <ScanResultView scan={scan} />
        </>
      )}
    </>
  )
}

export default UploadScan
