import { type CSSProperties, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { RoamingRover } from './components/RoamingRover'
import { prewarmTelemetry } from './hooks/useTelemetry'

// Warm up the dashboard ahead of the click. Fired on landing-page mount so
// by the time the user hits "Connect" the chunk, the heavy floor textures,
// and the telemetry WebSocket are already live.
function prefetchDashboard() {
  // The exact import path Vite uses; resolves to the same chunk as the
  // lazy() call in App.tsx, so this just primes the network/HTTP cache.
  void import('./Dashboard')
  for (const src of ['/trash.png', '/flowers.png']) {
    const img = new Image()
    img.src = src
  }
  // Open the telemetry WebSocket now so the dashboard renders with data
  // already in hand instead of an empty HUD waiting on the handshake.
  prewarmTelemetry()
}

/* ---------------------------------------------------------------------------
   ✏️ EDIT ME — All copy on this page is placeholder lorem ipsum. Search for
   the comments tagged "EDIT ME" to find each text block and replace it with
   real copy when you're ready.
   --------------------------------------------------------------------------- */

const TITLE = 'Festiclean'
const TILTS = [-1.4, 0.6, -1.0, 1.6, -2.1, 1.1, -0.7, 0.9, -1.2, 1.5]

export default function Landing() {
  // Kick off the dashboard chunk + image preloads once. Idle-callback if
  // available so we don't compete with the landing page's first paint.
  useEffect(() => {
    type IdleAPI = (cb: () => void) => void
    const ric: IdleAPI =
      (window as unknown as { requestIdleCallback?: IdleAPI }).requestIdleCallback ??
      ((cb) => setTimeout(cb, 200))
    ric(prefetchDashboard)
  }, [])

  return (
    <main className="landing">
      <header className="landing__nav">
        <span className="landing__nav-mark">Festiclean</span>
        <span className="landing__nav-meta">Barcelona · Demo 2026</span>
      </header>

      <section className="landing__hero">
        {/* EDIT ME — eyebrow / kicker line above the title */}
        <span className="landing__eyebrow">— A post-festival cleaning rover</span>

        {/* EDIT ME — main project title (animated letter-by-letter) */}
        <h1 className="landing__title" aria-label={TITLE}>
          {Array.from(TITLE).map((ch, i) => {
            const style: CSSProperties = {
              ['--i' as never]: i,
              ['--rest-rot' as never]: `${TILTS[i] ?? 0}deg`,
            }
            return (
              <span key={i} className="landing__title-letter" style={style} aria-hidden>
                {ch}
              </span>
            )
          })}
          <span
            className="landing__title-letter landing__title-dot"
            style={{
              ['--i' as never]: TITLE.length,
              ['--rest-rot' as never]: '0deg',
            } as CSSProperties}
            aria-hidden
          >
            .
          </span>
        </h1>

        {/* EDIT ME — single-line subtitle / tagline */}
        <p className="landing__subtitle">
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
          tempor incididunt.
        </p>

        {/* EDIT ME — body paragraph (project description, ~2–4 sentences) */}
        <p className="landing__body">
          Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi
          ut aliquip ex ea commodo consequat. Duis aute irure dolor in
          reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
          pariatur.
        </p>

        <Link to="/dashboard" className="landing__cta">
          <span>Connect</span>
          <span className="landing__cta-arrow" aria-hidden>
            →
          </span>
        </Link>

        <p className="landing__note">
          {/* EDIT ME — tiny helper line under the CTA, optional */}
          Streams live from <code>192.168.x.x</code> on the festival network.
        </p>
      </section>

      {/* 🤖 Periodic sweeping rover — drives across the bottom every 25-45s. */}
      <RoamingRover />

      <footer className="landing__footer">
        <span>HackUPC 2026</span>
        <span className="landing__sep">·</span>
        <span>Built on Arduino UNO Q + FastAPI + React</span>
      </footer>
    </main>
  )
}
