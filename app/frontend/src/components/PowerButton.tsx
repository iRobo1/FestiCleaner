import { useEffect, useState } from 'react'
import { type Telemetry } from '../api'

type Props = {
  telemetry: Telemetry | null
}

export function PowerButton({ telemetry }: Props) {
  // Optimistic local mirror so the button reacts instantly; reconciled the
  // next time telemetry arrives (or on an explicit failure).
  const [optimistic, setOptimistic] = useState<boolean | null>(null)
  const [busy, setBusy] = useState(false)

  // Reset optimistic state once the WebSocket confirms the new value.
  useEffect(() => {
    if (telemetry?.is_active === optimistic) {
      setOptimistic(null)
    }
  }, [telemetry?.is_active, optimistic])

  const isActive = optimistic ?? telemetry?.is_active ?? true

  async function toggle() {
    if (busy) return
    const next = !isActive
    setOptimistic(next)
    setBusy(true)
    const endpoint = next ? '/api/robot/start' : '/api/robot/shutdown'
    try {
      const res = await fetch(endpoint, { method: 'POST' })
      if (!res.ok) {
        setOptimistic(null)
        alert(`Power toggle failed: HTTP ${res.status}`)
      }
    } catch {
      setOptimistic(null)
      alert('Power toggle failed: backend unreachable')
    } finally {
      setBusy(false)
    }
  }

  return (
    <button
      className={`power ${isActive ? '' : 'power--off'}`}
      onClick={toggle}
      aria-pressed={!isActive}
      disabled={busy}
    >
      <span className="power__pip" aria-hidden />
      <span className="power__label">
        {isActive ? 'Power · On' : 'Powered Off'}
      </span>
    </button>
  )
}
