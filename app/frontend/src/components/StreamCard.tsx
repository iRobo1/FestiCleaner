import { type Telemetry } from '../api'

// Hostname / IP of the Arduino UNO Q. When set, embed the on-board video
// stream from the video_object_detection brick. Set in .env.local —
// see .env.example.
const BOARD_HOST = import.meta.env.VITE_BOARD_HOST
const BOARD_STREAM = BOARD_HOST ? `http://${BOARD_HOST}:4912/embed` : null

type Props = {
  telemetry: Telemetry | null
}

export function StreamCard({ telemetry }: Props) {
  return (
    <section className="stream">
      {BOARD_STREAM ? (
        <iframe
          className="stream__iframe"
          src={BOARD_STREAM}
          title="Robot on-board camera feed"
          allow="autoplay"
        />
      ) : (
        <div className="stream__placeholder">
          <span className="stream__placeholder-eyebrow">No board configured</span>
          <p className="stream__placeholder-body">
            Set <code>VITE_BOARD_HOST</code> in <code>app/frontend/.env.local</code>{' '}
            to your Arduino's IP, then restart <code>bun run dev</code>.
          </p>
        </div>
      )}
      <Hud telemetry={telemetry} />
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
