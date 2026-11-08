/**
 * Breadcrumb trail built from routes.js.
 * Links use "#/..." because the app runs on HashRouter.
 */
import React from 'react'
import { matchPath, useLocation } from 'react-router-dom'
import { CBreadcrumb, CBreadcrumbItem } from '@coreui/react'

import { routes } from '../routes'

const findRouteName = (pathname) => {
  const route = routes.find(
    (r) => r.path !== '/' && matchPath({ path: r.path, end: true }, pathname),
  )
  return route ? route.name : null
}

const AppBreadcrumb = () => {
  const { pathname } = useLocation()

  // "/scans/abc" -> ["/scans", "/scans/abc"]
  const parts = pathname.split('/').filter(Boolean)
  const crumbs = parts
    .map((_, i) => `/${parts.slice(0, i + 1).join('/')}`)
    .map((path, i) => ({ path, name: findRouteName(path), active: i === parts.length - 1 }))
    .filter((c) => c.name)

  return (
    <CBreadcrumb className="my-0">
      <CBreadcrumbItem href="#/dashboard">Home</CBreadcrumbItem>
      {crumbs.map((c) =>
        c.active ? (
          <CBreadcrumbItem key={c.path} active>
            {c.name}
          </CBreadcrumbItem>
        ) : (
          <CBreadcrumbItem key={c.path} href={`#${c.path}`}>
            {c.name}
          </CBreadcrumbItem>
        ),
      )}
    </CBreadcrumb>
  )
}

export default React.memo(AppBreadcrumb)
