import { useState } from 'react'
import { useTelemetry } from './hooks/useTelemetry'
import { useCleanedCells } from './hooks/useCleanedCells'
import { MapPanel } from './components/MapPanel'
import { LivePanel } from './components/LivePanel'
import { EdgeReveal } from './components/EdgeReveal'
import { PowerButton } from './components/PowerButton'

export default function Dashboard() {
  const { telemetry, connected } = useTelemetry()
  const { cleaned, reset } = useCleanedCells(telemetry?.position)
  const [sessionStart] = useState(() => Date.now())
  const [cameraAvailable, setCameraAvailable] = useState<boolean | null>(null)

  return (
    <>
      <EdgeReveal connected={connected} sessionStart={sessionStart} onClear={reset} />
      <main className="split">
        <MapPanel cleaned={cleaned} position={telemetry?.position} />
        <LivePanel
          telemetry={telemetry}
          cameraAvailable={cameraAvailable}
          onCameraStatus={setCameraAvailable}
        />
      </main>
      <div className="power-dock">
        <PowerButton telemetry={telemetry} />
      </div>
    </>
  )
}
