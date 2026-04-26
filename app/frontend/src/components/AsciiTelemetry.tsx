import { useEffect, useState } from 'react'
import { PHASE_KEYS, PHASE_LABELS, type Telemetry } from '../api'

const ASCII_W = 28

function meterBar(pct: number, char: string): { filled: string; empty: string } {
  const filled = Math.round((pct / 100) * ASCII_W)
  return {
    filled: char.repeat(filled),
    empty: '░'.repeat(ASCII_W - filled),
  }
}

type Props = { telemetry: Telemetry | null }

export function AsciiTelemetry({ telemetry }: Props) {
  const [stamp, setStamp] = useState(() => formatStamp(new Date()))

  useEffect(() => {
    const id = setInterval(() => setStamp(formatStamp(new Date())), 1000)
    return () => clearInterval(id)
  }, [])

  const battery = telemetry?.battery ?? 0
  const temp = telemetry?.temperature ?? 0
  const humidity = telemetry?.humidity ?? 0
  const phaseKey = telemetry?.phase ? PHASE_KEYS[telemetry.phase - 1] : null
  const phaseLabel = phaseKey ? PHASE_LABELS[phaseKey].toUpperCase() : '—'

  const batteryMeter = meterBar(battery, '█')
  const humidityMeter = meterBar(humidity, '▓')

  return (
    <div className="ascii">
      <div className="ascii__head">
        <span className="ascii__title">Typeset Feed</span>
        <span className="ascii__time">{stamp}</span>
      </div>

      <div className="ascii__body">
        <div className="ascii__row">
          <span className="ascii__row-label">Battery · {battery.toFixed(1)}%</span>
          <span className="ascii__bar">
            <span className="filled">{batteryMeter.filled}</span>
            <span className="empty">{batteryMeter.empty}</span>
          </span>
        </div>

        <div className="ascii__row">
          <span className="ascii__row-label">Humidity · {humidity.toFixed(1)}%</span>
          <span className="ascii__bar ascii__bar--humid">
            <span className="filled">{humidityMeter.filled}</span>
            <span className="empty">{humidityMeter.empty}</span>
          </span>
        </div>

        <div className="ascii__row">
          <span className="ascii__row-label">Temperature</span>
          <div className="ascii__temp">
            <span className="ascii__temp-num">{temp.toFixed(1)}</span>
            <span className="ascii__temp-unit">°C</span>
          </div>
        </div>

        <div className="ascii__row">
          <span className="ascii__row-label">Phase</span>
          <div className="ascii__temp">
            <span className="ascii__temp-num">{phaseLabel}</span>
          </div>
        </div>

        <div className="ascii__caption">
          No camera connected — typesetting telemetry in real time. The robot is still working.
        </div>
      </div>
    </div>
  )
}

function formatStamp(d: Date): string {
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  const ss = String(d.getSeconds()).padStart(2, '0')
  return `${hh}:${mm}:${ss}`
}
