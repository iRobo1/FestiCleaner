# Legacy components — pre-pivot dashboard

Snapshots from before the 2026-04-26 frontend pivot, when the dashboard
was a two-panel `MapPanel` + `LivePanel` layout with a hover-swap split,
floor-coverage cleaning visualization, and a hidden `EdgeReveal` top bar.

| File | Was at |
|---|---|
| `Dashboard.tsx` | the body of the previous `App.tsx` (router-less single-page dashboard) |
| `MapPanel.tsx` | `components/MapPanel.tsx` — the 40×40 Panot-tile reveal grid |
| `EdgeReveal.tsx` | `components/EdgeReveal.tsx` — top hover-pill with timer / capture / clear / power |
| `AsciiTelemetry.tsx` | `components/AsciiTelemetry.tsx` — typeset fallback when the camera was offline |
| `LivePanel.tsx` | `components/LivePanel.tsx` — wrapped the iframe / img fallback / ASCII fallback |
| `useCleanedCells.ts` | `hooks/useCleanedCells.ts` — radius-based cleaning logic |
| `styles-snapshot.css` | the full `styles.css` as it was at the pivot point |

Nothing in this folder is wired into the build — Vite tree-shakes it
out. To restore: copy back to the original paths, replace `App.tsx`
with `Dashboard.tsx`, and re-add the corresponding sections from
`styles-snapshot.css` into the live `styles.css`.
