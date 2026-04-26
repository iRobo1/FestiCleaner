import { useEffect, useState } from 'react'
import { CELL_SIZE, GRID_SIZE, type Telemetry } from '../api'

const ASCII_W = 28

function batteryBar(pct: number): { filled: string; empty: string } {
  const filled = Math.round((pct / 100) * ASCII_W)
  return {
    filled: '█'.repeat(filled),
    empty: '░'.repeat(ASCII_W - filled),
  }
}

function asciiMap(x: number, y: number): { rows: string[]; here: { row: number; col: number } } {
  const cols = 24
  const rows = 10
  const worldW = GRID_SIZE * CELL_SIZE
  const worldH = GRID_SIZE * CELL_SIZE
  const col = Math.min(cols - 1, Math.max(0, Math.floor((x / worldW) * cols)))
  const row = Math.min(rows - 1, Math.max(0, Math.floor((y / worldH) * rows)))
  const out: string[] = []
  for (let r = 0; r < rows; r++) {
    let line = ''
    for (let c = 0; c < cols; c++) {
      if (r === row && c === col) line += '◯'
      else line += '·'
    }
    out.push(line)
  }
  return { rows: out, here: { row, col } }
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
  const x = telemetry?.position.x ?? 0
  const y = telemetry?.position.y ?? 0

  const map = asciiMap(x, y)
  const bar = batteryBar(battery)

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
            <span className="filled">{bar.filled}</span>
            <span className="empty">{bar.empty}</span>
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
          <span className="ascii__row-label">
            Position · {x.toFixed(2)} m, {y.toFixed(2)} m
          </span>
          <pre className="ascii__map">
            {map.rows.map((line, idx) => (
              <span key={idx}>
                {idx === map.here.row ? (
                  <>
                    {line.slice(0, map.here.col)}
                    <span className="here">◯</span>
                    {line.slice(map.here.col + 1)}
                  </>
                ) : (
                  line
                )}
                {'\n'}
              </span>
            ))}
          </pre>
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
