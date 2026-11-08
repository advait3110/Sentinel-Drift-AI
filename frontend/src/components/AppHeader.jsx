/**
 * Top bar: sidebar toggle, API status, theme switcher and breadcrumb.
 */
import React, { useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {
  CContainer,
  CDropdown,
  CDropdownItem,
  CDropdownMenu,
  CDropdownToggle,
  CHeader,
  CHeaderNav,
  CHeaderToggler,
  useColorModes,
} from '@coreui/react'
import CIcon from '@coreui/icons-react'
import { cilContrast, cilMenu, cilMoon, cilSun } from '@coreui/icons'

import ApiStatus from './ApiStatus'
import AppBreadcrumb from './AppBreadcrumb'
import { THEME_STORAGE_KEY } from '../config'

const THEMES = [
  { value: 'light', label: 'Light', icon: cilSun },
  { value: 'dark', label: 'Dark', icon: cilMoon },
  { value: 'auto', label: 'Auto', icon: cilContrast },
]

const AppHeader = () => {
  const headerRef = useRef()
  const { colorMode, setColorMode } = useColorModes(THEME_STORAGE_KEY)
  const dispatch = useDispatch()
  const sidebarShow = useSelector((state) => state.sidebarShow)

  useEffect(() => {
    const handleScroll = () => {
      headerRef.current?.classList.toggle('shadow-sm', document.documentElement.scrollTop > 0)
    }
    document.addEventListener('scroll', handleScroll)
    return () => document.removeEventListener('scroll', handleScroll)
  }, [])

  const currentIcon = THEMES.find((t) => t.value === colorMode)?.icon || cilSun

  return (
    <CHeader position="sticky" className="mb-4 p-0" ref={headerRef}>
      <CContainer className="border-bottom px-4" fluid>
        <CHeaderToggler
          onClick={() => dispatch({ type: 'set', sidebarShow: !sidebarShow })}
          style={{ marginInlineStart: '-14px' }}
          aria-label="Toggle sidebar"
        >
          <CIcon icon={cilMenu} size="lg" />
        </CHeaderToggler>

        <CHeaderNav className="ms-auto align-items-center">
          <li className="nav-item">
            <ApiStatus />
          </li>
          <li className="nav-item py-1">
            <div className="vr h-100 mx-2 text-body text-opacity-75"></div>
          </li>
          <CDropdown variant="nav-item" placement="bottom-end">
            <CDropdownToggle caret={false} aria-label="Change theme">
              <CIcon icon={currentIcon} size="lg" />
            </CDropdownToggle>
            <CDropdownMenu>
              {THEMES.map((t) => (
                <CDropdownItem
                  key={t.value}
                  active={colorMode === t.value}
                  className="d-flex align-items-center"
                  as="button"
                  type="button"
                  onClick={() => setColorMode(t.value)}
                >
                  <CIcon className="me-2" icon={t.icon} size="lg" /> {t.label}
                </CDropdownItem>
              ))}
            </CDropdownMenu>
          </CDropdown>
        </CHeaderNav>
      </CContainer>
      <CContainer className="px-4" fluid>
        <AppBreadcrumb />
      </CContainer>
    </CHeader>
  )
}

export default AppHeader
