/**
 * Catches rendering errors in a page so the whole app doesn't go blank.
 */
import React from 'react'
import PropTypes from 'prop-types'
import { CAlert, CButton } from '@coreui/react'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    console.error('Page crashed:', error, info?.componentStack)
  }

  render() {
    if (!this.state.error) return this.props.children

    return (
      <CAlert color="danger">
        <h5 className="alert-heading">Something went wrong on this page.</h5>
        <p className="mb-3">
          {this.state.error.message || 'Unexpected error.'} Details are in the browser console
          (F12).
        </p>
        <CButton color="danger" variant="outline" onClick={() => this.setState({ error: null })}>
          Try again
        </CButton>
      </CAlert>
    )
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node,
}

export default ErrorBoundary
