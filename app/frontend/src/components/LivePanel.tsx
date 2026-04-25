import { useEffect } from 'react'
import { type Telemetry } from '../api'
import { AsciiTelemetry } from './AsciiTelemetry'

type Props = {
  telemetry: Telemetry | null
  cameraAvailable: boolean | null
  onCameraStatus: (ok: boolean) => void
}

export function LivePanel({ telemetry, cameraAvailable, onCameraStatus }: Props) {
  // One-shot probe of the camera endpoint at mount.
  useEffect(() => {
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
      <span className="panel__index">02 / 02</span>

      <div className="live-stage">
        {cameraAvailable ? (
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
  const x = telemetry?.position.x ?? 0
  const y = telemetry?.position.y ?? 0

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
        <span className="hud__label">Pos · X</span>
        <span className="hud__value">{x.toFixed(2)} m</span>
      </div>
      <div className="hud__cell hud__cell--br">
        <span className="hud__label">Pos · Y</span>
        <span className="hud__value">{y.toFixed(2)} m</span>
      </div>
    </div>
  )
}
