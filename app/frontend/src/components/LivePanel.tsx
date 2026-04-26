import { useEffect } from 'react'
import { type Telemetry } from '../api'
import { AsciiTelemetry } from './AsciiTelemetry'

// Hostname / IP of the Arduino UNO Q. When defined, embed the on-board
// video stream (served by the video_object_detection brick at port 4912)
// and skip probing the FastAPI camera endpoint.
//
// Set in app/frontend/.env.local — see .env.example.
const BOARD_HOST = import.meta.env.VITE_BOARD_HOST
const BOARD_STREAM = BOARD_HOST ? `http://${BOARD_HOST}:4912/embed` : null

type Props = {
  telemetry: Telemetry | null
  cameraAvailable: boolean | null
  onCameraStatus: (ok: boolean) => void
}

export function LivePanel({ telemetry, cameraAvailable, onCameraStatus }: Props) {
  useEffect(() => {
    if (BOARD_STREAM) {
      // Trust the board: report camera as available so the layout becomes
      // livestream-dominant. We can't easily detect iframe load failures
      // cross-origin, so this is intentionally optimistic.
      onCameraStatus(true)
      return
    }

    // No board configured — fall back to the local FastAPI camera probe.
    let cancelled = false
    fetch('/api/camera/frame')
      .then((r) => {
        if (!cancelled) onCameraStatus(r.ok)
      })
      .catch(() => {
        if (!cancelled) onCameraStatus(false)
      })
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <section className="panel panel--live">
      <span className="panel__label">Live</span>

      <div className="live-stage">
        {BOARD_STREAM ? (
          <div className="live-frame">
            <iframe
              className="live-iframe"
              src={BOARD_STREAM}
              title="Robot on-board camera feed"
              allow="autoplay"
            />
            <Hud telemetry={telemetry} />
          </div>
        ) : cameraAvailable ? (
          <div className="live-frame">
            <img
              src="/api/camera/stream"
              alt="Robot camera feed"
              onError={() => onCameraStatus(false)}
            />
            <Hud telemetry={telemetry} />
          </div>
        ) : (
          <AsciiTelemetry telemetry={telemetry} />
        )}
      </div>
    </section>
  )
}

function Hud({ telemetry }: { telemetry: Telemetry | null }) {
  const battery = telemetry?.battery ?? 0
  const temp = telemetry?.temperature ?? 0
  const humidity = telemetry?.humidity ?? 0

  return (
    <div className="hud">
      <div className="hud__cell hud__cell--tl">
        <span className="hud__label">Battery</span>
        <span className="hud__value">{battery.toFixed(1)}%</span>
      </div>
      <div className="hud__cell hud__cell--tr">
        <span className="hud__label">Temp</span>
        <span className="hud__value">{temp.toFixed(1)}°C</span>
      </div>
      <div className="hud__cell hud__cell--bl">
        <span className="hud__label">Humidity</span>
        <span className="hud__value">{humidity.toFixed(1)}%</span>
      </div>
    </div>
  )
}
