import { CELL_SIZE, GRID_SIZE, type Position } from '../api'

type Props = {
  cleaned: Set<string>
  position?: Position
}

export function MapPanel({ cleaned, position }: Props) {
  const totalCells = GRID_SIZE * GRID_SIZE
  const coverage = (cleaned.size / totalCells) * 100
  const robotCell = position
    ? {
        i: Math.min(GRID_SIZE - 1, Math.max(0, Math.floor(position.x / CELL_SIZE))),
        j: Math.min(GRID_SIZE - 1, Math.max(0, Math.floor(position.y / CELL_SIZE))),
      }
    : null

  const cells = []
  for (let j = 0; j < GRID_SIZE; j++) {
    for (let i = 0; i < GRID_SIZE; i++) {
      const isCleaned = cleaned.has(`${i},${j}`)
      const isRobot = robotCell?.i === i && robotCell?.j === j
      const cls = `cell${isCleaned ? ' cleaned' : ''}${isRobot ? ' robot' : ''}`
      cells.push(<div key={`${i},${j}`} className={cls} />)
    }
  }

  return (
    <section className="panel panel--map">
      <span className="panel__label">Map</span>
      <span className="panel__index">01 / 02</span>
      <div className="map-stage">
        <div className="map">{cells}</div>
        <div className="coverage">
          <span className="coverage__num">{coverage.toFixed(1)}</span>
          <span className="coverage__label">% revealed</span>
        </div>
      </div>
    </section>
  )
}
