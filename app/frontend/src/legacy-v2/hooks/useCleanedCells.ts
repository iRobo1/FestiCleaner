import { useCallback, useEffect, useState } from 'react'
import { CELL_SIZE, CLEAN_RADIUS_M, GRID_SIZE, type Position } from '../api'

// Cells whose center lies inside the cleaning radius around (rx, ry).
// Demo-only: real coverage would come from the robot/sensors.
function cellsInRadius(rx: number, ry: number): Array<[number, number]> {
  const out: Array<[number, number]> = []
  const r2 = CLEAN_RADIUS_M * CLEAN_RADIUS_M
  const minI = Math.max(0, Math.floor((rx - CLEAN_RADIUS_M) / CELL_SIZE))
  const maxI = Math.min(GRID_SIZE - 1, Math.floor((rx + CLEAN_RADIUS_M) / CELL_SIZE))
  const minJ = Math.max(0, Math.floor((ry - CLEAN_RADIUS_M) / CELL_SIZE))
  const maxJ = Math.min(GRID_SIZE - 1, Math.floor((ry + CLEAN_RADIUS_M) / CELL_SIZE))
  for (let i = minI; i <= maxI; i++) {
    for (let j = minJ; j <= maxJ; j++) {
      const cx = (i + 0.5) * CELL_SIZE
      const cy = (j + 0.5) * CELL_SIZE
      const dx = cx - rx
      const dy = cy - ry
      if (dx * dx + dy * dy <= r2) out.push([i, j])
    }
  }
  return out
}

export function useCleanedCells(position: Position | undefined) {
  const [cleaned, setCleaned] = useState<Set<string>>(() => new Set())

  useEffect(() => {
    if (!position) return
    const newCells = cellsInRadius(position.x, position.y)
    if (newCells.length === 0) return
    setCleaned((prev) => {
      let changed = false
      const next = new Set(prev)
      for (const [i, j] of newCells) {
        const key = `${i},${j}`
        if (!next.has(key)) {
          next.add(key)
          changed = true
        }
      }
      return changed ? next : prev
    })
  }, [position?.x, position?.y])

  const reset = useCallback(() => setCleaned(new Set()), [])
  return { cleaned, reset }
}
