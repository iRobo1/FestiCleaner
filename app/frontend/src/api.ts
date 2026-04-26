export const WS_BASE = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}`

export type Phase = 1 | 2 | 3 | 4
export type PhaseKey = 'search' | 'fetch' | 'return' | 'drop'

export const PHASE_KEYS: readonly PhaseKey[] = ['search', 'fetch', 'return', 'drop']
export const PHASE_LABELS: Readonly<Record<PhaseKey, string>> = {
  search: 'Search',
  fetch: 'Fetch',
  return: 'Return',
  drop: 'Drop',
}

export type Telemetry = {
  battery: number
  temperature: number
  humidity?: number
  phase?: Phase
  is_active: boolean
  last_update?: string
}

export type Stats = {
  total_telemetry_readings: number
  total_cleaned_cells: number
  total_camera_snapshots: number
  map_coverage_percent: number
}
