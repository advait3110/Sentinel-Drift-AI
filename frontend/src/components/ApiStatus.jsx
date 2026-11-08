/**
 * Header badge showing whether the backend is reachable and where scans are stored.
 */
import React, { useEffect, useState } from 'react'
import { CBadge, CTooltip } from '@coreui/react'

import { getHealth } from '../api/client'
import { HEALTH_POLL_MS } from '../config'

const ApiStatus = () => {
  const [status, setStatus] = useState({ state: 'checking' })

  useEffect(() => {
    let cancelled = false

    const check = async () => {
      try {
        const health = await getHealth()
        if (!cancelled) {
          setStatus({
            state: 'online',
            storage: health.storage,
            storageOk: health.storage_ok,
            storageError: health.storage_error,
          })
        }
      } catch (err) {
        if (!cancelled) setStatus({ state: 'offline', message: err.message })
      }
    }

    check()
    const timer = setInterval(check, HEALTH_POLL_MS)
    return () => {
      cancelled = true
      clearInterval(timer)
    }
  }, [])

  if (status.state === 'checking') {
    return <CBadge color="secondary">Checking API…</CBadge>
  }

  if (status.state === 'offline') {
    return (
      <CTooltip content={status.message}>
        <CBadge color="danger" role="status">
          API offline
        </CBadge>
      </CTooltip>
    )
  }

  if (status.storageOk === false) {
    return (
      <CTooltip content={status.storageError || 'The backend cannot read or write scans.'}>
        <CBadge color="danger" role="status">
          API online · storage error
        </CBadge>
      </CTooltip>
    )
  }

  const temporary = status.storage === 'InMemoryScanRepository'
  return (
    <CTooltip
      content={
        temporary
          ? 'Supabase is not configured on the backend. Scans are kept in memory and lost on restart.'
          : 'Backend connected. Scans are saved to Supabase.'
      }
    >
      <CBadge color={temporary ? 'warning' : 'success'} role="status">
        {temporary ? 'API online · temporary storage' : 'API online'}
      </CBadge>
    </CTooltip>
  )
}

export default ApiStatus
