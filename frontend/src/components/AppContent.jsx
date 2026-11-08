/**
 * Main content area: renders the page for the current route.
 */
import React, { Suspense } from 'react'
import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { CContainer, CSpinner } from '@coreui/react'

import { routes } from '../routes'
import ErrorBoundary from './ErrorBoundary'
import NotFound from '../views/NotFound'

const AppContent = () => {
  const location = useLocation()

  return (
    <CContainer className="px-4" lg>
      {/* key resets the error state when the user navigates to another page */}
      <ErrorBoundary key={location.pathname}>
        <Suspense
          fallback={
            <div className="text-center py-5">
              <CSpinner color="primary" />
            </div>
          }
        >
          <Routes>
            {routes.map(
              (route) =>
                route.element && (
                  <Route key={route.path} path={route.path} element={<route.element />} />
                ),
            )}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </CContainer>
  )
}

export default React.memo(AppContent)
