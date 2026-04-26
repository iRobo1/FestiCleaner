import { useTelemetry } from './hooks/useTelemetry'
import { StreamCard } from './components/StreamCard'
import { PowerButton } from './components/PowerButton'

export default function App() {
  const { telemetry } = useTelemetry()

  return (
    <main className="stage">
      <span className="brand">Festiclean · Barcelona</span>
      <StreamCard telemetry={telemetry} />
      <PowerButton telemetry={telemetry} />
    </main>
  )
}
