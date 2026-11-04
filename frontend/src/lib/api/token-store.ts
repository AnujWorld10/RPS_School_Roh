export type SessionEndReason = 'expired' | 'logout' | 'authentication-failed'

export type SessionTokens = {
  accessToken: string
  refreshToken: string
}

export type SessionSnapshot = {
  tokens: SessionTokens | null
  endReason: SessionEndReason | null
}

const serverSnapshot: SessionSnapshot = { tokens: null, endReason: null }
let snapshot = serverSnapshot
const listeners = new Set<() => void>()

function notifyListeners() {
  listeners.forEach((listener) => listener())
}

export function getSessionSnapshot() {
  return snapshot
}

export function getServerSessionSnapshot() {
  return serverSnapshot
}

export function subscribeToSession(listener: () => void) {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

export function getAccessToken() {
  return snapshot.tokens?.accessToken ?? null
}

export function getRefreshToken() {
  return snapshot.tokens?.refreshToken ?? null
}

export function setSessionTokens(tokens: SessionTokens) {
  snapshot = { tokens, endReason: null }
  notifyListeners()
}

export function clearSessionTokens(reason: SessionEndReason) {
  snapshot = { tokens: null, endReason: reason }
  notifyListeners()
}
