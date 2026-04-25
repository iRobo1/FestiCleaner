export const GRID_SIZE = 20
export const CELL_SIZE = 0.5
// Demo simplification: treat the robot as cleaning everything inside
// a circle of this radius (meters) around its current position.
export const CLEAN_RADIUS_M = 0.75

export const WS_BASE = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}`

export type Position = { x: number; y: number }

export type Telemetry = {
  battery: number
  temperature: number
  position: Position
  is_active: boolean
  last_update?: string
}

export type Stats = {
  total_telemetry_readings: number
  total_cleaned_cells: number
  total_camera_snapshots: number
  map_coverage_percent: number
}
