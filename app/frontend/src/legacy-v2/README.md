# Legacy-v2 — naked-panes dashboard (snapshotted 2026-04-26)

A second checkpoint of the frontend, taken right before the next major
endeavour. This is the version with:

- **Landing page** (`Landing.tsx`) with the cascading "Festiclean" title,
  the Connect → Dashboard CTA, and the periodic sweeping rover
  (`components/RoamingRover.tsx`).
- **Dashboard** (`Dashboard.tsx`) on a locked **3 / 7 split** — no
  hover-swap, no `data-camera` attribute, no resizing animation.
- **Naked panes**: `.panel` is a transparent flex container; the map sits
  directly on the Panot tile floor with rounded corners; the live frame
  keeps only its dark-green inner card.
- **Trash → flowers reveal**: each cell shows its (i, j) slice of
  `/trash.png`; cleaning fades it to opacity 0 to reveal the matching
  slice of `/flowers.png` underneath. Cells are scaled `1.012` to hide
  sub-pixel grid hairlines.
- **Coverage chip** at the bottom-right of the map — cream pill with a
  backdrop-blur, container-query font scaling.
- **Black-text HUD** (battery / temp / X / Y) overlaid on the live video
  with a cream halo for legibility.
- **Ceramic Power button** in `.power-dock` at the bottom-center,
  optimistic UI, hits `/api/robot/{shutdown,start}`.
- **Performance**: `Dashboard` is `lazy()`-imported so the landing page
  ships ~9 KB lighter; `useTelemetry` is a module-level singleton with a
  `prewarmTelemetry()` function that the landing page calls in
  `requestIdleCallback` to open the WS + warm chunks + decode the heavy
  textures before navigation.

## How to restore

```sh
# from app/frontend/src/
cp legacy-v2/App.tsx App.tsx
cp legacy-v2/Landing.tsx Landing.tsx
cp legacy-v2/Dashboard.tsx Dashboard.tsx
cp legacy-v2/api.ts api.ts
cp legacy-v2/styles.css styles.css
cp legacy-v2/vite-env.d.ts vite-env.d.ts
cp -r legacy-v2/components/* components/
cp -r legacy-v2/hooks/* hooks/
```

## How this differs from `legacy/`

`legacy/` is the older snapshot from before the brief pivot to a
single-stream dashboard. It still has the **hover-swap split**, the
**Panot-tile dirty cells with sepia filter** (no trash/flowers), no
PowerButton, no RoamingRover, and no code-splitting.

This snapshot supersedes it as the closest-to-current reference.
