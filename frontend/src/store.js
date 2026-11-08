/**
 * Redux store for UI state (sidebar and theme).
 * Server data (scans) is fetched per page and not stored here.
 */
import { legacy_createStore as createStore } from 'redux'

const initialState = {
  sidebarShow: true,
  sidebarUnfoldable: false,
  theme: 'light',
}

// dispatch({ type: 'set', sidebarShow: false })
const changeState = (state = initialState, { type, ...rest }) => {
  switch (type) {
    case 'set':
      return { ...state, ...rest }
    default:
      return state
  }
}

const store = createStore(changeState)
export default store
