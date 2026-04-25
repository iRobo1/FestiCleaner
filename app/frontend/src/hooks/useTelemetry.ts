import { useEffect, useRef, useState } from 'react'
import { type Telemetry, WS_BASE } from '../api'

export function useTelemetry() {
  const [telemetry, setTelemetry] = useState<Telemetry | null>(null)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    let cancelled = false
    let retryTimer: ReturnType<typeof setTimeout> | null = null

    function connect() {
      if (cancelled) return
      const ws = new WebSocket(`${WS_BASE}/ws/telemetry`)
      wsRef.current = ws

      ws.onopen = () => setConnected(true)
      ws.onclose = () => {
        setConnected(false)
        if (!cancelled) retryTimer = setTimeout(connect, 1000)
      }
      ws.onerror = () => ws.close()
      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data)
          if (msg.type === 'telemetry') setTelemetry(msg.data)
        } catch {
          // ignore malformed frames
        }
      }
    }

    connect()
    return () => {
      cancelled = true
      if (retryTimer) clearTimeout(retryTimer)
      wsRef.current?.close()
    }
  }, [])

  return { telemetry, connected }
}
