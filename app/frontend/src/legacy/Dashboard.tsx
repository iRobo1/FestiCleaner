import { useState } from 'react'
import { useTelemetry } from './hooks/useTelemetry'
import { useCleanedCells } from './hooks/useCleanedCells'
import { MapPanel } from './components/MapPanel'
import { LivePanel } from './components/LivePanel'
import { EdgeReveal } from './components/EdgeReveal'

export default function App() {
  const { telemetry, connected } = useTelemetry()
  const { cleaned, reset } = useCleanedCells(telemetry?.position)
  const [sessionStart] = useState(() => Date.now())
  const [cameraAvailable, setCameraAvailable] = useState<boolean | null>(null)

  // Adaptive default split: livestream-dominant when camera is on, else map-dominant.
  const cameraAttr = cameraAvailable ? 'on' : 'off'

  return (
    <>
      <EdgeReveal connected={connected} sessionStart={sessionStart} onClear={reset} />
      <main className="split" data-camera={cameraAttr}>
        <MapPanel cleaned={cleaned} position={telemetry?.position} />
        <LivePanel
          telemetry={telemetry}
          cameraAvailable={cameraAvailable}
          onCameraStatus={setCameraAvailable}
        />
      </main>
    </>
  )
}
