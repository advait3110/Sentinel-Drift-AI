/**
 * Root component: theme setup and top-level routing.
 *
 * Uses HashRouter, so URLs look like http://localhost:3000/#/scans.
 * That works on any static host without server-side rewrite rules.
 */
import React, { Suspense, useEffect } from 'react'
import { HashRouter, Route, Routes } from 'react-router-dom'
import { useSelector } from 'react-redux'
import { CSpinner, useColorModes } from '@coreui/react'

import './scss/style.scss'
import { THEME_STORAGE_KEY } from './config'

const DefaultLayout = React.lazy(() => import('./layout/DefaultLayout'))
const Page404 = React.lazy(() => import('./views/error-pages/page404/Page404'))
const Page500 = React.lazy(() => import('./views/error-pages/page500/Page500'))

const App = () => {
  const { isColorModeSet, setColorMode } = useColorModes(THEME_STORAGE_KEY)
  const storedTheme = useSelector((state) => state.theme)

  useEffect(() => {
    // Allow ?theme=dark in the URL, otherwise use the saved or default theme.
    // Works for both /?theme=dark#/dashboard and /#/dashboard?theme=dark
    const fromSearch = new URLSearchParams(window.location.search).get('theme')
    const fromHash = new URLSearchParams(window.location.hash.split('?')[1] || '').get('theme')
    const theme = (fromSearch || fromHash)?.match(/^(light|dark|auto)$/)?.[0]
    if (theme) {
      setColorMode(theme)
      return
    }
    if (!isColorModeSet()) {
      setColorMode(storedTheme)
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <HashRouter>
      <Suspense
        fallback={
          <div className="pt-3 text-center">
            <CSpinner color="primary" variant="grow" />
          </div>
        }
      >
        <Routes>
          <Route path="/404" element={<Page404 />} />
          <Route path="/500" element={<Page500 />} />
          <Route path="*" element={<DefaultLayout />} />
        </Routes>
      </Suspense>
    </HashRouter>
  )
}

export default App
