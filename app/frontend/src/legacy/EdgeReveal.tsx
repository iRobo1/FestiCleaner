import { useEffect, useState } from 'react'
import { type Stats } from '../api'

type Props = {
  connected: boolean
  sessionStart: number
  onClear: () => void
}

export function EdgeReveal({ connected, sessionStart, onClear }: Props) {
  const [stats, setStats] = useState<Stats | null>(null)
  const [now, setNow] = useState(Date.now())

  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    let cancelled = false
    async function fetchStats() {
      try {
        const res = await fetch('/api/stats')
        if (!res.ok) return
        const data: Stats = await res.json()
        if (!cancelled) setStats(data)
      } catch {
        // backend not running yet — ignore
      }
    }
    fetchStats()
    const id = setInterval(fetchStats, 3000)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [])

  async function captureSnapshot() {
    try {
      const res = await fetch('/api/camera/snapshot')
      if (!res.ok) {
        alert(`Snapshot failed: HTTP ${res.status}`)
        return
      }
      const data = await res.json()
      alert(`Snapshot ${data.id} archived`)
    } catch {
      alert('Snapshot failed: backend unreachable')
    }
  }

  const elapsed = Math.floor((now - sessionStart) / 1000)
  const hh = String(Math.floor(elapsed / 3600)).padStart(2, '0')
  const mm = String(Math.floor((elapsed % 3600) / 60)).padStart(2, '0')
  const ss = String(elapsed % 60).padStart(2, '0')

  return (
    <>
      <div className="edge-zone" aria-hidden />
      <header className="edge">
        <div className="edge__left">
          <span className={`edge__dot ${connected ? 'on' : ''}`} aria-label={connected ? 'connected' : 'offline'} />
          <span className="edge__brand">Festiclean · Barcelona</span>
        </div>
        <div className="edge__right">
          <span>
            T+ {hh}:{mm}:{ss}
          </span>
          <span className="edge__sep">/</span>
          <span>{stats?.total_telemetry_readings ?? 0} readings</span>
          <span className="edge__sep">/</span>
          <span>{stats?.total_camera_snapshots ?? 0} snapshots</span>
          <button className="edge__btn" onClick={captureSnapshot}>
            Capture
          </button>
          <button className="edge__btn edge__btn--danger" onClick={onClear}>
            Clear floor
          </button>
        </div>
      </header>
    </>
  )
}
