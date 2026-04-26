import { type Phase, type PhaseKey, PHASE_KEYS, PHASE_LABELS } from '../api'

// Geometry — wheel of radius 150 centered at (240, 240) in a 480-square viewBox.
// Nodes sit at the cardinal points; arc endpoints are inset 16.1° from each
// node so the connecting arrows don't punch into the node circles.
type Node = { key: PhaseKey; cx: number; cy: number }
const NODES: Node[] = [
  { key: 'search', cx: 240, cy: 90  },  // 12 o'clock
  { key: 'fetch',  cx: 390, cy: 240 },  //  3 o'clock
  { key: 'return', cx: 240, cy: 390 },  //  6 o'clock
  { key: 'drop',   cx: 90,  cy: 240 },  //  9 o'clock
]

// Connecting arcs (clockwise loop). Endpoints computed once; see plan file
// for the math (16.1° inset on each side of each 90° quadrant).
const ARCS = [
  'M 282 96  A 150 150 0 0 1 384 198',  // search → fetch
  'M 384 282 A 150 150 0 0 1 282 384',  // fetch  → return
  'M 198 384 A 150 150 0 0 1 96 282',   // return → drop
  'M 96 198  A 150 150 0 0 1 198 96',   // drop   → search
]

type Props = {
  phase: Phase | null | undefined
}

export function StateWheel({ phase }: Props) {
  const activeKey = phase ? PHASE_KEYS[phase - 1] : ''

  return (
    <section className="panel panel--map">
      <span className="panel__label">Phase</span>
      <div className="map-stage">
        <div className="wheel" data-active={activeKey}>
          <svg viewBox="0 0 480 480" className="wheel__svg" aria-hidden>
            <defs>
              <marker
                id="wheel-arrow"
                viewBox="0 0 10 10"
                refX="8"
                refY="5"
                markerWidth="5"
                markerHeight="5"
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#b85c38" />
              </marker>
            </defs>

            <g className="wheel__arcs">
              {ARCS.map((d, i) => (
                <path key={i} d={d} markerEnd="url(#wheel-arrow)" />
              ))}
            </g>

            <g className="wheel__nodes">
              {NODES.map((n) => (
                <g
                  key={n.key}
                  data-node={n.key}
                  className="wheel__node"
                  style={{ transformOrigin: `${n.cx}px ${n.cy}px` }}
                >
                  <circle cx={n.cx} cy={n.cy} r={42} className="wheel__node-circle" />
                  <text x={n.cx} y={n.cy} className="wheel__node-label">
                    {PHASE_LABELS[n.key].toUpperCase()}
                  </text>
                </g>
              ))}
            </g>
          </svg>
        </div>
      </div>
    </section>
  )
}
