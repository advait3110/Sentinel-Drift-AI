import React from 'react'
import { CFooter } from '@coreui/react'

import { APP_NAME, APP_VERSION } from '../config'

const AppFooter = () => (
  <CFooter className="px-4">
    <div>
      <span className="fw-semibold">{APP_NAME}</span>
      <span className="ms-2 text-body-secondary">v{APP_VERSION}</span>
    </div>
    <div className="ms-auto small text-body-secondary">
      UI built on{' '}
      <a href="https://coreui.io/react" target="_blank" rel="noopener noreferrer">
        CoreUI
      </a>{' '}
      (MIT)
    </div>
  </CFooter>
)

export default React.memo(AppFooter)
