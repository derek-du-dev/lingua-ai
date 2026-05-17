import { reactive } from 'vue'
import { loginAuthLoginPost, readCurrentUserAuthMeGet } from '../api/client/sdk.gen'
import type { UserPublic } from '../api/client/types.gen'
import { getApiErrorMessage, setApiToken } from './api'

const TOKEN_KEY = 'lingua_ai_token'
const USER_KEY = 'lingua_ai_user'

export const authState = reactive({
  token: '',
  user: null as UserPublic | null,
  restored: false,
})

let restorePromise: Promise<UserPublic | null> | null = null

function persistSession(token: string, user: UserPublic) {
  authState.token = token
  authState.user = user
  setApiToken(token)
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function logout() {
  authState.token = ''
  authState.user = null
  authState.restored = true
  setApiToken(null)
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function isAuthenticated() {
  return Boolean(authState.token && authState.user)
}

export function isAdmin() {
  return authState.user?.user_type === 3
}

export function isManager() {
  return authState.user?.user_type === 2 || authState.user?.user_type === 3
}

export async function login(username: string, password: string) {
  const result = await loginAuthLoginPost({
    body: {
      username,
      password,
    },
  })

  if (result.error || !result.data) {
    throw new Error(getApiErrorMessage(result.error, '登录遇到了一点小问题，请稍后再试。'))
  }

  persistSession(result.data.access_token, result.data.user)
  authState.restored = true
  return result.data.user
}

export async function restoreSession() {
  if (authState.restored) {
    return authState.user
  }

  if (restorePromise) {
    return restorePromise
  }

  restorePromise = restoreSessionInternal().finally(() => {
    restorePromise = null
  })

  return restorePromise
}

async function restoreSessionInternal() {
  const token = localStorage.getItem(TOKEN_KEY)
  const storedUser = localStorage.getItem(USER_KEY)

  if (!token) {
    logout()
    return null
  }

  authState.token = token
  setApiToken(token)

  if (storedUser) {
    try {
      authState.user = JSON.parse(storedUser) as UserPublic
    } catch {
      authState.user = null
    }
  }

  const result = await readCurrentUserAuthMeGet()
  if (result.data) {
    persistSession(token, result.data)
    authState.restored = true
    return result.data
  }

  logout()
  return null
}
