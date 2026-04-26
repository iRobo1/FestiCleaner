import { type CSSProperties } from 'react'
import { CELL_SIZE, GRID_SIZE, type Position } from '../api'

type Props = {
  cleaned: Set<string>
  position?: Position
}

// Each cell shows its (i, j) slice of the trash photograph that covers the
// whole map. When a cell is marked "cleaned" it fades to opacity 0,
// revealing the matching slice of the flower garden underneath.
const denom = Math.max(1, GRID_SIZE - 1)

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
      const style: CSSProperties = {
        ['--i' as never]: i,
        ['--j' as never]: j,
      }
      cells.push(<div key={`${i},${j}`} className={cls} style={style} />)
    }
  }

  const mapStyle: CSSProperties = {
    gridTemplateColumns: `repeat(${GRID_SIZE}, 1fr)`,
    gridTemplateRows: `repeat(${GRID_SIZE}, 1fr)`,
    ['--cells' as never]: GRID_SIZE,
    ['--cells-denom' as never]: denom,
  }

  return (
    <section className="panel panel--map">
      <span className="panel__label">Map</span>
      <div className="map-stage">
        <div className="map" style={mapStyle}>
          {cells}
          <div className="coverage">
            <span className="coverage__num">{coverage.toFixed(1)}</span>
            <span className="coverage__label">% revealed</span>
          </div>
        </div>
      </div>
    </section>
  )
}
