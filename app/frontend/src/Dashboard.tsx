import { useState } from 'react'
import { useTelemetry } from './hooks/useTelemetry'
import { StateWheel } from './components/StateWheel'
import { LivePanel } from './components/LivePanel'
import { EdgeReveal } from './components/EdgeReveal'
import { PowerButton } from './components/PowerButton'

export default function Dashboard() {
  const { telemetry, connected } = useTelemetry()
  const [sessionStart] = useState(() => Date.now())
  const [cameraAvailable, setCameraAvailable] = useState<boolean | null>(null)

  return (
    <>
      <EdgeReveal connected={connected} sessionStart={sessionStart} />
      <main className="split">
        <StateWheel phase={telemetry?.phase} />
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
