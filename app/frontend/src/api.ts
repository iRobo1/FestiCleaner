export const WS_BASE = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}`

export type Telemetry = {
  battery: number
  temperature: number
  humidity?: number
  is_active: boolean
  last_update?: string
}

export type Stats = {
  total_telemetry_readings: number
  total_cleaned_cells: number
  total_camera_snapshots: number
  map_coverage_percent: number
}
