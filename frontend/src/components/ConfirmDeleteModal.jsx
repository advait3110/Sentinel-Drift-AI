/**
 * Confirmation dialog for deleting a scan.
 */
import React from 'react'
import PropTypes from 'prop-types'
import {
  CAlert,
  CButton,
  CModal,
  CModalBody,
  CModalFooter,
  CModalHeader,
  CModalTitle,
  CSpinner,
} from '@coreui/react'

const ConfirmDeleteModal = ({ scan, deleting, error, onCancel, onConfirm }) => (
  <CModal visible={Boolean(scan)} onClose={onCancel} alignment="center" backdrop="static">
    <CModalHeader>
      <CModalTitle>Delete scan?</CModalTitle>
    </CModalHeader>
    <CModalBody>
      {scan && (
        <p className="mb-2">
          This permanently deletes the scan of <strong>{scan.filename}</strong> (score{' '}
          {scan.risk_score}) and all its findings. This cannot be undone.
        </p>
      )}
      {error && (
        <CAlert color="danger" className="mb-0">
          {error}
        </CAlert>
      )}
    </CModalBody>
    <CModalFooter>
      <CButton color="secondary" variant="outline" onClick={onCancel} disabled={deleting}>
        Cancel
      </CButton>
      <CButton color="danger" onClick={onConfirm} disabled={deleting}>
        {deleting ? (
          <>
            <CSpinner size="sm" className="me-2" />
            Deleting…
          </>
        ) : (
          'Delete'
        )}
      </CButton>
    </CModalFooter>
  </CModal>
)

ConfirmDeleteModal.propTypes = {
  scan: PropTypes.object,
  deleting: PropTypes.bool,
  error: PropTypes.string,
  onCancel: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
}

export default ConfirmDeleteModal