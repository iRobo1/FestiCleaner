import { useEffect, useState } from 'react'
import { type Telemetry, WS_BASE } from '../api'

// ── Module-level singleton ─────────────────────────────────────────────────
// One WebSocket per browser tab, opened on first call to either
// `prewarmTelemetry()` or `useTelemetry()`. Multiple components and routes
// share the same connection — the WS stays open across navigation, so the
// dashboard renders with telemetry already available instead of waiting
// 100-300 ms for the handshake on its mount.

let socket: WebSocket | null = null
let latestTelemetry: Telemetry | null = null
let isConnected = false
let retryTimer: ReturnType<typeof setTimeout> | null = null
const subscribers = new Set<() => void>()

function notify() {
  for (const cb of subscribers) cb()
}

function connect() {
  if (socket) return
  const ws = new WebSocket(`${WS_BASE}/ws/telemetry`)
  socket = ws

  ws.onopen = () => {
    isConnected = true
    notify()
  }
  ws.onclose = () => {
    isConnected = false
    socket = null
    notify()
    // Auto-reconnect — only if there are still subscribers OR the prewarm
    // call kicked us off. Either way, keep trying once a second.
    if (retryTimer) clearTimeout(retryTimer)
    retryTimer = setTimeout(connect, 1000)
  }
  ws.onerror = () => ws.close()
  ws.onmessage = (e) => {
    try {
      const msg = JSON.parse(e.data)
      if (msg.type === 'telemetry') {
        latestTelemetry = msg.data
        notify()
      }
    } catch {
      // ignore malformed frames
    }
  }
}

/**
 * Open the telemetry WebSocket eagerly — call from any page that wants the
 * connection ready before another route mounts the `useTelemetry()` hook.
 * Idempotent and safe to call repeatedly.
 */
export function prewarmTelemetry(): void {
  if (!socket) connect()
}

export function useTelemetry() {
  // Local force-update — the singleton notifies us whenever its values
  // change; we re-render in response. Cheaper than React's useSyncExternalStore
  // for our two values.
  const [, force] = useState(0)

  useEffect(() => {
    const cb = () => force((n) => n + 1)
    subscribers.add(cb)
    if (!socket) connect()
    return () => {
      subscribers.delete(cb)
      // Intentionally do NOT close the socket on unmount. The singleton
      // outlives any single component so re-mounts (e.g. on route change)
      // are instant.
    }
  }, [])

  return { telemetry: latestTelemetry, connected: isConnected }
}
