import { useEffect, useState } from 'react'

// A tiny rover with a broom drives across the bottom of the landing page
// every 25-45 seconds. Each pass lasts ~14 s. Easter-egg pacing — gentle
// reminder of what the project does without being constantly on-screen.

const MIN_GAP_MS = 25_000
const MAX_GAP_MS = 45_000
const DRIVE_DURATION_MS = 14_000
const FIRST_DRIVE_DELAY_MS = 4_000

export function RoamingRover() {
  // Bumped each cycle. The `key` on the rendered element resets the CSS
  // animation so the rover starts fresh on every drive-by.
  const [pass, setPass] = useState(0)
  // When `false`, the rover element is unmounted (offscreen between runs).
  const [driving, setDriving] = useState(false)

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>

    function scheduleNextRun(delay: number) {
      timer = setTimeout(() => {
        setPass((p) => p + 1)
        setDriving(true)
        // After the animation completes, hide the rover and schedule again.
        timer = setTimeout(() => {
          setDriving(false)
          const gap =
            MIN_GAP_MS + Math.random() * (MAX_GAP_MS - MIN_GAP_MS)
          scheduleNextRun(gap)
        }, DRIVE_DURATION_MS + 200)
      }, delay)
    }

    scheduleNextRun(FIRST_DRIVE_DELAY_MS)
    return () => clearTimeout(timer)
  }, [])

  if (!driving) return null

  return (
    <div className="rover" key={pass} aria-hidden>
      <svg viewBox="0 0 120 70" className="rover__svg">
        {/* Trailing dust — fades out behind the broom */}
        <g className="rover__dust">
          <circle cx="2"  cy="58" r="1.6" fill="#b85c38" opacity="0.55" />
          <circle cx="-4" cy="62" r="1.2" fill="#b85c38" opacity="0.4"  />
          <circle cx="-9" cy="56" r="1"   fill="#b85c38" opacity="0.25" />
          <circle cx="-14" cy="60" r="0.8" fill="#b85c38" opacity="0.15" />
        </g>

        {/* Broom (trailing left as rover moves right) */}
        <g className="rover__broom">
          <line x1="20" y1="40" x2="6" y2="54"
                stroke="#b85c38" strokeWidth="2.4" strokeLinecap="round" />
          <line x1="6" y1="54" x2="0" y2="62" stroke="#093624" strokeWidth="1" />
          <line x1="6" y1="54" x2="3" y2="62" stroke="#093624" strokeWidth="1" />
          <line x1="6" y1="54" x2="9" y2="62" stroke="#093624" strokeWidth="1" />
          <line x1="6" y1="54" x2="12" y2="62" stroke="#093624" strokeWidth="1" />
        </g>

        {/* Body */}
        <rect x="22" y="20" width="60" height="22" rx="5" fill="#093624" />
        {/* highlight stripe */}
        <rect x="24" y="22" width="56" height="5" rx="2" fill="#f1efe6" opacity="0.28" />
        {/* "porthole" window */}
        <circle cx="68" cy="32" r="4" fill="#f1efe6" opacity="0.35" />
        <circle cx="68" cy="32" r="2" fill="#d4a24c" />

        {/* Antenna + status pip */}
        <line x1="32" y1="20" x2="32" y2="10"
              stroke="#093624" strokeWidth="1.5" />
        <circle cx="32" cy="9" r="2.2" fill="#d4a24c" className="rover__pip" />

        {/* Wheels */}
        <g className="rover__wheels">
          <g transform="translate(34, 46)">
            <circle r="7" fill="#093624" />
            <circle r="2.4" fill="#f1efe6" />
            <line x1="-7" y1="0" x2="7" y2="0" stroke="#f1efe6" strokeWidth="0.8" />
            <line x1="0" y1="-7" x2="0" y2="7" stroke="#f1efe6" strokeWidth="0.8" />
          </g>
          <g transform="translate(70, 46)">
            <circle r="7" fill="#093624" />
            <circle r="2.4" fill="#f1efe6" />
            <line x1="-7" y1="0" x2="7" y2="0" stroke="#f1efe6" strokeWidth="0.8" />
            <line x1="0" y1="-7" x2="0" y2="7" stroke="#f1efe6" strokeWidth="0.8" />
          </g>
        </g>
      </svg>
    </div>
  )
}
