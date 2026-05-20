import { v4 as uuidv4 } from 'uuid'

const KEY = 'chatbox.client_id'

export function getClientId(): string {
  try {
    const cached = localStorage.getItem(KEY)
    if (cached) return cached
    const fresh = uuidv4()
    localStorage.setItem(KEY, fresh)
    return fresh
  } catch (_e) {
    return 'anonymous'
  }
}
